#!/usr/bin/python3.8

"""
This is a plugin for using spectrometer while powering a device under the test with SMU.
In future this plugin planned to be extended to synchronius operation of SMU.

This file only implements the hooks for pyIVLS.
The proper implementation may be found in SpecSMU directory (SpecSMU_GUI.py).
The main reason to put implementation in a different calss is to allow to reuse it in other applications.

This is mainly a standard implementation that includes
- GUI a Qt widget implementation
- GUI functionality - code that interracts with Qt GUI elements from widgets
- plugin core implementation - a set of functions that may be used outside of GUI

ivarad
25.06.10
"""

import os
import configparser
import pluggy

from specSMU_GUI import specSMU_GUI


class pyIVLS_SpecSMU_plugin:
    """Hooks for SpecSMU plugin (now closely following sweep plugin pattern)"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        # Read plugin metadata from .ini file if available
        path = os.path.dirname(__file__)
        for file in os.listdir(path):
            if file.endswith(".ini"):
                path = os.path.join(path, file)
                break
        config = configparser.ConfigParser()
        config.read(path)
        self.name = config.get("plugin", "name", fallback="SpecSMU")
        self.type = config.get("plugin", "type", fallback="complex")
        self.function = config.get("plugin", "function", fallback="complex")
        self._class = config.get("plugin", "class", fallback="")
        self.dependencies = config.get("plugin", "dependencies", fallback="smu,spectrometer").split(",")
        self.version = config.get("plugin", "version", fallback="")
        self.metadata = {"name": self.name, "type": self.type, "function": self.function, "version": self.version, "dependencies": self.dependencies}
        self.specsmu = specSMU_GUI()
        # Pass plugin metadata (including defaults) to the GUI for use in raw getter
        self.specsmu.plugin_metadata = {
            "default_smu": config.get("plugin", "default_smu", fallback=None),
            "default_spectrometer": config.get("plugin", "default_spectrometer", fallback=None),
        }

    @hookimpl
    def get_setup_interface(self, plugin_data) -> dict:
        """Returns a widget for a tab in setup, and probably data for the setup structure"""
        if hasattr(self.specsmu, "set_dependencies"):
            self.specsmu.set_dependencies(self.dependencies)
        if "function_dict" in plugin_data[self.name]:
            self.specsmu.function_dict = plugin_data[self.name]["function_dict"]
        self.specsmu._initGUI(plugin_data[self.name]["settings"])
        return {self.name: self.specsmu}

    @hookimpl
    def get_functions(self, args=None):
        """Returns a dictionary of publicly accessible functions. This function is called from pyIVLS_container"""
        if args is None or args.get("function") == self.function:
            return {self.name: self.specsmu._get_public_methods()}

    @hookimpl
    def set_function(self, function_dict):
        """Provides a list of available public functions from other plugins as a nested list"""
        pruned = {k: function_dict[k] for k in self.dependencies if k in function_dict}
        self.specsmu.function_dict = pruned
        if hasattr(self.specsmu, "set_dependencies"):
            self.specsmu.set_dependencies(self.dependencies)
        return self.specsmu.function_dict

    @hookimpl
    def get_plugin_settings(self, args=None):
        """Reads the current settings from the settingswidget, returns a dict. Returns (name, status, settings_dict)"""
        if args is None or args.get("function") == self.function:
            # Use the raw getter for saving settings
            settings = self.specsmu.get_settings_dict_raw()
            # Optionally, you can still parse/validate if needed:
            # status, parsed_settings = self.specsmu.parse_settings_widget()
            # return (self.name, status, parsed_settings)
            return (self.name, 0, settings)

    @hookimpl
    def get_log(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """
        if args is None or args.get("function") == self.function:
            return {self.name: self.specsmu.logger.logger_signal}
