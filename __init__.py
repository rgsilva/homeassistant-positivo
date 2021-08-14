"""The Positivo Casa Inteligente integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry, SOURCE_REAUTH
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import DOMAIN, API
from .tuya import TuyaAPI
from .tuya.exceptions import InvalidAuthentication

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["switch", "sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    # Ensure our name space for storing objects is a known type. A dict is
    # common/preferred as it allows a separate instance of your class for each
    # instance that has been created in the UI.
    hass.data.setdefault(DOMAIN, {})

    return True


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Set up Positivo Casa Inteligente from a config entry."""
    _LOGGER.info(config)

    try:
        api = TuyaAPI(config.data[CONF_USERNAME], config.data[CONF_PASSWORD])
        await hass.async_add_executor_job(lambda: api.login())

        hass.data[DOMAIN][config.entry_id] = { API: api }
    except InvalidAuthentication:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_REAUTH},
                data=config.data,
            )
        )
        return False

    hass.config_entries.async_setup_platforms(config, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
