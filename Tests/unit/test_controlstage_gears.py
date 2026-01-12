"""Unit tests for ControlStage gear handling (no hardware required).

These tests mock the ControlSerial connection so that no real
Arduino or motors are needed.
"""

from __future__ import annotations

import importlib
import unittest


class FakeDriver:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:  # pragma: no cover - trivial
        self.closed = True


class FakeControlSerial:
    def __init__(self, device: str) -> None:  # pragma: no cover - simple wiring
        self.device = device
        self.driver = FakeDriver()
        self.commands: list[str] = []

    def send_command(self, s: str):
        self.commands.append(s)
        # Simulate a successful reply in the Romi protocol: [0, ...]
        return [0]


class TestControlStageGears(unittest.TestCase):
    def setUp(self) -> None:
        # Patch ControlSerial in the module where ControlStage is defined
        from ControlMotors import ControlStage  # type: ignore

        # Import the concrete module that defines ControlStage
        cm = importlib.import_module(ControlStage.__module__)
        self._cm = cm
        self._orig_cs = cm.ControlSerial
        cm.ControlSerial = FakeControlSerial

    def tearDown(self) -> None:
        # Restore original ControlSerial
        self._cm.ControlSerial = self._orig_cs

    def _make_stage(self, gears):
        from ControlMotors import ControlStage  # type: ignore
        return ControlStage("FAKE_PORT", gears)

    def test_move_dx_uses_gear_and_updates_x(self):
        stage = self._make_stage([2, 3, 4])  # X gear = 2
        link = stage.link

        stage.move_dx(10)  # 10 stage steps

        # Motor steps should be 10 * 2 = 20
        self.assertEqual(stage.x, 10)
        self.assertEqual(link.commands[-1], "M[20,20,0,0]")

    def test_move_dy_uses_gear_and_updates_y(self):
        stage = self._make_stage([2, 3, 4])  # Y gear = 3
        link = stage.link

        stage.move_dy(5)  # 5 stage steps

        # Motor steps should be 5 * 3 = 15
        self.assertEqual(stage.y, 5)
        self.assertEqual(link.commands[-1], "M[15,0,15,0]")

    def test_move_dz_uses_gear_and_updates_z(self):
        stage = self._make_stage([2, 3, 4])  # Z gear = 4
        link = stage.link

        stage.move_dz(-3)  # -3 stage steps

        # Motor steps should be -3 * 4 = -12
        self.assertEqual(stage.z, -3)
        self.assertEqual(link.commands[-1], "M[12,0,0,-12]")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
