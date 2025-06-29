import logging
from typing import Optional

from homeassistant.components.fan import FanEntityFeature
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)
from miio import DeviceException
from miio.fan_common import OperationMode

from .config import (
    FEATURE_FLAGS_FAN_1C,
    FAN_PRESET_MODES_1C,
    AVAILABLE_ATTRIBUTES_FAN_1C,
    FAN_SPEEDS_1C,
)
from ..xiaomi_fan import XiaomiFan
from ..._base.features import FEATURE_SET_NATURAL_MODE

_LOGGER = logging.getLogger(__name__)


class XiaomiFan1C(XiaomiFan):
    """Representation of a Xiaomi Fan 1C."""

    def __init__(self, name, device, model, unique_id, retries, preset_modes_override):
        """Initialize the fan entity."""
        super().__init__(name, device, model, unique_id, retries, preset_modes_override)

        self._device_features = FEATURE_FLAGS_FAN_1C
        self._available_attributes = AVAILABLE_ATTRIBUTES_FAN_1C
        self._preset_modes = list(FAN_PRESET_MODES_1C)
        if preset_modes_override is not None:
            self._preset_modes = preset_modes_override

        self._oscillate = None

        self._state_attrs.update({attribute: None for attribute in self._available_attributes})

    @property
    def supported_features(self) -> int:
        """Supported features."""
        return (
            FanEntityFeature.SET_SPEED
            | FanEntityFeature.PRESET_MODE
            | FanEntityFeature.OSCILLATE
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
            self._state = state.is_on

            for preset_mode, value in FAN_PRESET_MODES_1C.items():
                if state.speed == value:
                    self._preset_mode = preset_mode

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
    def percentage(self) -> Optional[int]:
        """Return the current speed percentage."""
        return ordered_list_item_to_percentage(FAN_SPEEDS_1C, self._preset_mode)

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return len(FAN_SPEEDS_1C)

    @property
    def preset_modes(self):
        """Get the list of available preset modes."""
        return self._preset_modes

    @property
    def preset_mode(self):
        """Get the current preset mode."""
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
            FAN_PRESET_MODES_1C[preset_mode],
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
            FAN_PRESET_MODES_1C[percentage_to_ordered_list_item(FAN_SPEEDS_1C, percentage)],
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

    async def async_set_delay_off(self, delay_off_countdown: int) -> None:
        """Set scheduled off timer in minutes."""

        await self._try_command(
            "Setting delay off miio device failed.",
            self._device.delay_off,
            delay_off_countdown,
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
