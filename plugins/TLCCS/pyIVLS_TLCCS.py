#!/usr/bin/python3.8
import pluggy
from TLCCSGUI import TLCCS_GUI
import os
import configparser



class pyIVLS_TLCCS_plugin:
    """Thorlabs ccs plugin for pyIVLS"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
    #    self.plugin_name = "TLCCS"
    #    self.plugin_function = "spectrometer"
        # iterate current directory to find the .ini file
        path = os.path.dirname(__file__)
        for file in os.listdir(path):
            if file.endswith(".ini"):
                path = os.path.join(path, file)
                break
        config = configparser.ConfigParser()
        config.read(path)

        self.name = config.get("plugin", "name")
        self.type = config.get(
            "plugin",
            "type",
        )
        self.function = config.get("plugin", "function", fallback="")
        self._class = config.get("plugin", "class", fallback="")
        self.dependencies = config.get("plugin", "dependencies", fallback="").split(",")
        self.version = config.get("plugin", "version", fallback="")
        self.metadata = {
            "name": self.name,
            "type": self.type,
            "function": self.function,
            "version": self.version,
            "dependencies": self.dependencies,
        }
        # create the driver
        self.spectrometerGUI = TLCCS_GUI()

    @hookimpl
    def get_setup_interface(self, plugin_data) -> dict:
        """Returns GUI

        Returns:
            dict: name, widget
        """
        self.spectrometerGUI._initGUI(plugin_data[self.metadata["name"]]["settings"])
        return {self.metadata["name"]: self.spectrometerGUI.settingsWidget}

    @hookimpl
    def get_MDI_interface(self, args=None) -> dict:
        """Returns MDI window for camera preview

        Returns:
            dict: name, widget
        """
        return {self.metadata["name"]: self.spectrometerGUI.previewWidget}

    @hookimpl
    def get_functions(self, args=None):
        """Returns a dictionary of publicly accessible functions.

        Args:
            args (dict): function

        Returns:
            dict: functions
        """
        if args is None or args.get("function") == self.metadata["function"]:
            return {self.metadata["name"]: self.spectrometerGUI._get_public_methods()}

    @hookimpl
    def get_log(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.spectrometerGUI.logger.logger_signal}

    @hookimpl
    def get_info(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.spectrometerGUI.logger.info_popup_signal}

    @hookimpl
    def get_closeLock(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.metadata["function"]:
            return {self.metadata["name"]: self.spectrometerGUI._getCloseLockSignal()}

    @hookimpl
    def get_plugin_settings(self, args=None):
        """Reads the current settings from the settingswidget, returns a dict. Returns (name, status, settings_dict)"""
        if args is None or args.get("function") == self.metadata["function"]:
            status, settings = self.spectrometerGUI.parse_settings_widget()
            return (self.metadata["name"], status, settings)

