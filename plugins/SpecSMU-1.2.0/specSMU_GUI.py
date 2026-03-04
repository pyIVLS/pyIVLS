"""
This is a plugin for using spectrometer while powering a device under the test with SMU.
In future this plugin planned to be extended to synchronius operation of SMU with spectrometer.

This is a fast implementation, i.e. it only bounds spectrometer to SMU for runing in sequence mode.
Standalone functionality may be added later.

ivarad
25.06.10

v1.2
HW trigger added
NPLC time bug corrected (previously smu recieved NPLC time in ms but not in nplc units)

ivarad
26.02.20
"""

import os

import time
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget
from settingsWidget import Ui_Form
import numpy as np
import copy
from typing import Optional
from plugin_components import LoggingHelper


class specSMU_GUI(QWidget):
    """GUI implementation"""

    non_public_methods = []  # add function names here, if they should not be exported as public to another plugins
    public_methods = [
        "parse_settings_widget",
        "sequenceStep",
        "setSettings",
        "set_gui_from_settings",
    ]  # add function names here, necessary for descendents of QObject, otherwise _get_public_methods returns a lot of QObject methods
    ########Signals

    def _log_verbose(self, message):
        self.logger.log_debug(message)

    ########Functions
    def __init__(self):
        super(specSMU_GUI, self).__init__()
        self.path = os.path.dirname(__file__) + os.path.sep
        self.dependency = {
            "smu": [
                "parse_settings_widget",
                "smu_connect",
                "smu_init",
                "smu_abort",
                "smu_outputOFF",
                "smu_outputON",
                "smu_disconnect",
                "set_running",
                "smu_setOutput",
                "smu_channelNames",
                "smu_trigpulse",
                "smu_bufferRead",
            ],
            "spectrometer": [
                "parse_settings_widget",
                "set_gui_from_settings",
                "setSettings",
                "spectrometerConnect",
                "spectrometerDisconnect",
                "spectrometerSetIntegrationTime",
                "spectrometerGetIntegrationTime",
                "spectrometerStartScan",
                "spectrometerGetSpectrum",
                "spectrometerGetScan",
            ],
        }
        # Load the settings based on the name of this file.
        self.settingsWidget = uic.loadUi(self.path + "specSMU_settingsWidget.ui")
        
        self.settings = {}
        self.function_dict = {}
        self.last_integration_time: Optional[float] = None  # s
        self.logger = LoggingHelper(self)
        self.logger.log_debug(f"specSMU GUI initialized with logger: {self.logger}")
        self._connect_signals()

    def _connect_signals(self) -> None:
        """
        Connect all relevant signals for the GUI widgets, including SMU selection changes.
        """
        # Connect the channel combobox
        self.settingsWidget.comboBox_mode.currentIndexChanged.connect(self._mode_changed)

        # Connect the inject type combobox
        inject_box = self.settingsWidget.comboBox_inject
        inject_box.currentIndexChanged.connect(self._inject_changed)

        delayComboBox = self.settingsWidget.comboBox_DelayMode

        delayComboBox.currentIndexChanged.connect(self._delay_mode_changed)
        # Connect SMU selection box
        self.settingsWidget.smuBox.currentIndexChanged.connect(self._smu_plugin_changed)
        self.settingsWidget.spectrometerBox.currentIndexChanged.connect(self._spectrometer_plugin_changed)
        # Connect spectro pause checkbox
        self.settingsWidget.spectroPause.stateChanged.connect(self._spectro_pause_changed)
        self.logger.log_debug("Signals connected")

    def _smu_plugin_changed(self, index: Optional[int] = None) -> None:
        """
        Handle changes in the selected SMU plugin. Updates the available channels in the channel combo box.

        Args:
            index (Optional[int]): Index of the selected SMU plugin.
        """
        smu_selection = self.settingsWidget.smuBox.currentText()
        if hasattr(self, "function_dict") and "smu" in self.function_dict and smu_selection in self.function_dict["smu"]:
            try:
                channel_names = self.function_dict["smu"][smu_selection]["smu_channelNames"]()
                self.settingsWidget.comboBox_channel.clear()
                self.settingsWidget.comboBox_channel.addItems(channel_names)
            except Exception:
                self.settingsWidget.comboBox_channel.clear()
        else:
            self.settingsWidget.comboBox_channel.clear()

    def _spectrometer_plugin_changed(self, index: Optional[int] = None) -> None:
        """
        Handle changes in the selected spectrometer plugin. Updates any relevant GUI elements if needed.

        Args:
            index (Optional[int]): Index of the selected spectrometer plugin.
        """
        # Placeholder for any spectrometer-specific GUI updates
        self._log_verbose("Spectrometer plugin changed, but no specific actions defined yet.")

    ########Functions
    ########GUI Slots

    def _update_GUI_state(self):
        self._mode_changed(self.settingsWidget.comboBox_mode.currentIndex())
        self._inject_changed(self.settingsWidget.comboBox_inject.currentIndex())
        self._delay_mode_changed(self.settingsWidget.comboBox_DelayMode.currentIndex())
        self._spectro_pause_changed()

    def _mode_changed(self, index):
        """Handles the visibility of the mode input fields based on the selected mode."""

        mode = self.settingsWidget.comboBox_mode.currentText()
        if mode == "Continuous":
            self.settingsWidget.label_pulsedPause.setEnabled(False)
            self.settingsWidget.label_pulsedPause_2.setEnabled(False)
            self.settingsWidget.lineEdit_Pause.setEnabled(False)
            self.settingsWidget.groupBox_HWtrigger.setEnabled(False)
        elif mode == "Pulsed":
            self.settingsWidget.label_pulsedPause.setEnabled(True)
            self.settingsWidget.label_pulsedPause_2.setEnabled(True)
            self.settingsWidget.lineEdit_Pause.setEnabled(True)
            self.settingsWidget.groupBox_HWtrigger.setEnabled(False)
        elif mode == "HW pulse":
            #### this should also update HW tigger in spectrometer plugin
            #### however, there will be an issue with initialization of GUI as it is not clear what plugin will be loaded first
            #### for now externaltrigger of spectrometer is updated only in setSettings
            self.settingsWidget.label_pulsedPause.setEnabled(True)
            self.settingsWidget.label_pulsedPause_2.setEnabled(True)
            self.settingsWidget.lineEdit_Pause.setEnabled(True)
            self.settingsWidget.groupBox_HWtrigger.setEnabled(True)

        self.update()

    def _inject_changed(self, index: int) -> None:
        """
        Update the unit labels based on the selected injection type.

        Args:
            index (int): Index of the selected item in the inject combo box.
        """
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

    def _spectro_pause_changed(self) -> None:
        """Enable or disable spectro pause input based on the checkbox state."""

        self.settingsWidget.spectroPauseSpinBox.setEnabled(self.settingsWidget.spectroPause.isChecked())

    def _delay_mode_changed(self, index: int) -> None:
        """
        Enable or disable delay input fields based on the selected delay mode.

        Args:
            index (int): Index of the selected item in the delay mode combo box.
        """
        auto = self.settingsWidget.comboBox_DelayMode.currentText() == "Auto"
        self.settingsWidget.label_Delay.setEnabled(not auto)
        self.settingsWidget.lineEdit_Delay.setEnabled(not auto)
        self.settingsWidget.label_DelayUnits.setEnabled(not auto)

        self.update()

    ########Functions
    ################################### internal

    ########Functions
    ###############GUI setting up
    def _initGUI(self, plugin_info: dict) -> None:
        """
        Populate the GUI with values from the provided settings dictionary.

        Args:
            plugin_info (dict): Settings from plugin_data in pyIVLS_*_plugin.
        """
        # no checks here, since the plugin_info comes from a trusted source,
        # seqbuilder or .ini file
        self.settings.update(plugin_info)
        self.set_gui_from_settings()

    def set_gui_from_settings(self) -> None:
        """
        Updates the GUI fields based on the provided settings dictionary.

        Args:
            settings (dict): Dictionary containing settings to update the GUI.
        """
        self._log_verbose("Setting GUI from provided settings.")
        settings = self.settings
        # Set SMU selection
        smu_name = settings.get("smu", "")
        self.settingsWidget.smuBox.clear()
        self.settingsWidget.smuBox.addItems(list(self.function_dict["smu"].keys()))
        if smu_name:
            idx = self.settingsWidget.smuBox.findText(smu_name, Qt.MatchFlag.MatchFixedString)
            if idx > -1:
                self.settingsWidget.smuBox.setCurrentIndex(idx)

        # Set spectrometer selection
        spectro_name = settings.get("spectrometer", "")
        self.settingsWidget.spectrometerBox.clear()
        self.settingsWidget.spectrometerBox.addItems(list(self.function_dict["spectrometer"].keys()))
        if spectro_name:
            idx = self.settingsWidget.spectrometerBox.findText(spectro_name, Qt.MatchFlag.MatchFixedString)
            if idx > -1:
                self.settingsWidget.spectrometerBox.setCurrentIndex(idx)

        # Set combo boxes
        combo_map = {
            "comboBox_channel": "channel",
            "comboBox_inject": "inject",
            "comboBox_mode": "mode",
            "comboBox_DelayMode": "delaymode",
            "comboBox_sourceSenseMode": "sourcesensemode",
        }
        for box_name, key in combo_map.items():
            box = getattr(self.settingsWidget, box_name, None)
            value = settings.get(key, "")
            if box and value:
                idx = box.findText(value, Qt.MatchFlag.MatchFixedString)
                if idx > -1:
                    box.setCurrentIndex(idx)

        # Set line edits
        line_map = {
            "lineEdit_Start": "start",
            "lineEdit_End": "end",
            "lineEdit_Points": "points",
            "lineEdit_Limit": "limit",
        }
        for line_name, key in line_map.items():
            line_edit = getattr(self.settingsWidget, line_name, None)
            value = settings.get(key, "")
            if line_edit and value != "":
                line_edit.setText(str(value))

        # setnplc and delay (ms in GUI, s in settings)
        try:
            self.settingsWidget.lineEdit_NPLC.setText(f"{float(settings.get("nplc", 0.02))*1000}")
        except:
            self.logger.log_warn("Setting GUI from settings conversion failed. nplc is set as it is in settings")
            self.settingsWidget.lineEdit_NPLC.setText(str(settings.get("nplc", 0.02)))
        try:
            self.settingsWidget.lineEdit_Delay.setText(f"{float(settings.get("delay", 0.32))*1000}")
        except:
            self.logger.log_warn("Setting GUI from settings conversion failed.delay is set as it is in settings")
            self.settingsWidget.lineEdit_Delay.setText(str(settings.get("delay", 0.32)))

        # Set checkboxes
        def set_checkbox(cb_name: str, setting_key: str):
            cb = getattr(self.settingsWidget, cb_name, None)
            value = settings.get(setting_key, False)
            if cb is not None:
                if isinstance(value, str):
                    cb.setChecked(value.lower() == "true")
                else:
                    cb.setChecked(bool(value))

        set_checkbox("spectroUseLastInteg", "spectro_use_last_integ")
        set_checkbox("spectroCheckAfter", "spectro_check_after")
        set_checkbox("spectroPause", "spectro_pause")
        set_checkbox("checkBox_singleChannel", "singlechannel")

        # set spinbox
        spectro_pause_time = settings.get("spectro_pause_time", 1.0)
        self.settingsWidget.spectroPauseSpinBox.setValue(float(spectro_pause_time))

        # set HW trig
        try:
            self.settingsWidget.lineEdit_HWtrig_pulse.setText(f"{float(settings.get("hwtrigpulse", 0.00001))*1000}")
        except:
            self.logger.log_warn("Setting GUI from settings conversion failed. hwtrigpulse is set as it is in settings")
            self.settingsWidget.lineEdit_HWtrig_pulse.setText(str(settings.get("hwtrigpulse", 0.00001)))
            

        try:
            self.settingsWidget.lineEdit_powerPulse.setText(f"{float(settings.get("powerpulseext", 0.0005))*1000}")
        except:
            self.logger.log_warn("Setting GUI from settings conversion failed. powerpulseext is set as it is in settings")
            self.settingsWidget.lineEdit_powerPulse.setText(str(settings.get("powerpulseext", 0.0005)))

        self.settingsWidget.spinBox_digio.setValue(int(settings.get("ioline", 4)))
        
        # Update GUI state
        self._update_GUI_state()

        ### this function may be called either form seqBuilder to populate GUI or at initialization.
        ### at initialization the key "spectrometer_settings" is not in settings, so the GUI update for spectrometer plugin should not be performed
        if "spectrometer_settings" in self.settings:
            self.function_dict["spectrometer"][spectro_name]["set_gui_from_settings"]()

    ########Functions
    ###############GUI react to change

    ########Functions
    ########plugins interraction

    def set_dependencies(self, dependencies: list) -> None:
        """
        Set the list of plugin dependencies (e.g., available SMU and spectrometer types).
        Args:
            dependencies (list): List of dependency plugin names.
        """
        self.dependencies = dependencies
        # If function_dict is available, update the smuBox and spectrometerBox with available plugins
        self.settingsWidget.smuBox.clear()
        smu_keys = list(self.function_dict["smu"].keys()) if "smu" in self.function_dict else []
        self.settingsWidget.smuBox.addItems(smu_keys)
        self.settingsWidget.spectrometerBox.clear()
        spectro_keys = list(self.function_dict["spectrometer"].keys()) if "spectrometer" in self.function_dict else []
        self.settingsWidget.spectrometerBox.addItems(spectro_keys)

    def _getPublicFunctions(self, function_dict):
        self.missing_functions = []
        for dependency_plugin in list(self.dependency.keys()):
            if dependency_plugin not in function_dict:
                self.missing_functions.append(dependency_plugin)
                continue
            for dependency_function in self.dependency[dependency_plugin]:
                if dependency_function not in function_dict[dependency_plugin]:
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
            if callable(getattr(self, method)) and not method.startswith("__") and not method.startswith("_") and method not in self.non_public_methods and method in self.public_methods
        }
        return methods

    ########Functions to be used externally
    ###############get settings from GUI
    def parse_settings_widget(self):
        """
        Parses the settings widget for the plugin. Extracts current values. Checks if values are allowed. Provides settings to an external plugin if needed

        Returns [status, settings_dict]:
            status: 0 - no error, ~0 - error
            self.settings
        """
        self._log_verbose("Entering parse_settings_widget")

        if not self.function_dict:
            self._log_verbose("Missing function_dict in SpecSMU plugin")
            return [
                3,
                {
                    "Error message": "Missing functions in SpecSMU plugin. Check log",
                    "Missing functions": self.missing_functions,
                },
            ]

        # Use the raw getter for initial settings
        raw_settings = self.get_settings_dict_raw()
        self._log_verbose(f"Raw settings retrieved: {raw_settings}")

        # Validate and parse raw settings
        try:
            self.settings = {}
            self.settings["smu"] = raw_settings["smu"]
            self.settings["spectrometer"] = raw_settings["spectrometer"]
            self.settings["channel"] = raw_settings["channel"].lower()
            self.settings["inject"] = raw_settings["inject"].lower()
            self.settings["mode"] = raw_settings["mode"].lower()
            self.settings["delaymode"] = raw_settings["delaymode"].lower()
            self.settings["sourcesensemode"] = raw_settings["sourcesensemode"].lower()
            self.settings["singlechannel"] = raw_settings["singlechannel"]  # bool
            self.settings["spectro_check_after"] = raw_settings["spectro_check_after"]  # bool
            self.settings["spectro_pause"] = raw_settings["spectro_pause"]  # bool
            self.settings["spectro_use_last_integ"] = raw_settings["spectro_use_last_integ"]  # bool
            self.settings["drainchannel"] = ""  # PLACEHOLDER FIXME:


            # Parse numeric fields
            self.settings["start"] = float(raw_settings["start"])
            self.settings["end"] = float(raw_settings["end"])
            self.settings["points"] = int(raw_settings["points"])
            self.settings["limit"] = float(raw_settings["limit"])
            self.settings["nplc"] = float(raw_settings["nplc"])/1000
            self.settings["delay"] = float(raw_settings["delay"])/1000
            self.settings["pause"] = float(raw_settings["pause"])
            self.settings["spectro_pause_time"] = float(raw_settings["spectro_pause_time"])  # should already be float from double spin box
            self.settings["repeat"] = int(raw_settings["repeat"])  # will already be an int from spin box
            self.settings["hwtrigpulse"] = float(raw_settings["hwtrigpulse"])/1000
            if self.settings["hwtrigpulse"]<0:
                self._log_verbose(f"Value error in SpecSMU plugin: HW trigger pulse width can not be negative")
                return [1, {"Error message": f"Value error in SpecSMU plugin: HW trigger pulse width can not be negative"}]
            self.settings["powerpulseext"] = float(raw_settings["powerpulseext"])/1000
            if self.settings["powerpulseext"]<0:
                self._log_verbose(f"Value error in SpecSMU plugin: extension of the power pulse can not be negative")
                return [1, {"Error message": f"Value error in SpecSMU plugin: extension of the power pulse can not be negative"}]
            self.settings.["ioline"] = int(raw_settings["ioline"]) # should already be an int from spinbox

            self._log_verbose("Settings successfully parsed and validated")
        except ValueError as e:
            self._log_verbose(f"Error parsing settings: {e}")
            return [1, {"Error message": f"Value error in SpecSMU plugin: {e}"}]

        # Get selected SMU plugin
        smu_selection = self.settings["smu"]
        if smu_selection:
            [status, self.smu_settings] = self.function_dict["smu"][smu_selection]["parse_settings_widget"]()
            if status:
                self._log_verbose(f"Error in SMU plugin settings: {self.smu_settings}")
                return [2, self.smu_settings]
        else:
            self._log_verbose("No SMU selected")
            return [1, {"Error message": "No SMU selected"}]

        # Get selected spectrometer plugin
        spectro_selection = self.settings["spectrometer"]
        if spectro_selection:
            [status, self.spectrometer_settings] = self.function_dict["spectrometer"][spectro_selection]["parse_settings_widget"]()
            if status:
                self._log_verbose(f"Error in spectrometer plugin settings: {self.spectrometer_settings}")
                return [2, self.spectrometer_settings]
        else:
            self._log_verbose("No spectrometer selected")
            return [1, {"Error message": "No spectrometer selected"}]

        self.settings["smu_settings"] = self.smu_settings
        self.settings["spectrometer_settings"] = self.spectrometer_settings

        self._log_verbose("Exiting parse_settings_widget with success")
        return [0, self.settings]

    def setSettings(self, settings):  #### settings from sequenceBuilder
        # the filename in settings may be modified, as settings parameter is pointer, it will modify also the original data. So need to make sure that the original data is intact
        self.settings = {}
        self.settings = self.settings.update(copy.deepcopy(settings))
        self.smu_settings = self.settings["smu_settings"]
        if self.settings["mode"] == "hw pulse":
                self.settings["spectrometer_settings"]["externaltrigger"] = True
        else:
                self.settings["spectrometer_settings"]["externaltrigger"] = False
        self.spectrometer_settings = self.settings["spectrometer_settings"]
        spectro_name = self.settings["spectrometer"]
        self.function_dict["spectrometer"][spectro_name]["setSettings"](self.spectrometer_settings)
        

    # this function is called not from the main thread. Direct addressing of qt elements not from the main thread causes segmentation fault crash. Using a signal-slot interface between different threads should make it work
    #        self._setGUIfromSettings()
    ###############GUI enable/disable

    ###############sequence implementation

    def sequenceStep(self, postfix):
        self._log_verbose("Entering sequenceStep with postfix: " + postfix)
        self.spectrometer_settings["filename"] = self.spectrometer_settings["filename"] + postfix
        smu_name = self.settings["smu"]
        spectro_name = self.settings["spectrometer"]
        self._log_verbose(f"SMU: {smu_name}, Spectrometer: {spectro_name}")

        [status, message] = self.function_dict["smu"][smu_name]["smu_connect"]()
        if status:
            self._log_verbose(f"Error connecting SMU: {message}")
            return [status, message]

        self.function_dict["spectrometer"][spectro_name]["setSettings"](self.spectrometer_settings)
        [status, message] = self.function_dict["spectrometer"][spectro_name]["spectrometerConnect"]()
        if status:
            self._log_verbose(f"Error connecting Spectrometer: {message}")
            return [status, message]

        try:
            self._log_verbose("inside try block of sequenceStep")
            self._SpecSMUImplementation()
            self._log_verbose("SpecSMU action finished successfully")
            return [0, "specSMU action finished"]
        except Exception as e:
            self.logger.log_error("")  # log error includes traceback already
            return [1, {"Error message": "SpecSMU plugin: error in seq implementation", "Exception": str(e)}]
        finally:
            self.function_dict["smu"][smu_name]["smu_abort"](self.settings["channel"]) #in case of HW trig, as formally it uses a sweep
            self.function_dict["smu"][smu_name]["smu_outputOFF"]()
            self.function_dict["smu"][smu_name]["smu_disconnect"]()
            self.function_dict["spectrometer"][spectro_name]["spectrometerDisconnect"]()

    def smuInit(self):
        self._log_verbose("Entering smuInit")
        s = {}

        s["pulse"] = self.settings["mode"] == "pulsed"  # pulsed mode: may be True or False
        s["source"] = self.settings["channel"]  # may take values depending on the channel names in smu, e.g. for Keithley 2612B [smua, smub]
        s["drain"] = self.settings["drainchannel"]
        s["type"] = "v" if self.settings["inject"] == "voltage" else "i"  # source inject current or voltage: may take values [i ,v]
        s["single_ch"] = self.settings["singlechannel"]  # single channel mode: may be True or False

        s["sourcenplc"] = self.settings["nplc"] * self.smu_settings["lineFrequency"] #see page 552 of Keithley manual: 1 PLC = 20 ms for 50 Hz (nplc = time [s] * freq [Hz])
        s["delay"] = True if self.settings["delaymode"] == "auto" else False  # stabilization time mode for source: may take values [True - Auto, False - manual]
        s["delayduration"] = self.settings["delay"]  # stabilization time duration if manual (may not be used in single channel mode)
        s["limit"] = self.settings["limit"]  # limit for current in voltage mode or for voltage in current mode (may not be used in single channel mode)
        s["sourcehighc"] = self.smu_settings["sourcehighc"]

        s["start"] = self.settings["start"]  # start value for source, added for current injection to work
        s["end"] = self.settings["end"]  # end value for source -||-
        s["points"] = self.settings["points"]  # number of points for source -||-
        if self.settings["sourcesensemode"] == "4 wire":
            s["sourcesense"] = True  # source sence mode: may take values [True - 4 wire, False - 2 wire]
        else:
            s["sourcesense"] = False  # source sence mode: may take values [True - 4 wire, False - 2 wire]
        self._log_verbose(f"SMU settings: {s}")

        if not s["single_ch"]:
            self._log_verbose("Dual channel mode not implemented")
            return [1, {"Error message": "SpecSMU plugin: dual channel mode not implemented"}]

        if self.function_dict["smu"][self.settings["smu"]]["smu_init"](s):
            self._log_verbose("Error initializing SMU")
            return [2, {"Error message": "SpecSMU plugin: error in SMU plugin can not initialize"}]

        self._log_verbose("Leaving smuInit")
        return (0, "OK")

    def _make_hwtrig_dict(self):
        """ form the dict to be used with smu_trigpulse
        description of the dict in spectrometer plugin, function header"""
        trigpulse_dict = {}
        trigpulse_dict["source"] = self.settings["channel"]
        trigpulse_dict["type"] = 'v' if self.settings["inject"] == 'voltage' else 'i'
        trigpulse_dict["value"] = smuSetValue
        trigpulse_dict["limit"] = self.settings["limit"]
        trigpulse_dict["spectro_check_after"] = self.settings["spectro_check_after"]
        trigpulse_dict['sourcenplc'] =  self.settings["nplc"] * self.smu_settings["lineFrequency"] #see page 552 of Keithley manual: 1 PLC = 20 ms for 50 Hz (nplc = time [s] * freq [Hz])
        trigpulse_dict['nplcms'] =  self.settings["nplc"]*1000
        trigpulse_dict['delay'] = True if self.settings["delaymode"] == "auto" else False
        trigpulse_dict['delayduration'] = 0.360 if trigpulse_dicts['delay'] else self.settings["delay"]# duration of the delay before measurement if manual in s, max auto delay if measuredelay == True, i.e. 360ms see p.255 (float)
        trigpulse_dict['postwait'] = self.settings["powerpulseext"]
        trigpulse_dict['integrationtime'] = None #this in any case will be set in spectrometer plugin
        trigpulse_dict['linen'] = self.settings["ioline"]
        trigpulse_dict['digiopulse'] = self.settings["hwtrigpulse"]
        return trigpulse_dict

    def _SpecSMUImplementation(self):
        self._log_verbose("Entering _SpecSMUImplementation")
        smu_name = self.settings["smu"]
        spectro_name = self.settings["spectrometer"]
        if not self.settings["mode"] == "hw trig":
            status, state = self.smuInit()
            assert status == 0, f"Error in initializing SMU: {state}"
        smuLoop = self.settings["points"]
        if smuLoop > 1:
            smuChange = (self.settings["end"] - self.settings["start"]) / (smuLoop - 1)
        else:
            smuChange = 0
        specFilename = self.spectrometer_settings["filename"]
        repeat = self.settings["repeat"]
        for rep in range(repeat):
            self._log_verbose(f"Starting repeat {rep + 1} of {repeat}")
            # iterate over the SMU loop steps
            for smuLoopStep in range(smuLoop):
                smuSetValue = self.settings["start"] + smuLoopStep * smuChange
                if self.settings["mode"] == "continuous":
                    self._log_verbose(f"Setting SMU output to {smuSetValue}")
                    # set output on SMU
                    self.function_dict["smu"][smu_name]["smu_setOutput"](self.settings["channel"], "v" if self.settings["inject"] == "voltage" else "i", smuSetValue)
                    self._log_verbose("SMU output set")
