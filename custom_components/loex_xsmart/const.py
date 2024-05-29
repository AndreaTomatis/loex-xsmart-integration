"""Constants for the Loex Xsmart Integration integration."""

import enum

DOMAIN = "loex_xsmart"

MANUFACTURER = "Loex"

DEVICE_NAME = "Xsmart"

DEVICE_VERSION = "2.8"

CONF_SYNC_INTERVAL = "sync_interval"

DEFAULT_SYNC_INTERVAL = 10  # seconds

MAX_ROOMS = 38

CONTROL_VALUE = 20


# HVAC LOEX MODES
class LoexCircuitMode(enum.IntEnum):
    """Circuit Mode Enumeration."""

    LOEX_MODE_OFF = 0
    LOEX_MODE_COMFORT = 1
    LOEX_MODE_ECO = 2
    LOEX_MODE_AUTO = 3
    LOEX_MODE_NA = -1


# HVAC LOEX STATE
class LoexCircuitState(enum.IntEnum):
    """Circuit State Enumeration."""

    LOEX_STATE_OFF = 0
    LOEX_STATE_HEAT_COOL = 1
    LOEX_MODE_UNK = 2
    LOEX_MODE_IDLE = 3
    LOEX_STATE_NA = -1


# HVAC LOEX ROOM MODES
class LoexRoomMode(enum.IntEnum):
    """Loex Room Mode Enumeration."""

    LOEX_ROOM_MODE_OFF = 3
    LOEX_ROOM_MODE_COMFORT = 1
    LOEX_ROOM_MODE_ECO = 2
    LOEX_ROOM_MODE_AUTO = 0
    LOEX_ROOM_MODE_NA = -1


# LOEX SEASONS
class LoexSeason(enum.IntEnum):
    """Loex Season Enumeration."""

    LOEX_WINTER = 0
    LOEX_SUMMER = 1
