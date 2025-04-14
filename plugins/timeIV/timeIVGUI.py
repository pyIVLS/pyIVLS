'''
This is a timeIV plugin implementation for pyIVLS

The function of the plugin is to measure current and voltage change in time

This file should provide
- functions that will implement functionality of the hooks (see pyIVLS_timeIVGUI)
- GUI functionality - code that interracts with Qt GUI elements from widgets

'''

import os
import time
from datetime import datetime
from pathvalidate import is_valid_filename
from PyQt6 import uic
from PyQt6.QtWidgets import QVBoxLayout, QFileDialog
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from MplCanvas import MplCanvas # this should be moved to some pluginsShare
from threadStopped import thread_with_exception, ThreadStopped
from enum import Enum
import numpy as np

class timeIVexception(Exception): pass

#
class dataOrder(Enum):
    V = 1
    I = 0

class timeIVGUI(QObject): 
    """GUI implementation
    this class may be a child of QObject if Signals or Slot will be needed
    """
    non_public_methods = [] # add function names here, if they should not be exported as public to another plugins
########Signals
##remove this if plugin will only provide functions to another plugins, but will not interract with the user directly
    log_message = pyqtSignal(str)     
    info_message = pyqtSignal(str) 
########Functions          
    def __init__(self):

        super(timeIVGUI,self).__init__()
        
        # List of functions from another plugins required for functioning
        self.dependency = {
        "smu": ["get_line_frequency", "parse_settings_widget", "smu_connect", "smu_init", "smu_outputOFF",  "smu_outputON", "smu_disconnect","set_running", "smu_setOutput"], 
        }
        self.settings = {}
        
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
    
        self.settingsWidget = uic.loadUi(self.path + "timeIV_settingsWidget.ui")
        self.MDIWidget = uic.loadUi(self.path + "timeIV_MDIWidget.ui")
     
        #remove next if no direct interraction with user
        self._connect_signals()
        #remove next if no plots        
        self._create_plt()
        
    def _connect_signals(self):      
        self.settingsWidget.directoryButton.clicked.connect(self._getAddress)
        self.settingsWidget.stopButton.clicked.connect(self._stopAction)
        self.settingsWidget.runButton.clicked.connect(self._runAction)
        self.settingsWidget.stopTimerCheckBox.stateChanged.connect(self._stopTimerChanged)
        self.settingsWidget.autosaveCheckBox.stateChanged.connect(self._autosaveChanged)
        self.settingsWidget.checkBox_singleChannel.stateChanged.connect(self._single_channel_changed)
        self.settingsWidget.comboBox_sourceDelayMode.currentIndexChanged.connect(self._source_delay_mode_changed)
        self.settingsWidget.comboBox_drainDelayMode.currentIndexChanged.connect(self._drain_delay_mode_changed)
        self.settingsWidget.comboBox_inject.currentIndexChanged.connect(self._source_inject_changed)
        self.settingsWidget.comboBox_drainInject.currentIndexChanged.connect(self._drain_inject_changed)

    def _create_plt(self):
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.axes = self.sc.fig.add_subplot(111)
        
        self.axes_twinx = self.axes.twinx()
        self.axes.set_xlabel('Time (s)')
        self.axes.set_ylabel('Voltage (V)')
        self.axes_twinx.set_ylabel('Current (A)')

        layout = QVBoxLayout()
        layout.addWidget(self.sc._create_toolbar(self.MDIWidget))
        layout.addWidget(self.sc)
        self.MDIWidget.setLayout(layout)

########Functions 
########GUI Slots

