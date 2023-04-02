"""The Loex Xsmart API integration."""
from __future__ import annotations

import json
import logging
import requests

import urllib.parse

from homeassistant.exceptions import HomeAssistantError

from .const import LoexSeason, MAX_ROOMS

_LOGGER = logging.getLogger(__name__)

_ENDPOINT = "https://xsmart.loex.it"


class loex_api:
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
        # request data
        url = self.host + "/" + self.device_id + "/input.json"

        try:
            data = self.session.get(
                url,
                headers={"Authorization": self.authorization},
                timeout=10,
            )

            loex_data_structure = self.extract_from_api_data(data.json())
            return loex_data_structure
        except requests.exceptions.RequestException as excep:
            self.session.close()
            self.authenticate(self.username, self.password, self.device_id, self.plant)
            raise CannotConnect from excep

    def save_data(self, payload):
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

        # print(response.text)
        # print(response.request.url)
        # print(response.request.body)
        # print(response.request.headers)

        if response.status_code != 200:
            raise WriteToRemoteDeviceError

    def extract_from_api_data(self, data: json) -> dict:
        aggregated_data = {}

        # Get data related to external
        aggregated_data["external"] = {}
        try:
            aggregated_data["external"]["ext_temp"] = data["t" + str(10011)] / 10
        except KeyError:
            aggregated_data["external"]["ext_temp"] = "N/A"

        # Get data for the circuit
        aggregated_data["circuit"] = {}
        try:
            aggregated_data["circuit"]["name"] = data["t" + str(20001)]
        except KeyError:
            aggregated_data["circuit"]["name"] = "N/A"

        # Home temperature maybe equivalent to the max of all the rooms
        try:
            aggregated_data["circuit"]["home_temperature"] = data["t" + str(10003)] / 10
        except KeyError:
            aggregated_data["circuit"]["home_temperature"] = "N/A"

        # Home humidity maybe equivalent to the max of all the rooms
        try:
            aggregated_data["circuit"]["home_humidity"] = data["t" + str(10004)] / 10
        except KeyError:
            aggregated_data["circuit"]["home_humidity"] = "N/A"

        # Set temperature -> it depends on the mode value
        try:
            aggregated_data["circuit"]["temperature"] = data["t" + str(10101)] / 10
        except KeyError:
            aggregated_data["circuit"]["temperature"] = "N/A"

        try:
            aggregated_data["circuit"]["comfort_temperature"] = (
                data["t" + str(18011)] / 10
            )
        except KeyError:
            aggregated_data["circuit"]["comfort_temperature"] = "N/A"

        try:
            aggregated_data["circuit"]["eco_temperature"] = data["t" + str(18012)] / 10
        except KeyError:
            aggregated_data["circuit"]["eco_temperature"] = "N/A"

        # ["circuit"]["mode"]:
        # 0 : OFF
        # 1 : COMFORT
        # 2 : ECO
        # 3 : AUTO
        try:
            aggregated_data["circuit"]["mode"] = data["t" + str(10103)]
        except KeyError:
            aggregated_data["circuit"]["mode"] = "N/A"

        # ["circuit"]["state"]:
        # 0 : OFF
        # 1 : HEAT or COOL depending on ["circuit"]["season"] ??? TODO: Check correctness
        # 2 : Unknwown
        # 3 : IDLE
        try:
            aggregated_data["circuit"]["state"] = data["t" + str(10105)]
        except KeyError:
            aggregated_data["circuit"]["state"] = "N/A"

        try:
            aggregated_data["circuit"]["deumidification_active"] = data[
                "t" + str(10107)
            ]
        except KeyError:
            aggregated_data["circuit"]["deumidification_active"] = "N/A"

        try:
            aggregated_data["circuit"]["target_humidity"] = data["t" + str(18081)] / 10
        except KeyError:
            aggregated_data["circuit"]["target_humidity"] = "N/A"

        try:
            aggregated_data["circuit"]["histeresys_humidity"] = (
                data["t" + str(18082)] / 10
            )
        except KeyError:
            aggregated_data["circuit"]["histeresys_humidity"] = "N/A"

        try:
            if data["t" + str(10042)] == 1 and data["t" + str(10105)] == 0:
                aggregated_data["circuit"]["season"] = LoexSeason.LOEX_SUMMER
            else:
                aggregated_data["circuit"]["season"] = LoexSeason.LOEX_WINTER
        except KeyError:
            aggregated_data["circuit"]["season"] = "N/A"

        # Extract room data
        for room_id in range(MAX_ROOMS):
            aggregated_data[room_id] = {}

        # Extract Room name
        for room_id in range(MAX_ROOMS):
            try:
                aggregated_data[room_id]["room_name"] = data[
                    "t" + str(20201 + 7 * room_id)
                ]

            except KeyError:
                aggregated_data[room_id]["room_name"] = "N/A"

        # Extract validity
        for room_id in range(MAX_ROOMS):
            try:
                idx = (
                    room_id
                    + 2 * (room_id >= 8)
                    + 2 * (room_id >= 18)
                    + 2 * (room_id >= 28)
                )
                aggregated_data[room_id]["validity"] = data["t" + str(11021 + 10 * idx)]

            except KeyError:
                aggregated_data[room_id]["validity"] = "N/A"

        # Extract current temperature
        for room_id in range(MAX_ROOMS):
            try:
                idx = (
                    room_id
                    + 2 * (room_id >= 8)
                    + 2 * (room_id >= 18)
                    + 2 * (room_id >= 28)
                )
                aggregated_data[room_id]["temperature"] = (
                    data["t" + str(11022 + 10 * idx)] / 10
                )

            except KeyError:
                aggregated_data[room_id]["temperature"] = "N/A"

        # Extract target temperature
        for room_id in range(MAX_ROOMS):
            try:
                idx = (
                    room_id
                    + 2 * (room_id >= 8)
                    + 2 * (room_id >= 18)
                    + 2 * (room_id >= 28)
                )
                aggregated_data[room_id]["target_temperature"] = (
                    data["t" + str(11023 + 10 * idx)] / 10
                )

            except KeyError:
                aggregated_data[room_id]["target_temperature"] = "N/A"

        # Extract humidity
        for room_id in range(MAX_ROOMS):
            try:
                idx = (
                    room_id
                    + 2 * (room_id >= 8)
                    + 2 * (room_id >= 18)
                    + 2 * (room_id >= 28)
                )
                aggregated_data[room_id]["humidity"] = (
                    data["t" + str(11027 + 10 * idx)] / 10
                )

            except KeyError:
                aggregated_data[room_id]["humidity"] = "N/A"

        # Extract output_valve
        for room_id in range(MAX_ROOMS):
            try:
                idx = (
                    room_id
                    + 2 * (room_id >= 8)
                    + 2 * (room_id >= 18)
                    + 2 * (room_id >= 28)
                )
                aggregated_data[room_id]["output_valve"] = data[
                    "t" + str(11025 + 10 * idx)
                ]

            except KeyError:
                aggregated_data[room_id]["output_valve"] = "N/A"

        # Extract hvac modes
        # mode 0 = AUTO
        # mode 1 = COMFORT
        # mode 2 = ECO
        # mode 3 = OFF

        for room_id in range(MAX_ROOMS):
            try:
                idx = (
                    room_id
                    + 2 * (room_id >= 8)
                    + 2 * (room_id >= 18)
                    + 2 * (room_id >= 28)
                )
                aggregated_data[room_id]["room_mode"] = data[
                    "t" + str(11026 + 10 * idx)
                ]

            except KeyError:
                aggregated_data[room_id]["room_mode"] = "N/A"

        # print(aggregated_data)

        return aggregated_data

    def set_room_target_temperature(self, room_id, correction):
        idx = room_id + 2 * (room_id >= 8) + 2 * (room_id >= 18) + 2 * (room_id >= 28)

        payload = str(17621 + 10 * idx) + "=" + str(correction)

        self.save_data(payload)

    def set_circuit_target_temperature(self, mode, correction):
        if mode == 1:
            payload = str(18011) + "=" + str(correction)
        elif mode == 2:
            payload = str(18012) + "=" + str(correction)

        self.save_data(payload)

    def set_room_mode(self, room_id, mode):
        idx = room_id + 2 * (room_id >= 8) + 2 * (room_id >= 18) + 2 * (room_id >= 28)

        payload = str(17622 + 10 * idx) + "=" + str(mode)

        self.save_data(payload)

    def set_circuit_mode(self, mode):
        payload = str(18001) + "=" + str(mode)

        self.save_data(payload)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class WriteToRemoteDeviceError(HomeAssistantError):
    """Error to indicate we cannot connect."""
