import logging

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import DOMAIN

from .loex_api import loex_api

_LOGGER: logging.Logger = logging.getLogger(__package__)


class loex_coordinator(DataUpdateCoordinator):
    def __init__(
        self, hass: HomeAssistant, api: loex_api, update_interval: int
    ) -> None:
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
            raise UpdateFailed() from exception

    async def async_set_room_target_temperature(self, room_id, target_temperature):
        try:
            return await self.hass.async_add_executor_job(
                self.api.set_room_target_temperature, room_id, target_temperature
            )
        except Exception as exception:
            raise UpdateFailed() from exception

    async def async_set_circuit_target_temperature(self, mode, target_temperature):
        try:
            return await self.hass.async_add_executor_job(
                self.api.set_circuit_target_temperature, mode, target_temperature
            )
        except Exception as exception:
            raise UpdateFailed() from exception

    async def async_set_room_mode(self, room_id, mode):
        try:
            return await self.hass.async_add_executor_job(
                self.api.set_room_mode, room_id, mode
            )
        except Exception as exception:
            raise UpdateFailed() from exception

    async def async_set_circuit_mode(self, mode):
        try:
            return await self.hass.async_add_executor_job(
                self.api.set_circuit_mode, mode
            )
        except Exception as exception:
            raise UpdateFailed() from exception
