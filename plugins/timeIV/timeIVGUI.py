'''
This is a timeIV plugin implementation for pyIVLS

The function of the plugin is to measure current and voltage change in time

This file should provide
- functions that will implement functionality of the hooks (see pyIVLS_timeIVGUI)
- GUI functionality - code that interracts with Qt GUI elements from widgets

'''

import os
from datetime import datetime

from PyQt6 import uic
from PyQt6.QtWidgets import QVBoxLayout, QFileDialog
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from MplCanvas import MplCanvas # this should be moved to some pluginsShare

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
        "smu": ["get_line_frequency", "parse_settings_widget", "smu_connect", "smu_init", "smu_outputOFF", "smu_disconnect","set_running"], 
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
        	status, info = self.function_dict["smu"]["get_line_frequency"]
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
                                return [1, {"Error message":"Value error in timeIV plugin: source delay field should be positive"}]	]	                

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
        
        return [0, self.settings]	             
        
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

    	s["source"] = self.settings["channel"] #source channel: may take values [smua, smub]
    	s["drain"] = "smub" if self.settings["channel"] == "smua" else "smua"#drain channel: may take values [smub, smua]
    	s["type"] = "v" if self.settings["inject"] == "voltage" else "i"#source inject current or voltage: may take values [i ,v]
    	s["single_ch"] = self.settings["singlechannel"] #single channel mode: may be True or False    	 

    	s["sourcenplc"] = self.settings["sourcenplc"] #drain NPLC (may not be used in single channel mode)
    	s["sourcedelay"] = True if self.settings["sourcedelaymode"] == "auto" else False #stabilization time mode for source: may take values [True - Auto, False - manual]
    	s["sourcedelayduration"] = self.settings["sourcedelay"] #stabilization time duration if manual (may not be used in single channel mode)
    	s["sourcelimit"] = self.settings["sourcelimit"] #limit for current in voltage mode or for voltage in current mode (may not be used in single channel mode)
    	s["sourcehighc"] = self.smu_settings["sourcehighc"]

    	s["drainnplc"] = self.settings["drainnplc"] #drain NPLC (may not be used in single channel mode)
    	s["draindelay"] = True if self.settings["draindelaymode"] == "auto" else False #stabilization time mode for source: may take values [True - Auto, False - manual]
    	s["draindelayduration"] = self.settings["draindelay"] #stabilization time duration if manual (may not be used in single channel mode)
    	s["drainlimit"] = self.settings["drainlimit"] #limit for current in voltage mode or for voltage in current mode (may not be used in single channel mode)
    	s["drainhighc"] = self.smu_settings["drainhighc"]    	
    	
    	if self.smu_settings["sourcesensemode"] == "4 wire":
    		s["sourcesense"] = True #source sence mode: may take values [True - 4 wire, False - 2 wire]
    	else:
    		s["sourcesense"] = False #source sence mode: may take values [True - 4 wire, False - 2 wire]
    	if self.smu_settings["drainsensemode"] == "4 wire":
    		s["drainsense"] = True #source sence mode: may take values [True - 4 wire, False - 2 wire]
    	else:
    		s["drainsense"] = False #source sence mode: may take values [True - 4 wire, False - 2 wire]
    	
    	if self.function_dict["smu"]["smu_init"](s):
    		return [2, {"Error message":"timeIV plugin: error in SMU plugin can not initialize"}]
    	
    	return {0, "OK"}

########Functions
########plugin actions   
    def _stopAction(self):
        self.settingsWidget.stopButton.setEnabled(False)
        #self.run_thread.thread_stop()
        
    def _runAction(self):
        self.setRunning(True)
        status, info = self.parse_settings_widget()
        #########create file for measurements
        if status:
        	if status == 3:
        		self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f"{info['Error message']}. Missing plugins: {info['Missing functions']}")
        	else:
        		self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f"{info[Error message]}")
        	self.info_message.emit(f"{info[Error message]}")
        	self.setRunning(False)
        	return [status, info]
        [status, message] = self.function_dict["smu"]["smu_connect"]()
        if status:
            self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : timeIV plugin : {message}, status = {status}")
            self.info_message.emit(f"Can not connect to smu")
            #### enable the interface
            self.setRunning(False)
            return [status, info]
        status, info = self.smuInit()
        if status:
        	self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f"{info[Error message]}")
        	self.info_message.emit(f"{info[Error message]}")
        	self.setRunning(False)
        	return [status, info]
        ############ run measurement
