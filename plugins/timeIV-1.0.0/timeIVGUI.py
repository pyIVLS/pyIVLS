"""
This is a timeIV plugin implementation for pyIVLS

The function of the plugin is to measure current and voltage change in time

This file should provide
- functions that will implement functionality of the hooks (see pyIVLS_timeIVGUI)
- GUI functionality - code that interracts with Qt GUI elements from widgets

"""

import os
import time
from datetime import datetime
from pathvalidate import is_valid_filename
from PyQt6 import uic
from PyQt6.QtWidgets import QVBoxLayout, QFileDialog
from PyQt6.QtCore import QObject, Qt
from MplCanvas import MplCanvas  # this should be moved to some pluginsShare
from threadStopped import thread_with_exception, ThreadStopped
from enum import Enum
import copy
import pandas as pd
from plugins.plugin_components import LoggingHelper, CloseLockSignalProvider, public, get_public_methods


class timeIVexception(Exception):
    pass


#
class dataOrder(Enum):
    V = 1
    I = 0  # noqa: E741


class timeIVGUI(QObject):
    """GUI implementation
    this class may be a child of QObject if Signals or Slot will be needed
    """

    non_public_methods = []  # add function names here, if they should not be exported as public to another plugins
    public_methods = [
        "parse_settings_widget",
        "set_running",
        "setSettings",
        "sequenceStep",
        "set_gui_from_settings",
    ]  # necessary for descendents of QObject, otherwise _get_public_methods returns a lot of QObject methods

    ########Signals
    ##remove this if plugin will only provide functions to another plugins, but will not interract with the user directly

    def _get_public_methods(self):
        return get_public_methods(self)

    def _getLogSignal(self):
        return self.logger.logger_signal

    def _getInfoSignal(self):
        return self.logger.info_popup_signal

    def _getCloseLockSignal(self):
        return self.closelock.closeLock

    ########Functions
    def __init__(self):
        super(timeIVGUI, self).__init__()
        self.verbose = True  # Enable verbose logging
        self.logger = LoggingHelper(self)
        self.closelock = CloseLockSignalProvider()
        # List of functions from another plugins required for functioning
        self.dependency = {
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
            ],
        }
        self.settings = {}

        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep

        self.settingsWidget = uic.loadUi(self.path + "timeIV_settingsWidget.ui")
        self.MDIWidget = uic.loadUi(self.path + "timeIV_MDIWidget.ui")

        # remove next if no plots
        self._create_plt()
        self.logger.log_info("timeIVGUI initialized.")

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
        self.settingsWidget.smuBox.currentIndexChanged.connect(self._smu_plugin_changed)

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

    ########Functions
    ########GUI Slots

    ########Functions
    ################################### internal

    def _parseSaveData(self):
        self.settings["address"] = self.settingsWidget.lineEdit_path.text()
        if not os.path.isdir(self.settings["address"] + os.sep):
            self.logger.log_warn("timeIV plugin: address string should point to a valid directory")
            return (1, {"Error message": " timeIV plugin: address string should point to a valid directory"})

        self.settings["filename"] = self.settingsWidget.lineEdit_filename.text()
        if not is_valid_filename(self.settings["filename"]):
            self.logger.log_warn("timeIV plugin: filename is not valid")
            self.logger.info_popup("timeIV plugin: filename is not valid")
            return (1, {"Error message": "timeIV plugin: filename is not valid"})

        self.settings["samplename"] = self.settingsWidget.lineEdit_sampleName.text()
        self.settings["comment"] = self.settingsWidget.lineEdit_comment.text()
        return (0, "Ok")

    @public
    def parse_settings_widget(self):
        """Parses the settings widget for the templatePlugin. Extracts current values. Checks if values are allowed. Provides settings of template plugin to an external plugin

        Returns [status, settings_dict]:
            status: 0 - no error, ~0 - error (add error code later on if needed)
            self.settings
        """
        if not self.function_dict:
            return (
                3,
                {
                    "Error message": "Missing functions in timeIV plugin. Check log",
                    "Missing functions": self.missing_functions,
                },
            )

        smu_selection = self.settingsWidget.smuBox.currentText()
        if smu_selection not in self.function_dict["smu"]:
            return (3, {"Error message": "SMU plugin not found in function_dict"})
        self.settings["smu"] = smu_selection

        [status, self.smu_settings] = self.function_dict["smu"][self.settings["smu"]]["parse_settings_widget"]()
        if status:
            return (2, self.smu_settings)

        status, message = self._parseSaveData()
        if status:
            return (status, message)

        try:
            self.settings["timestep"] = float(self.settingsWidget.step_lineEdit.text())
        except ValueError:
            return (1, {"Error message": "Value error in timeIV plugin: time step field should be numeric"})
        if self.settings["timestep"] <= 0:
            return (1, {"Error message": "Value error in timeIV plugin: time step field should be greater than 0"})
        try:
            self.settings["stopafter"] = float(self.settingsWidget.stopAfterLineEdit.text())
        except ValueError:
            return (1, {"Error message": "Value error in timeIV plugin: stop after field should be numeric"})
        if self.settings["stopafter"] <= 0:
            return (1, {"Error message": "Value error in timeIV plugin: autosave interval field should be numeric"})
        try:
            self.settings["autosaveinterval"] = float(self.settingsWidget.autosaveLineEdit.text())
        except ValueError:
            return (
                1,
                {"Error message": "Value error in timeIV plugin: autosave interval field should be greater than 0"},
            )
        if self.settings["autosaveinterval"] <= 0:
            return (
                1,
                {"Error message": "Value error in timeIV plugin: autosave interval field should be greater than 0"},
            )
        self.settings["stoptimer"] = self.settingsWidget.stopTimerCheckBox.isChecked()
        self.settings["autosave"] = self.settingsWidget.autosaveCheckBox.isChecked()

        # SMU settings
        # Determine source channel: may take values depending on the channel names in smu, eg. for Keithley 2612B [smua, smub]
        self.settings["channel"] = (self.settingsWidget.comboBox_channel.currentText()).lower()
        currentIndex = self.settingsWidget.comboBox_channel.currentIndex()
        if self.settingsWidget.comboBox_channel.count() > 1:
            if currentIndex == 0:
                self.settings["drainchannel"] = self.settingsWidget.comboBox_channel.itemText(1)
            else:
                self.settings["drainchannel"] = self.settingsWidget.comboBox_channel.itemText(0)
        else:
            self.settings["drainchannel"] = "xxx"  # for compatability if the smu does not support second channel

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
        # start should be float
        try:
            self.settings["sourcevalue"] = float(self.settingsWidget.lineEdit_sourceSetValue.text())
        except ValueError:
            return (
                1,
                {"Error message": "Value error in timeIV plugin: source set value field should be numeric"},
            )

        # limit should be float >0
        try:
            self.settings["sourcelimit"] = float(self.settingsWidget.lineEdit_sourceLimit.text())
        except ValueError:
            return (
                1,
                {"Error message": "Value error in timeIV plugin: source limit field should be numeric"},
            )
        if self.settings["sourcelimit"] <= 0:
            return (
                1,
                {"Error message": "Value error in timeIV plugin: source limit field should be positive"},
            )

        # source nplc (in fact it is integration time for the measurement) is calculated from line frequency, should be float >0
        try:
            self.settings["sourcenplc"] = (
                0.001 * self.smu_settings["lineFrequency"] * float(self.settingsWidget.lineEdit_sourceNPLC.text())
            )
        except ValueError:
            return (
                1,
                {"Error message": "Value error in timeIV plugin: source nplc field should be numeric"},
            )
        if self.settings["sourcenplc"] <= 0:
            return (
                1,
                {"Error message": "Value error in timeIV plugin: source nplc field should be positive"},
            )

        # delay (in fact it is stabilization time before the measurement), for Keithley control should be in s in GUI is ms, should be >0
        try:
            self.settings["sourcedelay"] = float(self.settingsWidget.lineEdit_sourceDelay.text()) / 1000
        except ValueError:
            return (
                1,
                {"Error message": "Value error in timeIV plugin: source delay field should be numeric"},
            )
        if self.settings["sourcedelay"] <= 0:
            return (
                1,
                {"Error message": "Value error in timeIV plugin: source delay field should be positive"},
            )

        # start should be float
        try:
            self.settings["drainvalue"] = float(self.settingsWidget.lineEdit_drainSetValue.text())
        except ValueError:
            return (
                1,
                {"Error message": "Value error in timeIV plugin: drain set value field should be numeric"},
            )

        # limit should be float >0
        try:
            self.settings["drainlimit"] = float(self.settingsWidget.lineEdit_drainLimit.text())
        except ValueError:
            return (
                1,
                {"Error message": "Value error in timeIV plugin: drain limit field should be numeric"},
            )
        if self.settings["drainlimit"] <= 0:
            return (
                1,
                {"Error message": "Value error in timeIV plugin: drain limit field should be positive"},
            )

        # drain nplc (in fact it is integration time for the measurement) is calculated from line frequency, should be float >0
        try:
            self.settings["drainnplc"] = (
                0.001 * self.smu_settings["lineFrequency"] * float(self.settingsWidget.lineEdit_drainNPLC.text())
            )
        except ValueError:
            return (
                1,
                {"Error message": "Value error in timeIV plugin: drain nplc field should be numeric"},
            )
        if self.settings["drainnplc"] <= 0:
            return (
                1,
                {"Error message": "Value error in timeIV plugin: drain nplc field should be positive"},
            )

        # delay (in fact it is stabilization time before the measurement), for Keithley control should be in s in GUI is ms, should be >0
        try:
            self.settings["draindelay"] = float(self.settingsWidget.lineEdit_drainDelay.text()) / 1000
        except ValueError:
            return (
                1,
                {"Error message": "Value error in timeIV plugin: drain delay field should be numeric"},
            )
        if self.settings["draindelay"] <= 0:
            return (
                1,
                {"Error message": "Value error in timeIV plugin: drain delay field should be positive"},
            )
        retset = self.settings
        retset["smu_settings"] = self.smu_settings
        return (0, retset)

    ########Functions
    ###############GUI setting up
    def _initGUI(
        self,
        plugin_info,
    ):
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK
        self.logger.log_debug("Initializing GUI with plugin_info: " + str(plugin_info))
        self.settingsWidget.lineEdit_path.setText(plugin_info["address"])
        self.settingsWidget.lineEdit_filename.setText(plugin_info["filename"])
        self.settingsWidget.lineEdit_sampleName.setText(plugin_info["samplename"])
        self.settingsWidget.lineEdit_comment.setText(plugin_info["comment"])

        self.settingsWidget.step_lineEdit.setText(plugin_info["timestep"])
        self.settingsWidget.stopAfterLineEdit.setText(plugin_info["stopafter"])
        self.settingsWidget.autosaveLineEdit.setText(plugin_info["autosaveinterval"])

        if plugin_info["stoptimer"] == "True":
            self.settingsWidget.stopTimerCheckBox.setChecked(True)
        else:
            self.settingsWidget.stopTimerCheckBox.setChecked(False)

        if plugin_info["autosave"] == "True":
            self.settingsWidget.autosaveCheckBox.setChecked(True)
        else:
            self.settingsWidget.autosaveCheckBox.setChecked(False)
        # SMU settings
        if plugin_info["singlechannel"] == "True":
            self.settingsWidget.checkBox_singleChannel.setChecked(True)

        # fill channels
        default_smu = plugin_info["smu"]
        try:
            self.settingsWidget.comboBox_channel.clear()
            self.settingsWidget.comboBox_channel.addItems(self.function_dict["smu"][default_smu]["smu_channelNames"]())
            self.settingsWidget.comboBox_channel.setCurrentText(plugin_info["channel"])
        except KeyError:
            self.logger.log_warn(f"SMU {default_smu} not found in function_dict")
        # update the SMU selection combobox
        self.settingsWidget.smuBox.clear()
        self.settingsWidget.smuBox.addItems(list(self.function_dict["smu"].keys()))
        self.settingsWidget.smuBox.setCurrentText(default_smu)

        currentIndex = self.settingsWidget.comboBox_channel.findText(
            plugin_info["channel"], Qt.MatchFlag.MatchFixedString
        )
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
        self._smu_plugin_changed()

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

    def _smu_plugin_changed(self):
        """Handles the visibility of the SMU settings based on the selected SMU plugin.
        Not connected to the _update_gui_state calls, since it is already called when the SMU plugin is changed.
        """
        smu_selection = self.settingsWidget.smuBox.currentText()
        if smu_selection in self.function_dict["smu"]:
            available_channels = self.function_dict["smu"][smu_selection]["smu_channelNames"]()
            # get channel names from the selected SMU plugin
            self.settingsWidget.comboBox_channel.clear()
            self.settingsWidget.comboBox_channel.addItems(available_channels)

    @public
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
        self.missing_functions = []
        for dependency_plugin in list(self.dependency.keys()):
            if dependency_plugin not in function_dict:
                self.logger.log_error(f"Functions for dependency plugin '{dependency_plugin}' not found")
                self.missing_functions.append(dependency_plugin)
                continue
            for dependency_function in self.dependency[dependency_plugin]:
                if dependency_function not in function_dict[dependency_plugin]:
                    self.logger.log_error(
                        f"Function '{dependency_function}' for dependency plugin '{dependency_plugin}' not found"
                    )
                    self.missing_functions.append(f"{dependency_plugin}:{dependency_function}")
        if not self.missing_functions:
            self.settingsWidget.runButton.setEnabled(True)
            self.function_dict = function_dict
        else:
            self.settingsWidget.runButton.setDisabled(True)
            self.function_dict = {}
        return self.missing_functions

    @public
    def setSettings(self, settings):
        """Sets the settings for the plugin. Workflow from seqBuilder:
        1. Parse_settings_widget is called when step added to sequence
        2. When running, set_settings is called to set the settings for the plugin

        Args:
            settings (dict): outputs from parse_settings_widget function
        """
        self.logger.log_debug("Setting settings for timeIV plugin: " + str(settings))
        self.settings = []
        self.settings = copy.deepcopy(settings)
        self.smu_settings = settings["smu_settings"]

    @public
    def set_gui_from_settings(self):
        """
        Updates the GUI fields based on the internal settings dictionary.
        This function assumes that the settings have already been set using the `setSettings` function.
        """
        self.settingsWidget.lineEdit_path.setText(self.settings["address"])
        self.settingsWidget.lineEdit_filename.setText(self.settings["filename"])
        self.settingsWidget.lineEdit_sampleName.setText(self.settings["samplename"])
        self.settingsWidget.lineEdit_comment.setText(self.settings["comment"])

        self.settingsWidget.step_lineEdit.setText(str(self.settings["timestep"]))
        self.settingsWidget.stopAfterLineEdit.setText(str(self.settings["stopafter"]))
        self.settingsWidget.autosaveLineEdit.setText(str(self.settings["autosaveinterval"]))

        self.settingsWidget.stopTimerCheckBox.setChecked(self.settings["stoptimer"])
        self.settingsWidget.autosaveCheckBox.setChecked(self.settings["autosave"])

        # SMU settings
        self.settingsWidget.checkBox_singleChannel.setChecked(self.settings["singlechannel"])

        self.settingsWidget.comboBox_channel.setCurrentText(self.settings["channel"])
        self.settingsWidget.comboBox_inject.setCurrentText(self.settings["inject"])
        self.settingsWidget.comboBox_sourceSenseMode.setCurrentText(self.settings["sourcesensemode"])
        self.settingsWidget.comboBox_sourceDelayMode.setCurrentText(self.settings["sourcedelaymode"])
        self.settingsWidget.comboBox_drainInject.setCurrentText(self.settings["draininject"])
        self.settingsWidget.comboBox_drainSenseMode.setCurrentText(self.settings["drainsensemode"])
        self.settingsWidget.comboBox_drainDelayMode.setCurrentText(self.settings["draindelaymode"])

        self.settingsWidget.lineEdit_sourceSetValue.setText(str(self.settings["sourcevalue"]))
        self.settingsWidget.lineEdit_sourceLimit.setText(str(self.settings["sourcelimit"]))
        self.settingsWidget.lineEdit_sourceNPLC.setText(
            str(self.settings["sourcenplc"] / (0.001 * self.smu_settings["lineFrequency"]))
        )
        self.settingsWidget.lineEdit_sourceDelay.setText(str(self.settings["sourcedelay"] * 1000))
        self.settingsWidget.lineEdit_drainSetValue.setText(str(self.settings["drainvalue"]))
        self.settingsWidget.lineEdit_drainLimit.setText(str(self.settings["drainlimit"]))
        self.settingsWidget.lineEdit_drainNPLC.setText(
            str(self.settings["drainnplc"] / (0.001 * self.smu_settings["lineFrequency"]))
        )
        self.settingsWidget.lineEdit_drainDelay.setText(str(self.settings["draindelay"] * 1000))

        # Update the SMU selection combobox
        self.settingsWidget.smuBox.setCurrentText(self.settings["smu"])

        # Update the GUI state to reflect the current settings
        self._update_GUI_state()

    ########Functions
    ############### run preparations
    def smuInit(self):
        """intializaes smu with data for the 1st sweep step

        Return the same as for keithley_init [status, message]:
                status: 0 - no error, ~0 - error
                message
        """
        s = {}
        # THIS IS MISSING SOURCE VALUE ak start and end
        s["pulse"] = False
        s["source"] = self.settings[
            "channel"
        ]  # may take values depending on the channel names in smu, e.g. for Keithley 2612B [smua, smub]
        s["drain"] = self.settings["drainchannel"]
        s["type"] = (
            "v" if self.settings["inject"] == "voltage" else "i"
        )  # source inject current or voltage: may take values [i ,v]
        s["single_ch"] = self.settings["singlechannel"]  # single channel mode: may be True or False
        s["start"] = self.settings[
            "sourcevalue"
        ]  # start value for source in voltage mode or for drain in current mode (may not be used in single channel mode)
        s["end"] = self.settings["sourcevalue"]  # end value for source in
        s["sourcenplc"] = self.settings["sourcenplc"]  # drain NPLC (may not be used in single channel mode)
        s["delay"] = (
            True if self.settings["sourcedelaymode"] == "auto" else False
        )  # stabilization time mode for source: may take values [True - Auto, False - manual]
        s["delayduration"] = self.settings[
            "sourcedelay"
        ]  # stabilization time duration if manual (may not be used in single channel mode)
        s["limit"] = self.settings[
            "sourcelimit"
        ]  # limit for current in voltage mode or for voltage in current mode (may not be used in single channel mode)
        s["sourcehighc"] = self.smu_settings["sourcehighc"]

        s["drainnplc"] = self.settings["drainnplc"]  # drain NPLC (may not be used in single channel mode)
        s["draindelay"] = (
            True if self.settings["draindelaymode"] == "auto" else False
        )  # stabilization time mode for source: may take values [True - Auto, False - manual]
        s["draindelayduration"] = self.settings[
            "draindelay"
        ]  # stabilization time duration if manual (may not be used in single channel mode)
        s["drainlimit"] = self.settings[
            "drainlimit"
        ]  # limit for current in voltage mode or for voltage in current mode (may not be used in single channel mode)
        s["drainhighc"] = self.smu_settings["drainhighc"]

        if self.settings["sourcesensemode"] == "4 wire":
            s["sourcesense"] = True  # source sence mode: may take values [True - 4 wire, False - 2 wire]
        else:
            s["sourcesense"] = False  # source sence mode: may take values [True - 4 wire, False - 2 wire]
        if self.settings["drainsensemode"] == "4 wire":
            s["drainsense"] = True  # source sence mode: may take values [True - 4 wire, False - 2 wire]
        else:
            s["drainsense"] = False  # source sence mode: may take values [True - 4 wire, False - 2 wire]
        if self.function_dict["smu"][self.settings["smu"]]["smu_init"](s):
            return (2, {"Error message": "timeIV plugin: error in SMU plugin can not initialize"})

        return (0, "OK")

    ########Functions
    ########create file header

    def create_file_header(self, settings, smu_settings):
        """
        creates a header for the csv file in the old measuremnt system style

        input	smu_settings dictionary for Keithley2612GUI.py class (see Keithley2612BGUI.py)
            settings dictionary for the sweep plugin

        str containing the header

        """

        ## header may not be optimal, this is because it should repeat the structure of the headers produced by the old measurement station
        comment = "#####################"
        if settings["samplename"] == "":
            comment = f"{comment}\n#\n# measurement of {{noname}}\n#\n#"
        else:
            comment = f"{comment}\n#\n# measurement of {settings['samplename']}\n#\n#"
        comment = f"{comment}date {datetime.now().strftime('%d-%b-%Y, %H:%M:%S')}\n#"
        comment = f"{comment}Keithley source {settings['channel']}\n#"
        comment = f"{comment}Source in {settings['inject']} injection mode\n#"
        if settings["inject"] == "voltage":
            stepunit = "V"
            limitunit = "A"
        else:
            stepunit = "A"
            limitunit = "V"
        comment = f"{comment}\n#\n#"
        comment = f"{comment}Set value for time check {settings['sourcevalue']} {stepunit}\n#"
        comment = f"{comment}\n#"
        comment = f"{comment}Limit for step {settings['sourcelimit']} {limitunit}\n#"
        if settings["sourcedelaymode"] == "auto":
            comment = f"{comment}Measurement acquisition period is done in AUTO mode\n#"
        else:
            comment = f"{comment}Measurement stabilization period is{settings['sourcedelay'] / 1000} ms\n#"
        comment = f"{comment}NPLC value {settings['sourcenplc'] * 1000 / smu_settings['lineFrequency']} ms (for detected line frequency {smu_settings['lineFrequency']} Hz is {settings['sourcenplc']})\n#"
        comment = f"{comment}\n#\n#"
        comment = f"{comment}Continuous operation of the source with step time settings['timestep'] \n#\n#\n#"

        if not settings["singlechannel"]:
            comment = f"{comment}Drain in {settings['draininject']} injection mode\n#"
            if settings["inject"] == "voltage":
                stepunit = "V"
                limitunit = "A"
            else:
                stepunit = "A"
                limitunit = "V"
            comment = f"{comment}Set value for drain {settings['drainvalue']} {stepunit}\n#"
            comment = f"{comment}Limit for drain {settings['drainlimit']} {limitunit}\n#"
            if settings["draindelaymode"] == "auto":
                comment = f"{comment}Measurement acquisition period for drain is done in AUTO mode\n#"
            else:
                comment = f"{comment}Measurement stabilization period for drain is{settings['draindelay'] / 1000} ms\n#"
            comment = f"{comment}NPLC value {settings['drainnplc'] * 1000 / smu_settings['lineFrequency']} ms (for detected line frequency {smu_settings['lineFrequency']} Hz is {settings['drainnplc']})\n#"
        else:
            comment = f"{comment}\n#\n#\n#\n#\n#"

        comment = f"{comment}\n#"
        comment = f"{comment}Comment: {settings['comment']}\n#"
        comment = f"{comment}\n#"

        comment = f"{comment}\n#\n#\n#"

        if smu_settings["sourcehighc"]:
            comment = f"{comment}Source in high capacitance mode"
        else:
            comment = f"{comment}Source not in HighC mode (normal operation)"
        if not settings["singlechannel"]:
            if smu_settings["drainhighc"]:
                comment = f"{comment}. Drain in high capacitance mode\n#"
            else:
                comment = f"{comment}. Drain not in HighC mode (normal operation)\n#"
        else:
            comment = f"{comment}\n#"

        comment = f"{comment}\n#\n#\n#\n#\n#\n#\n#\n#\n#"

        if settings["stoptimer"]:
            comment = f"{comment}Timer set for {settings['stopafter']} minutes\n#"
        else:
            comment = f"{comment}\n#"

        if settings["sourcesensemode"] == "2 wire":
            comment = f"{comment}Sourse in 2 point measurement mode\n#"
        elif settings["sourcesensemode"] == "4 wire":
            comment = f"{comment}Sourse in 4 point measurement mode\n#"
        if not (settings["singlechannel"]):
            if settings["drainsensemode"] == "2 wire":
                comment = f"{comment}Drain in 2 point measurement mode\n"
            elif settings["drainsensemode"] == "4 wire":
                comment = f"{comment}Drain in 4 point measurement mode\n"
        else:
            comment = f"{comment}\n"

        if settings["singlechannel"]:
            comment = f"{comment}stime, IS, VS"
        else:
            comment = f"{comment}stime, IS, VS, ID, VD"

        return comment

    ########Functions
    ########plugin actions
    def _stopAction(self):
        self.logger.log_debug("Stopping timeIV plugin action")
        self.run_thread.thread_stop()

    def _runAction(self):
        self.logger.log_debug("Running timeIV plugin action")
        self.set_running(True)
        [status, message] = self.parse_settings_widget()
        if status:
            self.logger.log_error(f"Settings parsing failed: status={status}, {message}")
            self.logger.log_info(f"{message['Error message']}")
            self.set_running(False)
            return (status, message)

        self.function_dict["smu"][self.settings["smu"]]["set_running"](True)
        [status, message] = self.function_dict["smu"][self.settings["smu"]]["smu_connect"]()
        if status:
            self.logger.log_error(f"SMU connection failed: status={status}, {message}")
            self.logger.log_info(message["Error message"])
            self.set_running(False)
            self.function_dict["smu"][self.settings["smu"]]["set_running"](False)
            return (status, message)

        ##IRtodo#### check that the new file will not overwrite existing data -> implement dialog
        self.logger.log_debug("TimeIV run_thread created")
        self.run_thread = thread_with_exception(self._sequenceImplementation)
        self.run_thread.start()
        return (0, "OK")

    ########Functions
    ########sequence implementation
    def _saveData(self, fileheader, time, sourceI, sourceV, drainI=None, drainV=None):
        fulladdress = self.settings["address"] + os.sep + self.settings["filename"] + ".dat"
        self.logger.log_debug("Saving data to file: " + fulladdress)

        if drainI is None:
            data = list(zip(time, sourceI, sourceV))
            # np.savetxt(fulladdress, data, fmt='%.8f', delimiter=',', newline='\n', header=fileheader, comments='#')
        else:
            data = list(zip(time, sourceI, sourceV, drainI, drainV))

        with open(fulladdress, "w") as f:
            f.write(fileheader + "\n")
            pd.DataFrame(data).to_csv(f, index=False, header=False, float_format="%.12e", sep=",")

    @public
    def sequenceStep(self, postfix):
        self.logger.log_debug("Running sequence step with postfix: " + postfix)
        self.settings["filename"] = self.settings["filename"] + postfix
        [status, message] = self.function_dict["smu"][self.settings["smu"]]["smu_connect"]()
        if status:
            return (status, message)
        self._sequenceImplementation()
        self.function_dict["smu"][self.settings["smu"]]["smu_disconnect"]()
        return (0, "sweep finished")

    def _timeIVimplementation(self):
        self.logger.log_debug("_timeIVimplementation: Creating file header.")
        header = self.create_file_header(self.settings, self.smu_settings)

        self.logger.log_debug("_timeIVimplementation: Initializing SMU.")
        [status, message] = self.smuInit()
        if status:
            raise timeIVexception(f"{message['Error message']}")

        self.logger.log_debug("_timeIVimplementation: Turning off SMU output.")
        self.function_dict["smu"][self.settings["smu"]]["smu_outputOFF"]()

        self.logger.log_debug("_timeIVimplementation: Setting SMU output for source channel.")
        self.function_dict["smu"][self.settings["smu"]]["smu_setOutput"](
            self.settings["channel"],
            "v" if self.settings["inject"] == "voltage" else "i",
            self.settings["sourcevalue"],
        )

        if not self.settings["singlechannel"]:
            self.logger.log_debug("_timeIVimplementation: Setting SMU output for drain channel.")
            self.function_dict["smu"][self.settings["smu"]]["smu_setOutput"](
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
            self.function_dict["smu"][self.settings["smu"]]["smu_outputON"](
                self.settings["channel"], self.settings["drainchannel"]
            )
        else:
            self.logger.log_debug("_timeIVimplementation: Turning on SMU output for source channel.")
            self.function_dict["smu"][self.settings["smu"]]["smu_outputON"](self.settings["channel"])

        while True:
            self.logger.log_debug("_timeIVimplementation: Fetching IV data for source channel.")
            status, sourceIV = self.function_dict["smu"][self.settings["smu"]]["smu_getIV"](self.settings["channel"])
            if status:
                raise timeIVexception(sourceIV["Error message"])

            if not self.settings["singlechannel"]:
                self.logger.log_debug("_timeIVimplementation: Fetching IV data for drain channel.")
                status, drainIV = self.function_dict["smu"][self.settings["smu"]]["smu_getIV"](
                    self.settings["drainchannel"]
                )
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
        self.function_dict["smu"][self.settings["smu"]]["smu_outputOFF"]()
        self.function_dict["smu"][self.settings["smu"]]["smu_disconnect"]()
        self.set_running(False)
        self.logger.log_debug("_timeIVimplementation: Completed successfully.")
        return (0, "OK")

    def _sequenceImplementation(self):
        """
        Performs a timeIV on SMU, saves the result in a file

        Returns [status, message]:
               status: 0 - no error, ~0 - error
        """
        try:
            exception = 0  # handling turning off smu in case of exceptions. 0 = no exception, 1 - failure in smu, 2 - threadStopped, 3 - unexpected
            self._timeIVimplementation()
        except timeIVexception as e:
            self.logger.log_error(f"TimeIV implementation error: {e}")
            exception = 1
        except ThreadStopped:
            self.logger.log_info("TimeIV plugin implementation aborted")
            exception = 2
        except Exception as e:
            self.logger.log_error(f"TimeIV plugin implementation stopped because of unexpected exception: {e}")
            exception = 3
        finally:
            try:
                self.function_dict["smu"][self.settings["smu"]]["smu_outputOFF"]()
                self.function_dict["smu"][self.settings["smu"]]["smu_disconnect"]()
                if exception == 3 or exception == 1:
                    self.logger.log_info("Implementation stopped because of exception. Check log")
            except Exception as e:
                self.logger.log_error(f"SMU turn off failed because of unexpected exception: {e}")
                self.logger.log_info("SMU turn off failed. Check log")
            self.set_running(False)

    @public
    def get_current_gui_settings(self):
        """Return the current settings from the GUI widgets as a dict, without validation or conversion."""
        settings = {}
        settings["timestep"] = self.settingsWidget.step_lineEdit.text()
        settings["stopafter"] = self.settingsWidget.stopAfterLineEdit.text()
        settings["autosaveinterval"] = self.settingsWidget.autosaveLineEdit.text()
        settings["stoptimer"] = self.settingsWidget.stopTimerCheckBox.isChecked()
        settings["autosave"] = self.settingsWidget.autosaveCheckBox.isChecked()
        settings["channel"] = self.settingsWidget.comboBox_channel.currentText().lower()
        currentIndex = self.settingsWidget.comboBox_channel.currentIndex()
        if self.settingsWidget.comboBox_channel.count() > 1:
            if currentIndex == 0:
                settings["drainchannel"] = self.settingsWidget.comboBox_channel.itemText(1)
            else:
                settings["drainchannel"] = self.settingsWidget.comboBox_channel.itemText(0)
        else:
            settings["drainchannel"] = "xxx"
        settings["inject"] = self.settingsWidget.comboBox_inject.currentText().lower()
        settings["sourcedelaymode"] = self.settingsWidget.comboBox_sourceDelayMode.currentText().lower()
        settings["sourcesensemode"] = self.settingsWidget.comboBox_sourceSenseMode.currentText().lower()
        settings["draindelaymode"] = self.settingsWidget.comboBox_drainDelayMode.currentText().lower()
        settings["draininject"] = self.settingsWidget.comboBox_drainInject.currentText().lower()
        settings["drainsensemode"] = self.settingsWidget.comboBox_drainSenseMode.currentText().lower()
        settings["singlechannel"] = self.settingsWidget.checkBox_singleChannel.isChecked()
        settings["sourcevalue"] = self.settingsWidget.lineEdit_sourceSetValue.text()
        settings["sourcelimit"] = self.settingsWidget.lineEdit_sourceLimit.text()
        settings["sourcenplc"] = self.settingsWidget.lineEdit_sourceNPLC.text()
        settings["sourcedelay"] = self.settingsWidget.lineEdit_sourceDelay.text()
        settings["drainvalue"] = self.settingsWidget.lineEdit_drainSetValue.text()
        settings["drainlimit"] = self.settingsWidget.lineEdit_drainLimit.text()
        settings["drainnplc"] = self.settingsWidget.lineEdit_drainNPLC.text()
        settings["draindelay"] = self.settingsWidget.lineEdit_drainDelay.text()
        settings["smu"] = self.settingsWidget.smuBox.currentText()
        # Add any additional fields as needed
        settings["address"] = self.settingsWidget.lineEdit_path.text()
        settings["filename"] = self.settingsWidget.lineEdit_filename.text()
        settings["comment"] = self.settingsWidget.lineEdit_comment.text()
        settings["samplename"] = self.settingsWidget.lineEdit_sampleName.text()

        return 0, settings
