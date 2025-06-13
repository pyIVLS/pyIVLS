'''
This is a plugin for using spectrometer while powering a device under the test with SMU.
In future this plugin planned to be extended to synchronius operation of SMU with spectrometer.

This is a fast implementation, i.e. it only bounds spectrometer to SMU for runing in sequence mode. 
Standalone functionality may be added later.

ivarad
25.06.10

'''

import os

from PyQt6 import uic, QtWidgets
from PyQt6.QtCore import Qt
import numpy as np
import copy

class specSMU_GUI(): 
    """GUI implementation
    """
    non_public_methods = [] # add function names here, if they should not be exported as public to another plugins
    public_methods = ["parse_settings_widget", "sequenceStep", "setSettings"] # add function names here, necessary for descendents of QObject, otherwise _get_public_methods returns a lot of QObject methods
########Signals
##not needed for sequence implementation, may be added later only for standalone mode
    #log_message = pyqtSignal(str)     
    #info_message = pyqtSignal(str) 

########Functions          
    def __init__(self):

        #super(pluginTemplateGUI,self).__init__() ### this is needed if the class is a child of QObject
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        self.dependency = {
        "smu": ["parse_settings_widget", "smu_connect", "smu_init", "smu_outputOFF",  "smu_outputON", "smu_disconnect", "set_running", "smu_setOutput", "smu_channelNames"], 
        "spectrometer" : ["parse_settings_preview" , "spectrometerConnect", "spectrometerDisconnect", "spectrometerSetIntegrationTime", "spectrometerGetIntegrationTime", "spectrometerStartScan", "spectrometerGetSpectrum", "spectrometerGetScan"]
        }
        self.settingsWidget = uic.loadUi(self.path + "specSMU_settingsWidget.ui")

        # Initialize the functionality core that should be independent on GUI
        #### as this is a complex plugin, i.e. only bounds functionalities of different devices, it may not have "core functionality" but this may be added later on
        #self.templateFunctionality = pluginTemplate()
        
        #remove next if no direct interraction with user
        self._connect_signals()
        
    def _connect_signals(self):      
        # Connect the channel combobox
        self.settingsWidget.comboBox_mode.currentIndexChanged.connect(self._mode_changed)

        # Connect the inject type combobox
        inject_box = self.settingsWidget.comboBox_inject
        inject_box.currentIndexChanged.connect(self._inject_changed)

        delayComboBox = self.settingsWidget.comboBox_DelayMode

        delayComboBox.currentIndexChanged.connect(self._delay_mode_changed)
        



########Functions 
########GUI Slots

    def _update_GUI_state(self):
        self._mode_changed(self.settingsWidget.comboBox_mode.currentIndex())
        self._inject_changed(self.settingsWidget.comboBox_inject.currentIndex())
        self._delay_mode_changed(self.settingsWidget.comboBox_DelayMode.currentIndex())

    def _mode_changed(self, index):
        """Handles the visibility of the mode input fields based on the selected mode."""

        mode = self.settingsWidget.comboBox_mode.currentText()
        if mode == "Continuous":
            self.settingsWidget.label_pulsedPause.setEnabled(False)
            self.settingsWidget.label_pulsedPause_2.setEnabled(False)
            self.settingsWidget.lineEdit_Pause.setEnabled(False)
        elif mode == "Pulsed":
            self.settingsWidget.label_pulsedPause.setEnabled(True)
            self.settingsWidget.label_pulsedPause_2.setEnabled(True)
            self.settingsWidget.lineEdit_Pause.setEnabled(True)

        self.settingsWidget.update()


    def _inject_changed(self, index):
        """Changes the unit labels based on the selected injection type."""
        start_label = self.settingsWidget.label_StartUnits
        end_label = self.settingsWidget.label_EndUnits
        limit_label = self.settingsWidget.label_LimitUnits

        inject_type = self.settingsWidget.comboBox_inject.currentText()
        if inject_type == "Voltage":
            start_label.setText("V")
            end_label.setText("V")
            limit_label.setText("A")
        else:
            start_label.setText("A")
            end_label.setText("A")
            limit_label.setText("V")
        
    def _delay_mode_changed(self, index):
        """Handles the visibility of the delay input fields based on the selected mode."""
        if self.settingsWidget.comboBox_DelayMode.currentText() == "Auto":
            self.settingsWidget.label_Delay.setEnabled(False)
            self.settingsWidget.lineEdit_Delay.setEnabled(False)
            self.settingsWidget.label_DelayUnits.setEnabled(False)
        else:
            self.settingsWidget.label_Delay.setEnabled(True)
            self.settingsWidget.lineEdit_Delay.setEnabled(True)
            self.settingsWidget.label_DelayUnits.setEnabled(True)

        self.settingsWidget.update()

    
