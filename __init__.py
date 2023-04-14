from __future__ import annotations

import json
import re
import logging

from paho.mqtt import client as mqtt_client
from paho.mqtt.client import MQTTMessage

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.typing import ConfigType

import homeassistant.components.input_text

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

RAM_TOPIC = "home-assistant/mint/ram"
IP_TOPIC = "home-assistant/mint/ip"
NEW_IP_TOPIC = "home-assistant/mint/new_ip"
INIT_TOPIC = "home-assistant/mint/init"
EMOTION_REQUEST_TOPIC = "home-assistant/mint/emotion_req"
EMOTION_RESPONSE_TOPIC = "home-assistant/mint/emotion_res"
WIRELESS_TOPIC = "home-assistant/mint/wireless"

DEVICE_NAME_EID = "mint.device_name"
TOTAL_RAM_EID = "mint.total_ram"
FREE_RAM_EID = "mint.free_ram"
AVAILABLE_RAM_EID = "mint.available_ram"
EMOTION_EID = "mint.emotion"
IP_EID = "mint.ip"

DEVICE_NAME_ATTR = {"friendly_name": "Device name", "icon": "mdi:router"}
TOTAL_RAM_ATTR = {
    "friendly_name": "Total RAM",
    "icon": "mdi:database",
    "unit_of_measurement": "B",
}
FREE_RAM_ATTR = {
    "friendly_name": "Free RAM",
    "icon": "mdi:database",
    "unit_of_measurement": "B",
}
AVAILABLE_RAM_ATTR = {
    "friendly_name": "Available RAM",
    "icon": "mdi:database",
    "unit_of_measurement": "B",
}
EMOTION_ATTR = {
    "friendly_name": "Emotion",
    "icon": "mdi:emoticon-cool",
}
IP_ATTR = {
    "friendly_name": "Current IP address",
    "icon": "mdi:ip",
}


def remove_illegal_characters(string):
    string = string.replace(".", "_")
    string = string.replace("-", "_")
    return string


def process_message(hass: HomeAssistant, msg: MQTTMessage):
    data = json.loads(msg.payload)

    if msg.topic == RAM_TOPIC:
        if "total" in data:
            hass.states.set(TOTAL_RAM_EID, data["total"], TOTAL_RAM_ATTR)
        if "free" in data:
            hass.states.set(FREE_RAM_EID, data["free"], FREE_RAM_ATTR)
        if "available" in data:
            hass.states.set(AVAILABLE_RAM_EID, data["available"], AVAILABLE_RAM_ATTR)

    elif msg.topic == EMOTION_RESPONSE_TOPIC:
        if "emotion" in data:
            hass.states.set(EMOTION_EID, data["emotion"], EMOTION_ATTR)
    elif msg.topic == IP_TOPIC:
        if "value" in data:
            hass.states.set(IP_EID, data["value"], IP_ATTR)

    elif msg.topic == WIRELESS_TOPIC:
        radio_name = remove_illegal_characters(data["radio_name"])
        if "up" in data:
            hass.states.set(
                "mint." + radio_name + "_up",
                data["up"],
                {"icon": "mdi:alarm-light", "friendly_name": "On"}
                if data["up"] == 1
                else {"icon": "mdi:alarm-light-off", "friendly_name": "Off"},
            )
        if "channel" in data:
            hass.states.set(
                "mint." + radio_name + "_channel",
                data["channel"],
                {"friendly_name": "Channel"},
            )
        if "hwmode" in data:
            hass.states.set(
                "mint." + radio_name + "_hwmode",
                data["hwmode"],
                {"friendly_name": "Hardware mode"},
            )
        if "htmode" in data:
            hass.states.set(
                "mint." + radio_name + "_htmode",
                data["htmode"],
                {"friendly_name": "High throughput mode"},
            )

        if "all_interfaces" not in data:
            return

        for interface in data["all_interfaces"]:
            # ifname is required to create unique entities
            if "ifname" not in interface:
                break
            original_ifname = interface["ifname"]
            safe_ifname = remove_illegal_characters(original_ifname)
            if "conn_devices" in interface:
                hass.states.set(
                    "mint." + radio_name + "_" + safe_ifname + "_conn_devices",
                    interface["conn_devices"],
                    {
                        "icon": "mdi:cellphone-wireless",
                        "friendly_name": original_ifname + ": connected devices",
                    },
                )
            if "ifconfig.ssid" in interface:
                hass.states.set(
                    "mint." + radio_name + "_" + safe_ifname + "_ifconfig_ssid",
                    interface["ifconfig.ssid"],
                    {
                        "icon": "mdi:wifi",
                        "friendly_name": original_ifname + ": ssid",
                    },
                )
            if "ifconfig.wifi_id" in interface:
                hass.states.set(
                    "mint." + radio_name + "_" + safe_ifname + "_ifconfig_wifi_id",
                    interface["ifconfig.wifi_id"],
                    {
                        "icon": "mdi:wifi",
                        "friendly_name": original_ifname + ": wifi id",
                    },
                )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hello World from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN] = entry.data

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["button", "sensor"])
    )

    broker = hass.data[DOMAIN]["address"]
    port = hass.data[DOMAIN]["port"]
    topic = "home-assistant/mint/#"
    client_id = "ha-mint"
    username = hass.data[DOMAIN]["username"]
    password = hass.data[DOMAIN]["password"]

    def on_disconnect(client, userdata, rc):
        print("Disconnected...")
        client.loop_stop(force=False)

    def connect_mqtt() -> mqtt_client:
        client = mqtt_client.Client(client_id)
        client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        client.connect(broker, int(port))
        return client

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            hass.states.set(
                DEVICE_NAME_EID, hass.data[DOMAIN]["device_name"], DEVICE_NAME_ATTR
            )

            client.subscribe(topic)

            def get_emotion(arg):
                client.publish(EMOTION_REQUEST_TOPIC, payload=None)

            def change_ip(arg):
                input = hass.states.get("sensor.new_ip").name
                pattern = re.compile("[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+")

                if pattern.match(input) is not None:
                    client.publish(NEW_IP_TOPIC, payload=input)

            hass.bus.listen("send_emotion_request", get_emotion)

            hass.bus.listen("send_new_ip", change_ip)

    def on_message(client, userdata, msg: MQTTMessage):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        try:
            process_message(hass, msg)
        except Exception as ex:
            print(
                f"Unexpected error while processing published message in topic. Message: {ex}",
                msg.topic,
            )

    try:
        client = connect_mqtt()
        client.loop_start()
        print("connection done")
    except ConnectionRefusedError as ex:
        print("failure")
        _LOGGER.exception(
            "Exception while trying to connect to MQTT broker: %s. Check if MQTT broker is running",
            ex,
        )
        return False
    except Exception as ex:
        _LOGGER.exception("Unexpected exception: %s", ex)
        return False

    return True


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the MQTT example component."""
    init_states(hass)
    # Return boolean to indicate that initialization was successfully.
    return True


def init_states(hass: HomeAssistant):
    # hass.states.set(DEVICE_NAME_EID, None, DEVICE_NAME_ATTR)
    hass.states.set(IP_EID, None, IP_ATTR)
    hass.states.set(EMOTION_EID, None, EMOTION_ATTR)

