#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets


from plugins.template_plugin.template import Template


class pyIVLS_Template_plugin:
    """template hookspecs"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.template = Template()

    @hookimpl
    def get_setup_interface(self, pm) -> dict:
        """Template get_setup_interface hook implementation

        Args:
            pm (pluggy.PluginManager): The plugin manager

        Returns:
            dict: name : widget
        """

        # Find buttons from the settings widget
        find_button = self.template.settingsWidget.findChild(
            QtWidgets.QPushButton, "findButton"
        )
        save_button = self.template.settingsWidget.findChild(
            QtWidgets.QPushButton, "saveButton"
        )

        # Connect widget buttons to functions
        find_button.clicked.connect(self.template.find_button)
        save_button.clicked.connect(self.template.save_button)

        # Set the pm if it is needed
        if self.template.pm is None:
            self.template.pm = pm

        # Replace name here with the name of the plugin
        return {"Template": self.template.settingsWidget}

    # The rest of the hooks go here
