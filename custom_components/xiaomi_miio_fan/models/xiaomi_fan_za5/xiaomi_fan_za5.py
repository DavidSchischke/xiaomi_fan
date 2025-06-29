import logging
from typing import Optional

from homeassistant.components.fan import FanEntityFeature
from miio import DeviceException
from miio.fan_common import OperationMode, LedBrightness

from .config import (
    FEATURE_FLAGS_FAN_ZA5,
    AVAILABLE_ATTRIBUTES_FAN_ZA5,
    FAN_PRESET_MODES_ZA5,
)
from ..xiaomi_fan import XiaomiFan
from ..xiaomi_fan.config import FAN_PRESET_MODE_VALUES
from ..._base.features import (
    FEATURE_SET_NATURAL_MODE,
    FEATURE_SET_LED_BRIGHTNESS,
    FEATURE_SET_ANION,
)


_LOGGER = logging.getLogger(__name__)


class XiaomiFanZA5(XiaomiFan):
    """Representation of a Xiaomi Fan ZA5."""

    def __init__(self, name, device, model, unique_id, retries, preset_modes_override):
        """Initialize the fan entity."""
        super().__init__(name, device, model, unique_id, retries, preset_modes_override)

        self._device_features = FEATURE_FLAGS_FAN_ZA5
        self._available_attributes = AVAILABLE_ATTRIBUTES_FAN_ZA5
        self._preset_modes = list(FAN_PRESET_MODES_ZA5)
        if preset_modes_override is not None:
            self._preset_modes = preset_modes_override

        self._state_attrs.update({attribute: None for attribute in self._available_attributes})

    @property
    def supported_features(self) -> int:
        return (
            FanEntityFeature.DIRECTION
            | FanEntityFeature.OSCILLATE
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
            state = await self.hass.async_add_executor_job(self._device.status)
            _LOGGER.debug("Got new state: %s", state)

            self._available = True
            self._percentage = state.fan_speed
            self._oscillate = state.swing_mode
            self._natural_mode = state.mode == OperationMode.Nature
            self._state = state.power

            for preset_mode, value in FAN_PRESET_MODES_ZA5.items():
                if state.fan_level == value:
                    self._preset_mode = preset_mode

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
        return 100

    @property
    def preset_modes(self):
        return self._preset_modes

    @property
    def preset_mode(self):
        if self._state:
            return self._preset_mode
        return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        if not self._state:
            await self._try_command("Turning the miio device on failed.", self._device.on)
        await self._try_command(
            "Setting preset mode of the miio device failed.",
            self._device.set_speed,
            FAN_PRESET_MODE_VALUES[preset_mode],
        )

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        _LOGGER.debug("Setting the fan speed percentage to: %s", percentage)

        if percentage == 0:
            await self.async_turn_off()
            return

        if not self._state:
            await self._try_command("Turning the miio device on failed.", self._device.on)
        await self._try_command(
            "Setting preset mode of the miio device failed.",
            self._device.set_speed,
            percentage,
        )

    async def async_oscillate(self, oscillating: bool) -> None:
        """Set oscillation."""
        if oscillating:
            await self._try_command(
                "Setting oscillate on of the miio device failed.",
                self._device.set_oscillate,
                True,
            )
        else:
            await self._try_command(
                "Setting oscillate off of the miio device failed.",
                self._device.set_oscillate,
                False,
            )

    async def async_set_delay_off(self, delay_off_countdown: int) -> None:
        """Set scheduled off timer in minutes."""

        await self._try_command(
            "Setting delay off miio device failed.",
            self._device.delay_off,
            delay_off_countdown * 60,
        )

    async def async_set_natural_mode_on(self):
        """Turn the natural mode on."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        await self._try_command(
            "Setting fan natural mode of the miio device failed.",
            self._device.set_mode,
            OperationMode.Nature,
        )

    async def async_set_natural_mode_off(self):
        """Turn the natural mode off."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        await self._try_command(
            "Setting fan natural mode of the miio device failed.",
            self._device.set_mode,
            OperationMode.Normal,
        )

    async def async_set_led_brightness(self, brightness: int = 2):
        """Set the led brightness."""
        brightness = LedBrightness(brightness)
        if brightness == LedBrightness.Bright:
            brightness = 100
        elif brightness == LedBrightness.Dim:
            brightness = 1
        else:
            brightness = 0
        await self.async_set_raw_led_brightness(brightness)

    async def async_set_raw_led_brightness(self, brightness: int):
        """Set the raw led brightness."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        await self._try_command(
            "Setting the led brightness of the miio device failed.",
            self._device.set_light,
            brightness,
        )

    async def async_set_anion_on(self):
        """Turn anion on."""
        if self._device_features & FEATURE_SET_ANION == 0:
            return

        await self._try_command(
            "Setting anion of the miio device failed.",
            self._device.set_anion,
            True,
        )

    async def async_set_anion_off(self):
        """Turn anion off."""
        if self._device_features & FEATURE_SET_ANION == 0:
            return

        await self._try_command(
            "Setting anion of the miio device failed.",
            self._device.set_anion,
            False,
        )
