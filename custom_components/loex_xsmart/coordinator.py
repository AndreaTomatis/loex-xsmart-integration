"""Coordinator for the Loex Xsmart Integration integration."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .loex_api import loex_api

_LOGGER: logging.Logger = logging.getLogger(__package__)


class loex_coordinator(DataUpdateCoordinator):
    """Loex Coordinator class."""

    def __init__(
        self, hass: HomeAssistant, api: loex_api, update_interval: int
    ) -> None:
        """Initialize."""
        self.api = api
        self.platforms = []

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self):
        try:
            return await self.hass.async_add_executor_job(self.api.get_data)
        except Exception as exception:
            raise UpdateFailed from exception

    async def async_set_room_target_temperature(self, room_id, target_temperature):
        """Set room target temperature."""
        try:
            return await self.hass.async_add_executor_job(
                self.api.set_room_target_temperature, room_id, target_temperature
            )
        except Exception as exception:
            raise UpdateFailed from exception

    async def async_set_circuit_target_temperature(self, mode, target_temperature):
        """Set circuit target temperature."""
        try:
            return await self.hass.async_add_executor_job(
                self.api.set_circuit_target_temperature, mode, target_temperature
            )
        except Exception as exception:
            raise UpdateFailed from exception

    async def async_set_room_mode(self, room_id, mode):
        """Set room mode temperature."""
        try:
            return await self.hass.async_add_executor_job(
                self.api.set_room_mode, room_id, mode
            )
        except Exception as exception:
            raise UpdateFailed from exception

    async def async_set_circuit_mode(self, mode):
        """Set circuit mode temperature."""
        try:
            return await self.hass.async_add_executor_job(
                self.api.set_circuit_mode, mode
            )
        except Exception as exception:
            raise UpdateFailed from exception
