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

        self.metadata = {
            "name": self.name,
            "type": self.type,
            "function": self.function,
            "address": self.address,
        }

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
    def get_MDI_interface(self, args=None):
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

        return {self.name: self.affine_control._fetch_dependency_functions(function_dict)}

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
        if args is None or args.get("function") == self.metadata["function"]:
            return [self.affine_control, self.metadata]

    @hookimpl
    def get_plugin_settings(self, args=None):
        """See pyIVLS_hookspec.py for details."""
        if args is None or args.get("function") == self.metadata["function"]:
            status, settings = self.affine_control.parse_settings_widget()
            return (self.metadata["name"], status, settings)
