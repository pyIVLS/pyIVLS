import sys
import os
import time
from threading import Lock
#from Keithley2612B_test import Keithley2612B
from Keithley2612B import Keithley2612B

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QCheckBox,
    QComboBox,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QLabel,
)

import pyvisa
import numpy as np
import time

import pyIVLS_constants

'''
            settings dictionary for class
            
            
		# settings["channel"] source channel: may take values [smua, smub]
		# settings["inject"] source type: may take values [current, voltage]
		# settings["mode"] pulse/continuous operation: may take values [continuous, pulsed, mixed]
		# settings["continuousdelaymode"] stabilization time before measurement for continuous sweep: may take values [auto, manual]
		# settings["pulseddelaymode"] stabilization time before measurement for pulsed sweep: may take values [auto, manual]
		# settings["draindelaymode"] stabilization time before measurement for drain channel: may take values [auto, manual]
		# settings["sourcesensemode"] source sence mode: may take values [2 wire, 4 wire, 2 & 4 wire]		
		# settings["drainsensemode"] drain sence mode: may take values [2 wire, 4 wire, 2 & 4 wire]
		# settings["singlechannel"] single channel mode: may be True or False
		# settings["sourcehighc"] HighC mode for source: may be True or False        
		# settings["repeat"] repeat count: should be int >0
		# settings for continuous mode
		## settings["continuousstart"] start point
		## settings["continuousend"] end point
		## settings["continuouspoints"] number of points
		## settings["continuouslimit"] limit for current in voltage mode or for voltage in current mode
		## settings["continuousnplc"] integration time in nplc units
		## settings["continuousdelay"] stabilization time before the measurement
		# settings for pulsed mode
		## settings["pulsedstart"] start point
		## settings["pulsedend"] end point
		## settings["pulsedpoints"] number of points
		## settings["pulsedlimit"] limit for current in voltage mode or for voltage in current mode
		## settings["pulsednplc"] integration time in nplc units
		## settings["pulseddelay"] stabilization time before the measurement
		## settings["pulsepause"] pase between the pulses
		# settings for drain
		## settings["drainstart"] start point
		## settings["drainend"] end point
		## settings["drainpoints"] number of points should be not zero. If equals to 1 only the start point is used
		## settings["drainlimit"] limit for current in voltage mode or for voltage in current mode
		## settings["drainnplc"] integration time in nplc units
		## settings["draindelay"] stabilization time before the measurement
		## settings["drainhighc"] HighC mode for drain: may be True or False  


'''

class Keithley2612BGUI:
    """GUI for Keithley2612B"""
    non_public_methods = [] # add function names here, if they should not be exported as public to another plugins

    ####################################  threads

    ################################### internal functions

    ########Slots

    ########Signals

    ########Functions
    def __init__(self):

        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        self.settingsWidget = uic.loadUi(self.path + "Keithley2612B_settingsWidget.ui")

        # Initialize Keithley module
        ##IRtodo#### move Keithley address to GUI
        self.smu = Keithley2612B(pyIVLS_constants.KEITHLEY_tcmp, dbg_mode=True)
        self._connect_signals()
        self.settings = {}

    def _connect_signals(self):
        # Connect the channel combobox
        self.settingsWidget.comboBox_mode.currentIndexChanged.connect(self._mode_changed)

        # Connect the inject type combobox
        inject_box = self.settingsWidget.findChild(QComboBox, "comboBox_inject")
        inject_box.currentIndexChanged.connect(self._inject_changed)

        delay_continuous = self.settingsWidget.findChild(
            QComboBox, "comboBox_continuousDelayMode"
        )
        delay_pulsed = self.settingsWidget.findChild(
            QComboBox, "comboBox_pulsedDelayMode"
        )
        delay_drain = self.settingsWidget.findChild(
            QComboBox, "comboBox_drainDelayMode"
        )

        delay_continuous.currentIndexChanged.connect(self._delay_continuous_mode_changed)
        delay_pulsed.currentIndexChanged.connect(self._delay_pulsed_mode_changed)
        delay_drain.currentIndexChanged.connect(self._delay_drain_mode_changed)

        self.settingsWidget.checkBox_singleChannel.stateChanged.connect(self._single_channel_changed)

