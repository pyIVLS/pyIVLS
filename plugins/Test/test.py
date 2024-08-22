import os
from PyQt6 import uic

# FIXME: Debug
import cv2 as cv
import matplotlib.pyplot as plt


class Test:
    """Tester plugin for pyIVLS"""

    def __init__(self):

        # Initialize the pluginmanager as empty
        self.pm = None

        # Initialize settings widget buttons
        self.runButton = None
        self.statusLabel = None

        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        filename = (
            os.path.splitext(os.path.basename(__file__))[0] + "_settingsWidget.ui"
        )
        self.settingsWidget = uic.loadUi(self.path + filename)

    def run_button(self):
        """Run the test function"""
        self.statusLabel.setText("Running test function")
        mm_functions = self.pm.hook.get_functions(args={"function": "micromanipulator"})
        print(mm_functions)
        no_functions = self.pm.hook.get_functions(args={"function": "aint"})
        print(no_functions)
