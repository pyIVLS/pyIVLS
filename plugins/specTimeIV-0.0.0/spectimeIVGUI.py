"""
This is a timeIV plugin implementation for pyIVLS

The function of the plugin is to measure current and voltage change in time

This file should provide
- functions that will implement functionality of the hooks (see pyIVLS_timeIVGUI)
- GUI functionality - code that interracts with Qt GUI elements from widgets

"""

import os
import time
import copy
from datetime import datetime
from pathvalidate import is_valid_filename
from PyQt6 import uic
from PyQt6.QtWidgets import QVBoxLayout, QFileDialog, QWidget
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from MplCanvas import MplCanvas  # this should be moved to some pluginsShare
from threadStopped import thread_with_exception, ThreadStopped
from enum import Enum
from specTimeIV_utils import LoggingHelper, FileManager, GuiMapper, DependencyManager

# DynamicGuiFieldMapper available for future use
import numpy as np
import pandas as pd


class timeIVexception(Exception):
    pass


#
class dataOrder(Enum):
    V = 1
    I = 0


class specTimeIVGUI:
    """GUI implementation
    this class may be a child of QObject if Signals or Slot will be needed
    """

    non_public_methods = []  # add function names here, if they should not be exported as public to another plugins
    public_methods = ["parse_settings_widget", "set_running", "setSettings", "sequenceStep", "set_gui_from_settings"]  # necessary for descendents of QObject, otherwise _get_public_methods returns a lot of QObject methods

    ########Functions
    def __init__(self):
        # List of functions from another plugins required for functioning
        self.dependency: dict[str, list[str]] = {
            "smu": [
                "parse_settings_widget",
                "smu_connect",
                "smu_init",
                "smu_outputOFF",
                "smu_outputON",
                "smu_disconnect",
                "set_running",
                "smu_setOutput",
                "smu_channelNames",
                #"A very necessary function",  
            ],
            "spectrometer": ["parse_settings_preview", "setSettings", "spectrometerConnect", "spectrometerDisconnect", "spectrometerSetIntegrationTime", "spectrometerGetIntegrationTime", "spectrometerStartScan", "spectrometerGetSpectrum", "spectrometerGetScan"],
        }
        self.settings = {}

        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep

        self.settingsWidget: QWidget = uic.loadUi(self.path + "specTimeIV.ui")
        self.MDIWidget: QWidget = uic.loadUi(self.path + "specTimeIV_MDIWidget.ui")

        # stop yelling at me linter
        assert self.settingsWidget is not None, "Failed to load settingsWidget UI"
        assert self.MDIWidget is not None, "Failed to load MDIWidget UI"

        # remove next if no plots
        self._create_plt()
        self.filemanager = FileManager()
        self.logger = LoggingHelper(self)

        # Initialize dependency manager
        self.dependency_manager = DependencyManager(
            plugin_name=self.__class__.__name__,
            dependencies=self.dependency,
            widget=self.settingsWidget,
            mapping={
            "smu": "smuBox",
            "spectrometer": "spectroBox",
            }
        )
        
        self.dynamic_mapper = GuiMapper(self.settingsWidget, self.__class__.__name__)
        self._setup_dynamic_mappings()

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
        self.settingsWidget.smuBox.currentIndexChanged.connect(self._update_smu_channels)

    def _update_smu_channels(self):
        smu_plugin = self.dependency_manager.get_selected_dependencies().get("smu")
        if smu_plugin:
            # fetch channels from the selected SMU plugin and update the channel combobox
            channels = self.dependency_manager.function_dict["smu"][smu_plugin]["smu_channelNames"]()
            self.settingsWidget.comboBox_channel.clear()
            self.settingsWidget.comboBox_channel.addItems(channels)
            # if the channel in the settings is not in the list, reset it to the first available channel
            current_channel = self.settings.get("channel", "")
            if current_channel not in channels:
                self.settingsWidget.comboBox_channel.setCurrentIndex(0)
            else:
                self.settingsWidget.comboBox_channel.setCurrentText(current_channel)

    def _create_plt(self):
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.axes = self.sc.fig.add_subplot(111)

        self.axes_twinx = self.axes.twinx()
        self.axes.set_xlabel("Time (s)")
        self.axes.set_ylabel("Voltage (V)")
        self.axes_twinx.set_ylabel("Current (A)")

        layout = QVBoxLayout()
        layout.addWidget(self.sc._create_toolbar(self.MDIWidget))
        layout.addWidget(self.sc)
        self.MDIWidget.setLayout(layout)

    def _setup_dynamic_mappings(self, line_frequency=50):
        """Setup dynamic field mappings - simplified approach with just widget mapping."""

        # Simple field mapping: setting_name -> widget_name
        self.dynamic_field_mapping = {
            # Basic file and timing settings
            "address": "lineEdit_path",
            "filename": "lineEdit_filename",
            "samplename": "lineEdit_sampleName",
            "comment": "lineEdit_comment",
            "timestep": "step_lineEdit",
            "stopafter": "stopAfterLineEdit",
            "autosaveinterval": "autosaveLineEdit",
            "stoptimer": "stopTimerCheckBox",
            "autosave": "autosaveCheckBox",
            # SMU configuration
            "singlechannel": "checkBox_singleChannel",
            "channel": "comboBox_channel",
            "inject": "comboBox_inject",
            "sourcedelaymode": "comboBox_sourceDelayMode",
            "sourcesensemode": "comboBox_sourceSenseMode",
            "draindelaymode": "comboBox_drainDelayMode",
            "draininject": "comboBox_drainInject",
            "drainsensemode": "comboBox_drainSenseMode",
            # SMU values (will need conversion for some)
            "sourcevalue": "lineEdit_sourceSetValue",
            "sourcelimit": "lineEdit_sourceLimit",
            "sourcenplc": "lineEdit_sourceNPLC",  
            "sourcedelay": "lineEdit_sourceDelay",  
            "drainvalue": "lineEdit_drainSetValue",
            "drainlimit": "lineEdit_drainLimit",
            "drainnplc": "lineEdit_drainNPLC",  
            "draindelay": "lineEdit_drainDelay",  
            "smu": "smuBox",
            "spectrometer": "spectroBox"
        }  
        
        # Validation and conversion rules for extracting values from GUI
        # FIXME: The validation rules contain a magic constant for line frequency
        self.dynamic_validation_rules = {
            "address": {"validator": lambda x: isinstance(x, str) and len(x.strip()) > 0 and os.path.exists(x), "error_message": "Address is required"},
            "filename": {"validator": lambda x: isinstance(x, str) and is_valid_filename(x), "error_message": "filename must be a valid filename"},
            "timestep": {"validator": lambda x: isinstance(x, (float)) and x > 0, "error_message": "Time step must be positive"},
            "stopafter": {"validator": lambda x: isinstance(x, (float)) and x > 0, "error_message": "Stop time must be positive"},
            "autosaveinterval": {"validator": lambda x: isinstance(x, (float)) and x > 0, "error_message": "Auto save interval must be positive"},
            "sourcelimit": {"validator": lambda x: isinstance(x, (float)) and x > 0, "error_message": "Source limit must be positive"},
            "drainlimit": {"validator": lambda x: isinstance(x, (float)) and x > 0, "error_message": "Drain limit must be positive"},
            "sourcenplc": {
                "converter": lambda x: float(x) * 0.001 * line_frequency,
                "display_converter": lambda x: float(x) / (0.001 * line_frequency),
                "validator": lambda x: isinstance(x, (float)) and x > 0,
                "error_message": "Source NPLC must be positive"
            },
            "sourcedelay": {
                "converter": lambda x: float(x) / 1000,
                "display_converter": lambda x: float(x) * 1000,
                "validator": lambda x: isinstance(x, (float)) and x > 0,
                "error_message": "Source delay must be positive"
            },
            "drainnplc": {
                "converter": lambda x: float(x) * 0.001 * line_frequency,
                "display_converter": lambda x: float(x) / (0.001 * line_frequency),
                "validator": lambda x: isinstance(x, (float)) and x > 0,
                "error_message": "Drain NPLC must be positive"
            },
            "draindelay": {
                "converter": lambda x: float(x) / 1000,
                "display_converter": lambda x: float(x) * 1000,
                "validator": lambda x: isinstance(x, (float)) and x > 0,
                "error_message": "Drain delay must be positive"
            },
        }
        

    ########Functions
    ########GUI Slots

    ########Functions
    ################################### internal

    def set_gui_from_settings(self):
        """
        Updates the GUI fields based on the internal settings dictionary.
        This function assumes that the settings have already been set using the `setSettings` function.
        """
        # Use dynamic mapper to set all GUI values with automatic conversion
        status, error_msg = self.dynamic_mapper.set_values(
            self.settings, 
            self.dynamic_field_mapping,
            self.dynamic_validation_rules 
        )
        
        if status != 0:
            self.logger.log_warn(f"Error setting GUI values: {error_msg}")
            self.logger.info_popup(f"Error setting GUI values: {error_msg}")

        self._update_GUI_state()

    def parse_settings_widget(self) -> tuple[int, dict[str, str|float|bool]]:
        """Parses the settings widget for the templatePlugin. Extracts current values. Checks if values are allowed. Provides settings of template plugin to an external plugin

        Returns [status, settings_dict]:
            status: 0 - no error, ~0 - error 
            self.settings
        """
        if not self.dependency_manager.function_dict:
            return (3, {"Error message": "Missing functions in timeIV plugin. Check log", "Missing functions": self.missing_functions})

        # Get selected dependencies
        selected_deps = self.dependency_manager.get_selected_dependencies()
        
        # Validate SMU selection
        if "smu" in selected_deps:
            smu_selection = selected_deps["smu"]
            is_valid, error_msg = self.dependency_manager.validate_selection("smu", smu_selection)
            if not is_valid:
                return (3, {"Error message": f"SMU validation failed: {error_msg}"})
                
            self.settings["smu"] = smu_selection
            status, self.smu_settings = self.dependency_manager.function_dict["smu"][smu_selection]["parse_settings_widget"]()
            if status:
                return (2, self.smu_settings)
        else:
            return (3, {"Error message": "No SMU plugin selected"})

        # Validate spectro selection
        if "spectro" in selected_deps:
            spectro_selection = selected_deps["spectro"]
            is_valid, error_msg = self.dependency_manager.validate_selection("spectro", spectro_selection)
            if not is_valid:
                return (3, {"Error message": f"Spectro validation failed: {error_msg}"})
                
            self.settings["spectro"] = spectro_selection
            status, self.spectro_settings = self.dependency_manager.function_dict["spectro"][spectro_selection]["parse_settings_widget"]()
            if status:
                return (2, self.spectro_settings)
        else:
            # Spectro might be optional, so just log a warning
            self.logger.log_warn("No spectro plugin selected")
        

        # Use mapper component for value extraction and validation
        status, all_values = self.dynamic_mapper.get_values(self.dynamic_field_mapping, self.dynamic_validation_rules)
        if status:
            return (status, all_values)

        # Update settings with extracted values
        self.settings.update(all_values)

        # Handle dual channel logic
        currentIndex = self.settingsWidget.comboBox_channel.currentIndex()
        if self.settingsWidget.comboBox_channel.count() > 1:
            if currentIndex == 0:
                self.settings["drainchannel"] = self.settingsWidget.comboBox_channel.itemText(1)
            else:
                self.settings["drainchannel"] = self.settingsWidget.comboBox_channel.itemText(0)
        else:
            self.settings["drainchannel"] = "xxx"  # for compatibility if the smu does not support second channel

        retset = self.settings
        retset["smu_settings"] = self.smu_settings
        return (0, retset)

    ########Functions
    ###############GUI setting up
    def _initGUI(
        self,
        plugin_settings: dict[str, str|float|bool],
    ):
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK
        self.logger.log_debug("Initializing GUI with plugin_settings: " + str(plugin_settings))
        self.setSettings(plugin_settings)  # Update settings with plugin_settings

        self.set_gui_from_settings()  # update to the correct GUI state
        self.set_running(False)
        self._connect_signals()
        self._update_GUI_state()

    def _getAddress(self):
        address = self.settingsWidget.lineEdit_path.text()
        if not (os.path.exists(address)):
            address = self.path
        address = QFileDialog.getExistingDirectory(
            None,
            "Select directory for saving",
            address,
            options=QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks,
        )
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
        self._update_smu_channels()  # Update SMU channels based on current selection

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

    def set_running(self, status):
        # status == True the measurement is running
        self.settingsWidget.stopButton.setEnabled(status)
        self.settingsWidget.runButton.setEnabled(not status)

        self.settingsWidget.groupBox.setEnabled(not status)
        self.settingsWidget.groupBox_SMUGeneral.setEnabled(not status)
        self.settingsWidget.fileBox.setEnabled(not status)

        if status:
            self._update_GUI_state()

    ########Functions
    ########plugins interraction
    def _getPublicFunctions(self, function_dict):
        # Set function dict in dependency manager (this will automatically update comboboxes)
        self.dependency_manager.function_dict = function_dict
        
        # Validate dependencies
        is_valid, missing_functions = self.dependency_manager.validate_dependencies()
        
        if is_valid:
            self.logger.log_debug("All dependencies satisfied")
            self.settingsWidget.runButton.setEnabled(True)
            self.missing_functions = []
        else:
            self.logger.log_warn(f"Missing dependencies: {missing_functions}")
            self.settingsWidget.runButton.setDisabled(True)
            self.missing_functions = missing_functions
            
        return self.missing_functions

    def setSettings(self, settings):
        """Sets the settings for the plugin. Workflow from seqBuilder:
        1. Parse_settings_widget is called when step added to sequence
        2. When running, set_settings is called to set the settings for the plugin

        Args:
            settings (dict): outputs from parse_settings_widget function
        """
        self.logger.log_debug("Setting settings for timeIV plugin: " + str(settings))
        
        # Check if settings might be string values (from external import)

        self.settings = copy.deepcopy(settings)
            
        # Handle SMU settings separately
        if "smu_settings" in settings:
            self.smu_settings = settings["smu_settings"]


    def _get_public_methods(self):
        """
        Returns a nested dictionary of public methods for the plugin
        """
        # if the plugin type matches the requested type, return the functions

        methods = {method: getattr(self, method) for method in dir(self) if callable(getattr(self, method)) and not method.startswith("__") and not method.startswith("_") and method not in self.non_public_methods and method in self.public_methods}
        return methods

    ########Functions
    ############### run preparations
    def smuInit(self):
        """intializaes smu with data for the 1st sweep step

        Return the same as for keithley_init [status, message]:
                status: 0 - no error, ~0 - error
                message
        """
        function_dict = self.dependency_manager.function_dict
        s = {}
        # THIS IS MISSING SOURCE VALUE ak start and end
        s["pulse"] = False
        s["source"] = self.settings["channel"]  # may take values depending on the channel names in smu, e.g. for Keithley 2612B [smua, smub]
        s["drain"] = self.settings["drainchannel"]
        s["type"] = "v" if self.settings["inject"] == "voltage" else "i"  # source inject current or voltage: may take values [i ,v]
        s["single_ch"] = self.settings["singlechannel"]  # single channel mode: may be True or False

        s["sourcenplc"] = self.settings["sourcenplc"]  # drain NPLC (may not be used in single channel mode)
        s["delay"] = True if self.settings["sourcedelaymode"] == "auto" else False  # stabilization time mode for source: may take values [True - Auto, False - manual]
        s["delayduration"] = self.settings["sourcedelay"]  # stabilization time duration if manual (may not be used in single channel mode)
        s["limit"] = self.settings["sourcelimit"]  # limit for current in voltage mode or for voltage in current mode (may not be used in single channel mode)
        s["sourcehighc"] = self.smu_settings["sourcehighc"]

        s["drainnplc"] = self.settings["drainnplc"]  # drain NPLC (may not be used in single channel mode)
        s["draindelay"] = True if self.settings["draindelaymode"] == "auto" else False  # stabilization time mode for source: may take values [True - Auto, False - manual]
        s["draindelayduration"] = self.settings["draindelay"]  # stabilization time duration if manual (may not be used in single channel mode)
        s["drainlimit"] = self.settings["drainlimit"]  # limit for current in voltage mode or for voltage in current mode (may not be used in single channel mode)
        s["drainhighc"] = self.smu_settings["drainhighc"]

        if self.settings["sourcesensemode"] == "4 wire":
            s["sourcesense"] = True  # source sence mode: may take values [True - 4 wire, False - 2 wire]
        else:
            s["sourcesense"] = False  # source sence mode: may take values [True - 4 wire, False - 2 wire]
        if self.settings["drainsensemode"] == "4 wire":
            s["drainsense"] = True  # source sence mode: may take values [True - 4 wire, False - 2 wire]
        else:
            s["drainsense"] = False  # source sence mode: may take values [True - 4 wire, False - 2 wire]
        if function_dict["smu"][self.settings["smu"]]["smu_init"](s):
            return [2, {"Error message": "timeIV plugin: error in SMU plugin can not initialize"}]

        return {0, "OK"}

    ########Functions
    ########create file header

    def create_file_header(self, settings, smu_settings):
        return self.filemanager.create_file_header(settings, smu_settings)

    ########Functions
    ########plugin actions
    def _stopAction(self):
        self.logger.log_debug("Stopping timeIV plugin action")
        self.run_thread.thread_stop()

    def _runAction(self):
        function_dict = self.dependency_manager.function_dict
        self.logger.log_debug("Running timeIV plugin action")
        self.set_running(True)
        [status, message] = self.parse_settings_widget()
        if status:
            self.logger.log_warn("timeIV plugin: parse_settings_widget returned error: " + str(message))
            self.logger.info_popup(f"{message['Error message']}")
            self.set_running(False)
            return [status, message]

        function_dict["smu"][self.settings["smu"]]["set_running"](True)
        [status, message] = function_dict["smu"][self.settings["smu"]]["smu_connect"]()
        if status:
            self.logger.log_warn("timeIV plugin: smu_connect returned error: " + str(message))
            self.logger.info_popup(f"{message['Error message']}")

            self.set_running(False)
            function_dict["smu"][self.settings["smu"]]["set_running"](False)
            return [status, message]

        ##IRtodo#### check that the new file will not overwrite existing data -> implement dialog
        self.logger.log_debug("TimeIV run_thread created")
        self.run_thread = thread_with_exception(self._sequenceImplementation)
        self.run_thread.start()
        return [0, "OK"]

    ########Functions
    ########sequence implementation
    def _saveData(self, fileheader, time, sourceI, sourceV, drainI=None, drainV=None):
        fulladdress = self.settings["address"] + os.sep + self.settings["filename"] + ".dat"
        self.logger.log_debug("Saving data to file: " + fulladdress)

        if drainI == None:
            data = list(zip(time, sourceI, sourceV))
            # np.savetxt(fulladdress, data, fmt='%.8f', delimiter=',', newline='\n', header=fileheader, comments='#')
        else:
            data = list(zip(time, sourceI, sourceV, drainI, drainV))

        with open(fulladdress, "w") as f:
            f.write(fileheader + "\n")
            pd.DataFrame(data).to_csv(f, index=False, header=False, float_format="%.12e", sep=",")

    def sequenceStep(self, postfix):
        function_dict = self.dependency_manager.function_dict
        self.logger.log_debug("Running sequence step with postfix: " + postfix)
        self.settings["filename"] = self.settings["filename"] + postfix
        [status, message] = function_dict["smu"][self.settings["smu"]]["smu_connect"]()
        if status:
            return [status, message]
        self._sequenceImplementation()
        function_dict["smu"][self.settings["smu"]]["smu_disconnect"]()
        return [0, "sweep finished"]

    def _timeIVimplementation(self):
        function_dict = self.dependency_manager.function_dict
        self.logger.log_debug("_timeIVimplementation: Creating file header.")
        header = self.create_file_header(self.settings, self.smu_settings)

        self.logger.log_debug("_timeIVimplementation: Initializing SMU.")
        [status, message] = self.smuInit()
        if status:
            raise timeIVexception(f"{message['Error message']}")

        self.logger.log_debug("_timeIVimplementation: Turning off SMU output.")
        function_dict["smu"][self.settings["smu"]]["smu_outputOFF"]()

        self.logger.log_debug("_timeIVimplementation: Setting SMU output for source channel.")
        function_dict["smu"][self.settings["smu"]]["smu_setOutput"](
            self.settings["channel"],
            "v" if self.settings["inject"] == "voltage" else "i",
            self.settings["sourcevalue"],
        )

        if not self.settings["singlechannel"]:
            self.logger.log_debug("_timeIVimplementation: Setting SMU output for drain channel.")
            function_dict["smu"][self.settings["smu"]]["smu_setOutput"](
                self.settings["drainchannel"],
                "v" if self.settings["draininject"] == "voltage" else "i",
                self.settings["drainvalue"],
            )

        timeData = []
        startTic = time.time()
        saveTic = startTic
        self.logger.log_debug("_timeIVimplementation: SMU initialized successfully.")

        if not self.settings["singlechannel"]:
            self.logger.log_debug("_timeIVimplementation: Turning on SMU output for source and drain channels.")
            function_dict["smu"][self.settings["smu"]]["smu_outputON"](self.settings["channel"], self.settings["drainchannel"])
        else:
            self.logger.log_debug("_timeIVimplementation: Turning on SMU output for source channel.")
            function_dict["smu"][self.settings["smu"]]["smu_outputON"](self.settings["channel"])

        while True:
            self.logger.log_debug("_timeIVimplementation: Fetching IV data for source channel.")
            status, sourceIV = function_dict["smu"][self.settings["smu"]]["smu_getIV"](self.settings["channel"])
            if status:
                raise timeIVexception(sourceIV["Error message"])

            if not self.settings["singlechannel"]:
                self.logger.log_debug("_timeIVimplementation: Fetching IV data for drain channel.")
                status, drainIV = function_dict["smu"][self.settings["smu"]]["smu_getIV"](self.settings["drainchannel"])
                if status:
                    raise timeIVexception(drainIV["Error message"])

            currentTime = time.time()
            toc = currentTime - startTic

            if not timeData:
                self.logger.log_debug("_timeIVimplementation: Initializing plots.")
                self.axes.cla()
                self.axes_twinx.cla()
                timeData.append(toc)
                sourceV = [sourceIV[dataOrder.V.value]]
                plot_refs = self.axes.plot(timeData, sourceV, "bo")
                self.axes.set_xlabel("time (s)")
                self.axes.set_ylabel("Voltage (V)")
                self._plot_sourceV = plot_refs[0]
                self.axes_twinx.set_ylabel("Current (A)")
                sourceI = [sourceIV[dataOrder.I.value]]
                plot_refs = self.axes_twinx.plot(timeData, sourceI, "b*")
                self._plot_sourceI = plot_refs[0]

                if not self.settings["singlechannel"]:
                    drainV = [drainIV[dataOrder.V.value]]
                    plot_refs = self.axes.plot(timeData, drainV, "go")
                    self._plot_drainV = plot_refs[0]
                    drainI = [drainIV[dataOrder.I.value]]
                    plot_refs = self.axes_twinx.plot(timeData, drainI, "g*")
                    self._plot_drainI = plot_refs[0]
                else:
                    drainI = None
                    drainV = None
            else:
                self.logger.log_debug("_timeIVimplementation: Updating plots.")
                timeData.append(toc)
                self.axes.cla()
                sourceV.append(sourceIV[dataOrder.V.value])
                sourceI.append(sourceIV[dataOrder.I.value])
                self.axes.plot(timeData, sourceV, "bo")
                self.axes_twinx.cla()
                self.axes_twinx.plot(timeData, sourceI, "b*")

                if not self.settings["singlechannel"]:
                    drainV.append(drainIV[dataOrder.V.value])
                    drainI.append(drainIV[dataOrder.I.value])
                    self.axes_twinx.plot(timeData, drainI, "g*")
                    self.axes.plot(timeData, drainV, "go")

            self.axes.relim()
            self.axes.autoscale_view()
            self.sc.draw()

            if self.settings["stoptimer"]:
                if (currentTime - startTic) >= self.settings["stopafter"] * 60:  # convert to sec from min
                    self.logger.log_debug("_timeIVimplementation: Stop timer reached, saving data and exiting.")
                    self._saveData(header, timeData, sourceI, sourceV, drainI, drainV)
                    break

            if self.settings["autosave"]:
                if (currentTime - saveTic) >= self.settings["autosaveinterval"] * 60:  # convert to sec from min
                    self.logger.log_debug("_timeIVimplementation: Autosave interval reached, saving data.")
                    self._saveData(header, timeData, sourceI, sourceV, drainI, drainV)
                    saveTic = currentTime

            time.sleep(self.settings["timestep"])

        self.logger.log_debug("_timeIVimplementation: Turning off SMU output and disconnecting.")
        function_dict["smu"][self.settings["smu"]]["smu_outputOFF"]()
        function_dict["smu"][self.settings["smu"]]["smu_disconnect"]()
        self.set_running(False)
        self.logger.log_debug("_timeIVimplementation: Completed successfully.")
        return [0, "OK"]

    def _sequenceImplementation(self):
        """
        Performs a timeIV on SMU, saves the result in a file

        Returns [status, message]:
               status: 0 - no error, ~0 - error
        """
        try:
            function_dict = self.dependency_manager.function_dict
            exception = 0  # handling turning off smu in case of exceptions. 0 = no exception, 1 - failure in smu, 2 - threadStopped, 3 - unexpected
            self._timeIVimplementation()
        except timeIVexception as e:
            self.logger.log_warn(f"timeIV plugin implementation stopped because of exception: {e}")
            exception = 1
        except ThreadStopped:
            self.logger.log_warn("timeIV plugin implementation aborted")
            exception = 2
        except Exception as e:
            self.logger.log_warn(f"timeIV plugin implementation stopped because of unexpected exception: {e}")
            exception = 3
        finally:
            try:
                function_dict["smu"][self.settings["smu"]]["smu_outputOFF"]()
                function_dict["smu"][self.settings["smu"]]["smu_disconnect"]()
                if exception == 3 or exception == 1:
                    self.logger.info_popup("Implementation stopped because of exception. Check log")
            except Exception as e:
                self.logger.log_warn(f"timeIV plugin: smu turn off failed because of unexpected exception: {e}")
                self.logger.info_popup("SMU turn off failed. Check log")
            self.set_running(False)


