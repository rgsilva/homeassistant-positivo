from dataclasses import dataclass
import logging
from typing import Callable, Optional

import voluptuous as vol

from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity

from homeassistant.const import (
    CONF_USERNAME, CONF_PASSWORD, STATE_UNAVAILABLE,
    DEVICE_CLASS_CURRENT, DEVICE_CLASS_POWER, DEVICE_CLASS_VOLTAGE,
    ELECTRIC_CURRENT_MILLIAMPERE, ELECTRIC_POTENTIAL_VOLT, POWER_WATT)
    
from .const import DOMAIN, API

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
})

DPS_VOLTAGE = "20"
DPS_CURRENT = "18"
DPS_POWER = "19"

async def async_setup_entry(hass, config, async_add_devices):
    """Add sensors for passed config in HA."""

    api = hass.data[DOMAIN][config.entry_id][API]

    found_sensors = []
    groups = await hass.async_add_executor_job(lambda: api.groups())
    for group in groups:
        devices = await hass.async_add_executor_job(lambda: api.devices(group["groupId"]))
        for device in devices:
            if device.product == "switch":
                found_sensors.append(PositivoSensor(device, hass, SensorConfig(DPS_VOLTAGE, "Voltage", DEVICE_CLASS_VOLTAGE, ELECTRIC_POTENTIAL_VOLT, lambda value: value/10)))
                found_sensors.append(PositivoSensor(device, hass, SensorConfig(DPS_CURRENT, "Current", DEVICE_CLASS_CURRENT, ELECTRIC_CURRENT_MILLIAMPERE)))
                found_sensors.append(PositivoSensor(device, hass, SensorConfig(DPS_POWER, "Power", DEVICE_CLASS_POWER, POWER_WATT)))
                
    
    _LOGGER.info("Found %d sensors", len(found_sensors))
    async_add_devices(found_sensors)


@dataclass
class SensorConfig:
    dps: str
    name_suffix: str
    device_class: str
    unit: str
    value_func: Callable[[float], float] = lambda value: value
    

class PositivoSensor(SensorEntity):
    def __init__(self, device, hass, sensor_config: SensorConfig):
        self._device = device
        self._hass = hass
        self._config = sensor_config
        self._value = self._config.value_func(device.dps[self._config.dps])


    @property
    def name(self):
        return self._device.name + " " + self._config.name_suffix


    @property
    def state(self):
        if self._device.online:
            return self._value
        return STATE_UNAVAILABLE


    @property
    def device_class(self):
        return self._config.device_class


    @property
    def unit_of_measurement(self):
        return self._config.unit


    async def async_update(self, **kwargs):
        """Updates the sensor status"""
        await self._hass.async_add_executor_job(lambda: self._device.refresh())
        self._value = self._config.value_func(self._device.dps[self._config.dps])
