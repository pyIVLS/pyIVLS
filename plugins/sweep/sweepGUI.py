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
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK
        try:
             intPlotUpdate = int(plugin_info["plotUpdate"])
        except:
             intPlotUpdate = 0       
        self.settingsWidget.spinBox_plotUpdate.setValue(intPlotUpdate)
        self.settingsWidget.prescalerEdit.setText(plugin_info["prescaler"])

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
        """Parses the settings widget for the plugin. Extracts current values. Checks if values are allowed. Provides settings of sweep plugin to an external plugin

        Returns [status, settings_dict]:
            status: 0 - no error, ~0 - error
            self.settings
        """     
        if not self.function_dict:
                return [3,  {"Error message": f"Missing functions in sweep plugin : {self.missing_functions}"}]
        self.settings = {}

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

###############provide smu functions to sequence to handle excetions 
    def smu_connect(self):
            return self.function_dict["smu"]["smu_connect"]()

    def smu_disconnect(self):
            return self.function_dict["smu"]["smu_disconnect"]()

    def smu_abort(self):
            return self.function_dict["smu"]["smu_abort"]()

    def smu_outputOFF(self):
            return self.function_dict["smu"]["smu_outputOFF"]()

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
    				return [2, f"sweep plugin : smu_init failed"]
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
    	except Exception as e:
    		return [1, f"sweep stopped because of unexpected exception: {e}"]
