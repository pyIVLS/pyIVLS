import os
import inspect
from PyQt6 import uic
import pyIVLS_constants as const


class Plugin:
    # Classwide variables
    non_public_methods = ["setup", "get_public_methods", "hookimpl"]
    non_public_methods.extend(const.HOOKS)

    def __init__(self):
        self.plugin_name = None
        self.plugin_info = None
        self.pm = None

    # NOTE: currently creates quite a bit of overhead since the vars
    # are updated every time the plugin list is updated.
    # On the other hand, This will probably not be a bottleneck.
    def setup(self, pm, plugin_info):
        """
        Loads the plugin info
        """
        # Currently commented out, since I don't want to rewrite the entire plugin system
        # To store the settings widget in the plugin class
        """
        # Get the name of the subclass from the stack
        stack = inspect.stack()
        calling_class = stack[1].frame.f_locals["self"].__class__.__name__
        plugin_name = calling_class.removeprefix("pyIVLS_").removesuffix("_plugin")

        self.path = os.path.dirname(__file__) + os.path.sep
        filename = plugin_name + "_settingsWidget.ui"

        ui_file_path = self.path + plugin_name + os.path.sep + filename

        if os.path.exists(ui_file_path):
            print(f"Loading UI file {ui_file_path}")
            settingsWidget = uic.loadUi(ui_file_path)
        else:
            raise FileNotFoundError(f"UI file {ui_file_path} not found.")
        """
        stack = inspect.stack()
        calling_class = stack[1].frame.f_locals["self"].__class__.__name__
        plugin_name = calling_class.removeprefix("pyIVLS_").removesuffix("_plugin")

        # Set internal variables
        self.plugin_info = plugin_info.get(plugin_name)
        if self.plugin_info["dependencies"] != "":
            self.pm = pm
        self.plugin_name = plugin_name

    def get_public_methods(self):
        """
        Returns a nested dictionary of public methods for the plugin
        """
        # if the plugin type matches the requested type, return the functions

        methods = {
            method: getattr(self, method)
            for method in dir(self)
            if callable(getattr(self, method))
            and not method.startswith("__")
            and not method.startswith("_")
            and method not in self.non_public_methods
        }
        return {self.plugin_name: methods}
