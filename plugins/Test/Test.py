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
        mm_functions = mm_functions[0]
        mm_functions = mm_functions["Sutter"]
        print(mm_functions.keys())

        cam_functions = self.pm.hook.get_functions(args={"function": "camera"})
        cam_functions = cam_functions[0]
        cam_functions = cam_functions["VenusUSB2"]
        print(cam_functions.keys())

        aff_functions = self.pm.hook.get_functions(
            args={"function": "coordinate conversion"}
        )
        aff_functions = aff_functions[0]
        aff_functions = aff_functions["Affine"]
        print(aff_functions.keys())

        TLCCS_functions = self.pm.hook.get_functions(args={"function": "spectrometer"})
        TLCCS_functions = TLCCS_functions[0]
        TLCCS_functions = TLCCS_functions["TLCCS"]
        print(TLCCS_functions.keys())

        try:
            print(cam_functions["open"]())
            pic = cam_functions["camera_get_image"]()
            cv.imshow("Test", pic)
            print(TLCCS_functions["open"]())
            data = TLCCS_functions["run_scan"]()
            print(data)
        except Exception as e:
            print(f"exception: {e}")
        self.statusLabel.setText("Test function complete")
