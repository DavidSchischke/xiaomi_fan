from homeassistant.const import ATTR_MODE

from ..._base.attributes import *
from ..._base.speed_level import *
from ..._base.features import *

AVAILABLE_ATTRIBUTES_FAN_ZA5 = {
    ATTR_ANGLE: "swing_mode_angle",
    ATTR_DIRECT_SPEED: "fan_speed",
    ATTR_NATURAL_SPEED: "fan_speed",
    ATTR_DELAY_OFF_COUNTDOWN: "power_off_time",
    ATTR_AC_POWER: "powersupply_attached",
    ATTR_OSCILLATE: "swing_mode",
    ATTR_MODE: "mode",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_BUZZER: "buzzer",
    ATTR_RAW_LED_BRIGHTNESS: "light",
    ATTR_LED_BRIGHTNESS: "light_enum",
    ATTR_TEMPERATURE: "temperature",
    ATTR_HUMIDITY: "humidity",
    ATTR_BUTTON_PRESSED: "buttons_pressed",
    # Fixed attributes
    ATTR_LED: "led",
    ATTR_RAW_SPEED: "speed_rpm",
    ATTR_BATTERY: "battery_supported",
    ATTR_BATTERY_STATE: "battery_state",
    ATTR_IONIZER: "anion",
}

FAN_PRESET_MODES_ZA5 = {
    SPEED_OFF: 0,
    FAN_SPEED_LEVEL1: 25,
    FAN_SPEED_LEVEL2: 50,
    FAN_SPEED_LEVEL3: 75,
    FAN_SPEED_LEVEL4: 100,
}

# FIXME: Add speed level 4
FAN_SPEEDS_ZA5 = list(FAN_PRESET_MODES_ZA5)
FAN_SPEEDS_ZA5.remove(SPEED_OFF)


FEATURE_FLAGS_FAN_ZA5 = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_SET_OSCILLATION_ANGLE
    | FEATURE_SET_NATURAL_MODE
    | FEATURE_SET_ANION
)