########Functions
################################### internal

    def _parseSaveData(self) -> "status":
        self.settings["address"] = self.settingsWidget.lineEdit_path.text()
        if not os.path.isdir(self.settings["address"] + os.sep):
                self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : TLCCS plugin : address string should point to a valid directory")
                return [1, {"Error message":f"TLCCS plugin : address string should point to a valid directory"}]           
        self.settings["filename"] = self.settingsWidget.lineEdit_filename.text()
        if not is_valid_filename(self.settings["filename"]):
                self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : TLCCS plugin : filename is not valid")
                self.info_message.emit(f"TLCCS plugin : filename is not valid")
                return [1, {"Error message":f"TLCCS plugin : filename is not valid"}]
               
        self.settings["samplename"] = self.settingsWidget.lineEdit_sampleName.text()
        self.settings["comment"] = self.settingsWidget.lineEdit_comment.text()
        return [0,"Ok"]

    def parse_settings_widget(self) -> "status":
        """Parses the settings widget for the templatePlugin. Extracts current values. Checks if values are allowed. Provides settings of template plugin to an external plugin

        Returns [status, settings_dict]:
            status: 0 - no error, ~0 - error (add error code later on if needed)
            self.settings
        """        
        if not self.function_dict:
                return [3, {"Error message":"timeIV plugin : the plugin did not get all the neccessary functions from other plugins.", "Missing functions":self.missing_functions}]

        if not "lineFreuency" in self.settings:
        	status, info = self.function_dict["smu"]["get_line_frequency"]()
        	if status:
        		return [status, info]
        	else:
        		self.settings["lineFrequency"] = info

        status, message = self._parseSaveData()
        if status:
        	return [status, message]

        try:
                self.settings["timestep"] = float(self.settingsWidget.step_lineEdit.text())
        except ValueError:
                return [1, {"Error message":"Value error in timeIV plugin: time step field should be numeric"}]
        if self.settings["timestep"]<=0:
                return [1, {"Error message":"Value error in timeIV plugin: time step field should be greater than 0"}]
        try:
                self.settings["stopafter"] = float(self.settingsWidget.stopAfterLineEdit.text())
        except ValueError:
                return [1, {"Error message":"Value error in timeIV plugin: stop after field should be numeric"}]
        if self.settings["stopafter"]<=0:
                return [1, {"Error message":"Value error in timeIV plugin: stop after field should be greater than 0"}]                
        try:
                self.settings["autosaveinterval"] = float(self.settingsWidget.autosaveLineEdit.text())
        except ValueError:
                return [1, {"Error message":"Value error in timeIV plugin: autosave interval field should be numeric"}]
        if self.settings["autosaveinterval"]<=0:
                return [1, {"Error message":"Value error in timeIV plugin: autosave interval field should be greater than 0"}]
        self.settings["stoptimer"] = self.settingsWidget.stopTimerCheckBox.isChecked()
        self.settings["autosave"] = self.settingsWidget.autosaveCheckBox.isChecked()
        
        #SMU settings
        # Determine source channel: may take values [smua, smub]
        self.settings["channel"] = (self.settingsWidget.comboBox_channel.currentText()).lower()
        # Determine source type: may take values [current, voltage]
        self.settings["inject"] = (self.settingsWidget.comboBox_inject.currentText()).lower()
 	# Determine delay mode for source: may take values [auto, manual]
        self.settings["sourcedelaymode"] = (self.settingsWidget.comboBox_sourceDelayMode.currentText()).lower()
        # Determine source sence mode: may take values [2 wire, 4 wire, 2 & 4 wire]
        self.settings["sourcesensemode"] = (self.settingsWidget.comboBox_sourceSenseMode.currentText()).lower()
        # Determine delay mode for drain: may take values [auto, manual]
        self.settings["draindelaymode"] = (self.settingsWidget.comboBox_drainDelayMode.currentText()).lower()
        # Determine drain type: may take values [current, voltage]
        self.settings["draininject"] = (self.settingsWidget.comboBox_drainInject.currentText()).lower()
        # Determine drain sence mode: may take values [2 wire, 4 wire, 2 & 4 wire]
        self.settings["drainsensemode"] = (self.settingsWidget.comboBox_drainSenseMode.currentText()).lower()

	# Determine a single channel mode: may be True or False
        if self.settingsWidget.checkBox_singleChannel.isChecked():
        	self.settings["singlechannel"] = True
        else:	
	        self.settings["singlechannel"] = False
        self.settings["drainchannel"] = "smub" if self.settings["channel"] == "smua" else "smua"
        
        # Determine settings for source
        #start should be float
        try:
                        self.settings["sourcevalue"] = float(self.settingsWidget.lineEdit_sourceSetValue.text())
        except ValueError:
                        return [1, {"Error message":"Value error in timeIV plugin: source set value field should be numeric"}]
	        
        #limit should be float >0
        try:
                        self.settings["sourcelimit"] = float(self.settingsWidget.lineEdit_sourceLimit.text())
        except ValueError:
                        return [1, {"Error message":"Value error in timeIV plugin: source limit field should be numeric"}]
        if self.settings["sourcelimit"] <=0:
                        return [1, {"Error message":"Value error in timeIV plugin: source limit field should be positive"}]

        #source nplc (in fact it is integration time for the measurement) is calculated from line frequency, should be float >0
        try:
                        self.settings["sourcenplc"] =  0.001 * self.settings["lineFrequency"] * float(self.settingsWidget.lineEdit_sourceNPLC.text())
        except ValueError:
                        return [1, {"Error message":"Value error in timeIV plugin: source nplc field should be numeric"}]
        if self.settings["sourcenplc"] <=0:
                        return [1, {"Error message":"Value error in timeIV plugin: source nplc field should be positive"}]

        #delay (in fact it is stabilization time before the measurement), for Keithley control should be in s in GUI is ms, should be >0
        try:
                                self.settings["sourcedelay"] =  float(self.settingsWidget.lineEdit_sourceDelay.text())/1000
        except ValueError:
                                return [1, {"Error message":"Value error in timeIV plugin: source delay field should be numeric"}]
        if self.settings["sourcedelay"] <=0:
                                return [1, {"Error message":"Value error in timeIV plugin: source delay field should be positive"}]	                

        #start should be float
        try:
                        self.settings["drainvalue"] = float(self.settingsWidget.lineEdit_drainSetValue.text())
        except ValueError:
                        return [1, {"Error message":"Value error in timeIV plugin: drain set value field should be numeric"}]
	        
        #limit should be float >0
        try:
                        self.settings["drainlimit"] = float(self.settingsWidget.lineEdit_drainLimit.text())
        except ValueError:
                        return [1, {"Error message":"Value error in timeIV plugin: drain limit field should be numeric"}]
        if self.settings["drainlimit"] <=0:
                        return [1, {"Error message":"Value error in timeIV plugin: drain limit field should be positive"}]

        #drain nplc (in fact it is integration time for the measurement) is calculated from line frequency, should be float >0
        try:
                        self.settings["drainnplc"] =  0.001 * self.settings["lineFrequency"] * float(self.settingsWidget.lineEdit_drainNPLC.text())
        except ValueError:
                        return [1, {"Error message":"Value error in timeIV plugin: drain nplc field should be numeric"}]
        if self.settings["drainnplc"] <=0:
                        return [1, {"Error message":"Value error in timeIV plugin: drain nplc field should be positive"}]

        #delay (in fact it is stabilization time before the measurement), for Keithley control should be in s in GUI is ms, should be >0
        try:
                                self.settings["draindelay"] =  float(self.settingsWidget.lineEdit_drainDelay.text())/1000
        except ValueError:
                                return [1, {"Error message":"Value error in timeIV plugin: drain delay field should be numeric"}]
        if self.settings["draindelay"] <=0:
                                return [1, {"Error message":"Value error in timeIV plugin: drain delay field should be positive"}]	             	             
        
        [status, self.smu_settings] = self.function_dict["smu"]["parse_settings_widget"]()
        if status:
            return [2, self.smu_settings]
        
        return [0, self.settings]

