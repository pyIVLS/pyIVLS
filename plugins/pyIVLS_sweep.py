#!/usr/bin/python3.8
import pluggy
from sweepGUI import sweepGUI


class pyIVLS_sweep_plugin:
    """Hooks for the tester plugin"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        ##IRtothink#### there should be some kind of configuration file for installing the plugins. This config file may be stored in the plugin folder, and the plugin data may be read from there
        self.plugin_name = "sweep"
        self.plugin_function = "ivsweep"
        self.plugin_dependencies = ["smu", "camera"]
        self.sweep = sweepGUI()
        super().__init__()

    @hookimpl
    def get_setup_interface(self, plugin_data) -> dict:
        """returns a widget for a tab in setup, and probably data for the setup structure

        :plugin_type: as all the plugins will be rolled in one loop, but plugins will be of different types, not all of them should return smth.
        This argument will allow the specific implementation of the hook to identify if any response is needed or not.
        :return: dict containing widget and setup structure
        """
        self.sweep._initGUI(plugin_data[self.plugin_name]["settings"])
        return {self.plugin_name: self.sweep.settingsWidget}

    @hookimpl
    def get_MDI_interface(self, args=None) -> dict:
        """Returns MDI window for camera preview

        Returns:
            dict: name, widget
        """
        return {self.plugin_name: self.sweep.MDIWidget}

    @hookimpl
    def get_functions(self, args=None):
        """Returns a dictionary of publicly accessible functions. This function is called from pyIVLS_container

        Args:
            args (dict): function

        Returns:
            dict: functions
        """
        if args is None or args.get("function") == plugin_function:
            return {self.plugin_name: self.sweep._get_public_methods()}

    @hookimpl
    def set_function(self, function_dict):
        """provides a list of available public functions from other plugins as a nested list

        Returns:
            dict: name, widget
        """
        pruned = {
            function_dict_key: function_dict[function_dict_key]
            for function_dict_key in self.plugin_dependencies
            if function_dict_key in function_dict
        }
        ret = self.sweep._getPublicFunctions(pruned)

        return ret

    @hookimpl
    def get_log(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.sweep._getLogSignal()}

    @hookimpl
    def get_info(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.sweep._getInfoSignal()}

    @hookimpl
    def get_closeLock(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.sweep._getCloseLockSignal()}
