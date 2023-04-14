from __future__ import annotations

import logging

import voluptuous as vol
from paho.mqtt import client as mqtt_client

from homeassistant.const import (
    CONF_ADDRESS,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
)
from .const import DOMAIN, CONF_DEVICE_NAME


from homeassistant import config_entries
from homeassistant.core import HomeAssistant


_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_NAME): str,
        vol.Required(CONF_ADDRESS): str,
        vol.Required(CONF_PORT): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)
DATA_SCHEMA = vol.Schema({("host"): str})


async def validate_input(hass: HomeAssistant, data: dict):
    """Validate the user input allows us to connect."""

    def dummy_connect():
        try:
            client = mqtt_client.Client("conn_test")
            client.username_pw_set(data["username"], data["password"])
            client.connect(data["address"], int(data["port"]))
            client.loop_start()
            return client
        except Exception as ex:
            raise InvalidAddressOrPort

    def dummy_publish(client: mqtt_client.Client):
        try:
            client.publish("home-assistant/mint/test", "test")
        except Exception as ex:
            raise InvalidUsernameOrPassword

    def dummy_disconnect(client: mqtt_client.Client):
        client.disconnect()
        client.loop_stop(force=False)

    client = dummy_connect()
    dummy_publish(client)
    dummy_disconnect(client)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow."""

    VERSION = 1

    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
            except InvalidAddressOrPort:
                errors["base"] = "invalid_address_or_port"
            except InvalidAddress:
                errors["base"] = "invalid_address"
            except InvalidPort:
                errors["base"] = "invalid_port"
            except InvalidUsernameOrPassword:
                errors["base"] = "invalid_username_or_password"
            except Exception as ex:
                errors["base"] = "unknown"
            if not errors:
                return self.async_create_entry(title="Mint", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
            errors=errors,
        )


class InvalidAddressOrPort(Exception):
    ...


class InvalidAddress(Exception):
    ...


class InvalidPort(Exception):
    ...


class InvalidUsernameOrPassword(Exception):
    ...

