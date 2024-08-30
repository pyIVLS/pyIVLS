#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets


from plugins.TLCCS.TLCCS import CCSDRV
from plugins.plugin import Plugin


class pyIVLS_TLCCS_plugin(Plugin):
    """Thorlabs ccs plugin for pyIVLS"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        # crete the driver
        self.drv = CCSDRV()
        super().__init__()

    @hookimpl
    def get_setup_interface(self, pm, plugin_data) -> dict:
        """Template get_setup_interface hook implementation

        Args:
            pm (pluggy.PluginManager): The plugin manager, only used if needed.

        Returns:
            dict: name : widget
        """
        self.setup(pm, plugin_data)

        # Find buttons from the settings widget
        button = self.drv.settingsWidget.findChild(QtWidgets.QPushButton, "pushButton")

        # Connect widget buttons to functions
        button.clicked.connect(self.drv.read_integration_time_GUI)

        return {self.plugin_name: self.drv.settingsWidget}

    @hookimpl
    def get_functions(self, args):
        if args.get("function") == self.plugin_info["function"]:
            return self.get_public_methods()

    def run_scan(self):
        """Currently open needs to be called separatedly

        Returns:
            _type_: _description_
        """
        self.drv.start_scan()
        return self.drv.get_scan_data()

    def open(self) -> tuple:
        """Open the connection to the device"""
        if self.drv.open():
            return (self.plugin_name, True)
        return (self.plugin_name, False)
