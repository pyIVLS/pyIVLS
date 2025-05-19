#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets

from plugins.conDetect.conDetect import ConDetect


class pyIVLS_conDetect_plugin:
    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.detector = ConDetect()

    @hookimpl
    def get_setup_interface(self, pm, plugin_data) -> dict:
        """Template get_setup_interface hook implementation

        Args:
            pm (pluggy.PluginManager): The plugin manager

        Returns:
            dict: name : widget
        """

        self.setup(pm, plugin_data)

        # Find buttons from the settings widget
        save_button = self.detector.settingsWidget.findChild(
            QtWidgets.QPushButton, "saveButton"
        )

        # Connect widget buttons to functions
        save_button.clicked.connect(self._debug_button)

        return {self.plugin_name: self.detector.settingsWidget}

    # The rest of the hooks go here
    @hookimpl
    def get_functions(self, args):
        """Returns a dictionary of publicly accessible functions."""
        if args.get("function") == self.plugin_info["function"]:
            return self.get_public_methods()

    def _debug_button(self):
        self.detector.debug(self.pm)
