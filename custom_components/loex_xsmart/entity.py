"""The Loex Xsmart Loex Entity."""

import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEVICE_NAME, DEVICE_VERSION, DOMAIN, MANUFACTURER
from .coordinator import loex_coordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)


class loex_entity(
    CoordinatorEntity,
):
    """Loex Entity clas."""

    def __init__(self, coordinator: loex_coordinator, entry) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.entry = entry

    @property
    def device_info(self):
        """Return Device Info."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.api.host)},
            "name": DEVICE_NAME,
            "model": DEVICE_VERSION,
            "manufacturer": MANUFACTURER,
        }

    @property
    def available(self) -> bool:
        """Return whether is available."""
        return self.coordinator.data

    @property
    def should_poll(self) -> bool:
        """Return the possibility to poll."""
        return False
