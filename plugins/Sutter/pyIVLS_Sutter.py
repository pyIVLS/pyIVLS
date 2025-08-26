#!/usr/bin/python3.8
import pluggy
from sutterGUI import SutterGUI


class pyIVLS_Sutter_plugin:
    """Hooks for Sutter micromanipulator plugin"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.function = "micromanipulator"
        self.name = "Sutter"
        self.gui = SutterGUI(self.name, self.function)
        self.metadata = {
            "name": self.name,
            "function": self.function,
        }

    @hookimpl
    def get_setup_interface(self, plugin_data) -> dict:
        """Get the setup interface for the Sutter micromanipulator plugin."""
        settings = plugin_data.get(self.name, {}).get("settings", {})
        widget = self.gui.setup(settings)
        return {self.name: widget}

    @hookimpl
    def get_functions(self, args=None):
        """Returns a dictionary of publicly accessible functions."""
        if args is None or args.get("function") == self.function:
            return {self.name: self.gui._get_public_methods()}

    @hookimpl
    def get_log(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.function:
            return {self.name: self.gui.logger.logger_signal}

    @hookimpl
    def get_info(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.function:
            return {self.name: self.gui.logger.info_popup_signal}

    @hookimpl
    def get_closeLock(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.function:
            return {self.name: self.gui.cl.closeLock}

    @hookimpl
    def get_plugin_settings(self, args=None):
        """Reads the current settings from the settingswidget, returns a dict. Returns (name, status, settings_dict)"""
        if args is None or args.get("function") == self.function:
            status, settings = self.gui.parse_settings_widget()
            return (self.name, status, settings)
