#!/usr/bin/python3.8
import pluggy
from plugins.VenusUSB2.cameraHAL import VenusUSB2

# For parsing the settings widget
from PyQt6 import QtWidgets


class pyIVLS_VenusUSB2_plugin:
    hookimpl = pluggy.HookimplMarker("pyIVLS")

    @hookimpl
    def get_setup_interface(self) -> dict:
        """Sets up camera, preview, and save buttons for VenusUSB2 camera plugin

        Returns:
            dict: name, widget
        """

        self.camera = VenusUSB2()
        print("I am getting info for the camera plugin")

        preview_button = self.camera.settingsWidget.findChild(
            QtWidgets.QPushButton, "cameraPreview"
        )
        save_button = self.camera.settingsWidget.findChild(
            QtWidgets.QPushButton, "cameraSave"
        )

        preview_button.clicked.connect(self.camera.preview_button)
        save_button.clicked.connect(self.camera.save_button)

        return {"VenusUSB2": self.camera.settingsWidget}
