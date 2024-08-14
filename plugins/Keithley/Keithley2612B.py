import sys
import os
import time

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QCheckBox, QComboBox, QLineEdit, QPushButton
from PyQt6.QtCore import QObject

from keithley2600 import Keithley2600


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

    def measure(self):
        print("Measuring from Keithley 2612B")

    def parse_settings_widget(self):

        if self.s["comboBox_inject"]() == "voltage":
            print("Voltage source")
        else:
            print("Current source")

        if self.s["comboBox_channel"]() == "smuA":
            print("Channel A")
            self.currHandle = self.k.smua
        else:
            print("Channel B")
            self.currHandle = self.k.smub

        if self.s["checkBox_singleChannel"]():
            print("Single channel")
        else:
            print("Dual channel")

        if self.s["lineEdit_repeat"]() != "":
            print("Repeating")
        else:
            print("Not repeating")

    def run_single_channel_sweep(self):
        # WHAT NEEDS TO BE SET MANUALLY
        # Sensing
        # High-c
        # Pause
        # Integ time = NPLC = t_int
        # Voltage limit

        print("Running single channel sweep")
        raise NotImplementedError
        # self.k.voltage_sweep_single_smu(smu=, smu_sweeplist=, t_int=, delay=, pulsed=)
        # So this takes in a list of voltages to sweep, integraiton time, delay,
        # and whether it is pulsed or not.

    def run_dual_channel_sweep(self):
        print("Running dual channel sweep")
        raise NotImplementedError
        # self.k.voltage_sweep_dual_smu()

    def run_single_channel_current_sweep(self):
        print("Running single channel current sweep")
        raise NotImplementedError
        # self.k.current_sweep_single_smu()

    def run_dual_channel_current_sweep(self):
        print("Running dual channel current sweep")
        raise NotImplementedError
        # self.k.current_sweep_dual_smu()

    # FIXME: Missing hooks for current sweeps? Prolly needed


