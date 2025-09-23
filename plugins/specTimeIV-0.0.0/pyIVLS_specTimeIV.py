#!/usr/bin/python3.8

"""
This is a template for a plugin in pyIVLS

This file only implements the hooks for pyIVLS.
The proper implementation should be placed in a directory with the same name (for this template it is "pluginTemplate") next to this file.
The main reason to put implementation in a different calss is to allow to reuse it in other applications.

The standard implementation may (but not must) include
- GUI a Qt widget implementation
- GUI functionality (e.g. pluginTemplateGUI.py) - code that interracts with Qt GUI elements from widgets
- plugin core implementation - a set of functions that may be used outside of GUI
"""

import pluggy
from spectimeIVGUI import specTimeIVGUI
import os
import configparser


class pyIVLS_specTimeIV_plugin:
    """Hooks for pluginTemplate plugin
    Not all hooks must be implemented
    If hook is not needed it should be deleted
    """

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        # iterate current directory to find the .ini file
        path = os.path.dirname(__file__)
        for file in os.listdir(path):
            if file.endswith(".ini"):
                path = os.path.join(path, file)
                break
        config = configparser.ConfigParser()
        config.read(path)

        self.name = config.get("plugin", "name")
        self.type = config.get("plugin", "type")
        self.function = config.get("plugin", "function", fallback="")
        self._class = config.get("plugin", "class", fallback="")
        self.dependencies = config.get("plugin", "dependencies", fallback="").split(",")
        self.version = config.get("plugin", "version", fallback="")
        self.metadata = {"name": self.name, "type": self.type, "function": self.function, "version": self.version, "dependencies": self.dependencies}

        self.pluginClass = specTimeIVGUI()

    @hookimpl
    def get_setup_interface(self, plugin_data) -> dict:
        """Returns GUI plugin for the docking area (settings/buttons). This function is called from pyIVLS_container

        Returns:
            dict: name, widget
        """
        ##IRtodo#### add check if (error) show message and return error
        self.pluginClass._initGUI(plugin_data[self.name]["settings"])
        return {self.name: self.pluginClass.settingsWidget}

    @hookimpl
    def get_MDI_interface(self, args=None) -> dict:
        """Returns MDI window (visualisation). This function is called from pyIVLS_container

        Returns:
            dict: name, widget
        """
        return {self.name: self.pluginClass.MDIWidget}

    @hookimpl
    def get_log(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.function:
            return {self.name: self.pluginClass.logger.logger_signal}

    @hookimpl
    def get_info(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.function:
            return {self.name: self.pluginClass.logger.info_popup_signal}

    @hookimpl
    def set_function(self, function_dict):
        """provides a list of available public functions from other plugins as a nested list

        Returns:
            dict: name, widget
        """
        pruned = {function_dict_key: function_dict[function_dict_key] for function_dict_key in self.dependencies if function_dict_key in function_dict}
        self.pluginClass.dependency_manager.function_dict = pruned
        return self.pluginClass.dependency_manager.function_dict

    @hookimpl
    def get_plugin_settings(self, args=None):
        """Reads the current settings from the settingswidget, returns a dict. Returns (name, status, settings_dict)"""
        if args is None or args.get("function") == self.function:
            status, settings = self.pluginClass.parse_settings_widget()
            return (self.name, status, settings)

    @hookimpl
    def get_functions(self, args=None):
        """Returns a dictionary of publicly accessible functions.

        Args:
            args (dict): function

        Returns:
            dict: functions
        """
        if args is None or args.get("function") == self.metadata["function"]:
            return {self.metadata["name"]: self.pluginClass._get_public_methods()}
