#!/usr/bin/python3.8
from os.path import dirname, sep


import importlib
from configparser import SafeConfigParser
import pluggy

# Import to communicate with the GUI
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from plugins.pyIVLS_hookspec import pyIVLS_hookspec

import pyIVLS_constants


# please stop yelling at me pylint :(


class pyIVLS_container(QObject):
    """Container to handle pluggy module loading"""

    #### Signals for communication

    # send available plugins to the plugin loader
    available_plugins_signal = pyqtSignal(dict)
    # update the settings widget. This goes all the way to pyIVLS.py which handles the updating of the main GUI.
    plugins_updated_signal = pyqtSignal()
    # show a message to the user in the plugin loader GUI
    show_message_signal = pyqtSignal(str)

    #### Slots for communication
    @pyqtSlot()
    def read_available_plugins(self):
        """Called from the plugin loader to request the available plugins.
        Emits the available_plugins_signal with the plugin dictionary."""
        self.available_plugins_signal.emit(self.get_plugin_dict())

    @pyqtSlot(list)
    def update_registration(self, plugins_to_activate: list):
        """Updates the registrations based on the list of plugins to activate. Unloads all other plugins.
        Only signals the settings widget to update if changes are applied.

        Args:
            plugins_to_activate (list): list of plugin names to activate
        """

        changes_applied = False
        # add dependencies to the list of plugins to activate
        plugins_to_activate = self._check_dependencies_register(plugins_to_activate)

        for plugin in self.config.sections():
            if plugin in plugins_to_activate:
                if self._register(plugin):
                    changes_applied = True
            else:
                if self._unregister(plugin):
                    changes_applied = True

        if changes_applied:
            self.plugins_updated_signal.emit()
            self.cleanup()

    def get_plugin_info_from_settings(self) -> dict:
        """Returns a dictionary with the plugin info for the settings widget.

        Returns:
            dict: plugin name -> plugin widget
        """
        plugin_manager = self.pm
        single_element_dicts = self.pm.hook.get_setup_interface(pm=plugin_manager)
        combined_dict = {}
        for d in single_element_dicts:
            combined_dict.update(d)
        return combined_dict

    def get_plugin_dict(self) -> dict:
        """Returns a dictionary with all plugins and their properties.

        Returns:
            dict: plugin -> data
        """

        section_dict = {}

        # Iterate through all sections in the parser
        for section in self.config.sections():
            # Create a dictionary with the section name as the key and the section items as the value
            section_dict[section] = dict(self.config.items(section))

        return section_dict

    def _register(self, plugin: str) -> bool:
        """Registers a plugin with the plugin manager. Dynamically imports the plugin and creates an instance of the plugin class.
        Handles errors, checks if the plugin is already registered and if it is a dependency for another plugin.

        Args:
            plugin (str): plugin name to activate

        Returns:
            bool: registered or not
        """
        module_name = f"plugins.pyIVLS_{plugin}"
        class_name = f"pyIVLS_{plugin}_plugin"

        try:
            # Dynamic import using importlib
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, class_name)
            plugin_instance = plugin_class()
            # Check if the plugin is already registered
            if self.pm.get_plugin(plugin) is None:
                # Register the plugin with the standard name to prevent multiple instances
                self.pm.register(plugin_instance, name=plugin)
                self.config[plugin]["load"] = "True"
                # FIXME: remove debug print
                print(f"Plugin {plugin} loaded")
                return True
            else:
                return False
        except (ImportError, AttributeError) as e:
            print(f"Failed to load plugin {plugin}: {e}")
            self.config[plugin]["load"] = "False"
            return False

    def _unregister(self, plugin: str) -> bool:
        """unregisters a plugin with the plugin manager. Checks if the plugin is a dependency for another plugin.
        Handles errors.

        Args:
            plugin (str): plugin name to deactivate

        Returns:
            bool: unregistered or not
        """
        try:
            # Retrieve the registered plugin instance
            plugin_instance = self.pm.get_plugin(plugin)
            # is the plugin registered?
            if plugin_instance is not None:
                is_dependency, dependent_plugin = self._check_dependencies_unregister(
                    plugin
                )

                # check if the plugin is a dependency for another plugin
                if is_dependency:
                    self.show_message_signal.emit(
                        f"Plugin {plugin} is a dependency for {dependent_plugin}, not unloading"
                    )
                    return False
                # if not, unregister the plugin
                self.pm.unregister(plugin_instance)
                self.config[plugin]["load"] = "False"
                # FIXME: remove debug print
                print(f"Plugin {plugin} unloaded")
                return True
            # plugin not registered, do nothing.
            return False
        except ImportError as e:
            print(f"Failed to unload plugin {plugin}: {e}")
            return False
        except AttributeError as e:
            print(f"Failed to unload plugin {plugin}: {e}")
            return False

    def register_start_up(self):
        """Checks the .ini file for saved settings and registers all plugins that are set to load on startup."""
        for plugin in self.config.sections():
            if self.config[plugin]["load"] == "True":
                self._register(plugin)

    # NOTE: This function might fail with more complex circular dependencies. Plugins might be loaded multiple times, but _register() should handle this.
    def _check_dependencies_register(self, plugins_to_activate: list) -> list:
        """Checks the dependencies of the plugins to activate and adds them to the list of plugins to activate.

        Args:
            plugins_to_activate (list): list of plugins to activate

        Returns:
            list: list of plugins to activate with added dependencies
        """
        # list to store additional deps. FIXME: Add functionality to print these later.
        added_deps = []
        # go through all plugins to activate and check if they have dependencies
        for plugin in plugins_to_activate:
            dependencies = self.config[plugin]["dependencies"].split(",")
            for dependency in dependencies:
                # Check if dep is empty:
                if dependency == "":
                    continue
                if self.pm.get_plugin(dependency) is None:
                    # add the dependency to the list of plugins to activate
                    plugins_to_activate.append(dependency)
                    added_deps.append(dependency)
        # notify the user if dependencies are automatically added
        if added_deps:
            self.show_message_signal.emit(
                f"Added dependencies: {', '.join(added_deps)} to the list of plugins to activate"
            )
        return plugins_to_activate

    def _check_dependencies_unregister(self, plugin: str) -> tuple[bool, str]:
        """Goes through all active plugins and checks if the arg plugin is a necessary dependency for any of them. NOTE: this function only finds the first dependency, not all.

        Args:
            plugin (str): name of the plugin being unregistered

        Returns:
            tuple[bool, str]: is a dependency, dependent plugin name
        """
        for plugin_name in self.config.sections():
            if self.pm.get_plugin(plugin_name) is not None:
                dependencies = self.config[plugin_name]["dependencies"].split(",")
                if plugin in dependencies:
                    return True, plugin_name

        return False, ""

    def __init__(self):
        """initializes the container and the plugin manager. Reads the config file and registers all plugins set to load on startup."""
        super().__init__()
        self.path = dirname(__file__) + sep

        self.pm = pluggy.PluginManager("pyIVLS")
        self.pm.add_hookspecs(pyIVLS_hookspec)

        self.config = SafeConfigParser()
        self.config.read(self.path + pyIVLS_constants.configFileName)
        self.register_start_up()

    def cleanup(self) -> None:
        """Explicitly cleanup resources, such as writing the config file."""
        config_path = self.path + pyIVLS_constants.configFileName
        with open(config_path, "w") as configfile:
            self.config.write(configfile)
