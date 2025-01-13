import os
from PyQt6 import uic

# FIXME: Debug
import cv2 as cv
import matplotlib.pyplot as plt


class sweep:
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
        print("Test starting")
        self.statusLabel.setText("Running test function")
        mm_functions = self.pm.hook.get_functions(args={"function": "micromanipulator"})
        mm_functions = mm_functions[0]
        mm_functions = mm_functions["Sutter"]
        print(mm_functions.keys())

        cam_functions = self.pm.hook.get_functions(args={"function": "camera"})
        cam_functions = cam_functions[0]
        cam_functions = cam_functions["VenusUSB2"]
        print(cam_functions.keys())

        aff_functions = self.pm.hook.get_functions(args={"function": "coordinate conversion"})
        aff_functions = aff_functions[0]
        aff_functions = aff_functions["Affine"]
        print(aff_functions.keys())


        TLCCS_functions = self.pm.hook.get_functions(args={"function": "spectrometer"})
        TLCCS_functions = TLCCS_functions[0]
        TLCCS_functions = TLCCS_functions["TLCCS"]
        print(TLCCS_functions.keys())

        try:
            assert mm_functions["open"](), "Sutter failed to open"

            assert cam_functions["open"](), "Camera failed to open"

            assert TLCCS_functions["open"](), "Spec failed to open"

            aff_functions["coords"]((0,0))

        except Exception as e:
            print(e)
            self.statusLabel.setText("Test failed")
            return
        
        print("Test complete")


        self.statusLabel.setText("Test function complete")
