import cv2 as cv
import numpy as np
import os

from PyQt6 import uic
from PyQt6 import QtWidgets
from PyQt6.QtCore import QObject
import matplotlib.pyplot as plt


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

        # FIXME: Debug
        self.currPos = 0

    def contact(self):
        # FIXME: broky broky
        return False

    def move_to_contact(self):
        while not self.contact():
            print(f"Moving to contact: {self.currPos}")
            if not self.debug_move(3):
                break

    # FIXME: Remove later
    def debug_move(self, change):
        if self.currPos + change > 100:
            return False
        self.currPos += change
        return True
