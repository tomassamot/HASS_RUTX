"""
Example of a custom MQTT component.
Shows how to communicate with MQTT. Follows a topic on MQTT and updates the
state of an entity to the last message received on that topic.
Also offers a service 'set_state' that will publish a message on the topic that
will be passed via MQTT to our message received listener. Call the service with
example payload {"new_state": "some new state"}.
    figuration:
To use the mqtt_example component you will need to add the following to your
configuration.yaml file.
mqtt_basic_sync:
  topic: "home-assistant/mqtt_example"
"""
from __future__ import annotations

import voluptuous as vol
import json

import random
import time

from paho.mqtt import client as mqtt_client
from paho.mqtt.client import MQTTMessage

from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.components import frontend

from .const import DOMAIN, DEVICE_NAME, CONF_TOPIC, DEFAULT_TOPIC

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


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the MQTT example component."""

    broker = "192.168.10.103"
    port = 1883
    topic = "home-assistant/mint/#"
    # generate client ID with pub prefix randomly
    client_id = "python-mqtt-we"
    username = "broker"
    password = "brokerpass"

    device_name_eid = "mint.device_name"
    free_ram_eid = "mint.free_ram"
    total_ram_eid = "mint.total_ram"

    hass.states.set(device_name_eid, DEVICE_NAME)
    hass.states.set(free_ram_eid, "<empty>")
    hass.states.set(total_ram_eid, "<empty>")

    def on_disconnect(client, userdata, rc):
        print("Disconnected...")
        client.loop_stop(force=False)

    def connect_mqtt() -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(client_id)
        client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        print(f"trying to connnect to {broker}:{port}...")
        client.connect(broker, port)
        return client

    def on_message(client, userdata, msg: MQTTMessage):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if msg.topic == "home-assistant/mint/ram":
            data = json.loads(msg.payload)
            hass.states.set(free_ram_eid, data["free_ram"])
            hass.states.set(total_ram_eid, data["total_ram"])

    client = connect_mqtt()
    client.on_message = on_message
    client.subscribe(topic)
    client.loop_start()
    # client.loop(timeout=1.0, max_packets=1)

    # Return boolean to indicate that initialization was successfully.
    return True

