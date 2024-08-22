#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets


from plugins.ConDetect.ConDetect import ConDetect
from plugins.plugin import Plugin


class pyIVLS_ConDetect_plugin(Plugin):

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.detector = ConDetect()

    @hookimpl
    def get_setup_interface(self, pm):
        """Template get_setup_interface hook implementation

        Args:
            pm (pluggy.PluginManager): The plugin manager

        Returns:
            dict: name : widget
        """

        # Set the pm
        if self.detector.pm is None:
            self.detector.pm = pm

        # Find buttons from the settings widget
        save_button = self.detector.settingsWidget.findChild(
            QtWidgets.QPushButton, "saveButton"
        )

        # Connect widget buttons to functions
        save_button.clicked.connect(self.detector.debug)

        return {"ConDetect": self.detector.settingsWidget}

    # The rest of the hooks go here
