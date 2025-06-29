from miio.miot_device import MiotDevice
from miio.fan_common import FanException, MoveDirection

from .fan_status_fan_p33 import FanStatusP33
from .operation_mode_fan_p33 import OperationModeFanP33
from ...config import MODEL_FAN_P33


class FanP33(MiotDevice):
    mapping = {
        # https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:fan:0000A005:dmaker-p33:1
        "power": {"siid": 2, "piid": 1},
        "fan_level": {"siid": 2, "piid": 2},
        "swing_mode": {"siid": 2, "piid": 4},
        "swing_mode_angle": {"siid": 2, "piid": 5},
        "mode": {"siid": 2, "piid": 3},
        "power_off_time": {"siid": 3, "piid": 1},
        "child_lock": {"siid": 7, "piid": 1},
        "light": {"siid": 4, "piid": 1},
        "buzzer": {"siid": 5, "piid": 1},
        "set_move": {"siid": 6, "piid": 1},
        "fan_speed": {"siid": 2, "piid": 6},
    }

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_FAN_P33,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover, model=model)

    def status(self):
        """Retrieve properties."""
        return FanStatusP33(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
        )

    def on(self):
        """Power on."""
        return self.set_property("power", True)

    def off(self):
        """Power off."""
        return self.set_property("power", False)

    def set_speed(self, speed: int):
        """Set fan speed."""
        if speed < 0 or speed > 100:
            raise FanException("Invalid speed: %s" % speed)

        return self.set_property("fan_speed", speed)

    def set_angle(self, angle: int):
        """Set the oscillation angle."""
        if angle not in [30, 60, 90, 120, 140]:
            raise FanException(
                "Unsupported angle. Supported values: "
                + ", ".join("{0}".format(i) for i in [30, 60, 90, 120, 140])
            )

        return self.set_property("swing_mode_angle", angle)

    def set_oscillate(self, oscillate: bool):
        """Set oscillate on/off."""
        if oscillate:
            return self.set_property("swing_mode", True)
        else:
            return self.set_property("swing_mode", False)

    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        if buzzer:
            return self.set_property("buzzer", True)
        else:
            return self.set_property("buzzer", False)

    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        self.status()
        return self.set_property("child_lock", lock)

    def set_light(self, light: bool):
        """Set indicator state."""
        return self.set_property("light", light)

    def set_mode(self, mode: OperationModeFanP33):
        """Set mode."""
        return self.set_property("mode", OperationModeFanP33[mode.name].value)

    def delay_off(self, minutes: int):
        """Set delay off minutes."""

        if minutes < 0 or minutes > 480:
            raise FanException("Invalid value for a delayed turn off: %s" % minutes)

        return self.set_property("power_off_time", minutes)

    def set_rotate(self, direction: MoveDirection):
        """Rotate fan 7.5 degrees horizontally to given direction."""
        # Values for P33
        # { "value": 0, "description": "NONE" },
        # { "value": 1, "description": "LEFT" },
        # { "value": 2, "description": "RIGHT" }
        value = 0
        if direction == MoveDirection.Left:
            value = 1
        elif direction == MoveDirection.Right:
            value = 2
        return self.set_property("set_move", value)
