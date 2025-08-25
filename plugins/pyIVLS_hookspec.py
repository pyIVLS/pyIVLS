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
    def get_plugin(self, args=None):
        """
        IN THE PROGRESS OF BEING DEPRECATED
        Returns the plugin as a reference to itself.
        NOTE: when writing implmentations of this, the plugin should contain its own metadata, such as name, type, version, etc.

        Args:
            args (_type_, optional): can be used to specify which plugin is needed based on
            type, function, etc.

        Returns:
            tuple[object, metadata]: reference to the plugin itself along with its properties such as name, type, version, etc.

        IN THE PROGRESS OF BEING DEPRECATED
        """

    @hookspec
    def set_plugin(self, plugin_list, args=None):
        """
        IN THE PROGRESS OF BEING DEPRECATED

        gets a list of plugins available, fetches the ones it needs.

        Args:
            plugin_list (list): list of plugins in the form of [plugin1, plugin2, ...]
        IN THE PROGRESS OF BEING DEPRECATED
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

    @hookspec
    def get_plugin_settings(self, args=None):
        """Reads the current settings from the settingswidget, returns a dict.

        Args:
            args (dict??, optional): Spesifies if a response is needed, for instance when saving a spesific plugin's settings.
        Returns:
            Tuple [str, int, dict]: name + error code + dict containing the current settings of the plugin. (naming should be consistent with the ini-file?)
        """
