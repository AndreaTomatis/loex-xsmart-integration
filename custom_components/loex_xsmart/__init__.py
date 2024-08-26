"""The Loex Xsmart Integration integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_SYNC_INTERVAL, DEFAULT_SYNC_INTERVAL, DOMAIN
from .coordinator import loex_coordinator
from .loex_api import loex_api

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Loex Xsmart Integration from a config entry."""

    if hass.data.get(DOMAIN) is None:
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

    sync_interval = entry.options.get(CONF_SYNC_INTERVAL, DEFAULT_SYNC_INTERVAL)

    coordinator = loex_coordinator(hass, api=loex, update_interval=sync_interval)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    # Store an API object for your platforms to access
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.add_update_listener(async_reload_entry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entries."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
