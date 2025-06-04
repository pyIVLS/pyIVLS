#!/usr/bin/python3.8


import pluggy
from touchDetectGui import touchDetectGUI

class pyIVLS_touchDetect_plugin:


    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.name = "touchDetect"
        self.type = "script"
        self.function = "contactingMove"
        self._class = "loop"
        self.dependencies = ["smu", "micromanipulator", "contacting"]
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

        if args is None or args.get("function") == self.plugin_function:
            return {self.name : self.pluginClass._getLogSignal()}

    @hookimpl
    def get_info(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.name : self.pluginClass._getInfoSignal()}

    @hookimpl
    def get_closeLock(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
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
