#!/usr/bin/python3.8
import importlib
import sys
from configparser import ConfigParser
from datetime import datetime
from os.path import dirname, sep

import pluggy

# Import to communicate with the GUI
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

import pyIVLS_constants
from plugins.pyIVLS_hookspec import pyIVLS_hookspec


class pyIVLS_container(QObject):
    """
    Container to handle plugin loading and unloading. The plugins are saved with the name field in the .ini file.
    """

    #### Signals for communication

    # send available plugins to the plugin loader
    available_plugins_signal = pyqtSignal(dict)
    # update the settings widget. This goes all the way to pyIVLS.py which handles the updating of the main GUI.
    plugins_updated_signal = pyqtSignal()
    # send available plugins and functions to seqBuilder
    seqComponents_signal = pyqtSignal(dict, list)
    # show a message to the user in the plugin loader GUI
    show_message_signal = pyqtSignal(str)
    # add info to log
    log_message = pyqtSignal(str)

    #### Slots for communication
    @pyqtSlot()
    def read_available_plugins(self):
        """Called from the plugin loader to request the available plugins.
        Emits the available_plugins_signal with the plugin dictionary."""
        if self.debug:
            print("read_available_plugins in container called")
        self.available_plugins_signal.emit(self.get_plugin_dict())

    @pyqtSlot(list)
    def update_registration(self, plugins_to_activate: list):
        """Updates the registrations based on the list of plugins to activate. Unloads all other plugins.
        Only signals the settings widget to update if changes are applied.

        Args:
            plugins_to_activate (list): list of plugin names to activate
        """
        # NOTE: There is some overhead here, since all plugins are checked even is no changes are made.
        # I don't think that this will be a problem, since the check is O(n) on a small set (under 100 plugins).
        if self.debug:
            print("update_registration in container called with: ", plugins_to_activate)
        changes_applied = False
        # add dependencies to the list of plugins to activate
        plugins_to_activate = self._check_dependencies_register(plugins_to_activate)

        for plugin in self.config.sections():
            # check that the section is a plugin.
            if plugin.rsplit("_", 1)[1] == "plugin":
                if plugin in plugins_to_activate:
                    if self._register(plugin):
                        changes_applied = True
                else:
                    if self._unregister(plugin):
                        changes_applied = True

        if changes_applied:
            self.plugins_updated_signal.emit()
            self.cleanup()

    def get_plugin_info_for_settingsGUI(self) -> dict:
        """Returns a dictionary with the plugin info for the settings widget.

        Returns:
            dict: plugin name -> plugin widget
        """
        single_element_dicts = self.pm.hook.get_setup_interface(
            plugin_data=self.get_plugin_dict()
        )
        combined_dict = {}
        for d in single_element_dicts:
            combined_dict.update(d)
        return combined_dict

    def get_plugin_info_for_MDIarea(self) -> dict:
        """Returns a dictionary with the plugin info for the settings widget.

        Returns:
            dict: plugin name -> plugin widget
        """
        single_element_dicts = self.pm.hook.get_MDI_interface()
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
        for plugin in self.config.sections():
            if plugin.rsplit("_", 1)[1] == "plugin":
                option_dict = {}
                for option in [
                    "type",
                    "function",
                    "class",
                    "load",
                    "dependencies",
                    "address",
                ]:
                    if self.config.has_option(plugin, option):
                        option_dict[option] = self.config[plugin][option]
                    else:
                        option_dict[option] = ""
                if self.config.has_section(f"{self.config[plugin]['name']}_settings"):
                    option_dict["settings"] = dict(
                        self.config.items(f"{self.config[plugin]['name']}_settings")
                    )
                else:
                    option_dict["settings"] = {}
                section_dict[self.config[plugin]["name"]] = option_dict
        return section_dict

    def _register(self, plugin) -> bool:
        """Registers a plugin with the plugin manager. Dynamically imports the plugin and creates an instance of the plugin class.
        Handles errors, checks if the plugin is already registered and if it is a dependency for another plugin.

        Args:
            plugin (str): section name in the ini file, aka x_plugin

        Returns:
            bool: Changes made or not. True if the plugin was registered, False if it was already registered or an error occurred.
        """
        # read the plugin name from the config
        plugin_name = self.config[plugin]["name"]

        if self.debug:
            print("Registering plugin: ", plugin_name)

        module_name = f"pyIVLS_{plugin_name}"
        class_name = f"pyIVLS_{plugin_name}_plugin"
        # add the plugin path if stored in a weird place. For future use.
        sys.path.append(self.path + "plugins" + sep + self.config[plugin]["address"])
        try:
            # Dynamic import using importlib
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, class_name)
            plugin_instance = plugin_class()
            # Check if the plugin is already registered
            if self.pm.get_plugin(plugin_name) is None:
                # Register the plugin with the standard name to prevent multiple instances
                self.pm.register(plugin_instance, name=plugin_name)
                self.config[plugin]["load"] = "True"
                self.public_function_exchange()
                self.log_message.emit(
                    datetime.now().strftime("%H:%M:%S.%f")
                    + f" : Plugin {plugin_name} loaded"
                )
                return True
            else:
                # sys.path.remove(self.path + "plugins" + sep + self.config[plugin]["address"])
                # Commented out since I think it is not needed. Might lead to issues where reloading the plugin removes the path.
                return False
        except (ImportError, AttributeError) as e:
            self.log_message.emit(
                datetime.now().strftime("%H:%M:%S.%f")
                + f" : Failed to load plugin {plugin_name}: {e}"
            )
            self.config[plugin]["load"] = "False"
            sys.path.remove(
                self.path + "plugins" + sep + self.config[plugin]["address"]
            )
            return False

    def _unregister(self, plugin: str) -> bool:
        """unregisters a plugin with the plugin manager. Checks if the plugin is a dependency for another plugin.
        Handles errors.

        Args:
            plugin (str): section name in the ini file, aka x_plugin

        Returns:
            bool: unregistered or not
        """
        try:
            # read the plugin name from the config
            plugin_name = self.config[plugin]["name"]
            # Retrieve the registered plugin instance
            plugin_instance = self.pm.get_plugin(plugin_name)
            if self.debug:
                print(
                    f"Trying to unregister plugin: {plugin} with name {plugin_name}. Instance: {plugin_instance}"
                )
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
                self.log_message.emit(
                    datetime.now().strftime("%H:%M:%S.%f")
                    + f": Plugin {plugin_name} unloaded"
                )
                return True
            # plugin not registered, do nothing.
            return False
        except ImportError:
            self.log_message.emit(
                datetime.now().strftime("%H:%M:%S.%f")
                + ": Failed to unload plugin {plugin}: {e}"
            )
            return False
        except AttributeError as e:
            self.log_message.emit(
                datetime.now().strftime("%H:%M:%S.%f")
                + f" : Failed to unload plugin {plugin}: {e}"
            )
            return False

    def register_start_up(self):
        """Checks the .ini file for saved settings and registers all plugins that are set to load on startup."""
        self.config = ConfigParser()
        self.config.read(self.path + pyIVLS_constants.configFileName)

        # FIXME: Naive implementation. If a pluginload fails on startup, it's not retried. This makes it possible for the user™ to break something.
        ##IRtodo#### it needs to be checked that there are no 2 plugins with the same name/or 2 plugins with the same function
        for plugin in self.config.sections():
            # sections contain at least _settings and _plugin, extract the ones that are plugins:
            _, type = plugin.rsplit("_", 1)
            if type == "plugin":
                if self.config[plugin]["load"] == "True":
                    self._register(plugin)

    def public_function_exchange(self):
        # Get all the plugin public functions by plugin name
        plugin_public_functions = self.pm.hook.get_functions()
        function_map = {}

        for single_dict in plugin_public_functions:
            for plugin_name, methods in single_dict.items():
                plugin_function = self.config[plugin_name + "_plugin"]["function"]
                
                if plugin_function not in function_map:
                    # Store first occurrence as-is
                    function_map[plugin_function] = {plugin_name: methods}
                else:
                    # If already exists, check if it's the first conflict
                    existing = function_map[plugin_function]
                    if isinstance(existing, dict) and len(existing) == 1:
                        # Convert from flat to nested if there's now a conflict
                        function_map[plugin_function][plugin_name] = methods
                    else:
                        # Add to existing nested structure
                        function_map[plugin_function][plugin_name] = methods

        # Flatten functions with only one plugin back to function -> methods
        final_map = {}
        for function, plugins in function_map.items():
            if len(plugins) == 1:
                plugin_name = next(iter(plugins))
                final_map[function] = plugins[plugin_name]
            else:
                final_map[function] = plugins

        print("Final function map:", final_map)  # Debugging output

        self.pm.hook.set_function(function_dict=final_map)
        self.seqComponents_signal.emit(self.get_plugin_dict(),plugin_public_functions)

    def getLogSignals(self):
        plugin_logSignals = self.pm.hook.get_log()
        logSignals = []
        for logSignal in plugin_logSignals:
            plugin_name = list(logSignal.keys())[0]
            logSignals.append(logSignal[plugin_name])
        return logSignals

    def getInfoSignals(self):
        plugin_infoSignals = self.pm.hook.get_info()
        infoSignals = []
        for infoSignal in plugin_infoSignals:
            plugin_name = list(infoSignal.keys())[0]
            infoSignals.append(infoSignal[plugin_name])
        return infoSignals

    def getCloseLockSignals(self):
        plugin_closeLockSignals = self.pm.hook.get_closeLock()
        closeLockSignals = []
        for closeLockSignal in plugin_closeLockSignals:
            plugin_name = list(closeLockSignal.keys())[0]
            closeLockSignals.append(closeLockSignal[plugin_name])
        return closeLockSignals

    def _check_dependencies_register(self, plugins_to_activate: list) -> list:
        """Check the dependencies of plugins to be activated. Adds the
        dependencies to the list of plugin to be activated.

        Args:
            plugins_to_activate (list): plugins to be activated, format: x_plugin (section name in the ini file)

        Returns:
            list: updated loading list, format: x_plugin (section name in the ini file)
        """

        def resolve_dependencies(plugin, seen):
            """recursion helper to find the dependencies of dependencies"""
            if plugin in seen:
                return  # stop when seeing an already seen plugin
            seen.add(plugin)

            dependencies = self.config[plugin].get("dependencies", "").split(",")
            if self.debug:
                print(f"Checking dependencies for {plugin}: {dependencies}")

            for dependency in filter(None, dependencies):  # filter out empties
                for section in self.config.sections():
                    name, type = section.rsplit("_", 1)
                    # if type is plugin and fulfills the dep
                    if (
                        type == "plugin"
                        and self.config[section].get("function") == dependency
                    ):
                        # if not registered and not in list to be registered
                        if (
                            self.pm.get_plugin(name) is None
                            and section not in plugins_to_activate
                        ):
                            # plugins to activate + section, added_deps + name for the message.
                            plugins_to_activate.append(section)
                            added_deps.append(name)
                            # here we go again :)
                            resolve_dependencies(section, seen)

        added_deps = []
        seen = set()

        if self.debug:
            print("Checking dependencies for: ", plugins_to_activate)

        for plugin in plugins_to_activate.copy():
            resolve_dependencies(plugin, seen)

        if added_deps:
            self.log_message.emit(
                datetime.now().strftime("%H:%M:%S.%f")
                + f": Added dependencies: {', '.join(added_deps)}"
            )

        return plugins_to_activate

    def _check_dependencies_unregister(self, plugin: str) -> tuple[bool, str]:
        """Goes through all active plugins and checks if the arg plugin is a necessary dependency for any of them. NOTE: this function only finds the first dependency, not all.

        Args:
            plugin (str): name of the plugin being unregistered, format: x_plugin (section name in the ini file)

        Returns:
            tuple[bool, str]: is a dependency, dependent plugin name in format x_plugin
        """
        # TODO: Modify this to take in a list of plugins and modify the list according to dependencies.
        # see _check_dependencies_register for the logic.

        # iterate through all sections
        for section in self.config.sections():
            if section.rsplit("_", 1)[1] == "plugin":
                name = self.config[section]["name"]
                # check if the section is a plugin and if it is loaded
                if self.pm.get_plugin(name) is not None:
                    # check the depencency list of the registered plugin
                    dependencies = (
                        self.config[section].get("dependencies", "").split(",")
                    )
                    # Check that if the plugin currently being unregistered is needed by the registered plugin
                    if self.config[plugin]["function"] in dependencies:
                        return True, section

        return False, ""

    def __init__(self):
        """initializes the container and the plugin manager. Reads the config file and registers all plugins set to load on startup."""
        super().__init__()
        self.path = dirname(__file__) + sep
        sys.path.append(self.path + "plugins" + sep)
        self.pm = pluggy.PluginManager("pyIVLS")
        self.pm.add_hookspecs(pyIVLS_hookspec)
        self.debug = False

    def cleanup(self) -> None:
        """Explicitly cleanup resources, such as writing the config file."""
        config_path = self.path + pyIVLS_constants.configFileName
        with open(config_path, "w") as configfile:
            self.config.write(configfile)
