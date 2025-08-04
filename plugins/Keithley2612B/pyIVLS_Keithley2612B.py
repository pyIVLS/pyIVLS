import pluggy
from Keithley2612BGUI import Keithley2612BGUI


class pyIVLS_Keithley2612B_plugin:
    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.plugin_name = "Keithley2612B"
        self.plugin_function = "smu"
        self.dependencies = []
        self.type = "device"  # unnecessary
        self.address = "Keithley2612B"  # unnecessary
        self.smu = Keithley2612BGUI()
        self.metadata = {"name": self.plugin_name, "type": self.type, "function": self.plugin_function, "address": self.address, "version": "placeholder", "dependencies": self.dependencies}

    @hookimpl
    def get_setup_interface(self, plugin_data) -> dict:
        """returns a widget for a tab in setup, and probably data for the setup structure

        :plugin_type: as all the plugins will be rolled in one loop, but plugins will be of different types, not all of them should return smth.
        This argument will allow the specific implementation of the hook to identify if any response is needed or not.
        :return: dict containing widget and setup structure
        """
        self.smu._initGUI(plugin_data[self.plugin_name]["settings"])
        return {self.plugin_name: self.smu.settingsWidget}

    @hookimpl
    def get_functions(self, args=None):
        """returns a dict of publicly accessible functions.

        :return: dict of functions
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.smu._get_public_methods()}

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
