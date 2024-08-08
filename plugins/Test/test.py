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
        image = self.pm.hook.camera_get_image()
        print("I got an image")

        """"
        ret = self.pm.hook.affine_coords(x=0, y=0)

        print(f"hooked Affine coordinates: {ret[0]}")
        """
        # FIXME: coords no work

        if self.pm.hook.mm_change_active_device(dev_num=2):
            print("Changed active device with great success")

        if self.pm.hook.mm_move(speed=1, x=200, y=200, z=200):
            print("Moved micromanipulator with great success")

        if self.pm.hook.mm_move(speed=1, x=0, y=0, z=0):
            print("Moved micromanipulator with great success")

        if self.pm.hook.mm_change_active_device(dev_num=1):
            print("Changed active device with great success")

        if self.pm.hook.mm_move(speed=1, x=0, y=100, z=200):
            print("Moved micromanipulator with great success")

        self.statusLabel.setText("Test function complete")
