"""The Loex Xsmart API integration."""

from __future__ import annotations

import json
import logging
import urllib.parse

import requests

from homeassistant.exceptions import HomeAssistantError

from .const import MAX_ROOMS, LoexSeason

_LOGGER = logging.getLogger(__name__)

_ENDPOINT = "https://xsmart.loex.it"


class loex_api:
    """Loex API class."""

    def __init__(self) -> None:
        """Initialize."""
        self.host = _ENDPOINT
        self.authorization = None
        self.device_id = None
        self.username = None
        self.password = None
        self.plant = None
        self.session = None

    def authenticate(
        self, username: str, password: str, device_id: str, plant: str
    ) -> bool:
        """Autenticate."""
        url = (
            self.host + "/jwt/?id=" + device_id + "&plant=" + urllib.parse.quote(plant)
        )

        self.session = requests.Session()
        response = self.session.get(
            url,
            auth=(username, password),
            timeout=10,
        )

        if response.status_code == 200:
            self.username = username
            self.password = password
            self.device_id = device_id
            self.plant = plant
            self.authorization = response.text
            return True

        self.session = None

        return False

    def get_data(self) -> dict:
        """Get data."""
        url = self.host + "/" + self.device_id + "/input.json"

        try:
            data = self.session.get(
                url,
                headers={"Authorization": self.authorization},
                timeout=10,
            )

            return self.extract_from_api_data(data.json())
        except requests.exceptions.RequestException as excep:
            self.session.close()
            self.authenticate(self.username, self.password, self.device_id, self.plant)
            raise CannotConnect from excep

    def save_data(self, payload):
        """Save data."""
        url = self.host + "/" + self.device_id + "/output.json"

        try:
            response = self.session.post(
                url,
                data=payload,
                headers={"Content-Type": "text/plain"},
                auth=(self.username, self.password),
            )

        except requests.exceptions.RequestException as excep:
            self.session.close()
            self.authenticate(self.username, self.password, self.device_id, self.plant)
            raise CannotConnect from excep

        if response.status_code != 200:
            raise WriteToRemoteDeviceError

    def parse_external_data(self, data: json) -> dict:
        """Parse external data."""
        external_data = {}

        try:
            external_data["ext_temp"] = data["t" + str(10011)] / 10
        except KeyError:
            external_data["ext_temp"] = "N/A"

        return external_data

    def parse_circuit_data(self, data: json) -> dict:
        """Parse circuit data."""
        circuit_data = {}

        try:
            circuit_data["name"] = data["t" + str(20001)]
        except KeyError:
            circuit_data["name"] = "N/A"

        # Home temperature maybe equivalent to the max of all the rooms
        try:
            circuit_data["home_temperature"] = data["t" + str(10003)] / 10
        except KeyError:
            circuit_data["home_temperature"] = "N/A"

        # Home humidity maybe equivalent to the max of all the rooms
        try:
            circuit_data["home_humidity"] = data["t" + str(10004)] / 10
        except KeyError:
            circuit_data["home_humidity"] = "N/A"

        # Set temperature -> it depends on the mode value
        try:
            circuit_data["temperature"] = data["t" + str(10101)] / 10
        except KeyError:
            circuit_data["temperature"] = "N/A"

        try:
            circuit_data["comfort_temperature"] = data["t" + str(18011)] / 10
        except KeyError:
            circuit_data["comfort_temperature"] = "N/A"

        try:
            circuit_data["eco_temperature"] = data["t" + str(18012)] / 10
        except KeyError:
            circuit_data["eco_temperature"] = "N/A"

        # ["circuit"]["mode"]:
        # 0 : OFF
        # 1 : COMFORT
        # 2 : ECO
        # 3 : AUTO
        try:
            circuit_data["mode"] = data["t" + str(10103)]
        except KeyError:
            circuit_data["mode"] = "N/A"

        # ["circuit"]["state"]:
        # 0 : OFF
        # 1 : HEAT or COOL depending on ["circuit"]["season"]
        # 2 : Unknwown
        # 3 : IDLE
        try:
            circuit_data["state"] = data["t" + str(10105)]
        except KeyError:
            circuit_data["state"] = "N/A"

        try:
            circuit_data["deumidification_active"] = data["t" + str(10107)]
        except KeyError:
            circuit_data["deumidification_active"] = "N/A"

        try:
            circuit_data["target_humidity"] = data["t" + str(18081)] / 10
        except KeyError:
            circuit_data["target_humidity"] = "N/A"

        try:
            circuit_data["histeresys_humidity"] = data["t" + str(18082)] / 10
        except KeyError:
            circuit_data["histeresys_humidity"] = "N/A"

        try:
            if data["t" + str(10042)] == 1 and data["t" + str(10043)] == 0:
                circuit_data["season"] = LoexSeason.LOEX_SUMMER
            else:
                circuit_data["season"] = LoexSeason.LOEX_WINTER
        except KeyError:
            circuit_data["season"] = "N/A"

        return circuit_data

    def parse_room_data(self, data: json, room_id) -> dict:
        """Parse room data."""
        room_data = {}

        # Extract Room name
        try:
            room_data["room_name"] = data["t" + str(20201 + 7 * room_id)]
        except KeyError:
            room_data["room_name"] = "N/A"

        # Extract validity
        try:
            idx = (
                room_id + 2 * (room_id >= 8) + 2 * (room_id >= 18) + 2 * (room_id >= 28)
            )
            room_data["validity"] = data["t" + str(11021 + 10 * idx)]
        except KeyError:
            room_data["validity"] = "N/A"

        # Extract current temperature
        try:
            idx = (
                room_id + 2 * (room_id >= 8) + 2 * (room_id >= 18) + 2 * (room_id >= 28)
            )
            room_data["temperature"] = data["t" + str(11022 + 10 * idx)] / 10
        except KeyError:
            room_data["temperature"] = "N/A"

        # Extract target temperature
        try:
            idx = (
                room_id + 2 * (room_id >= 8) + 2 * (room_id >= 18) + 2 * (room_id >= 28)
            )
            room_data["target_temperature"] = data["t" + str(11023 + 10 * idx)] / 10
        except KeyError:
            room_data["target_temperature"] = "N/A"

        # Extract humidity
        try:
            idx = (
                room_id + 2 * (room_id >= 8) + 2 * (room_id >= 18) + 2 * (room_id >= 28)
            )
            room_data["humidity"] = data["t" + str(11027 + 10 * idx)] / 10
        except KeyError:
            room_data["humidity"] = "N/A"

        # Extract output_valve
        try:
            idx = (
                room_id + 2 * (room_id >= 8) + 2 * (room_id >= 18) + 2 * (room_id >= 28)
            )
            room_data["output_valve"] = data["t" + str(11025 + 10 * idx)]
        except KeyError:
            room_data["output_valve"] = "N/A"

        # Extract hvac modes
        # mode 0 = AUTO
        # mode 1 = COMFORT
        # mode 2 = ECO
        # mode 3 = OFF
        try:
            idx = (
                room_id + 2 * (room_id >= 8) + 2 * (room_id >= 18) + 2 * (room_id >= 28)
            )
            room_data["room_mode"] = data["t" + str(11026 + 10 * idx)]
        except KeyError:
            room_data["room_mode"] = "N/A"

        return room_data

    def extract_from_api_data(self, data: json) -> dict:
        """Extract data from API."""
        aggregated_data = {}

        # Parse data related to external
        aggregated_data["external"] = self.parse_external_data(data)

        # Parse data for the circuit
        aggregated_data["circuit"] = self.parse_circuit_data(data)

        # Parse room data
        for room_id in range(MAX_ROOMS):
            aggregated_data[room_id] = self.parse_room_data(data, room_id)

        _LOGGER.debug("Data parsed from API:\n %s", aggregated_data)

        return aggregated_data

    def set_room_target_temperature(self, room_id, correction):
        """Set room target temperature."""
        idx = room_id + 2 * (room_id >= 8) + 2 * (room_id >= 18) + 2 * (room_id >= 28)

        payload = str(17621 + 10 * idx) + "=" + str(correction)

        self.save_data(payload)

    def set_circuit_target_temperature(self, mode, correction):
        """Set circuit target temperature."""
        if mode == 1:
            payload = str(18011) + "=" + str(correction)
        elif mode == 2:
            payload = str(18012) + "=" + str(correction)

        self.save_data(payload)

    def set_room_mode(self, room_id, mode):
        """Set room mode."""
        idx = room_id + 2 * (room_id >= 8) + 2 * (room_id >= 18) + 2 * (room_id >= 28)

        payload = str(17622 + 10 * idx) + "=" + str(mode)

        self.save_data(payload)

    def set_circuit_mode(self, mode):
        """Set circuit mode."""
        payload = str(18001) + "=" + str(mode)

        self.save_data(payload)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class WriteToRemoteDeviceError(HomeAssistantError):
    """Error to indicate we cannot connect."""
