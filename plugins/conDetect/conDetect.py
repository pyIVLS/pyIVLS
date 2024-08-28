import cv2 as cv
import numpy as np
import os

from PyQt6 import uic
from PyQt6 import QtWidgets
from PyQt6.QtCore import QObject
import matplotlib.pyplot as plt
import pyftdi.serialext
import pyIVLS_constants as const


class ConDetect:

    def __init__(self):

        # Initialize the pluginmanager as empty
        self.pm = None
        self.mm_func = None
        self.smu_func = None
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        filename = (
            os.path.splitext(os.path.basename(__file__))[0] + "_settingsWidget.ui"
        )
        self.settingsWidget = uic.loadUi(self.path + filename)

    def connect(self):
        self.port = pyftdi.serialext.serial_for_url(const.CONDETECT_PORT, baudrate=400)
        if self.mm_func is None:
            self.mm_func = self.pm.hook.get_functions(
                args={"function": "micromanipulator"}
            )[0]
            if self.mm_func.get("Sutter"):
                self.mm_func = self.mm_func.get("Sutter")
                self.mm_func["open"]()
            else:
                raise Exception("Can't access sutter functions")
            
        if self.smu_func is None:
            self.smu_func = self.pm.hook.get_functions(
                args={"function": "smu"}
            )[0]
            if self.smu_func.get("Keithley2612B"):
                self.smu_func = self.smu_func.get("Keithley2612B")
                self.smu_func["open"]()
            else:
                raise Exception("Can't access Keithley2612B functions")
            
    def measurement_mode(self, channel):
        if channel == 1:
            self.port.rts = True
            self.port.dtr = False
        elif channel == 2:
            self.port.rts = False
            self.port.dtr = True
        else:
            raise Exception("Invalid channel number")
          
    def contact(self):
        # FIXME: broky broky
        return False

    def move_to_contact(self):
        while not self.contact():
            print(
                f"Moving to contact until I hit something :DDDDD t: Sutter manipulator"
            )
            moveResult = self.mm_func["mm_lower"](z_change=10)
            print(moveResult)
            if not moveResult[0]:
                print("Ouch, i hit something")
                break

    def debug(self):
        print("Debugging")
        if self.port is None:
            self.connect()  # Connect to the serial port

        try:
            print(self.mm_func["mm_change_active_device"](dev_num=4))
        except Exception as e:
            print(f"Haha stupid code go brrrrr: {e}")
  
        self.move_to_contact()
