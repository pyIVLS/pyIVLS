#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets


from plugins.ConDetect.ConDetect import ConDetect
from plugins.plugin import Plugin


class pyIVLS_ConDetect_plugin(Plugin):

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.detector = ConDetect()
        super().__init__()

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
        save_button.clicked.connect(self.detector.debug)

        return {self.plugin_name: self.detector.settingsWidget}

    # The rest of the hooks go here
    @hookimpl
    def get_functions(self, args):
        """Returns a dictionary of publicly accessible functions."""
        if args.get("function") == self.plugin_info["function"]:
            return self.get_public_methods()
