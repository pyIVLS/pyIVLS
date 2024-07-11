#!/usr/bin/python3.8
import sys
from os.path import dirname, sep

from configparser import SafeConfigParser
import pluggy
from plugins.pyIVLS_hookspec import pyIVLS_hookspec

import pyIVLS_constants


class pyIVLS_container():

  def getPluginInfoFromSettings(self):
#     inData = [None]*pyRTA_constants.positionsSettings
#     parser = SafeConfigParser()
#     parser.read(self.path+pyIVLS_constants.configFileName)
#     inData[pyIVLS_constants.plugins_num] = parser.get('Plugins', 'num').lstrip()
#     inData[pyIVLS_constants.plugins_num] = parser.get('Plugins', 'num').lstrip()

#     with open(self.path+pyIVLS_constants.configFileName, 'w') as configfile:
#          parser.write(configfile)

    plugin_name = 'pyIVLS_Keithley_plugin'
    #from plugins.pyIVLS_Keithley import pyIVLS_Keithley_plugin
    exec('from plugins.pyIVLS_Keithley import ' + plugin_name)
    exec('self.pm.register(' + plugin_name + '())')


    thisdict = {'type':'device', "model": "Mustang", "year": 1964}
    return self.pm.hook.get_setup_interface(kwargs = thisdict)[0]

  def __init__(self):
    super(pyIVLS_container,self).__init__()
    self.path = dirname(__file__) + sep 

    self.pm = pluggy.PluginManager("pyIVLS")
    self.pm.add_hookspecs(pyIVLS_hookspec)

