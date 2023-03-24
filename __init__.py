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
from homeassistant.components.sensor.const import SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfInformation
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.components import frontend
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, CONF_TOPIC, DEFAULT_TOPIC, CONF_DEVICE_NAME


DEVICE_NAME_EID = "mint.device_name"
FREE_RAM_EID = "mint.free_ram"
TOTAL_RAM_EID = "mint.total_ram"


def clear_states(hass: HomeAssistant):
    hass.states.remove(DEVICE_NAME_EID)
    hass.states.remove(FREE_RAM_EID)
    hass.states.remove(TOTAL_RAM_EID)


def process_message(hass: HomeAssistant, msg: MQTTMessage):
    if msg.topic == "home-assistant/mint/ram":
        data = json.loads(msg.payload)
        if data["free_ram"] is None:
            print("ERR: free_ram is None")
        if data["total_ram"] is None:
            print("ERR: total_ram is None")
        hass.states.set(FREE_RAM_EID, data["free_ram"])
        hass.states.set(TOTAL_RAM_EID, data["total_ram"])


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

    def on_disconnect(client, userdata, rc):
        print("Disconnected...")
        client.loop_stop(force=False)

    def connect_mqtt() -> mqtt_client:
        client = mqtt_client.Client(client_id)
        # client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        client.on_connect_fail = on_connect_fail
        print(f"trying to connnect to {broker}:{port}...")
        client.connect(broker, int(port))
        return client

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            hass.states.set(DEVICE_NAME_EID, hass.data[DOMAIN]["device_name"])
            client.subscribe(topic)
        else:
            clear_states(hass)

    def on_connect_fail(client, userdata, flags, rc):
        clear_states(hass)

    def on_message(client, userdata, msg: MQTTMessage):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        # if hass.states.get(device_name_eid) == DEFAULT_DEVICE_NAME:
        #     hass.states.set(device_name_eid, hass.data[DOMAIN]["device_name"])

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
    init_states(hass)

    # Return boolean to indicate that initialization was successfully.
    return True


def init_states(hass: HomeAssistant):
    hass.states.set(DEVICE_NAME_EID, "<empty>")
    hass.states.set(FREE_RAM_EID, "<empty>")
    hass.states.set(TOTAL_RAM_EID, "<empty>")

