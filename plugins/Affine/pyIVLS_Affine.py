#!/usr/bin/python3.8
import pluggy

from AffineGUI import AffineGUI


class pyIVLS_Affine_plugin:
    """Hooks for affine conversion plugin
    This class acts as a bridge between plugins"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        """
        Initialize the plugin and set up properties.
        """
        self.affine_control = AffineGUI()
        self.name = "Affine"
        self.function = "positioning"
        self.type = "script"  # unnecessary
        self.address = "Affine"  # unnecessary

    @hookimpl
    def get_setup_interface(self, plugin_data: dict) -> dict:
        """Returns GUI
        Args:
            plugin_data (dict): plugin data read from .ini to read initial settings.

        Returns:
            dict: name, widget
        """
        settings = plugin_data[self.name].get("settings", {})
        self.affine_control._initGUI(settings)
        return {self.name: self.affine_control.settingsWidget}

    @hookimpl
    def get_MDI_interface(self, args=None) -> dict:
        """Returns MDI window

        Returns:
            dict: name, widget
        """
        if args is None or args.get("function") == self.function:
            return {self.name: self.affine_control.MDIWidget}

    @hookimpl
    def get_functions(self, args=None):
        """Returns a dictionary of publicly accessible functions.

        Args:
            args (dict): function

        Returns:
            dict: functions
        """
        if args is None or args.get("function") == self.function:
            return {self.name: self.affine_control._get_public_methods(self.function)}

    @hookimpl
    def set_function(self, function_dict):
        """Sets the functions for the plugin.

        Args:
            args (dict): function

        Returns:
            dict: functions
        """

        return {
            self.name: self.affine_control._fetch_dependency_functions(function_dict)
        }

    @hookimpl
    def get_log(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """
        if args is None or args.get("function") == self.function:
            return {self.name: self.affine_control._getLogSignal()}

    @hookimpl
    def get_info(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """
        if args is None or args.get("function") == self.function:
            return {self.name: self.affine_control._getInfoSignal()}

    @hookimpl
    def get_closeLock(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """
        if args is None or args.get("function") == self.function:
            return {self.name: self.affine_control._getCloseLockSignal()}
