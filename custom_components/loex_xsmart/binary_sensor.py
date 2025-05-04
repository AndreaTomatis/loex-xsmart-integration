"""Binary Sensor Platform for Loex Xsmart Integration."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import loex_coordinator
from .entity import loex_entity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities) -> None:
    """Entry setup."""
    coordinator: loex_coordinator

    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for idx in coordinator.data["control"]:
        input_sensor = loex_binary_sensor(
            coordinator,
            entry,
            idx,
            coordinator.data["control"][idx]["description"],
            "",
            sensor_type,
        )
        entities.extend([input_sensor])

    async_add_entities(entities, True)


class loex_binary_sensor(loex_entity, BinarySensorEntity):
    """Elkron binary sensor class."""

    def __init__(
        self,
        coordinator: loex_coordinator,
        entry: ConfigEntry,
        idx: str,
        description: str,
        icon: str,
        device_class: str,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, entry)
        self.coordinator = coordinator
        self._id = idx
        self.description = description
        self._icon = icon
        self._device_class = device_class

    @property
    def is_on(self):
        """Return status."""
        try:
            return self.coordinator.data[INPUTS][self._id]["state_info"]["unbalanced"]
        except KeyError as error:
            _LOGGER.error("Exception while parsing data: %s", error)

    @property
    def icon(self) -> str:
        """Return icon."""
        return self._icon

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return device class."""
        return self._device_class

    @property
    def name(self) -> str:
        """Return name."""
        return f"{self.description}"

    @property
    def id(self):
        """Return id."""
        return f"{DOMAIN}_{self._id}"

    @property
    def unique_id(self):
        """Return unique id."""
        return f"{DOMAIN}-{self._id}-{self.coordinator.api.hostip}"
