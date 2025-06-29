"""
Support for Xiaomi Mi Smart Pedestal Fan.

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/fan.xiaomi_miio/
"""

import asyncio
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.fan import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_HOST,
    CONF_NAME,
    CONF_TOKEN,
)
from homeassistant.exceptions import PlatformNotReady
from miio import Device, DeviceException, Fan, Fan1C, FanLeshow, FanMiot, FanP5

from .models import *
from .config import *

from ._base.attributes import *
from ._base.features import *
from ._base.services import *
from ._base.speed_level import *

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Xiaomi Miio Fan"
DEFAULT_RETRIES = 20
DATA_KEY = "fan.xiaomi_miio_fan"
DOMAIN = "xiaomi_miio_fan"

CONF_MODEL = "model"
CONF_RETRIES = "retries"
CONF_PRESET_MODES_OVERRIDE = "preset_modes_override"


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_TOKEN): vol.All(cv.string, vol.Length(min=32, max=32)),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_MODEL): vol.In(
            [
                MODEL_FAN_V2,
                MODEL_FAN_V3,
                MODEL_FAN_SA1,
                MODEL_FAN_ZA1,
                MODEL_FAN_ZA3,
                MODEL_FAN_ZA4,
                MODEL_FAN_ZA5,
                MODEL_FAN_P5,
                MODEL_FAN_P8,
                MODEL_FAN_P9,
                MODEL_FAN_P10,
                MODEL_FAN_P11,
                MODEL_FAN_P15,
                MODEL_FAN_P18,
                MODEL_FAN_P30,
                MODEL_FAN_P33,
                MODEL_FAN_P39,
                MODEL_FAN_P45,
                MODEL_FAN_LESHOW_SS4,
                MODEL_FAN_1C,
            ]
        ),
        vol.Optional(CONF_RETRIES, default=DEFAULT_RETRIES): cv.positive_int,
        vol.Optional(CONF_PRESET_MODES_OVERRIDE, default=None): vol.Any(None, [cv.string]),
    }
)


AIRPURIFIER_SERVICE_SCHEMA = vol.Schema({vol.Optional(ATTR_ENTITY_ID): cv.entity_ids})

SERVICE_SCHEMA_LED_BRIGHTNESS = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_BRIGHTNESS): vol.All(vol.Coerce(int), vol.Clamp(min=0, max=2))}
)

SERVICE_SCHEMA_RAW_LED_BRIGHTNESS = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_BRIGHTNESS): vol.Coerce(int)}
)

SERVICE_SCHEMA_OSCILLATION_ANGLE = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_ANGLE): cv.positive_int}
)

SERVICE_SCHEMA_DELAY_OFF = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_DELAY_OFF_COUNTDOWN): cv.positive_int}
)

