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

class pyIVLS_container(QObject):
  
  #### Signals for communication
  available_plugins_signal = pyqtSignal(dict)

  #### Slots for communication 
  @pyqtSlot()
  def read_available_plugins(self):
    self.available_plugins_signal.emit(self.getPluginDict())
    #old
    #keys = list(self.getPluginDict().keys())
    #self.available_plugins_signal.emit(keys)

  def getPluginInfoFromSettings(self):
#     inData = [None]*pyRTA_constants.positionsSettings
#     parser = SafeConfigParser()
#     parser.read(self.path+pyIVLS_constants.configFileName)
#     inData[pyIVLS_constants.plugins_num] = parser.get('Plugins', 'num').lstrip()
#     inData[pyIVLS_constants.plugins_num] = parser.get('Plugins', 'num').lstrip()

#     with open(self.path+pyIVLS_constants.configFileName, 'w') as configfile:
#          parser.write(configfile)


     
    """
    for plugin in load_these_dict: 
       if load_these_dict[plugin]:
            exec(f'from plugins.pyIVLS_{plugin} import pyIVLS_{plugin}_plugin')
            exec(f'self.pm.register(pyIVLS_{plugin}_plugin())')
    
  
  
    thisdict = {'type':'device', "model": "Mustang", "year": 1964}
    return self.pm.hook.get_setup_interface(kwargs = thisdict)[0]
    """
  
  # FIXME: figure out if this is the most reasonable way to do this.
  def getPluginDict(self) -> dict:
    parser = self.config
    parser.read(self.path+pyIVLS_constants.configFileName)  # FIXME: check the path to be better
    # Extract the number of plugins
    num_plugins = parser.getint('Plugins', 'num')
    
    # Extract plugin names
    plugins = []
    for i in range(1, num_plugins + 1):
        plugin_key = f'plugin{i}'
        plugin_name = parser.get('Plugins', plugin_key)
        plugins.append(plugin_name)

    pluginDict = {}

    for plugin in plugins:
      if plugin in parser.sections():
        pluginDict[plugin] = dict(parser.items(plugin))

    return pluginDict
  
  def setRegistered(self, active: list):
    for plugin in self.currentConfig:
      if plugin in active:
        if self.currentConfig[plugin]['load'] == 'False':
            exec(f'from plugins.pyIVLS_{plugin} import pyIVLS_{plugin}_plugin')
            exec(f'self.pm.register(pyIVLS_{plugin}_plugin())')
  

  # This could just use .is_registered() from pluggy
  def _register(self, plugin: str):
    assert plugin in self.config.sections(), f"Error: Plugin {plugin} not found in the .ini file"
    if self.config[plugin]['load'] == 'False':
      try:
          # Dynamic import using importlib
          module_name = f'plugins.pyIVLS_{plugin}'
          class_name = f'pyIVLS_{plugin}_plugin'
          module = importlib.import_module(module_name)
          plugin_class = getattr(module, class_name)
          self.pm.register(plugin_class())

          self.config[plugin]['load'] = 'True'
      except (ModuleNotFoundError, AttributeError) as e:
          print(f"Error loading plugin {plugin}: {e}")
    
  # This could just use .is_registered() from pluggy
  def _unregister(self, plugin: str):
    assert plugin in self.config.sections(), f"Error: Plugin {plugin} not found in the .ini file"
    if self.config[plugin]['load'] == 'True':
      try:
          class_name = f'pyIVLS_{plugin}_plugin'
          self.pm.register(f"{class_name}()")
          self.config[plugin]['load'] = 'False'

      except (ModuleNotFoundError, AttributeError) as e:
          print(f"Error unloading plugin {plugin}: {e}")
    
  def registerStartUp(self):
    for plugin in self.config.sections():
      if self.config[plugin]['load'] == 'True':
        self._register(plugin)

  def updatePluginRegistration(self, pluginsToActivate: list):
    for plugin in self.config.sections():
      if plugin in pluginsToActivate:
        self._register(plugin)
      else:
        self._unregister(plugin)

  def __init__(self):
    super().__init__()
    self.path = dirname(__file__) + sep 

    self.pm = pluggy.PluginManager("pyIVLS")
    self.pm.add_hookspecs(pyIVLS_hookspec)
    
    self.config = SafeConfigParser()
    self.config.read(self.path+pyIVLS_constants.configFileName)

  def __del__(self):
    with open(self.path+pyIVLS_constants.configFileName, 'w') as configfile:
      self.config.write(configfile)