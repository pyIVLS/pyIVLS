#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets

from runSweepGUI import runSweepGUI

class pyIVLS_runSweep_plugin():
    """Hooks for the tester plugin"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        ##IRtothink#### there should be some kind of configuration file for installing the plugins. This config file may be stored in the plugin folder, and the plugin data may be read from there
        self.plugin_name="runSweep"
        self.plugin_function="sequence"
        self.plugin_dependencies=["ivsweep"]
        self.sweep = runSweepGUI()
        super().__init__()

    @hookimpl
    def get_setup_interface(self, plugin_data) -> dict:
        """returns a widget for a tab in setup, and probably data for the setup structure

        :plugin_type: as all the plugins will be rolled in one loop, but plugins will be of different types, not all of them should return smth.
        This argument will allow the specific implementation of the hook to identify if any response is needed or not.
        :return: dict containing widget and setup structure
        """
        self.sweep._initGUI(plugin_data[self.plugin_name]["settings"])
        return {self.plugin_name: self.sweep.settingsWidget}

    @hookimpl
    def get_log(self, args = None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """
        
        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.sweep._getLogSignal()}

    @hookimpl
    def get_info(self, args = None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """
        
        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.sweep._getInfoSignal()}
        
    @hookimpl
    def set_function(self, function_dict):
        """ provides a list of available public functions from other plugins as a nested list

        Returns:
            dict: name, widget
        """
        return self.sweep._getPublicFunctions({function_dict_key: function_dict[function_dict_key] for function_dict_key in self.plugin_dependencies if function_dict_key in function_dict})
