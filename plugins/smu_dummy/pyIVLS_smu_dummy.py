import pluggy
from dummy_gui import Keithley2612BGUI
import os
import configparser


class pyIVLS_smu_dummy_plugin:
    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
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
        self.metadata = {"name": self.name, "type": self.type, "function": self.function, "version": self.version, "dependencies": self.dependencies}

        self.smu = Keithley2612BGUI()

    @hookimpl
    def get_setup_interface(self, plugin_data) -> dict:
        """returns a widget for a tab in setup, and probably data for the setup structure

        :plugin_type: as all the plugins will be rolled in one loop, but plugins will be of different types, not all of them should return smth.
        This argument will allow the specific implementation of the hook to identify if any response is needed or not.
        :return: dict containing widget and setup structure
        """
        self.smu._initGUI(plugin_data[self.name]["settings"])
        return {self.name: self.smu.settingsWidget}

    @hookimpl
    def get_functions(self, args=None):
        """returns a dict of publicly accessible functions.

        :return: dict of functions
        """

        if args is None or args.get("function") == self.function:
            return {self.name: self.smu._get_public_methods()}

    @hookimpl
    def get_plugin_settings(self, args=None):
        """See pyIVLS_hookspec.py for details."""
        if args is None or args.get("function") == self.metadata["function"]:
            status, settings = self.smu.parse_settings_widget()
            return (self.metadata["name"], status, settings)

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
            return [self.smu, self.metadata]
