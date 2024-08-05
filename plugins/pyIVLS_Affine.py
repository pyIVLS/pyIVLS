#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets

from plugins.CoordConverter.affine import Affine


class pyIVLS_Affine_plugin:
    """Hooks for VenusUSB2 camera plugin"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.affine = Affine()

    @hookimpl
    def get_setup_interface(self) -> dict:
        """Sets up camera, preview, and save buttons for VenusUSB2 camera plugin

        Returns:
            dict: name, widget
        """

        mask_button = self.affine.settingsWidget.findChild(
            QtWidgets.QPushButton, "maskButton"
        )

        # Connect widget buttons to functions
        mask_button.clicked.connect(self.affine.mask_button)

        return {"Affine": self.affine.settingsWidget}
