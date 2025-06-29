from typing import Dict, Any

from miio.miot_device import DeviceStatus

from .operation_mode_fan_p39 import OperationModeFanP39


class FanStatusP39(DeviceStatus):
    """Container for status reports for FanP39."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    @property
    def child_lock(self) -> bool:
        return self.data["child_lock"]

    @property
    def fan_level(self) -> int:
        return self.data["fan_level"]

    @property
    def fan_speed(self) -> int:
        return self.data["fan_speed"]

    @property
    def mode(self) -> str:
        return OperationModeFanP39(self.data["mode"]).name

    @property
    def power(self) -> bool:
        return self.data["power"]

    @property
    def delay_off_countdown(self) -> int:
        return self.data["power_off_time"]

    @property
    def oscillate(self) -> bool:
        return self.data["swing_mode"]

    @property
    def angle(self) -> int:
        return self.data["swing_mode_angle"]