########Functions
###############GUI setting up           	
    def _initGUI(self, plugin_info:"dictionary with settings obtained from plugin_data in pyIVLS_*_plugin"):
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK
        
        self.settingsWidget.lineEdit_path.setText(plugin_info["address"])
        self.settingsWidget.lineEdit_filename.setText(plugin_info["filename"])
        self.settingsWidget.lineEdit_sampleName.setText(plugin_info["samplename"])
        self.settingsWidget.lineEdit_comment.setText(plugin_info["comment"])

        self.settingsWidget.step_lineEdit.setText(plugin_info["timestep"])
        self.settingsWidget.stopAfterLineEdit.setText(plugin_info["stopafter"])
        self.settingsWidget.autosaveLineEdit.setText(plugin_info["autosaveinterval"])
        
        if plugin_info["stoptimer"] == True:
        	self.settingsWidget.stopTimerCheckBox.setChecked(True)
        else:
        	self.settingsWidget.stopTimerCheckBox.setChecked(False)

        if plugin_info["autosave"] == True:
        	self.settingsWidget.autosaveCheckBox.setChecked(True)
        else:
        	self.settingsWidget.autosaveCheckBox.setChecked(False)
        # SMU settings
        if plugin_info["singlechannel"] == "True":
            self.settingsWidget.checkBox_singleChannel.setChecked(True)
        currentIndex = self.settingsWidget.comboBox_channel.findText(plugin_info["channel"], Qt.MatchFlag.MatchFixedString)
        if currentIndex > -1:
           self.settingsWidget.comboBox_channel.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_inject.findText(plugin_info["inject"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_inject.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_sourceSenseMode.findText(plugin_info["sourcesensemode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_sourceSenseMode.setCurrentIndex(currentIndex)          
        currentIndex = self.settingsWidget.comboBox_sourceDelayMode.findText(plugin_info["sourcedelaymode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_sourceDelayMode.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_drainInject.findText(plugin_info["draininject"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_drainInject.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_drainSenseMode.findText(plugin_info["drainsensemode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_drainSenseMode.setCurrentIndex(currentIndex) 
        currentIndex = self.settingsWidget.comboBox_drainDelayMode.findText(plugin_info["draindelaymode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_drainDelayMode.setCurrentIndex(currentIndex)

        self.settingsWidget.lineEdit_sourceSetValue.setText(plugin_info["sourcesetvalue"])
        self.settingsWidget.lineEdit_sourceLimit.setText(plugin_info["sourcelimit"])
        self.settingsWidget.lineEdit_sourceNPLC.setText(plugin_info["sourcenplc"])
        self.settingsWidget.lineEdit_sourceDelay.setText(plugin_info["sourcedelay"])
        self.settingsWidget.lineEdit_drainSetValue.setText(plugin_info["drainsetvalue"])
        self.settingsWidget.lineEdit_drainLimit.setText(plugin_info["drainlimit"])
        self.settingsWidget.lineEdit_drainNPLC.setText(plugin_info["drainnplc"])
        self.settingsWidget.lineEdit_drainDelay.setText(plugin_info["draindelay"])
       
        # update to the correct GUI state
        self.setRunning(False)
        self._update_GUI_state()

    def _getAddress(self):
        address = self.settingsWidget.lineEdit_path.text()
        if not(os.path.exists(address)):
                address = self.path
        address = QFileDialog.getExistingDirectory(None, "Select directory for saving", address, options = QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks)
        if address:
                self.settingsWidget.lineEdit_path.setText(address)

########Functions
###############GUI react to change
    def _update_GUI_state(self):
    	self._stopTimerChanged(self.settingsWidget.stopTimerCheckBox.checkState().value)
    	self._autosaveChanged(self.settingsWidget.autosaveCheckBox.checkState().value)
    	self._single_channel_changed(self.settingsWidget.checkBox_singleChannel.checkState().value)
    	self._source_delay_mode_changed(self.settingsWidget.comboBox_sourceDelayMode.currentIndex())
    	self._drain_delay_mode_changed(self.settingsWidget.comboBox_drainDelayMode.currentIndex())
    	self._source_inject_changed(self.settingsWidget.comboBox_inject.currentIndex())
    	self._drain_inject_changed(self.settingsWidget.comboBox_drainInject.currentIndex())
        
    def _single_channel_changed(self, int):
        """Handles the visibility of the drain input fields based use single chennel box"""
        if self.settingsWidget.checkBox_singleChannel.isChecked():
             self.settingsWidget.DrainBox.setEnabled(False)
        else:     
             self.settingsWidget.DrainBox.setEnabled(True)

    def _source_delay_mode_changed(self, index):
        """Handles the visibility of the delay input fields based on the selected mode."""
        if self.settingsWidget.comboBox_sourceDelayMode.currentText() == "Auto":
            self.settingsWidget.label_sourceDelay.setEnabled(False)
            self.settingsWidget.lineEdit_sourceDelay.setEnabled(False)
            self.settingsWidget.label_sourceDelayUnits.setEnabled(False)
        else:
            self.settingsWidget.label_sourceDelay.setEnabled(True)
            self.settingsWidget.lineEdit_sourceDelay.setEnabled(True)
            self.settingsWidget.label_sourceDelayUnits.setEnabled(True)

    def _drain_delay_mode_changed(self, index):
        """Handles the visibility of the delay input fields based on the selected mode."""
        if self.settingsWidget.comboBox_drainDelayMode.currentText() == "Auto":
            self.settingsWidget.label_drainDelay.setEnabled(False)
            self.settingsWidget.lineEdit_drainDelay.setEnabled(False)
            self.settingsWidget.label_drainDelayUnits.setEnabled(False)
        else:
            self.settingsWidget.label_drainDelay.setEnabled(True)
            self.settingsWidget.lineEdit_drainDelay.setEnabled(True)
            self.settingsWidget.label_drainDelayUnits.setEnabled(True)

    def _source_inject_changed(self, index):
        """Changes the unit labels based on the selected injection type."""

        inject_type = self.settingsWidget.comboBox_inject.currentText()
        if inject_type == "Voltage":
            self.settingsWidget.label_sourceSetValue.setText("U")
            self.settingsWidget.label_sourceSetValueUnits.setText("V")
            self.settingsWidget.label_sourceLimitUnits.setText("A")
        else:
            self.settingsWidget.label_sourceSetValue.setText("I")
            self.settingsWidget.label_sourceSetValueUnits.setText("A")
            self.settingsWidget.label_sourceLimitUnits.setText("V")

    def _drain_inject_changed(self, index):
        """Changes the unit labels based on the selected injection type."""

        inject_type = self.settingsWidget.comboBox_drainInject.currentText()
        if inject_type == "Voltage":
            self.settingsWidget.label_drainSetValue.setText("U")
            self.settingsWidget.label_drainSetValueUnits.setText("V")
            self.settingsWidget.label_drainLimitUnits.setText("A")
        else:
            self.settingsWidget.label_drainSetValue.setText("I")
            self.settingsWidget.label_drainSetValueUnits.setText("A")
            self.settingsWidget.label_drainLimitUnits.setText("V")

    def _stopTimerChanged(self, int):
    	if self.settingsWidget.stopTimerCheckBox.isChecked():
    		self.settingsWidget.stopAfterLineEdit.setEnabled(True)
    		self.settingsWidget.stopAfterlabel.setEnabled(True)
    		self.settingsWidget.stopAfteUnitslabel.setEnabled(True)
    	else:
    		self.settingsWidget.stopAfterLineEdit.setEnabled(False)
    		self.settingsWidget.stopAfterlabel.setEnabled(False)
    		self.settingsWidget.stopAfteUnitslabel.setEnabled(False)

    def _autosaveChanged(self, int):
    	if self.settingsWidget.autosaveCheckBox.isChecked():
    		self.settingsWidget.autosaveIntervalLable.setEnabled(True)
    		self.settingsWidget.autosaveLineEdit.setEnabled(True)
    		self.settingsWidget.autosaveintervalUnitslabel.setEnabled(True)
    	else:
    		self.settingsWidget.autosaveIntervalLable.setEnabled(False)
    		self.settingsWidget.autosaveLineEdit.setEnabled(False)
    		self.settingsWidget.autosaveintervalUnitslabel.setEnabled(False)

    def setRunning(self, status):
    	#status == True the measurement is running
        self.settingsWidget.stopButton.setEnabled(status)
        self.settingsWidget.runButton.setEnabled(not status)

        self.settingsWidget.groupBox.setEnabled(not status)        
        self.settingsWidget.groupBox_SMUGeneral.setEnabled(not status)        
        self.settingsWidget.fileBox.setEnabled(not status)  
        
        if status:
        	self._update_GUI_state()
        
########Functions
########plugins interraction        
    def _getPublicFunctions(self,function_dict): 
        self.missing_functions = []    
        for dependency_plugin in list(self.dependency.keys()):
                if not dependency_plugin in function_dict:
                        self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : timeIV plugin : Functions for dependency plugin '{dependency_plugin}' not found")
                        self.missing_functions.append(dependency_plugin)
                        continue
                for dependency_function in self.dependency[dependency_plugin]:
                        if not dependency_function in function_dict[dependency_plugin]:
                                self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : timeIV plugin : Function '{dependency_function}' for dependency plugin '{dependency_plugin}' not found")
                                self.missing_functions.append(f"{dependency_plugin}:{dependency_function}")
        if not self.missing_functions:
            self.settingsWidget.runButton.setEnabled(True)   
            self.function_dict = function_dict
        else:    
            self.settingsWidget.runButton.setDisabled(True)   
            self.function_dict = {}
        return self.missing_functions
 
    def _getLogSignal(self):
        return self.log_message

    def _getInfoSignal(self):
        return self.info_message        
########Functions
############### run preparations
    def smuInit(self): 
    	"""intializaes smu with data for the 1st sweep step

    	Return the same as for keithley_init [status, message]:
    		status: 0 - no error, ~0 - error
    		message
    	"""     
    	s = {}

    	s["pulse"] = False
    	s["source"] = self.settings["channel"] #source channel: may take values [smua, smub]
    	s["drain"] = self.settings["drainchannel"]#drain channel: may take values [smub, smua]
    	s["type"] = "v" if self.settings["inject"] == "voltage" else "i"#source inject current or voltage: may take values [i ,v]
    	s["single_ch"] = self.settings["singlechannel"] #single channel mode: may be True or False    	 

    	s["sourcenplc"] = self.settings["sourcenplc"] #drain NPLC (may not be used in single channel mode)
    	s["delay"] = True if self.settings["sourcedelaymode"] == "auto" else False #stabilization time mode for source: may take values [True - Auto, False - manual]
    	s["delayduration"] = self.settings["sourcedelay"] #stabilization time duration if manual (may not be used in single channel mode)
    	s["limit"] = self.settings["sourcelimit"] #limit for current in voltage mode or for voltage in current mode (may not be used in single channel mode)
    	s["sourcehighc"] = self.smu_settings["sourcehighc"]

    	s["drainnplc"] = self.settings["drainnplc"] #drain NPLC (may not be used in single channel mode)
    	s["draindelay"] = True if self.settings["draindelaymode"] == "auto" else False #stabilization time mode for source: may take values [True - Auto, False - manual]
    	s["draindelayduration"] = self.settings["draindelay"] #stabilization time duration if manual (may not be used in single channel mode)
    	s["drainlimit"] = self.settings["drainlimit"] #limit for current in voltage mode or for voltage in current mode (may not be used in single channel mode)
    	s["drainhighc"] = self.smu_settings["drainhighc"]    	
    	
    	if self.settings["sourcesensemode"] == "4 wire":
    		s["sourcesense"] = True #source sence mode: may take values [True - 4 wire, False - 2 wire]
    	else:
    		s["sourcesense"] = False #source sence mode: may take values [True - 4 wire, False - 2 wire]
    	if self.settings["drainsensemode"] == "4 wire":
    		s["drainsense"] = True #source sence mode: may take values [True - 4 wire, False - 2 wire]
    	else:
    		s["drainsense"] = False #source sence mode: may take values [True - 4 wire, False - 2 wire]
    	if self.function_dict["smu"]["smu_init"](s):
    		return [2, {"Error message":"timeIV plugin: error in SMU plugin can not initialize"}]
    	
    	return {0, "OK"}

########Functions
########create file header

    def create_file_header(self, settings, smu_settings):
            '''
            creates a header for the csv file in the old measuremnt system style
            
            input	smu_settings dictionary for Keithley2612GUI.py class (see Keithley2612BGUI.py)
            	settings dictionary for the sweep plugin	
            
            str containing the header
            
            '''

            ## header may not be optimal, this is because it should repeat the structure of the headers produced by the old measurement station
            comment = "#####################"
            if settings["samplename"] == "":
               comment = f"{comment}\n\n measurement of {{noname}}\n\n"
            else:   
               comment = f"{comment}\n\n measurement of {settings['samplename']}\n\n" 
            comment = f"{comment}date {datetime.now().strftime('%d-%b-%Y, %H:%M:%S')}\n"
            comment = f"{comment}Keithley source {settings['channel']}\n"
            comment = f"{comment}Source in {settings['inject']} injection mode\n"
            if settings["inject"] == "voltage":
               stepunit = "V"
               limitunit = "A"
            else:   
               stepunit = "A"
               limitunit = "V"
            comment = f"{comment}\n\n"
            comment = f"{comment}Set value for time check {settings['sourcevalue']} {stepunit}\n"
            comment = f"{comment}\n"
            comment = f"{comment}Limit for step {settings['sourcelimit']} {limitunit}\n"
            if settings["sourcedelaymode"] == 'auto':
                comment = f"{comment}Measurement acquisition period is done in AUTO mode\n"
            else:
                comment = f"{comment}Measurement stabilization period is{settings['sourcedelay']/1000} ms\n"
            comment = f"{comment}NPLC value {settings['sourcenplc']*1000/settings['lineFrequency']} ms (for detected line frequency {settings['lineFrequency']} Hz is {settings['sourcenplc']})\n"
            comment = f"{comment}\n\n"
            comment = f"{comment}Continuous operation of the source with step time settings['timestep'] \n\n\n"
	   
            if not settings["singlechannel"]:
                comment = f"{comment}Drain in {settings['draininject']} injection mode\n"
                if settings["inject"] == "voltage":
                        stepunit = "V"
                        limitunit = "A"
                else:   
                        stepunit = "A"
                        limitunit = "V"
                comment = f"{comment}Set value for drain {settings['drainvalue']} {stepunit}\n"
                comment = f"{comment}Limit for drain {settings['drainlimit']} {limitunit}\n"
                if settings["draindelaymode"] == 'auto':
                        comment = f"{comment}Measurement acquisition period for drain is done in AUTO mode\n"
                else:
                        comment = f"{comment}Measurement stabilization period for drain is{settings['draindelay']/1000} ms\n"
                comment = f"{comment}NPLC value {settings['drainnplc']*1000/settings['lineFrequency']} ms (for detected line frequency {settings['lineFrequency']} Hz is {settings['drainnplc']})\n"
            else:
            	comment = f"{comment}\n\n\n\n\n"

            comment = f"{comment}\n"
            comment = f"{comment}Comment: {settings['comment']}\n"
            comment = f"{comment}\n"	

            comment = f"{comment}\n\n\n"
	   
            if smu_settings["sourcehighc"]:
                        comment = f"{comment}Source in high capacitance mode"
            else:
                        comment = f"{comment}Source not in HighC mode (normal operation)"
            if not settings["singlechannel"]:
                if smu_settings["drainhighc"]:
                        comment = f"{comment}. Drain in high capacitance mode\n"
                else:
                        comment = f"{comment}. Drain not in HighC mode (normal operation)\n"
            else:
                comment = f"{comment}\n"
            
            comment = f"{comment}\n\n\n\n\n\n\n\n\n"

            if not(smu_settings["singlechannel"]):
                if smu_settings["drainhighc"]:
                    comment = f"{comment}High capacitance mode for drain is enabled\n"
                else:
                    comment = f"{comment}High capacitance mode for drain is disabled\n"
            else:
                comment = f"{comment}\n"
                
            comment = f"{comment}\n\n\n\n\n\n\n\n\n"

            if settings["stoptimer"]:
                    comment = f"{comment}Timer set for {settings['stopafter']} minutes\n"
            else:
                    comment = f"{comment}\n"

            if settings["sourcesensemode"] == "2 wire":
                comment = f"{comment}Sourse in 2 point measurement mode\n"
            elif settings["sourcesensemode"] == "4 wire":
                comment = f"{comment}Sourse in 4 point measurement mode\n"
            if not(settings["singlechannel"]):
                if settings["drainsensemode"] == "2 wire":
                    comment = f"{comment}Drain in 2 point measurement mode\n"
                elif settings["drainsensemode"] == "4 wire":
                    comment = f"{comment}Drain in 4 point measurement mode\n"
            else:
                comment = f"{comment}\n"

            if settings["singlechannel"]:
                comment = f"{comment}stime, IS, VS\n"
            else:
                comment = f"{comment}stime, IS, VS, ID, VD"

            return comment

########Functions
########plugin actions   
    def _stopAction(self):
        self.run_thread.thread_stop()
        
    def _runAction(self):
        try:
                self.setRunning(True)
                status, info = self.parse_settings_widget()
                if status:
        	        if status == 3:
        		        self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f":timeIV : missing plugins: {info['Missing functions']}")
        	        raise timeIVexception(f"{info['Error message']}")
                [status, message] = self.function_dict["smu"]["smu_connect"]()
                if status:
        	        raise timeIVexception(f"can not connect to smu {message}")
                [status, info] = self.smuInit()
                if status:
        	        raise timeIVexception(f"{info['Error message']}")

        ##IRtodo#### check that the new file will not overwrite existing data -> implement dialog

                self.run_thread = thread_with_exception(self._sequenceImplementation)
                self.run_thread.start()
        except Exception as e:
                self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f":timeIV : {e}")
                self.info_message.emit(f"{e}")
                self.setRunning(False)
                return [status, info]

########Functions
########sequence implementation
    def _saveData(self, fileheader, time, sourceI, sourceV, drainI = None, drainV = None) :   
        fulladdress = self.settings["address"] + os.sep + self.settings["filename"] + ".dat"
        if drainI == None:
                np.savetxt(fulladdress, np.hstack([time, sourceI, sourceV]).T, fmt='%.8f', delimiter=',', newline='\n', header=fileheader, comments='#')        
                print("save")
        else:
                np.savetxt(fulladdress, np.hstack([time, sourceI, sourceV, drainI, drainV]).T, fmt='%.8f', delimiter=',', newline='\n', header=fileheader, comments='#')

    def _sequenceImplementation(self) :
        try:
                header = self.create_file_header(self.settings, self.smu_settings)
                self.function_dict["smu"]["smu_outputOFF"]()
                self.function_dict["smu"]["smu_setOutput"](self.settings["channel"], 'v' if self.settings['inject']=='voltage' else 'i', self.settings["sourcevalue"])
                if not self.settings["singlechannel"]:
                        self.function_dict["smu"]["smu_setOutput"](self.settings["drainchannel"], 'v' if self.settings['draininject']=='voltage' else 'i', self.settings["drainvalue"])
                timeData = []
                startTic = time.time()
                saveTic = startTic
                self.function_dict["smu"]["smu_outputON"](self.settings["channel"], self.settings["drainchannel"])
                while True:
                        status, sourceIV = self.function_dict["smu"]["smu_getIV"](self.settings["channel"])
                        if status:
                                raise timeIVexception(sourceIV["Error message"])
                        if not self.settings["singlechannel"]:
                                status, drainIV = self.function_dict["smu"]["smu_getIV"](self.settings["drainchannel"])
                                if status:
                                        raise timeIVexception(drainIV["Error message"])
                        currentTime =  time.time() 
                        toc = currentTime - startTic                                      
                        if not timeData:
                                self.axes.cla()
                                self.axes_twinx.cla()
                                timeData.append(toc)
                                sourceV = [sourceIV[dataOrder.V.value]]
                                plot_refs = self.axes.plot(timeData, sourceV, 'bo')
                                self.axes.set_xlabel('time (s)')
                                self.axes.set_ylabel('Voltage (V)')
                                self._plot_sourceV = plot_refs[0]
                                self.axes_twinx.set_ylabel('Current (A)')
                                sourceI = [sourceIV[dataOrder.I.value]]
                                plot_refs = self.axes_twinx.plot(timeData, sourceI, 'b*')
                                self._plot_sourceI = plot_refs[0]
                                if not self.settings["singlechannel"]:
                                        drainV = [drainIV[dataOrder.V.value]]
                                        plot_refs = self.axes.plot(timeData, drainV, 'go')
                                        self._plot_drainV = plot_refs[0]
                                        drainI = [drainIV[dataOrder.I.value]]
                                        plot_refs = self.axes_twinx.plot(timeData, drainI, 'g*')
                                        self._plot_drainI = plot_refs[0]
                                else:
                                        drainI = None
                                        drainV = None
                        else:
                                timeData.append(toc)
                                sourceV.append(sourceIV[dataOrder.V.value])
                                sourceI.append(sourceIV[dataOrder.I.value])
                                self._plot_sourceV.set_xdata(timeData)
                                self._plot_sourceV.set_ydata(sourceV)
                                #self._plot_sourceI.set_ydata(sourceI)
                                ##### there is a bug in matplotlib, the axes name is on a wrong side after cla()
                                #####https://github.com/matplotlib/matplotlib/issues/28268
                                self.axes_twinx.cla()
                                self.axes_twinx.plot(timeData, sourceI, 'b*')
                                
                                if not self.settings["singlechannel"]:
                                        self._plot_drainV.set_ydata(drainV)
                                        self._plot_drainI.set_ydata(drainI)
                        self.axes.relim()
                        self.axes.autoscale_view()
                        self.sc.draw()        
                        if self.settings["stoptimer"]:
                                if (currentTime - startTic) >= self.settings["stopafter"]*60: #convert to sec from min
                                        self._saveData(header, timeData, sourceI, sourceV, drainI, drainV)
                                        break
                        if self.settings["autosave"]:
                                if (currentTime - saveTic) >= self.settings["autosaveinterval"]*60: #convert to sec from min
                                        self._saveData(header, timeData, sourceI, sourceV, drainI, drainV)
                                        saveTic = currentTime
                        time.sleep(self.settings["timestep"])
                self.function_dict["smu"]["smu_outputOFF"]()
                self.function_dict["smu"]["smu_disconnect"]()
                self.setRunning(False)
                return [0,"OK"]
        except ThreadStopped:
                self.setRunning(False)
                try:
        	        self.function_dict["smu"]["smu_outputOFF"]()
        	        self.function_dict["smu"]["smu_disconnect"]()
        	        return [0,"OK"]
                except Exception as e:
        	        self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f' : timeIV : smu turn off failed')
        	        return [1, {"Error message", e}] 
        except Exception as e:
                self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f":timeIV: smu returned wrong status with message {e}")
                self.info_message.emit(f"timeIV sequence failed with message: {e}")
                self.setRunning(False)
                try:
        	        self.function_dict["smu"]["smu_outputOFF"]()
        	        self.function_dict["smu"]["smu_disconnect"]()
                except:
        	        self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f' : timeIV : smu turn off failed')
                finally:       
        	        return [1, {"Error message", e}]
