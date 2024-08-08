#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets

from plugins.Sutter.mpc_hal import Mpc325


class pyIVLS_Sutter_plugin:
    """Hooks for Sutter micromanipulator plugin"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.hal = Mpc325()

    @hookimpl
    def get_setup_interface(self, pm) -> dict:
        """Sets up camera, preview, and save buttons for VenusUSB2 camera plugin

        Returns:
            dict: name, widget
        """
        # FIXME: Check buttons, see below.
        """
        preview_button = self.camera.settingsWidget.findChild(
            QtWidgets.QPushButton, "cameraPreview"
        )
        save_button = self.camera.settingsWidget.findChild(
            QtWidgets.QPushButton, "cameraSave"
        )
        # Connect widget buttons to functions
        preview_button.clicked.connect(self.camera.preview_button)
        save_button.clicked.connect(self.camera.save_button)
            """

        return {"Sutter": self.hal.settingsWidget}
    
    @hookimpl
    def get_functions(self, *args):
        if "micromanipulator" in args
            return {
                "mm_change_active_device": self.hal.change_active_device,
                "mm_move": self.hal.slow_move_to,
                "mm_stop": self.hal.stop   
            }

    @hookimpl
    def mm_change_active_device(self, dev_num):
        """Micromanipulator active device change.

        Args:
            *args: device number
        """
        if self.hal.change_active_device(dev_num):
            return True
        return False
    
    # FIXME: Create a wrapper function for move through settings. 
    @hookimpl
    def mm_move(self, speed, x, y, z):
        """Micromanipulator move.

        Args:
            *args: x, y, z
        """
        if self.hal.slow_move_to(speed, x, y, z):
            return True
        return False
    
    @hookimpl
    def mm_stop(self):
        """Micromanipulator stop.
        """
        self.hal.stop()
    