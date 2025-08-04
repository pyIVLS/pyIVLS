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
from pluginTemplateGUI import pluginTemplateGUI
import os
import configparser


class pyIVLS_pluginTemplate_plugin:
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
        self.function = config.get("plugin", "function")
        self._class = config.get("plugin", "class")
        self.dependencies = config.get("plugin", "dependencies", fallback="").split(",")
        self.pluginClass = pluginTemplateGUI()

    @hookimpl
    def get_setup_interface(self, plugin_data) -> dict:
        """Returns GUI plugin for the docking area (settings/buttons). This function is called from pyIVLS_container
        Args:
            plugin_data (dict): plugin dict from pyIVLS_container. Used for example to get the initial settings.
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
    def get_functions(self, args=None):
        """Returns a dictionary of publicly accessible functions. This function is called from pyIVLS_container

        Args:
            args (dict): function

        Returns:
            dict: functions
        """
        if args is None or args.get("function") == self.function:
            return {self.name: self.pluginClass._get_public_methods()}

    @hookimpl
    def set_function(self, function_dict):
        """provides a list of publicly available functions to the plugin as a nested dict
        {'function1' : {'def1': object, 'def2':object},
         'function2' : {'def1': object, 'def2':object},}

        :return: list containing missed plugins or functions in form of [plg1, plg2:func3]
        """
        raise NotImplementedError()

    @hookimpl
    def get_plugin(self, args=None):
        """Returns the plugin as a reference to itself.
        NOTE: when writing implmentations of this, the plugin should contain its own metadata, such as name, type, version, etc.

        Args:
            args (_type_, optional): can be used to specify which plugin is needed based on
            type, function, etc.

        Returns:
            tuple[object, metadata]: reference to the plugin itself along with its properties such as name, type, version, etc.
        """
        raise NotImplementedError()

    @hookimpl
    def set_plugin(self, plugin_list, args=None):
        """gets a list of plugins available, fetches the ones it needs.

        Args:
            plugin_list (list): list of plugins in the form of [plugin1, plugin2, ...]
        """
        raise NotImplementedError()

    @hookimpl
    def get_log(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.function:
            return {self.name: self.camera_control._getLogSignal()}

    @hookimpl
    def get_info(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.function:
            return {self.name: self.pluginClass._getInfoSignal()}

    @hookimpl
    def get_closeLock(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.function:
            return {self.name: self.pluginClass._getCloseLockSignal()}
