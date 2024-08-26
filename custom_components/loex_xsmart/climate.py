"""Climate Platform for Loex Xsmart Integration."""

import logging
from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    PRESET_COMFORT,
    PRESET_ECO,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant

from .const import (
    CONTROL_VALUE,
    DOMAIN,
    LoexCircuitMode,
    LoexCircuitState,
    LoexRoomMode,
    LoexSeason,
)
from .coordinator import loex_coordinator
from .entity import loex_entity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Add entries."""
    coordinator: loex_coordinator

    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for room_id in coordinator.data:
        if room_id == "external":
            continue

        if room_id == "circuit":
            main_circuit = loex_main_circuit(
                coordinator,
                entry,
                "main_circuit",
                coordinator.data["circuit"]["name"],
                "mdi:thermostat",
            )
            entities.extend([main_circuit])
            continue

        if (coordinator.data[room_id]["validity"]) == 6:
            thermostat = loex_thermostat(
                coordinator,
                entry,
                room_id,
                coordinator.data[room_id]["room_name"],
                "mdi:thermostat",
            )
            entities.extend([thermostat])

    async_add_entities(entities, True)


class loex_main_circuit(loex_entity, ClimateEntity):
    """Create Main circuit."""

    def __init__(
        self,
        coordinator: loex_coordinator,
        entry: ConfigEntry,
        idx: str,
        description: str,
        icon: str,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, entry)
        self._id = idx
        self.description = description
        self._icon = icon
        self.current_temperature_value = None
        self.current_humidity_value = None
        # TODO: Remove by  2025.1
        self._enable_turn_on_off_backwards_compatibility = False

        self._hvac_mode = HVACMode.OFF
        self._preset_mode = PRESET_COMFORT

        self._preset_list = [
            PRESET_ECO,
            PRESET_COMFORT,
        ]

        self._hvac_list = [
            HVACMode.HEAT_COOL,
            HVACMode.OFF,
        ]

    async def async_turn_on(self):
        """Turn the entity on."""
        if self._hvac_mode == HVACMode.HEAT_COOL:
            if self._preset_mode == PRESET_COMFORT:
                await self.coordinator.async_set_circuit_mode(
                    LoexCircuitMode.LOEX_MODE_COMFORT
                )
            elif self._preset_mode == PRESET_ECO:
                await self.coordinator.async_set_circuit_mode(
                    LoexCircuitMode.LOEX_MODE_ECO
                )
        elif self._hvac_mode == HVACMode.AUTO:
            await self.coordinator.async_set_circuit_mode(
                LoexCircuitMode.LOEX_MODE_AUTO
            )

    async def async_turn_off(self):
        """Turn the entity off."""
        await self.coordinator.async_set_circuit_mode(LoexCircuitMode.LOEX_MODE_OFF)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set Temperature."""

        mode = self.coordinator.data["circuit"]["mode"]

        if mode == LoexCircuitMode.LOEX_MODE_OFF:
            return  # TODO: define what to do
        if mode == LoexCircuitMode.LOEX_MODE_AUTO:
            return  # Do Nothing

        target = int(kwargs.get("temperature") * 10)

        await self.coordinator.async_set_circuit_target_temperature(mode, target)

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set HVAC Mode."""

        # Turn on the device if not already on
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.async_set_circuit_mode(LoexCircuitMode.LOEX_MODE_OFF)
        elif hvac_mode == HVACMode.HEAT_COOL:
            if self._preset_mode == PRESET_COMFORT:
                await self.coordinator.async_set_circuit_mode(
                    LoexCircuitMode.LOEX_MODE_COMFORT
                )
            elif self._preset_mode == PRESET_ECO:
                await self.coordinator.async_set_circuit_mode(
                    LoexCircuitMode.LOEX_MODE_ECO
                )
        elif hvac_mode == HVACMode.AUTO:
            await self.coordinator.async_set_circuit_mode(
                LoexCircuitMode.LOEX_MODE_AUTO
            )
        else:
            _LOGGER.warning(
                "Unsupported mode for this device (%s): %s", self.name, hvac_mode
            )
            return

    @property
    def hvac_mode(self) -> str | None:
        """Return current operation."""
        if self.coordinator.data["circuit"]["mode"] == LoexCircuitMode.LOEX_MODE_OFF:
            return HVACMode.OFF
        if self.coordinator.data["circuit"]["mode"] == LoexCircuitMode.LOEX_MODE_AUTO:
            return HVACMode.AUTO

        season = self.coordinator.data["circuit"]["season"]
        if season == LoexSeason.LOEX_WINTER:
            return HVACMode.HEAT
        if season == LoexSeason.LOEX_SUMMER:
            return HVACMode.COOL
        return None

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """List of available operation modes."""
        return self._hvac_list

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        # From specification 18011 and 18012 MODBUS
        return 10.0

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        # From specification 18011 and 18012 MODBUS
        return 30.0

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.TURN_OFF
        )

    @property
    def hvac_action(self) -> HVACAction:
        """Return the current running hvac operation if supported.

        Need to be one of CURRENT_HVAC_*.
        """
        season = self.coordinator.data["circuit"]["season"]
        state = self.coordinator.data["circuit"]["state"]

        if state == LoexCircuitState.LOEX_MODE_IDLE:
            return HVACAction.IDLE
        if state == LoexCircuitState.LOEX_STATE_HEAT_COOL:
            if season == LoexSeason.LOEX_SUMMER:
                return HVACAction.COOLING
            if season == LoexSeason.LOEX_WINTER:
                return HVACAction.HEATING
        if state == LoexCircuitState.LOEX_STATE_OFF:
            return HVACAction.OFF
        return None

    @property
    def current_temperature(self) -> float:
        """Get Current Temperature."""
        value = self.coordinator.data["circuit"]["home_temperature"]
        if (
            self.current_temperature_value is None
            or abs(value - self.current_temperature_value) < CONTROL_VALUE
        ):
            self.current_temperature_value = value

        return self.current_temperature_value

    @property
    def target_temperature(self) -> float:
        """Get Target Temperature."""
        return self.coordinator.data["circuit"]["temperature"]

    @property
    def target_humidity(self) -> int:
        """Get Target Humidity."""
        return self.coordinator.data["circuit"]["target_humidity"]

    @property
    def current_humidity(self) -> int:
        """Get Current Humidity."""
        value = self.coordinator.data["circuit"]["home_humidity"]
        if (
            self.current_humidity_value is None
            or abs(value - self.current_humidity_value) < CONTROL_VALUE
        ):
            self.current_humidity_value = value

        return self.current_humidity_value

    @property
    def preset_mode(self) -> str:
        """Return current operation."""
        preset_mode = self.coordinator.data["circuit"]["mode"]
        if preset_mode == LoexCircuitMode.LOEX_MODE_COMFORT:
            self._preset_mode = PRESET_COMFORT
        elif preset_mode == LoexCircuitMode.LOEX_MODE_ECO:
            self._preset_mode = PRESET_ECO

        return self._preset_mode

    @property
    def preset_modes(self) -> list[str]:
        """Get Preset Modes."""
        return self._preset_list

    @property
    def temperature_unit(self) -> str:
        """Get Temperature Unit."""
        return UnitOfTemperature.CELSIUS

    @property
    def icon(self) -> str:
        """Get Icon."""
        return self._icon

    @property
    def name(self) -> str:
        """Get Name."""
        return f"{self.description}"

    @property
    def id(self) -> str:
        """Get Id."""
        return f"{DOMAIN}_{self._id}"

    @property
    def unique_id(self) -> str:
        """Get Unique Id."""
        return f"{DOMAIN}-{self._id}-{self.coordinator.api.host}"


class loex_thermostat(loex_entity, ClimateEntity):
    """Create Loex Thermostat."""

    def __init__(
        self,
        coordinator: loex_coordinator,
        entry: ConfigEntry,
        idx: str,
        description: str,
        icon: str,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, entry)
        self._id = idx
        self.description = description
        self._icon = icon
        self.current_temperature_value = None
        self.current_humidity_value = None
        self.set_target_temperature_pending = False
        self.set_target_temperature = -1

        self._preset_mode = PRESET_COMFORT
        self._room_mode = HVACMode.OFF
        # TODO: Remove by  2025.1
        self._enable_turn_on_off_backwards_compatibility = False

        self._hvac_list = [
            HVACMode.AUTO,
            HVACMode.HEAT_COOL,
            HVACMode.OFF,
        ]

        self._preset_list = [
            PRESET_ECO,
            PRESET_COMFORT,
        ]

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set Hvac Mode."""
        # Turn on the device if not already on
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.async_set_room_mode(
                self._id, LoexRoomMode.LOEX_ROOM_MODE_OFF
            )
        elif hvac_mode == HVACMode.HEAT_COOL:
            if self._preset_mode == PRESET_COMFORT:
                await self.coordinator.async_set_room_mode(
                    self._id, LoexRoomMode.LOEX_ROOM_MODE_COMFORT
                )
            elif self._preset_mode == PRESET_ECO:
                await self.coordinator.async_set_room_mode(
                    self._id, LoexRoomMode.LOEX_ROOM_MODE_ECO
                )
        elif hvac_mode == HVACMode.AUTO:
            await self.coordinator.async_set_room_mode(
                self._id, LoexRoomMode.LOEX_ROOM_MODE_AUTO
            )
        else:
            _LOGGER.warning(
                "Unsupported mode for this device (%s): %s", self.name, hvac_mode
            )
            return

    async def async_turn_on(self):
        """Turn the entity on."""
        if self._room_mode == HVACMode.HEAT_COOL:
            if self._preset_mode == PRESET_COMFORT:
                await self.coordinator.async_set_room_mode(
                    self._id, LoexRoomMode.LOEX_ROOM_MODE_COMFORT
                )
            elif self._preset_mode == PRESET_ECO:
                await self.coordinator.async_set_room_mode(
                    self._id, LoexRoomMode.LOEX_ROOM_MODE_ECO
                )
        elif self._room_mode == HVACMode.AUTO:
            await self.coordinator.async_set_room_mode(
                self._id, LoexRoomMode.LOEX_ROOM_MODE_AUTO
            )

    async def async_turn_off(self):
        """Turn the entity off."""
        await self.coordinator.async_set_room_mode(
            self._id, LoexRoomMode.LOEX_ROOM_MODE_OFF
        )

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set Temperature."""
        if self.coordinator.data["circuit"]["mode"] == LoexRoomMode.LOEX_ROOM_MODE_AUTO:
            return  # TODO: define what to do
        if self.coordinator.data["circuit"]["mode"] == LoexRoomMode.LOEX_ROOM_MODE_OFF:
            return  # DO Nothing

        target = (
            kwargs.get("temperature") - self.coordinator.data["circuit"]["temperature"]
        ) * 10

        self.set_target_temperature_pending = True
        self.set_target_temperature = kwargs.get("temperature")

        await self.coordinator.async_set_room_target_temperature(self._id, int(target))

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set preset mode."""
        # await self._device.async_set_mode(ThermostatV3Mode[preset_mode])
        _LOGGER.debug("Set present mode %s", preset_mode)

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current operation."""
        state = self.coordinator.data["circuit"]["state"]

        if state == LoexCircuitState.LOEX_STATE_OFF:
            # If the circuit is off we set the room to off.
            self._room_mode = HVACMode.OFF
        else:
            mode = self.coordinator.data[self._id]["room_mode"]
            if mode == LoexRoomMode.LOEX_ROOM_MODE_OFF:
                self._room_mode = HVACMode.OFF
            elif mode == LoexRoomMode.LOEX_ROOM_MODE_AUTO:
                self._room_mode = HVACMode.AUTO
            else:
                season = self.coordinator.data["circuit"]["season"]
                if season == LoexSeason.LOEX_WINTER:
                    self._room_mode = HVACMode.HEAT
                elif season == LoexSeason.LOEX_SUMMER:
                    self._room_mode = HVACMode.COOL

        return self._room_mode

    @property
    def preset_mode(self) -> str:
        """Return current active preset."""
        preset_mode = self.coordinator.data[self._id]["room_mode"]
        if preset_mode == LoexCircuitMode.LOEX_MODE_COMFORT:
            self._preset_mode = PRESET_COMFORT
        elif preset_mode == LoexCircuitMode.LOEX_MODE_ECO:
            self._preset_mode = PRESET_ECO

        return self._preset_mode

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """List of available operation modes."""
        return self._hvac_list

    @property
    def preset_modes(self) -> list[str]:
        """Get preset modes."""
        return self._preset_list

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return self.coordinator.data["circuit"]["temperature"] - 4

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return self.coordinator.data["circuit"]["temperature"] + 4

    @property
    def _is_device_active(self):
        """If the toggleable device is currently active."""
        # return self._is_device_active_function(forced=False)
        return True

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Return the list of supported features."""
        return (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.TURN_OFF
        )

    @property
    def hvac_action(self) -> HVACAction:
        """Return the current running hvac operation."""

        season = self.coordinator.data["circuit"]["season"]
        state = self.coordinator.data["circuit"]["state"]

        if state == LoexCircuitState.LOEX_STATE_OFF:
            return HVACAction.OFF

        valve_output = self.coordinator.data[self._id]["output_valve"]
        if valve_output > 0:
            if season == LoexSeason.LOEX_SUMMER:
                return HVACAction.COOLING
            if season == LoexSeason.LOEX_WINTER:
                return HVACAction.HEATING

        return HVACAction.IDLE

    @property
    def current_temperature(self) -> float:
        """Get current temperature."""
        value = self.coordinator.data[self._id]["temperature"]
        if (
            self.current_temperature_value is None
            or abs(value - self.current_temperature_value) < CONTROL_VALUE
        ):
            self.current_temperature_value = value

        return self.current_temperature_value

    @property
    def target_temperature(self) -> float:
        """Get target temperature."""
        # This check is to avoid the problem that the data sent from the sistem get the update after some time
        if self.set_target_temperature_pending:
            if (
                self.coordinator.data[self._id]["target_temperature"]
                == self.set_target_temperature
            ):
                self.set_target_temperature_pending = False

            return self.set_target_temperature

        return self.coordinator.data[self._id]["target_temperature"]

    @property
    def current_humidity(self) -> int:
        """Get current humidity."""
        value = self.coordinator.data[self._id]["humidity"]
        if (
            self.current_humidity_value is None
            or abs(value - self.current_humidity_value) < CONTROL_VALUE
        ):
            self.current_humidity_value = value

        return self.current_humidity_value

    @property
    def temperature_unit(self) -> str:
        """Get temperature unit."""
        return UnitOfTemperature.CELSIUS

    @property
    def icon(self) -> str:
        """Get icon."""
        return self._icon

    @property
    def name(self) -> str:
        """Get name."""
        return f"{self.description}"

    @property
    def id(self) -> str:
        """Get id."""
        return f"{DOMAIN}_{self._id}"

    @property
    def unique_id(self) -> str:
        """Get unique id."""
        return f"{DOMAIN}-{self._id}-{self.coordinator.api.host}"
