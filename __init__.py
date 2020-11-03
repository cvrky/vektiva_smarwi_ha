"""The Vektiva Smarwi integration."""

import asyncio

import voluptuous

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

CONFIG_SCHEMA = voluptuous.Schema({DOMAIN: voluptuous.Schema({})}, extra=voluptuous.ALLOW_EXTRA)

# For your initial PR, limit it to 1 platform.
PLATFORMS = ["cover"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Vektiva Smarwi component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Vektiva Smarwi from a config entry."""
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)


    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    #if unload_ok:
    #    hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
