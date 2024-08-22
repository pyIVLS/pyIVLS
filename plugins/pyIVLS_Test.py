#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets

from plugins.Test.Test import Test
from plugins.plugin import Plugin


class pyIVLS_Test_plugin(Plugin):
    """Hooks for the tester plugin"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.test = Test()
        super().__init__()

    @hookimpl
    def get_setup_interface(self, pm, plugin_data) -> dict:
        """Sets up the buttons for affine conversion plugin

        Returns:
            dict: name, widget
        """
        self.setup(pm, plugin_data)
        self.test.runButton = self.test.settingsWidget.findChild(
            QtWidgets.QPushButton, "runButton"
        )

        self.test.statusLabel = self.test.settingsWidget.findChild(
            QtWidgets.QLabel, "statusLabel"
        )

        # Connect widget buttons to functions
        self.test.runButton.clicked.connect(self.test.run_button)

        self.test.statusLabel.setText("Test function not run")

        # FIXME: This is a bit stupidos
        self.test.pm = self.pm
        return {self.plugin_name: self.test.settingsWidget}

    @hookimpl
    def get_functions(self, args):
        if args.get("function") == self.plugin_info["function"]:
            return self.get_public_methods()
