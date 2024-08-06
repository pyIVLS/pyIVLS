"""Module for the MPC-325 abstraction layer


"""

import struct  # Handling binary
import time  # for device-spesified wait-times
from typing import Final  # for constants
import serial  # Accessing sutter device through serial port
import numpy as np  # for better typing
import os

from PyQt6 import uic
from PyQt6 import QtWidgets
from PyQt6.QtCore import QObject

DEFAULT_PORT = (
    "/dev/serial/by-id/usb-Sutter_Sutter_Instrument_ROE-200_SI9NGJEQ-if00-port0"
)


class Mpc325(QObject):
    """Handles communication with the Sutter MPC-325 micromanipulator system.
    Methods are named after the commands in the manual.
    """

    def __init__(self):
        self._port = DEFAULT_PORT
        # constants from the manual.
        self._baudrate: Final = 128000
        self._timeout = 30  # seconds
        self._databits: Final = serial.EIGHTBITS
        self._stopbits: Final = serial.STOPBITS_ONE
        self._parity: Final = serial.PARITY_NONE
        self._s2mconv: Final = np.float64(0.0625)
        self._m2sconv: Final = np.float64(16.0)
        self._minimum_ms: Final = 0
        self._maximum_m: Final = 25000
        self._maximum_s: Final = (
            400000  # Manual says 266667, this is the actual maximum.
        )
        self.ser = serial.Serial()  # init a closed port

        # Load the settings widget
        QObject.__init__(self)
        self.path = os.path.dirname(__file__) + os.path.sep
        self.settingsWidget = uic.loadUi(self.path + "sutter_settingsWidget.ui")

        # initialize labels that might be modified:
        self.port_label = self.settingsWidget.findChild(QtWidgets.QLabel, "portLabel")

    # Close the connection when python garbage collection gets around to it.
    def __del__(self):
        if self.ser.is_open():
            self.ser.close()

    def open(self):
        # Open port
        try:
            self.ser = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                stopbits=self._stopbits,
                parity=self._parity,
                timeout=self._timeout,
                bytesize=self._databits,
            )
            print(
                f"Port {self._port} is open: {self.ser.is_open}. Flushing I/O to initialize."
            )
            self._flush()
        except serial.SerialException as e:
            print(f"Error: {e}")

    def _validate_and_unpack(self, format_str, output):
        """Takes in a struct of bytes, validates end marker and unpacks the data.
        Handles possible errors for the whole code.

        Args:
            format (str): format string for struct
            output (): bytes recieved from serial port

        Returns:
           Tuple : unpacked data based on format, without the end marker. If end marker is invalid, returns [-1, -1, -1, -1, -1, -1].
        """
        unpacked_data = struct.unpack(format_str, output)
        # Check last byte for simple validation.
        if unpacked_data[-1] != 0x0D:
            print(
                f"Invalid end marker sent from device. Expected 0x0D, got {unpacked_data[-1]}. Flushing buffers."
            )
            self._flush()
            return [-1, -1, -1, -1, -1, -1]  # Return error code
        else:
            return unpacked_data[:-1]

    def _flush(self):
        """Flushes i/o buffers. Also applies a wait time between commands. Every method should call this before sending a command."""
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        time.sleep(
            0.002
        )  # Hardcoded wait time (2 ms) between commands from the manual.

    def get_connected_devices_status(self):
        """Get the status of connected micromanipulators

        Returns:
            tuple: first element is how many devices connected, second element is a list representing
            the status of connected devices
        """
        self._flush()
        self.ser.write(bytes([85]))  # Send command to the device (ASCII: U)
        output = self.ser.read(6)

        unpacked_data = self._validate_and_unpack("6B", output)
        num_devices = unpacked_data[0]  # Number of devices connected
        device_statuses = unpacked_data[1:5]  # Status of each device (0 or 1)

        return (num_devices, device_statuses)

    def get_active_device(self):
        """Returns the current active device.

        Returns:
            int: active device number
        """
        self._flush()
        self.ser.write(bytes([75]))  # Send command to the device (ASCII: K)
        output = self.ser.read(4)
        unpacked = self._validate_and_unpack("4B", output)
        return unpacked[0]

    def change_active_device(self, dev_num: int):
        """Change active device

        Args:
            devNum (int): Device number to be activated (1-4 on this system)

        Returns:
            bool: Change successful
        """
        self._flush()
        command = struct.pack("<2B", 73, dev_num)
        self.ser.write(command)  # Send command to the device (ASCII: I )

        output = self.ser.read(2)
        unpacked = self._validate_and_unpack("2B", output)
        if unpacked[0] == 69:  # If error
            return False
        else:
            return True

    def get_current_position(self):
        """Get current position in microns.

        Returns:
            tuple: (x,y,z)
        """
        self._flush()
        self.ser.write(bytes([67]))  # Send command (ASCII: C)
        output = self.ser.read(14)
        unpacked = self._validate_and_unpack("=BIIIB", output)

        return (self._s2m(unpacked[1]), self._s2m(unpacked[2]), self._s2m(unpacked[3]))

    def calibrate(self):
        """Calibrate the device. Does the same thing as the calibrate button on the back of the control unit.
        (moves to 0,0,0)
        """
        self._flush()
        self.ser.write(bytes([78]))  # Send command (ASCII: N)
        output = self.ser.read(1)
        self._validate_and_unpack("B", output)

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
        print(
            f"Moving to: ({self._s2m(x_s)}, {self._s2m(y_s)}, {self._s2m(z_s)}) in microns."
        )
        command2 = struct.pack(
            "<3I", x_s, y_s, z_s
        )  # < to enforce little endianness. Just in case someone tries to run this on an IBM S/360
        command3 = struct.pack("<B", 13)

        self.ser.write(command1)
        self.ser.write(command2)
        self.ser.write(command3)
        output = self.ser.read(1)
        self._validate_and_unpack("B", output)

    def slow_move_to(self, speed, x: np.float64, y: np.float64, z: np.float64):
        """Slower move in straight lines. Less prone to collisions

        Args:
            speed (int): speed in range 0-15. Enforced in the code.
            x (np.float64): x in microns
            y (np.float64): y in microns
            z (np.float64): z in microns

        """
        self._flush()
        # Enforce speed limits
        speed = max(0, min(speed, 15))

        # Pack first part of command
        command1 = struct.pack("<2B", 83, speed)
        # check bounds for coordinates and convert to microsteps. Makes really *really* sure that the values are good.
        x_s = self._handrail_step(self._m2s(self._handrail_micron(x)))
        y_s = self._handrail_step(self._m2s(self._handrail_micron(y)))
        z_s = self._handrail_step(self._m2s(self._handrail_micron(z)))
        print(
            f"Moving to: ({self._s2m(x_s)}, {self._s2m(y_s)}, {self._s2m(z_s)}) in microns."
        )
        command2 = struct.pack(
            "<3I", x_s, y_s, z_s
        )  # < to enforce little endianness. Just in case someone tries to run this on an IBM S/360

        self.ser.write(command1)
        time.sleep(0.03)  # wait period spesified in the manual (30 ms)
        self.ser.write(command2)
        output = self.ser.read(1)
        self._validate_and_unpack("B", output)

    def stop(self):
        """Stop the current movement"""
        self._flush()
        self.ser.write(bytes([3]))  # Send command (ASCII: <ETX>)
        output = self.ser.read(1)
        self._validate_and_unpack("B", output)

    # Handrails for microns/microsteps. Realistically would be enough just to check the microsteps, but CATCH ME LETTING A MISTAKE BREAK THESE
    def _handrail_micron(self, microns) -> np.uint32:
        return max(self._minimum_ms, min(microns, self._maximum_m))

    def _handrail_step(self, steps) -> np.uint32:
        return max(self._minimum_ms, min(steps, self._maximum_s))

    # Function to convert microns to microsteps.
    def _m2s(self, microns: np.float64) -> np.uint32:
        return np.uint32(microns * self._m2sconv)

    # Function to convert microsteps to microns.
    def _s2m(self, steps: np.uint32) -> np.float64:
        return np.float64(steps * self._s2mconv)
