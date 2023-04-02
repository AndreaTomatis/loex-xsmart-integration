"""The Loex Xsmart Integration integration."""
from __future__ import annotations

import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .loex_api import loex_api
from .coordinator import loex_coordinator

from .const import DOMAIN, CONF_SYNC_INTERVAL, DEFAULT_SYNC_INTERVAL

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Loex Xsmart Integration from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    # Create API instance
    loex = loex_api()
    # Validate the API connection (and authentication)
    await hass.async_add_executor_job(
        loex.authenticate,
        entry.data["username"],
        entry.data["password"],
        entry.data["deviceId"],
        entry.data["plant"],
    )
    # Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = loex

    sync_interval = entry.options.get(CONF_SYNC_INTERVAL, DEFAULT_SYNC_INTERVAL)

    coordinator = loex_coordinator(hass, api=loex, update_interval=sync_interval)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN] = coordinator

    # await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            hass.async_add_job(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )

    entry.add_update_listener(async_reload_entry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
    #    hass.data[DOMAIN].pop(entry.entry_id)

    coordinator = hass.data[DOMAIN]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN] = []

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
