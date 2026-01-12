"""Hardware test for the Z motor.

Run this only when an Arduino with the Oquam firmware is connected
on the configured COM port and the stage is safe to move.
"""

from ControlMotors import ControlStage
import time


def _ask_with_default(prompt, default):
	"""Utility to ask the user for input with a default value."""
	resp = input(f"{prompt} [{default}]: ").strip()
	return resp or default


def main():
	print("[axis-test] ==== Manual hardware test for X/Y/Z axes ====")

	port = _ask_with_default("Arduino COM port", "COM6")

	axes_raw = _ask_with_default(
		"Which axis/axes to test (X, Y, Z, XY, XYZ)",
		"Z",
	)
	axes = []
	for ch in axes_raw.lower():
		if ch in ("x", "y", "z") and ch not in axes:
			axes.append(ch)
	if not axes:
		axes = ["z"]

	gears_input = input(
		"Gear ratios GX GY GZ (motor-steps per stage-step) [1 1 1]: "
	).strip()
	if gears_input:
		try:
			parts = [int(p) for p in gears_input.split()]
			if len(parts) == 3:
				gears = parts
			else:
				print("[axis-test] Invalid number of gear values, using default [1, 1, 1].")
				gears = [1, 1, 1]
		except ValueError:
			print("[axis-test] Invalid gear input, using default [1, 1, 1].")
			gears = [1, 1, 1]
	else:
		gears = [1, 1, 1]

	step_input = _ask_with_default(
		"Absolute/relative step size on the tested axis", "10"
	)
	try:
		step = int(step_input)
	except ValueError:
		print("[axis-test] Invalid step size, using 10.")
		step = 10

	timeout_input = _ask_with_default(
		"Maximum time to wait for homing to complete in seconds", "60"
	)
	try:
		homing_timeout = float(timeout_input)
	except ValueError:
		print("[axis-test] Invalid timeout, using 60 s.")
		homing_timeout = 60.0

	homing_answer = input(
		"Run homing at the END of the test (after movements)? [y/N]: "
	).strip().lower()
	do_homing_end = homing_answer.startswith("y")

	print(f"[axis-test] Connecting to Arduino on {port} with gears {gears} ...")
	stage = ControlStage(port, gears)

	try:
		for axis in axes:
			print("")
			print(f"[axis-test] ==== Testing axis {axis.upper()} ====.")

			# Step 1: with motors DISABLED, have user move near homing/start position
			print("[axis-test] Step 1: disabling motors (handle_enable(0)).")
			stage.handle_enable(0)
			input(
				"[axis-test] Motors are DISABLED. Manually move the "
				f"{axis.upper()} axis close to its homing/start position (with enough travel "
				"range for test moves). Press Enter when ready... "
			)

			# Step 2: enable motors and perform programmed moves with user observation
			print("[axis-test] Step 2: enabling motors (handle_enable(1)).")
			stage.handle_enable(1)
			input(
				"[axis-test] Motors are ENABLED. Do NOT force the axis by hand. "
				"Press Enter to start programmed moves on this axis... "
			)

			# Build absolute and relative move commands on the selected axis
			x = y = z = 0
			if axis == "x":
				x = step
			elif axis == "y":
				y = step
			else:
				z = step

			print(
				f"[axis-test] Moving to absolute position {axis.upper()}={step} (dt=2000) ..."
			)
			stage.handle_moveto(2000, x, y, z)
			input(
				"[axis-test] Check that the stage moved as expected to the absolute "
				f"position on {axis.upper()}. Press Enter to continue... "
			)

			print(
				f"[axis-test] Applying relative move d{axis.upper()}={step} (dt=2000) ..."
			)
			stage.handle_move(2000, x, y, z)
			input(
				"[axis-test] Check that an additional relative move occurred on the "
				f"{axis.upper()} axis. Press Enter to finish this axis... "
			)

			print("[axis-test] Movement test finished for this axis.")

		# Optional: homing at the END of the full test, if requested
		if do_homing_end:
			print("")
			print("[axis-test] ==== Final homing sequence (per selected axis) ====")
			for axis in axes:
				print("")
				if axis == "x":
					print("[axis-test] Starting X homing (X only, Y/Z skipped) ...")
					stage.handle_set_homing(0, -1, -1)
				elif axis == "y":
					print("[axis-test] Starting Y homing (Y only, X/Z skipped) ...")
					stage.handle_set_homing(1, -1, -1)
				else:  # "z"
					print("[axis-test] Starting Z homing (Z only, X/Y skipped) ...")
					stage.handle_set_homing(2, -1, -1)

				stage.handle_homing()
				print(
					f"[axis-test] Waiting up to {homing_timeout:.0f} s for homing to complete ..."
				)
				time.sleep(homing_timeout)
				print("[axis-test] Homing completed for this axis.")
	finally:
		print("[axis-test] Disabling stage movement and closing stage.")
		try:
			stage.handle_enable(0)
		except Exception:
			pass
		stage.close()


if __name__ == "__main__":
	main()
