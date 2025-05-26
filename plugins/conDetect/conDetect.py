# from pyftdi.ftdi import Ftdi
import serial
from threading import Lock


class conDetect:
    def __init__(self):
        # for ftdi        self.device = None
        self.device = (
            serial.Serial()
        )  # https://pyserial.readthedocs.io/en/latest/pyserial_api.html
        self.lock = Lock()

    def connect(self, source):
        ### ftdi:///? should be used to retrieve the available FTDI URLs with serial number
        ### see https://eblot.github.io/pyftdi/urlscheme.html
        # for ftdi          self.device = Ftdi().create_from_url("ftdi://%d:%d:%s/1"% (VID, PID, serial))
        with self.lock:
            self.device.port = source
            self.device.open()
            self.device.reset_input_buffer()
            self.device.reset_output_buffer()

    def disconnect(self):
        # for ftdi         self.device.purge_buffers()
        # for ftdi         self.device.close()
        # for ftdi         self.device = None
        with self.lock:
            self.device.reset_input_buffer()
            self.device.reset_output_buffer()
            self.device.close()

    def setDefault(self):
        # for ftdi            self.device.set_rts(True)
        # for ftdi            self.device.set_dtr(True)
        with self.lock:
            self.device.rts = True
            self.device.dtr = True

    def loCheck(self, status):
        # for ftdi            self.device.set_dtr(not status)
        with self.lock:
            self.device.dtr = not status

    def hiCheck(self, status):
        # for ftdi            self.device.set_rts(not status)
        with self.lock:
            self.device.rts = not status