########Functions
################################### internal
    def _pushButton(self):
        self.sequenceStep("aa")

########Functions
###############GUI setting up               
    def _initGUI(self, plugin_info:"dictionary with settings obtained from plugin_data in pyIVLS_*_plugin"):
        ##populates GUI with values stored in settings
        
        if plugin_info["singlechannel"] == "True":
            self.settingsWidget.checkBox_singleChannel.setChecked(True)
        self.settingsWidget.comboBox_channel.clear()
        self.settingsWidget.comboBox_channel.addItems(self.function_dict["smu"]["smu_channelNames"]())
        currentIndex = self.settingsWidget.comboBox_channel.findText(plugin_info["channel"], Qt.MatchFlag.MatchFixedString)
        if currentIndex > -1:
           self.settingsWidget.comboBox_channel.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_inject.findText(plugin_info["inject"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_inject.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_mode.findText(plugin_info["mode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_mode.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_DelayMode.findText(plugin_info["delaymode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_DelayMode.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_sourceSenseMode.findText(plugin_info["sourcesensemode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_sourceSenseMode.setCurrentIndex(currentIndex)
        self.settingsWidget.lineEdit_Start.setText(plugin_info["start"])
        self.settingsWidget.lineEdit_End.setText(plugin_info["end"])
        self.settingsWidget.lineEdit_Points.setText(plugin_info["points"])
        self.settingsWidget.lineEdit_Limit.setText(plugin_info["limit"])
        self.settingsWidget.lineEdit_NPLC.setText(plugin_info["nplc"])
        self.settingsWidget.lineEdit_Delay.setText(plugin_info["delay"])

        # update to the correct GUI state
        self._update_GUI_state()

########Functions
###############GUI react to change

########Functions
########plugins interraction        

    def _getPublicFunctions(self,function_dict):
        self.missing_functions = []    
        for dependency_plugin in list(self.dependency.keys()):
                if not dependency_plugin in function_dict:
                        self.missing_functions.append(dependency_plugin)
                        continue
                for dependency_function in self.dependency[dependency_plugin]:
                        if not dependency_function in function_dict[dependency_plugin]:
                                self.missing_functions.append(f"{dependency_plugin}:{dependency_function}")
        if not self.missing_functions: 
            self.function_dict = function_dict
        else:     
            self.function_dict = {}
        return self.missing_functions

########IRtoThink## for now this plugin will be used only as a part of sequences, so this is not required. It may change later on, if the plugin will be reorganized as a standalone.

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
            and method in self.public_methods
        }
        return methods

#    def _getLogSignal(self):
#        return self.log_message
#        
#    def _getInfoSignal(self):
#        return self.info_message
#
#    def _getCloseLockSignal(self):
#        return self.closeLock        
#    
########Functions to be used externally
###############get settings from GUI 
    def parse_settings_widget(self):
        """Parses the settings widget for the plugin. Extracts current values. Checks if values are allowed. Provides settings of to an external plugin if needed

        Returns [status, settings_dict]:
            status: 0 - no error, ~0 - error
            self.settings
        """     
        if not self.function_dict:
                return [3,  {"Error message": f"Missing functions in SpecSMU plugin. Check log" , "Missing functions" : self.missing_functions}]
        self.settings = {}

        [status, self.smu_settings] = self.function_dict["smu"]["parse_settings_widget"]()
        if status:
            return [2, self.smu_settings]

        [status, self.spectrometer_settings] = self.function_dict["spectrometer"]["parse_settings_widget"]()
        if status:
            return [2, self.spectrometer_settings]

        self.settings["smu_settings"] = self.smu_settings
        self.settings["spectrometer_settings"] = self.spectrometer_settings
        
        # Determine source channel: may take values depending on the channel names in smu, e.g. for Keithley 2612B [smua, smub]
        self.settings["channel"] = (self.settingsWidget.comboBox_channel.currentText()).lower()
        currentIndex = self.settingsWidget.comboBox_channel.currentIndex()
        self.settings["drainchannel"] = self.settings["channel"] # dual channel not implemented. 
        # Determine source type: may take values [current, voltage]
        self.settings["inject"] = (self.settingsWidget.comboBox_inject.currentText()).lower()
        # Determine pulse/continuous mode: may take values [continuous, pulsed, mixed]
        self.settings["mode"] = (self.settingsWidget.comboBox_mode.currentText()).lower()
        # Determine delay mode : may take values [auto, manual]
        self.settings["delaymode"] = (self.settingsWidget.comboBox_DelayMode.currentText()).lower()
        # Determine source sence mode: may take values [2 wire, 4 wire, 2 & 4 wire]
        self.settings["sourcesensemode"] = (self.settingsWidget.comboBox_sourceSenseMode.currentText()).lower()

        # Determine a single channel mode: may be True or False
        if self.settingsWidget.checkBox_singleChannel.isChecked():
            self.settings["singlechannel"] = True
        else:
            self.settings["singlechannel"] = False

        # Determine settings
        #start should be float
        try:
                        self.settings["start"] = float(self.settingsWidget.lineEdit_Start.text())
        except ValueError:
                        return [1, {"Error message":"Value error in SpecSMU plugin: start field should be numeric"}]
            
        #end should be float
        try:
                        self.settings["end"] = float(self.settingsWidget.lineEdit_End.text())
        except ValueError:
                        return [1, {"Error message":"Value error in SpecSMU plugin: end field should be numeric"}]
        
        #number of points should be int >0
        try:
                        self.settings["points"] = int(self.settingsWidget.lineEdit_Points.text())
        except ValueError:
                        return [1, {"Error message":"Value error in SpecSMU plugin: number of points field should be integer"}]
        if self.settings["points"] <1:
                        return [1, {"Error message":"Value error in SpecSMU plugin: number of points field can not be less than 1"}]

        #limit should be float >0
        try:
                        self.settings["limit"] = float(self.settingsWidget.lineEdit_Limit.text())
        except ValueError:
                        return [1, {"Error message":"Value error in SpecSMU plugin: limit field should be numeric"}]
        if self.settings["limit"] <=0:
                        return [1, {"Error message":"Value error in SpecSMU plugin: limit field should be positive"}]

        #nplc (in fact it is integration time for the measurement) is calculated from line frequency, should be float >0
        try:
                        self.settings["nplc"] =  0.001 * self.smu_settings["lineFrequency"] * float(self.settingsWidget.lineEdit_NPLC.text())
        except ValueError:
                        return [1, {"Error message":"Value error in SpecSMU plugin: continuous nplc field should be numeric"}]
        if self.settings["nplc"] <=0:
                        return [1, {"Error message":"Value error in SpecSMU plugin: continuous nplc field should be positive"}]

        #delay (in fact it is stabilization time before the measurement), for Keithley control should be in s in GUI is ms, should be >0
        try:
                                self.settings["delay"] =  float(self.settingsWidget.lineEdit_Delay.text())/1000
        except ValueError:
                                return [1, {"Error message":"Value error in SpecSMU plugin: delay field should be numeric"}]
        if self.settings["delay"] <=0:
                                return [1, {"Error message":"Value error in SpecSMU plugin: delay field should be positive"}]                    

        #pause between pulses should be >0
        try:
                        self.settings["pause"] = float(self.settingsWidget.lineEdit_Pause.text())
        except ValueError:
                        return [1, {"Error message":"Value error in SpecSMU plugin: pulse pause field should be numeric"}]
        if self.settings["pause"] <=0:
                        return [1, {"Error message":"Value error in SpecSMU plugin: pulse pause field should be positive"}]

        return [0, self.settings]

    def setSettings(self, settings): #### settings from sequenceBuilder
#the filename in settings may be modified, as settings parameter is pointer, it will modify also the original data. So need to make sure that the original data is intact
        self.settings = []
        self.settings = copy.deepcopy(settings)
        self.smu_settings = settings["smu_settings"]
        self.spectrometer_settings = settings["spectrometer_settings"]
#this function is called not from the main thread. Direct addressing of qt elements not from te main thread causes segmentation fault crash. Using a signal-slot interface between different threads should make it work
#        self._setGUIfromSettings()
###############GUI enable/disable



###############sequence implementation

    def sequenceStep(self, postfix):
        self.spectrometer_settings["filename"] = self.spectrometer_settings["filename"] + postfix
        [status, message] = self.function_dict["smu"]["smu_connect"]()
        if status:
            return [status, message]
        [status, message] = self.function_dict["spectrometer"]["spectrometerConnect"]()
        if status:
            print(f"Error in connecting to spectrometer: {message}")
            return [status, message]
        ##IRtothink####error detection should be implemented
        self._SpecSMUImplementation()
        self.function_dict["smu"]["smu_disconnect"]()
        self.function_dict["spectrometer"]["spectrometerDisconnect"]()
        return [0, "specSMU action finished"]
    
    def smuInit(self): 
        """intializaes smu

        Return the same as for keithley_init [status, message]:
            status: 0 - no error, ~0 - error
            message
        """     
        s = {}

        s["pulse"] = False #### for now it is SW control, this may change for HW triggering
        s["source"] = self.settings["channel"] #may take values depending on the channel names in smu, e.g. for Keithley 2612B [smua, smub]
        s["drain"] = self.settings["drainchannel"]
        s["type"] = "v" if self.settings["inject"] == "voltage" else "i"#source inject current or voltage: may take values [i ,v]
        s["single_ch"] = self.settings["singlechannel"] #single channel mode: may be True or False         

        s["sourcenplc"] = self.settings["nplc"] #drain NPLC (may not be used in single channel mode)
        s["delay"] = True if self.settings["delaymode"] == "auto" else False #stabilization time mode for source: may take values [True - Auto, False - manual]
        s["delayduration"] = self.settings["delay"] #stabilization time duration if manual (may not be used in single channel mode)
        s["limit"] = self.settings["limit"] #limit for current in voltage mode or for voltage in current mode (may not be used in single channel mode)
        s["sourcehighc"] = self.smu_settings["sourcehighc"]

        if self.settings["sourcesensemode"] == "4 wire":
            s["sourcesense"] = True #source sence mode: may take values [True - 4 wire, False - 2 wire]
        else:
            s["sourcesense"] = False #source sence mode: may take values [True - 4 wire, False - 2 wire]

        if not s["single_ch"]:
            return [1, {"Error message":"SpecSMU plugin: dual channel mode not implemented"}]

            s["drainnplc"] = self.settings["drainnplc"] #drain NPLC (may not be used in single channel mode)
            s["draindelay"] = True if self.settings["draindelaymode"] == "auto" else False #stabilization time mode for source: may take values [True - Auto, False - manual]
            s["draindelayduration"] = self.settings["draindelay"] #stabilization time duration if manual (may not be used in single channel mode)
            s["drainlimit"] = self.settings["drainlimit"] #limit for current in voltage mode or for voltage in current mode (may not be used in single channel mode)
            s["drainhighc"] = self.smu_settings["drainhighc"]        
            if self.settings["drainsensemode"] == "4 wire":
                s["drainsense"] = True #source sence mode: may take values [True - 4 wire, False - 2 wire]
            else:
                s["drainsense"] = False #source sence mode: may take values [True - 4 wire, False - 2 wire]
        
        if self.function_dict["smu"]["smu_init"](s):
            return [2, {"Error message":"SpecSMU plugin: error in SMU plugin can not initialize"}]
        
        return {0, "OK"}
    
    def _SpecSMUImplementation(self):

        def set_integ_get_spectrum(integration_time):
            """Sets the integration time for the spectrometer and gets a spectrum."""
            status, message = self.function_dict["spectrometer"]["spectrometerSetIntegrationTime"](integration_time)
            if status:
                return [status, message]
            status, spectrum_option = self.function_dict["spectrometer"]["spectrometerGetScan"]()
            if status:
                return [status, spectrum_option]
            return [0, spectrum_option]
        self.smuInit()
        smuLoop = self.settings["points"]
        if smuLoop > 1:
            smuChange = (self.settings["end"] - self.settings["start"])/(smuLoop-1)
        else:
            smuChange = 0
        for smuLoopStep in range(smuLoop):
            # set smu set value according to current iteration.
            smuSetValue = self.settings["start"] + smuLoopStep*smuChange
            ####get spectrometer Integration time from settings

            integration_time_setting = self.spectrometer_settings["integrationTime"]
            print("------------------------")
            print(f"Integ time from spectro: {integration_time_setting}")

            ####get spectrometer Integration time
            ####if different
            ########## set integration time and get 1 spectrum (should be a function?)
            ####if auto integration time
            ########## run get integration time loop (more or less the getAutoTime function fom TLCCS), but with pauses if needed

            status, integration_time_seconds = self.function_dict["spectrometer"]["spectrometerGetIntegrationTime"]()
            print("------------------------")
            integration_time = integration_time_seconds
            print(f"Integ time from spectro read: {integration_time}")
            if status:
                raise NotImplementedError(f"Error in getting integration time from spectrometer: {integration_time}")
            

            if integration_time != integration_time_setting:

                # set and get spectrum
                status, spectrum = set_integ_get_spectrum(integration_time_setting)
                if status:
                    raise NotImplementedError(f"Error in setting integration time or getting spectrum: {spectrum}")
                # is this stupid???
            if self.spectrometer_settings["integrationtimetype"] == "auto":
                status, auto_time = self.function_dict["spectrometer"]["getAutoTime"]()
                print("auto")
                if not status:
                    integration_time_setting = auto_time
                    print(f"autotime found: {auto_time}")


                
            self.function_dict["smu"]["smu_outputON"](self.settings["channel"])
            self.function_dict["smu"]["smu_setOutput"](self.settings["channel"], 'v' if self.settings['inject']=='voltage' else 'i', smuSetValue)
            # get spectrum
            status, spectrum = self.function_dict["spectrometer"]["spectrometerGetScan"]()
            if status:
                raise NotImplementedError(f"Error in getting spectrum: {spectrum}")
            status, sourceIV = self.function_dict["smu"]["smu_getIV"](self.settings["channel"])
            self.function_dict["smu"]["smu_outputOFF"]()
            

            varDict = {}
            varDict['integrationtime'] = self.spectrometer_settings['integrationTime']
            varDict['triggermode'] = 1 if self.spectrometer_settings['externalTrigger'] else 0
            varDict['name'] = self.spectrometer_settings["samplename"]
            varDict['comment'] = str(sourceIV)
            address = self.spectrometer_settings["filename"] + f"_{smuSetValue:04f}" + " iv"
            self.function_dict["spectrometer"]["createFile"](varDict=varDict, filedelimeter=";",address=address, data=spectrum)
            
            ##measure
            ##save
        
        return 0