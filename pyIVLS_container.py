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

# FIXME: Debug
from plugins.pyIVLS_VenusUSB2 import pyIVLS_VenusUSB2_plugin
from plugins.pyIVLS_Keithley2612B import pyIVLS_Keithley2612B_plugin


class pyIVLS_container(QObject):

    #### Signals for communication
    available_plugins_signal = pyqtSignal(dict)
    plugins_updated_signal = pyqtSignal()

    #### Slots for communication
    @pyqtSlot()
    def read_available_plugins(self):
        self.available_plugins_signal.emit(self.getPluginDict())

    @pyqtSlot(list)
    def update_registration(self, pluginsToActivate: list):
        for plugin in self.config.sections():
            if plugin in pluginsToActivate:
                self._register(plugin)
            else:
                self._unregister(plugin)
        self.plugins_updated_signal.emit()

    def getPluginInfoFromSettings(self):
        #     inData = [None]*pyRTA_constants.positionsSettings
        #     parser = SafeConfigParser()
        #     parser.read(self.path+pyIVLS_constants.configFileName)
        #     inData[pyIVLS_constants.plugins_num] = parser.get('Plugins', 'num').lstrip()
        #     inData[pyIVLS_constants.plugins_num] = parser.get('Plugins', 'num').lstrip()

        #     with open(self.path+pyIVLS_constants.configFileName, 'w') as configfile:
        #          parser.write(configfile)

        return_v = self.pm.hook.get_setup_interface()
        print(f"Inside the container, this is what i got: {return_v}")
        return return_v

    def getPluginDict(self) -> dict:
        # Extract plugin names
        section_dict = {}

        # Iterate through all sections in the parser
        for section in self.config.sections():
            section_dict[section] = dict(self.config.items(section))

        return section_dict

    def _register(self, plugin: str):
        module_name = f"plugins.pyIVLS_{plugin}"
        class_name = f"pyIVLS_{plugin}_plugin()"
        if not self.pm.is_registered(class_name):
            # Dynamic import using importlib
            module = importlib.import_module(module_name)
            self.pm.register(class_name)
            self.config[plugin]["load"] = "True"
            print(f"Plugin {plugin} loaded")



    def _unregister(self, plugin: str):
        class_name = f"pyIVLS_{plugin}_plugin()"
        if self.pm.is_registered(class_name):
            self.pm.unregister(class_name)
            self.config[plugin]["load"] = "False"
            print(f"Plugin {plugin} unloaded")


    def registerStartUp(self):
        for plugin in self.config.sections():
            if self.config[plugin]["load"] == "True":
                self._register(plugin)

    # FIXME: Does not handle cases where a dependency is not found or when a dependence is unloaded.
    def check_dependencies(self, plugin: str):
        """Registers the necessary dependencies for a plugin

        Args:
            plugin (str): plugin name
        """
        assert (
            plugin in self.config.sections()
        ), f"Error: Plugin {plugin} not found in the .ini file"
        try:
            dependencies = self.config[plugin]["dependencies"].split(",")
            for dependency in dependencies:
                if not self.pm.is_registered(f"pyIVLS_{dependency}_plugin()"):
                    self._register(dependency)
        except KeyError:
            pass


    def is_registered(self, plugin: str) -> bool:
        return self.pm.is_registered(f"pyIVLS_{plugin}_plugin()")

    def __init__(self):
        super(pyIVLS_container, self).__init__()
        self.path = dirname(__file__) + sep

        self.pm = pluggy.PluginManager("pyIVLS")
        self.pm.add_hookspecs(pyIVLS_hookspec)
        
        # FIXME: DEBUG
        # self.pm.register(pyIVLS_VenusUSB2_plugin())
        
        self.config = SafeConfigParser()
        self.config.read(self.path + pyIVLS_constants.configFileName)

    def __del__(self):
        with open(self.path + pyIVLS_constants.configFileName, "w") as configfile:
            self.config.write(configfile)
        