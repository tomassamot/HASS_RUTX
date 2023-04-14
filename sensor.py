from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    async_add_entities([NewIpState()])


class NewIpState(SensorEntity):
    _attr_name = "New IP"
    _attr_icon = "mdi:form-textbox"
    _attr_unique_id = "new_ip1"
    _attr_state = ""

