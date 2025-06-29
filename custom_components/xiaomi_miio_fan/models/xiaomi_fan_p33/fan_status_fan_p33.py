from typing import Dict, Any

from miio.miot_device import DeviceStatus

from .operation_mode_fan_p33 import OperationModeFanP33


class FanStatusP33(DeviceStatus):
    """Container for status reports for FanP33."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response of a Fan (dmaker.fan.p33, fw: 2.1.3):

        {'did': 'power', 'siid': 2, 'piid': 1, 'code': 0, 'value': True},
        {'did': 'fan_level', 'siid': 2, 'piid': 2, 'code': 0, 'value': 1},
        {'did': 'swing_mode', 'siid': 2, 'piid': 4, 'code': 0, 'value': False},
        {'did': 'swing_mode_angle', 'siid': 2, 'piid': 5, 'code': 0, 'value': 120},
        {'did': 'mode', 'siid': 2, 'piid': 3, 'code': 0, 'value': 1},
        {'did': 'power_off_time', 'siid': 3, 'piid': 1, 'code': 0, 'value': 0},
        {'did': 'child_lock', 'siid': 7, 'piid': 1, 'code': 0, 'value': False},
        {'did': 'light', 'siid': 4, 'piid': 1, 'code': 0, 'value': True},
        {'did': 'buzzer', 'siid': 5, 'piid': 1, 'code': 0, 'value': True},
        {'did': 'set_move', 'siid': 6, 'piid': 1, 'code': -4003},
        {'did': 'fan_speed', 'siid': 2, 'piid': 6, 'code': 0, 'value': 20},
        """
        self.data = data

    @property
    def buzzer(self) -> bool:
        return self.data["buzzer"]

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
    def light(self) -> bool:
        return self.data["light"]

    @property
    def led(self) -> bool:
        return self.light

    @property
    def mode(self) -> str:
        return OperationModeFanP33(self.data["mode"]).name

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
