import os
from PyQt6 import uic

# FIXME: Debug
import cv2 as cv


class Test:
    """Tester plugin for pyIVLS"""

    def __init__(self):

        # Initialize the pluginmanager as empty
        self.pm = None

        # Initialize settings widget buttons
        self.runButton = None
        self.statusLabel = None

        # Load the settings widget
        self.path = os.path.dirname(__file__) + os.path.sep
        self.settingsWidget = uic.loadUi(self.path + "test_settingsWidget.ui")

    def run_button(self):
        """Run the test function"""
        image = self.pm.hook.camera_get_image()[0]
        if image:
            cv.imshow("Test image", image)
            cv.waitKey(0)
        print("Hooked camera")

        (x, y) = self.pm.hook.affine_coords(0, 0)[0]

        print(f"hooked Affine coordinates: {x}, {y}")

        if self.pm.hook.mm_change_active_device(2):
            print("Changed active device with great success")

        if self.pm.hook.mm_move(1, 100, 100, 100):
            print("Moved micromanipulator with great success")

        self.statusLabel.setText("Test function complete")
