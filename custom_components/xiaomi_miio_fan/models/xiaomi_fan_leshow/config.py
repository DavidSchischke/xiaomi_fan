from homeassistant.const import ATTR_MODE
from ..._base.attributes import *
from ..._base.features import FEATURE_SET_BUZZER

FEATURE_FLAGS_FAN_LESHOW_SS4 = FEATURE_SET_BUZZER

AVAILABLE_ATTRIBUTES_FAN_LESHOW_SS4 = {
    ATTR_MODE: "mode",
    ATTR_RAW_SPEED: "speed",
    ATTR_BUZZER: "buzzer",
    ATTR_OSCILLATE: "oscillate",
    ATTR_DELAY_OFF_COUNTDOWN: "delay_off_countdown",
    ATTR_ERROR_DETECTED: "error_detected",
}
