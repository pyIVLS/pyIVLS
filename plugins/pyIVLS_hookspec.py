#!/usr/bin/python3.8
import pluggy


class pyIVLS_hookspec:
    hookspec = pluggy.HookspecMarker("pyIVLS")

    @hookspec
    def get_setup_interface(self, plugin_data: dict) -> dict:
        """returns a widget for a tab in setup, and probably data for the setup structure

        :plugin_type: as all the plugins will be rolled in one loop, but plugins will be of different types, not all of them should return smth.
        This argument will allow the specific implementation of the hook to identify if any response is needed or not.
        :return: dict containing widget and setup structure
        """

    @hookspec
    def get_MDI_interface(self, args=None) -> dict:
        """returns a widget for a tab in setup, and probably data for the setup structure

        args may include
               :plugin_type: as all the plugins will be rolled in one loop, but plugins will be of different types, not all of them should return smth.
               This argument will allow the specific implementation of the hook to identify if any response is needed or not.
               :return: dict containing widget and setup structure

        """

    @hookspec
    def get_function(self, args=None):
        """returns a dict of publicly accessible functions.¨
        kwargs can be used to specify which functions are needed based on
        type, function.
        """

    @hookspec
    def set_function(self, function_dict):
        """provides a list of publicly available functions to the plugin as a nested dict
        {'function1' : {'def1': object, 'def2':object},
         'function2' : {'def1': object, 'def2':object},}

        :return: list containing missed plugins or functions in form of [plg1, plg2:func3]
        """

    @hookspec
    def get_log(self, args=None):
        """provides the signal for logging to main app

        args may include
        :plugin_type: as all the plugins will be rolled in one loop, but plugins will be of different types, not all of them should return smth.
        This argument will allow the specific implementation of the hook to identify if any response is needed or not.
        :return: dict containing signal for logging
        """

    @hookspec
    def get_info(self, args=None):
        """provides the signal for showing info messages in the main app

        args may include
        :plugin_type: as all the plugins will be rolled in one loop, but plugins will be of different types, not all of them should return smth.
        This argument will allow the specific implementation of the hook to identify if any response is needed or not.
        :return: dict containing signal for logging
        """

    @hookspec
    def get_closeLock(self, args=None):
        """provides the signal for preventing main window close if a proccess is running

        args may include
        :plugin_type: as all the plugins will be rolled in one loop, but plugins will be of different types, not all of them should return smth.
        This argument will allow the specific implementation of the hook to identify if any response is needed or not.
        :return: dict containing signal for logging
        """
