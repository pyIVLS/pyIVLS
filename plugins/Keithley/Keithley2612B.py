import sys
import os
import time
from threading import Lock


from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QCheckBox, QComboBox, QLineEdit, QPushButton
from PyQt6.QtCore import QObject

import pyvisa
from keithley2600 import Keithley2600

"""
My notes:
Keithely2600 can handle voltage sweeps, but the following parameters need to be set separately:
-high c
-sense 
-limits for curr
-pulse pause
-repeat
-current injection instead of voltage
"""


class Keithley2612B(QObject):

    ####################################  threads

    ################################### internal functions

    ########Slots

    ########Signals

    ########Functions
    def __init__(self):

        QObject.__init__(self)
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        filename = (
            os.path.splitext(os.path.basename(__file__))[0] + "_settingsWidget.ui"
        )
        self.settingsWidget = uic.loadUi(self.path + filename)

        # Extract settings from settingsWidget
        self.s = self._get_settings_dict()

        self.PLACEHOLDER = "Enter VISA address"

        # Initialize the measurement lock

        # FIXME: DEBUG
        debug_button = self.settingsWidget.findChild(QPushButton, "pushButton")
        debug_button.clicked.connect(self.parse_settings_widget)

    def _get_settings_dict(self):
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

    def connect(self):
        print("Connecting to Keithley 2612B")
        self.k = Keithley2600(self.PLACEHOLDER)

    def disconnect(self):
        print("Disconnecting from Keithley 2612B")
        self.k.disconnect()

    def busy(self) -> bool:
        if self.k is not None:
            return self.k.busy
        else:
            return False

    def parse_settings_widget(self) -> dict:
        """Parse the settings widget into a form that the legacy code can understand.

        Returns:
            dict: Parsed settings.
        """
        legacy_dict = {}

        # Determine source type
        inject_type = self.s["comboBox_inject"]()
        print("Voltage source" if inject_type == "voltage" else "Current source")

        # Determine source channel
        legacy_dict["source"] = (
            "smua" if self.s["comboBox_channel"]() == "smuA" else "smub"
        )

        # Set single channel and drain
        legacy_dict["single_ch"] = self.s["checkBox_singleChannel"]()
        if not legacy_dict["single_ch"]:
            legacy_dict["drain"] = "smub" if legacy_dict["source"] == "smua" else "smua"

        # Set source sense mode
        source_sense_mode = self.s["comboBox_sourceSenseMode"]()
        if source_sense_mode == "2 wire":
            legacy_dict["sense"] = False
        elif source_sense_mode == "4 wire":
            legacy_dict["sense"] = True
        else:
            legacy_dict["sense"] = False
            print("sense mode set to both, but currently not implemented.")

        # Set drain sense mode
        drain_sense_mode = self.s["comboBox_drainSenseMode"]()
        if drain_sense_mode == "2 wire":
            legacy_dict["sense_drain"] = False
        elif drain_sense_mode == "4 wire":
            legacy_dict["sense_drain"] = True
        else:
            legacy_dict["sense_drain"] = False
            print("sense mode set to both, but currently not implemented.")

        # set nplc
        legacy_dict["nplc"] = self.s["lineEdit_nplc"]()

        return legacy_dict

    def init_channel(self, s: dict):
        """Combines the functionality of init_sigle_channel and init_dual_channel into one function.
        % % % Keithley.delay %%str "off"/time in sec before measurement
        % % % Keithley.pulse %%str "off"/time in sec pause between pulses
        % % % Keithley.source %%str "smua"/"smub"
        % % % Keithley.drain %%str "smua"/"smub"
        % % % Keithley.nplc %% str
        % % % Keithley.sense %% true/false
        % % % Keithley.sense_drain %% true/false
        % % % Keithley.single_ch %% true/false

        Args:
            s (dict): dict of settings. See above.
            dev (_type_): pyvisa device instance
        """
        self.k._write("reset()")
        self.k._write("beeper.enable=0")
        self.k._write(f"{s['source']}.reset()")

        if "drain" in s:
            self.k._write(f"{s['drain']}.reset()")

        if s["sense"]:
            self.k._write(f"{s['source']}.sense = {s['source']}.SENSE_REMOTE")
        else:
            self.k._write(f"{s['source']}.sense = {s['source']}.SENSE_LOCAL")

        if not s["single_ch"]:
            if s["sense_drain"] and s["sense"]:
                self.k._write(f"{s['drain']}.sense = {s['drain']}.SENSE_REMOTE")
            else:
                self.k._write(f"{s['drain']}.sense = {s['drain']}.SENSE_LOCAL")

        # Common settings
        self.k._write(f"{s['source']}.measure.filter.count = 4")
        self.k._write(f"{s['source']}.measure.filter.enable = {s['source']}.FILTER_ON")
        self.k._write(
            f"{s['source']}.measure.filter.type = {s['source']}.FILTER_REPEAT_AVG"
        )
        self.k._write(f"{s['source']}.measure.autorangei = {s['source']}.AUTORANGE_ON")
        self.k._write(f"{s['source']}.measure.autorangev = {s['source']}.AUTORANGE_ON")

        if not s["single_ch"]:
            self.k._write("smua.measure.filter.count = 4")
            self.k._write("smub.measure.filter.count = 4")
            self.k._write("smua.measure.filter.enable = smua.FILTER_ON")
            self.k._write("smub.measure.filter.enable = smub.FILTER_ON")
            self.k._write("smua.measure.filter.type = smua.FILTER_REPEAT_AVG")
            self.k._write("smub.measure.filter.type = smub.FILTER_REPEAT_AVG")
            self.k._write(
                f"{s['drain']}.measure.autorangei = {s['drain']}.AUTORANGE_ON"
            )
            self.k._write(
                f"{s['drain']}.measure.autorangev = {s['drain']}.AUTORANGE_ON"
            )

        if s["pulse"] == "off":
            self.k._write(
                f"{s['source']}.trigger.endpulse.action = {s['source']}.SOURCE_HOLD"
            )
        else:
            self.k._write(
                f"{s['source']}.trigger.endpulse.action = {s['source']}.SOURCE_IDLE"
            )
            self.k._write(f"trigger.timer[1].delay = {s['pulse']}")
            self.k._write("trigger.timer[1].passthrough = false")
            self.k._write("trigger.timer[1].count = 1")
            self.k._write("trigger.blender[1].orenable = true")
            self.k._write(
                f"trigger.blender[1].stimulus[1] = {s['source']}.trigger.SWEEPING_EVENT_ID"
            )
            self.k._write(
                f"trigger.blender[1].stimulus[2] = {s['source']}.trigger.PULSE_COMPLETE_EVENT_ID"
            )
            self.k._write("trigger.timer[1].stimulus = trigger.blender[1].EVENT_ID")
            self.k._write(
                f"{s['source']}.trigger.source.stimulus = trigger.timer[1].EVENT_ID"
            )

        self.k._write(
            f"{s['source']}.source.settling = {s['source']}.SETTLE_FAST_RANGE"
        )
        self.k._write("display.screen = display.SMUA_SMUB")
        self.k._write("format.data = format.ASCII")

        if s["delay"] == "off":
            self.k._write(f"{s['source']}.measure.delay = {s['source']}.DELAY_AUTO")
            if s["pulse"] == "off":
                self.k._write(f"{s['source']}.measure.delayfactor = 28.0")
            else:
                self.k._write(f"{s['source']}.measure.delayfactor = 1.0")
        else:
            self.k._write(f"{s['source']}.measure.delay = {s['delay']}")

        self.k._write(
            f"{s['source']}.trigger.measure.iv({s['source']}.nvbuffer1, {s['source']}.nvbuffer2)"
        )
        self.k._write(f"{s['source']}.trigger.measure.action = {s['source']}.ENABLE")
        self.k._write(f"{s['source']}.trigger.source.action = {s['source']}.ENABLE")
        self.k._write(f"{s['source']}.measure.nplc = {s['nplc']}")
        self.k._write(
            f"{s['source']}.trigger.endsweep.action = {s['source']}.SOURCE_IDLE"
        )
        self.k._write(
            f"{s['source']}.trigger.measure.stimulus = {s['source']}.trigger.SOURCE_COMPLETE_EVENT_ID"
        )
        self.k._write(
            f"{s['source']}.trigger.endpulse.stimulus = {s['source']}.trigger.MEASURE_COMPLETE_EVENT_ID"
        )

        # Set highc mode if needed.
        if s.get("highC_source", False):
            self.k._write(f"{s['source']}.source.highc = {s['source']}.ENABLE")
        if s["single_ch"] and s.get("highC_drain", False):
            self.k._write(f"{s['drain']}.source.highc = {s['drain']}.ENABLE")

        if not s["single_ch"]:
            self.k._write(
                f"{s['drain']}.trigger.measure.iv({s['drain']}.nvbuffer1, {s['drain']}.nvbuffer2)"
            )
            self.k._write(f"{s['drain']}.trigger.measure.action = {s['drain']}.ENABLE")
            self.k._write(f"{s['drain']}.trigger.source.action = {s['drain']}.DISABLE")

            if s["delay"] == "off":
                self.k._write(f"{s['drain']}.measure.delay = {s['drain']}.DELAY_AUTO")
                if s["pulse"] == "off":
                    self.k._write(f"{s['drain']}.measure.delayfactor = 28.0")
                else:
                    self.k._write(f"{s['drain']}.measure.delayfactor = 1.0")
            else:
                self.k._write(f"{s['drain']}.measure.delay = {s['delay']}")

            self.k._write(f"{s['drain']}.measure.nplc = {s['nplc']}")
            self.k._write(
                f"{s['drain']}.trigger.measure.stimulus = {s['source']}.trigger.SOURCE_COMPLETE_EVENT_ID"
            )
            self.k._write(
                f"{s['source']}.trigger.measure.stimulus = {s['source']}.trigger.SOURCE_COMPLETE_EVENT_ID"
            )
            self.k._write("trigger.blender[2].orenable = false")
            self.k._write(
                f"trigger.blender[2].stimulus[1] = {s['source']}.trigger.MEASURE_COMPLETE_EVENT_ID"
            )
            self.k._write(
                f"trigger.blender[2].stimulus[2] = {s['drain']}.trigger.MEASURE_COMPLETE_EVENT_ID"
            )
            self.k._write(
                f"{s['source']}.trigger.endpulse.stimulus = trigger.blender[2].EVENT_ID"
            )

    def run_sweep(self, s: dict):
        """
        % % % Keithley.steps %%int
        % % % Keithley.repeat %%int
        % % % Keithley.start %%int
        % % % Keithley.end %%int
        % % % Keithley.limit %%float
        % % % Keithley.delay %%str "off"/time in sec before measurement SET
        % % % Keithley.pulse %%str "off"/time in sec pause between pulses
        % % % Keithley.source %%str "smua"/"smub"
        % % % Keithley.drain %%str "smua"/"smub"
        % % % Keithley.type %%str "i"/"v"
        % % % Keithley.drainLimit %% str
        % % % Keithley.freq %% float
        % % % Keithley.drainVoltage %% str "off"/value
        % % % Keithley.nplc %% str  SET
        % % % Keithley.sense %% true/false
        % % % Keithley.sense_drain %% true/false
        % % % Keithley.single_ch %% true/false

        Args:
            s (dict): _description_
        """
