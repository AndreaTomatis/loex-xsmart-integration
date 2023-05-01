"""Constants for the Loex Xsmart Integration integration."""

from homeassistant.backports.enum import StrEnum

DOMAIN = "loex_xsmart"

MANUFACTURER = "Loex"

DEVICE_NAME = "Xsmart"

DEVICE_VERSION = "2.8"

CONF_SYNC_INTERVAL = "sync_interval"

DEFAULT_SYNC_INTERVAL = 10  # seconds

MAX_ROOMS = 38

CONTROL_VALUE = 20


# HVAC LOEX MODES
class LoexCircuitMode(StrEnum):
    LOEX_MODE_OFF = "0"
    LOEX_MODE_COMFORT = "1"
    LOEX_MODE_ECO = "2"
    LOEX_MODE_AUTO = "3"


# HVAC LOEX ROOM MODES
class LoexRoomMode(StrEnum):
    LOEX_ROOM_MODE_OFF = "3"
    LOEX_ROOM_MODE_COMFORT = "1"
    LOEX_ROOM_MODE_ECO = "2"
    LOEX_ROOM_MODE_AUTO = "0"


# LOEX SEASONS
class LoexSeason(StrEnum):
    LOEX_WINTER = "0"
    LOEX_SUMMER = "1"
