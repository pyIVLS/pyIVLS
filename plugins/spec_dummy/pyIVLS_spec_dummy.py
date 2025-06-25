#!/usr/bin/python3.8
import pluggy
from dummy_spectro import dummy_spectro_GUI
import configparser
import os


class pyIVLS_spec_dummy_plugin:
    """Thorlabs ccs plugin for pyIVLS"""

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

        self.plugin_name = config.get("plugin", "name")
        self.type = config.get(
            "plugin",
            "type",
        )
        self.plugin_function = config.get("plugin", "function", fallback="")
        self._class = config.get("plugin", "class", fallback="")
        self.dependencies = config.get("plugin", "dependencies", fallback="").split(",")
        self.version = config.get("plugin", "version", fallback="")
        self.metadata = {"name": self.plugin_name, "type": self.type, "function": self.plugin_function, "version": self.version, "dependencies": self.dependencies}

        # create the driver
        self.spectrometerGUI = dummy_spectro_GUI()

    @hookimpl
    def get_setup_interface(self, plugin_data) -> dict:
        """Returns GUI

        Returns:
            dict: name, widget
        """
        self.spectrometerGUI._initGUI(plugin_data[self.plugin_name]["settings"])
        return {self.plugin_name: self.spectrometerGUI.settingsWidget}

    @hookimpl
    def get_MDI_interface(self, args=None) -> dict:
        """Returns MDI window for camera preview

        Returns:
            dict: name, widget
        """
        return {self.plugin_name: self.spectrometerGUI.previewWidget}

    @hookimpl
    def get_functions(self, args=None):
        """Returns a dictionary of publicly accessible functions.

        Args:
            args (dict): function

        Returns:
            dict: functions
        """
        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.spectrometerGUI._get_public_methods()}

    @hookimpl
    def get_log(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.spectrometerGUI._getLogSignal()}

    @hookimpl
    def get_info(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.spectrometerGUI._getInfoSignal()}

    @hookimpl
    def get_closeLock(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.spectrometerGUI._getCloseLockSignal()}

    @hookimpl
    def get_plugin_settings(self, args=None):
        """Reads the current settings from the settingswidget, returns a dict. Returns (name, status, settings_dict)"""
        if args is None or args.get("function") == self.plugin_function:
            status, settings = self.spectrometerGUI.get_current_gui_settings()
            return (self.plugin_name, status, settings)
