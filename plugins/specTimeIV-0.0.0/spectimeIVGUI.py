"""
This is a timeIV plugin implementation for pyIVLS

The function of the plugin is to measure current and voltage change in time

This file should provide
- functions that will implement functionality of the hooks (see pyIVLS_timeIVGUI)
- GUI functionality - code that interracts with Qt GUI elements from widgets

"""

import copy
import os
import time
from typing import Annotated, Any, Literal

import pandas as pd
from annotated_types import Gt
from MplCanvas import MplCanvas  # this should be moved to some pluginsShare
from pathvalidate import is_valid_filename
from plugin_components import DataOrder, DependencyManager, FileManager, LoggingHelper, PluginException, load_widget
from pydantic import BaseModel, DirectoryPath, field_validator
from PyQt6.QtWidgets import QFileDialog, QVBoxLayout
from threadStopped import ThreadStopped, thread_with_exception


def s_to_ms(s: float) -> float:
    """Convert seconds to milliseconds."""
    return s * 1000


def ms_to_s(ms: float) -> float:
    """Convert milliseconds to seconds."""
    return ms / 1000


class SpecTimeIVSettings(BaseModel):
    timestep: float
    stoptimer: bool
    stopafter: float
    address: DirectoryPath
    filename: str
    comment: str
    samplename: str
    autosave: bool
    autosaveinterval: float
    singlechannel: bool
    channel: str
    inject: Literal["current", "voltage"]
    sourcesensemode: Literal["2 wire", "4 wire", "2 & 4 wire"]
    sourcedelaymode: Literal["auto", "manual"]
    sourcevalue: float
    sourcelimit: Annotated[float, Gt(0)]
    sourcenplc: Annotated[float, Gt(0)]
    sourcedelay: Annotated[float, Gt(0)]
    draininject: Literal["current", "voltage"]
    drainsensemode: Literal["2 wire", "4 wire", "2 & 4 wire"]
    draindelaymode: Literal["auto", "manual"]
    drainvalue: float
    drainlimit: Annotated[float, Gt(0)]
    drainnplc: Annotated[float, Gt(0)]
    draindelay: Annotated[float, Gt(0)]
    smu: str
    spectrometer: str

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, value: str) -> str:
        if not is_valid_filename(value):
            raise ValueError("Filename is not valid.")
        return value


