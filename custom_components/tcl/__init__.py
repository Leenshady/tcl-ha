import asyncio
import logging
import threading

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from .const import DOMAIN, SUPPORTED_PLATFORMS, FILTER_TYPE_EXCLUDE, FILTER_TYPE_INCLUDE
from .core.attribute import TclAttribute
from .core.client import TclClient, EVENT_DEVICE_DATA_CHANGED, TclClientException, TokenInfo
from .core.config import AccountConfig, DeviceFilterConfig, EntityFilterConfig
from .core.device import TclDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {
        'devices': [],
        'signals': []
    })

    await try_update_token(hass, entry)
    # 定时更新token
    token_signal = threading.Event()
    hass.async_create_background_task(token_updater(hass, entry, token_signal), 'tcl-token-updater')
    hass.data[DOMAIN]['signals'].append(token_signal)

    account_cfg = AccountConfig(hass, entry)
    client = TclClient(hass, account_cfg.account_id, account_cfg.token)
    devices = await client.get_devices()
    _LOGGER.debug('共获取到{}个设备'.format(len(devices)))

    hass.data[DOMAIN]['devices'] = devices

    # 监听设备数据
    device_signal = threading.Event()
    hass.async_create_background_task(client.listen_devices(devices, device_signal), 'tcl-device-data')
    hass.data[DOMAIN]['signals'].append(device_signal)

    await hass.config_entries.async_forward_entry_setups(entry, SUPPORTED_PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(entry_update_listener))

    return True


async def token_updater(hass: HomeAssistant, entry: ConfigEntry, signal: threading.Event):
    """
    每1小时检查一次token有效性，若token刷新则重载集成
    :param hass:
    :param entry:
    :param signal:
    :return:
    """
    while not signal.is_set():
        if await try_update_token(hass, entry):
            _LOGGER.info('token refreshed, reload integration...')
            await hass.config_entries.async_reload(entry.entry_id)
            break
        else:
            _LOGGER.debug('token is valid')

        await asyncio.sleep(3600)


async def try_update_token(hass: HomeAssistant, entry: ConfigEntry):
    """
    尝试刷新token，刷新成功返回True，如refresh_token无效则会抛出异常
    :param hass:
    :param entry:
    :return:
    """
    cfg = AccountConfig(hass, entry)
    client = TclClient(hass, cfg.account_id, cfg.token)

    try:
        await client.get_user_info()
        return False
    except TclClientException:
        token_info = await client.refresh_token(cfg.refresh_token)
        cfg.token = token_info.token
        cfg.refresh_token = token_info.refresh_token
        cfg.save()

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    for platform in SUPPORTED_PLATFORMS:
        if not await hass.config_entries.async_forward_entry_unload(entry, platform):
            return False

    for signal in hass.data[DOMAIN]['signals']:
        signal.set()

    del hass.data[DOMAIN]

    return True


async def entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    _LOGGER.debug('reload tcl integration...')
    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_config_entry_device(hass: HomeAssistant, config: ConfigEntry, device: DeviceEntry) -> bool:
    device_id = list(device.identifiers)[0][1]

    _LOGGER.info('Device [{}] removing...'.format(device_id))

    for device in hass.data[DOMAIN]['devices']:
        if device.id.lower() == device_id:
            target_device = device
            break
    else:
        _LOGGER.error('Device [{}] not found'.format(device_id))
        return False

    cfg = DeviceFilterConfig(hass, config)
    if cfg.filter_type == FILTER_TYPE_EXCLUDE:
        cfg.add_device(target_device.id)
    else:
        cfg.remove_device(target_device.id)

    cfg.save()

    _LOGGER.info('Device [{}] removed'.format(device_id))

    return True


async def async_register_entity(hass: HomeAssistant, entry: ConfigEntry, async_add_entities, platform, setup) -> None:
    entities = []
    for device in hass.data[DOMAIN]['devices']:
        if DeviceFilterConfig.is_skip(hass, entry, device.id):
            continue

        for attribute in device.attributes:
            if attribute.platform != platform:
                continue

            if EntityFilterConfig.is_skip(hass, entry, device.id, attribute.key):
                continue

            entities.append(setup(device, attribute))

    async_add_entities(entities)
