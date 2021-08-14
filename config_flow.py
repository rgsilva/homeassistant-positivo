"""Config flow for Positivo Casa Inteligente integration."""
from __future__ import annotations

import logging
import sys
from typing import Any
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .tuya import TuyaAPI, InvalidAuthentication

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("password"): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    
    await hass.async_add_executor_job(
        test_login, data["username"], data["password"]
    )

    # Return info that you want to store in the config entry.
    return {
        "title": data["username"],
        CONF_USERNAME: data["username"],
        CONF_PASSWORD: data["password"],
    }


def test_login(username: str, password: str):
    try:
        TuyaAPI(username, password).login()
    except InvalidAuthentication:
        raise InvalidAuth


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Positivo Casa Inteligente."""

    VERSION = 1

    async def async_step_user(
        self, info: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if info is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, info)
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=info)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
