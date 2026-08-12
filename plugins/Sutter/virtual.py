"""Module for the MPC-325 abstraction layer"""

import logging
import random
import struct  # Handling binary
import threading  # for thread safety
import time  # for device-specified wait-times
from typing import Final  # for constants and options

import numpy as np  # for better typing

logger = logging.getLogger(__name__)


class VirtualMpc325:
    """
    Virtual manipulator for testing
    """

    """ 
        15: 1300,
        14: 1218.75,
        13: 1137.5,
    """

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
    _TIMEOUT: Final = 3

    def __init__(self):
        self.man_pos = [
            (np.uint32(0), np.uint32(0), np.uint32(0)),
            (np.uint32(5000), np.uint32(5000), np.uint32(0)),
            (np.uint32(10000), np.uint32(10000), np.uint32(0)),
            (np.uint32(15000), np.uint32(15000), np.uint32(0)),
        ]

        self._is_connected = False
        self.active_device = 1
        self._comm_lock = threading.Lock()  # Lock for thread safety

    def open(self, port: str | None = None):
        with self._comm_lock:
            # Open port
            if not self.is_connected():
                logger.debug(f"Opening virtual port {port}")
                self._is_connected = True

    def close(self):
        with self._comm_lock:
            if self.is_connected():
                self._is_connected = False

    def read(self, num_bytes: int) -> None:
        logger.debug(f"Reading {num_bytes} bytes from virtual device")

    def write(self, data: bytes) -> None:
        command_map = {
            85: "Get connected devices status",
            75: "Get active device",
            67: "Get current position",
            73: "Change active device",
            78: "Calibrate",
            77: "Quick move to position",
            83: "Slow move to position",
        }
        line = ""
        if data[0] in command_map:
            line = f"Executing command: {command_map[data[0]]}"
        line += f" with data: {data}"
        logger.debug(line)

    def is_connected(self):
        """Check if the port is open and connected.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self._is_connected

    def _flush(self):
        """Flushes i/o buffers. Also applies a wait time between commands. Every method should call this before sending a command."""

        time.sleep(0.002)  # Hardcoded wait time (2 ms) between commands from the manual.

    def get_connected_devices_status(self):
        """Get the status of connected micromanipulators

        Returns:
            tuple: first element is how many devices connected, second element is a list representing
            the status of connected devices
        """
        with self._comm_lock:
            self._flush()
            self.write(bytes([85]))  # Send command to the device (ASCII: U)
            self.read(6)  # Expecting 6 bytes back: 1 byte for number of devices, 4 bytes for device statuses, 1 byte for end marker
            num_devices = 4  # Simulate 4 devices connected
            device_statuses = [1, 1, 1, 1]  # Simulate all devices are connected and active
            return (num_devices, device_statuses)

    def get_active_device(self):
        """Returns the current active device.

        Returns:
            int: active device number
        """
        with self._comm_lock:
            self._flush()
            self.write(bytes([75]))  # Send command to the device (ASCII: K)
            self.read(4)  # Expecting 4 bytes back: 1 byte for active device number, 2 bytes for FW version, 1 byte for end marker
            return self.active_device  # Return the simulated active device number

    def change_active_device(self, dev_num: int):
        """Change active device

        Args:
            devNum (int): Device number to be activated (1-4 on this system)

        Returns:
            bool: Change successful
        """
        with self._comm_lock:
            self._flush()
            if dev_num < 1 or dev_num > 4:
                raise ValueError(f"Device number {dev_num} is out of range. Must be between 1 and 4.")
            command = struct.pack("<2B", 73, dev_num)
            self.write(command)  # Send command to the device (ASCII: I )
            self.read(2)  # Expecting 2 bytes back: 1 byte for active device number, 1 byte for end marker
            # check that the device is available and active
            self.active_device = dev_num  # Simulate changing the active device
            if self.active_device != dev_num:
                raise RuntimeError(f"Failed to change active device. Expected {dev_num}, got {self.active_device}.")
            return True

    def get_current_position(self):
        """Get current position in microns.

        Returns:
            tuple: (x,y,z)
        """
        with self._comm_lock:
            self._flush()
            self.write(bytes([67]))  # Send command (ASCII: C)
            self.read(14)  # Expecting 14 bytes back: 1 byte drv number 3*4 bytes for x,y,z positions in microsteps, 1 byte for end marker
            active_device = self.get_active_device()
            return (
                self._s2m(self.man_pos[active_device - 1][0]),
                self._s2m(self.man_pos[active_device - 1][1]),
                self._s2m(self.man_pos[active_device - 1][2]),
            )

    def calibrate(self):
        """Calibrate the device. Does the same thing as the calibrate button on the back of the control unit.
        (moves to 0,0,0)
        """
        with self._comm_lock:
            if self.is_connected:
                # add longer timeout for this
                self._flush()
                self.write(bytes([78]))  # Send command (ASCII: N)
                logger.debug("Calibrating device...")
                time.sleep(4 * random.random())  # Simulate calibration time
                self.read(1)  # Expecting 1 byte back: end marker
                return True

    def stop(self):
        """Stop the current movement"""
        self.write(struct.pack("<B", 0x03))

    def move(self, x=None, y=None, z=None, quick_move=True, speed=7, segment=True, segment_length=500):
        """Move to a position. If quick_move is set to True, the movement will be at full speed.

        Args:
            x (np.float64): x in microns
            y (np.float64): y in microns
            z (np.float64): z in microns
            quick_move (bool, optional): Whether to use quick move or slow move. Defaults to True.
            speed (int, optional): Speed for slow move in range 0-15. Defaults to 7.
        """

        def _interal_move(x, y, z, quick_move, speed):
            if quick_move:
                self.quick_move_to(x, y, z)
            else:
                self.slow_move_to(x, y, z, speed)

        curr_pos = self.get_current_position()
        # If any of the coordinates are None, use the current position.
        if x is None:
            x = curr_pos[0]
        if y is None:
            y = curr_pos[1]
        if z is None:
            z = curr_pos[2]

        # If the position after handrails is the same, do nothing.
        if (curr_pos[0] == self._handrail_micron(x)) and (curr_pos[1] == self._handrail_micron(y)) and (curr_pos[2] == self._handrail_micron(z)):
            return
        # for moves, add more generous timeout since they really do take a while.
        self.ser.timeout = self._TIMEOUT * 10
        if segment:
            segments = self.segment_move(curr_pos, (x, y, z), length=segment_length)
            for segment_target in segments:
                _interal_move(*segment_target, quick_move=quick_move, speed=speed)  # Move to each segment target without further segmentation
        else:
            _interal_move(x, y, z, quick_move, speed)
        self.ser.timeout = self._TIMEOUT  # reset timeout to default

    def quick_move_to(self, x: np.float64, y: np.float64, z: np.float64):
        """Quickmove orthogonally at full speed.

        Args:
            x (np.float64): x in microns
            y (np.float64): y in microns
            z (np.float64): z in microns
        """
        self._flush()
        # Pack first part of command
        command1 = struct.pack("<B", 77)
        # check bounds for coordinates and convert to microsteps. Makes really *really* sure that the values are good.
        x_s = self._handrail_step(self._m2s(self._handrail_micron(x)))
        y_s = self._handrail_step(self._m2s(self._handrail_micron(y)))
        z_s = self._handrail_step(self._m2s(self._handrail_micron(z)))

        command2 = struct.pack("<3I", x_s, y_s, z_s)  # < to enforce little endianness. Just in case someone tries to run this on an IBM S/360

        self.ser.write(command1)
        self.ser.write(command2)

        byt = self.read(1)  # Expecting 1 byte back: end marker
        self._validate_and_unpack("<B", byt, name="quick_move_to")  # Just to validate the end marker

    def slow_move_to(self, x: np.float64, y: np.float64, z: np.float64, speed: int):
        """Slower move in straight lines. Speed is set as a class variable. (Or given as an argument)

        Args:
            speed (int): speed in range 0-15. Enforced in the code.
            x (np.float64): x in microns
            y (np.float64): y in microns
            z (np.float64): z in microns

        """
        self._flush()

        # Enforce speed limits
        if speed > 15 or speed < 0:
            raise ValueError(f"Speed {speed} is out of range. Must be between 0 and 15.")
        # Pack first part of command
        command1 = struct.pack("<2B", 83, speed)
        # check bounds for coordinates and convert to microsteps. Makes really *really* sure that the values are good.
        x_s = self._handrail_step(self._m2s(self._handrail_micron(x)))
        y_s = self._handrail_step(self._m2s(self._handrail_micron(y)))
        z_s = self._handrail_step(self._m2s(self._handrail_micron(z)))
        command2 = struct.pack("<3I", x_s, y_s, z_s)  # < to enforce little endianness. Just in case someone tries to run this on an IBM S/360

        self.ser.write(command1)
        time.sleep(0.035)  # wait period specified in the manual (30 ms) Updated to 35 ms on recommendation from Sutter instr
        self.ser.write(command2)
        byt = self.read(1)  # Expecting 1 byte back: end marker
        self._validate_and_unpack("<B", byt, name="slow_move_to")  # Just to validate the end marker

    # Handrails for microns/microsteps. Realistically would be enough just to check the microsteps, but CATCH ME LETTING A MISTAKE BREAK THESE
    def _handrail_micron(self, microns: np.float64) -> np.float64:
        return np.float64(max(self._MINIMUM_MS, min(microns, self._MAXIMUM_M)))

    def _handrail_step(self, steps: np.uint32) -> np.uint32:
        return np.uint32(max(self._MINIMUM_MS, min(steps, self._MAXIMUM_S)))

    # Function to convert microns to microsteps.
    def _m2s(self, microns: np.float64) -> np.uint32:
        return np.uint32(microns * self._M2SCONV)

    # Function to convert microsteps to microns.
    def _s2m(self, steps: np.uint32) -> np.float64:
        return np.float64(steps * self._S2MCONV)

    # Segmenter
    def segment_move(self, current_position: tuple, target_position: tuple, length: int) -> list[tuple]:
        """Break up a move into segments of specified length.

        Args:
            current_position (tuple[float]): Current position as (x, y, z) in microns
            target_position (tuple[float]): Target position as (x, y, z) in microns
            length (int): Max length of each segment in microns
        Returns:
            list[tuple]: List of target positions for each segment, including the final target position, in microns
        """
        segments = []
        current_position = np.array(current_position)
        target_position = np.array(target_position)
        total_distance = np.linalg.norm(target_position - current_position)
        if total_distance == 0:
            return [tuple(target_position)]
        direction_vector = (target_position - current_position) / total_distance
        num_segments = int(np.ceil(total_distance / length))
        for i in range(1, num_segments + 1):
            segment_target = current_position + direction_vector * min(i * length, total_distance)
            segments.append(tuple(segment_target))
        return segments
