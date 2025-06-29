import logging
from enum import Enum
from functools import partial

from homeassistant.components.fan import FanEntity
from miio import DeviceException

from .attributes import ATTR_MODEL
from .features import FEATURE_SET_BUZZER, FEATURE_SET_CHILD_LOCK
from .status import SUCCESS

_LOGGER = logging.getLogger(__name__)


class XiaomiGenericDevice(FanEntity):
    """Representation of a generic Xiaomi device."""

    _enable_turn_on_off_backwards_compatibility = False

    def __init__(self, name, device, model, unique_id, retries, preset_modes_override):
        """Initialize the generic Xiaomi device."""
        self._name = name
        self._device = device
        self._model = model
        self._unique_id = unique_id
        self._retry = 0
        self._retries = retries
        self._preset_modes_override = preset_modes_override

        self._available = False
        self._state = None
        self._state_attrs = {ATTR_MODEL: self._model}
        self._device_features = FEATURE_SET_BUZZER
        self._skip_update = False

    @property
    def supported_features(self):
        """Flag supported features."""
        return 0

    @property
    def should_poll(self):
        """Poll the device."""
        return True

    @property
    def unique_id(self):
        """Return an unique ID."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def available(self):
        """Return true when state is known."""
        return self._available

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes of the device."""
        return self._state_attrs

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    @staticmethod
    def _extract_value_from_attribute(state, attribute):
        value = getattr(state, attribute, None)
        if isinstance(value, Enum):
            return value.value

        return value

    async def _try_command(self, mask_error, func, *args, **kwargs):
        """Call a miio device command handling error messages."""
        try:
            result = await self.hass.async_add_executor_job(partial(func, *args, **kwargs))

            _LOGGER.debug("Response received from miio device: %s", result)

            return result == SUCCESS
        except DeviceException as exc:
            _LOGGER.error(mask_error, exc)
            self._available = False
            return False

    async def async_turn_on(self, speed: str = None, mode: str = None, **kwargs) -> None:
        """Turn the device on."""
        result = await self._try_command("Turning the miio device on failed.", self._device.on)
        if speed:
            result = await self.async_set_speed(speed)

        if result:
            self._state = True
            self._skip_update = True

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the device off."""
        result = await self._try_command("Turning the miio device off failed.", self._device.off)

        if result:
            self._state = False
            self._skip_update = True

    async def async_set_buzzer_on(self):
        """Turn the buzzer on."""
        if self._device_features & FEATURE_SET_BUZZER == 0:
            return

        await self._try_command(
            "Turning the buzzer of the miio device on failed.",
            self._device.set_buzzer,
            True,
        )

    async def async_set_buzzer_off(self):
        """Turn the buzzer off."""
        if self._device_features & FEATURE_SET_BUZZER == 0:
            return

        await self._try_command(
            "Turning the buzzer of the miio device off failed.",
            self._device.set_buzzer,
            False,
        )

    async def async_set_child_lock_on(self):
        """Turn the child lock on."""
        if self._device_features & FEATURE_SET_CHILD_LOCK == 0:
            return

        await self._try_command(
            "Turning the child lock of the miio device on failed.",
            self._device.set_child_lock,
            True,
        )

    async def async_set_child_lock_off(self):
        """Turn the child lock off."""
        if self._device_features & FEATURE_SET_CHILD_LOCK == 0:
            return

        await self._try_command(
            "Turning the child lock of the miio device off failed.",
            self._device.set_child_lock,
            False,
        )
