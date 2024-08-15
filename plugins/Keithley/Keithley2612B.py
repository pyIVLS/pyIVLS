import sys
import os
import time
from threading import Lock


from PyQt6 import uic
from PyQt6.QtWidgets import (
    QWidget,
    QCheckBox,
    QComboBox,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
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

        # Initialize the settings dict
        self.s = self._get_settings_dict()

        # Initialize resource manager
        self.rm = pyvisa.ResourceManager("@py")

        # FIXME: DEBUG
        debug_button = self.settingsWidget.findChild(QPushButton, "pushButton")
        debug_button.clicked.connect(self.debug_button)

        self._connect_signals()

    def debug_button(self):
        settings = self.parse_settings_widget()
        self.connect()
        print(settings)
        self.init_channel(settings, self.k)
        self.disconnect()

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
        mode_box = self.settingsWidget.findChild(QComboBox, "comboBox_mode")
        mode_box.activated.connect(self._mode_changed)
        # call mode changed to update to the correct mode
        self._mode_changed()

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

    def connect(self):
        print("Connecting to Keithley 2612B")
        self.k = self.rm.open_resource(pyIVLS_constants.keithley_visa)
        self.k.query("*IDN?")
        # FIXME: add settings for termination
        # my_instrument.read_termination = '\n'
        # my_instrument.write_termination = '\n'

    def disconnect(self):
        print("Disconnecting from Keithley 2612B")
        self.k.close()

    def busy(self) -> bool:
        raise NotImplementedError("Busy function not implemented yet.")

    def parse_settings_widget(self) -> dict:
        """Parse the settings widget into a form that the legacy code can understand.

        Returns:
            dict: Parsed settings.
        """
        legacy_dict = {}
        # FIXME: determine line frequency. This is not in the settings widget, quite obviously.

        # Determine source channel
        legacy_dict["source"] = (
            "smua" if self.s["comboBox_channel"]() == "smuA" else "smub"
        )

        # Determine source type
        inject_type = self.s["comboBox_inject"]()
        print("Voltage source" if inject_type == "voltage" else "Current source")

        # Determine repeat count
        legacy_dict["repeat"] = self.s["lineEdit_repeat"]()

        # set mode
        if self.s["comboBox_mode"]() == "Continuous":
            legacy_dict["pulse"] = "off"
        elif self.s["comboBox_mode"]() == "Pulsed":
            legacy_dict["pulse"] = self.s["lineEdit_pulsedPause"]()
        else:
            # How to handle this? Call a separate function to handle this?
            raise NotImplementedError("Mixed mode not implemented yet.")

        # Set single channel and drain
        legacy_dict["single_ch"] = self.s["checkBox_singleChannel"]()
        if not legacy_dict["single_ch"]:
            legacy_dict["drain"] = "smub" if legacy_dict["source"] == "smua" else "smua"

            # Read data for the drain if not in single channel mode
            legacy_dict["highC_drain"] = self.s["checkBox_drainHighC"]()
            legacy_dict["drainVoltage"] = self.s["lineEdit_drainStart"]()
            legacy_dict["drainLimit"] = self.s["lineEdit_drainLimit"]()
            legacy_dict["nplc_drain"] = self.s["lineEdit_drainNPLC"]()

        # Set source sense mode
        source_sense_mode = self.s["comboBox_sourceSenseMode"]()
        if source_sense_mode == "2 wire":
            legacy_dict["sense"] = False
        elif source_sense_mode == "4 wire":
            legacy_dict["sense"] = True
        else:
            # How to handle this? Call a separate function to handle this?
            raise NotImplementedError("2 + 4 mode not implemented yet.")

        # set drain sense mode in case it is needed.
        drain_sense_mode = self.s["comboBox_drainSenseMode"]()
        if not legacy_dict["single_ch"]:
            if drain_sense_mode == "2 wire":
                legacy_dict["sense_drain"] = False
            elif drain_sense_mode == "4 wire":
                legacy_dict["sense_drain"] = True
            else:
                # How to handle this? Call a separate function to handle this, which provides two copies of the settings?
                raise NotImplementedError("2 + 4 mode not implemented yet.")

        if legacy_dict["pulse"]:
            legacy_dict["start"] = self.s["lineEdit_pulsedStart"]()
            legacy_dict["end"] = self.s["lineEdit_pulsedEnd"]()
            legacy_dict["steps"] = self.s["lineEdit_pulsedPoints"]()
            legacy_dict["limit"] = self.s["lineEdit_pulsedLimit"]()
            legacy_dict["nplc"] = self.s["lineEdit_pulsedNPLC"]()
            # FIXME: NOT READING PULSE PAUSE
            if self.s["comboBox_pulsedDelayMode"]() == "Auto":
                legacy_dict["delay"] = "off"
            else:
                legacy_dict["delay"] = self.s["lineEdit_pulsedDelay"]()

        else:
            legacy_dict["start"] = self.s["lineEdit_continuousStart"]()
            legacy_dict["end"] = self.s["lineEdit_continuousEnd"]()
            legacy_dict["steps"] = self.s["lineEdit_continuousPoints"]()
            legacy_dict["limit"] = self.s["lineEdit_continuousLimit"]()
            legacy_dict["nplc"] = self.s["lineEdit_continuousNPLC"]()
            if self.s["comboBox_continuousDelayMode"]() == "Auto":
                legacy_dict["delay"] = "off"
            else:
                legacy_dict["delay"] = self.s["lineEdit_continuousDelay"]()

        return legacy_dict

    def init_channel(self, s: dict, k):
        """Combines the functionality of init_sigle_channel and init_dual_channel into one function.
        % % % Keithley.delay %%str "off"/time in sec before measurement
        % % % Keithley.pulse %%str "off"/time in sec pause between pulses
        % % % Keithley.source %%str "smua"/"smub"
        % % % Keithley.drain %%str "smua"/"smub"
        % % % Keithley.nplc %% str
        % % % Keithley.sense %% true/false
        % % % Keithley.sense_drain %% true/false
        % % % Keithley.single_ch %% true/false
        Sets integration time, sense mode, pulse delay.
        Args:
            s (dict): dict of settings. See above.
            dev (_type_): pyvisa device instance
        """
        k.write("reset()")
        k.write("beeper.enable=0")
        k.write(f"{s['source']}.reset()")

        if "drain" in s:
            k.write(f"{s['drain']}.reset()")

        if s["sense"]:
            k.write(f"{s['source']}.sense = {s['source']}.SENSE_REMOTE")
        else:
            k.write(f"{s['source']}.sense = {s['source']}.SENSE_LOCAL")

        if not s["single_ch"]:
            if s["sense_drain"] and s["sense"]:
                k.write(f"{s['drain']}.sense = {s['drain']}.SENSE_REMOTE")
            else:
                k.write(f"{s['drain']}.sense = {s['drain']}.SENSE_LOCAL")

        # Common settings
        k.write(f"{s['source']}.measure.filter.count = 4")
        k.write(f"{s['source']}.measure.filter.enable = {s['source']}.FILTER_ON")
        k.write(f"{s['source']}.measure.filter.type = {s['source']}.FILTER_REPEAT_AVG")
        k.write(f"{s['source']}.measure.autorangei = {s['source']}.AUTORANGE_ON")
        k.write(f"{s['source']}.measure.autorangev = {s['source']}.AUTORANGE_ON")

        if not s["single_ch"]:
            k.write("smua.measure.filter.count = 4")
            k.write("smub.measure.filter.count = 4")
            k.write("smua.measure.filter.enable = smua.FILTER_ON")
            k.write("smub.measure.filter.enable = smub.FILTER_ON")
            k.write("smua.measure.filter.type = smua.FILTER_REPEAT_AVG")
            k.write("smub.measure.filter.type = smub.FILTER_REPEAT_AVG")
            k.write(f"{s['drain']}.measure.autorangei = {s['drain']}.AUTORANGE_ON")
            k.write(f"{s['drain']}.measure.autorangev = {s['drain']}.AUTORANGE_ON")

        if s["pulse"] == "off":
            k.write(
                f"{s['source']}.trigger.endpulse.action = {s['source']}.SOURCE_HOLD"
            )
        else:
            k.write(
                f"{s['source']}.trigger.endpulse.action = {s['source']}.SOURCE_IDLE"
            )
            k.write(f"trigger.timer[1].delay = {s['pulse']}")
            k.write("trigger.timer[1].passthrough = false")
            k.write("trigger.timer[1].count = 1")
            k.write("trigger.blender[1].orenable = true")
            k.write(
                f"trigger.blender[1].stimulus[1] = {s['source']}.trigger.SWEEPING_EVENT_ID"
            )
            k.write(
                f"trigger.blender[1].stimulus[2] = {s['source']}.trigger.PULSE_COMPLETE_EVENT_ID"
            )
            k.write("trigger.timer[1].stimulus = trigger.blender[1].EVENT_ID")
            k.write(
                f"{s['source']}.trigger.source.stimulus = trigger.timer[1].EVENT_ID"
            )

        k.write(f"{s['source']}.source.settling = {s['source']}.SETTLE_FAST_RANGE")
        k.write("display.screen = display.SMUA_SMUB")
        k.write("format.data = format.ASCII")

        if s["delay"] == "off":
            k.write(f"{s['source']}.measure.delay = {s['source']}.DELAY_AUTO")
            if s["pulse"] == "off":
                k.write(f"{s['source']}.measure.delayfactor = 28.0")
            else:
                k.write(f"{s['source']}.measure.delayfactor = 1.0")
        else:
            k.write(f"{s['source']}.measure.delay = {s['delay']}")

        k.write(
            f"{s['source']}.trigger.measure.iv({s['source']}.nvbuffer1, {s['source']}.nvbuffer2)"
        )
        k.write(f"{s['source']}.trigger.measure.action = {s['source']}.ENABLE")
        k.write(f"{s['source']}.trigger.source.action = {s['source']}.ENABLE")
        k.write(f"{s['source']}.measure.nplc = {s['nplc']}")
        k.write(f"{s['source']}.trigger.endsweep.action = {s['source']}.SOURCE_IDLE")
        k.write(
            f"{s['source']}.trigger.measure.stimulus = {s['source']}.trigger.SOURCE_COMPLETE_EVENT_ID"
        )
        k.write(
            f"{s['source']}.trigger.endpulse.stimulus = {s['source']}.trigger.MEASURE_COMPLETE_EVENT_ID"
        )

        # Set highc mode if needed.
        if s.get("highC_source", False):
            k.write(f"{s['source']}.source.highc = {s['source']}.ENABLE")
        if s["single_ch"] and s.get("highC_drain", False):
            k.write(f"{s['drain']}.source.highc = {s['drain']}.ENABLE")

        if not s["single_ch"]:
            k.write(
                f"{s['drain']}.trigger.measure.iv({s['drain']}.nvbuffer1, {s['drain']}.nvbuffer2)"
            )
            k.write(f"{s['drain']}.trigger.measure.action = {s['drain']}.ENABLE")
            k.write(f"{s['drain']}.trigger.source.action = {s['drain']}.DISABLE")

            if s["delay"] == "off":
                k.write(f"{s['drain']}.measure.delay = {s['drain']}.DELAY_AUTO")
                if s["pulse"] == "off":
                    k.write(f"{s['drain']}.measure.delayfactor = 28.0")
                else:
                    k.write(f"{s['drain']}.measure.delayfactor = 1.0")
            else:
                k.write(f"{s['drain']}.measure.delay = {s['delay']}")

            k.write(f"{s['drain']}.measure.nplc = {s['nplc']}")
            k.write(
                f"{s['drain']}.trigger.measure.stimulus = {s['source']}.trigger.SOURCE_COMPLETE_EVENT_ID"
            )
            k.write(
                f"{s['source']}.trigger.measure.stimulus = {s['source']}.trigger.SOURCE_COMPLETE_EVENT_ID"
            )
            k.write("trigger.blender[2].orenable = false")
            k.write(
                f"trigger.blender[2].stimulus[1] = {s['source']}.trigger.MEASURE_COMPLETE_EVENT_ID"
            )
            k.write(
                f"trigger.blender[2].stimulus[2] = {s['drain']}.trigger.MEASURE_COMPLETE_EVENT_ID"
            )
            k.write(
                f"{s['source']}.trigger.endpulse.stimulus = trigger.blender[2].EVENT_ID"
            )

    def run_sweep_voltage(self, s: dict):
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
        # Generate the sweep list for the source
        sweep_list = np.linspace(s["start"], s["end"], s["steps"])
        if s["source"] == "smua":
            self.k.voltage_sweep_single_channel(
                smu=s["source"],
                sweep_list=sweep_list,
                delay=int(s["delay"]),
                pulsed=s["pulse"],
            )
        if s["single_ch"]:
            self.k.voltage_sweep_single_channel(
                smu=s["source_inst"],
                sweep_list=sweep_list,
                delay=int(s["delay"]),
                pulsed=s["pulse"],
            )

    def KeithleyRunSingleChSweep(self, s: dict):
        readsteps = s["steps"]
        waitDelay = float(s["pulse"]) if s["pulse"] != "off" else 1

        k.write(f"{s['source']}.nvbuffer1.clear()")
        k.write(f"{s['source']}.nvbuffer2.clear()")
        k.write(f"{s['source']}.trigger.count = {s['steps']}")
        k.write(f"{s['source']}.trigger.arm.count = {s['repeat']}")
        k.write(
            f"{s['source']}.trigger.source.linear{s['type']}({s['start']},{s['end']},{s['steps']})"
        )

        if s["type"] == "i":
            if abs(s["start"]) < 1.5 and abs(s["end"]) < 1.5:
                k.write(f"{s['source']}.trigger.source.limitv = {s['limit']}")
                k.write(f"{s['source']}.source.limitv = {s['limit']}")
            else:
                k.write(
                    f"{s['source']}.measure.filter.enable = {s['source']}.FILTER_OFF"
                )
                k.write(
                    f"{s['source']}.source.autorangei = {s['source']}.AUTORANGE_OFF"
                )
                k.write(
                    f"{s['source']}.source.autorangev = {s['source']}.AUTORANGE_OFF"
                )
                k.write(f"{s['source']}.source.delay = 100e-6")
                k.write(f"{s['source']}.measure.autozero = {s['source']}.AUTOZERO_OFF")
                k.write(f"{s['source']}.source.rangei = 10")
                k.write(f"{s['source']}.source.leveli = 0")
                k.write(f"{s['source']}.source.limitv = 6")
                k.write(f"{s['source']}.trigger.source.limiti = 10")
            k.write(f"display.{s['source']}.measure.func = display.MEASURE_DCVOLTS")
        else:
            if abs(s["limit"]) < 1.5:
                k.write(f"{s['source']}.trigger.source.limiti = {s['limit']}")
                k.write(f"{s['source']}.source.limiti = {s['limit']}")
            else:
                k.write(
                    f"{s['source']}.measure.filter.enable = {s['source']}.FILTER_OFF"
                )
                k.write(
                    f"{s['source']}.source.autorangei = {s['source']}.AUTORANGE_OFF"
                )
                k.write(
                    f"{s['source']}.source.autorangev = {s['source']}.AUTORANGE_OFF"
                )
                k.write(f"{s['source']}.measure.rangei = 10")
                k.write(f"{s['source']}.source.delay = 100e-6")
                k.write(f"{s['source']}.measure.autozero = {s['source']}.AUTOZERO_OFF")
                k.write(f"{s['source']}.source.rangev = 6")
                k.write(f"{s['source']}.source.levelv = 0")
                k.write(f"{s['source']}.source.limiti = {s['limit']}")
                k.write(f"{s['source']}.trigger.source.limiti = {s['limit']}")
            k.write(f"display.{s['source']}.measure.func = display.MEASURE_DCAMPS")

        k.write(f"{s['source']}.source.output = {s['source']}.OUTPUT_ON")
        k.write(f"{s['source']}.trigger.initiate()")
        time.sleep(waitDelay)

        buffer_prev = 0
        iv = []
        # NOTE: change to use read_buffer method of Keithley2600?
        while True:
            if not self.busy():
                k.write(f"{s['source']}.abort()")
                k.write(f"{s['source']}.source.output = {s['source']}.OUTPUT_OFF")
                return iv

            k.write(f"print({s['source']}.nvbuffer2.n)")
            buffern = int(s["handle"].read())

            if buffern >= s["steps"] * s["repeat"]:
                break

            if buffern > buffer_prev:
                k.write(f"printbuffer({buffern}, {buffern}, {s['source']}.nvbuffer1)")
                i_tmp = float(s["handle"].read())
                k.write(f"printbuffer({buffern}, {buffern}, {s['source']}.nvbuffer2)")
                v_tmp = float(s["handle"].read())
                iv.append((v_tmp, i_tmp))

                if (s["type"] == "i" and abs(v_tmp) > 0.95 * abs(s["limit"])) or (
                    s["type"] == "v" and abs(i_tmp) > 0.95 * abs(s["limit"])
                ):
                    k.write(f"{s['source']}.abort()")
                    readsteps = buffern
                    break

                buffer_prev = buffern

            time.sleep(0.5)

        time.sleep(waitDelay * 1.2)
        k.write(f"{s['source']}.source.output = {s['source']}.OUTPUT_OFF")
        k.write(f"printbuffer(1, {readsteps}, {s['source']}.nvbuffer1)")
        iv[:, 0] = [float(x) for x in s["handle"].read().split()]
        k.write(f"printbuffer(1, {readsteps}, {s['source']}.nvbuffer2)")
        iv[:, 1] = [float(x) for x in s["handle"].read().split()]

        return iv
