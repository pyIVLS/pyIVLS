"""
This is a class for peltier controller

"""

import pyvisa
from threading import Lock


class itc503:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.lock = Lock()

    def open(self, source=None):
        """Opens the itc503 device for use

        Returns status
            0 - no error
        """
        if source is None:
            raise ValueError("Source address is empty.")
        with self.lock:
            self.device = self.rm.open_resource(source)
            self.device.write_termination = "\r\n"
            self.device.read_termination = "\r\n"
            # "Q2" tells ITC to use also \r as a termination character has to be used only after restarting ITC
            self.device.write("Q2")
            # "C3" tells instrument to be at REMOTE UNLOCKED state different numbers after C tell ITC to be at different states -> see ITC503 user manual
            self.device.write("C3")
            self.device.read_bytes(3)
            self.device.clear()
        return 0

    def close(self):
        """Closes connection to itc 503 and restores the device into LOCAL MODE

        Returns status
            0 - no error
        """
        with self.lock:
            self.device.write("C0")
            # ITC wants to send confirmation after some commands so we read those after command
            self.device.read_bytes(3)
            self.device.close()
        return 0

    def setT(self, temperature):
        """set the setpoint

        Returns status
            0 - no error
        """
        with self.lock:
            if temperature < 10:
                self.device.write(f"T{temperature:.3f}")
            elif temperature < 100:
                self.device.write(f"T{temperature:.2f}")
            else:
                self.device.write(f"T{temperature:.1f}")
            self.device.read_bytes(3)
            self.device.clear()
        return 0

    def getData(self):
        """get the data out of controller and return it as a float

        Returns:
            temperature as a float
        """
        with self.lock:
            self.device.clear()  # it may be an exageration, but it feels that sometimes there are some bytes left in buffer
            self.device.write("R1")
            str = self.device.read_bytes(8)  # a workaround, as the number of bytes is different, and self.device.read does not work
            if str[-1] == ord("\r"):
                temp = float(str[1:-1])
                self.device.clear()
            else:
                temp = float(str[1:-2])
            return temp
