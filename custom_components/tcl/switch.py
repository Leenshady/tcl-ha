import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from . import async_register_entity
from .core.attribute import TclAttribute
from .core.device import TclDevice
from .entity import TclAbstractEntity
from .helpers import try_read_as_bool

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    await async_register_entity(
        hass,
        entry,
        async_add_entities,
        Platform.SWITCH,
        lambda device, attribute: TclSwitch(device, attribute)
    )


class TclSwitch(TclAbstractEntity, SwitchEntity):

    def __init__(self, device: TclDevice, attribute: TclAttribute):
        super().__init__(device, attribute)

    def _update_value(self):
        try:
            if self._attribute.key in self._attributes_data:
                self._attr_is_on = try_read_as_bool(self._attributes_data[self._attribute.key])
        except ValueError:
            _LOGGER.exception('entity [{}] read value failed'.format(self._attr_unique_id))
            self._attr_available = False

    def turn_on(self, **kwargs: Any) -> None:
        self._send_command({
            self._attribute.key: 1
        })

    def turn_off(self, **kwargs: Any) -> None:
        self._send_command({
            self._attribute.key: 0
        })
