import os
import inspect
from PyQt6 import uic
import pyIVLS_constants as const


# NOTE: Work in progress. PLuggy wont register inherited hooks
class Plugin:
    # Classwide variables
    non_public_methods = ["load_settings_widget", "get_public_methods"]
    non_public_methods.extend(const.HOOKS)


    def __init__(self):
        self.settingsWidget, self.plugin_name = self.load_settings_widget()
        settingsWidget = None
        plugin_name = None
        plugin_info = None

    def load_settings_widget(self, pm, plugin_info):
        """
        Loads the settings widget UI file
        """
        # Get the name of the subclass
        stack = inspect.stack()
        calling_class = stack[1].frame.f_locals["self"].__class__.__name__
        plugin_name = calling_class.removeprefix("pyIVLS_").removesuffix("_plugin")

        self.path = os.path.dirname(__file__) + os.path.sep
        filename = plugin_name + "_settingsWidget.ui"

        ui_file_path = self.path + plugin_name + os.path.sep + filename

        if os.path.exists(ui_file_path):
            print(f"Loading UI file {ui_file_path}")
            return uic.loadUi(ui_file_path), plugin_name
        else:
            raise FileNotFoundError(f"UI file {ui_file_path} not found.")

    def get_public_methods(self):
        """
        Returns a list of public methods for the plugin
        """
        return [
            method
            for method in dir(self)
            if callable(getattr(self, method))
            and not method.startswith("__")
            and method not in self.non_public_methods
        ]