SERVICE_TO_METHOD = {
    SERVICE_SET_BUZZER_ON: {"method": "async_set_buzzer_on"},
    SERVICE_SET_BUZZER_OFF: {"method": "async_set_buzzer_off"},
    SERVICE_SET_CHILD_LOCK_ON: {"method": "async_set_child_lock_on"},
    SERVICE_SET_CHILD_LOCK_OFF: {"method": "async_set_child_lock_off"},
    SERVICE_SET_LED_BRIGHTNESS: {
        "method": "async_set_led_brightness",
        "schema": SERVICE_SCHEMA_LED_BRIGHTNESS,
    },
    SERVICE_SET_RAW_LED_BRIGHTNESS: {
        "method": "async_set_raw_led_brightness",
        "schema": SERVICE_SCHEMA_RAW_LED_BRIGHTNESS,
    },
    SERVICE_SET_OSCILLATION_ANGLE: {
        "method": "async_set_oscillation_angle",
        "schema": SERVICE_SCHEMA_OSCILLATION_ANGLE,
    },
    SERVICE_SET_DELAY_OFF: {
        "method": "async_set_delay_off",
        "schema": SERVICE_SCHEMA_DELAY_OFF,
    },
    SERVICE_SET_NATURAL_MODE_ON: {"method": "async_set_natural_mode_on"},
    SERVICE_SET_NATURAL_MODE_OFF: {"method": "async_set_natural_mode_off"},
    SERVICE_SET_ANION_ON: {"method": "async_set_anion_on"},
    SERVICE_SET_ANION_OFF: {"method": "async_set_anion_off"},
}


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the miio fan device from config."""
    if DATA_KEY not in hass.data:
        hass.data[DATA_KEY] = {}

    host = config[CONF_HOST]
    token = config[CONF_TOKEN]
    name = config[CONF_NAME]
    model = config.get(CONF_MODEL)
    retries = config[CONF_RETRIES]
    preset_modes_override = config.get(CONF_PRESET_MODES_OVERRIDE)

    _LOGGER.info("Initializing with host %s (token %s...)", host, token[:5])
    unique_id = None

    if model is None:
        try:
            miio_device = Device(host, token)
            device_info = await hass.async_add_executor_job(miio_device.info)
            model = device_info.model
            unique_id = f"{model}-{device_info.mac_address}"
            _LOGGER.info(
                "%s %s %s detected",
                model,
                device_info.firmware_version,
                device_info.hardware_version,
            )
        except DeviceException as ex:
            raise PlatformNotReady from ex

    if model in [
        MODEL_FAN_V2,
        MODEL_FAN_V3,
        MODEL_FAN_SA1,
        MODEL_FAN_ZA1,
        MODEL_FAN_ZA3,
        MODEL_FAN_ZA4,
    ]:
        fan = Fan(host, token, model=model)
        device = XiaomiFan(name, fan, model, unique_id, retries, preset_modes_override)
    elif model == MODEL_FAN_P5:
        fan = FanP5(host, token, model=model)
        device = XiaomiFanP5(name, fan, model, unique_id, retries, preset_modes_override)
    elif model == MODEL_FAN_P9:
        fan = FanMiot(host, token, model=model)
        device = XiaomiFanMiot(name, fan, model, unique_id, retries, preset_modes_override)
    elif model in [MODEL_FAN_P10, MODEL_FAN_P18, MODEL_FAN_P30]:
        fan = FanMiot(host, token, model=MODEL_FAN_P10)
        device = XiaomiFanMiot(name, fan, model, unique_id, retries, preset_modes_override)
    elif model in [MODEL_FAN_P11, MODEL_FAN_P15]:
        fan = FanMiot(host, token, model=MODEL_FAN_P11)
        device = XiaomiFanMiot(name, fan, model, unique_id, retries, preset_modes_override)
    elif model == MODEL_FAN_LESHOW_SS4:
        fan = FanLeshow(host, token, model=model)
        device = XiaomiFanLeshow(name, fan, model, unique_id, retries, preset_modes_override)
    elif model in [MODEL_FAN_1C, MODEL_FAN_P8]:
        fan = Fan1C(host, token, model=model)
        device = XiaomiFan1C(name, fan, model, unique_id, retries, preset_modes_override)
    elif model == MODEL_FAN_ZA5:
        fan = FanZA5(host, token, model=model)
        device = XiaomiFanZA5(name, fan, model, unique_id, retries, preset_modes_override)
    elif model == MODEL_FAN_P33:
        fan = FanP33(host, token, model=model)
        device = XiaomiFanP33(name, fan, model, unique_id, retries, preset_modes_override)
    elif model == MODEL_FAN_P39:
        fan = FanP39(host, token, model=model)
        device = XiaomiFanP39(name, fan, model, unique_id, retries, preset_modes_override)
    elif model == MODEL_FAN_P45:
        fan = FanP45(host, token, model=model)
        device = XiaomiFanP45(name, fan, model, unique_id, retries, preset_modes_override)
    else:
        _LOGGER.error(
            "Unsupported device found! Please create an issue at "
            "https://github.com/syssi/xiaomi_fan/issues "
            "and provide the following data: %s",
            model,
        )
        return False

    hass.data[DATA_KEY][host] = device
    async_add_entities([device], update_before_add=True)

    async def async_service_handler(service):
        """Map services to methods on XiaomiFan."""
        method = SERVICE_TO_METHOD.get(service.service)
        params = {key: value for key, value in service.data.items() if key != ATTR_ENTITY_ID}
        entity_ids = service.data.get(ATTR_ENTITY_ID)
        if entity_ids:
            devices = [
                device for device in hass.data[DATA_KEY].values() if device.entity_id in entity_ids
            ]
        else:
            devices = hass.data[DATA_KEY].values()

        update_tasks = []
        for device in devices:
            if not hasattr(device, method["method"]):
                continue
            await getattr(device, method["method"])(**params)
            update_tasks.append(asyncio.create_task(device.async_update_ha_state(True)))

        if update_tasks:
            await asyncio.wait(update_tasks)

    for air_purifier_service in SERVICE_TO_METHOD:
        schema = SERVICE_TO_METHOD[air_purifier_service].get("schema", AIRPURIFIER_SERVICE_SCHEMA)
        hass.services.async_register(
            DOMAIN, air_purifier_service, async_service_handler, schema=schema
        )
