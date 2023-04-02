"""Config flow for Loex Xsmart Integration integration."""
from __future__ import annotations

import logging

import requests

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

_ENDPOINT = "https://xsmart.loex.it"

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("password"): str,
        vol.Required("plant"): str,
        vol.Required("deviceId"): str,
    }
)


class LoexXsmartHub:
    def __init__(self) -> None:
        """Initialize."""
        self.host = _ENDPOINT

    def authenticate(
        self, username: str, password: str, device_id: str, plant: str
    ) -> bool:
        response = requests.get(
            str(self.host + "/jwt/?id=" + device_id + "&plant=" + plant),
            auth=(username, password),
            timeout=10,
        )

        if response.status_code == 200:
            return True

        raise InvalidAuth


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    hub = LoexXsmartHub()

    result = await hass.async_add_executor_job(
        hub.authenticate,
        data["username"],
        data["password"],
        data["deviceId"],
        data["plant"],
    )

    if not result:
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": data["plant"]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Loex Xsmart Integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
