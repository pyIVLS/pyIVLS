import pluggy
from Keithley2612BGUI import Keithley2612BGUI
import os
import configparser

class pyIVLS_Keithley2612B_plugin:
    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        """
        Initialize the plugin and set up properties.
        """
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

        self.smu = Keithley2612BGUI()

    @hookimpl
    def get_setup_interface(self, plugin_data) -> dict:
        """returns a widget for a tab in setup, and probably data for the setup structure

        :plugin_type: as all the plugins will be rolled in one loop, but plugins will be of different types, not all of them should return smth.
        This argument will allow the specific implementation of the hook to identify if any response is needed or not.
        :return: dict containing widget and setup structure
        """
        self.smu._initGUI(plugin_data[self.name]["settings"])
        return {self.metadata["name"]: self.smu.settingsWidget}

    @hookimpl
    def get_functions(self, args=None):
        """returns a dict of publicly accessible functions.

        :return: dict of functions
        """

        if args is None or args.get("function") == self.metadata["function"]:
            return {self.metadata["name"]: self.smu._get_public_methods()}

    @hookimpl
    def get_plugin_settings(self, args=None):
        """See pyIVLS_hookspec.py for details."""
        if args is None or args.get("function") == self.metadata["function"]:
            status, settings = self.smu.parse_settings_widget()
            return (self.metadata["name"], status, settings)
        
    @hookimpl
    def get_log(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.metadata["function"]:
            return {self.metadata["name"]: self.smu._getLogSignal()}

    @hookimpl
    def get_info(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.metadata["function"]:
            return {self.metadata["name"]: self.smu._getInfoSignal()}