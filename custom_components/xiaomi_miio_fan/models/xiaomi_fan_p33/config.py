from ..._base.attributes import *
from ..._base.speed_level import *
from ..._base.features import *

AVAILABLE_ATTRIBUTES_FAN_P33 = {
    ATTR_MODE: "mode",
    ATTR_OSCILLATE: "oscillate",
    ATTR_ANGLE: "angle",
    ATTR_DELAY_OFF_COUNTDOWN: "delay_off_countdown",
    ATTR_LED: "led",
    ATTR_BUZZER: "buzzer",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_RAW_SPEED: "speed",
}

FAN_PRESET_MODES_P33 = {
    SPEED_OFF: 0,
    FAN_SPEED_LEVEL1: 1,
    FAN_SPEED_LEVEL2: 35,
    FAN_SPEED_LEVEL3: 70,
    FAN_SPEED_LEVEL4: 100,
}

FAN_SPEEDS_P33 = list(FAN_PRESET_MODES_P33)
FAN_SPEEDS_P33.remove(SPEED_OFF)

FEATURE_FLAGS_FAN_P33 = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_OSCILLATION_ANGLE
    | FEATURE_SET_NATURAL_MODE
)
