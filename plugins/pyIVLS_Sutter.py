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

        calibrate_button = self.hal.settingsWidget.findChild(
            QtWidgets.QPushButton, "calibrateButton"
        )

        connect_button = self.hal.settingsWidget.findChild(
            QtWidgets.QPushButton, "connectButton"
        )

        connect_button.clicked.connect(self.hal.open)

        calibrate_button.clicked.connect(self.hal.calibrate)

        return {"Sutter": self.hal.settingsWidget}

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
        """Micromanipulator stop."""
        self.hal.stop()
