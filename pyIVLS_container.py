#!/usr/bin/python3.8
import importlib
import sys
from configparser import ConfigParser
from os.path import dirname, sep, basename

import pluggy

# Import to communicate with the GUI
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from plugins.pyIVLS_hookspec import pyIVLS_hookspec


class pyIVLS_container(QObject):
    """
    Container to handle plugin loading and unloading. The plugins are saved with the name field in the .ini file.
    """

    #### Signals for communication
    ### main config name
    configFileName = "pyIVLS.ini"  # FIXME: Magic path until plugin importer is implemented.
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

    def emit_log(self, message: str):
        classname = self.__class__.__name__
        self.log_message.emit(f"{classname} : {message}")

    def emit_error(self, message: str):
        """Emit an error message to the log."""
        classname = self.__class__.__name__
        self.log_message.emit(f"{classname} : ERROR : {message}")

    #### Slots for communication
    @pyqtSlot()
    def read_available_plugins(self):
        """Called from the plugin loader to request the available plugins.
        Emits the available_plugins_signal with the plugin dictionary."""
        if self.debug:
            print("read_available_plugins in container called")
        self.available_plugins_signal.emit(self.get_plugin_dict())

    @pyqtSlot(list, list)
    def update_registration(self, plugins_to_activate: list, hidden_activation: list):
        """Updates the registrations based on the list of plugins to activate. Unloads all other plugins.
        Only signals the settings widget to update if changes are applied.

        Args:
            plugins_to_activate (list): list of plugin names to activate
        """
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

        # update .ini with the hidden mode changes
        for section in self.config.sections():
            if section.rsplit("_", 1)[1] == "plugin":
                if section in hidden_activation:
                    if self.config[section]["hidden"] == "False":
                        changes_applied = True
                    self.config[section]["hidden"] = "True"
                else:
                    if self.config[section]["hidden"] == "True":
                        changes_applied = True
                    self.config[section]["hidden"] = "False"

        if changes_applied:
            self.public_function_exchange()
            self.plugins_updated_signal.emit()
            self.cleanup()

    @pyqtSlot(list)
    def update_config(self, add_ini):
        """Imports a new plugin from an ini file.

        Args:
            add_ini (list): address, ini_path, plugin_name
        """
        # load the config file
        plugin_address, ini_path, plugin_name = add_ini
        new_config = ConfigParser()
        new_config.read(ini_path)
        section_plugin = None
        section_settings = None
        new_section = None
        new_section_settings = None
        # check if a plugin is already registered in the pm
        if self.pm.get_plugin(plugin_name) is not None:
            self.emit_log(f"Plugin {plugin_name} is active, disable it before adding a new version.")
            return
        # get the plugin name from the config
        for section in new_config.sections():
            # if the section name is "plugin"
            if section == "plugin":
                section_plugin = section
                new_section = f"{plugin_name}_plugin"
                new_config[section]["address"] = plugin_address
            elif section == "settings":
                section_settings = section
                new_section_settings = f"{plugin_name}_settings"

        if section_plugin is None or new_section is None:
            self.emit_log(f"Plugin {plugin_name} does not have a plugin section.")
            return

        # add a load option and a load_widget option to the plugin section
        new_config[section_plugin]["load"] = "False"  # default to not loaded
        new_config[section_plugin]["hidden"] = "True"  # default to not loaded in the widget

        # check that the naming is correct
        module_name = f"pyIVLS_{plugin_name}"
        class_name = f"pyIVLS_{plugin_name}_plugin"

        sys.path.append(self.path + "plugins" + sep + new_config[section_plugin]["address"])
        try:
            # Dynamic import using importlib
            module = importlib.import_module(module_name)
            getattr(module, class_name)
            # if the plugin throws no errors here, it's probably a valid plugin.

            # update the section in the config file
            if self.config.has_section(new_section):
                # update the section
                for key, value in new_config[section_plugin].items():
                    self.config[new_section][key] = value
            else:
                # add the section
                self.config.add_section(new_section)
                for key, value in new_config[section_plugin].items():
                    self.config[new_section][key] = value

            if new_section_settings is not None and section_settings is not None:
                # update the settings section
                if self.config.has_section(new_section_settings):
                    # update the section
                    for key, value in new_config[section_settings].items():
                        self.config[new_section_settings][key] = value
                else:
                    # add the section
                    self.config.add_section(new_section_settings)
                    for key, value in new_config[section_settings].items():
                        self.config[new_section_settings][key] = value

            self.emit_log(f"Plugin {plugin_name} added to config file.")
            self.available_plugins_signal.emit(self.get_plugin_dict())

            # write to file
            self.cleanup()

        except ImportError as e:
            self.emit_error(f" : Failed to import plugin {plugin_name} from {plugin_address}: {e}")
        except AttributeError as e:
            self.emit_error(f" : Failed to get plugin class {class_name} from module {module_name}: {e}.")
        except Exception as e:
            self.emit_error(f" : Unknown exception when importing {plugin_name}: {e}")
        finally:
            sys.path.remove(self.path + "plugins" + sep + new_config[section_plugin]["address"])

    @pyqtSlot(str)
    def update_config_file(self, config_path: str) -> None:
        """Updates the config file with the given path. This is called from the plugin loader to update the config file.

        Args:
            config_path (str): full path to the config file
        """
        if self.debug:
            print("Updating config file: ", config_path)
        print("Updating config file: ", config_path)
        # Update the config file path and ensure the directory path is updated
        # get the name of the file, not the full path
        configName = basename(config_path)
        self.configFileName = configName
        self.pm = pluggy.PluginManager("pyIVLS")
        self.pm.add_hookspecs(pyIVLS_hookspec)
        self.register_start_up()
        self.plugins_updated_signal.emit()

    @pyqtSlot()
    def save_settings(self):
        modifications = {}
        current_config: list = self.pm.hook.get_plugin_settings()
        for plugin, code, settings in current_config:
            if code != 0:
                self.emit_error(f"Error saving settings for plugin {plugin}: {code}, {settings['Error message']}")
                continue
            if self.config.has_section(f"{plugin}_settings"):
                for key, value in settings.items():
                    if key == "Error message":
                        # failure to parse settings
                        continue
                    if self.config.has_option(f"{plugin}_settings", key):
                        old_value = self.config[f"{plugin}_settings"][key]
                        if old_value != str(value):
                            self.config[f"{plugin}_settings"][key] = str(value)
                            if plugin not in modifications:
                                modifications[plugin] = []
                            modifications[plugin].append((key, old_value, str(value)))

        # write the config file to disk
        self.cleanup()

        # send detailed info to the log
        if modifications:
            for plugin, changes in modifications.items():
                change_lines = [f"{key}: '{old}' -> '{new}'" for key, old, new in changes]
                change_text = "; ".join(change_lines)
                self.emit_log(f"Settings saved for plugin {plugin}: {change_text}")

    def _hidden_plugin_list(self) -> list:
        """Returns a list of hidden plugins."""
        hidden_plugins = []
        for plugin in self.config.sections():
            if plugin.rsplit("_", 1)[1] == "plugin":
                if self.config[plugin]["hidden"] == "True":
                    hidden_plugins.append(plugin.rsplit("_", 1)[0])
        return hidden_plugins

    def _visible_plugin_list(self) -> list:
        """Returns a list of visible plugins."""
        visible_plugins = []
        for plugin in self.config.sections():
            if plugin.rsplit("_", 1)[1] == "plugin":
                if self.config[plugin]["hidden"] == "False":
                    visible_plugins.append(plugin.rsplit("_", 1)[0])
        return visible_plugins

    def get_plugin_info_for_settingsGUI(self) -> dict:
        """Returns a dictionary with the plugin info for the settings widget.

        Returns:
            dict: plugin name -> plugin widget
        """
        single_element_dicts: list[dict] = self.pm.hook.get_setup_interface(plugin_data=self.get_plugin_dict())
        visible = self._visible_plugin_list()
        combined_dict = {}
        for entry in single_element_dicts:
            if next(iter(entry.keys())) in visible:
                combined_dict.update(entry)
        return combined_dict

    def get_plugin_info_for_MDIarea(self) -> dict:
        """Returns a dictionary with the plugin info for the settings widget.

        Returns:
            dict: plugin name -> plugin widget
        """
        single_element_dicts: list[dict] = self.pm.hook.get_MDI_interface()
        visible = self._visible_plugin_list()
        combined_dict = {}
        for entry in single_element_dicts:
            if next(iter(entry.keys())) in visible:
                combined_dict.update(entry)
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
                    "hidden",
                    "class",
                    "load",
                    "dependencies",
                    "address",
                    "version",
                    "load_widget",
                ]:
                    if self.config.has_option(plugin, option):
                        option_dict[option] = self.config[plugin][option]
                    else:
                        option_dict[option] = ""
                if self.config.has_section(f"{self.config[plugin]['name']}_settings"):
                    option_dict["settings"] = dict(self.config.items(f"{self.config[plugin]['name']}_settings"))
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
                self.emit_log(f"Plugin {plugin_name} loaded")
                return True
            else:
                # sys.path.remove(self.path + "plugins" + sep + self.config[plugin]["address"])
                # Commented out since I think it is not needed. Might lead to issues where reloading the plugin removes the path.
                return False
        except (ImportError, AttributeError) as e:
            self.emit_error(f"Failed to load plugin {plugin_name}: {e}")
            self.config[plugin]["load"] = "False"
            sys.path.remove(self.path + "plugins" + sep + self.config[plugin]["address"])
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
                print(f"Trying to unregister plugin: {plugin} with name {plugin_name}. Instance: {plugin_instance}")
            # is the plugin registered?
            if plugin_instance is not None:
                is_dependency, dependent_plugin = self._check_dependencies_unregister(plugin)

                # check if the plugin is a dependency for another plugin
                if is_dependency:
                    self.show_message_signal.emit(
                        f"Plugin {plugin} is a dependency for {dependent_plugin}, not unloading"
                    )
                    return False
                # if not, unregister the plugin
                self.pm.unregister(plugin_instance)
                self.config[plugin]["load"] = "False"
                self.emit_log(f"Plugin {plugin_name} unloaded")
                return True
            # plugin not registered, do nothing.
            return False
        except ImportError:
            self.emit_error(f"Failed to unload plugin {plugin}")
            return False
        except AttributeError as e:
            self.emit_error(f"Failed to unload plugin {plugin}: {e}")
            return False

    def register_start_up(self):
        """Checks the .ini file for saved settings and registers all plugins that are set to load on startup."""
        self.config = ConfigParser()
        self.config.read(self.path + self.configFileName)
        # FIXME: Naive implementation. If a pluginload fails on startup, it's not retried. This makes it possible for the user™ to break something.
        for plugin in self.config.sections():
            # sections contain at least _settings and _plugin, extract the ones that are plugins:
            _, type = plugin.rsplit("_", 1)
            if type == "plugin":
                if self.config[plugin]["load"] == "True":
                    self._register(plugin)

        # everything is loaded, exchange public functions
        self.public_function_exchange()
        self.plugins_updated_signal.emit()
        self.cleanup()

    def public_function_exchange(self):
        # Get all the plugin public functions by plugin name
        if self.pm.list_name_plugin() == []:
            return  # No plugins registered, nothing to do
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

        self.pm.hook.set_function(function_dict=function_map)
        self.seqComponents_signal.emit(self.get_plugin_dict(), plugin_public_functions)

        # pass plugin references around
        plugin_list = self.pm.hook.get_plugin()
        if self.debug:
            print("Available plugin objects in public_function_exchange: ", plugin_list)
        self.pm.hook.set_plugin(plugin_list=plugin_list)

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
        dependencies to the list of plugins to activate only when no plugins of that type are already registered.

        Args:
            plugins_to_activate (list): plugins to be activated, format: x_plugin (section name in the ini file)

        Returns:
            list: updated loading list, format: x_plugin (section name in the ini file)
        """

        def resolve_dependencies(plugin, seen):
            """Recursion helper to find the dependencies of dependencies."""
            if plugin in seen:
                return  # Stop when seeing an already seen plugin
            seen.add(plugin)
            dependencies = self.config[plugin].get("dependencies", "").split(",")
            if self.debug:
                print(f"Checking dependencies for {plugin}: {dependencies}")

            for dependency in filter(None, dependencies):  # Filter out empties
                for section in self.config.sections():
                    name, type = section.rsplit("_", 1)
                    # If type is plugin and fulfills the dependency
                    if type == "plugin" and self.config[section].get("function") == dependency:
                        # Check if any plugin of this type is already registered
                        active_plugins_of_type = [
                            sec
                            for sec in self.config.sections()
                            if sec.rsplit("_", 1)[1] == "plugin"
                            and self.config[sec].get("function") == dependency
                            and self.pm.get_plugin(self.config[sec]["name"]) is not None
                        ]

                        # Add dependency only if no active plugins of this type exist
                        if not active_plugins_of_type and section not in plugins_to_activate:
                            plugins_to_activate.append(section)
                            added_deps.append(name)
                            resolve_dependencies(section, seen)

        added_deps = []
        seen = set()

        if self.debug:
            print("Checking dependencies for: ", plugins_to_activate)

        for plugin in plugins_to_activate.copy():
            resolve_dependencies(plugin, seen)

        if added_deps:
            self.emit_log(f"Added dependencies: {', '.join(added_deps)}")

        return plugins_to_activate

    def _check_dependencies_unregister(self, plugin: str) -> tuple[bool, str]:
        """Checks if the plugin can be unregistered based on dependencies and type.

        Args:
            plugin (str): name of the plugin being unregistered, format: x_plugin (section name in the ini file)

        Returns:
            tuple[bool, str]: is a dependency, dependent plugin name in format x_plugin
        """
        plugin_type = self.config[plugin]["function"]

        # Check if the plugin is the last of its type
        active_plugins_of_type = [
            section
            for section in self.config.sections()
            if section.rsplit("_", 1)[1] == "plugin"
            and self.config[section].get("function") == plugin_type
            and self.pm.get_plugin(self.config[section]["name"]) is not None
        ]

        is_last_of_type = len(active_plugins_of_type) == 1

        # Check if any other registered plugin depends on this type of plugin
        for section in self.config.sections():
            if section == plugin:
                continue  # Skip checking the plugin against itself
            if section.rsplit("_", 1)[1] == "plugin":
                name = self.config[section]["name"]
                if self.pm.get_plugin(name) is not None:
                    dependencies = self.config[section].get("dependencies", "").split(",")
                    if plugin_type in dependencies:
                        # If this is the last plugin of its type, return True and the dependent plugin
                        if is_last_of_type:
                            return True, section

        # If there are other plugins of the same type, unregistration is not conflicted
        return False, ""

    def __init__(self, config_file_name: str | None = None):
        """initializes the container and the plugin manager. Reads the config file and registers all plugins set to load on startup."""
        super().__init__()
        if config_file_name is None:
            self.configFileName = self.configFileName
        else:
            self.configFileName = config_file_name
        self.path = dirname(__file__) + sep
        sys.path.append(self.path + "plugins" + sep)
        self.pm = pluggy.PluginManager("pyIVLS")
        self.pm.add_hookspecs(pyIVLS_hookspec)
        self.debug = False

    def cleanup(self) -> None:
        """Explicitly cleanup resources, such as writing the config file."""
        config_path = self.path + self.configFileName
        with open(config_path, "w") as configfile:
            self.config.write(configfile)
