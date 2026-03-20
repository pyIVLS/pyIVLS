### Hardware abstraction layer for Sutter instrument MPC-325
Abstaction layer to use the micromanipulators made in python. No implementation to be used standalone as part of sequence, and instead meant to be used by other plugins that depend on this.
Implements almost full functionality as defined by the [programming interface](https://www.sutter.com/hubfs/WEB%20-%20Manuals/MPC-365_QuickRef_ExternalControl.pdf):
  - Initialization and calibration
  - moving to a specified position
  - handling devices / getting their status.

Communicates to the device with VCP-drivers through a virtual serial port.

# Installation:
Add 99-suttermpc325.rules to /etc/udev/rules.d to automatically load basic drivers and open a port.
You might need to fiddle around with the ports a bit to find the correct one, default is set to access the instrument by id.

# Public API:

Utility:
- setSettings(settings: dict) -> None
  - Sets internal settings from sequence-builder style config.
  - Expected keys: address (str), speed (int), quickmove (bool|str), speed_text (str, optional).
  - Edge cases:
    - Missing keys do not raise here; HAL update issues are logged.
    - Settings are deep-copied, so caller dictionary is not modified.

- set_gui_from_settings() -> tuple[int, dict]
  - Schedules GUI refresh from internal settings via Qt signal.
  - Returns:
    - (0, {"Error message": "GUI updated scheduled"})
  - Edge cases:
    - Update is asynchronous; the GUI may not be updated yet when return value is received.

- parse_settings_widget() -> tuple[int, dict]
  - Parses GUI controls and returns settings in ini-compatible format.
  - Returns:
    - (0, settings_dict) with keys: address (str), speed (int), quickmove (bool), speed_text (str)
    - (1, {"Error message": str}) on parse failure
  - Edge cases:
    - If speed text cannot be parsed into an integer prefix, returns status 1.
    - On success, updates both internal settings and HAL runtime state.

Device Functionality:
- mm_open() -> tuple[int, dict]
  - Opens serial connection to configured Sutter device.
  - Returns:
    - (0, {"Error message": str}) on success (including already-connected case)
    - (1, {...}) on value/argument errors
    - (4, {...}) on hardware/serial errors
  - Edge cases:
    - If already connected, returns success and does not reconnect.
    - If settings address is empty, reads address from GUI input.

- mm_change_active_device(dev_num: int) -> tuple[int, dict]
  - Changes active manipulator device.
  - Args:
    - dev_num: 1-based manipulator index (1-4)
  - Returns:
    - (0, {"Error message": ...}) on success
    - (1, {...}) on invalid arguments
    - (4, {"Error message": ...}) if HAL reports device-change failure
  - Edge cases:
    - Emits GUI signal to update device combobox when change succeeds.

- mm_move(x: float | None = None, y: float | None = None, z: float | None = None) -> tuple[int, dict]
  - Moves to absolute XYZ coordinates in microns.
  - Returns:
    - (0, {"Error message": "Sutter moved"}) on success
    - (1, {...}) on value/argument errors
    - (4, {...}) on hardware/serial errors
  - Edge cases:
    - Any axis set to None keeps current coordinate.
    - If final target equals current position (after HAL bounds handling), no physical move may occur and status is still success.

- mm_move_relative(x_change: float = 0, y_change: float = 0, z_change: float = 0) -> tuple[int, dict]
  - Moves relative to current position.
  - Returns same status model as mm_move.
  - Edge cases:
    - Uses live current position at call time.

- mm_calibrate(all: bool = False) -> tuple[int, dict]
  - Calibrates active device.
  - Returns:
    - (0, {"Error message": "Sutter calibrated"}) on success
    - (4, {...}) when unsupported options or HAL errors occur
  - Edge cases:
    - Performs pre-calibration move to minimum Z.
    - all=True is not implemented and is returned as hardware error wrapper.

- mm_stop() -> tuple[int, dict]
  - Requests stop for ongoing movement/read.
  - Returns:
    - (0, {"Error message": "Sutter stopped"}) on success
    - (4, {...}) on failure
  - Edge cases:
    - Safe to call even when no motion is active.

- mm_zmove(z_change: float, absolute: bool = False) -> tuple[int, dict]
  - Moves in Z only.
  - Args:
    - z_change: delta Z in microns, or absolute Z target when absolute=True
    - absolute: mode selector for z_change
  - Returns:
    - (0, {"Error message": "Sutter moved"}) on success
    - (1, {"Error message": "Sutter move out of bounds"}) for bounds violations
    - (4, {...}) for hardware/serial errors
  - Edge cases:
    - Bounds checked against HAL limits before movement.

- mm_get_active_device() -> tuple[int, int]
  - Returns active manipulator index as 1-based integer.
  - Returns:
    - (0, device_index)

- mm_up_max() -> tuple[int, dict]
  - Moves active manipulator to z=0.
  - Returns:
    - (0, {"Error message": ...}) on success or if already at z=0
    - (1, {...}) on value/argument errors
    - (4, {...}) on hardware/serial errors

- mm_current_position(manipulator_name: int | None = None) -> tuple[float, float, float] | tuple[int, dict]
  - Returns current XYZ position in microns.
  - Args:
    - manipulator_name: optional 1-based device index to query
  - Returns:
    - (x, y, z) on success
    - (4, {"Error message": ...}) if temporary device switch fails
  - Edge cases:
    - Non-standard return type (raw position tuple, not status tuple) for compatibility.
    - When manipulator_name is provided, active device is restored after query.

- mm_devices() -> list
  - Returns connected-device count and status list.
  - Returns:
    - [0, (device_count, device_statuses)] on success
    - [code, status_dict] if opening the device fails
  - Edge cases:
    - Uses list return format for compatibility with existing plugin calls.

- mm_get_positions() -> tuple[int, dict] | None
  - Returns manipulator positions map.
  - Returns:
    - (0, {device_index: (x, y, z)}) on first successful device read
    - (4, {"Error message": ...}) on failure
    - None if no connected devices are reported
  - Edge cases:
    - Current implementation returns after first connected device rather than aggregating all devices.

- mm_get_num_manipulators() -> int
  - Returns total count of connected manipulators.
  - Edge cases:
    - Non-standard return type (raw int) for compatibility.

- mm_slow_move(x: float | None = None, y: float | None = None, z: float | None = None) -> list
  - Fixed-speed slow move used for stop testing.
  - Returns:
    - [0, {"Error message": "Sutter moved"}] on success
    - [1, {"Error message": ...}] when all coordinates are None
    - [4, {...}] on hardware/serial errors
  - Edge cases:
    - Missing axes are backfilled from current position.
    - Uses fixed speed level 7.

Note on exception behavior:
- Public device methods are wrapped by a decorator that re-raises ThreadStopped, maps InterruptedError to success-style stop result, maps ValueError to status 1, and other exceptions to status 4.


# Notes
I have a theory: Sutter dislikes getting manual inputs from the ROE-200 while it is being externally controlled. Pure software controls seem to work fine, but adding manual moves and device changes during external control seems to decrease stability. Is the ROE-200 buffering something into the serial port during manual moves??
