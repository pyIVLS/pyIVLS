#!/usr/bin/python3.8
import pluggy
from plugins.Sutter.sutterGUI import SutterGUI


class pyIVLS_Sutter_plugin:
    """Hooks for Sutter micromanipulator plugin"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.function = "micromanipulator"
        self.name = "Sutter"
        self.gui = SutterGUI(self.name, self.function)

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
            return {self.name: self.gui._get_log_signal()}

    @hookimpl
    def get_info(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.function:
            return {self.name: self.gui._get_info_signal()}

    @hookimpl
    def get_closeLock(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.function:
            return {self.name: self.gui._get_close_lock_signal()}