#                integration_time_setting = float(self.spectrometer_settings["integrationtime"])
#                status, integration_time_seconds = self.function_dict["spectrometer"][spectro_name]["spectrometerGetIntegrationTime"]()
#                integration_time = integration_time_seconds
#                if status:
#                    self._log_verbose(f"Error getting integration time: {integration_time}")
#                    raise NotImplementedError(f"Error in getting integration time from spectrometer: {integration_time}, no handling provided")

                # set filename
                self.spectrometer_settings["filename"] = specFilename + f"_{smuSetValue:.4f}" + f"_{rep}" + " iv.csv"

                # automatic integration time handling
                if self.spectrometer_settings["integrationtimetype"] == "auto":
                    # set settings for spectrometer
                    self.function_dict["spectrometer"][spectro_name]["setSettings"](self.spectrometer_settings)

                    # use last integration time if checkbox is set and last_integration_time is available
                    last_integration_time = None
                    if self.settings["spectro_use_last_integ"]:
                        # no checks on wheter self.last_integration_time is set, since getAutoTime takes in Optional[float]
                        self._log_verbose(f"Using last valid integration time as initial guess for AutoTime: {self.last_integration_time}")
                        last_integration_time = self.last_integration_time

                    # check mode, pulse or continuous
                    if self.settings["mode"] == "continuous":
                        self.function_dict["smu"][smu_name]["smu_outputON"](self.settings["channel"])
                        status, auto_time = self.function_dict["spectrometer"][spectro_name]["getAutoTime"](last_integration_time=last_integration_time)
                    elif self.settings["mode"] == "pulsed":
                        # "Abandon all hope, ye who enter here"
                        status, auto_time = self.function_dict["spectrometer"][spectro_name]["getAutoTime"](
                            external_action=self.function_dict["smu"][smu_name]["smu_outputON"],
                            external_action_args=(self.settings["channel"],),
                            external_cleanup=self.function_dict["smu"][smu_name]["smu_outputOFF"],
                            pause_duration=self.settings["pause"],
                            last_integration_time=last_integration_time,
                        )
                    elif self.settings["mode"] == "hw trig":

                        # hw trig mode mainly based on smu_trigpulse. Spectrometer plugin understands that it is in hw trig mode from externaltrigger setting
                        status, auto_time = self.function_dict["spectrometer"][spectro_name]["getAutoTime"](
                            external_action=self.function_dict["smu"][smu_name]["smu_trigpulse"],
                            external_action_args=(_make_hwtrig_dict(),),
                            external_cleanup=self.function_dict["smu"][smu_name]["smu_outputOFF"],
                            pause_duration=self.settings["pause"],
                            last_integration_time=last_integration_time,
                        )

                    # Depending on the branch, auto_time may be None if getAutoTime failed
                    if status == 0:
                        # Write integration time setting to be the one determined by auto time
                        integration_time_setting = float(auto_time)
                    # failure in autotime
                    elif status == 1:
                        if auto_time["Error message"] == "Integration time too high":
                            raise NotImplementedError(f"Error in getting auto integration time: {auto_time}, no handling provided")
                        elif auto_time["Error message"] == "Integration time too low":
                            # getAutoTime failed because it hit the lower limit of the auto range
                            continue  # skip this point, do not measure
                        else:
                            raise NotImplementedError(f"Error in getting auto integration time: {auto_time}, no handling provided")
                    # some other error code than 0,1
                    else:
                        self._log_verbose(f"Error getting auto integration time: {auto_time}")
                        # autotime failed
                        raise NotImplementedError(f"Error in getting auto integration time: {auto_time}, no handling provided")
                # non-automatic integration time handling
                else:
                    integration_time_setting = float(self.spectrometer_settings["integrationtime"])

                # integration time setting is determined based on autotime or from GUI, now check if it is different from the current one
                status, integration_time_seconds = self.function_dict["spectrometer"][spectro_name]["spectrometerGetIntegrationTime"]()
                integration_time = integration_time_seconds
                if status:
                    self._log_verbose(f"Error getting integration time: {integration_time}")
                    raise NotImplementedError(f"Error in getting integration time from spectrometer: {integration_time}, no handling provided")

                # check integration time
                if not np.isclose(integration_time, integration_time_setting, atol=0, rtol=0.0001):
                    self._log_verbose(f"Setting integration time to {integration_time_setting}, current is {integration_time}")
                    self._log_verbose(f"Integ time determined with mode: {self.spectrometer_settings['integrationtimetype']}")
                    status, state = self.function_dict["spectrometer"][spectro_name]["spectrometerSetIntegrationTime"](integration_time_setting)
                    if status:
                        self._log_verbose(f"Error setting integration time: {integration_time_setting}")
                        raise NotImplementedError(f"Error in setting integration time: {state}, no handling provided")
                else:
                    self._log_verbose(f"Not changing integration time, current {integration_time} is close to setting {integration_time_setting}")
                    self._log_verbose(f"Integ time determined with mode: {self.spectrometer_settings['integrationtimetype']}")

                if not self.settings["mode"] == "hw trig":
                    # integration time set, smu ready, spectrometer ready:
                    self.function_dict["smu"][smu_name]["smu_outputON"](self.settings["channel"])  # output on

                    # pause before any measurements if spectro_pause is set
                    if self.settings["spectro_pause"]:
                        self._log_verbose(f"Pausing for {self.settings['spectro_pause_time']} seconds before reading spectrum")
                        time.sleep(self.settings["spectro_pause_time"])

                    # if checkbox for before and after is set:
                    after_flag = self.settings["spectro_check_after"]
                    sourceIV_before = (None, None)
                    if after_flag:
                        # IV before spectrum
                        status, sourceIV_before = self.function_dict["smu"][smu_name]["smu_getIV"](self.settings["channel"])

                    # spectrum
                    status, spectrum = self.function_dict["spectrometer"][spectro_name]["spectrometerGetScan"]()
                    if status:
                        self._log_verbose(f"Error getting spectrum: {spectrum}")
                        raise NotImplementedError(f"Error in getting spectrum: {spectrum}, no handling provided")
                        
                    # IV after spectrum
                    status, sourceIV_after = self.function_dict["smu"][smu_name]["smu_getIV"](self.settings["channel"])
                    time.sleep(0.02)
                #HW trig mode
                else:
                    #arm spectrometer
                    self.self.function_dict["spectrometer"][spectro_name]["spectrometerTrigScan"]()
                    time.sleep(0.02) #just a precaution, duration does not mean anything specific, does not affect the measurement as smu is off
                    #make dict for smu, as we do not know if autotime was used
                    trigDict = _make_hwtrig_dict()
                    trigDict["integrationtime"] = integration_time_setting#in s
                    #run smupulse
                    status, info = self.function_dict["smu"][smu_name]["smu_trigpulse"](trigDict)
                    if status:
                        self._log_verbose(f"Error running smupulse: {info}")
                        raise NotImplementedError(f"Error in smu_trigpulse: {info}, no handling provided")
                    time.sleep(0.2)#probably not needed
                    
                    # spectrum
                    status, spectrum = self.function_dict["spectrometer"][spectro_name]["spectrometerGetScan"]()
                    if status:
                        self._log_verbose(f"Error getting spectrum: {spectrum}")
                        raise NotImplementedError(f"Error in getting spectrum: {spectrum}, no handling provided")

                # scan finished, now time to sleep if in pulsed mode
                if not self.settings["mode"] == "continuous":
                    self.function_dict["smu"][smu_name]["smu_outputOFF"]()
                    self._log_verbose(f"Sleeping for {self.settings['pause']} seconds in pulsed mode")
                    time.sleep(self.settings["pause"])

                # saving the results
                varDict = {}
                varDict["integrationtime"] = integration_time_setting
                varDict["triggermode"] = 1 if self.spectrometer_settings["externalTrigger"] else 0
                varDict["name"] = self.spectrometer_settings["samplename"]
                if self.settings["mode"] == "hw trig":
                    IVdata = self.function_dict["smu"][self.settings["smu"]]["smu_bufferRead"](trigDict["source"])
                    readings = ",".join(map(str, IVdata.ravel()))
                else:
                    if after_flag:
                        # sourceIV is returned as a tuple (i, v, readings)
                        i_before, v_before = sourceIV_before
                        i_after, v_after = sourceIV_after
                        readings = str(i_before) + "," + str(v_before) + "," + str(i_after) + "," + str(v_after)
                    else:
                        i_after, v_after = sourceIV_after
                        readings = str(i_after) + "," + str(v_after)

                varDict["comment"] = self.spectrometer_settings["comment"] + " " + readings
                address = self.spectrometer_settings["address"] + os.sep + self.spectrometer_settings["filename"]
                status, state = self.function_dict["spectrometer"][spectro_name]["createFile"](varDict=varDict, filedelimeter=";", address=address, data=spectrum)
                if status:
                    self.logger.log_error(f"Error writing to file: {state}")
                    raise NotImplementedError(f"Error in writing spectrum to file: {state}, no handling provided")

                # updating the internal state of last integration time
                self.last_integration_time = integration_time_setting
                # do not continue if reached the limit
                if (
                        self.settings["inject"] == "voltage"
                        and abs(i_after) >= abs(self.settings["limit"])
                    ) or (
                        self.settings["inject"] == "current"
                        and (abs(lastV) >= abs(measurement["limit"]))
                    ):
                        self.function_dict["smu"][smu_name]["smu_outputOFF"]()
                        break
        self._log_verbose("Exiting _SpecSMUImplementation")
        return 0

    def get_settings_dict_raw(self) -> dict:
        """
        Returns the current settings from the GUI as a raw dictionary (no parsing/validation).
        This is useful for saving or for further parsing/validation elsewhere.
        Does not write to internal state.
        """
        settings = {}
        settings["smu"] = self.settingsWidget.smuBox.currentText()
        settings["spectrometer"] = self.settingsWidget.spectrometerBox.currentText()
        settings["channel"] = self.settingsWidget.comboBox_channel.currentText()
        settings["inject"] = self.settingsWidget.comboBox_inject.currentText()
        settings["mode"] = self.settingsWidget.comboBox_mode.currentText()
        settings["delaymode"] = self.settingsWidget.comboBox_DelayMode.currentText()
        settings["sourcesensemode"] = self.settingsWidget.comboBox_sourceSenseMode.currentText()
        settings["singlechannel"] = self.settingsWidget.checkBox_singleChannel.isChecked()
        settings["start"] = self.settingsWidget.lineEdit_Start.text()
        settings["end"] = self.settingsWidget.lineEdit_End.text()
        settings["points"] = self.settingsWidget.lineEdit_Points.text()
        settings["limit"] = self.settingsWidget.lineEdit_Limit.text()
        settings["nplc"] = self.settingsWidget.lineEdit_NPLC.text()
        settings["delay"] = self.settingsWidget.lineEdit_Delay.text()
        settings["pause"] = self.settingsWidget.lineEdit_Pause.text()
        settings["spectro_check_after"] = self.settingsWidget.spectroCheckAfter.isChecked()
        settings["spectro_pause"] = self.settingsWidget.spectroPause.isChecked()
        settings["spectro_pause_time"] = self.settingsWidget.spectroPauseSpinBox.value()
        settings["spectro_use_last_integ"] = self.settingsWidget.spectroUseLastInteg.isChecked()
        settings["repeat"] = self.settingsWidget.repeat_spinbox.value()
        settings["hwtrigpulse"] = self.settingsWidget.lineEdit_HWtrig_pulse.text()
        settings["powerpulseext"] = self.settingsWidget.lineEdit_powerPulse.text()
        settings["ioline"] = self.settingsWidget.spinBox_digio.value()
        return settings
