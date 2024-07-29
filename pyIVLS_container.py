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

  @pyqtSlot(list)
  def update_registration(self, pluginsToActivate: list):
    for plugin in self.config.sections():
      if plugin in pluginsToActivate:
        self._register(plugin)
      else:
        self._unregister(plugin)

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
  
  def getPluginDict(self) -> dict:    
    # Extract plugin names
    section_dict = {}
    
    # Iterate through all sections in the parser
    for section in self.config.sections():
        section_dict[section] = dict(self.config.items(section))
    
    return section_dict
  
  def _register(self, plugin: str):
    assert plugin in self.config.sections(), f"Error: Plugin {plugin} not found in the .ini file"
    module_name = f'plugins.pyIVLS_{plugin}'
    class_name = f'pyIVLS_{plugin}_plugin'
    if not self.pm.is_registered(f"{class_name}()"): 
      try:
          self.check_dependencies(plugin)
          # Dynamic import using importlib
          module = importlib.import_module(module_name)
          self.pm.register(f"{class_name}()")
          self.config[plugin]['load'] = 'True'
          print(f"Plugin {plugin} loaded")

      except (ModuleNotFoundError, AttributeError) as e:
          print(f"Error loading plugin {plugin}: {e}")
    
  def _unregister(self, plugin: str):
    assert plugin in self.config.sections(), f"Error: Plugin {plugin} not found in the .ini file"
    class_name = f'pyIVLS_{plugin}_plugin'
    if self.pm.is_registered(f"{class_name}()"): 
      try:
        self.pm.unregister(f"{class_name}()")
        self.config[plugin]['load'] = 'False'
        print(f"Plugin {plugin} unloaded")

      except (ModuleNotFoundError, AttributeError) as e:
          print(f"Error unloading plugin {plugin}: {e}")
    
  def registerStartUp(self):
    for plugin in self.config.sections():
      if self.config[plugin]['load'] == 'True':
        self._register(plugin)

  def check_dependencies(self, plugin: str):
    """Registers the necessary dependencies for a plugin

    Args:
        plugin (str): plugin name
    """
    assert plugin in self.config.sections(), f"Error: Plugin {plugin} not found in the .ini file"
    try:
      dependencies = self.config[plugin]['dependencies'].split(',')
      for dependency in dependencies:
        if not self.pm.is_registered(f"pyIVLS_{dependency}_plugin()"):
          self._register(dependency)
    except KeyError:
      pass

  def __init__(self):
    super().__init__()
    self.path = dirname(__file__) + sep 

    self.pm = pluggy.PluginManager("pyIVLS")
    self.pm.add_hookspecs(pyIVLS_hookspec)
    
    self.config = SafeConfigParser()
    self.config.read(self.path+pyIVLS_constants.configFileName)
    self.registerStartUp()

  def __del__(self):
    with open(self.path+pyIVLS_constants.configFileName, 'w') as configfile:
      self.config.write(configfile)