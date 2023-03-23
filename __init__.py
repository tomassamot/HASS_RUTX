from __future__ import annotations

import voluptuous as vol
import json

import random
import time

from paho.mqtt import client as mqtt_client
from paho.mqtt.client import MQTTMessage
from homeassistant import exceptions

from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.components import frontend

from .const import DOMAIN, CONF_TOPIC, DEFAULT_TOPIC, CONF_DEVICE_NAME

# The domain of your component. Should be equal to the name of your component.


# Schema to validate the configured MQTT topic


# CONFIG_SCHEMA = vol.Schema(
#     {
#         DOMAIN: vol.Schema(
#             {vol.Required(CONF_DEVICE_NAME): mqtt.valid_subscribe_topic},
#             {vol.Required(CONF_TOPIC)},
#         )
#     },
#     extra=vol.ALLOW_EXTRA,
# )
DEFAULT_DEVICE_NAME = "<empty>"
DEVICE_NAME = DEFAULT_DEVICE_NAME

device_name_eid = "mint.device_name"
free_ram_eid = "mint.free_ram"
total_ram_eid = "mint.total_ram"


def process_message(hass: HomeAssistant, msg: MQTTMessage):
    if msg.topic == "home-assistant/mint/ram":
        data = json.loads(msg.payload)
        hass.states.set(free_ram_eid, data["free_ram"])
        hass.states.set(total_ram_eid, data["total_ram"])


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hello World from a config entry."""
    print("I AM SECOND")
    hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN] = entry.data

    # broker = "192.168.10.103"
    # port = 1883
    # topic = "home-assistant/mint/#"
    # # generate client ID with pub prefix randomly
    # client_id = "python-mqtt-we"
    # username = "broker"
    # password = "brokerpass"

    broker = hass.data[DOMAIN]["address"]
    port = hass.data[DOMAIN]["port"]
    topic = "home-assistant/mint/#"
    # generate client ID with pub prefix randomly
    client_id = "python-mqtt-we"
    username = hass.data[DOMAIN]["username"]
    password = hass.data[DOMAIN]["password"]

    # time.sleep(0.5)
    # hass.states.set(device_name_eid, hass.data[DOMAIN]["device_name"])

    def on_disconnect(client, userdata, rc):
        print("Disconnected...")
        client.loop_stop(force=False)

    def connect_mqtt() -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                hass.states.set(device_name_eid, hass.data[DOMAIN]["device_name"])
                print("Connected to MQTT Broker!")
                client.subscribe(topic)
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(client_id)
        # client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        print(f"trying to connnect to {broker}:{port}...")
        client.connect(broker, int(port))
        return client

    def on_message(client, userdata, msg: MQTTMessage):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        # if hass.states.get(device_name_eid) == DEFAULT_DEVICE_NAME:
        #     hass.states.set(device_name_eid, hass.data[DOMAIN]["device_name"])

        print("DEVICE_NAME: ", DEVICE_NAME)
        # hass.states.set(device_name_eid, DEVICE_NAME)
        try:
            process_message(hass, msg)
        except Exception:
            print(
                "Unexpected error while processing published message in topic ",
                msg.topic,
            )

    client = connect_mqtt()
    client.loop_start()

    return True


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the MQTT example component."""
    print("I AM FIRST")
    hass.states.set(device_name_eid, "<empty>")
    hass.states.set(free_ram_eid, "<empty>")
    hass.states.set(total_ram_eid, "<empty>")

    # Return boolean to indicate that initialization was successfully.
    return True

