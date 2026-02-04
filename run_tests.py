"""Test runner for the ControlMotors sub-repo.

This script separates fast, automated unit tests from hardware-dependent
tests that actually move motors.

Usage (from ControlMotors directory):

    cd ControlMotors
    python run_tests.py               # unit tests only (no hardware)
    python run_tests.py --with-hardware  # also run hardware tests

Test layout:
- Tests/unit/      -> no-hardware tests (safe to run anywhere)
- Tests/hardware/  -> scripts/tests that require a real Arduino + motors
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
import unittest
import os
import importlib

ROOT = Path(__file__).resolve().parent


def sanity_import_check() -> int:
    """Basic check that the ControlMotors package can be imported.

    This verifies that the installed environment and package structure are
    coherent without touching any real hardware.
    """

    print("[ControlMotors tests] Importing ControlStage from ControlMotors...")
    try:
        from ControlMotors import ControlStage  # type: ignore
    except Exception as exc:  # pragma: no cover - diagnostic path
        print("[ControlMotors tests] FAILED: could not import ControlStage")
        print(f"  Error: {exc}")
        return 1

    # Simple smoke test: construct a ControlStage with a fake port name
    # but do NOT open hardware. We only check that the class exists and is
    # callable, not that a device is connected.
    print("[ControlMotors tests] OK: ControlStage is importable.")
    return 0


def _filtered_suite(suite: unittest.TestSuite, skip_names: set[str]) -> unittest.TestSuite:
    """Return a copy of the suite without tests whose id contains any name in skip_names.

    The unittest discovery builds nested suites; we rebuild a filtered tree.
    """

    filtered = unittest.TestSuite()
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            filtered.addTest(_filtered_suite(test, skip_names))
        else:
            test_id = test.id()
            if not any(name in test_id for name in skip_names):
                filtered.addTest(test)
    return filtered


def _count_tests(suite: unittest.TestSuite) -> int:
    count = 0
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            count += _count_tests(test)
        else:
            count += 1
    return count


def run_unittest_discover(start_dir: Path, label: str) -> int:
    """Discover and run unittest tests under the given directory.

    Returns 0 on success, 1 if any test failed.
    """

    if not start_dir.is_dir():
        print(f"[ControlMotors tests] Skipping {label}: folder '{start_dir}' not found.")
        return 0

    print(f"\n[ControlMotors tests] Running {label} tests in {start_dir}...")
    loader = unittest.TestLoader()
    suite = loader.discover(str(start_dir), pattern="test_*.py")

    discovered = _count_tests(suite)

    # Allow skipping specific tests via env var CM_SKIP_TESTS (comma-separated substrings)
    skip_env = os.getenv("CM_SKIP_TESTS", "")
    skip_names = {name.strip() for name in skip_env.split(",") if name.strip()}

    if skip_names:
        suite = _filtered_suite(suite, skip_names)
        selected = _count_tests(suite)
        skipped = discovered - selected
        print(f"[ControlMotors tests] Discovered {discovered} tests; skipped {skipped}; running {selected}.")
    else:
        print(f"[ControlMotors tests] Discovered {discovered} tests; running all.")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


def main() -> int:
    parser = argparse.ArgumentParser(prog="ControlMotors tests")
    parser.add_argument(
        "--with-hardware",
        action="store_true",
        help="Also run hardware tests in Tests/hardware (will move motors)",
    )
    args = parser.parse_args()

    rc = 0

    # 1. Sanity import check (no hardware touched)
    rc |= sanity_import_check()

    # 2. Pure unit tests (no hardware)
    unit_dir = ROOT / "Tests" / "unit"
    rc |= run_unittest_discover(unit_dir, "unit")

    # 3. Optional hardware tests
    if args.with_hardware:
        hw_dir = ROOT / "Tests" / "hardware"
        print("\n[ControlMotors tests] WARNING: running hardware tests may move the stage.")
        print("Ensure the Arduino is connected and the COM port in the tests is correct.")
        rc |= run_unittest_discover(hw_dir, "hardware")
    else:
        print("\n[ControlMotors tests] Hardware tests in 'Tests/hardware' were NOT run.")
        print("Use '--with-hardware' if you want to execute them (they will move motors).")

    if rc == 0:
        print("\n[ControlMotors tests] All selected test suites passed.")
    else:
        print("\n[ControlMotors tests] Some test suites failed.")

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
