import sys
import os
import time
from threading import Lock
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
		# settings for drain
		## settings["drainstart"] start point
		## settings["drainend"] end point
		## settings["drainpoints"] number of points
		## settings["drainlimit"] limit for current in voltage mode or for voltage in current mode
		## settings["drainnplc"] integration time in nplc units
		## settings["draindelay"] stabilization time before the measurement
		## settings["drainhighc"] HighC mode for drain: may be True or False  


'''

class Keithley2612BGUI:

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
        self.smu = Keithley2612B(pyIVLS_constants.KEITHLEY_VISA, dbg_mode=True)
	##IRtodo#### check here or in some other place if Keithley is actually connected

        self._connect_signals()

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
        self._mode_changed(self.settingsWidget.comboBox_mode.currentIndex())
        self._inject_changed(self.settingsWidget.comboBox_inject.currentIndex())
        self._delay_continuous_mode_changed(self.settingsWidget.comboBox_continuousDelayMode.currentIndex())
        self._delay_pulsed_mode_changed(self.settingsWidget.comboBox_pulsedDelayMode.currentIndex())
        self._delay_drain_mode_changed(self.settingsWidget.comboBox_drainDelayMode.currentIndex())

########Functions
###############GUI react to change

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
        
########Functions to be used externally
###############get settings from GUI

    def parse_settings_widget(self) -> "status":
        """Parses the settings widget for the Keithley. Extracts current values

        Returns:
            0 - no error
            ~0 - error (add error code later on if needed)
        """       

        self.settings = {}
        mixed_mode_flag = False
        double_sense_mode_flag = False
        ret_list = []

        # Determine source channel: may take values [smua, smub]
        self.settings["channel"] = (self.settingsWidget.comboBox_channel.currentText()).lower()
        # Determine source type: may take values [current, voltage]
        self.settings["inject"] = (self.settingsWidget.comboBox_inject.currentText()).lower()
        # Determine pulse/continuous mode: may take values [continuous, pulsed, mixed]
        self.settings["mode"] = (self.settingsWidget.comboBox_mode.currentText()).lower
 	# Determine delay mode for continuous sweep: may take values [auto, manual]
        self.settings["continuousdelaymode"] = (self.settingsWidget.comboBox_continuousDelayMode.currentText()).lower
        # Determine delay mode for pulsed sweep: may take values [auto, manual]
        self.settings["pulseddelaymode"] = (self.settingsWidget.comboBox_pulsedDelayMode.currentText()).lower
        # Determine delay mode for drain: may take values [auto, manual]
        self.settings["draindelaymode"] = (self.settingsWidget.comboBox_drainDelayMode.currentText()).lower
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
        self.settings["repeat"] = int(self.settingsWidget.lineEdit_repeat.text())

        # Determine settings for continuous mode
	#start should be float
        self.settings["continuousstart"] = float(self.settingsWidget.lineEdit_continuousStart.text())
      	#end should be float
        self.settings["continuousend"] = float(self.settingsWidget.lineEdit_continuousEnd.text())
        #number of points should be int >0
        self.settings["continuouspoints"] = int(self.settingsWidget.lineEdit_continuousPoints.text())
        #limit should be float >0
        self.settings["continuouslimit"] = float(self.settingsWidget.lineEdit_continuousLimit.text())
        #continuous nplc (in fact it is integration time for the measurement) is calculated from line frequency, should be float >0
        ##IRtodo#### line frequency may be read from Keithley itself
        self.settings["continuousnplc"] =  0.001 * pyIVLS_constants.LINE_FREQ * float(self.settingsWidget.lineEdit_continuousNPLC.text())
        #delay (in fact it is stabilization time before the measurement), for Keithley control should be in s in GUI is ms, should be >0
        self.settings["continuousdelay"] =  float(self.settingsWidget.lineEdit_continuousDelay.text())/1000

        # Determine settings for pulsed mode
	#start should be float
        self.settings["pulsedstart"] = float(self.settingsWidget.lineEdit_pulsedStart.text())
      	#end should be float
        self.settings["pulsedend"] = float(self.settingsWidget.lineEdit_pulsedEnd.text())
        #number of points should be int >0
        self.settings["pulsedpoints"] = int(self.settingsWidget.lineEdit_pulsedPoints.text())
        #limit should be float >0
        self.settings["pulsedlimit"] = float(self.settingsWidget.lineEdit_pulsedLimit.text())
        #pulsed nplc (in fact it is integration time for the measurement) is calculated from line frequency, should be float >0
        ##IRtodo#### line frequency may be read from Keithley itself
        self.settings["pulsednplc"] = 0.001 * pyIVLS_constants.LINE_FREQ * float(self.settingsWidget.lineEdit_pulsedNPLC.text())
        #delay (in fact it is stabilization time before the measurement), for Keithley control should be in s in GUI is ms, should be >0
        self.settings["pulseddelay"] = float(self.settingsWidget.lineEdit_pulsedDelay.text())/1000
        #pause between pulses
        self.settings["pulsedpause"] = float(self.settingsWidget.lineEdit_pulsedPause.text())

        # Determine settings for drain mode
	#start should be float
        self.settings["drainstart"] = float(self.settingsWidget.lineEdit_drainStart.text())
      	#end should be float
        self.settings["drainend"] = float(self.settingsWidget.lineEdit_drainEnd.text())
        #number of points should be int >0
        self.settings["drainpoints"] = int(self.settingsWidget.lineEdit_drainPoints.text())
        #limit should be float >0
        self.settings["drainlimit"] = float(self.settingsWidget.lineEdit_drainLimit.text())
        #drain nplc (in fact it is integration time for the measurement) is calculated from line frequency, should be float >0
        ##IRtodo#### line frequency may be read from Keithley itself
        self.settings["drainnplc"] =  0.001 * pyIVLS_constants.LINE_FREQ * float(self.settingsWidget.lineEdit_drainNPLC.text())
        #delay (in fact it is stabilization time before the measurement), for Keithley control should be in s in GUI is ms, should be >0
        self.settings["draindelay"] =  float(self.settingsWidget.lineEdit_drainDelay.text())/1000
        # Determine a HighC mode for drain: may be True or False 
        if self.settingsWidget.checkBox_drainHighC.isChecked():
        	self.settings["drainhighc"] = True
        else:	
	        self.settings["drainhighc"] = False

	##IRtodo######### add here checks that the values are allowed
        return 0
        
    def resistance_measurement(self, channel) -> float:
    ##IRtothink#### Should it be kept like this?
        """Measure the resistance at the probe.

        Returns:
            float: resistance
        """
        if channel == "smua" or channel == "smub":
            try:
                # Restore Series 2600B defaults.
                self.safewrite(f"{channel}.reset()")
                # Select current source function.
                self.safewrite(f"{channel}.source.func = {channel}.OUTPUT_DCAMPS")
                # Set source range to 10 mA.
                self.safewrite(f"{channel}.source.rangei = 10e-3")
                # Set current source to 10 mA.
                self.safewrite(f"{channel}.source.leveli = 10e-3")
                # Set voltage limit to 10 V. FIXME: Value of 1 v is arbitrary.
                self.safewrite(f"{channel}.source.limitv = 1")
                # Enable 2-wire ohms. FIXME: Check this
                self.safewrite(f"{channel}.sense = {channel}.SENSE_LOCAL")
                # Set voltage range to auto.
                self.safewrite(f"{channel}.measure.autorangev = {channel}.AUTORANGE_ON")
                # Turn on output.
                self.safewrite(f"{channel}.source.output = {channel}.OUTPUT_ON")
                # Get resistance reading.
                res = self.safequery(f"print({channel}.measure.r())")
                return res
            except Exception as e:
                print(f"Error measuring resistance: {e}")
                return -1
            finally:
                self.safewrite(f"{channel}.source.output = {channel}.OUTPUT_OFF")
                self.safewrite(f"{channel}.source.leveli = 0")
        else:
            raise ValueError(f"Invalid channel {channel}")

 
    def smu_init(self, s:dict):
        """an interface for an externall calling function to initialize Keithley
        s: dictionary containing the settings for the sweep to initialize. It is different from the self. settings, as it contains data only for the current sweep 
        
        Returns:
            0 - no error
            ~0 - error (add error code later on if needed)

        Args:
            s (dict): Configuration dictionary.
        
        Note: this function should be called only when the settings are checked, i.e. after parse_settings_widget
        """
        return smu.keithley_init(s)
