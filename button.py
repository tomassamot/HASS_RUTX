from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    async_add_entities([EmotionButton(), IpChangeButton()])


class EmotionButton(ButtonEntity):
    _attr_name = "Emotion getter"
    _attr_unique_id = "emotion_getter1"

    def press(self) -> None:
        """Handle the button press."""
        self.hass.bus.fire("send_emotion_request", {})


class IpChangeButton(ButtonEntity):
    _attr_name = "Change IP address"
    _attr_unique_id = "ip_changer1"

    def press(self) -> None:
        """Handle the button press."""
        self.hass.bus.fire("send_new_ip", {})

