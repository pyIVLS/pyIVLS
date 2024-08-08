import cv2 as cv
import numpy as np
import os

from PyQt6 import uic
from PyQt6 import QtWidgets
from PyQt6.QtCore import QObject
import matplotlib.pyplot as plt


class Template:
    """Template plugin for pyIVLS"""

    def __init__(self):

        # Initialize the pluginmanager as empty
        self.pm = None
        # NOTE: This is unncessary if the plugin has no dependencies.

        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        filename = (
            os.path.splitext(os.path.basename(__file__))[0] + "_settingsWidget.ui"
        )
        self.settingsWidget = uic.loadUi(self.path + filename)

        # save the labels that might be modified:
        self.possible_label = self.settingsWidget.findChild(
            QtWidgets.QLabel, "possibleLabel"
        )

    def find_button(self) -> bool:
        """Template for a find button

        Returns:
            bool: _description_
        """
        raise NotImplementedError

    def save_button(self) -> bool:
        """Template for a save button

        Returns:
            bool: _description_
        """
        raise NotImplementedError
