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
    def get_functions(self, args):
        """Get functions for the Sutter micromanipulator plugin.

        Returns:
            dict: functions
        """
        if args.get("function") == "micromanipulator":
            return {
                "mm_open": self.hal.open,
                "mm_change_active_device": self.hal.change_active_device,
                "mm_move": self.hal.move,
                "mm_stop": self.hal.stop,
                "mm_lower": self.mm_lower,
            }

    # DEPRECATED - REMOVE

    def open(self) -> tuple[str, bool]:
        """Open the device.

        Returns:
            bool: True if open
        """
        if self.hal.open():
            return ("Sutter", True)
        return ("Sutter", False)

    def mm_change_active_device(self, dev_num):
        """Micromanipulator active device change.

        Args:
            *args: device number
        """
        if self.hal.change_active_device(dev_num):
            return True
        return False

    def mm_move(self, x, y, z):
        """Micromanipulator move.

        Args:
            *args: x, y, z
        """
        if self.hal.move(x, y, z):
            return True
        return False

    def mm_stop(self):
        """Micromanipulator stop."""
        self.hal.stop()

    def mm_lower(self, z_change) -> bool:

        (x, y, z) = self.hal.get_current_position()
        # FIXME: replace the placeholder maximum
        if z + z_change > 1000 or z + z_change < self.hal._minimum_ms:
            return False
        else:
            self.hal.slow_move_to(x, y, z + z_change, speed=0)
            return True
