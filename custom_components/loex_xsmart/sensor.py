"""Sensor Platform for Loex Xsmart Integration."""

import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.const import UnitOfTemperature, PERCENTAGE

from .const import DOMAIN
from .entity import loex_entity
from .coordinator import loex_coordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    coordinator: loex_coordinator

    coordinator = hass.data[DOMAIN]

    entities = []

    external_temp = loex_temperature_sensor(
        coordinator,
        entry,
        "ext_temp",
        "External Temperature Sensor",
        UnitOfTemperature.CELSIUS,
        "mdi:temperature-celsius",
        SensorDeviceClass.TEMPERATURE,
    )

    entities.extend([external_temp])

    for room_id in coordinator.data:
        if room_id == "external":
            continue

        if room_id == "circuit":
            continue

        if (coordinator.data[room_id]["validity"]) == 6:
            humidity_sensor = loex_humidity_sensor(
                coordinator,
                entry,
                str(room_id) + "_humidity",
                room_id,
                coordinator.data[room_id]["room_name"],
                PERCENTAGE,
                "mdi:water-percent",
                SensorDeviceClass.HUMIDITY,
            )
            entities.extend([humidity_sensor])

    async_add_entities(entities, True)


class loex_temperature_sensor(loex_entity, SensorEntity):
    def __init__(
        self,
        coordinator: loex_coordinator,
        entry: ConfigEntry,
        idx: str,
        description: str,
        unit: str,
        icon: str,
        device_class: str,
    ) -> None:
        super().__init__(coordinator, entry)
        self._id = idx
        self.description = description
        self.unit = unit
        self._icon = icon
        self._device_class = device_class

    @property
    def state(self):
        return self.coordinator.data["external"]["ext_temp"]

    @property
    def unit_of_measurement(self):
        return self.unit

    @property
    def icon(self) -> str:
        return self._icon

    @property
    def device_class(self) -> SensorDeviceClass:
        return self._device_class

    @property
    def name(self) -> str:
        return f"{self.description}"

    @property
    def id(self):
        return f"{DOMAIN}_{self._id}"

    @property
    def unique_id(self):
        return f"{DOMAIN}-{self._id}-{self.coordinator.api.host}"


class loex_humidity_sensor(loex_entity, SensorEntity):
    def __init__(
        self,
        coordinator: loex_coordinator,
        entry: ConfigEntry,
        idx: str,
        room_id,
        description: str,
        unit: str,
        icon: str,
        device_class: str,
    ) -> None:
        super().__init__(coordinator, entry)
        self._id = idx
        self._room_id = room_id
        self.description = description
        self.unit = unit
        self._icon = icon
        self._device_class = device_class

    @property
    def state(self):
        return self.coordinator.data[self._room_id]["humidity"]

    @property
    def unit_of_measurement(self):
        return self.unit

    @property
    def icon(self):
        return self._icon

    @property
    def device_class(self) -> SensorDeviceClass:
        return self._device_class

    @property
    def name(self) -> str:
        return f"{self.description}"

    @property
    def id(self):
        return f"{DOMAIN}_{self._id}"

    @property
    def unique_id(self):
        return f"{DOMAIN}-{self._id}-{self.coordinator.api.host}"
