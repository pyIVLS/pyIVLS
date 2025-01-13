import os
from datetime import datetime
#from sweep import sweep
from MplCanvas import MplCanvas

from PyQt6 import uic
from PyQt6.QtWidgets import QFileDialog, QVBoxLayout
from PyQt6.QtCore import QObject, pyqtSignal

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
        "smu": ["parse_settings_widget", "test_communication"], 
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
 #       self.settingsWidget.stopButton.clicked.connect(self._stopAction)
        self.settingsWidget.runButton.clicked.connect(self._runAction)
 
    def _create_plt(self):
    ##IRtodo#### make proper axes for displaying necessary curves
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        axes = sc.fig.add_subplot(111)
        axes.plot([0,1,2,3,4], [10,1,20,3,40])

        layout = QVBoxLayout()
        layout.addWidget(sc._create_toolbar(self.MDIWidget))
        layout.addWidget(sc)
        self.MDIWidget.setLayout(layout)

########Functions
###############GUI setting up
    def _initGUI(self, plugin_info:"dictionary with settings obtained from plugin_data in pyIVLS_*_plugin"):
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK
        self.settingsWidget.lineEdit_path.setText(plugin_info["address"])
        self.settingsWidget.lineEdit_filename.setText(plugin_info["filename"])

    def _getAddress(self):
        address = self.settingsWidget.lineEdit_path.text()
        if not(os.path.exists(address)):
                address = self.path
        address = QFileDialog.getExistingDirectory(None, "Select directory for saving", self.path, options = QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks)
        if address:
                self.settingsWidget.lineEdit_path.setText(address)

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
    def _runAction(self):
        ##IRtodo#### disable interface controls
        ##IRtodo#### check that the new file will not overwrite existing data -> show message
        ##IRtodo#### check data input by user by calling plugin functions
        self.smu_settings = self.function_dict["smu"]["test_communication"]()
        print(self.smu_settings)
        ##IRtodo#### form file to save
        ##IRtodo#### check devices are connected
        ##IRtodo#### create a thread that will execute the run
                ##### this thred will handle all the measurements needs to be executed and will save the data        
                ##IRtodo#### form settings for device (select if it 2 or 4 wire, continuos or pulsed and call a plugin function to form settings)
                ##IRtodo#### init

