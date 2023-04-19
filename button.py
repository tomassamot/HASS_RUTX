from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    async_add_entities([EmotionButton(), IpChangeButton(), BanButton()])


class EmotionButton(ButtonEntity):
    _attr_name = "Emotion getter"
    _attr_unique_id = "emotion_getter1"

    def press(self) -> None:
        """Handle the button press."""
        self.hass.bus.fire("mint_send_emotion_request", {})


class IpChangeButton(ButtonEntity):
    _attr_name = "Change IP address"
    _attr_unique_id = "ip_changer1"

    def press(self) -> None:
        self.hass.bus.fire("mint_send_new_ip", {})


class BanButton(ButtonEntity):
    _attr_name = "Ban given device"
    _attr_unique_id = "ban_hammer"

    def press(self) -> None:
        self.hass.bus.fire("mint_ban_device", {})

