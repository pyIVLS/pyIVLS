import cv2 as cv
import numpy as np
import os

from PyQt6 import uic
from PyQt6 import QtWidgets
from PyQt6.QtCore import QObject
import matplotlib.pyplot as plt
import pyftdi.serialext


class ConDetect:

    def __init__(self):

        # Initialize the pluginmanager as empty
        self.pm = None
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        filename = (
            os.path.splitext(os.path.basename(__file__))[0] + "_settingsWidget.ui"
        )
        self.settingsWidget = uic.loadUi(self.path + filename)

    def connect(self):
        self.port = pyftdi.serialext.serial_for_url(
            "ftdi://ftdi:232:UUT1/1", baudrate=400
        )

    def contact(self):
        # FIXME: broky broky
        return False

    def move_to_contact(self):
        while not self.contact():
            print(
                f"Moving to contact until I hit something :DDDDD t: Sutter manipulator"
            )
            moveResult = self.pm.hook.mm_lower(z_change=100)
            print(moveResult)
            if not moveResult[0]:
                print("Owie, i hit something")
                break

    def debug(self):
        print("Debugging")
        print(self.pm.hook.open())
        try:
            print(self.pm.hook.mm_change_active_device(dev_num=4))
        except Exception as e:
            print(e)
        # self.connect()
        self.move_to_contact()
