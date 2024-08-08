#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets

from plugins.Test.test import Test


class pyIVLS_Test_plugin:
    """Hooks for the tester plugin"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.test = Test()

    @hookimpl
    def get_setup_interface(self, pm) -> dict:
        """Sets up the buttons for affine conversion plugin

        Returns:
            dict: name, widget
        """

        self.test.runButton = self.test.settingsWidget.findChild(
            QtWidgets.QPushButton, "runButton"
        )

        self.test.statusLabel = self.test.settingsWidget.findChild(
            QtWidgets.QLabel, "statusLabel"
        )

        # Connect widget buttons to functions
        self.test.runButton.clicked.connect(self.test.run_button)

        self.test.statusLabel.setText("Test function not run")

        return {"Test": self.test.settingsWidget}
