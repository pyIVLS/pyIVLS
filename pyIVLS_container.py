#!/usr/bin/python3.8
import sys
from os.path import dirname, sep

from configparser import SafeConfigParser
import pluggy
from plugins.pyIVLS_hookspec import pyIVLS_hookspec

import pyIVLS_constants

import importlib

# Import to communicate with the GUI
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

# please stop yelling at me pylint :(


class pyIVLS_container(QObject):

    #### Signals for communication
    available_plugins_signal = pyqtSignal(dict)
    plugins_updated_signal = pyqtSignal()

    #### Slots for communication
    @pyqtSlot()
    def read_available_plugins(self):
        self.available_plugins_signal.emit(self.getPluginDict())

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

    def getPluginInfoFromSettings(self):
        #     inData = [None]*pyRTA_constants.positionsSettings
        #     parser = SafeConfigParser()
        #     parser.read(self.path+pyIVLS_constants.configFileName)
        #     inData[pyIVLS_constants.plugins_num] = parser.get('Plugins', 'num').lstrip()
        #     inData[pyIVLS_constants.plugins_num] = parser.get('Plugins', 'num').lstrip()

        #     with open(self.path+pyIVLS_constants.configFileName, 'w') as configfile:
        #          parser.write(configfile)

        single_element_dicts = self.pm.hook.get_setup_interface()
        combined_dict = {}
        for d in single_element_dicts:
            combined_dict.update(d)
        return combined_dict

    def getPluginDict(self) -> dict:
        # Extract plugin names
        section_dict = {}

        # Iterate through all sections in the parser
        for section in self.config.sections():
            section_dict[section] = dict(self.config.items(section))

        return section_dict

    def _register(self, plugin: str) -> bool:
        module_name = f"plugins.pyIVLS_{plugin}"
        class_name = f"pyIVLS_{plugin}_plugin"

        try:
            # Dynamic import using importlib
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, class_name)
            plugin_instance = plugin_class()

            if self.pm.get_plugin(plugin) is None:
                self.pm.register(plugin_instance, name=plugin)
                self.config[plugin]["load"] = "True"
                print(f"Plugin {plugin} loaded")
                return True
            else:
                return False
        except (ImportError, AttributeError) as e:
            print(f"Failed to load plugin {plugin}: {e}")
            return False

    def _unregister(self, plugin: str) -> bool:
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
                    print(
                        f"Plugin {plugin} is a dependency for {dependent_plugin}, not unloading"
                    )
                    return False
                # if not, unregister the plugin
                self.pm.unregister(plugin_instance)
                self.config[plugin]["load"] = "False"
                print(f"Plugin {plugin} unloaded")
                return True
            # plugin already registered, do nothing.
            else:
                return False
        except Exception as e:
            print(f"Failed to unload plugin {plugin}: {e}")
            return False

    def register_start_up(self):
        for plugin in self.config.sections():
            if self.config[plugin]["load"] == "True":
                self._register(plugin)

    # NOTE: This function might fail with more complex circular dependencies.
    def _check_dependencies_register(self, plugins_to_activate: list):
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

        return plugins_to_activate

    def _check_dependencies_unregister(self, plugin: str) -> tuple[bool, str]:
        for plugin_name in self.config.sections():
            if self.pm.get_plugin(plugin_name) is not None:
                dependencies = self.config[plugin_name]["dependencies"].split(",")
                if plugin in dependencies:
                    return True, plugin_name

        return False, ""

    def __init__(self):
        super().__init__()
        self.path = dirname(__file__) + sep

        self.pm = pluggy.PluginManager("pyIVLS")
        self.pm.add_hookspecs(pyIVLS_hookspec)

        self.config = SafeConfigParser()
        self.config.read(self.path + pyIVLS_constants.configFileName)
        self.register_start_up()

    def cleanup(self):
        """Explicitly cleanup resources, such as writing the config file."""
        config_path = self.path + pyIVLS_constants.configFileName
        with open(config_path, "w") as configfile:
            self.config.write(configfile)
