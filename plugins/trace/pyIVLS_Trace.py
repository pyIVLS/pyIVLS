import pluggy
import os
import configparser
from plugins.trace.TraceGUI import TraceGui


class pyIVLS_Trace_plugin:
    """Hooks for trace plugin
    This class acts as a bridge between plugins"""

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

        self.name = config.get("plugin", "name")
        self.type = config.get("plugin", "type")
        self.function = config.get("plugin", "function")
        self._class = config.get("plugin", "class")
        self.dependencies = config.get("plugin", "dependencies", fallback="").split(",")
        self.version = config.get("plugin", "version")
        self.metadata = {"name": self.name, "type": self.type, "function": self.function, "version": self.version, "dependencies": self.dependencies}
        self.trace_control = TraceGui()

    @hookimpl
    def get_setup_interface(self, plugin_data: dict) -> dict:
        """Returns GUI
        Args:
            plugin_data (dict): plugin data read from .ini to read initial settings.

        Returns:
            dict: name, widget
        """
        # Plugin data is keyed by plugin name
        if self.name not in plugin_data:
            raise ValueError(f"Plugin data for {self.name} not found in plugin_data")
        plugin_data = plugin_data[self.name]
        self.trace_control.set_settings_from_plugin_data(plugin_data)
        return {self.name: self.trace_control.settingsWidget}

    @hookimpl
    def get_MDI_interface(self, args=None):
        """Returns MDI window

        Returns:
            dict: name, widget
        """
        if args is None or args.get("function") == self.function:
            return {self.name: self.trace_control.MDIWidget}

    @hookimpl
    def get_plugin_settings(self, args=None):
        """Returns the current settings as (name, status, settings_dict)."""
        status, settings = self.trace_control.parse_settings_widget()
        return (self.metadata["name"], status, settings)
