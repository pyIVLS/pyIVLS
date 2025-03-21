import os
from pathvalidate import is_valid_filename
from datetime import datetime
import time
import numpy as np

from PyQt6 import uic
from PyQt6.QtWidgets import QFileDialog, QVBoxLayout
from PyQt6.QtCore import QObject, pyqtSignal

from sweepCommon import create_file_header, create_sweep_reciepe
from threadStopped import thread_with_exception # this should be moved to some pluginsShare


class runSweepGUI(QObject):
    """Sequence for sweep module"""

####################################  threads

################################### internal functions

########Slots

########Signals

    log_message = pyqtSignal(str) 
    info_message = pyqtSignal(str) 
########Functions

    def __init__(self):
        super(runSweepGUI,self).__init__()
    
        # List of functions from another plugins required for functioning
        self.dependency = {
        "ivsweep": ["parse_settings_widget", "sweepImplementation", "smu_connect", "set_running"],  
        }
        
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        self.settingsWidget = uic.loadUi(self.path + "runSweep_settingsWidget.ui")
   
        self._connect_signals()

    def _connect_signals(self):
        self.settingsWidget.directoryButton.clicked.connect(self._getAddress)
        self.settingsWidget.stopButton.clicked.connect(self._stopAction)
        self.settingsWidget.runButton.clicked.connect(self._runAction)

########Functions
################################### internal
                
    def _parse_settings_widget(self):
        """Parses the settings widget for the sweep. Extracts current values

        Returns [status]:
            status: 0 - no error, ~0 - error (add error code later on if needed)
        """   
        self.settings = {}
        
        if not self.function_dict:
                self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : runsweep plugin : the plugin did not get all the neccessary functions from other plugins. List of missing functions {self.missing_functions}")
                self.info_message.emit(f"runsweep plugin : the plugin did not get all the neccessary functions. See log for fetails")
                return [3, self.missing_functions]
        self.settings["address"] = self.settingsWidget.lineEdit_path.text()
        if not os.path.isdir(self.settings["address"] + os.sep):
                self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : runsweep plugin : address string should point to a valid directory")
                self.info_message.emit(f"runsweep plugin : address string should point to a valid directory")
                return [1, "Value error"]           
        self.settings["filename"] = self.settingsWidget.lineEdit_filename.text()
        if not is_valid_filename(self.settings["filename"]):
                self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : runsweep plugin : filename is not valid")
                self.info_message.emit(f"runsweep plugin : filename is not valid")
                return [1, "Value error"]
               
        self.settings["samplename"] = self.settingsWidget.lineEdit_sampleName.text()
        self.settings["comment"] = self.settingsWidget.lineEdit_comment.text()

        return [0, "OK"]

########Functions
###############GUI setting up
    def _initGUI(self, plugin_info:"dictionary with settings obtained from plugin_data in pyIVLS_*_plugin"):
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK
        self.settingsWidget.lineEdit_path.setText(plugin_info["address"])
        self.settingsWidget.lineEdit_filename.setText(plugin_info["filename"])
        self.settingsWidget.lineEdit_sampleName.setText(plugin_info["samplename"])
        self.settingsWidget.lineEdit_comment.setText(plugin_info["comment"])

    def _getAddress(self):
        address = self.settingsWidget.lineEdit_path.text()
        if not(os.path.exists(address)):
                address = self.path
        address = QFileDialog.getExistingDirectory(None, "Select directory for saving", address, options = QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks)
        if address:
                self.settingsWidget.lineEdit_path.setText(address)

########Functions
###############GUI react to change

    def _set_running(self, status):
        self.settingsWidget.fileBox.setEnabled(not status)
        self.settingsWidget.stopButton.setEnabled(status)
        self.settingsWidget.runButton.setEnabled(not status)
        self.function_dict["ivsweep"]["set_running"](status)                
                        
########Functions
########plugins interraction
    def _getPublicFunctions(self,function_dict): 
        self.missing_functions = []    
        for dependency_plugin in list(self.dependency.keys()):
                if not dependency_plugin in function_dict:
                        self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : runSweep plugin : Functions for dependency plugin '{dependency_plugin}' not found")
                        self.missing_functions.append(dependency_plugin)
                        continue
                for dependency_function in self.dependency[dependency_plugin]:
                        if not dependency_function in function_dict[dependency_plugin]:
                                self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : runSweep plugin : Function '{dependency_function}' for dependency plugin '{dependency_plugin}' not found")
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
########plugin actions   
    def _stopAction(self):
        self.settingsWidget.stopButton.setEnabled(False)
        self.run_thread.thread_stop()
        
    def _runAction(self):
        
        #### disable interface controls. It is important to disable interfaces befor getting the data from them to assure that the input is not changed after it was checked
        self._set_running(True)
        [status, message] = self._parse_settings_widget()
        if status:
                #### enable the interface
                self._set_running(False)
                return 1
        [status, self.sweep_settings] = self.function_dict["ivsweep"]["parse_settings_widget"]()
        if status:
                if status == 2:
                        self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : runsweep : the sweep plugin reported an error in a dependent plugin: {self.sweep_settings}")
                        self.info_message.emit(self.sweep_settings["Error message"])
                else:
                        self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f' : runsweep : the sweep plugin reported an error: {self.sweep_settings["Error message"]}')
                        self.info_message.emit(self.sweep_settings["Error message"])
                #### enable the interface
                self._set_running(False)
                return 1

        #check the needed devices are connected
        [status, message] = self.function_dict["ivsweep"]["smu_connect"]()
        if status:
            self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : runsweep plugin : {message}, status = {status}")
            self.info_message.emit(f"Can not connect to smu")
            #### enable the interface
            self._set_running(False)
            return 1

        ##IRtodo#### check that the new file will not overwrite existing data -> implement dialog

        self.run_thread = thread_with_exception(self._sequenceImplementation)
        self.run_thread.start()		

########Functions
########sequence implementation  
    def _sequenceImplementation(self) :
    	try:
                [status, message] = self.function_dict["ivsweep"]["sweepImplementation"](self.settings)
                if status:
                        self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f' : runsweep : sweep implementation failed: {message}')
                        self.info_message.emit(f'Sweep implementation failed. See log') 
                        try:
                                self.function_dict["ivsweep"]["smu_abort"]()
                                self.function_dict["ivsweep"]["smu_outputOFF"]()
                                self.function_dict["ivsweep"]["smu_disconnect"]()
                        except:
                                self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f' : runsweep : smu turn off failed')
                                self.info_message.emit(f'SMU turn off failed')                                                         
    	except ThreadStopped:
                        try:
                                self.function_dict["ivsweep"]["smu_abort"]()
                                self.function_dict["ivsweep"]["smu_outputOFF"]()
                                self.function_dict["ivsweep"]["smu_disconnect"]()
                        except:
                                self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f' : runsweep : smu turn off failed')
                                self.info_message.emit(f'SMU turn off failed')
    	finally:
                        #### enable the interface
                        self._set_running(False)
                                
