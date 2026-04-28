"""Module for the MPC-325 abstraction layer"""

import struct  # Handling binary
import time  # for device-specified wait-times
from typing import Final, Optional  # for constants and options
import threading  # for thread safety

import numpy as np  # for better typing
import serial  # Accessing sutter device through serial port


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
    # FIXME: I have no idea why, but for some reason manipulators fail to move at the top 3 speeds. All other speeds seem to work
    """ 
        15: 1300,
        14: 1218.75,
        13: 1137.5,
    """
    # FIXME: The issue must be hardware related, since the I double checked every command being sent to the device and
    # they match with the corresponding quickmove commands. The speed is also correctly being packed into the command
    # when checked before sending. Increasing the wait time between commands 1 and 2 sometimes allows higher speeds to work,
    # but not reliably.
    # on higher speeds, the manipulators try to move so the command is getting to them, but the movement itself doesn't happen. Slipping hardware???
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
    _BAUDRATE: Final = 128000
    _DATABITS: Final = serial.EIGHTBITS
    _STOPBITS: Final = serial.STOPBITS_ONE
    _PARITY: Final = serial.PARITY_NONE
    _S2MCONV: Final = np.float64(0.0625)
    _M2SCONV: Final = np.float64(16.0)
    _MINIMUM_MS: Final = 0
    _MAXIMUM_M: Final = 25000
    _MAXIMUM_S: Final = 400000
    _TIMEOUT: Final = 3  


    def __init__(self):
        # vars for a single instance
        self.ser = serial.Serial()  # init a closed port
        # Initialize settings:
        self._comm_lock = threading.Lock()
        self.end_marker_bytes = struct.pack("<B", 13)  # End marker (ASCII: CR)


    def read(self, size: int) -> bytes:
        """Read a specified number of bytes from the serial port.

        Args:
            size (int): Number of bytes to read.
        Returns:
            bytes: The bytes read from the serial port.
        """
        return self.ser.read(size)
        """
        Very stupid
        end = self.end_marker_bytes
        bytes_read = b''
        start_time = time.monotonic()
        while len(bytes_read) < size:
            possible_bytes = self.ser.in_waiting
            if possible_bytes > 0:
                byts = self.ser.read(possible_bytes)
                bytes_read += byts
                if end in bytes_read:
                    break
            if time.monotonic() - start_time > self._TIMEOUT:
                raise TimeoutError(f"Timeout while reading from serial port. Expected {size} bytes, got {len(bytes_read)} bytes. Last byte read was: {bytes_read[-1] if len(bytes_read) > 0 else 'None'}.") 
            time.sleep(0.4)
        return bytes_read
        """
        
    def open(self, port: Optional[str] = None):
        print(f"Opening Sutter MPC-325 on port {port}..."   )
        with self._comm_lock:
            # Open port
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
            name (str, optional):

        Returns:
           Tuple : unpacked data based on format, without the end marker. If end marker is invalid, throws.
        """
        unpacked_data = struct.unpack(format_str, output)
        # Check last byte for simple validation.
        if unpacked_data[-1] != 0x0D:
            raise ValueError(f"Invalid end marker sent from Sutter. Expected 0x0D, got {unpacked_data[-1]}. Response for command {name if name else 'unknown'} was: {unpacked_data}")
        return unpacked_data[:-1]

    def _flush(self):
        """Flushes i/o buffers. Also applies a wait time between commands. Every method should call this before sending a command."""
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.ser.flush()
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
            output = self.read(6)  # Expecting 6 bytes back: 1 byte for number of devices, 4 bytes for device statuses, 1 byte for end marker
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
            output = self.read(4) # Expecting 4 bytes back: 1 byte for active device number, 2 bytes for FW version, 1 byte for end marker
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
            output = self.read(2) # Expecting 2 bytes back: 1 byte for active device number, 1 byte for end marker
            unpacked = self._validate_and_unpack("2B", output, name="change_active_device")
            # check that the device is available and active
            if unpacked[0] != dev_num:
                raise RuntimeError(f"Failed to change active device. Expected {dev_num}, got {unpacked[0]}.")
            return True

    def get_current_position(self):
        """Get current position in microns.

        Returns:
            tuple: (x,y,z)
        """
        with self._comm_lock:
            self._flush()
            self.ser.write(bytes([67]))  # Send command (ASCII: C)
            output = self.read(14) # Expecting 14 bytes back: 1 byte drv number 3*4 bytes for x,y,z positions in microsteps, 1 byte for end marker
            unpacked = self._validate_and_unpack("=BIIIB", output, name="get_current_position")
            return (self._s2m(unpacked[1]), self._s2m(unpacked[2]), self._s2m(unpacked[3]))

    def calibrate(self):
        """Calibrate the device. Does the same thing as the calibrate button on the back of the control unit.
        (moves to 0,0,0)
        """
        with self._comm_lock:
            if self.is_connected:
                # add longer timeout for this
                self.ser.timeout = self._TIMEOUT * 10
                self._flush()
                self.ser.write(bytes([78]))  # Send command (ASCII: N)
                output = self.read(1) # Expecting 1 byte back: end marker 
                self._validate_and_unpack("<B", output, name="calibrate")  # Just to validate the end marker
                self.ser.timeout = self._TIMEOUT  # reset timeout to default
                return True


    def stop(self):
        """Stop the current movement"""
        self.ser.write(struct.pack("<B", 0x03))
        
    
    def move(self, x=None, y=None, z=None, quick_move=True, speed=7, segment=True, segment_length = 500):
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
                print(f"Quick moving to ({x}, {y}, {z})")
                self.quick_move_to(x, y, z)
            else:
                print(f"Slow moving to ({x}, {y}, {z}) at speed {speed}")
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
            print(f"Segmenting move into {len(segments)} segments of max length {segment_length} microns.") 
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
        speed = max(0, min(speed, 15))
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
    def segment_move(self, current_position:tuple, target_position:tuple, length:int) -> list[tuple]:
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

