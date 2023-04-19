from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Entities for IP change"""
    async_add_entities([NewIpState()])

    """Entities for banning devices, connected wirelessly"""
    async_add_entities([DeviceToBanState(), BanDurationState(), InterfaceNameState()])


class NewIpState(SensorEntity):
    """Sensor behaving as a textbox for new IP"""

    _attr_name = "<New IP>"
    _attr_icon = "mdi:form-textbox"
    _attr_unique_id = "new_ip1"
    _attr_state = " "


class DeviceToBanState(SensorEntity):
    """Sensor behaving as a textbox for device to ban"""

    _attr_name = "<Device to ban>"
    _attr_icon = "mdi:form-textbox"
    _attr_unique_id = "device_to_ban1"
    _attr_state = " "


class BanDurationState(SensorEntity):
    """Sensor behaving as a textbox for ban duration"""

    _attr_name = "<Ban duration>"
    _attr_icon = "mdi:form-textbox"
    _attr_unique_id = "ban_duration1"
    _attr_state = " "


class InterfaceNameState(SensorEntity):
    """Sensor behaving as a textbox for interface name"""

    _attr_name = "<Interface name>"
    _attr_icon = "mdi:form-textbox"
    _attr_unique_id = "interface_name1"
    _attr_state = " "

