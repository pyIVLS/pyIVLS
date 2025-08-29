#!/usr/bin/python3.8

"""
This is a peltierController plugin for pyIVLS

This file only implements the hooks for pyIVLS.
The proper implementation is in peltierController directory.
Note: The main reason to put implementation in a different calss is to allow to reuse it in other applications.

The peltierController contains
- peltierController_settingsWidget.ui a Qt widget implementation
- peltierController_MDIWidget.ui - a MDI window for displaying timedependecies of temperature
- peltierControllerGUI.py - code that interracts with Qt GUI elements from widgets
        main functionality:
                start temperature visualization
                set temperature
                set power
- peltierController.py - a set of functions that may be used outside of GUI
"""

import pluggy

from peltierControllerGUI import peltierControllerGUI


class pyIVLS_peltierController_plugin:
    """Hooks for peltierController plugin

    get_log and get_info should be implemented, as the plugin may start manual temperature monitor or set tempereature/power
    """

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.plugin_name = "peltierController"
        self.plugin_function = "temperature"  # e.g. smu, camera, micromanipulator, etc.
        self.pluginClass = peltierControllerGUI()

    @hookimpl
    def get_setup_interface(self, plugin_data) -> dict:
        """Returns GUI plugin for the docking area (settings/buttons). This function is called from pyIVLS_container

        Returns:
            dict: name, widget
        """
        ##IRtodo#### add check if (error) show message and return error
        self.pluginClass._initGUI(plugin_data[self.plugin_name]["settings"])
        return {self.plugin_name: self.pluginClass.settingsWidget}

    @hookimpl
    def get_MDI_interface(self, args=None) -> dict:
        """Returns MDI window (visualisation). This function is called from pyIVLS_container

        Returns:
            dict: name, widget
        """
        return {self.plugin_name: self.pluginClass.MDIWidget}

    @hookimpl
    def get_functions(self, args=None):
        """Returns a dictionary of publicly accessible functions. This function is called from pyIVLS_container

        Args:
            args (dict): function

        Returns:
            dict: functions
        """
        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.pluginClass._get_public_methods()}

    @hookimpl
    def get_log(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.pluginClass._getLogSignal()}

    @hookimpl
    def get_info(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.pluginClass._getInfoSignal()}
