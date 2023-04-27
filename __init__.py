from __future__ import annotations

import json
import re
import logging
import requests

from paho.mqtt import client as mqtt_client
from paho.mqtt.client import MQTTMessage

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

RAM_TOPIC = "home-assistant/mint/ram"
IP_TOPIC = "home-assistant/mint/ip"
NEW_IP_TOPIC = "home-assistant/mint/new_ip"
INIT_TOPIC = "home-assistant/mint/init"
EMOTION_REQUEST_TOPIC = "home-assistant/mint/emotion_req"
EMOTION_RESPONSE_TOPIC = "home-assistant/mint/emotion_res"
WIRELESS_TOPIC = "home-assistant/mint/wireless"
BAN_DEVICE_TOPIC = "home-assistant/mint/ban_device"
LAN_PORTS_TOPIC = "home-assistant/mint/lan_ports"
DHCP_LEASES_TOPIC = "home-assistant/mint/dhcp_leases"

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


def process_message(hass: HomeAssistant, msg: MQTTMessage):
    """Process message, received from MQTT broker"""

    def remove_illegal_characters(string):
        string = string.replace(".", "_")
        string = string.replace("-", "_")
        string = string.replace(" ", "_")
        return string

    data: json = json.loads(msg.payload)

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

        def get_radio_information(radio: dict[str, any], radio_name):
            if "up" in radio:
                hass.states.set(
                    "mint." + radio_name + "_up",
                    "",
                    {"icon": "mdi:alarm-light", "friendly_name": "On"}
                    if radio["up"] == 1
                    else {"icon": "mdi:alarm-light-off", "friendly_name": "Off"},
                )

            if "config" in radio:
                config = radio["config"]
                if "channel" in config:
                    hass.states.set(
                        "mint." + radio_name + "_channel",
                        config["channel"],
                        {"friendly_name": "Channel"},
                    )
                if "hwmode" in config:
                    hass.states.set(
                        "mint." + radio_name + "_hwmode",
                        config["hwmode"],
                        {"friendly_name": "Hardware mode"},
                    )
                if "htmode" in config:
                    hass.states.set(
                        "mint." + radio_name + "_htmode",
                        config["htmode"],
                        {"friendly_name": "High throughput mode"},
                    )

            if "interfaces" in radio:
                for interface in radio["interfaces"]:
                    # ifname is required to create unique entities
                    if "ifname" not in interface:
                        continue
                    original_ifname = interface["ifname"]
                    safe_ifname = remove_illegal_characters(original_ifname)
                    if "conn_devices" in interface:
                        hass.states.set(
                            "mint." + radio_name + "_" + safe_ifname + "_conn_devices",
                            interface["conn_devices"],
                            {
                                "icon": "mdi:cellphone-wireless",
                                "friendly_name": original_ifname
                                + ": Connected devices",
                            },
                        )
                    if "banned_devices" in interface:
                        hass.states.set(
                            "mint."
                            + radio_name
                            + "_"
                            + safe_ifname
                            + "_banned_devices",
                            interface["banned_devices"],
                            {
                                "icon": "mdi:cellphone-wireless",
                                "friendly_name": original_ifname + ": Banned devices",
                            },
                        )
                    if "config" in interface:
                        ifconfig = interface["config"]
                        if "ssid" in ifconfig:
                            hass.states.set(
                                "mint."
                                + radio_name
                                + "_"
                                + safe_ifname
                                + "_ifconfig_ssid",
                                ifconfig["ssid"],
                                {
                                    "icon": "mdi:wifi",
                                    "friendly_name": original_ifname + ": ssid",
                                },
                            )
                        if "wifi_id" in ifconfig:
                            hass.states.set(
                                "mint."
                                + radio_name
                                + "_"
                                + safe_ifname
                                + "_ifconfig_wifi_id",
                                ifconfig["wifi_id"],
                                {
                                    "icon": "mdi:wifi",
                                    "friendly_name": original_ifname + ": wifi id",
                                },
                            )

        for radio_name in data:
            get_radio_information(data[radio_name], radio_name)

    elif msg.topic == LAN_PORTS_TOPIC:
        for key in data:
            lan_name = remove_illegal_characters(key)
            lan = data[key]
            if "speed" in lan:
                hass.states.set(
                    "mint." + lan_name + "_speed",
                    lan["speed"],
                    {
                        "icon": "mdi:lightning-bolt",
                        "friendly_name": lan_name.upper() + " speed",
                    },
                )
            if "state" in lan:
                hass.states.set(
                    "mint." + lan_name + "_state",
                    "",
                    {
                        "icon": "mdi:ethernet-cable",
                        "friendly_name": lan_name.upper() + " IS UP",
                    }
                    if lan["state"] == "up"
                    else {
                        "icon": "mdi:ethernet-cable-off",
                        "friendly_name": lan_name + " IS DOWN",
                    },
                )
            if "topology" in lan:
                hass.states.set(
                    "mint." + lan_name + "_mac",
                    lan["topology"],
                    {
                        "icon": "mdi:ethernet",
                        "friendly_name": lan_name.upper() + " MAC",
                    },
                )

    elif msg.topic == DHCP_LEASES_TOPIC:
        lease_hostnames = ""
        lease_ipaddrs = ""
        lease_macs = ""

        is_first_iteration = True
        for lease in data:
            if "hostname" not in lease:
                if is_first_iteration:
                    lease_hostnames += "*"
                else:
                    lease_hostnames += ",*"
            else:
                if is_first_iteration:
                    lease_hostnames += lease["hostname"]
                else:
                    lease_hostnames += "," + lease["hostname"]

            if "ipaddr" not in lease:
                if is_first_iteration:
                    lease_ipaddrs += "*"
                else:
                    lease_ipaddrs += ",*"
            else:
                if is_first_iteration:
                    lease_ipaddrs += lease["ipaddr"]
                else:
                    lease_ipaddrs += "; " + lease["ipaddr"]

            if "mac" not in lease:
                if is_first_iteration:
                    lease_macs += "*"
                else:
                    lease_macs += ", *"
            else:
                if is_first_iteration:
                    lease_macs += lease["mac"]
                else:
                    lease_macs += "; " + lease["mac"]

            if is_first_iteration:
                is_first_iteration = False

        hass.states.set(
            "mint.lease_hostnames", lease_hostnames, {"friendly_name": "Host names"}
        )
        hass.states.set(
            "mint.lease_ipaddrs", lease_ipaddrs, {"friendly_name": "IP addresses"}
        )
        hass.states.set(
            "mint.lease_macs", lease_macs, {"friendly_name": "MAC addresses"}
        )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
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

            hass.states.remove("sensor.new_ip")
            client.subscribe(topic)

            def get_emotion(arg):
                client.publish(EMOTION_REQUEST_TOPIC, payload=None)

            def change_ip(arg):
                newip_input = hass.states.get("sensor.new_ip").name
                pattern = re.compile("[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+")

                if pattern.match(newip_input) is not None:
                    message = json.dumps({"new_ip": str(newip_input)})
                    client.publish(NEW_IP_TOPIC, payload=message)

            def ban_device(arg):
                addr = hass.states.get("sensor.device_to_ban").name
                ifname = hass.states.get("sensor.interface_name").name
                try:
                    ban_time = int(hass.states.get("sensor.ban_duration").name)
                except Exception as ex:
                    _LOGGER.warn(
                        f"Exception when trying to read ban_time: {ex}. Defaulting ban_time to 5 seconds (5000)."
                    )
                    ban_time = 5000

                message = json.dumps(
                    {"addr": addr, "ban_time": ban_time, "ifname": ifname}
                )

                client.publish(BAN_DEVICE_TOPIC, payload=message)

            hass.bus.listen("mint_send_emotion_request", get_emotion)
            hass.bus.listen("mint_send_new_ip", change_ip)
            hass.bus.listen("mint_ban_device", ban_device)

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
    """Set up the component."""
    hass.states.remove("sensor.new_ip")
    init_states(hass)

    # Return boolean to indicate that initialization was successfully.
    return True


def init_states(hass: HomeAssistant):
    hass.states.set(IP_EID, None, IP_ATTR)
    hass.states.set(EMOTION_EID, None, EMOTION_ATTR)

