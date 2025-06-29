from typing import Dict, Any, Optional

from miio.miot_device import DeviceStatus
from miio.fan_common import LedBrightness

from .operation_mode_za5 import OperationModeFanZA5


class FanStatusZA5(DeviceStatus):
    """Container for status reports for FanZA5."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    # TODO: Docstrings.
    @property
    def anion(self) -> bool:
        return self.data["anion"]

    @property
    def battery_supported(self) -> bool:
        return self.data["battery_supported"]

    @property
    def buttons_pressed(self) -> str:
        code = self.data["buttons_pressed"]
        if code == 0:
            return "None"
        if code == 1:
            return "Power"
        if code == 2:
            return "Swing"
        return "Unknown"

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
    def humidity(self) -> int:
        return self.data["humidity"]

    @property
    def light(self) -> int:
        return self.data["light"]

    @property
    def light_enum(self) -> str:
        if self.light == 1:
            brightness = 1
        elif self.light == 0:
            brightness = 2
        else:
            brightness = 0
        return LedBrightness(brightness).name

    @property
    def mode(self) -> str:
        return OperationModeFanZA5(self.data["mode"]).name

    @property
    def power(self) -> bool:
        return self.data["power"]

    @property
    def power_off_time(self) -> int:
        return self.data["power_off_time"]

    @property
    def powersupply_attached(self) -> bool:
        return self.data["powersupply_attached"]

    @property
    def speed_rpm(self) -> int:
        return self.data["speed_rpm"]

    @property
    def swing_mode(self) -> bool:
        return self.data["swing_mode"]

    @property
    def swing_mode_angle(self) -> int:
        return self.data["swing_mode_angle"]

    @property
    def temperature(self) -> Any:
        return self.data["temperature"]

    @property
    def led(self) -> Optional[bool]:
        if self.light is None:
            return
        return self.light > 0

    @property
    def battery_state(self) -> str:
        if self.powersupply_attached:
            return "Charging"
        return "Discharging"
