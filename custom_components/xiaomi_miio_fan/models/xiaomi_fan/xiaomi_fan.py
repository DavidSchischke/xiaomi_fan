import logging

from homeassistant.components.fan import FanEntityFeature
from miio import DeviceException
from miio.fan_common import MoveDirection, LedBrightness

from .config import *
from ..._base import XiaomiGenericDevice
from ..._base.features import (
    FEATURE_SET_LED_BRIGHTNESS,
    FEATURE_SET_OSCILLATION_ANGLE,
    FEATURE_SET_NATURAL_MODE,
)


_LOGGER = logging.getLogger(__name__)


class XiaomiFan(XiaomiGenericDevice):
    """Representation of a Xiaomi Pedestal Fan."""

    def __init__(self, name, device, model, unique_id, retries, preset_modes_override):
        """Initialize the fan entity."""
        super().__init__(name, device, model, unique_id, retries, preset_modes_override)

        self._device_features = FEATURE_FLAGS_FAN
        self._available_attributes = AVAILABLE_ATTRIBUTES_FAN
        self._percentage = None
        self._preset_modes = list(FAN_PRESET_MODES)
        if preset_modes_override is not None:
            self._preset_modes = preset_modes_override

        self._preset_mode = None
        self._oscillate = None
        self._natural_mode = False

        self._state_attrs.update({attribute: None for attribute in self._available_attributes})

    @property
    def supported_features(self) -> int:
        """Supported features."""
        return (
            FanEntityFeature.SET_SPEED
            | FanEntityFeature.PRESET_MODE
            | FanEntityFeature.OSCILLATE
            | FanEntityFeature.DIRECTION
            | FanEntityFeature.TURN_OFF
            | FanEntityFeature.TURN_ON
        )

    async def async_update(self):
        """Fetch state from the device."""
        # On state change the device doesn't provide the new state immediately.
        if self._skip_update:
            self._skip_update = False
            return

        try:
            state = await self.hass.async_add_executor_job(self._device.status)
            _LOGGER.debug("Got new state: %s", state)

            self._available = True
            self._oscillate = state.oscillate
            self._natural_mode = state.natural_speed != 0
            self._state = state.is_on

            if self._natural_mode:
                for preset_mode, range in FAN_PRESET_MODES.items():
                    if state.natural_speed in range:
                        self._preset_mode = preset_mode
                        self._percentage = state.natural_speed
                        break
            else:
                for preset_mode, range in FAN_PRESET_MODES.items():
                    if state.direct_speed in range:
                        self._preset_mode = preset_mode
                        self._percentage = state.direct_speed
                        break

            self._state_attrs.update(
                {
                    key: self._extract_value_from_attribute(state, value)
                    for key, value in self._available_attributes.items()
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
    def percentage(self):
        """Return the current speed."""
        return self._percentage

    @property
    def preset_modes(self):
        """Get the list of available preset modes."""
        return self._preset_modes

    @property
    def preset_mode(self):
        """Get the current preset mode."""
        return self._preset_mode

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        if preset_mode == SPEED_OFF:
            await self.async_turn_off()
            return

        if self._natural_mode:
            await self._try_command(
                "Setting fan speed of the miio device failed.",
                self._device.set_natural_speed,
                FAN_PRESET_MODE_VALUES[preset_mode],
            )
        else:
            await self._try_command(
                "Setting fan speed of the miio device failed.",
                self._device.set_direct_speed,
                FAN_PRESET_MODE_VALUES[preset_mode],
            )

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        _LOGGER.debug("Setting the fan speed percentage to: %s", percentage)

        if percentage == 0:
            await self.async_turn_off()
            return

        if self._natural_mode:
            await self._try_command(
                "Setting fan speed percentage of the miio device failed.",
                self._device.set_natural_speed,
                percentage,
            )
        else:
            await self._try_command(
                "Setting fan speed percentage of the miio device failed.",
                self._device.set_direct_speed,
                percentage,
            )

    async def async_set_direction(self, direction: str) -> None:
        """Set the direction of the fan."""
        if direction == "forward":
            direction = "right"

        if direction == "reverse":
            direction = "left"

        if self._oscillate:
            await self._try_command(
                "Setting oscillate off of the miio device failed.",
                self._device.set_oscillate,
                False,
            )

        await self._try_command(
            "Setting move direction of the miio device failed.",
            self._device.set_rotate,
            MoveDirection(direction),
        )

    @property
    def oscillating(self):
        """Return the oscillation state."""
        return self._oscillate

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

    async def async_set_oscillation_angle(self, angle: int) -> None:
        """Set oscillation angle."""
        if self._device_features & FEATURE_SET_OSCILLATION_ANGLE == 0:
            return

        await self._try_command(
            "Setting angle of the miio device failed.", self._device.set_angle, angle
        )

    async def async_set_delay_off(self, delay_off_countdown: int) -> None:
        """Set scheduled off timer in minutes."""

        await self._try_command(
            "Setting delay off miio device failed.",
            self._device.delay_off,
            delay_off_countdown * 60,
        )

    async def async_set_led_brightness(self, brightness: int = 2):
        """Set the led brightness."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        await self._try_command(
            "Setting the led brightness of the miio device failed.",
            self._device.set_led_brightness,
            LedBrightness(brightness),
        )

    async def async_set_natural_mode_on(self):
        """Turn the natural mode on."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        self._natural_mode = True
        await self.async_set_percentage(self._percentage)

    async def async_set_natural_mode_off(self):
        """Turn the natural mode off."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        self._natural_mode = False
        await self.async_set_percentage(self._percentage)
