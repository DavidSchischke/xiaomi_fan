from homeassistant.const import ATTR_MODE

from ..._base.attributes import *
from ..._base.speed_level import *

from ..xiaomi_fan_p39.config import FEATURE_FLAGS_FAN_P39

AVAILABLE_ATTRIBUTES_FAN_P45 = {
    ATTR_MODE: "mode",
    ATTR_OSCILLATE: "oscillate",
    ATTR_ANGLE: "angle",
    ATTR_DELAY_OFF_COUNTDOWN: "delay_off_countdown",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_RAW_SPEED: "speed",
    ATTR_LED: "led",
}

FAN_PRESET_MODES_P45 = {
    SPEED_OFF: 0,
    FAN_SPEED_LEVEL1: 1,
    FAN_SPEED_LEVEL2: 35,
    FAN_SPEED_LEVEL3: 70,
    FAN_SPEED_LEVEL4: 100,
}

FAN_SPEEDS_P45 = list(FAN_PRESET_MODES_P45)
FAN_SPEEDS_P45.remove(SPEED_OFF)

FEATURE_FLAGS_FAN_P45 = FEATURE_FLAGS_FAN_P39
