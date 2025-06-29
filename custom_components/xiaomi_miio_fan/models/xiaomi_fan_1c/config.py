from homeassistant.const import ATTR_MODE
from ..xiaomi_fan.config import FEATURE_FLAGS_FAN

from ..._base.attributes import (
    ATTR_RAW_SPEED,
    ATTR_BUZZER,
    ATTR_OSCILLATE,
    ATTR_DELAY_OFF_COUNTDOWN,
    ATTR_LED,
    ATTR_CHILD_LOCK,
)
from ..._base.speed_level import *

AVAILABLE_ATTRIBUTES_FAN_1C = {
    ATTR_MODE: "mode",
    ATTR_RAW_SPEED: "speed",
    ATTR_BUZZER: "buzzer",
    ATTR_OSCILLATE: "oscillate",
    ATTR_DELAY_OFF_COUNTDOWN: "delay_off_countdown",
    ATTR_LED: "led",
    ATTR_CHILD_LOCK: "child_lock",
}

FAN_PRESET_MODES_1C = {
    SPEED_OFF: 0,
    FAN_SPEED_LEVEL1: 1,
    FAN_SPEED_LEVEL2: 2,
    FAN_SPEED_LEVEL3: 3,
}

FAN_SPEEDS_1C = list(FAN_PRESET_MODES_1C)
FAN_SPEEDS_1C.remove(SPEED_OFF)

FEATURE_FLAGS_FAN_1C = FEATURE_FLAGS_FAN
