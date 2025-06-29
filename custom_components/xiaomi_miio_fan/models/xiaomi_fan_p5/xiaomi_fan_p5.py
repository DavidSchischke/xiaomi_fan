import logging

from miio import DeviceException
from miio.fan_common import OperationMode

from .config import (
    AVAILABLE_ATTRIBUTES_FAN_P5,
    FEATURE_FLAGS_FAN_P5,
    FAN_PRESET_MODES_P5,
    FAN_PRESET_MODE_VALUES_P5,
)
from ..xiaomi_fan import XiaomiFan
from ..._base.speed_level import SPEED_OFF
from ..._base.features import FEATURE_SET_NATURAL_MODE


_LOGGER = logging.getLogger(__name__)


class XiaomiFanP5(XiaomiFan):
    """Representation of a Xiaomi Pedestal Fan P5."""

    def __init__(self, name, device, model, unique_id, retries, preset_modes_override):
        """Initialize the fan entity."""
        super().__init__(name, device, model, unique_id, retries, preset_modes_override)

        self._device_features = FEATURE_FLAGS_FAN_P5
        self._available_attributes = AVAILABLE_ATTRIBUTES_FAN_P5
        self._percentage = None
        self._preset_modes = list(FAN_PRESET_MODES_P5)
        if preset_modes_override is not None:
            self._preset_modes = preset_modes_override

        self._preset_mode = None
        self._oscillate = None
        self._natural_mode = False

        self._state_attrs.update({attribute: None for attribute in self._available_attributes})

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
            self._percentage = state.speed
            self._oscillate = state.oscillate
            self._natural_mode = state.mode == OperationMode.Nature
            self._state = state.is_on

            for preset_mode, range in FAN_PRESET_MODES_P5.items():
                if state.speed in range:
                    self._preset_mode = preset_mode
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

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        if preset_mode == SPEED_OFF:
            await self.async_turn_off()
            return

        if not self._state:
            await self._try_command("Turning the miio device on failed.", self._device.on)
        await self._try_command(
            "Setting fan speed of the miio device failed.",
            self._device.set_speed,
            FAN_PRESET_MODE_VALUES_P5[preset_mode],
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
            "Setting fan speed percentage of the miio device failed.",
            self._device.set_speed,
            percentage,
        )

    async def async_set_natural_mode_on(self):
        """Turn the natural mode on."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        await self._try_command(
            "Turning on natural mode of the miio device failed.",
            self._device.set_mode,
            OperationMode.Nature,
        )

    async def async_set_natural_mode_off(self):
        """Turn the natural mode off."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        await self._try_command(
            "Turning on natural mode of the miio device failed.",
            self._device.set_mode,
            OperationMode.Normal,
        )

    async def async_set_delay_off(self, delay_off_countdown: int) -> None:
        """Set scheduled off timer in minutes."""

        await self._try_command(
            "Setting delay off miio device failed.",
            self._device.delay_off,
            delay_off_countdown,
        )
