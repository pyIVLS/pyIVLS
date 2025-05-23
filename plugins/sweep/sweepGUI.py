import os
import time
import numpy as np
from MplCanvas import MplCanvas # this should be moved to some pluginsShare

from PyQt6 import uic
from PyQt6.QtWidgets import QVBoxLayout

from sweepCommon import create_file_header, create_sweep_reciepe

class sweepGUI():
    """Basic sweep module"""
    non_public_methods = [] # add function names here, if they should not be exported as public to another plugins
<<<<<<< Updated upstream
=======
    public_methods = ["parse_settings_widget", "set_running", "setSettings", "sequenceStep"] # necessary for descendents of QObject, otherwise _get_public_methods returns a lot of QObject methods
>>>>>>> Stashed changes
####################################  threads

################################### internal functions

########Slots

########Signals
 
########Functions

    def __init__(self):  
        # List of functions from another plugins required for functioning
        self.dependency = {
        "smu": ["parse_settings_widget", "smu_connect", "smu_init", "smu_runSweep", "smu_abort", "smu_outputOFF", "smu_disconnect","smu_getLastBufferValue", "smu_bufferRead", "set_running"], 
        }
        
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        self.settingsWidget = uic.loadUi(self.path + "sweep_settingsWidget.ui")
        self.MDIWidget = uic.loadUi(self.path + "sweep_MDIWidget.ui")
        
        self._create_plt()      

    def _create_plt(self):
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.axes = self.sc.fig.add_subplot(111)
       
        self.axes.set_xlabel('Voltage (V)')
        self.axes.set_ylabel('Current (A)')

        layout = QVBoxLayout()
        layout.addWidget(self.sc._create_toolbar(self.MDIWidget))
        layout.addWidget(self.sc)
        self.MDIWidget.setLayout(layout)

########Functions
###############GUI setting up

    def _initGUI(self, plugin_info:"dictionary with settings obtained from plugin_data in pyIVLS_*_plugin"):
<<<<<<< Updated upstream
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK
=======
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

>>>>>>> Stashed changes
        try:
             intPlotUpdate = int(plugin_info["plotUpdate"])
        except:
             intPlotUpdate = 0       
        self.settingsWidget.spinBox_plotUpdate.setValue(intPlotUpdate)
        self.settingsWidget.prescalerEdit.setText(plugin_info["prescaler"])

