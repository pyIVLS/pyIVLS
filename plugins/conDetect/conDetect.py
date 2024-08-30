import cv2 as cv
import numpy as np
import os

from PyQt6 import uic
from PyQt6 import QtWidgets
from PyQt6.QtCore import QObject
import matplotlib.pyplot as plt
import pyftdi.serialext
import pyIVLS_constants as const

import time


class ConDetect:

    def __init__(self):

        # Initialize the pluginmanager as empty
        self.mm_func = None
        self.smu_func = None
        self.port = None
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        filename = (
            os.path.splitext(os.path.basename(__file__))[0] + "_settingsWidget.ui"
        )
        self.settingsWidget = uic.loadUi(self.path + filename)

    def connect(self, pm):
        self.port = pyftdi.serialext.serial_for_url(const.CONDETECT_PORT, baudrate=400)

        if self.mm_func is None:
            self.mm_func = pm.hook.get_functions(args={"function": "micromanipulator"})[
                0
            ]
            if self.mm_func.get("Sutter"):
                self.mm_func = self.mm_func.get("Sutter")
                self.mm_func["open"]()
            else:
                raise Exception("Can't access sutter functions")

        if self.smu_func is None:
            self.smu_func = pm.hook.get_functions(args={"function": "smu"})[0]
            if self.smu_func.get("Keithley2612B"):
                self.smu_func = self.smu_func.get("Keithley2612B")
                self.smu_func["open"]()
            else:
                raise Exception("Can't access Keithley2612B functions")

    def measurement_mode(self, rts, dtr):
        """Sets the pins to send 5v

        Args:
            rts (bool): rts on/off
            dtr (bool): dtr on/off
        """
        # rts seems to act in reverse so correct for that
        self.port.rts = not rts
        # dtr seems to act in reverse so correct for that
        self.port.dtr = not dtr

    def contact(self):
        res = self.smu_func["measure_resistance"](channel="smua")
        # NOTE: Just a random guess at a good value
        if res[0] < 1000:
            return True
        # dtr sinen
        # rts punane

        return False

    def move_to_contact(self, manipulator):
        assert self.mm_func["mm_change_active_device"](dev_num=manipulator)

        # FIXME: Current implementation relies on the wires being corrected to the same manipulators.
        # only supports two manipulators moving
        if manipulator == 1:
            self.measurement_mode(False, True)
        elif manipulator == 2:
            self.measurement_mode(True, False)

        while not self.contact():
            move_result = self.mm_func["mm_lower"](z_change=50)
            if not move_result:
                print(f"manipulator {manipulator} reached end of travel")
                return False
        self.measurement_mode(False, False)
        return True

    def debug(self, pm):
        print("Debugging")
        if self.port is None:
            self.connect(pm)  # Connect to the serial port
        try:
            self.move_to_contact(1)

            self.move_to_contact(2)

        except Exception as e:
            print(f"Haha stupid code go brrrrr: {e}")
        finally:
            print("Yep yep done debugging")
