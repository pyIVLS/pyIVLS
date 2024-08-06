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
