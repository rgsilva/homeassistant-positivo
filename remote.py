import logging
import voluptuous as vol
import json

from . import tuya_remote

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import entity_platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.components.remote import RemoteEntity, PLATFORM_SCHEMA
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, STATE_UNAVAILABLE

from typing import Iterable, Optional

from .const import DOMAIN, API

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
})

async def async_setup_entry(hass: HomeAssistant, config, async_add_devices):
    """Add remote controls for passed config in HA."""

    api = hass.data[DOMAIN][config.entry_id][API]

    found_gateways = []
    found_remotes = []
    groups = await hass.async_add_executor_job(lambda: api.groups())
    for group in groups:
        devices = await hass.async_add_executor_job(lambda: api.devices(group["groupId"]))
        for gw_device in devices:
            if gw_device.product == "smart_ir": # only smart IR gateways
                found_gateways.append(gw_device)
                sub_devices = await hass.async_add_executor_job(lambda: api.ir_children(gw_device.id))
                for sub_device in sub_devices:
                    buttons = await hass.async_add_executor_job(lambda: api.ir_get_buttons(gw_device.id, sub_device.id))
                    found_remotes.append(PositivoRemote(hass, gw_device, sub_device, buttons))

    _LOGGER.info("Found %d remotes", len(found_remotes))
    async_add_devices(found_remotes)

    await add_service(hass, found_gateways)
    _LOGGER.info(f"Added IR service for %d gateways", len(found_gateways))


async def add_service(hass: HomeAssistant, gateways):
    async def send_raw_ir(call: ServiceCall):
        if "device" in call.data:
            device_id = call.data["device"]
            devices = list(g for g in gateways if g.id == device_id)
            if len(devices) == 0:
                raise ValueError("Device not found")
            device = devices[0]
        else:
            device = gateways[0]

        protocol = call.data["protocol"]
        command = json.loads(call.data["command"])

        encoded_value = tuya_remote.tuya_encode(protocol, command)
        payload = {"1":"study_key", "3":"", "7": encoded_value}
        
        await hass.async_add_executor_job(lambda: device.set_dps_many(payload))

    schema = vol.Schema({
        vol.Required("device") if len(gateways) > 1 else vol.Optional("device"): vol.In(list(g.id for g in gateways)),
        vol.Required("protocol"): vol.In(tuya_remote.AVAILABLE_PROTOCOLS),
        vol.Required("command"): str,
    })
    hass.services.async_register(DOMAIN, "send_ir", send_raw_ir, schema)


class PositivoRemote(RemoteEntity):
    def __init__(self, hass: HomeAssistant, gateway_device, remote_device, buttons):
        self._remote = remote_device
        self._gateway = gateway_device
        self._hass: HomeAssistant = hass
        self._buttons = self._button_map(buttons)


    def _button_map(self, buttons):
        result = {}
        for button in buttons:
            result[button["name"]] = button
        return result


    @property
    def name(self):
        return self._remote.name


    @property
    def available(self) -> Optional[str]:
        """Remotes are always available if the gateway is available"""
        return self._gateway.online
    
    @property
    def state(self):
        return STATE_UNAVAILABLE

    async def async_send_command(self, command: Iterable[str], **kwargs):
        """Send commands to a device."""
        for subcommand in command:
            if subcommand in self._buttons:
                await self._hass.async_add_executor_job(lambda: self._remote.set_dps_many(self._buttons[subcommand]["dps"]))
