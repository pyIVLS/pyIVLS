#!/usr/bin/python3.8
from os.path import dirname, sep
import sys

import importlib
from configparser import ConfigParser
import pluggy

# Import to communicate with the GUI
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from plugins.pyIVLS_hookspec import pyIVLS_hookspec

import pyIVLS_constants


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

    def get_plugin_info_for_settingsGUI(self) -> dict:
        """Returns a dictionary with the plugin info for the settings widget.

        Returns:
            dict: plugin name -> plugin widget
        """
        plugin_manager = self.pm
        single_element_dicts = self.pm.hook.get_setup_interface(plugin_data=self.get_plugin_dict())
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
                if plugin.rsplit("_", 1)[1] == 'plugin':
                        option_dict = {}
                        for option in ["type","function", "class", "load", "dependencies", "address"]:
                                if self.config.has_option(plugin, option):
                                        option_dict[option] = self.config[plugin][option]
                                else:
                                        option_dict[option] = "" 
                        if self.config.has_section(f"{self.config[plugin]['name']}_settings"):
                                option_dict["settings"] = dict(self.config.items(f"{self.config[plugin]['name']}_settings"))  
                        else:
                                option_dict["settings"] = {}
                        section_dict[self.config[plugin]['name']] = option_dict         
        return section_dict

    def _register(self, plugin) -> bool:
        """Registers a plugin with the plugin manager. Dynamically imports the plugin and creates an instance of the plugin class.
        Handles errors, checks if the plugin is already registered and if it is a dependency for another plugin.

        Args:
            plugin (str): section name in the ini file

        Returns:
            bool: registered or not
        """
        plugin_name = self.config[plugin]["name"]
        
        module_name = f"pyIVLS_{plugin_name}"
        class_name = f"pyIVLS_{plugin_name}_plugin"
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
                # FIXME: remove debug print
                print(f"Plugin {plugin_name} loaded")
                return True
            else:
                sys.path.remove(self.path + "plugins" + sep + self.config[plugin]["address"])
                return False
        except (ImportError, AttributeError) as e:
            print(f"Failed to load plugin {plugin_name}: {e}")
            self.config[plugin]["load"] = "False"
            sys.path.remove(self.path + "plugins" + sep + self.config[plugin]["address"])
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
        # FIXME: Naive implementation. If a pluginload fails on startup, it's not retried. This makes it possible for the user™ to break something.
        ##IRtodo#### it needs to be checked that there are no 2 plugins with the same name/or 2 plugins with the same function
        for plugin in self.config.sections():
                if plugin.rsplit("_", 1)[1] == 'plugin':
                        if self.config[plugin]["load"] == "True":
                                self._register(plugin)

    def public_function_exchange(self):
        #get all the plugin public functions by plugin name, in case at some point there may be 2 plugins with the same function.
        plugin_public_functions = self.pm.hook.get_functions()
        available_public_functions = {}
        #change public functions names as dict keys to plugin function, thus every plugin may find objects it needs
        for public_functions in plugin_public_functions:
            plugin_name = list(public_functions.keys())[0]
            available_public_functions[self.config[plugin_name + '_plugin']["function"]] = public_functions[plugin_name]
        self.pm.hook.set_function(function_dict = available_public_functions)    

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
            
    # NOTE: This function *might* fail with circular dependencies. Plugins might be loaded multiple times, but _register should make sure that only one instance is registered.
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
                # Check against the "function" field
                for plugin_name in self.config.sections():
                    if self.config[plugin_name]["function"] == dependency:
                        if self.pm.get_plugin(plugin_name) is None:
                            # add the dependency to the list of plugins to activate
                            plugins_to_activate.append(plugin_name)
                            added_deps.append(plugin_name)
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
                # Check against the "function" field
                if self.config[plugin]["function"] in dependencies:
                    return True, plugin_name

        return False, ""

    def __init__(self):
        """initializes the container and the plugin manager. Reads the config file and registers all plugins set to load on startup."""
        super().__init__()
        self.path = dirname(__file__) + sep
        sys.path.append(self.path + "plugins"+ sep)
        self.pm = pluggy.PluginManager("pyIVLS")
        self.pm.add_hookspecs(pyIVLS_hookspec)

        self.config = ConfigParser()
        self.config.read(self.path + pyIVLS_constants.configFileName)
        self.register_start_up()

    def cleanup(self) -> None:
        """Explicitly cleanup resources, such as writing the config file."""
        config_path = self.path + pyIVLS_constants.configFileName
        with open(config_path, "w") as configfile:
            self.config.write(configfile)
