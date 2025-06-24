#!/usr/bin/python3.8


import pluggy
import configparser
from touchDetectGui import touchDetectGUI
import os
class pyIVLS_touchDetect_plugin:


    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):

        # iterate current directory to find the .ini file
        path = os.path.dirname(__file__)
        for file in os.listdir(path):
            if file.endswith(".ini"):
                path = os.path.join(path, file)
                break
        config = configparser.ConfigParser()
        # no need to close resource, since configparser handles it internally
        # https://stackoverflow.com/questions/990867/closing-file-opened-by-configparser
        config.read(path)

        self.name = config.get("plugin", "name")
        self.type = config.get("plugin", "type")
        self.function = config.get("plugin", "function")
        self._class = config.get("plugin", "class")
        self.dependencies = config.get("plugin", "dependencies").split(",")
        self.pluginClass = touchDetectGUI()


    @hookimpl
    def get_setup_interface(self, plugin_data) -> dict:
        """Returns GUI plugin for the docking area (settings/buttons). This function is called from pyIVLS_container
        Args:
            plugin_data (dict): plugin dict from pyIVLS_container. Used for example to get the initial settings.
        Returns:
            dict: name, widget
        """
        settings = plugin_data.get(self.name, {}).get("settings", {})
        return {self.name: self.pluginClass.setup(settings)}


    @hookimpl
    def get_log(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.function:
            return {self.name : self.pluginClass._getLogSignal()}

    @hookimpl
    def get_info(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.function:
            return {self.name : self.pluginClass._getInfoSignal()}

    @hookimpl
    def get_closeLock(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.function:
            pass

    @hookimpl
    def set_plugin(self, plugin_list):
        """gets a list of plugins available, fetches the ones it needs.

        Args:
            plugin_list (list): list of plugins in the form of [plugin1, plugin2, ...]
        """
        plugins_to_fetch = []
        
        for plugin, metadata in plugin_list:
            if metadata.get("function", "") in self.dependencies:
                plugins_to_fetch.append([plugin, metadata])
        
                
        self.pluginClass.dependency = plugins_to_fetch

    @hookimpl
    def get_functions(self, args=None):
        """returns a dict of publicly accessible functions.

        :return: dict containing the functions
        """
        if args is None or args.get("function") == self.function:
            return {self.name: self.pluginClass._get_public_methods()}