#!/usr/bin/python3.8


import pluggy
from affineMoveGui import affineMoveGUI


class pyIVLS_affineMove_plugin:
    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.name = "affineMove"
        self.type = "script"
        self.function = "move"
        self._class = "loop"
        self.dependencies = ["positioning", "micromanipulator", "camera"]
        self.plg = affineMoveGUI()

    @hookimpl
    def get_setup_interface(self, plugin_data: dict) -> dict:
        """Returns GUI plugin for the docking area (settings/buttons). This function is called from pyIVLS_container
        Args:
            plugin_data (dict): plugin dict from pyIVLS_container. Used for example to get the initial settings.
        Returns:
            dict: name, widget
        """
        settings = plugin_data[self.name]["settings"]
        return {self.name: self.plg.setup(settings)}

    @hookimpl
    def get_MDI_interface(self, args=None) -> dict:
        """Returns MDI window (visualisation). This function is called from pyIVLS_container

        Returns:
            dict: name, widget
        """
        return {self.name: self.plg.MDIWidget}

    @hookimpl
    def get_functions(self, args=None):
        """returns a dict of publicly accessible functions.

        :return: dict containing the functions
        """
        if args is None or args.get("function") == self.function:
            return {self.name: self.plg._get_public_methods()}

    @hookimpl
    def set_function(self, function_dict):
        """Hook to set methods from other plugins to this plugins function dictionary
        Returns: Missing methods
        """
        # set functions to DependencyManager
        self.plg.dm.set_function_dict(function_dict)
        missing, list = self.plg.dm.validate_dependencies()
        return list

    @hookimpl
    def get_log(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.function:
            return {self.name: self.plg.logger.logger_signal}

    @hookimpl
    def get_info(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.function:
            return {self.name: self.plg.logger.info_popup_signal}

    @hookimpl
    def get_closeLock(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.function:
            return {self.name: self.plg.cl.closeLock}

    @hookimpl
    def get_plugin_settings(self, args=None):
        """Reads the current settings from the settingswidget, returns a dict. Returns (name, status, settings_dict)"""
        if args is None or args.get("function") == self.function:
            status, settings = self.plg.parse_settings_widget()
            return (self.name, status, settings)
