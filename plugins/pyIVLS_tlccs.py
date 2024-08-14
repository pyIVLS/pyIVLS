#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets


from plugins.Thorspec.tlccs import CCSDRV


class pyIVLS_tlccs_plugin:
    """Thorlabs ccs plugin for pyIVLS"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        # crete the driver
        self.drv = CCSDRV()

    @hookimpl
    def get_setup_interface(self, pm) -> dict:
        """Template get_setup_interface hook implementation

        Args:
            pm (pluggy.PluginManager): The plugin manager, only used if needed.

        Returns:
            dict: name : widget
        """

        # Find buttons from the settings widget
        button = self.drv.settingsWidget.findChild(QtWidgets.QPushButton, "pushButton")

        # Connect widget buttons to functions
        button.clicked.connect(self.drv.read_integration_time_GUI)

        # Replace name here with the name of the plugin
        return {"tlccs": self.drv.settingsWidget}

    # The rest of the hooks go here
