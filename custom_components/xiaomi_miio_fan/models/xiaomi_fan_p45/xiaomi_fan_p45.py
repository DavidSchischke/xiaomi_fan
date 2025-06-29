import logging
from typing import Optional

from homeassistant.components.fan import FanEntityFeature
from miio import DeviceException

from .config import (
    FEATURE_FLAGS_FAN_P45,
    AVAILABLE_ATTRIBUTES_FAN_P45,
    FAN_PRESET_MODES_P45,
    FAN_SPEEDS_P45,
)
from .operation_mode_fan_p45 import OperationModeFanP45
from ..xiaomi_fan_miot import XiaomiFanMiot
from ..._base.features import FEATURE_SET_NATURAL_MODE


_LOGGER = logging.getLogger(__name__)


class XiaomiFanP45(XiaomiFanMiot):
    """Representation of a Xiaomi Fan P45."""

    def __init__(self, name, device, model, unique_id, retries, preset_modes_override):
        """Initialize the fan entity."""
        super().__init__(name, device, model, unique_id, retries, preset_modes_override)

        self._device_features = FEATURE_FLAGS_FAN_P45
        self._available_attributes = AVAILABLE_ATTRIBUTES_FAN_P45
        self._percentage = None
        self._preset_modes = list()
        if preset_modes_override is not None:
            self._preset_modes = preset_modes_override

        self._preset_mode = None
        self._oscillate = None
        self._natural_mode = False

        self._state_attrs.update({attribute: None for attribute in self._available_attributes})

    @property
    def supported_features(self) -> int:
        return (
            # FanEntityFeature.DIRECTION
            FanEntityFeature.OSCILLATE
            | FanEntityFeature.PRESET_MODE
            | FanEntityFeature.SET_SPEED
            | FanEntityFeature.TURN_OFF
            | FanEntityFeature.TURN_ON
        )

    async def async_update(self):
        if self._skip_update:
            self._skip_update = False
            return

        try:
            tmp = self._device.status()
            for k, v in tmp.data.items():
                print(f"{k}: {v} {type(v)}")
            state = await self.hass.async_add_executor_job(self._device.status)
            _LOGGER.debug("Got new state: %s", state)

            self._available = True
            self._percentage = state.fan_speed
            self._oscillate = state.oscillate
            self._natural_mode = state.mode == OperationModeFanP45.Nature
            self._state = state.power

            for preset_mode, value in FAN_PRESET_MODES_P45.items():
                if state.fan_level == value:
                    self._preset_mode = preset_mode
                    break

            self._state_attrs.update(
                {
                    key: self._extract_value_from_attribute(state, value)
                    for key, value in self._available_attributes.items()
                    if hasattr(state, value)
                }
            )
            self._retry = 0

        except DeviceException as ex:
            self._retry = self._retry + 1
            if self._retry < self._retries:
                _LOGGER.info(
                    "%s Got exception while fetching the state: %s , _retry=%s",
                    self.__class__.__name__,
                    ex,
                    self._retry,
                )
            else:
                self._available = False
                _LOGGER.error(
                    "%s Got exception while fetching the state: %s , _retry=%s",
                    self.__class__.__name__,
                    ex,
                    self._retry,
                )

    @property
    def percentage(self) -> Optional[int]:
        return self._percentage

    @property
    def speed_count(self) -> int:
        return len(FAN_SPEEDS_P45)

    @property
    def preset_modes(self):
        return self._preset_modes

    @property
    def preset_mode(self):
        if self._state:
            return self._preset_mode
        return None

    async def async_set_natural_mode_on(self):
        """Turn the natural mode on."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        await self._try_command(
            "Setting fan natural mode of the miio device failed.",
            self._device.set_mode,
            OperationModeFanP45.Nature,
        )

    async def async_set_natural_mode_off(self):
        """Turn the natural mode off."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        await self._try_command(
            "Setting fan natural mode of the miio device failed.",
            self._device.set_mode,
            OperationModeFanP45.Normal,
        )
