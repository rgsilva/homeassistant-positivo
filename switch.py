import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant
from homeassistant.components.switch import (ATTR_CURRENT_POWER_W, PLATFORM_SCHEMA, SwitchEntity)
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, STATE_ON, STATE_OFF, STATE_UNAVAILABLE

from datetime import datetime
from typing import Optional

from .const import DOMAIN, API

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
})


async def async_setup_entry(hass, config, async_add_devices):
    """Add switches for passed config in HA."""

    api = hass.data[DOMAIN][config.entry_id][API]

    found_switches = []
    groups = await hass.async_add_executor_job(lambda: api.groups())
    for group in groups:
        devices = await hass.async_add_executor_job(lambda: api.devices(group["groupId"]))
        for device in devices:
            if device.product == "switch":
                found_switches.append(PositivoSwitch(device, hass))
    
    _LOGGER.info("Found %d switches", len(found_switches))
    async_add_devices(found_switches)


class PositivoSwitch(SwitchEntity):
    MIN_UPDATE_THRESHOLD = 5

    DPS_SWITCH = "1"
    DPS_CURRENT = "18"
    DPS_VOLTAGE = "20"
    DPS_POWER = "19"

    def __init__(self, device, hass):
        self._device = device
        self._hass = hass
        self._is_on = device.dps[PositivoSwitch.DPS_SWITCH]
        self._last_update = datetime.now()


    @property
    def name(self):
        return self._device.name


    @property
    def is_on(self):
        return self._is_on


    @property
    def available(self) -> Optional[str]:
        """Return the availability of the device"""
        return self._device.online


    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        success = await self._hass.async_add_executor_job(lambda: self._device.set_dps(PositivoSwitch.DPS_SWITCH, True))
        if success:
            self._is_on = True
        else:
            _LOGGER.error("Operation failed: unable to turn switch on!")


    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        success = await self._hass.async_add_executor_job(lambda: self._device.set_dps(PositivoSwitch.DPS_SWITCH, False))
        if success:
            self._is_on = False
        else:
            _LOGGER.error("Operation failed: unable to turn switch on!")


    async def async_update(self, **kwargs):
        """Updates the switch status"""
        
        # If the state was manually changed by us in the last N seconds, we don't update the status.
        if (datetime.now() - self._last_update).seconds < PositivoSwitch.MIN_UPDATE_THRESHOLD:
            return

        await self._hass.async_add_executor_job(lambda: self._device.refresh())
        self._is_on = self._device.dps[PositivoSwitch.DPS_SWITCH]