########Functions
###############GUI setting up

    def _initGUI(self, plugin_info:"dictionary with settings obtained from plugin_data in pyIVLS_*_plugin"):
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK
        if plugin_info["singlechannel"] == "True":
            self.settingsWidget.checkBox_singleChannel.setChecked(True)
        if plugin_info["sourcehighc"] == 'True':
            self.settingsWidget.checkBox_sourceHighC.setChecked(True)
        if plugin_info["drainhighc"] == 'True':
            self.settingsWidget.checkBox_drainHighC.setChecked(True)
        currentIndex = self.settingsWidget.comboBox_channel.findText(plugin_info["channel"], Qt.MatchFlag.MatchFixedString)
        if currentIndex > -1:
           self.settingsWidget.comboBox_channel.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_inject.findText(plugin_info["inject"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_inject.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_mode.findText(plugin_info["mode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_mode.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_continuousDelayMode.findText(plugin_info["continuousdelaymode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_continuousDelayMode.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_pulsedDelayMode.findText(plugin_info["pulseddelaymode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_pulsedDelayMode.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_drainDelayMode.findText(plugin_info["draindelaymode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_drainDelayMode.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_sourceSenseMode.findText(plugin_info["sourcesensemode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_sourceSenseMode.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_drainSenseMode.findText(plugin_info["drainsensemode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_drainSenseMode.setCurrentIndex(currentIndex)
        self.settingsWidget.lineEdit_repeat.setText(plugin_info["repeat"])
        self.settingsWidget.lineEdit_continuousStart.setText(plugin_info["continuousstart"])
        self.settingsWidget.lineEdit_continuousEnd.setText(plugin_info["continuousend"])
        self.settingsWidget.lineEdit_continuousPoints.setText(plugin_info["continuouspoints"])
        self.settingsWidget.lineEdit_continuousLimit.setText(plugin_info["continuouslimit"])
        self.settingsWidget.lineEdit_continuousNPLC.setText(plugin_info["continuousnplc"])
        self.settingsWidget.lineEdit_continuousDelay.setText(plugin_info["continuousdelay"])
        self.settingsWidget.lineEdit_pulsedStart.setText(plugin_info["pulsedstart"])
        self.settingsWidget.lineEdit_pulsedEnd.setText(plugin_info["pulsedend"])
        self.settingsWidget.lineEdit_pulsedPoints.setText(plugin_info["pulsedpoints"])
        self.settingsWidget.lineEdit_pulsedLimit.setText(plugin_info["pulsedlimit"])
        self.settingsWidget.lineEdit_pulsedNPLC.setText(plugin_info["pulsednplc"])
        self.settingsWidget.lineEdit_pulsedPause.setText(plugin_info["pulsedpause"])
        self.settingsWidget.lineEdit_pulsedDelay.setText(plugin_info["pulseddelay"])
        self.settingsWidget.lineEdit_drainStart.setText(plugin_info["drainstart"])
        self.settingsWidget.lineEdit_drainEnd.setText(plugin_info["drainend"])
        self.settingsWidget.lineEdit_drainPoints.setText(plugin_info["drainpoints"])
        self.settingsWidget.lineEdit_drainLimit.setText(plugin_info["drainlimit"])
        self.settingsWidget.lineEdit_drainNPLC.setText(plugin_info["drainnplc"])
        self.settingsWidget.lineEdit_drainDelay.setText(plugin_info["draindelay"])

        # update to the correct GUI state
        self._update_GUI_state()

########Functions
###############GUI react to change
    def _update_GUI_state(self):
        self._mode_changed(self.settingsWidget.comboBox_mode.currentIndex())
        self._inject_changed(self.settingsWidget.comboBox_inject.currentIndex())
        self._delay_continuous_mode_changed(self.settingsWidget.comboBox_continuousDelayMode.currentIndex())
        self._delay_pulsed_mode_changed(self.settingsWidget.comboBox_pulsedDelayMode.currentIndex())
        self._delay_drain_mode_changed(self.settingsWidget.comboBox_drainDelayMode.currentIndex())

    def _mode_changed(self, index):
        """Handles the visibility of the mode input fields based on the selected mode."""
        group_continuous = self.settingsWidget.findChild(
            QWidget, "groupBox_continuousSweep"
        )
        group_pulsed = self.settingsWidget.findChild(QWidget, "groupBox_pulsedSweep")

        mode = self.settingsWidget.comboBox_mode.currentText()
        if mode == "Continuous":
            group_continuous.setEnabled(True)
            group_pulsed.setEnabled(False)
        elif mode == "Pulsed":
            group_continuous.setEnabled(False)
            group_pulsed.setEnabled(True)
        elif mode == "Mixed":
            group_continuous.setEnabled(True)
            group_pulsed.setEnabled(True)

        self.settingsWidget.update()

    def _inject_changed(self, index):
        """Changes the unit labels based on the selected injection type."""
        continuous_start_label = self.settingsWidget.findChild(
            QLabel, "label_continuousStartUnits"
        )
        pulse_start_label = self.settingsWidget.findChild(
            QLabel, "label_pulsedStartUnits"
        )
        drain_start_label = self.settingsWidget.findChild(
            QLabel, "label_drainStartUnits"
        )
        continuous_end_label = self.settingsWidget.findChild(
            QLabel, "label_continuousEndUnits"
        )

        pulse_end_label = self.settingsWidget.findChild(QLabel, "label_pulsedEndUnits")

        drain_end_label = self.settingsWidget.findChild(QLabel, "label_drainEndUnits")

        continuous_limit_label = self.settingsWidget.findChild(
            QLabel, "label_continuousLimitUnits"
        )
        pulse_limit_label = self.settingsWidget.findChild(
            QLabel, "label_pulsedLimitUnits"
        )
        drain_limit_label = self.settingsWidget.findChild(
            QLabel, "label_drainLimitUnits"
        )

        inject_type = self.settingsWidget.comboBox_inject.currentText()
        if inject_type == "Voltage":
            continuous_start_label.setText("V")
            pulse_start_label.setText("V")
            drain_start_label.setText("V")
            continuous_end_label.setText("V")
            pulse_end_label.setText("V")
            drain_end_label.setText("V")
            continuous_limit_label.setText("A")
            pulse_limit_label.setText("A")
            drain_limit_label.setText("A")
        else:
            continuous_start_label.setText("A")
            pulse_start_label.setText("A")
            drain_start_label.setText("A")
            continuous_end_label.setText("A")
            pulse_end_label.setText("A")
            drain_end_label.setText("A")
            continuous_limit_label.setText("V")
            pulse_limit_label.setText("V")
            drain_limit_label.setText("V")

    def _delay_continuous_mode_changed(self, index):
        """Handles the visibility of the delay input fields based on the selected mode."""
        if self.settingsWidget.comboBox_continuousDelayMode.currentText() == "Auto":
            self.settingsWidget.label_continuousDelay.setEnabled(False)
            self.settingsWidget.lineEdit_continuousDelay.setEnabled(False)
            self.settingsWidget.label_continuousDelayUnits.setEnabled(False)
        else:
            self.settingsWidget.label_continuousDelay.setEnabled(True)
            self.settingsWidget.lineEdit_continuousDelay.setEnabled(True)
            self.settingsWidget.label_continuousDelayUnits.setEnabled(True)

        self.settingsWidget.update()
        
    def _delay_pulsed_mode_changed(self, index):
        """Handles the visibility of the delay input fields based on the selected mode."""
        if self.settingsWidget.comboBox_pulsedDelayMode.currentText() == "Auto":
            self.settingsWidget.label_pulsedDelay.setEnabled(False)
            self.settingsWidget.lineEdit_pulsedDelay.setEnabled(False)
            self.settingsWidget.label_pulsedDelayUnits.setEnabled(False)
        else:
            self.settingsWidget.label_pulsedDelay.setEnabled(True)
            self.settingsWidget.lineEdit_pulsedDelay.setEnabled(True)
            self.settingsWidget.label_pulsedDelayUnits.setEnabled(True)

        self.settingsWidget.update()        

    def _delay_drain_mode_changed(self, index):
        """Handles the visibility of the delay input fields based on the selected mode."""
        if self.settingsWidget.comboBox_drainDelayMode.currentText() == "Auto":
            self.settingsWidget.label_drainDelay.setEnabled(False)
            self.settingsWidget.lineEdit_drainDelay.setEnabled(False)
            self.settingsWidget.label_drainDelayUnits.setEnabled(False)
        else:
            self.settingsWidget.label_drainDelay.setEnabled(True)
            self.settingsWidget.lineEdit_drainDelay.setEnabled(True)
            self.settingsWidget.label_drainDelayUnits.setEnabled(True)

        self.settingsWidget.update()

    def _single_channel_changed(self):
        """Handles the visibility of the drain input fields based use single chennel box"""
        if self.settingsWidget.checkBox_singleChannel.isChecked():
             self.settingsWidget.groupBox_drain.setEnabled(False)
             self.settingsWidget.groupBox_drainSweep.setEnabled(False)
        else:     
             self.settingsWidget.groupBox_drain.setEnabled(True)
             self.settingsWidget.groupBox_drainSweep.setEnabled(True)

        self.settingsWidget.update()

########Functions
########plugins interraction
    def _get_public_methods(self):
        """
        Returns a nested dictionary of public methods for the plugin
        """
        # if the plugin type matches the requested type, return the functions

        methods = {
            method: getattr(self, method)
            for method in dir(self)
            if callable(getattr(self, method))
            and not method.startswith("__")
            and not method.startswith("_")
            and method not in self.non_public_methods
        }
        return methods
        
########Functions to be used externally
###############get settings from GUI

    def parse_settings_widget(self):
        """Parses the settings widget for the Keithley. Extracts current values

        Returns [status, settings_dict]:
            status: 0 - no error, ~0 - error (add error code later on if needed)
            self.settings
        """       
        ##IRtothink#### this implementation requires that all settings (including those not needed for current sweep) to be good. This is not a bad thing, but might be an overkill. A possible implementation will be to use some default values that may be stored in plugin installation package
        
        if not "lineFreuency" in self.settings:
        	status, info = self.smu.getLineFrequency()
        	if status:
        		return [status, info]
        	else:
        		self.settings["lineFrequency"] = info
 
        # Determine source channel: may take values [smua, smub]
        self.settings["channel"] = (self.settingsWidget.comboBox_channel.currentText()).lower()
        # Determine source type: may take values [current, voltage]
        self.settings["inject"] = (self.settingsWidget.comboBox_inject.currentText()).lower()
        # Determine pulse/continuous mode: may take values [continuous, pulsed, mixed]
        self.settings["mode"] = (self.settingsWidget.comboBox_mode.currentText()).lower()
 	# Determine delay mode for continuous sweep: may take values [auto, manual]
        self.settings["continuousdelaymode"] = (self.settingsWidget.comboBox_continuousDelayMode.currentText()).lower()
        # Determine delay mode for pulsed sweep: may take values [auto, manual]
        self.settings["pulseddelaymode"] = (self.settingsWidget.comboBox_pulsedDelayMode.currentText()).lower()
        # Determine delay mode for drain: may take values [auto, manual]
        self.settings["draindelaymode"] = (self.settingsWidget.comboBox_drainDelayMode.currentText()).lower()
        # Determine source sence mode: may take values [2 wire, 4 wire, 2 & 4 wire]
        self.settings["sourcesensemode"] = (self.settingsWidget.comboBox_sourceSenseMode.currentText()).lower()
        # Determine drain sence mode: may take values [2 wire, 4 wire, 2 & 4 wire]
        self.settings["drainsensemode"] = (self.settingsWidget.comboBox_drainSenseMode.currentText()).lower()

	# Determine a single channel mode: may be True or False
        if self.settingsWidget.checkBox_singleChannel.isChecked():
        	self.settings["singlechannel"] = True
        else:	
	        self.settings["singlechannel"] = False
	# Determine a HighC mode for source: may be True or False        
        if self.settingsWidget.checkBox_sourceHighC.isChecked():
        	self.settings["sourcehighc"] = True
        else:	
	        self.settings["sourcehighc"] = False

        # Determine repeat count: should be int >0
        try:
        	self.settings["repeat"] = int(self.settingsWidget.lineEdit_repeat.text())
        except ValueError:
                        return [1, {"Error message":"Value error in Keithley plugin: repeat field should be integer"}]
        if self.settings["repeat"] <1:
                        return [1, {"Error message":"Value error in Keithley plugin: repeat field can not be less than 1"}]


        # Determine settings for continuous mode
        #start should be float
        try:
                        self.settings["continuousstart"] = float(self.settingsWidget.lineEdit_continuousStart.text())
        except ValueError:
                        return [1, {"Error message":"Value error in Keithley plugin: continuous start field should be numeric"}]
	        
        #end should be float
        try:
                        self.settings["continuousend"] = float(self.settingsWidget.lineEdit_continuousEnd.text())
        except ValueError:
                        return [1, {"Error message":"Value error in Keithley plugin: continuous end field should be numeric"}]
        
        #number of points should be int >0
        try:
                        self.settings["continuouspoints"] = int(self.settingsWidget.lineEdit_continuousPoints.text())
        except ValueError:
                        return [1, {"Error message":"Value error in Keithley plugin: continuous number of points field should be integer"}]
        if self.settings["continuouspoints"] <1:
                        return [1, {"Error message":"Value error in Keithley plugin: continuous number of points field can not be less than 1"}]

        #limit should be float >0
        try:
                        self.settings["continuouslimit"] = float(self.settingsWidget.lineEdit_continuousLimit.text())
        except ValueError:
                        return [1, {"Error message":"Value error in Keithley plugin: continuous limit field should be numeric"}]
        if self.settings["continuouslimit"] <=0:
                        return [1, {"Error message":"Value error in Keithley plugin: continuous limit field should be positive"}]

        #continuous nplc (in fact it is integration time for the measurement) is calculated from line frequency, should be float >0
        try:
                        self.settings["continuousnplc"] =  0.001 * self.settings["lineFrequency"] * float(self.settingsWidget.lineEdit_continuousNPLC.text())
        except ValueError:
                        return [1, {"Error message":"Value error in Keithley plugin: continuous nplc field should be numeric"}]
        if self.settings["continuousnplc"] <=0:
                        return [1, {"Error message":"Value error in Keithley plugin: continuous nplc field should be positive"}]

        #delay (in fact it is stabilization time before the measurement), for Keithley control should be in s in GUI is ms, should be >0
        try:
                                self.settings["continuousdelay"] =  float(self.settingsWidget.lineEdit_continuousDelay.text())/1000
        except ValueError:
                                return [1, {"Error message":"Value error in Keithley plugin: continuous delay field should be numeric"}]
        if self.settings["continuousdelay"] <=0:
                                return [1, {"Error message":"Value error in Keithley plugin: continuous delay field should be positive"}]	                

        # Determine settings for pulsed mode
        #start should be float
        try:
                        self.settings["pulsedstart"] = float(self.settingsWidget.lineEdit_pulsedStart.text())
        except ValueError:
                        return [1, {"Error message":"Value error in Keithley plugin: pulsed start field should be numeric"}]

        #end should be float
        try:
                        self.settings["pulsedend"] = float(self.settingsWidget.lineEdit_pulsedEnd.text())
        except ValueError:
                        return [1, {"Error message":"Value error in Keithley plugin: pulsed end field should be numeric"}]
	        
        #number of points should be int >0
        try:
                        self.settings["pulsedpoints"] = int(self.settingsWidget.lineEdit_pulsedPoints.text())
        except ValueError:
                        return [1, {"Error message":"Value error in Keithley plugin: pulsed number of points field should be integer"}]
        if self.settings["pulsedpoints"] <1:
                        return [1, {"Error message":"Value error in Keithley plugin: pulsed number of points field can not be less than 1"}]

        #limit should be float >0
        try:
                        self.settings["pulsedlimit"] = float(self.settingsWidget.lineEdit_pulsedLimit.text())
        except ValueError:
                        return [1, {"Error message":"Value error in Keithley plugin: pulsed limit field should be numeric"}]
        if self.settings["pulsedlimit"] <=0:
                        return [1, {"Error message":"Value error in Keithley plugin: pulsed limit field should be positive"}]
                        
        #pulsed nplc (in fact it is integration time for the measurement) is calculated from line frequency, should be float >0
        try:
                        self.settings["pulsednplc"] = 0.001 * self.settings["lineFrequency"] * float(self.settingsWidget.lineEdit_pulsedNPLC.text())
        except ValueError:
                        return [1, {"Error message":"Value error in Keithley plugin: pulsed nplc field should be numeric"}]
        if self.settings["pulsednplc"] <=0:
                        return [1, {"Error message":"Value error in Keithley plugin: pulsed nplc field should be positive"}]

        #delay (in fact it is stabilization time before the measurement), for Keithley control should be in s in GUI is ms, should be >0
        try:
                                self.settings["pulseddelay"] = float(self.settingsWidget.lineEdit_pulsedDelay.text())/1000
        except ValueError:
                                return [1, {"Error message":"Value error in Keithley plugin: pulsed delay field should be numeric"}]
        if self.settings["pulseddelay"] <=0:
                                return [1, {"Error message":"Value error in Keithley plugin: pulsed delay field should be positive"}]        

        #pause between pulses should be >0
        try:
                        self.settings["pulsepause"] = float(self.settingsWidget.lineEdit_pulsedPause.text())
        except ValueError:
                        return [1, {"Error message":"Value error in Keithley plugin: pulse pause field should be numeric"}]
        if self.settings["pulsepause"] <=0:
                        return [1, {"Error message":"Value error in Keithley plugin: pulse pause field should be positive"}]

        # Determine settings for drain mode
        #start should be float
        try:
                        self.settings["drainstart"] = float(self.settingsWidget.lineEdit_drainStart.text())
        except ValueError:
                        return [1, {"Error message":"Value error in Keithley plugin: drain start field should be numeric"}]

        #end should be float
        try:
                        self.settings["drainend"] = float(self.settingsWidget.lineEdit_drainEnd.text())
        except ValueError:
                        return [1, {"Error message":"Value error in Keithley plugin: drain end field should be numeric"}]
	        
        #number of points should be int >0
        try:
                        self.settings["drainpoints"] = int(self.settingsWidget.lineEdit_drainPoints.text())
        except ValueError:
                        return [1, {"Error message":"Value error in Keithley plugin: drain number of points field should be integer"}]
        if self.settings["drainpoints"] <1:
                        return [1, {"Error message":"Value error in Keithley plugin: drain number of points field can not be less than 1"}]

        #limit should be float >0
        try:
                        self.settings["drainlimit"] = float(self.settingsWidget.lineEdit_drainLimit.text())
        except ValueError:
                        return [1, {"Error message":"Value error in Keithley plugin: drain limit field should be numeric"}]
        if self.settings["drainlimit"] <=0:
                        return [1, {"Error message":"Value error in Keithley plugin: drain limit field should be positive"}]
                        
        #drain nplc (in fact it is integration time for the measurement) is calculated from line frequency, should be float >0
        try:
                        self.settings["drainnplc"] =  0.001 * self.settings["lineFrequency"] * float(self.settingsWidget.lineEdit_drainNPLC.text())
        except ValueError:
                        return [1, {"Error message":"Value error in Keithley plugin: drain nplc field should be numeric"}]
        if self.settings["drainnplc"] <=0:
                        return [1, {"Error message":"Value error in Keithley plugin: drain nplc field should be positive"}]

        #delay (in fact it is stabilization time before the measurement), for Keithley control should be in s in GUI is ms, should be >0
        try:
                                self.settings["draindelay"] =  float(self.settingsWidget.lineEdit_drainDelay.text())/1000
        except ValueError:
                                return [1, {"Error message":"Value error in Keithley plugin: drain delay field should be numeric"}]
        if self.settings["draindelay"] <=0:
                                return [1, {"Error message":"Value error in Keithley plugin: drain delay field should be positive"}]                                

        # Determine a HighC mode for drain: may be True or False 
        if self.settingsWidget.checkBox_drainHighC.isChecked():
        	self.settings["drainhighc"] = True
        else:	
	        self.settings["drainhighc"] = False

        return [0, self.settings]

###############GUI enable/disable
    def set_running(self, status):
        self.settingsWidget.groupBox_general.setEnabled(not status)
        self.settingsWidget.groupBox_channels.setEnabled(not status)
        self.settingsWidget.groupBox_sweep.setEnabled(not status)
        if not status:
                self._update_GUI_state()

###############function for keithley control outside of sweep
    def smu_basicInit(self): 
    	"""intializaes smu with data for the 1st sweep step

    	Return the same as for keithley_init [status, message]:
    		status: 0 - no error, ~0 - error
    		message
    	"""     
    	s = {}

    	s["source"] = self.settings["channel"] #source channel: may take values [smua, smub]
    	s["drain"] = "smub" if self.settings["channel"] == "smua" else "smua"#drain channel: may take values [smub, smua]
    	s["type"] = "v" if self.settings["inject"] == "voltage" else "i"#source inject current or voltage: may take values [i ,v]
    	s["single_ch"] = self.settings["singlechannel"] #single channel mode: may be True or False
    	s["repeat"] = self.settings["repeat"] #repeat count: should be int >0
    	s["pulsepause"] = self.settings["pulsepause"] #pause between pulses in sweep (may not be used in continuous)
    	 
    	s["sourcehighc"] = self.settings["sourcehighc"]
    	s["drainnplc"] = self.settings["drainnplc"] #drain NPLC (may not be used in single channel mode)
    	
    	s["draindelay"] = self.settings["draindelaymode"] #stabilization time before measurement for drain channel: may take values [auto, manual] (may not be used in single channel mode)
    	s["draindelayduration"] = self.settings["draindelay"] #stabilization time duration if manual (may not be used in single channel mode)
    	s["drainlimit"] = self.settings["drainlimit"] #limit for current in voltage mode or for voltage in current mode (may not be used in single channel mode)
    	
    	s["sourcehighc"] = self.settings["sourcehighc"]
    	s["drainhighc"] = self.settings["drainhighc"]   	
    	s["drainvoltage"] = self.settings["drainstart"]
    	if self.smu_settings["sourcesensemode"] == "4 wire":
    		s["sourcesense"] = True #source sence mode: may take values [True - 4 wire, False - 2 wire]
    	else:
    		s["sourcesense"] = False #source sence mode: may take values [True - 4 wire, False - 2 wire]
    	if self.smu_settings["drainsensemode"] == "4 wire":
    		s["drainsense"] = True #source sence mode: may take values [True - 4 wire, False - 2 wire]
    	else:
    		s["drainsense"] = False #source sence mode: may take values [True - 4 wire, False - 2 wire]
    	if not (self.settings["mode"] == "pulsed"):
    		s["pulse"] = False# set pulsed mode: may be True - pulsed, False - continuous
    		s['sourcenplc'] = self.settings["continuousnplc"] #integration time in nplc units
    		s["delay"] = self.settings["continuousdelaymode"] #stabilization time mode for source: may take values [True - Auto, False - manual]
    		s["delayduration"] = self.settings["continuousdelay"] #stabilization time duration if manual				
    		s["steps"] = self.settings["continuouspoints"] #number of points in sweep
    		s["start"] = self.settings["continuousstart"] #start point of sweep
    		s["end"] = self.settings["continuousend"] #end point of sweep
    		s["limit"] = self.settings["continuouslimit"] #limit for the voltage if is in current injection mode, limit for the current if in voltage injection mode
    	else:
    		s["pulse"] = True# set pulsed mode: may be True - pulsed, False - continuous
    		s['sourcenplc'] = self.settings["pulsednplc"] #integration time in nplc units
    		s["delay"] = self.settings["pulseddelaymode"] #stabilization time mode for source: may take values [True - Auto, False - manual]
    		s["delayduration"] = self.settings["pulseddelay"] #stabilization time duration if manual				
    		s["steps"] = self.settings["pulsedpoints"] #number of points in sweep
    		s["start"] = self.settings["pulsedstart"] #start point of sweep
    		s["end"] = self.settings["pulsedend"] #end point of sweep
    		s["limit"] = self.settings["pulsedlimit"] #limit for the voltage if is in current injection mode, limit for the current if in voltage injection mode    	
    	
    	return self.smu.keithley_init(s) 
###############providing access to SMU functions

    def smu_connect(self): 
        """an interface for an externall calling function to connect to Keithley
        
        Returns [status, message]:
            0 - no error, ~0 - error (add error code later on if needed)
            message contains devices response to IDN query if devices is connected, or an error message otherwise
        
        """
        return self.smu.keithley_connect()

    def smu_disconnect(self): 
        """an interface for an externall calling function to disconnect Keithley
        
        """
        self.smu.keithley_disconnect()

    def smu_abort(self, channel): 
        """An interface for an externall calling function to stop the sweep on Keithley 
        (this function will NOT switch OFF the outputs)
        s: channel to get the last value (may be 'smua' or 'smub')
        """
        
        self.smu.abort_sweep(channel)

    def smu_outputON(self, source = None, drain = None): 
        """An interface for an externall calling function to switch on the output
        
        source and drain are "smua" or "smub"
        """       
        self.smu.channelsON(source, drain)  
    
    def smu_outputOFF(self): 
        """An interface for an externall calling function to switch off the output
        """
        
        self.smu.channelsOFF()   

    def get_line_frequency(self):
        """gets line frequency to provide to the plugins that will use it for nplc calculatin

        Returns:
            list [status, linefrequency/error message]
        """
        return self.smu.getLineFrequency()
    
    def smu_init(self, s:dict):
        """an interface for an externall calling function to initialize Keithley
        s: dictionary containing the settings for the sweep to initialize. It is different from the self. settings, as it contains data only for the current sweep 
        
    	Return the same as for keithley_init [status, message]:
    		status: 0 - no error, ~0 - error
    		message

        Args:
            s (dict): Configuration dictionary.
        
        Note: this function should be called only when the settings are checked, i.e. after parse_settings_widget
        """
        return self.smu.keithley_init(s)    
        
    def smu_runSweep(self, s:dict):
        """an interface for an externall calling function to run sweep on Keithley
        s: dictionary containing the settings to run the sweep. It is different from the self. settings, as it contains data only for the current sweep 
        
        Returns:
            0 - no error
            ~0 - error (add error code later on if needed)

        Args:
            s (dict): Configuration dictionary.
        
        Note: this function should be called only after the Keithley is initialized (i.e. after smu.keithley_init(s))
        """
        return  self.smu.keithley_run_sweep(s)

    def smu_getLastBufferValue(self, channel, readings = None):
        """an interface for an externall calling function to get last buffer value from Keithley
        s: channel to get the last value (may be 'smua' or 'smub')
        
        Returns:
            list [i, v, number of point in the buffer]
        """
        return  self.smu.get_last_buffer_value(channel)
        
    def smu_bufferRead(self, channel):
        """an interface for an externall calling function to get the content of a channel buffer from Keithley
        s: channel to get the last value (may be 'smua' or 'smub')
        
        Returns:
            np.ndarray (current, voltage)
        """
        return  self.smu.read_buffers(channel)

    def smu_getIV(self, channel):
        """gets IV data

        Returns:
            list [i, v]
        """
        try:
                return [0, self.smu.getIV(channel)]
        except:
                return [4, {"Error message":"Failed to get IV data"}]

    def smu_setOutput(self, channel, outputType, value):
        """sets smu output but does not switch it ON
	channel = "smua" or "smub"
	outputType = "i" or "v"
	value = float
        """
        try:
                return [0, self.smu.setOutput(channel,outputType,value)]
        except:
                return [4, {"Error message":"Failed to set smu output"}]
