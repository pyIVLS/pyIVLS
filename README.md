#### Changelog
# 1. MDI area added to MainWindow (will be used for vizualization)
# 2. Device plugins are separated into the GUI and core parts. The main idea of separation is to be able to use core without the GUI
# 3. pyIVLS are not any more descendents of plugin class. Mainly it is done because the public functions should be provided by GUI classes, but not by the plugin itself. As a benefit, requirements to the plugin names are removed
# 4. Some GUI clases may now be descendents of QObject as they may need to emit signals for logging (see note on logging and error messaging)
# 5. Changed the structure of ini file, now it allows to save plugin settings
# 6. class option is added to the plugin descriptor in the ini file. This is related to suggested implementation of the built-in functionality of run and address selection. (class = step for measurement, class = loop for looping the steps, class = none for support plugins not directly used in recipe)
# 7. Execution flow is modified to allow to add messages from pluginContainer to log. Message slot from pluginloader is removed, info signal from plugin container is connected to the message slot in pyIVLS_GUI, as for all the other information windows.

#### TODO list
# 1. add settings validation to GUI (partially done)
# 2. add settings locking/unlocking to GUI (partially done)
# 3. implement logging (at the moment log signals are collected from plugins and in pyIVLS.py connected to a addDataLog slot in pyIVLS_GUI.py)
# 4. remove constants file. The info from it may be moved to the plugin settings.
# 5. implement saving of settings to configuration file
# 6. implement reopening of docking window and MDI windows
# 7. implement autosave for long measurements
# 8. implement close check, i.e. the main GUI window can not be closed if a measuremen or preview is running
# 9. implement loading/saving of *.ini file this should allow to save/load certain measurement configurations
# 10. modify _get_public_methods in plugins. Now it returns also quit some subfunctions from dependent modules (e.g. for VenusUSB2). It may be reasonable to create a list with name of the methods to be exported, if the method name is in the list if will be processed by this function
# 11. implement GUI for adding/removing plugins. This should take care that plugin info in *.ini (i.e. name, class, function. etc) corresponds to info in plugin itself
# 12. implement measurement run and address selection for data saving as a built-in functionality. A temporary workaround is the use of plugings with function = sequence
##      For the final realization the main window may have another docking window (recipe editor), where measurement recipies may be created. A reciepe will replace sequence plugins. A reciepe may be a combination of measurement (e.g. sweep, TLCCS) and loop scripts (e.g. Affine, peltier),
##      this may require introduction of new/replacement of plugin type/function classification, as the recipe editor should know what plugins allow looping, and what are just direct measurements. Also looping interface should be thought through.

#### plugin specific TODO lists
######### VenusUSB2
####	Implement manipulation of the image (size change, digital zoom, etc.). May be reasonable to thing about changing integration time without stopping the preview
######### runSweep
####	Stop button

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
#11. python3 -m pip install pathvalidate # required for sequenceces
#12. python3 -m pip install pyserial # required for peltierController, senseMultiplexer, etc.
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
#
## peltierController
# the device is detected as 1a86:7523 QinHeng Electronics CH340 serial converter. To provide access to /dev/ttyUSB0 add user to dialout group
#sudo usermod -a -G dialout $USER

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
# in case of sweep only run sweep plugin should save to the log and show messages to the user. All other plugins communicate to the sweep plugin, e.g. with returned status of the functions.
# This is necessary to avoid multiple messaging
## standard error codes
#0 = no error, 1 = Value error, 2 = Any error reported by dependent plugin, 3 = missing functions or plugins, 4 = harware error
##plugins return errors in form of list [number, {"Error message":"Error text"}], e.g. [1, {"Error message":"Value error in sweep plugin: SMU limit prescaler field should be numeric"}]
#error text will be shown in the dialog message in the interaction plugin, so the error text should contain the plugin name, e.g. return [1, {"Error message":"Value error in Keithley plugin: drain nplc field should be numeric"}]
##intermidiate plugins should pass the error to the plugins that interract with users as is, just changing the error code
#e.g.return [2, self.smu_settings]
##the plugin interracting with user adds to the log it's own name, and name of the plugin that transmitted this error 
#(not the name of original plugin, that's why the message should contain the original plugin name, as if there will be multiple intermediate plugins some of the plugin names may be dropped)
#e.g. self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f' : runsweep : the sweep plugin reported an error: {self.sweep_settings["Error message"]}')

#### execution flow
#1. When pyIVLS.py is run it creates an instance of the pyIVLS_container.py (handles all the plugins) and the main window
##	signals (including log and user message) from pyIVLS_container.py and pyIVLS_pluginloader are connected to respective slots
#2. register_start_up of pyIVLS_container.py is called
##	reads plugin data from ini
##	registers the plugins marked for loading in ini (_register function)
#3. pyIVLS.py makes initialization of main slots and signals between plugin container and GUI. This includes connecting signals from plugins to the main window
##      log signals from plugins is connected to slot addDataLog in pyIVLS_GUI.py
##      info signals from plugins are connectend to slot show_message in pyIVLS_GUI.py
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
