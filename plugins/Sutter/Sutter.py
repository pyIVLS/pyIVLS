"""Module for the MPC-325 abstraction layer"""

import struct  # Handling binary
import time  # for device-spesified wait-times
from datetime import datetime  # for error messages
from typing import Final  # for constants
import threading  # for thread safety

import numpy as np  # for better typing
import serial  # Accessing sutter device through serial port


class SutterError(Exception):
    """
    # NOTE UNUSED
    From readme:
    0 = no error,
    1 = Value error,
    2 = Any error reported by dependent plugin,
    3 = missing functions or plugins,
    4 = harware error
    plugins return errors in form of list [number, {"Error message":"Error text", "Exception":f"e"}]
    e.g. [1, {"Error message":"Value error in sweep plugin: SMU limit prescaler field should be numeric"}]
    error text will be shown in the dialog message in the interaction plugin,
    so the error text should contain the plugin name,
    e.g. return [1, {"Error message":"Value error in Keithley plugin: drain nplc field should be numeric"}]

    """

    def __init__(self, message, error_code):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.timestamp = datetime.now().strftime("%H:%M:%S.%f")
        self.message = f"{self.timestamp}: {self.message} (Sutter error Code: {self.error_code})"

    def __str__(self):
        return self.message


class Mpc325:
    """
    Handles communication with the Sutter MPC-325 micromanipulator system.
    Methods are named after the commands in the manual.
    revision 0.2
    2025.05.22
    otsoha
    """

    # constants from the manual. These are the the same for the whole class
    # move speeds in micrometers per second
    # FIXME: I have no idea why, but for some reason manipulator 1 fails to move at the top 2 speeds.
    """ 
    15: 1300,
    14: 1218.75,
    """
    _MOVE_SPEEDS: Final = {

        13: 1137.5,
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
    _BAUDRATE: Final = 128000
    _DATABITS: Final = serial.EIGHTBITS
    _STOPBITS: Final = serial.STOPBITS_ONE
    _PARITY: Final = serial.PARITY_NONE
    _S2MCONV: Final = np.float64(0.0625)
    _M2SCONV: Final = np.float64(16.0)
    _MINIMUM_MS: Final = 0
    _MAXIMUM_M: Final = 25000
    _MAXIMUM_S: Final = 400000  # Manual says 266667, this is the actual maximum. UPDATE 23.5.2025: This has been updated in the manual as well.
    _TIMEOUT: Final = 120  # seconds, to allow for long moves. 
    # WARNING: TOO SHORT TIMEOUT WILL LEAD TO COMPLETION INDICATORS BEING LEFT IN THE BUFFER. This results in the move functions returning a completed move
    # even though the move has not been completed yet. This leads to further commands being sent before the move is completed, which leads to missed commands.

    def __init__(self):
        # vars for a single instance
        self.ser = serial.Serial()  # init a closed port
        # Initialize settings:
        self.speed = 0
        self.quick_move = False
        self.port = ""
        self._comm_lock = threading.Lock()
        self._stop_requested = threading.Event()
        self.end_marker_bytes = struct.pack("<B", 13)  # End marker (ASCII: CR)


    def update_internal_state(self, quick_move: bool = None, speed: int = None, source: str = None):
        """Update the internal state of the micromanipulator.

        Args:
            quick_move (bool): Whether to use quick move or not.
            speed (int): Speed in range 0-15.
            source (str): Source for the micromanipulator.
        """
        # NOTE: checking can be added here, but i dont think its necessary. Reasoning:
        # Quickmove is a boolean, it can only be wrongly set if the user manually calls this function with a wrong parameter
        # Speed is selected from a combobox, that dynamically reads the speedlist from this class.
        # Source is a string, so it can be anything.
        if quick_move is not None:
            self.quick_move = quick_move
        if speed is not None:
            self.speed = speed
        if source is not None:
            self.port = source

    def open(self, port: str = None):
        with self._comm_lock:
            # Open port
            if port is None:
                port = self.port
            if not self.is_connected():
                self.ser.port = port
                self.ser.baudrate = self._BAUDRATE
                self.ser.parity = self._PARITY
                self.ser.stopbits = self._STOPBITS
                self.ser.timeout = self._TIMEOUT
                self.ser.bytesize = self._DATABITS
                self.ser.open()
                time.sleep(0.2)  # wait for the port to open??
                self._flush()  # Flush the buffers after opening the port??

                # ok so these are here just because the connection sometimes hangs on first open after turning sutter on.

    def close(self):
        with self._comm_lock:
            if self.is_connected():
                self.ser.close()

    def is_connected(self):
        """Check if the port is open and connected.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self.ser.is_open

    def _validate_and_unpack(self, format_str, output, name=None):
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
        assert unpacked_data[-1] == 0x0D, f"Invalid end marker sent from Sutter. Expected 0x0D, got {unpacked_data[-1]}"
        return unpacked_data[:-1]

    def _flush(self):
        """Flushes i/o buffers. Also applies a wait time between commands. Every method should call this before sending a command."""
        input_waiting = self.ser.in_waiting
        output_waiting = self.ser.out_waiting
        if input_waiting > 0:
            print(f"WARNING: Input buffer was not empty. {input_waiting} bytes were waiting to be read.")
            print(f"Timeout is {self.ser.timeout} seconds, which seems to be too short for the move to complete")
            stuff = self.ser.read(input_waiting)
            print(stuff)
        if output_waiting > 0:
            print(f"WARNING: Output buffer was not empty. {output_waiting} bytes were waiting to be read.")
            print(f"Timeout is {self.ser.timeout} seconds, which seems to be too short for the move to complete")
            stuff = self.ser.read(output_waiting)
            print(stuff)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.ser.flush()
        # NOTE: added some more waittime to try out.
        time.sleep(0.002)  # Hardcoded wait time (2 ms) between commands from the manual.

    def get_connected_devices_status(self):
        """Get the status of connected micromanipulators

        Returns:
            tuple: first element is how many devices connected, second element is a list representing
            the status of connected devices
        """
        with self._comm_lock:
            self._flush()
            self.ser.write(bytes([85]))  # Send command to the device (ASCII: U)
            output = self.ser.read_until(expected=self.end_marker_bytes)
            unpacked_data = self._validate_and_unpack("6B", output, name="get_connected_devices_status")
            num_devices = unpacked_data[0]  # Number of devices connected
            device_statuses = unpacked_data[1:5]  # Status of each device (0 or 1)
            return (num_devices, device_statuses)

    def get_active_device(self):
        """Returns the current active device.

        Returns:
            int: active device number
        """
        with self._comm_lock:
            self._flush()
            self.ser.write(bytes([75]))  # Send command to the device (ASCII: K)
            output = self.ser.read_until(expected=self.end_marker_bytes)
            unpacked = self._validate_and_unpack("4B", output, name="get_active_device")
            return unpacked[0]

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
            self.ser.write(command)  # Send command to the device (ASCII: I )
            output = self.ser.read(2) # response should be 2 bytes, 1st is the currently active device, 2nd is the completion indicator
            unpacked = self._validate_and_unpack("2B", output, name="change_active_device")
            if unpacked[0] != dev_num:
                return False  
            return True

    def get_current_position(self):
        """Get current position in microns.

        Returns:
            tuple: (x,y,z)
        """
        with self._comm_lock:
            self._flush()
            self.ser.write(bytes([67]))  # Send command (ASCII: C)
            output = self.ser.read(14)
            unpacked = self._validate_and_unpack("=BIIIB", output, name="get_current_position")
            return (self._s2m(unpacked[1]), self._s2m(unpacked[2]), self._s2m(unpacked[3]))

    def calibrate(self):
        """Calibrate the device. Does the same thing as the calibrate button on the back of the control unit.
        (moves to 0,0,0)
        """
        with self._comm_lock:
            if self.is_connected:
                self._flush()
                self.ser.write(bytes([78]))  # Send command (ASCII: N)
                output = self.ser.read_until(expected=self.end_marker_bytes)
                assert output[-1] == 0x0D, f"Invalid end marker sent from Sutter. Expected 0x0D, got {output[-1]}"
                return True
                

    def stop(self):
        """Stop the current movement"""
        with self._comm_lock:
            self._flush()
            self.ser.write(bytes([3]))  # Send command (ASCII: <ETX>)
            output = self.ser.read_until(expected=self.end_marker_bytes)
            assert output[-1] == 0x0D, f"Invalid end marker sent from Sutter. Expected 0x0D, got {output[-1]}"

    def move(self, x=None, y=None, z=None):
        """Move to a position. If quick_move is set to True, the movement will be at full speed.

        Args:
            x (np.float64): x in microns
            y (np.float64): y in microns
            z (np.float64): z in microns
        """
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
            print(f"Already at position {curr_pos}. Not moving.")
            return

        if self.quick_move:
            self.quick_move_to(x, y, z)
        else:
            self.slow_move_to(x, y, z)

    def quick_move_to(self, x: np.float64, y: np.float64, z: np.float64):
        """Quickmove orthogonally at full speed.

        Args:
            x (np.float64): x in microns
            y (np.float64): y in microns
            z (np.float64): z in microns
        """
        with self._comm_lock:
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

            end_marker_bytes = struct.pack("<B", 13)  # End marker (ASCII: CR)

            byt = self.ser.read_until(expected=end_marker_bytes)  # Read until the end marker (ASCII: CR)
            assert byt[-1] == 0x0D, f"Invalid end marker sent from Sutter. Expected 0x0D, got {byt[-1]}"

    def slow_move_to(self, x: np.float64, y: np.float64, z: np.float64, speed=None):
        """Slower move in straight lines. Speed is set as a class variable. (Or given as an argument)

        Args:
            speed (int): speed in range 0-15. Enforced in the code.
            x (np.float64): x in microns
            y (np.float64): y in microns
            z (np.float64): z in microns

        """
        with self._comm_lock:
            if speed is None:
                speed = self.speed
            self._flush()
            # Enforce speed limits
            speed = max(0, min(speed, 15))
            # Pack first part of command
            command1 = struct.pack("<2B", 83, speed)
            # check bounds for coordinates and convert to microsteps. Makes really *really* sure that the values are good.
            x_s = self._handrail_step(self._m2s(self._handrail_micron(x)))
            y_s = self._handrail_step(self._m2s(self._handrail_micron(y)))
            z_s = self._handrail_step(self._m2s(self._handrail_micron(z)))
            print(f"Moving to {self._handrail_micron(x)}, {self._handrail_micron(y)}, {self._handrail_micron(z)} with speed {speed} ({self._MOVE_SPEEDS[speed]} microns/s)")
            command2 = struct.pack("<3I", x_s, y_s, z_s)  # < to enforce little endianness. Just in case someone tries to run this on an IBM S/360
            self.ser.write(command1)
            time.sleep(0.03)  # wait period specified in the manual (30 ms)
            self.ser.write(command2)

            end_marker_bytes = struct.pack("<B", 13)  # End marker (ASCII: CR)
            byt = self.ser.read_until(expected=end_marker_bytes)  # Read until the end marker (ASCII: CR)
            assert byt[-1] == 0x0D, f"Invalid end marker sent from Sutter. Expected 0x0D, got {byt[-1]}"

    # Handrails for microns/microsteps. Realistically would be enough just to check the microsteps, but CATCH ME LETTING A MISTAKE BREAK THESE
    def _handrail_micron(self, microns) -> np.uint32:
        return max(self._MINIMUM_MS, min(microns, self._MAXIMUM_M))

    def _handrail_step(self, steps) -> np.uint32:
        return max(self._MINIMUM_MS, min(steps, self._MAXIMUM_S))

    # Function to convert microns to microsteps.
    def _m2s(self, microns: np.float64) -> np.uint32:
        return np.uint32(microns * self._M2SCONV)

    # Function to convert microsteps to microns.
    def _s2m(self, steps: np.uint32) -> np.float64:
        return np.float64(steps * self._S2MCONV)

    def _calculate_wait_time(self, speed, x, y, z):
        """Approximates time of travel. NOTE: make sure to pass microns, not microsteps to this

        Args:
            speed (int): speed
            x (_type_): x target in microns
            y (_type_): y target in microns
            z (_type_): z target in microns

        Returns:
            _type_: move speed in seconds
        """
        curr_pos = self.get_current_position()
        x_diff = abs(curr_pos[0] - x)
        y_diff = abs(curr_pos[1] - y)
        z_diff = abs(curr_pos[2] - z)

        total_diff = x_diff + y_diff + z_diff

        time = total_diff / self._MOVE_SPEEDS[speed]
        return time