def init_channel(self, s: dict, dev):
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
    dev.write("reset()")
    dev.write("beeper.enable=0")
    dev.write(f"{s['source']}.reset()")

    if "drain" in s:
        dev.write(f"{s['drain']}.reset()")

    if s["sense"]:
        dev.write(f"{s['source']}.sense = {s['source']}.SENSE_REMOTE")
    else:
        dev.write(f"{s['source']}.sense = {s['source']}.SENSE_LOCAL")

    if not s["single_ch"]:
        if s["sense_drain"] and s["sense"]:
            dev.write(f"{s['drain']}.sense = {s['drain']}.SENSE_REMOTE")
        else:
            dev.write(f"{s['drain']}.sense = {s['drain']}.SENSE_LOCAL")

    # Common settings
    dev.write(f"{s['source']}.measure.filter.count = 4")
    dev.write(f"{s['source']}.measure.filter.enable = {s['source']}.FILTER_ON")
    dev.write(f"{s['source']}.measure.filter.type = {s['source']}.FILTER_REPEAT_AVG")
    dev.write(f"{s['source']}.measure.autorangei = {s['source']}.AUTORANGE_ON")
    dev.write(f"{s['source']}.measure.autorangev = {s['source']}.AUTORANGE_ON")

    if not s["single_ch"]:
        dev.write("smua.measure.filter.count = 4")
        dev.write("smub.measure.filter.count = 4")
        dev.write("smua.measure.filter.enable = smua.FILTER_ON")
        dev.write("smub.measure.filter.enable = smub.FILTER_ON")
        dev.write("smua.measure.filter.type = smua.FILTER_REPEAT_AVG")
        dev.write("smub.measure.filter.type = smub.FILTER_REPEAT_AVG")
        dev.write(f"{s['drain']}.measure.autorangei = {s['drain']}.AUTORANGE_ON")
        dev.write(f"{s['drain']}.measure.autorangev = {s['drain']}.AUTORANGE_ON")

    if s["pulse"] == "off":
        dev.write(f"{s['source']}.trigger.endpulse.action = {s['source']}.SOURCE_HOLD")
    else:
        dev.write(f"{s['source']}.trigger.endpulse.action = {s['source']}.SOURCE_IDLE")
        dev.write(f"trigger.timer[1].delay = {s['pulse']}")
        dev.write("trigger.timer[1].passthrough = false")
        dev.write("trigger.timer[1].count = 1")
        dev.write("trigger.blender[1].orenable = true")
        dev.write(
            f"trigger.blender[1].stimulus[1] = {s['source']}.trigger.SWEEPING_EVENT_ID"
        )
        dev.write(
            f"trigger.blender[1].stimulus[2] = {s['source']}.trigger.PULSE_COMPLETE_EVENT_ID"
        )
        dev.write("trigger.timer[1].stimulus = trigger.blender[1].EVENT_ID")
        dev.write(f"{s['source']}.trigger.source.stimulus = trigger.timer[1].EVENT_ID")

    dev.write(f"{s['source']}.source.settling = {s['source']}.SETTLE_FAST_RANGE")
    dev.write("display.screen = display.SMUA_SMUB")
    dev.write("format.data = format.ASCII")

    if s["delay"] == "off":
        dev.write(f"{s['source']}.measure.delay = {s['source']}.DELAY_AUTO")
        if s["pulse"] == "off":
            dev.write(f"{s['source']}.measure.delayfactor = 28.0")
        else:
            dev.write(f"{s['source']}.measure.delayfactor = 1.0")
    else:
        dev.write(f"{s['source']}.measure.delay = {s['delay']}")

    dev.write(
        f"{s['source']}.trigger.measure.iv({s['source']}.nvbuffer1, {s['source']}.nvbuffer2)"
    )
    dev.write(f"{s['source']}.trigger.measure.action = {s['source']}.ENABLE")
    dev.write(f"{s['source']}.trigger.source.action = {s['source']}.ENABLE")
    dev.write(f"{s['source']}.measure.nplc = {s['nplc']}")
    dev.write(f"{s['source']}.trigger.endsweep.action = {s['source']}.SOURCE_IDLE")
    dev.write(
        f"{s['source']}.trigger.measure.stimulus = {s['source']}.trigger.SOURCE_COMPLETE_EVENT_ID"
    )
    dev.write(
        f"{s['source']}.trigger.endpulse.stimulus = {s['source']}.trigger.MEASURE_COMPLETE_EVENT_ID"
    )

    if s.get("highC", False):
        dev.write(f"{s['source']}.source.highc = {s['source']}.ENABLE")

    if not s["single_ch"]:
        dev.write(
            f"{s['drain']}.trigger.measure.iv({s['drain']}.nvbuffer1, {s['drain']}.nvbuffer2)"
        )
        dev.write(f"{s['drain']}.trigger.measure.action = {s['drain']}.ENABLE")
        dev.write(f"{s['drain']}.trigger.source.action = {s['drain']}.DISABLE")

        if s["delay"] == "off":
            dev.write(f"{s['drain']}.measure.delay = {s['drain']}.DELAY_AUTO")
            if s["pulse"] == "off":
                dev.write(f"{s['drain']}.measure.delayfactor = 28.0")
            else:
                dev.write(f"{s['drain']}.measure.delayfactor = 1.0")
        else:
            dev.write(f"{s['drain']}.measure.delay = {s['delay']}")

        dev.write(f"{s['drain']}.measure.nplc = {s['nplc']}")
        dev.write(
            f"{s['drain']}.trigger.measure.stimulus = {s['source']}.trigger.SOURCE_COMPLETE_EVENT_ID"
        )
        dev.write(
            f"{s['source']}.trigger.measure.stimulus = {s['source']}.trigger.SOURCE_COMPLETE_EVENT_ID"
        )
        dev.write("trigger.blender[2].orenable = false")
        dev.write(
            f"trigger.blender[2].stimulus[1] = {s['source']}.trigger.MEASURE_COMPLETE_EVENT_ID"
        )
        dev.write(
            f"trigger.blender[2].stimulus[2] = {s['drain']}.trigger.MEASURE_COMPLETE_EVENT_ID"
        )
        dev.write(
            f"{s['source']}.trigger.endpulse.stimulus = trigger.blender[2].EVENT_ID"
        )