class specTimeIVGUI:
    @property
    def settingsWidget(self) -> Any:
        # typecast to Any to avoid unkown attribute nuisance errors when accessing the widget.
        if not hasattr(self, "_settingsWidget"):
            raise NotImplementedError("Settings widget not implemented, remove this function if settings widget is not needed.")
        if self._settingsWidget is None:
            raise RuntimeError("Settings widget not initialized.")
        return self._settingsWidget

    @property
    def MDIWidget(self) -> Any:
        # typecast to Any to avoid unkown attribute nuisance errors when accessing the widget.
        if not hasattr(self, "_mdiWidget"):
            raise NotImplementedError("MDI widget not implemented, remove this function if MDI widget is not needed.")
        if self._mdiWidget is None:
            raise RuntimeError("MDI widget not initialized.")
        return self._mdiWidget

    # public and nonpublic methods
    non_public_methods = []  # add function names here, if they should not be exported as public to another plugins

    public_methods = [
        "parse_settings_widget",
        "sequenceStep",
        "setSettings",
        "set_gui_from_settings",
    ]  # add function names here, necessary for descendents of QObject, otherwise _get_public_methods returns a lot of QObject methods
    ########Signals

    ########Functions
    def __init__(self):
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
                # "A very necessary function",
            ],
            "spectrometer": [
                "setSettings",
                "spectrometerConnect",
                "spectrometerDisconnect",
                "spectrometerSetIntegrationTime",
                "spectrometerGetIntegrationTime",
                "spectrometerStartScan",
                "spectrometerGetSpectrum",
                "spectrometerGetScan",
                "createFile",
                # "Very very important function",
            ],
        }
        self.settings = {}

        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep

        self._settingsWidget, self._mdiWidget = load_widget(settings=True, mdi=True, path=self.path)

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
        )
        self._connect_signals()

    def _connect_signals(self):
        self.logger.log_debug("Connecting GUI signals to slots")
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
        self.logger.log_debug("Updating SMU channels in the GUI")
        smu_plugin = self.settingsWidget.smuBox.currentText()
        if smu_plugin:
            # fetch channels from the selected SMU plugin and update the channel combobox
            channels = self.dependency_manager.function_dict["smu"][smu_plugin]["smu_channelNames"]()
            self.logger.log_debug(f"SMU channels fetched for {smu_plugin}: {channels}")
            self.settingsWidget.comboBox_channel.clear()
            self.settingsWidget.comboBox_channel.addItems(channels)
            # if the channel in the settings is not in the list, reset it to the first available channel
            current_channel = self.settings.get("channel", "")
            if current_channel not in channels:
                self.settingsWidget.comboBox_channel.setCurrentIndex(0)
            else:
                self.settingsWidget.comboBox_channel.setCurrentText(current_channel)
        else:
            self.logger.log_debug("No SMU plugin selected, cannot update channels")

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

    def set_gui_from_settings(self):
        """
        Updates the GUI fields based on the internal settings dictionary.
        This function assumes that the settings have already been set using the `setSettings` function.
        """
        self.settingsWidget.lineEdit_path.setText(str(self.settings["address"]))
        self.settingsWidget.lineEdit_filename.setText(str(self.settings["filename"]))
        self.settingsWidget.lineEdit_sampleName.setText(str(self.settings["samplename"]))
        self.settingsWidget.lineEdit_comment.setText(str(self.settings["comment"]))

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
        self.settingsWidget.lineEdit_sourceNPLC.setText(str(s_to_ms(self.settings["sourcenplc"])))  # settings stores as s, but GUI shows in ms, so convert to ms for showing
        self.settingsWidget.lineEdit_sourceDelay.setText(str(s_to_ms(self.settings["sourcedelay"])))  # settings stores as s, but GUI shows in ms, so convert to ms for showing
        self.settingsWidget.lineEdit_drainSetValue.setText(str(self.settings["drainvalue"]))
        self.settingsWidget.lineEdit_drainLimit.setText(str(self.settings["drainlimit"]))
        self.settingsWidget.lineEdit_drainNPLC.setText(str(s_to_ms(self.settings["drainnplc"])))  # settings stores as s, but GUI shows in ms, so convert to ms for showing
        self.settingsWidget.lineEdit_drainDelay.setText(str(s_to_ms(self.settings["draindelay"])))  # settings stores as s, but GUI shows in ms, so convert to ms for showing

        # Update the SMU selection combobox
        self.settingsWidget.smuBox.setCurrentText(self.settings["smu"])
        self.settingsWidget.spectroBox.setCurrentText(self.settings["spectrometer"])

        # Update the GUI state to reflect the current settings
        self._update_GUI_state()

    def _parseSaveData(self):
        """Returns the parsed save data dictionary, does not write to it.

        Returns:
            _type_: _description_
        """
        save_settings = {}
        save_settings["address"] = self.settingsWidget.lineEdit_path.text()
        if not os.path.isdir(save_settings["address"] + os.sep):
            self.logger.log_warn("timeIV plugin: address string should point to a valid directory")
            return (1, {"Error message": " timeIV plugin: address string should point to a valid directory"})

        save_settings["filename"] = self.settingsWidget.lineEdit_filename.text()
        if not is_valid_filename(save_settings["filename"]):
            self.logger.log_warn("timeIV plugin: filename is not valid")
            self.logger.info_popup("timeIV plugin: filename is not valid")
            return (1, {"Error message": "timeIV plugin: filename is not valid"})

        save_settings["samplename"] = self.settingsWidget.lineEdit_sampleName.text()
        save_settings["comment"] = self.settingsWidget.lineEdit_comment.text()
        return (0, save_settings)

    def parse_settings_widget(self):
        """Parses the settings widget for the templatePlugin. Extracts current values. Checks if values are allowed. Provides settings of template plugin to an external plugin

        Returns [status, settings_dict]:
            status: 0 - no error, ~0 - error (add error code later on if needed)
            self.settings
        """
        # eat settings from GUI
        new_settings = self.read_gui()
        # validate
        valid = SpecTimeIVSettings.model_validate(new_settings)

        # serialize
        valid_settings = valid.model_dump()

        # parse deps
        status, state = self.dependency_manager.parse_dependencies(valid_settings)
        if status != 0:
            return status, state

        # add field for drain channel
        available_channels = self.dependency_manager.function_dict["smu"][valid_settings["smu"]]["smu_channelNames"]()  # fetch channels from the selected SMU plugin
        # the drain channel is the other available channel of the SMU
        # remove the selected source channel from the list of available channels
        available_channels.remove(valid_settings["channel"])
        if len(available_channels) > 0:
            valid_settings["drainchannel"] = available_channels[0]
        else:
            valid_settings["drainchannel"] = "xxx"  # if single channel SMU

        # write to internal
        self.settings = valid_settings

        # Return a copy so callers cannot mutate plugin state by reference.
        return [0, copy.deepcopy(self.settings)]

    ########Functions
    ###############GUI setting up
    def _initGUI(
        self,
        plugin_info,
    ):
        # test validation of settings briefly:
        m = SpecTimeIVSettings.model_validate(plugin_info)
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

        # dump to dict so that old logic works.
        valid_settings = valid.model_dump()

        # fill comboboxes with available deps.
        self.settingsWidget.smuBox.clear()
        self.settingsWidget.smuBox.addItems(list(self.dependency_manager.function_dict["smu"].keys()))
        self.settingsWidget.smuBox.setCurrentText(plugin_info["smu"])

        self.settingsWidget.spectroBox.clear()
        self.settingsWidget.spectroBox.addItems(list(self.dependency_manager.function_dict["spectrometer"].keys()))
        self.settingsWidget.spectroBox.setCurrentText(plugin_info["spectrometer"])

        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK
        self.logger.log_debug("Initializing GUI with plugin_info: " + str(valid_settings))
        # Write the unvalidated settings to the internal state. Spooky.
        self.setSettings(valid_settings)
        # COMMAND the gui to update itself
        self.set_gui_from_settings()

        # update to the correct GUI state
        self.set_running(False)
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
        if self.settingsWidget.comboBox_sourceDelayMode.currentText() == "auto":
            self.settingsWidget.label_sourceDelay.setEnabled(False)
            self.settingsWidget.lineEdit_sourceDelay.setEnabled(False)
            self.settingsWidget.label_sourceDelayUnits.setEnabled(False)
        else:
            self.settingsWidget.label_sourceDelay.setEnabled(True)
            self.settingsWidget.lineEdit_sourceDelay.setEnabled(True)
            self.settingsWidget.label_sourceDelayUnits.setEnabled(True)

    def _drain_delay_mode_changed(self, index):
        """Handles the visibility of the delay input fields based on the selected mode."""
        if self.settingsWidget.comboBox_drainDelayMode.currentText() == "auto":
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
        if inject_type == "voltage":
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
        if inject_type == "voltage":
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
        else:
            self.smu_settings = {}

        # Handle spectrometer settings separately
        if "spectrometer_settings" in settings:
            self.spectrometer_settings = settings["spectrometer_settings"]
        else:
            self.spectrometer_settings = {}

    def _get_public_methods(self):
        """
        Returns a nested dictionary of public methods for the plugin
        """
        # if the plugin type matches the requested type, return the functions

        methods = {
            method: getattr(self, method)
            for method in dir(self)
            if callable(getattr(self, method)) and not method.startswith("__") and not method.startswith("_") and method not in self.non_public_methods and method in self.public_methods
        }
        return methods

    ########Functions
    ############### run preparations
    def smuInit(self):
        """intializaes smu with data for the 1st sweep step

        Return [status, message]:
                status: 0 - no error, ~0 - error
                message
        """
        function_dict = self.dependency_manager.function_dict
        s = {}

        def guardrail_nplc(nplc_seconds, line_frequency):
            nplc = nplc_seconds * line_frequency
            if nplc > 25:
                nplc = 25
                self.logger.log_warn("NPLC value exceeds 25, setting to 25")
            return nplc

        freq = self.smu_settings["lineFrequency"]

        # THIS IS MISSING SOURCE VALUE ak start and end
        s["pulse"] = False
        s["source"] = self.settings["channel"]  # may take values depending on the channel names in smu, e.g. for Keithley 2612B [smua, smub]
        s["drain"] = self.settings["drainchannel"]
        s["type"] = "v" if self.settings["inject"] == "voltage" else "i"  # source inject current or voltage: may take values [i ,v]
        s["single_ch"] = self.settings["singlechannel"]  # single channel mode: may be True or False

        s["sourcenplc"] = guardrail_nplc(self.settings["sourcenplc"], freq)  # drain NPLC (may not be used in single channel mode)
        s["delay"] = True if self.settings["sourcedelaymode"] == "auto" else False  # stabilization time mode for source: may take values [True - Auto, False - manual]
        s["delayduration"] = self.settings["sourcedelay"]  # stabilization time duration if manual (may not be used in single channel mode)
        s["limit"] = self.settings["sourcelimit"]  # limit for current in voltage mode or for voltage in current mode (may not be used in single channel mode)
        s["sourcehighc"] = self.smu_settings["sourcehighc"]

        s["drainnplc"] = guardrail_nplc(self.settings["drainnplc"], freq)  # drain NPLC (may not be used in single channel mode)
        s["draindelay"] = True if self.settings["draindelaymode"] == "auto" else False  # stabilization time mode for source: may take values [True - Auto, False - manual]
        s["draindelayduration"] = self.settings["draindelay"]  # stabilization time duration if manual (may not be used in single channel mode)
        s["drainlimit"] = self.settings["drainlimit"]  # limit for current in voltage mode or for voltage in current mode (may not be used in single channel mode)
        s["drainhighc"] = self.smu_settings["drainhighc"]

        s["sourcedelayfactor"] = self.smu_settings["sourcedelayfactor"]

        # new addition for filters
        if self.smu_settings["drainfiltertype"] == "Repeat average":
            s["drainfiltertype"] = "FILTER_REPEAT_AVG"
            s["drainfiltervalue"] = self.smu_settings["drainfiltervalue"]
        else:
            s["drainfiltertype"] = "FILTER_OFF"
        s["draindelayfactor"] = self.smu_settings["draindelayfactor"]

        if self.smu_settings["sourcefiltertype"] == "Repeat average":
            s["sourcefiltertype"] = "FILTER_REPEAT_AVG"
            s["sourcefiltervalue"] = self.smu_settings["sourcefiltervalue"]
        else:
            s["sourcefiltertype"] = "FILTER_OFF"

        if self.settings["sourcesensemode"] == "4 wire":
            s["sourcesense"] = True  # source sence mode: may take values [True - 4 wire, False - 2 wire]
        else:
            s["sourcesense"] = False  # source sence mode: may take values [True - 4 wire, False - 2 wire]
        if self.settings["drainsensemode"] == "4 wire":
            s["drainsense"] = True  # source sence mode: may take values [True - 4 wire, False - 2 wire]
        else:
            s["drainsense"] = False  # source sence mode: may take values [True - 4 wire, False - 2 wire]

        function_dict["smu"][self.settings["smu"]]["smu_init"](s)

        return [0, {"message": "OK"}]

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

        status, data = self.parse_settings_widget()
        if status:
            error_msg = data.get("Error message", str(data)) if isinstance(data, dict) else str(data)
            self.logger.log_error("timeIV plugin: parse_settings_widget returned error: " + error_msg)
            self.logger.info_popup(error_msg)
            self.set_running(False)
            return [status, data]

        function_dict["smu"][self.settings["smu"]]["set_running"](True)

        status, state = function_dict["smu"][self.settings["smu"]]["smu_connect"]()
        if status:
            self.logger.log_error("timeIV plugin: smu_connect returned error: " + state)
            self.logger.info_popup(state)
            self.set_running(False)
            function_dict["smu"][self.settings["smu"]]["set_running"](False)
            return [2, {"Error message": state}]

        ##IRtodo#### check that the new file will not overwrite existing data -> implement dialog
        self.logger.log_debug("TimeIV run_thread created")
        self.run_thread = thread_with_exception(self._sequenceImplementation)
        self.run_thread.start()
        return [0, {"message": "OK"}]

    ########Functions
    ########sequence implementation
    def _saveData(self, fileheader, time, sourceI, sourceV, drainI=None, drainV=None):
        # the address is stored as path, append the filename and .dat extension to create the full file path
        fulladdress = os.path.join(self.settings["address"], self.settings["filename"] + ".dat")
        self.logger.log_debug("Saving data to file: " + fulladdress)

        if drainI is None:
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

        function_dict["smu"][self.settings["smu"]]["smu_connect"]()
        # if status:
        #    return [2, {"Error message": state}]

        self._sequenceImplementation()
        function_dict["smu"][self.settings["smu"]]["smu_disconnect"]()
        # if status:
        #    self.logger.log_warn(f"Error disconnecting SMU: {state}")
        return [0, {"message": "sweep finished"}]

    def _initialize_smu(self):
        """Initializes the SMU with the settings provided in self.settings."""
        function_dict = self.dependency_manager.function_dict
        smu_name = self.settings["smu"]
        self.logger.log_debug(f"Initializing SMU: {smu_name}")

        status, data = self.smuInit()
        if status:
            error_msg = data.get("Error message", str(data)) if isinstance(data, dict) else str(data)
            raise PluginException(error_msg)

        # turn off outputs, setup new source
        self.logger.log_debug("_timeIVimplementation: Turning off SMU output.")
        function_dict["smu"][smu_name]["smu_outputOFF"]()
        # if status:
        #    self.logger.log_warn(f"Error turning off SMU output: {state}")
        self.logger.log_debug("_timeIVimplementation: Setting SMU output for source channel.")
        status, state = function_dict["smu"][smu_name]["smu_setOutput"](
            self.settings["channel"],
            "v" if self.settings["inject"] == "voltage" else "i",
            self.settings["sourcevalue"],
        )
        if status:
            self.logger.log_warn(f"Error setting SMU output: {state}")

        # setup drain channel if not in single channel mode
        if not self.settings["singlechannel"]:
            self.logger.log_debug("_timeIVimplementation: Setting SMU output for drain channel.")
            status, state = function_dict["smu"][smu_name]["smu_setOutput"](
                self.settings["drainchannel"],
                "v" if self.settings["draininject"] == "voltage" else "i",
                self.settings["drainvalue"],
            )
            if status:
                self.logger.log_warn(f"Error setting SMU drain output: {state}")

        # Turn on output
        if not self.settings["singlechannel"]:
            self.logger.log_debug("_timeIVimplementation: Turning on SMU output for source and drain channels.")
            function_dict["smu"][smu_name]["smu_outputON"](self.settings["channel"], self.settings["drainchannel"])
        else:
            self.logger.log_debug("_timeIVimplementation: Turning on SMU output for source channel.")
            function_dict["smu"][smu_name]["smu_outputON"](self.settings["channel"])
        # if status:
        #    self.logger.log_warn(f"Error turning on SMU outputs: {state}")

        return [0, {"message": "SMU initialized successfully"}]

    def _initialize_spectrometer(self):
        """Initializes the spectrometer with the settings provided in self.spectrometer_settings."""
        function_dict = self.dependency_manager.function_dict
        spectrometer_name = self.settings["spectrometer"]
        self.logger.log_debug(f"Initializing spectrometer: {spectrometer_name}")

        function_dict["spectrometer"][spectrometer_name]["setSettings"](self.spectrometer_settings)

        status, state = function_dict["spectrometer"][spectrometer_name]["spectrometerConnect"]()
        if status:
            self.logger.log_warn(f"Error connecting Spectrometer: {state}")
            return [2, {"Error message": state}]
        # check what mode spectrometer is in for integration time
        auto_mode = self.spectrometer_settings["integrationtimetype"] == "auto"
        if auto_mode:
            self.logger.log_warn("Spectrometer auto integration time mode is not supported in spectimeIV plugin. Defaulting to constant integration time.")
        # Get and set constant integration time for the measurement
        integration_time_setting = self.spectrometer_settings["integrationtime"]
        self.logger.log_debug(f"Setting constant integration time: {integration_time_setting}")
        time.sleep(integration_time_setting + 1)  # Wait for the integration time to elapse before setting it
        status, state = function_dict["spectrometer"][spectrometer_name]["spectrometerSetIntegrationTime"](integration_time_setting)
        if status:
            self.logger.log_warn(f"Error setting integration time: {state}")
            raise PluginException(f"Error setting integration time: {state}")

        return [0, {"message": "Spectrometer initialized successfully"}]

    def _timeIVimplementation(self):
        function_dict = self.dependency_manager.function_dict
        self.logger.log_debug("_timeIVimplementation: Creating file header.")
        header = self.create_file_header(self.settings, self.smu_settings)
        spectrometer_name = self.settings["spectrometer"]
        smu_name = self.settings["smu"]

        status, data = self._initialize_smu()
        if status:
            error_msg = data.get("message", str(data)) if isinstance(data, dict) else str(data)
            self.logger.log_warn(f"Error initializing SMU: {error_msg}")
            raise PluginException(f"Error initializing SMU: {error_msg}")
        # output channels are now both on.

        status, data = self._initialize_spectrometer()
        if status:
            error_msg = data.get("message", str(data)) if isinstance(data, dict) else str(data)
            self.logger.log_warn(f"Error initializing Spectrometer: {error_msg}")
            raise PluginException(f"Error initializing Spectrometer: {error_msg}")
        # spectrometer now connected with integration time set

        timeData = []
        startTic = time.time()
        saveTic = startTic
        scan_counter = 0  # Counter for spectrometer file naming
        self.logger.log_debug("_timeIVimplementation: SMU initialized successfully.")

        # start of measurement loop
        drainIV = None  # Initialize to avoid unbound variable issues
        sourceV = []
        sourceI = []
        drainV = None
        drainI = None
        while True:
            # fetch IV Data for source
            self.logger.log_debug("_timeIVimplementation: Fetching IV data for source channel.")

            # Handle legacy [status, data] format for smu_getIV
            status, sourceIV = function_dict["smu"][smu_name]["smu_getIV"](self.settings["channel"])
            if status:
                raise PluginException(f"SMU getIV error for source: {sourceIV}")

            # fetch IV Data for drain if not in single channel mode
            if not self.settings["singlechannel"]:
                self.logger.log_debug("_timeIVimplementation: Fetching IV data for drain channel.")

                status, drainIV = function_dict["smu"][smu_name]["smu_getIV"](self.settings["drainchannel"])
                if status:
                    raise PluginException(f"SMU getIV error for drain: {drainIV}")
            else:
                drainIV = None

            currentTime = time.time()
            toc = currentTime - startTic

            # Plot doesn't exist yet, initialize it
            if not timeData:
                self.logger.log_debug("_timeIVimplementation: Initializing plots.")
                self.axes.cla()
                self.axes_twinx.cla()
                timeData.append(toc)
                sourceV = [sourceIV[DataOrder.V.value]]
                plot_refs = self.axes.plot(timeData, sourceV, "bo")
                self.axes.set_xlabel("time (s)")
                self.axes.set_ylabel("Voltage (V)")
                self._plot_sourceV = plot_refs[0]
                self.axes_twinx.set_ylabel("Current (A)")
                sourceI = [sourceIV[DataOrder.I.value]]
                plot_refs = self.axes_twinx.plot(timeData, sourceI, "b*")
                self._plot_sourceI = plot_refs[0]

                if not self.settings["singlechannel"] and drainIV is not None:
                    drainV = [drainIV[DataOrder.V.value]]
                    plot_refs = self.axes.plot(timeData, drainV, "go")
                    self._plot_drainV = plot_refs[0]
                    drainI = [drainIV[DataOrder.I.value]]
                    plot_refs = self.axes_twinx.plot(timeData, drainI, "g*")
                    self._plot_drainI = plot_refs[0]
                else:
                    drainI = None
                    drainV = None
            else:
                self.logger.log_debug("_timeIVimplementation: Updating plots.")
                timeData.append(toc)
                self.axes.cla()
                sourceV.append(sourceIV[DataOrder.V.value])
                sourceI.append(sourceIV[DataOrder.I.value])
                self.axes.plot(timeData, sourceV, "bo")
                self.axes_twinx.cla()
                self.axes_twinx.plot(timeData, sourceI, "b*")

                if not self.settings["singlechannel"] and drainIV is not None and drainV is not None and drainI is not None:
                    drainV.append(drainIV[DataOrder.V.value])
                    drainI.append(drainIV[DataOrder.I.value])
                    self.axes_twinx.plot(timeData, drainI, "g*")
                    self.axes.plot(timeData, drainV, "go")

            # plot is now updated, redraw the canvas
            self.axes.relim()
            self.axes.autoscale_view()
            self.sc.draw()

            # Take spectrometer scan after each plot update
            self.logger.log_debug("_timeIVimplementation: Taking spectrometer scan.")

            # Handle legacy [status, data] format for spectrometerGetScan
            status, spectrum = function_dict["spectrometer"][spectrometer_name]["spectrometerGetScan"]()
            if status:
                self.logger.log_warn(f"Error getting spectrum: {spectrum}")
                spectrum = None

            if spectrum is not None:
                # Save spectrum data with timestamp and IV data
                scan_counter += 1
                spectrum_filename = f"{self.spectrometer_settings['filename']}_scan_{scan_counter:04d}_t_{toc:.2f}s.csv"

                # Create metadata dictionary
                varDict = {}
                varDict["integrationtime"] = self.spectrometer_settings["integrationtime"]
                varDict["triggermode"] = 1 if self.spectrometer_settings.get("externalTrigger", False) else 0
                varDict["name"] = self.spectrometer_settings.get("samplename", "")
                varDict["timestamp"] = toc
                sourceIV_formatted = [float(sourceIV[DataOrder.I.value]), float(sourceIV[DataOrder.V.value])]

                # add IV data to the comment on the spectrometer file
                if not self.settings["singlechannel"] and drainI is not None and drainV is not None:
                    drainIV_formatted = [float(drainI[-1]), float(drainV[-1])]
                    varDict["comment"] = self.spectrometer_settings.get("comment", "") + f" Time: {toc:.2f}s, Source I/V: {sourceIV_formatted}, Drain I/V: {drainIV_formatted}"
                else:
                    varDict["comment"] = self.spectrometer_settings.get("comment", "") + f" Time: {toc:.2f}s, Source I/V: {sourceIV_formatted}"

                # Save spectrum file
                spectrum_address = self.spectrometer_settings["address"] + os.sep + spectrum_filename
                try:
                    status, state = function_dict["spectrometer"][spectrometer_name]["createFile"](varDict=varDict, filedelimeter=";", address=spectrum_address, data=spectrum)
                    if status:
                        self.logger.log_error(f"Error saving spectrum: {state}")
                    else:
                        self.logger.log_debug(f"Spectrum saved to: {spectrum_filename}")
                except Exception as e:
                    self.logger.log_error(f"Error saving spectrum: {e}")

            # check if it is time to stop
            if self.settings["stoptimer"]:
                if (currentTime - startTic) >= self.settings["stopafter"] * 60:  # convert to sec from min
                    self.logger.log_debug("_timeIVimplementation: Stop timer reached, saving data and exiting.")
                    self._saveData(header, timeData, sourceI, sourceV, drainI, drainV)
                    time.sleep(self.settings["timestep"])  # ensure the last data is saved before exiting
                    break

            # check if it is time to autosave
            if self.settings["autosave"]:
                if (currentTime - saveTic) >= self.settings["autosaveinterval"] * 60:  # convert to sec from min
                    self.logger.log_debug("_timeIVimplementation: Autosave interval reached, saving data.")
                    self._saveData(header, timeData, sourceI, sourceV, drainI, drainV)
                    saveTic = currentTime

            # take a nap until we need to take the next measurement
            time.sleep(self.settings["timestep"])

        self.logger.log_debug("_timeIVimplementation: Completed successfully.")
        return [0, {"message": "OK"}]

    def _sequenceImplementation(self):
        """
        Performs a timeIV on SMU, saves the result in a file

        Returns [status, message]:
               status: 0 - no error, ~0 - error
        """
        exception = 0  # handling turning off smu in case of exceptions. 0 = no exception, 1 - failure in smu, 2 - threadStopped, 3 - unexpected
        function_dict = self.dependency_manager.function_dict
        try:
            self._timeIVimplementation()
        except PluginException as e:
            self.logger.log_error(f"timeIV plugin implementation stopped because of exception: {e}")
            exception = 1
        except ThreadStopped:
            self.logger.log_error("timeIV plugin implementation aborted")
            exception = 2
        except Exception as e:
            self.logger.log_error(f"timeIV plugin implementation stopped because of unexpected exception: {e}")
            exception = 3
        finally:
            try:
                function_dict["smu"][self.settings["smu"]]["smu_outputOFF"]()
                # if status:
                #    self.logger.log_warn(f"Error turning off SMU output during cleanup: {state}")

                function_dict["smu"][self.settings["smu"]]["smu_disconnect"]()
                # if status:
                #    self.logger.log_warn(f"Error disconnecting SMU during cleanup: {state}")

                # status, state = function_dict["spectrometer"][self.settings["spectrometer"]]["spectrometerDisconnect"]()
                # if status:
                # self.logger.log_warn(f"Error disconnecting spectrometer during cleanup: {state}")

                if exception == 3 or exception == 1:
                    self.logger.info_popup("Implementation stopped because of exception. Check log")
            except Exception as e:
                self.logger.log_warn(f"timeIV plugin: smu or spectrometer turn off failed because of unexpected exception: {e}")

                self.logger.info_popup("SMU or spectrometer turn off failed. Check log")
            self.set_running(False)

    def read_gui(self) -> dict:
        """Reads the current GUI values into a dictionary that comforms to the pydantic schema.

        Returns:
            dict: settings dictionary
        """

        wid = self.settingsWidget
        return {
            "timestep": wid.step_lineEdit.text(),
            "stoptimer": wid.stopTimerCheckBox.isChecked(),
            "stopafter": float(wid.stopAfterLineEdit.text()),
            "address": wid.lineEdit_path.text(),
            "filename": wid.lineEdit_filename.text(),
            "comment": wid.lineEdit_comment.text(),
            "samplename": wid.lineEdit_sampleName.text(),
            "autosave": wid.autosaveCheckBox.isChecked(),
            "autosaveinterval": wid.autosaveLineEdit.text(),
            "singlechannel": wid.checkBox_singleChannel.isChecked(),
            "channel": wid.comboBox_channel.currentText(),
            "inject": wid.comboBox_inject.currentText(),
            "sourcesensemode": wid.comboBox_sourceSenseMode.currentText(),
            "sourcedelaymode": wid.comboBox_sourceDelayMode.currentText(),
            "sourcevalue": wid.lineEdit_sourceSetValue.text(),
            "sourcelimit": wid.lineEdit_sourceLimit.text(),
            "sourcenplc": ms_to_s(float(wid.lineEdit_sourceNPLC.text())),
            "sourcedelay": ms_to_s(float(wid.lineEdit_sourceDelay.text())),
            "draininject": wid.comboBox_drainInject.currentText(),
            "drainsensemode": wid.comboBox_drainSenseMode.currentText(),
            "draindelaymode": wid.comboBox_drainDelayMode.currentText(),
            "drainvalue": wid.lineEdit_drainSetValue.text(),
            "drainlimit": wid.lineEdit_drainLimit.text(),
            "drainnplc": ms_to_s(float(wid.lineEdit_drainNPLC.text())),
            "draindelay": ms_to_s(float(wid.lineEdit_drainDelay.text())),
            "smu": wid.smuBox.currentText(),
            "spectrometer": wid.spectroBox.currentText(),
        }


