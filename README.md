#### Changelog
# 1. MDI area added to MainWindow (will be used for vizualization)
# 2. Device plugins are separated into the GUI and core parts. The main idea of separation is to be able to use core without the GUI
# 3. pyIVLS are not any more descendents of plugin class. Mainly it is done because the public functions should be provided by GUI classes, but not by the plugin itself. As a benefit, requirements to the plugin names are removed
# 4. GUI clases are now descendents of QObject as they need to emit signals for logging (and probably for warnings in future implementations)
# 5. Changed the structure of ini file, now it allows to save plugin settings

#### TODO list
# 1. add settings validation to GUI
# 2. add settings locking/unlocking to GUI
# 3. implement logging (at the moment log signals are collected from plugins and in pyIVLS.py connected to a addDataLog slot in pyIVLS_GUI.py)
# 4. implement warning messaging
# 5. implement saving of settings to configuration file
# 6. implement reopening of docking window and MDI windows
# 7. implement autosave for long measurements

#### install (Ubuntu 24.04.1 LTS)
# 1. python3 -m venv .venv
# 2. source .venv/bin/activate
# 3. python3 -m pip install pyqt6
# 4. python3 -m pip install pluggy
## if pyvisa needed, e.g. Keithley via eth
# 5. python3 -m pip install pyvisa
# 5a. python3 -m pip install pyvisa_py
# 5b. python3 -m pip install psutil # required to supress some warnings
# 5c. python3 -m pip install zeroconf  # required to supress some warnings
## if usbtmc is needed, e.g. Keithley via USB
# 6. python3 -m pip install pyhton-usbtmc
# 6a. python3 -m pip install PyUSB # required for usbtmc
# 7. python3 -m pip install numpy
## if cameras are needed
# 8. python3 -m pip install opencv-python
# 9. python3 -m pip install matplotlib
#10. python3 -m pip install datetime
# deactivate

# change the first line of pyIVLS.py to address the virual environment 
## e.g.#!/home/ivls/git_pyIVLS/pyIVLS/.venv/bin/python3
#run with
## ./pyIVLS.py

#### settings for hardware discovery
# to avoid running the script as superused some rules needs to be created
# check https://github.com/python-ivi/python-usbtmc for details
# example of /etc/udev/rules.d for Ubuntu 24.04.1 LTS to run Keithley 2612B
#begin of /etc/udev/rules.d
## USBTMC instruments
#
## Keithley2612B
#SUBSYSTEMS=="usb", ACTION=="add", ATTRS{idVendor}=="05e6", ATTRS{idProduct}=="2612", GROUP="usbtmc", MODE="0660"
#end of of /etc/udev/rules.d
# In case of using this approach: the group must exist, the user running the script should be member of the group. 
# Example for creating the group and adding the user
##sudo groupadd usbtmc
##sudo usermod -a -G usbtmc ivls

#### plugin conventions
# 1. Every plugin  consists of a couple of files. 
#	pyIVLS_name.py - implementation of the pluggy interface
#	nameGUI.py - a GUI widget for setting and controlling the core. Together with core implementation may be reused in another GUI software
#	name.py - core implementation. May be reused without GUI
# 2. The plugins should be registered in pyIVLS_container
#	if a plugin should be loaded, it is done in pyIVLS_container:_register. This creates an instance of pyIVLS_*.py class
#	pyIVLS_*.py in its initialization creates an instance of *GUI.py
#	*GUI.py in its initialization creates an instanse of the core class and loads GUI

#### logging and error messaging
# Logs messages and info messages for user should be sent only by the plugin that directly interracts with the user, i.e.
# in case of sweep only sweep plugin should save to the log and show messages to the user. All other plugins communicate to the sweep plugin, e.g. with returned status of the functions.
# This is necessary to avoid multiple messaging

#### execution flow
#1. When pyIVLS.py is run it creates an instance of the pyIVLS_container.py (handles all the plugins) and the main window
##2. In the initialization the pyIVLS_container.py 
##	reads plugin data from ini
##	registers the plugins marked for loading in ini (_register function)
#3. pyIVLS.py makes initialization of main slots and signals between plugin container and GUI. This includes connecting signals from plugins to the main window
#4. pyIVLS.py calls a public_function_exchange() from pyIVLS_container.py to provide functions from dependency plugins to the plugins that require them
#5. pyIVLS.py calls get_plugin_info_for_settingsGUI() for adding settings widgets to main GUI window
##6. get_plugin_info_for_settingsGUI() is implemented in pyIVLS_container.py  
##		it initializes plugin dictionaries with data from ini file in get_plugin_dict()
##		it requests the settings widgets get_setup_interface() hook implementation
###7.	get_setup_interface() is implementsd in pyIVLS_*.py plugin file
###		it initilizes the plugin_info variable of pyIVLS_*.py (the variable is initialized in setup of parent plugin.py class)
###		it calls the initGUI function of the *GUI.py class, that initializes the GUI with values obtained from ini (the data from ini is not checked, checking will happen at execution of plugin functionality)		
###		it returns the dictionary containg settingsWidget property of the *GUI.py class
#8. pyIVLS.py transfers the obtained dictionary to the main window class for setting up the settings widgets
#9. pyIVLS.py calls get_plugin_info_for_MDIarea() for adding MDI windows to main GUI window MDI area
##10. get_plugin_info_for_MDIarea() is implemented in pyIVLS_container.py
##	it requests the MDI windows with get_MDI_interface() hook implementation
###11. with get_MDI_interface() is implemented in pyIVLS_*.py plugin file
