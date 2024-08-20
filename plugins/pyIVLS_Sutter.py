#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets

from plugins.Sutter.sutter import Mpc325


class pyIVLS_Sutter_plugin:
    """Hooks for Sutter micromanipulator plugin"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.hal = Mpc325()

    @hookimpl
    def get_setup_interface(self, pm) -> dict:
        """Sets up camera, preview, and save buttons for sutter plugin

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

        status_button = self.hal.settingsWidget.findChild(
            QtWidgets.QPushButton, "statusButton"
        )
        save_button = self.hal.settingsWidget.findChild(
            QtWidgets.QPushButton, "saveButton"
        )

        save_button.clicked.connect(self.hal.save_button)
        connect_button.clicked.connect(self.hal.connect_button)
        calibrate_button.clicked.connect(self.hal.calibrate)
        status_button.clicked.connect(self.hal.status_button)

        return {"Sutter": self.hal.settingsWidget}

    @hookimpl
    def open(self, **kwargs) -> tuple[str, bool]:
        """Open the device.

        Returns:
            bool: True if open
        """
        if self.hal.open():
            return ("Sutter", True)
        return ("Sutter", False)

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
    def mm_move(self, x, y, z):
        """Micromanipulator move.

        Args:
            *args: x, y, z
        """
        if self.hal.move(x, y, z):
            return True
        return False

    @hookimpl
    def mm_stop(self):
        """Micromanipulator stop."""
        self.hal.stop()

    @hookimpl(optionalhook=True)
    def mm_lower(self, z_change):

        (x, y, z) = self.hal.get_current_position()
        if z + z_change > self.hal._maximum_m or z + z_change < self.hal._minimum_ms:
            return False

        if self.hal.slow_move_to(x, y, z + z_change, speed=1):
            return True
        return False
