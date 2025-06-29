from miio.miot_device import MiotDevice
from miio.fan_common import FanException

from .fan_status_fan_p45 import FanStatusP45
from .operation_mode_fan_p45 import OperationModeFanP45
from ...config import MODEL_FAN_P45
from ..._base.utils import _filter_request_fields


class FanP45(MiotDevice):
    mapping = {
        # https://home.miot-spec.com/spec/xiaomi.fan.p45
        "power": {"siid": 2, "piid": 1},
        "fan_level": {"siid": 2, "piid": 4},
        "mode": {"siid": 2, "piid": 3},
        "swing_mode": {"siid": 2, "piid": 6},
        "swing_mode_angle": {"siid": 2, "piid": 7},
        "power_off_time": {"siid": 12, "piid": 2},
        "fan_speed": {"siid": 2, "piid": 5},
        "child_lock": {"siid": 11, "piid": 1},
        # TODO: Does this work?
        "light": {"siid": 5, "piid": 1},
        # TODO: Is now moved to AIID. Not supported in implementation?!
        # "set_move": {"siid": , "piid": , "access": ["write"]},
        # TODO: Missing are alarm, turn-left and -right and different natural modes
    }

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_FAN_P45,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover, model)

    def get_properties_for_mapping(self, *, max_properties=15) -> list:
        """Retrieve raw properties based on mapping. Copied from P39"""
        mapping = self._get_mapping()

        # We send property key in "did" because it's sent back via response and we can identify the property.
        properties = [
            {"did": k, **_filter_request_fields(v)}
            for k, v in mapping.items()
            if "aiid" not in v and ("access" not in v or "read" in v["access"])
        ]

        return self.get_properties(
            properties, property_getter="get_properties", max_properties=max_properties
        )

    def status(self):
        return FanStatusP45(
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

    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        self.status()
        return self.set_property("child_lock", lock)

    def set_mode(self, mode: OperationModeFanP45):
        """Set mode."""
        return self.set_property("mode", OperationModeFanP45[mode.name].value)

    def delay_off(self, minutes: int):
        """Set delay off minutes."""

        if minutes < 0 or minutes > 480:
            raise FanException("Invalid value for a delayed turn off: %s" % minutes)

        return self.set_property("power_off_time", minutes)

    # TODO: Implement via AAID
    # def set_rotate(self, direction: FanMoveDirection):
    #     """Rotate fan 7.5 degrees horizontally to given direction."""
    #     # Values for P39
    #     # { "value": 0, "description": "None" },
    #     # { "value": 1, "description": "Left" },
    #     # { "value": 2, "description": "Right" }
    #     value = 0
    #     if direction == FanMoveDirection.Left:
    #         value = 1
    #     elif direction == FanMoveDirection.Right:
    #         value = 2
    #     return self.set_property("set_move", value)
