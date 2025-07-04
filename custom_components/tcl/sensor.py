import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from . import async_register_entity
from .core.attribute import TclAttribute
from .core.device import TclDevice
from .entity import TclAbstractEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    await async_register_entity(
        hass,
        entry,
        async_add_entities,
        Platform.SENSOR,
        lambda device, attribute: TclSensor(device, attribute)
    )


class TclSensor(TclAbstractEntity, SensorEntity):

    def __init__(self, device: TclDevice, attribute: TclAttribute):
        super().__init__(device, attribute)

    def _update_value(self):
        values = self._attributes_data[self._attribute.key]
        comparison_table = self._attribute.ext.get('value_comparison_table', {})
        ret_values = {}
        for key, value in values.items():
            if value in comparison_table:
                data_comparison_table = comparison_table[str(key)]
                ret_values[str(key)] = data_comparison_table[value]  # 值存在于表中，使用映射后的值
            else:
                ret_values[str(key)] = value  # 值不存在，保留原值
        self._attr_native_value = ret_values
