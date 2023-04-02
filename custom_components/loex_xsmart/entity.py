import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, DEVICE_NAME, DEVICE_VERSION

from .coordinator import loex_coordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)


class loex_entity(
    CoordinatorEntity,
):
    def __init__(self, coordinator: loex_coordinator, entry):
        super().__init__(coordinator)
        self.entry = entry

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.api.host)},
            "name": DEVICE_NAME,
            "model": DEVICE_VERSION,
            "manufacturer": MANUFACTURER,
        }

    @property
    def available(self) -> bool:
        return not not self.coordinator.data

    @property
    def should_poll(self) -> bool:
        return False
