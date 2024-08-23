import sys
import os
import time
from threading import RLock, Lock


from PyQt6 import uic
from PyQt6.QtWidgets import (
    QWidget,
    QCheckBox,
    QComboBox,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QLabel,
)
from PyQt6.QtCore import QObject

import pyvisa
import numpy as np
import time

import pyIVLS_constants

"""
My notes:
Keithely2600 can handle voltage sweeps, but the following parameters need to be set separately:
-high c
-sense 
-limits for curr
-pulse pause
-repeat
-current injection instead of voltage

Currently, Keithley2600 is only used to check if the device is busy.
It might not be necessary to use it at all.
"""


class Keithley2612B:

    ####################################  threads

    ################################### internal functions

    ########Slots

    ########Signals

    ########Functions
    def __init__(self):

        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        filename = (
            os.path.splitext(os.path.basename(__file__))[0] + "_settingsWidget.ui"
        )
        self.settingsWidget = uic.loadUi(self.path + filename)

        # Initialize the settings dict
        self.s = self._get_settings_dict()

        # Initialize resource manager
        self.rm = pyvisa.ResourceManager("@py")

        # FIXME: DEBUG button
        debug_button = self.settingsWidget.findChild(QPushButton, "pushButton")
        debug_button.clicked.connect(self.debug_button)

        self._connect_signals()

        # Initialize the lock for the measurement
        self.lock = Lock()
        self.debug_mode = False

        assert self.settingsWidget is not None, "Settings widget not found"
        assert self.rm is not None, "Resource manager not found"

    ## Widget functions
    def debug_button(self):
        try:
            settings = self.parse_settings_widget()
            print(settings)
            print("--------------------------------")
        except Exception as e:
            print(f"Exception in debug_button: {e}")

        """        self.debug_mode = True
        self.connect()
        self.keithley_init(settings)
        print("--- channel initialized ---")
        print("busy: ", self.busy())
        data = self.KeithleyRunSingleChSweep(settings)
        print("data: ", data)
        self.disconnect()
        # print("--- Sweep done, i'm happy now ---")"""

        """        
        self.connect()
        if settings["single_ch"]:
            self.KeithleyInitSingleCh(settings, self.k)
        else:
            self.keithley_init_dual_ch(settings, self.k)
        self.disconnect()
        """

    def _get_settings_dict(self):
        """Generates a dict of the settings. Returned as lambda functions so that the latest values
        are always returned. Accessed by () on the value.

        Returns:
            dict: name of the widget -> lambda function to get the current value
        """
        checkboxes = self.settingsWidget.findChildren(QCheckBox)
        comboboxes = self.settingsWidget.findChildren(QComboBox)
        lineedits = self.settingsWidget.findChildren(QLineEdit)

        settings = {}

        # Extract the settings into a dict
        # Format: settings[objectName] = function to get current value
        for checkbox in checkboxes:
            settings[checkbox.objectName()] = lambda cb=checkbox: cb.isChecked()
        for combobox in comboboxes:
            settings[combobox.objectName()] = lambda cb=combobox: cb.currentText()
        for lineedit in lineedits:
            settings[lineedit.objectName()] = lambda le=lineedit: le.text()

        return settings

    def _connect_signals(self):
        # Connect the channel combobox
        mode_box = self.settingsWidget.findChild(QComboBox, "comboBox_mode")
        mode_box.activated.connect(self._mode_changed)
        # call mode changed to update to the correct mode
        self._mode_changed()

        # Connect the inject type combobox
        inject_box = self.settingsWidget.findChild(QComboBox, "comboBox_inject")
        inject_box.activated.connect(self._inject_changed)
        self._inject_changed()

        # Connect the drain follows source checkbox
        drain_follows_source = self.settingsWidget.findChild(
            QCheckBox, "checkBox_drainFollowSource"
        )
        source_highC = self.settingsWidget.findChild(QCheckBox, "checkBox_sourceHighC")
        source_sense_mode = self.settingsWidget.findChild(
            QComboBox, "comboBox_sourceSenseMode"
        )
        source_highC.stateChanged.connect(self._drain_follows_source_changed)
        source_sense_mode.activated.connect(self._drain_follows_source_changed)
        drain_follows_source.stateChanged.connect(self._drain_follows_source_changed)
        self._drain_follows_source_changed()

        # FIXME: This does not currently work, as QHBoxLayout cannot be shown or hidden as a group.
        """
        delay_continuous = self.settingsWidget.findChild(
            QComboBox, "comboBox_continuousDelayMode"
        )
        delay_pulsed = self.settingsWidget.findChild(
            QComboBox, "comboBox_pulsedDelayMode"
        )
        delay_drain = self.settingsWidget.findChild(
            QComboBox, "comboBox_drainDelayMode"
        )

        delay_continuous.activated.connect(self._delay_mode_changed)
        delay_pulsed.activated.connect(self._delay_mode_changed)
        delay_drain.activated.connect(self._delay_mode_changed)
        # call delay mode changed to update to the correct mode
        self._delay_mode_changed()
        """

    def _drain_follows_source_changed(self):
        if self.s["checkBox_drainFollowSource"]():
            drain_highC = self.settingsWidget.findChild(
                QCheckBox, "checkBox_drainHighC"
            )
            drain_sense_mode = self.settingsWidget.findChild(
                QComboBox, "comboBox_drainSenseMode"
            )
            drain_highC.setChecked(self.s["checkBox_sourceHighC"]())
            drain_sense_mode.setCurrentText(self.s["comboBox_sourceSenseMode"]())

    def _mode_changed(self):
        """Handles the visibility of the mode input fields based on the selected mode."""
        group_continuous = self.settingsWidget.findChild(
            QWidget, "groupBox_continuousSweep"
        )
        group_pulsed = self.settingsWidget.findChild(QWidget, "groupBox_pulsedSweep")

        mode = self.s["comboBox_mode"]()

        if mode == "Continuous":
            group_continuous.setVisible(True)
            group_pulsed.setVisible(False)
        elif mode == "Pulsed":
            group_continuous.setVisible(False)
            group_pulsed.setVisible(True)
        elif mode == "Mixed":
            group_continuous.setVisible(True)
            group_pulsed.setVisible(True)

        self.settingsWidget.update()

    def _inject_changed(self):
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

        inject_type = self.s["comboBox_inject"]()
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

    def _delay_mode_changed(self):
        """Handles the visibility of the delay input fields based on the selected mode."""
        continuous_input = self.settingsWidget.findChild(
            QHBoxLayout, "HBoxLayout_continuousDelay"
        )
        pulsed_input = self.settingsWidget.findChild(
            QHBoxLayout, "HBoxLayout_pulsedDelay"
        )
        drain_input = self.settingsWidget.findChild(
            QHBoxLayout, "HBoxLayout_drainDelay"
        )

        delay_continuous_mode = self.s.get("delay_continuous_mode", "")
        delay_pulsed_mode = self.s.get("delay_pulsed_mode", "")
        delay_drain_mode = self.s.get("delay_drain_mode", "")

        if delay_continuous_mode == "auto":
            continuous_input.setVisible(False)
        else:
            continuous_input.setVisible(True)

        if delay_pulsed_mode == "auto":
            pulsed_input.setVisible(False)
        else:
            pulsed_input.setVisible(True)

        if delay_drain_mode == "auto":
            drain_input.setVisible(False)
        else:
            drain_input.setVisible(True)

        self.settingsWidget.update()

    ## Communication functions
    def safewrite(self, command):
        try:
            self.k.write(command)
            if self.debug_mode:
                error_code = self.k.query("print(errorqueue.next())")
                if "Queue Is Empty" not in error_code:
                    print(f"Error sending command: {command}\nError code: {error_code}")
        except Exception as e:
            print(f"Exception sending command: {command}\nException: {e}")
        finally:
            self.k.write("errorqueue.clear()")

    def connect(self) -> bool:
        """Connect to the Keithley 2612B.

        Returns:
            bool: connection succesful or nah
        """
        try:
            print("Connecting to Keithley 2612B")
            self.k = self.rm.open_resource(pyIVLS_constants.KEITHLEY_VISA)
            print(self.k.query("*IDN?"))
            self.k.read_termination = "\n"
            return True
        except:
            print("Failed to connect to Keithley 2612B")
            return False

    def disconnect(self):
        print("Disconnecting from Keithley 2612B")
        if self.k is not None:
            self.k.close()

    ## Device functions
    def busy(self) -> bool:
        """Try to acquire the lock. If the lock can be captured, the instrument is not busy.
        If acquired, release the lock and return False.
        If not acquired, return True.

        Returns:
            bool: device busy status
        """
        gotten = self.lock.acquire(blocking=False)
        if gotten:
            self.lock.release()

        return not gotten

    def resistance_measurement(self, channel) -> float:
        """Measure the resistance at the probe.

        Returns:
            float: resistance
        """
        if channel == "smua" or channel == "smub":
            # Restore Series 2600B defaults.
            self.safewrite(f"{channel}.reset()")
            # Select current source function.
            self.safewrite(f"{channel}.source.func = {channel}.OUTPUT_DCAMPS")
            # Set source range to 10 mA.
            self.safewrite(f"{channel}.source.rangei = 10e-3")
            # Set current source to 10 mA.
            self.safewrite(f"{channel}.source.leveli = 10e-3")
            # Set voltage limit to 10 V. FIXME: Value of 1 v is arbitrary.
            self.safewrite(f"{channel}.source.limitv = 1")
            # Enable 4-wire ohms.
            self.safewrite(f"{channel}.sense = {channel}.SENSE_REMOTE")
            # Set voltage range to auto.
            self.safewrite(f"{channel}.measure.autorangev = {channel}.AUTORANGE_ON")
            # Turn on output.
            self.safewrite(f"{channel}.source.output = {channel}.OUTPUT_ON")
            # Get resistance reading.
            resistance = float(self.k.query_ascii_values(f"{channel}.measure.r()"))
            # Turn off output.
            self.safewrite(f"{channel}.source.output = {channel}.OUTPUT_OFF")
            return resistance
        else:
            raise ValueError(f"Invalid channel {channel}")

    def read_buffer(self, channel, buffer_number, start, end) -> np.ndarray:
        raise NotImplementedError("This function is not implemented yet.")

    def parse_settings_widget(self) -> list[dict]:
        """Parses the settings widget and extracts a dict of settings. If the settings are invalid, an AssertionError is raised.
        Provides multiple dicts if necessary for 2+4 wire mode and mixed mode.

        Returns:
            list[dict]: A list of settings dictionaries.
        """

        legacy_dict = {}
        mixed_mode_flag = False
        double_sense_mode_flag = False
        ret_list = []

        # Determine source channel
        legacy_dict["source"] = (
            "smua" if self.s["comboBox_channel"]() == "smuA" else "smub"
        )

        # Determine source type
        inject_type = self.s["comboBox_inject"]()
        legacy_dict["type"] = "v" if inject_type == "Voltage" else "i"

        # Determine repeat count
        legacy_dict["repeat"] = int(self.s["lineEdit_repeat"]())

        # Set single channel and drain
        legacy_dict["single_ch"] = self.s["checkBox_singleChannel"]()
        legacy_dict["highC"] = self.s["checkBox_sourceHighC"]()
        if not legacy_dict["single_ch"]:
            legacy_dict["drain"] = "smub" if legacy_dict["source"] == "smua" else "smua"

            # FIXME: Check what the data should contain, the old code expects to have standard value "off" for drainVoltage.
            # FIXME: Add drain delay mode reading.
            legacy_dict["highC_drain"] = self.s["checkBox_drainHighC"]()
            legacy_dict["drainVoltage"] = self.s["lineEdit_drainStart"]()
            legacy_dict["drainLimit"] = self.s["lineEdit_drainLimit"]()
            legacy_dict["nplc_drain"] = float(
                float(self.s["lineEdit_drainNPLC"]())
                * 0.001
                * pyIVLS_constants.LINE_FREQ
            )
            if self.s["comboBox_drainDelayMode"]() == "Auto":
                legacy_dict["delay_drain"] = "off"
            else:
                legacy_dict["delay_drain"] = self.s["lineEdit_drainDelay"]()

        # Set sense mode
        source_sense_mode = self.s["comboBox_sourceSenseMode"]()
        if source_sense_mode == "2 wire":
            legacy_dict["sense"] = False
        elif source_sense_mode == "4 wire":
            legacy_dict["sense"] = True
        else:
            double_sense_mode_flag = True

        # set pulse mode
        if self.s["comboBox_mode"]() == "Continuous":
            legacy_dict["pulse"] = "off"
        elif self.s["comboBox_mode"]() == "Pulsed":
            legacy_dict["pulse"] = self.s["lineEdit_pulsedPause"]()
        else:
            mixed_mode_flag = True

        # If 2+4wire mode, create two dicts, one for each mode
        if double_sense_mode_flag:
            legacy_dict["sense"] = False
            ret_list.append(legacy_dict.copy())
            legacy_dict["sense"] = True
            ret_list.append(legacy_dict)
        else:
            ret_list.append(legacy_dict)

        # Set the pulse mode in mixed mode for all dicts:
        # NOTE: iterating over a copy of the list to avoid an infinite loop.
        for legacy_dict in ret_list[:]:
            if mixed_mode_flag:
                legacy_dict["pulse"] = self.s["lineEdit_pulsedPause"]()
                dict_copy = legacy_dict.copy()
                dict_copy["pulse"] = "off"
                ret_list.append(dict_copy)

        return self._read_and_validate_settings(ret_list)

    def _read_and_validate_settings(self, settings: list[dict]) -> list[dict]:
        """Reads start, end, limit, steps, nplc and delay settings from the GUI and validates them.
        This method is for internal use only

        Args:
            settings (list[dict]): A list of settings dictrionaries.

        Returns:
            list[dict]: A list of validated settings dictionaries.
        """
        # if in pulse mode, read the settings from the pulsed sweep group
        for legacy_dict in settings:
            if legacy_dict["pulse"] != "off":
                legacy_dict["start"] = float(self.s["lineEdit_pulsedStart"]())
                legacy_dict["end"] = float(self.s["lineEdit_pulsedEnd"]())
                legacy_dict["steps"] = int(self.s["lineEdit_pulsedPoints"]())
                legacy_dict["limit"] = float(self.s["lineEdit_pulsedLimit"]())
                legacy_dict["nplc"] = float(
                    float(self.s["lineEdit_pulsedNPLC"]())
                    * 0.001
                    * pyIVLS_constants.LINE_FREQ
                )

                if self.s["comboBox_pulsedDelayMode"]() == "Auto":
                    legacy_dict["delay"] = "off"
                else:
                    legacy_dict["delay"] = self.s["lineEdit_pulsedDelay"]()
            # else must be in continous mode, read the settings from the continuous sweep group
            else:
                legacy_dict["start"] = float(self.s["lineEdit_continuousStart"]())
                legacy_dict["end"] = float(self.s["lineEdit_continuousEnd"]())
                legacy_dict["steps"] = int(self.s["lineEdit_continuousPoints"]())
                legacy_dict["limit"] = float(self.s["lineEdit_continuousLimit"]())
                legacy_dict["nplc"] = float(
                    float(self.s["lineEdit_continuousNPLC"]())
                    * 0.001
                    * pyIVLS_constants.LINE_FREQ
                )
                if self.s["comboBox_continuousDelayMode"]() == "Auto":
                    legacy_dict["delay"] = "off"
                else:
                    legacy_dict["delay"] = self.s["lineEdit_continuousDelay"]()

            # Make assertions
            assert legacy_dict["steps"] > 0, "Steps have to be greater than 0"
            assert legacy_dict["repeat"] > 0, "Repeat count has to be greater than 0"
            assert (
                legacy_dict["nplc"] >= 0.001 and legacy_dict["nplc"] <= 25
            ), "NPLC value out of range"
            assert legacy_dict["delay"] == "off" or (
                float(legacy_dict["delay"]) >= 0.0001
                and float(legacy_dict["delay"]) <= 999.9999
            ), "Delay value out of range"
            if not legacy_dict["single_ch"]:
                assert (
                    legacy_dict["nplc_drain"] >= 0.001
                    and legacy_dict["nplc_drain"] <= 25
                ), "NPLC value out of range"
                assert legacy_dict["delay_drain"] == "off" or (
                    float(legacy_dict["delay_drain"]) >= 0.0001
                    and float(legacy_dict["delay_drain"]) <= 999.9999
                ), "Delay for drain value out of range"

        return settings

    def keithley_init(self, s: dict):
        """Initialize Keithley SMU for single or dual channel operation.

        Args:
            s (dict): Configuration dictionary.
        """

        self.safewrite("reset()")
        self.safewrite("beeper.enable=0")
        self.safewrite(f"{s['source']}.reset()")
        if not s["single_ch"]:
            self.safewrite(f"{s['drain']}.reset()")

        if s["sense"]:
            self.safewrite(f"{s['source']}.sense = {s['source']}.SENSE_REMOTE")
        else:
            self.safewrite(f"{s['source']}.sense = {s['source']}.SENSE_LOCAL")

        if not s["single_ch"]:
            if s["sense_drain"] and s["sense"]:
                self.safewrite(f"{s['drain']}.sense = {s['drain']}.SENSE_REMOTE")
            else:
                self.safewrite(f"{s['drain']}.sense = {s['drain']}.SENSE_LOCAL")
        # Set filter for source
        self.safewrite(f"{s['source']}.measure.filter.count = 4")
        self.safewrite(f"{s['source']}.measure.filter.enable = {s['source']}.FILTER_ON")
        self.safewrite(
            f"{s['source']}.measure.filter.type = {s['source']}.FILTER_REPEAT_AVG"
        )
        # set autoranges on for source
        self.safewrite(f"{s['source']}.measure.autorangei = {s['source']}.AUTORANGE_ON")
        self.safewrite(f"{s['source']}.measure.autorangev = {s['source']}.AUTORANGE_ON")

        if not s["single_ch"]:
            # If dual channel, set filter and autoranges for drain
            self.safewrite(f"{s['drain']}.measure.filter.count = 4")
            self.safewrite(
                f"{s['drain']}.measure.filter.enable = {s['drain']}.FILTER_ON"
            )
            self.safewrite(
                f"{s['drain']}.measure.filter.type = {s['drain']}.FILTER_REPEAT_AVG"
            )
            self.safewrite(
                f"{s['drain']}.measure.autorangei = {s['drain']}.AUTORANGE_ON"
            )
            self.safewrite(
                f"{s['drain']}.measure.autorangev = {s['drain']}.AUTORANGE_ON"
            )
        # If pulse is off, set to continuous. FIXME: Should this be set on the drain as well?
        # HACK: This whole thing is copied from the old code. Hopefully no problems.
        if s["pulse"] == "off":
            self.safewrite(
                f"{s['source']}.trigger.endpulse.action = {s['source']}.SOURCE_HOLD"
            )
        else:
            self.safewrite(
                f"{s['source']}.trigger.endpulse.action = {s['source']}.SOURCE_IDLE"
            )
            self.safewrite(f"trigger.timer[1].delay = {s['pulse']}")
            self.safewrite("trigger.timer[1].passthrough = false")
            self.safewrite("trigger.timer[1].count = 1")
            self.safewrite("trigger.blender[1].orenable = true")
            self.safewrite(
                f"trigger.blender[1].stimulus[1] = {s['source']}.trigger.SWEEPING_EVENT_ID"
            )
            self.safewrite(
                f"trigger.blender[1].stimulus[2] = {s['source']}.trigger.PULSE_COMPLETE_EVENT_ID"
            )
            self.safewrite("trigger.timer[1].stimulus = trigger.blender[1].EVENT_ID")
            self.safewrite(
                f"{s['source']}.trigger.source.stimulus = trigger.timer[1].EVENT_ID"
            )

        self.safewrite(
            f"{s['source']}.source.settling = {s['source']}.SETTLE_FAST_RANGE"
        )
        self.safewrite("display.screen = display.SMUA_SMUB")
        self.safewrite("format.data = format.ASCII")

        if s["delay"] == "off":
            self.safewrite(f"{s['source']}.measure.delay = {s['source']}.DELAY_AUTO")
            if s["pulse"] == "off":
                self.safewrite(f"{s['source']}.measure.delayfactor = 28.0")
            else:
                self.safewrite(f"{s['source']}.measure.delayfactor = 1.0")
        else:
            self.safewrite(f"{s['source']}.measure.delay = {s['delay']}")

        self.safewrite(
            f"{s['source']}.trigger.measure.iv({s['source']}.nvbuffer1, {s['source']}.nvbuffer2)"
        )
        self.safewrite(f"{s['source']}.trigger.measure.action = {s['source']}.ENABLE")
        self.safewrite(f"{s['source']}.trigger.source.action = {s['source']}.ENABLE")
        self.safewrite(f"{s['source']}.measure.nplc = {s['nplc']}")
        self.safewrite(
            f"{s['source']}.trigger.endsweep.action = {s['source']}.SOURCE_IDLE"
        )
        self.safewrite(
            f"{s['source']}.trigger.measure.stimulus = {s['source']}.trigger.SOURCE_COMPLETE_EVENT_ID"
        )
        self.safewrite(
            f"{s['source']}.trigger.endpulse.stimulus = {s['source']}.trigger.MEASURE_COMPLETE_EVENT_ID"
        )

        if not s["single_ch"]:
            self.safewrite(
                f"{s['drain']}.trigger.measure.iv({s['drain']}.nvbuffer1, {s['drain']}.nvbuffer2)"
            )
            self.safewrite(f"{s['drain']}.trigger.measure.action = {s['drain']}.ENABLE")
            self.safewrite(f"{s['drain']}.trigger.source.action = {s['drain']}.DISABLE")
            self.safewrite(f"{s['drain']}.measure.nplc = {s['nplc']}")
            self.safewrite(
                f"{s['drain']}.trigger.measure.stimulus = {s['source']}.trigger.SOURCE_COMPLETE_EVENT_ID"
            )
            self.safewrite("trigger.blender[2].orenable = false")
            self.safewrite(
                f"trigger.blender[2].stimulus[1] = {s['source']}.trigger.MEASURE_COMPLETE_EVENT_ID"
            )
            self.safewrite(
                f"trigger.blender[2].stimulus[2] = {s['drain']}.trigger.MEASURE_COMPLETE_EVENT_ID"
            )
            self.safewrite(
                f"{s['source']}.trigger.endpulse.stimulus = trigger.blender[2].EVENT_ID"
            )

        # FIXME: Should highC be the same for both channels?
        if s["highC"]:
            self.safewrite(f"{s['source']}.source.highc = {s['source']}.ENABLE")
            if not s["single_ch"] and s["highC"]:
                self.safewrite(f"{s['drain']}.source.highc = {s['drain']}.ENABLE")

    def keithley_run_single_ch_sweep(self, s: dict) -> np.ndarray:
        """Runs a single channel sweep on. Handles locking the instrument and releasing it after the sweep is done.
        This method sets the start, end, steps, type of injection and the limit.

        Args:
            s (dict): settings dictionary

        Returns:
            list(or np.ndarray): I-V data
        """
        # Try and acquire the lock to make sure nothing else is running
        with self.lock:
            try:
                print("Measurement started")
                readsteps = s["steps"]
                waitDelay = float(s["pulse"]) if s["pulse"] != "off" else 1

                # Clear buffers, set repeats and steps, set sweep range.
                self.safewrite(f"{s['source']}.nvbuffer1.clear()")
                self.safewrite(f"{s['source']}.nvbuffer2.clear()")
                self.safewrite(f"{s['source']}.trigger.count = {s['steps']}")
                self.safewrite(f"{s['source']}.trigger.arm.count = {s['repeat']}")
                self.safewrite(
                    f"{s['source']}.trigger.source.linear{s['type']}({s['start']},{s['end']},{s['steps']})"
                )
                # if current injection
                if s["type"] == "i":
                    if abs(s["start"]) < 1.5 and abs(s["end"]) < 1.5:
                        # if the sweep maximum is under 1.5 A, set the limit from the GUI.
                        self.safewrite(
                            f"{s['source']}.trigger.source.limitv = {s['limit']}"
                        )
                        self.safewrite(f"{s['source']}.source.limitv = {s['limit']}")
                    else:
                        # If the sweep maximum is over 1.5 A:
                        # HACK: do some stuff, this is from the old code.
                        self.safewrite(
                            f"{s['source']}.measure.filter.enable = {s['source']}.FILTER_OFF"
                        )
                        self.safewrite(
                            f"{s['source']}.source.autorangei = {s['source']}.AUTORANGE_OFF"
                        )
                        self.safewrite(
                            f"{s['source']}.source.autorangev = {s['source']}.AUTORANGE_OFF"
                        )
                        self.safewrite(f"{s['source']}.source.delay = 100e-6")
                        self.safewrite(
                            f"{s['source']}.measure.autozero = {s['source']}.AUTOZERO_OFF"
                        )
                        self.safewrite(f"{s['source']}.source.rangei = 10")
                        self.safewrite(f"{s['source']}.source.leveli = 0")
                        self.safewrite(f"{s['source']}.source.limitv = 6")
                        self.safewrite(f"{s['source']}.trigger.source.limiti = 10")
                    self.safewrite(
                        f"display.{s['source']}.measure.func = display.MEASURE_DCVOLTS"
                    )
                # if voltage injection
                else:
                    if abs(s["limit"]) < 1.5:
                        # if the current limit is under 1.5 A, set the limit from the GUI.
                        self.safewrite(
                            f"{s['source']}.trigger.source.limiti = {s['limit']}"
                        )
                        self.safewrite(f"{s['source']}.source.limiti = {s['limit']}")
                    else:
                        # If the current limit is over 1.5 A:
                        # HACK: Do some stuff, this is from the old code.
                        self.safewrite(
                            f"{s['source']}.measure.filter.enable = {s['source']}.FILTER_OFF"
                        )
                        self.safewrite(
                            f"{s['source']}.source.autorangei = {s['source']}.AUTORANGE_OFF"
                        )
                        self.safewrite(
                            f"{s['source']}.source.autorangev = {s['source']}.AUTORANGE_OFF"
                        )
                        self.safewrite(f"{s['source']}.measure.rangei = 10")
                        self.safewrite(f"{s['source']}.source.delay = 100e-6")
                        self.safewrite(
                            f"{s['source']}.measure.autozero = {s['source']}.AUTOZERO_OFF"
                        )
                        self.safewrite(f"{s['source']}.source.rangev = 6")
                        self.safewrite(f"{s['source']}.source.levelv = 0")
                        self.safewrite(f"{s['source']}.source.limiti = {s['limit']}")
                        self.safewrite(
                            f"{s['source']}.trigger.source.limiti = {s['limit']}"
                        )
                    self.safewrite(
                        f"display.{s['source']}.measure.func = display.MEASURE_DCAMPS"
                    )
                # Turn on the source and trigger the sweep.
                self.safewrite(f"{s['source']}.source.output = {s['source']}.OUTPUT_ON")
                self.safewrite(f"{s['source']}.trigger.initiate()")
                time.sleep(waitDelay)

                # Read the buffer until the sweep is done.
                # FIXME: This should probably be encapsulated in a separate function
                buffer_prev = 0
                iv = np.array([])
                while True:
                    if not self.busy():
                        # From the old code, this aborts if the scan has not properly started.
                        print("Not busy, aborting")
                        self.safewrite(f"{s['source']}.abort()")
                        self.safewrite(
                            f"{s['source']}.source.output = {s['source']}.OUTPUT_OFF"
                        )
                        return iv

                    # Get the number of readings in nvbuffer2
                    readings = self.k.query_ascii_values(
                        f"print({s['source']}.nvbuffer2.n)"
                    )
                    buffern = int(readings[0])

                    # If there are enough readings to cover the whole sweep, break
                    if buffern >= s["steps"] * s["repeat"]:
                        break

                    if buffern > buffer_prev:
                        # Read current (nvbuffer1) and voltage (nvbuffer2)

                        i_values = self.k.query_ascii_values(
                            f"printbuffer({buffer_prev + 1}, {buffern}, {s['source']}.nvbuffer1)"
                        )
                        v_values = self.k.query_ascii_values(
                            f"printbuffer({buffer_prev + 1}, {buffern}, {s['source']}.nvbuffer2)"
                        )

                        # Add to the iv array
                        iv.extend(list(zip(v_values, i_values)))

                        # Check for limit condition
                        if (
                            s["type"] == "i"
                            and any(abs(v) > 0.95 * abs(s["limit"]) for v in v_values)
                        ) or (
                            s["type"] == "v"
                            and any(abs(i) > 0.95 * abs(s["limit"]) for i in i_values)
                        ):
                            # kill if limits exceeded
                            self.safewrite(f"{s['source']}.abort()")
                            readsteps = buffern
                            break

                        # Update buffer_prev
                        buffer_prev = buffern

                    time.sleep(0.5)

                time.sleep(waitDelay * 1.2)
                self.safewrite(
                    f"{s['source']}.source.output = {s['source']}.OUTPUT_OFF"
                )

                # Final buffer read to ensure all data is captured
                # FIXME: absolutely something wrong with this :DDDDD
                if buffer_prev > 0:
                    iv = np.array(iv)
                    readsteps = buffer_prev

                    iv[:, 1] = self.k.query_ascii_values(
                        f"printbuffer(1, {readsteps}, {s['source']}.nvbuffer1)"
                    )
                    iv[:, 0] = self.k.query_ascii_values(
                        f"printbuffer(1, {readsteps}, {s['source']}.nvbuffer2)"
                    )

                return iv
            except:
                # if something fails, abort the measurement and turn off the source. return whatever has been collected so far.
                self.safewrite(
                    f"{s['source']}.source.output = {s['source']}.OUTPUT_OFF"
                )
                self.safewrite(f"{s['source']}.abort()")
                return iv

    def KeithleyRunDualChSweep(self, s: dict):
        with self.lock:
            try:
                readsteps = s["steps"]
                waitDelay = float(s["pulse"]) if s["pulse"] != "off" else 1

                self.safewrite(f"{s['source']}.nvbuffer1.clear()")
                self.safewrite(f"{s['source']}.nvbuffer2.clear()")
                self.safewrite(f"{s['drain']}.nvbuffer1.clear()")
                self.safewrite(f"{s['drain']}.nvbuffer2.clear()")
                self.safewrite(f"{s['source']}.trigger.count = {s['steps']}")
                self.safewrite(f"{s['source']}.trigger.arm.count = {s['repeat']}")
                self.safewrite(f"{s['drain']}.trigger.count = {s['steps']}")
                self.safewrite(f"{s['drain']}.trigger.arm.count = {s['repeat']}")
                self.safewrite(
                    f"display.{s['drain']}.measure.func = display.MEASURE_DCAMPS"
                )
                self.safewrite(
                    f"{s['source']}.trigger.source.linear{s['type']}({s['start']},{s['end']},{s['steps']})"
                )

                if s["type"] == "i":
                    if s["pulse"] == "off" or (
                        abs(s["start"]) < 1.5 and abs(s["end"]) < 1.5
                    ):
                        self.safewrite(
                            f"{s['source']}.trigger.source.limitv = {s['limit']}"
                        )
                        self.safewrite(f"{s['source']}.source.limitv = {s['limit']}")
                    else:
                        self.safewrite("smua.measure.filter.enable = smua.FILTER_OFF")
                        self.safewrite("smub.measure.filter.enable = smub.FILTER_OFF")
                        self.safewrite(
                            f"{s['source']}.source.autorangei = {s['source']}.AUTORANGE_OFF"
                        )
                        self.safewrite(
                            f"{s['source']}.source.autorangev = {s['source']}.AUTORANGE_OFF"
                        )
                        self.safewrite(
                            f"{s['drain']}.source.autorangei = {s['drain']}.AUTORANGE_OFF"
                        )
                        self.safewrite(
                            f"{s['drain']}.source.autorangev = {s['drain']}.AUTORANGE_OFF"
                        )
                        self.safewrite(f"{s['source']}.measure.rangei = 10")
                        self.safewrite(f"{s['drain']}.measure.rangei = 10")
                        self.safewrite(f"{s['source']}.source.delay = 100e-6")
                        self.safewrite(
                            f"{s['source']}.measure.autozero = {s['source']}.AUTOZERO_OFF"
                        )
                        self.safewrite(f"{s['source']}.source.rangei = 10")
                        self.safewrite(f"{s['source']}.source.leveli = 0")
                        self.safewrite(f"{s['source']}.source.limitv = 6")
                        self.safewrite(f"{s['source']}.trigger.source.limiti = 10")
                    self.safewrite(
                        f"display.{s['source']}.measure.func = display.MEASURE_DCVOLTS"
                    )
                else:
                    if s["pulse"] == "off" or abs(s["limit"]) < 1.5:
                        self.safewrite(
                            f"{s['source']}.trigger.source.limiti = {s['limit']}"
                        )
                        self.safewrite(f"{s['source']}.source.limiti = {s['limit']}")
                    else:
                        self.safewrite("smua.measure.filter.enable = smua.FILTER_OFF")
                        self.safewrite("smub.measure.filter.enable = smub.FILTER_OFF")
                        self.safewrite(
                            f"{s['source']}.source.autorangei = {s['source']}.AUTORANGE_OFF"
                        )
                        self.safewrite(
                            f"{s['source']}.source.autorangev = {s['source']}.AUTORANGE_OFF"
                        )
                        self.safewrite(
                            f"{s['drain']}.source.autorangei = {s['drain']}.AUTORANGE_OFF"
                        )
                        self.safewrite(
                            f"{s['drain']}.source.autorangev = {s['drain']}.AUTORANGE_OFF"
                        )
                        self.safewrite(f"{s['source']}.measure.rangei = 10")
                        self.safewrite(f"{s['drain']}.measure.rangei = 10")
                        self.safewrite(f"{s['source']}.source.delay = 100e-6")
                        self.safewrite(
                            f"{s['source']}.measure.autozero = {s['source']}.AUTOZERO_OFF"
                        )
                        self.safewrite(f"{s['source']}.source.rangev = 6")
                        self.safewrite(f"{s['source']}.source.levelv = 0")
                        self.safewrite(f"{s['source']}.source.limiti = 0.1")
                        self.safewrite(f"{s['source']}.trigger.source.limiti = 10")
                    self.safewrite(
                        f"display.{s['source']}.measure.func = display.MEASURE_DCAMPS"
                    )
                # FIXME: check the what value is read into this value
                if s["drainVoltage"] != "off":
                    self.safewrite(
                        f"{s['drain']}.source.func = {s['drain']}.OUTPUT_DCVOLTS"
                    )
                    self.safewrite(f"{s['drain']}.source.levelv = {s['drainVoltage']}")
                    self.safewrite(f"{s['drain']}.source.limiti = {s['drainLimit']}")
                    drainLimitVoltage = float(s["drainLimit"])
                else:
                    self.safewrite(
                        f"{s['drain']}.source.func = {s['drain']}.OUTPUT_DCVOLTS"
                    )
                    self.safewrite(f"{s['drain']}.source.levelv = 0")
                    if s["type"] == "v" and s["limit"] > 1.5:
                        self.safewrite(f"{s['drain']}.source.limiti = 1.5")
                        drainLimitVoltage = 1.5
                    else:
                        self.safewrite(f"{s['drain']}.source.limiti = {s['limit']}")
                        drainLimitVoltage = s["limit"]
                    if s["type"] == "i":
                        self.safewrite(f"{s['drain']}.source.limiti = {s['end']}")
                        drainLimitVoltage = s["end"]

                self.safewrite(f"{s['source']}.source.output = {s['source']}.OUTPUT_ON")
                self.safewrite(f"{s['drain']}.source.output = {s['drain']}.OUTPUT_ON")
                self.safewrite(f"{s['drain']}.trigger.initiate()")
                self.safewrite(f"{s['source']}.trigger.initiate()")
                time.sleep(waitDelay)

                # Buffer reading starts here.
                buffer_prev = 0
                iv = np.array([])

                while True:
                    if not self.busy():
                        self.safewrite(f'{s["source"]}.abort()')
                        self.safewrite(f'{s["drain"]}.abort()')
                        iv = []
                        time.sleep(0.5)
                        self.safewrite(
                            f'{s["source"]}.source.output = {s["source"]}.OUTPUT_OFF'
                        )
                        self.safewrite(
                            f'{s["drain"]}.source.output = {s["drain"]}.OUTPUT_OFF'
                        )
                        break

                    # Get the number of readings in nvbuffer2
                    readings = self.k.query_ascii_values(
                        f"print({s['source']}.nvbuffer2.n)"
                    )
                    buffern = int(readings[0])

                    if buffern >= s["steps"] * s["repeat"]:
                        break

                    if buffern > buffer_prev:
                        # Read currents (nvbuffer1) and voltages (nvbuffer2)

                        i_values_source = self.k.query_ascii_values(
                            f"printbuffer({buffer_prev + 1}, {buffern}, {s['source']}.nvbuffer1)"
                        )
                        v_values_source = self.k.query_ascii_values(
                            f"printbuffer({buffer_prev + 1}, {buffern}, {s['source']}.nvbuffer2)"
                        )
                        i_values_drain = self.k.query_ascii_values(
                            f"printbuffer({buffer_prev + 1}, {buffern}, {s['drain']}.nvbuffer1)"
                        )
                        v_values_drain = self.k.query_ascii_values(
                            f"printbuffer({buffer_prev + 1}, {buffern}, {s['drain']}.nvbuffer2)"
                        )

                        buffer_prev = buffern
                    time.sleep(0.5)

                time.sleep(waitDelay * 1.2)
                # Loop over, stop outputs.
                self.safewrite(
                    f"{s['source']}.source.output = {s['source']}.OUTPUT_OFF"
                )
                self.safewrite(f"{s['drain']}.source.output = {s['drain']}.OUTPUT_OFF")

            except:
                # if something fails, abort the measurement and turn off the source. return whatever has been collected so far.
                self.safewrite(
                    f"{s['source']}.source.output = {s['source']}.OUTPUT_OFF"
                )
                self.safewrite(f"{s['drain']}.source.output = {s['drain']}.OUTPUT_OFF")
                self.safewrite(f"{s['source']}.abort()")
                self.safewrite(f"{s['drain']}.abort()")

                return iv
