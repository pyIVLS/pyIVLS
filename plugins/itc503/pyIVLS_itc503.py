#!/usr/bin/python3.8

"""
This is a itc503 plugin for pyIVLS. The plugin is based on peltierController for pyIVLS

This file only implements the hooks for pyIVLS.
The proper implementation is in itc503 directory.
Note: The main reason to put implementation in a different class is to allow to reuse it in other applications.

The itc503 contains
- itc503_settingsWidget.ui a Qt widget implementation
- itc503_MDIWidget.ui - a MDI window for displaying time dependecies of temperature
- itc503GUI.py - code that interracts with Qt GUI elements from widgets
        main functionality:
                start temperature visualization
                set temperature
                set power
- itc503.py - a set of functions that may be used outside of GUI
"""

import pluggy

from itc503GUI import itc503GUI


class pyIVLS_itc503_plugin:
    """Hooks for itc503 plugin

    get_log and get_info should be implemented, as the plugin may start manual temperature monitor or set tempereature
    """

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.plugin_name = "itc503"
        self.plugin_function = "temperature"  # e.g. smu, camera, micromanipulator, etc.
        self.pluginClass = itc503GUI()
        super().__init__()

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

    @hookimpl
    def get_closeLock(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.pluginClass._getCloseLockSignal()}

    @hookimpl
    def get_plugin_settings(self, args=None):
        """See pyIVLS_hookspec.py for details."""
        if args is None or args.get("function") == self.plugin_function:
            status, settings = self.pluginClass._get_current_gui_values()
            return (self.plugin_name, status, settings)
