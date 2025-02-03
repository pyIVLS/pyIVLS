import os
from datetime import datetime
import time
import numpy as np
from MplCanvas import MplCanvas

from PyQt6 import uic
from PyQt6.QtWidgets import QFileDialog, QVBoxLayout
from PyQt6.QtCore import QObject, pyqtSignal

from sweepCommon import create_file_header, create_sweep_reciepe
from threadStopped import ThreadStopped, thread_with_exception


class sweepGUI(QObject):
    """Basic sweep module"""

####################################  threads

################################### internal functions

########Slots

########Signals

    log_message = pyqtSignal(str) 

########Functions

    def __init__(self):
        super(sweepGUI,self).__init__()
    
        # List of functions from another plugins required for functioning
        self.dependency = {
        "smu": ["parse_settings_widget", "smu_connect", "smu_init", "smu_runSweep", "smu_abort", "smu_outputOFF", "smu_getLastBufferValue", "smu_bufferRead"], 
        }
        
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        self.settingsWidget = uic.loadUi(self.path + "sweep_settingsWidget.ui")
        self.MDIWidget = uic.loadUi(self.path + "sweep_MDIWidget.ui")
        
        self._create_plt()      
        #self.measure = sweep()
        self._connect_signals()

    def _connect_signals(self):
        self.settingsWidget.directoryButton.clicked.connect(self._getAddress)
        self.settingsWidget.stopButton.clicked.connect(self._stopAction)
        self.settingsWidget.runButton.clicked.connect(self._runAction)
 
    def _create_plt(self):
    ##IRtodo#### make proper axes for displaying necessary curves
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.axes = self.sc.fig.add_subplot(111)

        layout = QVBoxLayout()
        layout.addWidget(self.sc._create_toolbar(self.MDIWidget))
        layout.addWidget(self.sc)
        self.MDIWidget.setLayout(layout)

########Functions
###############GUI setting up
    def _initGUI(self, plugin_info:"dictionary with settings obtained from plugin_data in pyIVLS_*_plugin"):
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK
        self.settingsWidget.lineEdit_path.setText(plugin_info["address"])
        self.settingsWidget.lineEdit_filename.setText(plugin_info["filename"])
        self.settingsWidget.lineEdit_sampleName.setText(plugin_info["samplename"])
        self.settingsWidget.lineEdit_comment.setText(plugin_info["comment"])
        try:
             intPlotUpdate = int(plugin_info["plotUpdate"])
        except:
             intPlotUpdate = 0       
        self.settingsWidget.spinBox_plotUpdate.setValue(intPlotUpdate)

    def _getAddress(self):
        address = self.settingsWidget.lineEdit_path.text()
        if not(os.path.exists(address)):
                address = self.path
        address = QFileDialog.getExistingDirectory(None, "Select directory for saving", self.path, options = QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks)
        if address:
                self.settingsWidget.lineEdit_path.setText(address)
                
    def _parse_settings_widget(self):
        """Parses the settings widget for the sweep. Extracts current values

        Returns [status]:
            status: 0 - no error, ~0 - error (add error code later on if needed)
        """   
        self.settings = {}
        self.settings["address"] = self.settingsWidget.lineEdit_path.text()
        self.settings["filename"] = self.settingsWidget.lineEdit_filename.text()
        self.settings["samplename"] = self.settingsWidget.lineEdit_sampleName.text()
        self.settings["comment"] = self.settingsWidget.lineEdit_comment.text()
        self.settings["plotUpdate"] = self.settingsWidget.spinBox_plotUpdate.value()

        ##IRtodo######### add here checks that the values are allowed
        return 0

########Functions
########plugins interraction
    def _getPublicFunctions(self,function_dict):
        missing_functions = []    
        for dependency_plugin in list(self.dependency.keys()):
                if not dependency_plugin in function_dict:
                        now = datetime.now()
                        self.log_message.emit(now.strftime("%H:%M:%S.%f") + f" : sweep plugin : Functions for dependency plugin '{dependency_plugin}' not found")
                        missing_functions.append(dependency_plugin)
                        continue
                for dependency_function in self.dependency[dependency_plugin]:
                        if not dependency_function in function_dict[dependency_plugin]:
                                now = datetime.now()
                                self.log_message.emit(now.strftime("%H:%M:%S.%f") + f" : sweep plugin : Function '{dependency_function}' for dependency plugin '{dependency_plugin}' not found")
                                missing_functions.append(f"{dependency_plugin}:{dependency_function}")
        if not missing_functions:
            self.settingsWidget.runButton.setEnabled(True)   
            self.function_dict = function_dict
        else:    
            self.settingsWidget.runButton.setDisabled(True)   
            self.function_dict = {}
        return missing_functions
        
    def _getLogSignal(self):
        return self.log_message
        