<<<<<<< Updated upstream
=======
        self.settingsWidget.lineEdit_path.setText(plugin_info["address"])
        self.settingsWidget.lineEdit_filename.setText(plugin_info["filename"])
        self.settingsWidget.lineEdit_sampleName.setText(plugin_info["samplename"])
        self.settingsWidget.lineEdit_comment.setText(plugin_info["comment"])

    def _setGUIfromSettings(self):
        ##populates GUI with values stored in settings
        if self.settings["singlechannel"]:
            self.settingsWidget.checkBox_singleChannel.setChecked(True)
        else:
            self.settingsWidget.checkBox_singleChannel.setChecked(True)
        currentIndex = self.settingsWidget.comboBox_channel.findText(self.settings["channel"], Qt.MatchFlag.MatchFixedString)
        if currentIndex > -1:
           self.settingsWidget.comboBox_channel.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_inject.findText(self.settings["inject"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_inject.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_mode.findText(self.settings["mode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_mode.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_continuousDelayMode.findText(self.settings["continuousdelaymode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_continuousDelayMode.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_pulsedDelayMode.findText(self.settings["pulseddelaymode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_pulsedDelayMode.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_drainDelayMode.findText(self.settings["draindelaymode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_drainDelayMode.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_sourceSenseMode.findText(self.settings["sourcesensemode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_sourceSenseMode.setCurrentIndex(currentIndex)
        currentIndex = self.settingsWidget.comboBox_drainSenseMode.findText(self.settings["drainsensemode"])
        if currentIndex > -1:
           self.settingsWidget.comboBox_drainSenseMode.setCurrentIndex(currentIndex)
        self.settingsWidget.lineEdit_repeat.setText(f"{self.settings['repeat']}")
        self.settingsWidget.lineEdit_continuousStart.setText(f"{self.settings['continuousstart']}")
        self.settingsWidget.lineEdit_continuousEnd.setText(f"{self.settings['continuousend']}")
        self.settingsWidget.lineEdit_continuousPoints.setText(f"{self.settings['continuouspoints']}")
        self.settingsWidget.lineEdit_continuousLimit.setText(f"{self.settings['continuouslimit']}")
        self.settingsWidget.lineEdit_continuousNPLC.setText(f"{self.settings['continuousnplc']}")
        self.settingsWidget.lineEdit_continuousDelay.setText(f"{self.settings['continuousdelay']}")
        self.settingsWidget.lineEdit_pulsedStart.setText(f"{self.settings['pulsedstart']}")
        self.settingsWidget.lineEdit_pulsedEnd.setText(f"{self.settings['pulsedend']}")
        self.settingsWidget.lineEdit_pulsedPoints.setText(f"{self.settings['pulsedpoints']}")
        self.settingsWidget.lineEdit_pulsedLimit.setText(f"{self.settings['pulsedlimit']}")
        self.settingsWidget.lineEdit_pulsedNPLC.setText(f"{self.settings['pulsednplc']}")
        self.settingsWidget.lineEdit_pulsedPause.setText(f"{self.settings['pulsedpause']}")
        self.settingsWidget.lineEdit_pulsedDelay.setText(f"{self.settings['pulseddelay']}")
        self.settingsWidget.lineEdit_drainStart.setText(f"{self.settings['drainstart']}")
        self.settingsWidget.lineEdit_drainEnd.setText(f"{self.settings['drainend']}")
        self.settingsWidget.lineEdit_drainPoints.setText(f"{self.settings['drainpoints']}")
        self.settingsWidget.lineEdit_drainLimit.setText(f"{self.settings['drainlimit']}")
        self.settingsWidget.lineEdit_drainNPLC.setText(f"{self.settings['drainnplc']}")
        self.settingsWidget.lineEdit_drainDelay.setText(f"{self.settings['draindelay']}")

        # update to the correct GUI state
        self._update_GUI_state()

        self.settingsWidget.spinBox_plotUpdate.setValue(self.settings["plotUpdate"])
        self.settingsWidget.prescalerEdit.setText(f"{self.settings['prescaler']}")

        self.settingsWidget.lineEdit_path.setText(self.settings["address"])
        self.settingsWidget.lineEdit_filename.setText(self.settings["filename"])
        self.settingsWidget.lineEdit_sampleName.setText(self.settings["samplename"])
        self.settingsWidget.lineEdit_comment.setText(self.settings["comment"])

        
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
             self.settingsWidget.groupBox_drainSweep.setEnabled(False)
        else:     
             self.settingsWidget.groupBox_drainSweep.setEnabled(True)

        self.settingsWidget.update()

>>>>>>> Stashed changes
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
            self.settingsWidget.runButton.setEnabled(True)   
            self.function_dict = function_dict
        else:    
            self.settingsWidget.runButton.setDisabled(True)   
            self.function_dict = {}
        return self.missing_functions
        
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

<<<<<<< Updated upstream
                
=======
    def _getLogSignal(self):
        return self.log_message

    def _getInfoSignal(self):
        return self.info_message
        
    def _getCloseLockSignal(self):
        return self.closeLock

>>>>>>> Stashed changes
########Functions to be used externally
###############get settings from GUI 
    def parse_settings_widget(self):
        """Parses the settings widget for the plugin. Extracts current values. Checks if values are allowed. Provides settings of sweep plugin to an external plugin

        Returns [status, settings_dict]:
            status: 0 - no error, ~0 - error
            self.settings
        """     
        if not self.function_dict:
                return [3,  {"Error message": f"Missing functions in sweep plugin : {self.missing_functions}"]

        self.settings["plotUpdate"] = self.settingsWidget.spinBox_plotUpdate.value()
        try:
                self.settings["prescaler"] = float(self.settingsWidget.prescalerEdit.text())
        except ValueError:
                return [1, {"Error message":"Value error in sweep plugin: SMU limit prescaler field should be numeric"}]
        if self.settings["prescaler"]>1:
                return [1, {"Error message":"Value error in sweep plugin: SMU limit prescaler can not be greater than 1"}]
        if self.settings["prescaler"]<=0:
                return [1, {"Error message":"Value error in sweep plugin: SMU limit prescaler should be greater than 0"}]

        [status, self.smu_settings] = self.function_dict["smu"]["parse_settings_widget"]()
        if status:
            return [2, self.smu_settings]

        return [0, self.settings]

<<<<<<< Updated upstream
###############provide smu functions to sequence to handle excetions 
    def smu_connect(self):
            return self.function_dict["smu"]["smu_connect"]()

    def smu_disconnect(self):
            return self.function_dict["smu"]["smu_disconnect"]()

    def smu_abort(self):
            return self.function_dict["smu"]["smu_abort"]()

    def smu_outputOFF(self):
            return self.function_dict["smu"]["smu_outputOFF"]()

=======
    def setSettings(self, settings):
        self.settings = settings
        self._setGUIfromSettings()
>>>>>>> Stashed changes
###############GUI enable/disable

    def set_running(self, status):
        self.settingsWidget.groupBox.setEnabled(not status)
        self.function_dict["smu"]["set_running"](status)
        
########sweep implementation  
    def sweepImplementation(self, file_settings):
    	"""
    	Performs an IV sweep on SMU, saves the result in a file
    	Input: dict
    	        file_settings["address"] - address to save the result
    	        file_settings["filename"] - filename to use
    	        file_settings["samplename"] - data for the header
    	        file_settings["comment"] - date for the header
    	        
    	Returns [status, message]:
            status: 0 - no error, ~0 - error
    	"""
    	try:
                [recipe, drainsteps, sensesteps, modesteps] = create_sweep_reciepe(self.smu_settings)
    		if  self.function_dict["smu"]["smu_init"](recipe[0]):
    				return [1, f"sweep plugin : smu_init failed"]
    		data = np.array([])                
    		for recipeStep,measurement in enumerate(recipe):
    			#creating a new header
    			if recipeStep % (sensesteps*modesteps) == 0:
    				columnheader = ''
    				if not measurement["single_ch"]:
    					fileheader = create_file_header(file_settings, self.smu_settings, backVoltage = measurement["drainvoltage"])
    				else:	
    					fileheader = create_file_header(file_settings, self.smu_settings)
	    		if measurement["sourcesense"]:
	    			columnheader = f"{columnheader}IS_4pr, VS_4pr,"
	    		else:	
	    			columnheader = f"{columnheader}IS_2pr, VS_2pr,"
	    		if not measurement["single_ch"]:
	    			if measurement["drainsense"]:
		    			columnheader = f"{columnheader}ID_4pr, VD_4pr,"
		    		else:	
		    			columnheader = f"{columnheader}ID_2pr, VD_2pr,"
	    		#running sweep
	    		if  self.function_dict["smu"]["smu_runSweep"](measurement):
		                return [1, f"sweep plugin : smu_runSweep failed"]
		                
	    		#plotting while measuring
	    		self.axes.cla()
	    		self.axes.set_xlabel('Voltage (V)')
	    		self.axes.set_ylabel('Current (A)')
	    		self.sc.draw()
	    		buffer_prev = 0
	    		while True:
      		    		time.sleep(self.settings["plotUpdate"])
      		    		[lastI, lastV, lastPoints] = self.function_dict["smu"]["smu_getLastBufferValue"](measurement["source"])
      		    		if lastPoints >= measurement["steps"]*measurement["repeat"]:
      		    			break
      		    		if lastPoints >	buffer_prev:
      		    			if buffer_prev == 0:
      		    				Xdata_source = [lastV]
      		    				Ydata_source = [lastI]
      		    				plot_refs = self.axes.plot(Xdata_source, Ydata_source, 'bo')
      		    				_plot_ref_source = plot_refs[0]
      		    				if not measurement["single_ch"]:
      		    					[lastI_drain, lastV_drain, lastPoints_drain] = self.function_dict["smu"]["smu_getLastBufferValue"](measurement["source"], lastPoints)
      		    					Xdata_drain = [lastV]
      		    					Ydata_drain = [lastI]
      		    					plot_refs = self.axes.plot(Xdata_drain, Ydata_drain, 'go')
      		    					_plot_ref_drain = plot_refs[0]
      		    			else:
      		    				Xdata_source.append(lastV)
      		    				Ydata_source.append(lastI)
      		    				_plot_ref_source.set_xdata(Xdata_source)
      		    				_plot_ref_source.set_ydata(Ydata_source)
      		    				if not measurement["single_ch"]:
      		    					[lastI_drain, lastV_drain, lastPoints_drain] = self.function_dict["smu"]["smu_getLastBufferValue"](measurement["drain"], lastPoints)
      		    					Xdata_drain.append(lastV_drain)
      		    					Ydata_drain.append(lastI_drain)
      		    					_plot_ref_drain.set_xdata(Xdata_source)
      		    					_plot_ref_drain.set_ydata(Ydata_drain)
      		    			self.axes.relim()
      		    			self.axes.autoscale_view()
      		    			self.sc.draw()
      		    			if (measurement["type"] == 'i' and (abs(lastV)> self.settings["prescaler"]*abs(measurement["limit"])) ) or (measurement["type"] == 'i' and (abs(lastV)> self.settings["prescaler"]*abs(measurement["limit"])) ):
      		    				self.function_dict["smu"]["smu_abort"](measurement["source"])
      		    				break
      		    			buffer_prev = lastPoints
	    		#### Keithley may produce a 5042 error, so make a delay here
	    		time.sleep(self.settings["plotUpdate"])
	    		self.function_dict["smu"]["smu_outputOFF"]()
	    		IV_source = self.function_dict["smu"]["smu_bufferRead"](measurement["source"])
	    		self.axes.cla()
	    		self.axes.set_xlabel('Voltage (V)')
	    		self.axes.set_ylabel('Current (A)')
	    		plot_refs = self.axes.plot(IV_source[:,1], IV_source[:,0], 'bo')
	    		if not measurement["single_ch"]:
	    			IV_drain = self.function_dict["smu"]["smu_bufferRead"](measurement["drain"])
	    			plot_refs = self.axes.plot(IV_source[:,1], IV_drain[:,0], 'go')
	    		self.sc.draw()
	    		IVresize = 0	
	    		if data.size == 0:
	    			data = IV_source
	    		else:
	    			dataLength = np.size(data,0)
	    			IVLength = np.size(IV_source,0)
	    			if dataLength < IVLength:
	    				data = np.vstack([data, np.full((IVLength - dataLength, np.size(data,1)), "")])
	    			else:	
	    				IVresize = dataLength - IVLength
	    				IV_source = np.vstack([IV_source, np.full((IVresize, 2), "")])
	    			data = np.hstack([data, IV_source])	
	    		if not measurement["single_ch"]:
	    			if IVresize:
	    				IV_drain = np.vstack([IV_drain, np.full((IVresize, 2), "")])
	    			data = np.hstack([data, IV_drain])	
	    		columnheader = f"{columnheader[:-1]}"
	    		if drainsteps > 1:
	    			fulladdress = file_settings["address"] + os.sep + file_settings["filename"] + f"{drainvoltage}V"+".dat"
	    		else:
	    			fulladdress = file_settings["address"] + os.sep + file_settings["filename"] + ".dat"
	    		fulladdress = file_settings["address"] + file_settings["filename"] + ".dat"
	    		np.savetxt(fulladdress, data, fmt='%.8f', delimiter=',', newline='\n', header=fileheader + columnheader, comments='#')
    		return [0, "sweep finished"]
<<<<<<< Updated upstream
=======

    def _sequenceStep(self, postfix):
        self.settings["filename"] = self.settings["filename"] + postfix
        [status, message] = self.function_dict["smu"]["smu_connect"]()
        if status:
            return [status, message]
        self._sweepImplementation()
        self.function_dict["smu"]["smu_disconnect"]()
        return [0, "sweep finished"]

    def _sequenceImplementation(self):
    	"""
    	Performs an IV sweep on SMU, saves the result in a file
    	        
    	Returns [status, message]:
            status: 0 - no error, ~0 - error
    	"""    	
    	try:
    		exception = 0 #handling turning off smu in case of exceptions. 0 = no exception, 1 - failure in smu, 2 - threadStopped, 3 - unexpected
    		self._sweepImplementation()
    	except sweepException as e:
    		self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f'{e}')
    		exception = 1
    	except ThreadStopped:
    	        self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f': sweep plugin implementation aborted')
    	        exception = 2
>>>>>>> Stashed changes
    	except Exception as e:
    		return [1, f"sweep stopped because of unexpected exception: {e}"]