"""     def parse_settings_widget(self):


    function_dict = self.dependency_manager.function_dict
    if not function_dict:
        return (
            3,
            {
                "Error message": "Missing functions in timeIV plugin. Check log",
                "Missing functions": self.missing_functions,
            },
        )
    smu_selection = self.settingsWidget.smuBox.currentText()
    spectrometer_selection = self.settingsWidget.spectroBox.currentText()
    if smu_selection not in function_dict["smu"]:
        return (3, {"Error message": "SMU plugin not found in function_dict"})
    if spectrometer_selection not in function_dict["spectrometer"]:
        return (3, {"Error message": "Spectrometer plugin not found in function_dict"})

    # initialize new settings dict as to not write bad values to internal settings
    new_settings = {}
    new_settings["smu"] = smu_selection
    new_settings["spectrometer"] = spectrometer_selection

    status, smu_settings = function_dict["smu"][new_settings["smu"]]["parse_settings_widget"]()
    if status:
        return (2, smu_settings)
    status, spectrometer_settings = function_dict["spectrometer"][new_settings["spectrometer"]]["parse_settings_widget"]()
    if status:
        return (2, spectrometer_settings)

    status, save_settings = self._parseSaveData()
    if status:
        return (status, save_settings)
    else:
        new_settings.update(save_settings)

    try:
        new_settings["timestep"] = float(self.settingsWidget.step_lineEdit.text())
    except ValueError:
        return (1, {"Error message": "Value error in timeIV plugin: time step field should be numeric"})
    if new_settings["timestep"] <= 0:
        return (1, {"Error message": "Value error in timeIV plugin: time step field should be greater than 0"})
    try:
        new_settings["stopafter"] = float(self.settingsWidget.stopAfterLineEdit.text())
    except ValueError:
        return (1, {"Error message": "Value error in timeIV plugin: stop after field should be numeric"})
    if new_settings["stopafter"] <= 0:
        return (1, {"Error message": "Value error in timeIV plugin: autosave interval field should be numeric"})
    try:
        new_settings["autosaveinterval"] = float(self.settingsWidget.autosaveLineEdit.text())
    except ValueError:
        return (
            1,
            {"Error message": "Value error in timeIV plugin: autosave interval field should be greater than 0"},
        )
    if new_settings["autosaveinterval"] <= 0:
        return (
            1,
            {"Error message": "Value error in timeIV plugin: autosave interval field should be greater than 0"},
        )
    new_settings["stoptimer"] = self.settingsWidget.stopTimerCheckBox.isChecked()
    new_settings["autosave"] = self.settingsWidget.autosaveCheckBox.isChecked()

    # SMU settings
    # Determine source channel: may take values depending on the channel names in smu, eg. for Keithley 2612B [smua, smub]
    new_settings["channel"] = (self.settingsWidget.comboBox_channel.currentText()).lower()
    currentIndex = self.settingsWidget.comboBox_channel.currentIndex()
    if self.settingsWidget.comboBox_channel.count() > 1:
        if currentIndex == 0:
            new_settings["drainchannel"] = self.settingsWidget.comboBox_channel.itemText(1)
        else:
            new_settings["drainchannel"] = self.settingsWidget.comboBox_channel.itemText(0)
    else:
        new_settings["drainchannel"] = "xxx"  # for compatability if the smu does not support second channel

    # Determine source type: may take values [current, voltage]
    new_settings["inject"] = (self.settingsWidget.comboBox_inject.currentText()).lower()
    # Determine delay mode for source: may take values [auto, manual]
    new_settings["sourcedelaymode"] = (self.settingsWidget.comboBox_sourceDelayMode.currentText()).lower()
    # Determine source sence mode: may take values [2 wire, 4 wire, 2 & 4 wire]
    new_settings["sourcesensemode"] = (self.settingsWidget.comboBox_sourceSenseMode.currentText()).lower()
    # Determine delay mode for drain: may take values [auto, manual]
    new_settings["draindelaymode"] = (self.settingsWidget.comboBox_drainDelayMode.currentText()).lower()
    # Determine drain type: may take values [current, voltage]
    new_settings["draininject"] = (self.settingsWidget.comboBox_drainInject.currentText()).lower()
    # Determine drain sence mode: may take values [2 wire, 4 wire, 2 & 4 wire]
    new_settings["drainsensemode"] = (self.settingsWidget.comboBox_drainSenseMode.currentText()).lower()

    # Determine a single channel mode: may be True or False
    if self.settingsWidget.checkBox_singleChannel.isChecked():
        new_settings["singlechannel"] = True
    else:
        new_settings["singlechannel"] = False

    # Determine settings for source
    # start should be float
    try:
        new_settings["sourcevalue"] = float(self.settingsWidget.lineEdit_sourceSetValue.text())
    except ValueError:
        return (
            1,
            {"Error message": "Value error in timeIV plugin: source set value field should be numeric"},
        )

    # limit should be float >0
    try:
        new_settings["sourcelimit"] = float(self.settingsWidget.lineEdit_sourceLimit.text())
    except ValueError:
        return (
            1,
            {"Error message": "Value error in timeIV plugin: source limit field should be numeric"},
        )
    if new_settings["sourcelimit"] <= 0:
        return (
            1,
            {"Error message": "Value error in timeIV plugin: source limit field should be positive"},
        )

    # source nplc (in fact it is integration time for the measurement) is calculated from line frequency, should be float >0
    try:
        new_settings["sourcenplc"] = float(self.settingsWidget.lineEdit_sourceNPLC.text()) / 1000  # value in settings is in s; value in GUI is in ms
    except ValueError:
        return (
            1,
            {"Error message": "Value error in timeIV plugin: source nplc field should be numeric"},
        )
    if new_settings["sourcenplc"] <= 0:
        return (
            1,
            {"Error message": "Value error in timeIV plugin: source nplc field should be positive"},
        )

    # delay (in fact it is stabilization time before the measurement), for Keithley control should be in s in GUI is ms, should be >0
    try:
        new_settings["sourcedelay"] = float(self.settingsWidget.lineEdit_sourceDelay.text()) / 1000
    except ValueError:
        return (
            1,
            {"Error message": "Value error in timeIV plugin: source delay field should be numeric"},
        )
    if new_settings["sourcedelay"] <= 0:
        return (
            1,
            {"Error message": "Value error in timeIV plugin: source delay field should be positive"},
        )

    # start should be float
    try:
        new_settings["drainvalue"] = float(self.settingsWidget.lineEdit_drainSetValue.text())
    except ValueError:
        return (
            1,
            {"Error message": "Value error in timeIV plugin: drain set value field should be numeric"},
        )

    # limit should be float >0
    try:
        new_settings["drainlimit"] = float(self.settingsWidget.lineEdit_drainLimit.text())
    except ValueError:
        return (
            1,
            {"Error message": "Value error in timeIV plugin: drain limit field should be numeric"},
        )
    if new_settings["drainlimit"] <= 0:
        return (
            1,
            {"Error message": "Value error in timeIV plugin: drain limit field should be positive"},
        )

    # drain nplc (in fact it is integration time for the measurement) is calculated from line frequency, should be float >0
    try:
        new_settings["drainnplc"] = float(self.settingsWidget.lineEdit_drainNPLC.text()) / 1000  # value in settings is in s; value in GUI is in ms
    except ValueError:
        return (
            1,
            {"Error message": "Value error in timeIV plugin: drain nplc field should be numeric"},
        )
    if new_settings["drainnplc"] <= 0:
        return (
            1,
            {"Error message": "Value error in timeIV plugin: drain nplc field should be positive"},
        )

    # delay (in fact it is stabilization time before the measurement), for Keithley control should be in s in GUI is ms, should be >0
    try:
        new_settings["draindelay"] = float(self.settingsWidget.lineEdit_drainDelay.text()) / 1000
    except ValueError:
        return (
            1,
            {"Error message": "Value error in timeIV plugin: drain delay field should be numeric"},
        )
    if new_settings["draindelay"] <= 0:
        return (
            1,
            {"Error message": "Value error in timeIV plugin: drain delay field should be positive"},
        )
    # Commit internal state only after all validation passed.
    new_settings["smu"] = smu_selection
    new_settings["smu_settings"] = smu_settings

    new_settings["spectrometer"] = spectrometer_selection
    new_settings["spectrometer_settings"] = spectrometer_settings

    self.settings = copy.deepcopy(new_settings)
    self.smu_settings = copy.deepcopy(smu_settings)
    self.spectrometer_settings = copy.deepcopy(spectrometer_settings)

    # Return a copy so callers cannot mutate plugin state by reference.
    return [0, copy.deepcopy(self.settings)]"""