########Functions
########plugin actions   
    def _stopAction(self):
        self.settingsWidget.stopButton.setEnabled(False)
        self.run_thread.sweep_stop()
        
    def _runAction(self):
        ##IRtodo#### disable interface controls
        self.settingsWidget.stopButton.setEnabled(True)
        ##IRtodo#### check that the new file will not overwrite existing data -> show message

        #check data input by user by calling plugin functions
        self._parse_settings_widget()
        #no need to check if we have all the needed functions from the other plugins as they are already checked in _getPublicFunction
        [status, self.smu_settings] = self.function_dict["smu"]["parse_settings_widget"]()
        if status:
            self.log_message.emit(now.strftime("%H:%M:%S.%f") + f" : sweep plugin : error getting settings from smu plugin, status = {status}")
            return 1
        
        #check the needed devices are connected
        [status, message] = self.function_dict["smu"]["smu_connect"]()
        if status:
            self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : sweep plugin : {message}, status = {status}")
            return 1
        [recipe, drainsteps, sensesteps, modesteps] = create_sweep_reciepe(self.smu_settings)
        self.run_thread = thread_with_exception(self._sweepImplementation, (recipe, drainsteps, sensesteps, modesteps))
        self.run_thread.start()		

########Functions
########sweep implementation  
    #moving this into the sweepCommon feels to be tempting, but it may create some unreasonable overheads:
    	#1. plugin functions will need to be sent also
    	#2. updating the plot will require transfer of the handles
    #this makes this function not that independent, so in another sweep implementations it may be just copied as a block
    def _sweepImplementation(self, recipe, drainsteps, sensesteps, modesteps) :
    	try:
    		#initializaing SMU, may be moved into the loop, here it will save a bit of time
    		if  self.function_dict["smu"]["smu_init"](recipe[0]):
    				self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : sweep plugin : smu_init failed")
    				##IRtodo#### enable interface controls
    				return 1
    		data = np.array([])                
    		for recipeStep,measurement in enumerate(recipe):
    			#creating a new header
    			if recipeStep % (sensesteps*modesteps) == 0:
    				columnheader = ''
    				if not measurement["single_ch"]:
    					fileheader = create_file_header(self.settings, self.smu_settings, backVoltage = measurement["drainvoltage"])
    				else:	
    					fileheader = create_file_header(self.settings, self.smu_settings)
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
		                self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : sweep plugin : smu_runSweep failed")
		                ##IRtodo#### enable interface controls
		                return 1        
		                
	    		#plotting while measuring
	    		self.axes.cla()
	    		self.sc.draw()
	    		buffer_prev = 0
	    		while True:
      		    		time.sleep(self.settings["plotUpdate"])
      		    		##IRtodo#### plotting should be done for both source and drain
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
      		    			##IRtodo#### add stop before limit to GUI	
      		    			if (measurement["type"] == 'i' and (abs(lastV)> 0.95*abs(measurement["limit"])) ) or (measurement["type"] == 'i' and (abs(lastV)> 0.95*abs(measurement["limit"])) ):
      		    				self.function_dict["smu"]["smu_abort"](measurement["source"])
      		    				break
      		    			buffer_prev = lastPoints
	    		#### Keithley may produce a 5042 error, so make a delay here
	    		time.sleep(self.settings["plotUpdate"])
	    		self.function_dict["smu"]["smu_outputOFF"]()
	    		IV_source = self.function_dict["smu"]["smu_bufferRead"](measurement["source"])
	    		self.axes.cla()
	    		plot_refs = self.axes.plot(IV_source[:,1], IV_source[:,0], 'bo')
	    		if not measurement["single_ch"]:
	    			IV_drain = self.function_dict["smu"]["smu_bufferRead"](measurement["drain"])
	    			plot_refs = self.axes.plot(IV_source[:,1], IV_drain[:,0], 'go')
	    		self.sc.draw()
	    		if not measurement["single_ch"]:
	    			##IRtodo#### plotting should be done for both source and drain
	    			IV_drain = self.function_dict["smu"]["smu_bufferRead"](measurement["drain"])
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
	    			fulladdress = self.settings["address"] + os.sep + self.settings["filename"] + f"{drainvoltage}V"+".dat"
	    		else:
	    			fulladdress = self.settings["address"] + os.sep + self.settings["filename"] + ".dat"
	    		fulladdress = self.settings["address"] + self.settings["filename"] + ".dat"
	    		np.savetxt(fulladdress, data, fmt='%.8f', delimiter=',', newline='\n', header=fileheader + columnheader, comments='#')		
    	except ThreadStopped:
    		self.function_dict["smu"]["smu_abort"](measurement["source"])
    		self.function_dict["smu"]["smu_outputOFF"]()
