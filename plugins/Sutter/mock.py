import threading
import time
from typing import Final

import numpy as np


class Mpc325Mock:
    """
    Pure software mock for the Sutter MPC-325 micromanipulator HAL.

    Mirrors the public API of `Mpc325` in `Sutter.py` so GUI code can switch
    between real hardware and this virtual backend without changes.
    """

    # Movement speeds (microns/s) aligned with real HAL for GUI combobox
    _MOVE_SPEEDS: Final = {
        12: 1056.25,
        11: 975,
        10: 893.75,
        9: 812.5,
        8: 731.25,
        7: 650,
        6: 568.75,
        5: 487.5,
        4: 406.25,
        3: 325,
        2: 243.75,
        1: 162.5,
        0: 81.25,
    }

    _S2MCONV: Final = np.float64(0.0625)
    _M2SCONV: Final = np.float64(16.0)
    _MINIMUM_MS: Final = 0
    _MAXIMUM_M: Final = 25000
    _MAXIMUM_S: Final = 400000

    def __init__(self, num_devices: int = 4):
        # Connection state
        self._connected = False
        self.port = ""

        # Settings
        self.speed = 0
        self.quick_move = False

        # Device and position state
        self._comm_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._active_device = 1
        self._device_statuses = [1 if i < num_devices else 0 for i in range(4)]
        # Positions per device (microns)
        self._positions = {i + 1: (0.0, 0.0, 0.0) for i in range(4)}

    # -------- State helpers --------
    def update_internal_state(self, quick_move: bool = None, speed: int = None, source: str = None):
        if quick_move is not None:
            self.quick_move = bool(quick_move)
        if speed is not None:
            self.speed = int(speed)
        if source is not None:
            self.port = str(source)

    # -------- Connection --------
    def open(self, port: str = None):
        with self._comm_lock:
            if port is not None:
                self.port = port
            self._connected = True
            # Simulate small connection delay
            time.sleep(0.05)

    def close(self):
        with self._comm_lock:
            self._connected = False

    def is_connected(self):
        return self._connected

    # -------- Devices --------
    def get_connected_devices_status(self):
        with self._comm_lock:
            num_devices = sum(1 for s in self._device_statuses if s == 1)
            return (num_devices, list(self._device_statuses))

    def get_active_device(self):
        with self._comm_lock:
            return self._active_device

    def change_active_device(self, dev_num: int):
        with self._comm_lock:
            if dev_num < 1 or dev_num > 4:
                raise ValueError(f"Device number {dev_num} is out of range. Must be between 1 and 4.")
            if self._device_statuses[dev_num - 1] != 1:
                return False
            self._active_device = dev_num
            return True

    # -------- Positions / calibration --------
    def get_current_position(self):
        with self._comm_lock:
            return self._positions[self._active_device]

    def calibrate(self):
        with self._comm_lock:
            self._positions[self._active_device] = (0.0, 0.0, 0.0)
            return True

    # -------- Stop --------
    def stop(self):
        self._stop_event.set()
        time.sleep(0.05)
        self._stop_event.clear()

    # -------- Movement --------
    def move(self, x=None, y=None, z=None):
        curr_x, curr_y, curr_z = self.get_current_position()
        target_x = curr_x if x is None else x
        target_y = curr_y if y is None else y
        target_z = curr_z if z is None else z

        target_x = self._handrail_micron(target_x)
        target_y = self._handrail_micron(target_y)
        target_z = self._handrail_micron(target_z)

        if (curr_x, curr_y, curr_z) == (target_x, target_y, target_z):
            return

        if self.quick_move:
            self.quick_move_to(target_x, target_y, target_z)
        else:
            self.slow_move_to(target_x, target_y, target_z, self.speed)

    def quick_move_to(self, x: np.float64, y: np.float64, z: np.float64):
        with self._comm_lock:
            self._positions[self._active_device] = (float(x), float(y), float(z))
            time.sleep(0.005)

    def slow_move_to(self, x: np.float64, y: np.float64, z: np.float64, speed=None):
        with self._comm_lock:
            if speed is None:
                speed = self.speed
            speed = max(0, min(int(speed), 12))  # align with usable range

            start = np.array(self._positions[self._active_device], dtype=float)
            target = np.array((float(x), float(y), float(z)), dtype=float)

        total_dist = float(np.sum(np.abs(target - start)))
        # Avoid divide-by-zero; minimal time for small moves
        move_speed = max(self._MOVE_SPEEDS.get(speed, 81.25), 1e-3)
        duration = total_dist / move_speed
        duration = max(duration, 0.01)

        # Simulate blocking movement with interpolation and stop support
        steps = max(int(duration / 0.02), 1)
        for i in range(1, steps + 1):
            if self._stop_event.is_set():
                # emulate interrupted read behavior
                raise InterruptedError("Move interrupted by stop command")
            frac = i / steps
            new_pos = start + (target - start) * frac
            with self._comm_lock:
                self._positions[self._active_device] = (float(new_pos[0]), float(new_pos[1]), float(new_pos[2]))
            time.sleep(0.02)

        with self._comm_lock:
            self._positions[self._active_device] = (float(target[0]), float(target[1]), float(target[2]))

    # -------- Conversions / handrails --------
    def _handrail_micron(self, microns) -> np.uint32:
        return max(self._MINIMUM_MS, min(float(microns), self._MAXIMUM_M))

    def _handrail_step(self, steps) -> np.uint32:
        return max(self._MINIMUM_MS, min(int(steps), self._MAXIMUM_S))

    def _m2s(self, microns: np.float64) -> np.uint32:
        return np.uint32(microns * self._M2SCONV)

    def _s2m(self, steps: np.uint32) -> np.float64:
        return np.float64(steps * self._S2MCONV)

    def _calculate_wait_time(self, speed, x, y, z):
        curr_pos = self.get_current_position()
        x_diff = abs(curr_pos[0] - x)
        y_diff = abs(curr_pos[1] - y)
        z_diff = abs(curr_pos[2] - z)
        total_diff = x_diff + y_diff + z_diff
        move_speed = self._MOVE_SPEEDS.get(int(speed), 81.25)
        return total_diff / move_speed
