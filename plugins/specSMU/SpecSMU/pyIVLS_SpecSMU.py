#!/usr/bin/python3.8

"""
This is a plugin for using spectrometer while powering a device under the test with SMU.
In future this plugin planned to be extended to synchronius operation of SMU with spectrometer.

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

import pluggy

from specSMU_GUI import specSMU_GUI


class pyIVLS_SpecSMU_plugin:
    """Hooks for specSMU plugin"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.plugin_name = "SpecSMU"
        self.plugin_function = "complex"  # e.g. smu, camera, micromanipulator, etc.
        self.plugin_dependencies = ["smu", "spectrometer"]
        self.pluginClass = specSMU_GUI()
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
    def get_functions(self, args=None):
        """Returns a dictionary of publicly accessible functions. This function is called from pyIVLS_container

        Args:
            args (dict): function

        Returns:
            dict: functions
        """
        if args is None or args.get("function") == plugin_function:
            return {self.plugin_name: self.pluginClass._get_public_methods()}

    @hookimpl
    def set_function(self, function_dict):
        """provides a list of available public functions from other plugins as a nested list

        Returns:
            dict: name, widget
        """
        return self.pluginClass._getPublicFunctions({function_dict_key: function_dict[function_dict_key] for function_dict_key in self.plugin_dependencies if function_dict_key in function_dict})
