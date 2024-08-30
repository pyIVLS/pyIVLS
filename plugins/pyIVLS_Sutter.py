#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets

from plugins.Sutter.Sutter import Mpc325
from plugins.plugin import Plugin


class pyIVLS_Sutter_plugin(Plugin):
    """Hooks for Sutter micromanipulator plugin"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.hal = Mpc325()
        super().__init__()

    @hookimpl
    def get_setup_interface(self, pm, plugin_data) -> dict:
        """Get the setup interface for the Sutter micromanipulator plugin."""
        self.setup(pm, plugin_data)

        return {self.plugin_name: self._connect_buttons(self.hal.settingsWidget)}

    @hookimpl
    def get_functions(self, args):
        """Returns a dictionary of publicly accessible functions."""
        if args.get("function") == self.plugin_info["function"]:
            return self.get_public_methods()

    def _connect_buttons(self, settingsWidget):
        calibrate_button = settingsWidget.findChild(
            QtWidgets.QPushButton, "calibrateButton"
        )

        connect_button = settingsWidget.findChild(
            QtWidgets.QPushButton, "connectButton"
        )

        status_button = settingsWidget.findChild(QtWidgets.QPushButton, "statusButton")
        save_button = settingsWidget.findChild(QtWidgets.QPushButton, "saveButton")

        save_button.clicked.connect(self.hal.save_button)
        connect_button.clicked.connect(self.hal.connect_button)
        calibrate_button.clicked.connect(self.hal.calibrate)
        status_button.clicked.connect(self.hal.status_button)
        return settingsWidget

    def open(self) -> tuple:
        """Open the device.

        Returns:
            tuple: name, success
        """
        if self.hal.open():
            return (self.plugin_name, True)
        return (self.plugin_name, False)

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
        """Moves the micromanipulator in the z axis. If the move is out of bounds, it will return False.

        Args:
            z_change (float): change in z axis in micron

        Returns:
            bool: Moved or not
        """

        (x, y, z) = self.hal.get_current_position()
        if z + z_change > self.hal._MAXIMUM_M or z + z_change < self.hal._MINIMUM_MS:
            return False
        else:
            self.hal.slow_move_to(x, y, z + z_change, speed=0)
            return True
