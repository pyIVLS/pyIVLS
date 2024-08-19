import sys
import os
import time
from threading import RLock


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

        # Initialize the lock for the measurement
        self.lock = RLock()
        self.debug_mode = False

    ## Widget functions
    def debug_button(self):
        settings = self.parse_settings_widget()
        print(settings)
        self.debug_mode = True
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
        mode_box = self.settingsWidget.findChild(QComboBox, "comboBox_mode")
        mode_box.activated.connect(self._mode_changed)
        # call mode changed to update to the correct mode
        self._mode_changed()

        inject_box = self.settingsWidget.findChild(QComboBox, "comboBox_inject")
        inject_box.activated.connect(self._inject_changed)
        self._inject_changed()

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
            self.self.safewrite(command)
            if self.debug_mode:
                error_code = self.k.query("print(errorqueue.next())")
                if "Queue Is Empty" not in error_code:
                    print(f"Error sending command: {command}\nError code: {error_code}")
        except Exception as e:
            print(f"Exception sending command: {command}\nException: {e}")
        finally:
            self.self.safewrite("errorqueue.clear()")

    def connect(self):
        print("Connecting to Keithley 2612B")
        self.k = self.rm.open_resource(pyIVLS_constants.keithley_visa)
        self.k.query("*IDN?")
        self.k.read_termination = "\n"
        # FIXME: add settings for termination
        # my_instrument.read_termination = '\n'
        # my_instrument.write_termination = '\n'

    def disconnect(self):
        print("Disconnecting from Keithley 2612B")
        self.k.close()

    def busy(self) -> bool:

        gotten = self.lock.acquire(blocking=False)

        if gotten:
            self.lock.release()

        return not gotten

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
        legacy_dict["type"] = "v" if inject_type == "voltage" else "i"

        # Determine repeat count
        legacy_dict["repeat"] = int(self.s["lineEdit_repeat"]())
        assert legacy_dict["repeat"] > 0

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
        legacy_dict["highC"] = self.s["checkBox_sourceHighC"]()
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

        if legacy_dict["pulse"] != "off":
            legacy_dict["start"] = float(self.s["lineEdit_pulsedStart"]())
            legacy_dict["end"] = float(self.s["lineEdit_pulsedEnd"]())
            legacy_dict["steps"] = int(self.s["lineEdit_pulsedPoints"]())
            legacy_dict["limit"] = float(self.s["lineEdit_pulsedLimit"]())
            legacy_dict["nplc"] = self.s["lineEdit_pulsedNPLC"]()
            if self.s["comboBox_pulsedDelayMode"]() == "Auto":
                legacy_dict["delay"] = "off"
            else:
                legacy_dict["delay"] = self.s["lineEdit_pulsedDelay"]()

        else:
            legacy_dict["start"] = float(self.s["lineEdit_continuousStart"]())
            legacy_dict["end"] = float(self.s["lineEdit_continuousEnd"]())
            legacy_dict["steps"] = int(self.s["lineEdit_continuousPoints"]())
            legacy_dict["limit"] = float(self.s["lineEdit_continuousLimit"]())
            legacy_dict["nplc"] = self.s["lineEdit_continuousNPLC"]()
            if self.s["comboBox_continuousDelayMode"]() == "Auto":
                legacy_dict["delay"] = "off"
            else:
                legacy_dict["delay"] = self.s["lineEdit_continuousDelay"]()
        assert legacy_dict["steps"] > 0

        return legacy_dict

    def KeithleyInitSingleCh(self, s: dict):
        """TESTED AND WORKING YEEHAW

        Args:
            s (dict): _description_
            k (_type_): _description_
        """
        self.safewrite("reset()")
        self.safewrite("beeper.enable=0")
        self.safewrite(f'{s["source"]}.reset()')

        if s["sense"]:
            self.safewrite(f'{s["source"]}.sense = {s["source"]}.SENSE_REMOTE')
        else:
            self.safewrite(f'{s["source"]}.sense = {s["source"]}.SENSE_LOCAL')

        # Consider moving this to GUI
        self.safewrite(f'{s["source"]}.measure.filter.count = 4')
        self.safewrite(f'{s["source"]}.measure.filter.enable = {s["source"]}.FILTER_ON')
        self.safewrite(
            f'{s["source"]}.measure.filter.type = {s["source"]}.FILTER_REPEAT_AVG'
        )
        self.safewrite(f'{s["source"]}.measure.autorangei = {s["source"]}.AUTORANGE_ON')
        self.safewrite(f'{s["source"]}.measure.autorangev = {s["source"]}.AUTORANGE_ON')
        # End of consider moving this to GUI

        if s["pulse"] == "off":
            self.safewrite(
                f'{s["source"]}.trigger.endpulse.action = {s["source"]}.SOURCE_HOLD'
            )
        else:
            self.safewrite(
                f'{s["source"]}.trigger.endpulse.action = {s["source"]}.SOURCE_IDLE'
            )
            self.safewrite(f'trigger.timer[1].delay = {s["pulse"]}')
            self.safewrite("trigger.timer[1].passthrough = false")
            self.safewrite("trigger.timer[1].count = 1")
            self.safewrite("trigger.blender[1].orenable = true")
            self.safewrite(
                f'trigger.blender[1].stimulus[1] = {s["source"]}.trigger.SWEEPING_EVENT_ID'
            )
            self.safewrite(
                f'trigger.blender[1].stimulus[2] = {s["source"]}.trigger.PULSE_COMPLETE_EVENT_ID'
            )
            self.safewrite("trigger.timer[1].stimulus = trigger.blender[1].EVENT_ID")
            self.safewrite(
                f'{s["source"]}.trigger.source.stimulus = trigger.timer[1].EVENT_ID'
            )

        self.safewrite(
            f'{s["source"]}.source.settling = {s["source"]}.SETTLE_FAST_RANGE'
        )
        self.safewrite("display.screen = display.SMUA_SMUB")
        self.safewrite("format.data = format.ASCII")

        if s["delay"] == "off":
            self.safewrite(f'{s["source"]}.measure.delay = {s["source"]}.DELAY_AUTO')
            if s["pulse"] == "off":
                self.safewrite(f'{s["source"]}.measure.delayfactor = 28.0')
            else:
                self.safewrite(f'{s["source"]}.measure.delayfactor = 1.0')
        else:
            self.safewrite(f'{s["source"]}.measure.delay = {s["delay"]}')

        self.safewrite(
            f'{s["source"]}.trigger.measure.iv({s["source"]}.nvbuffer1, {s["source"]}.nvbuffer2)'
        )
        self.safewrite(f'{s["source"]}.trigger.measure.action = {s["source"]}.ENABLE')
        self.safewrite(f'{s["source"]}.trigger.source.action = {s["source"]}.ENABLE')
        self.safewrite(f'{s["source"]}.measure.nplc = {s["nplc"]}')
        self.safewrite(
            f'{s["source"]}.trigger.endsweep.action = {s["source"]}.SOURCE_IDLE'
        )
        self.safewrite(
            f'{s["source"]}.trigger.measure.stimulus = {s["source"]}.trigger.SOURCE_COMPLETE_EVENT_ID'
        )
        self.safewrite(
            f'{s["source"]}.trigger.endpulse.stimulus = {s["source"]}.trigger.MEASURE_COMPLETE_EVENT_ID'
        )

        if s["highC"]:
            self.safewrite(f'{s["source"]}.source.highc = {s["source"]}.ENABLE')

    def keithley_init_dual_ch(self, s: dict):
        """Tested and working

        Args:
            s (dict): _description_
            k (_type_): _description_
        """

        self.safewrite("reset()")
        self.safewrite("beeper.enable=0")
        self.safewrite(f"{s['source']}.reset()")
        self.safewrite(f"{s['drain']}.reset()")

        if s["sense"]:
            self.safewrite(f"{s['source']}.sense = {s['source']}.SENSE_REMOTE")
        else:
            self.safewrite(f"{s['source']}.sense = {s['source']}.SENSE_LOCAL")

        if s["sense_drain"] and s["sense"]:
            self.safewrite(f"{s['drain']}.sense = {s['drain']}.SENSE_REMOTE")
        else:
            self.safewrite(f"{s['drain']}.sense = {s['drain']}.SENSE_LOCAL")

        self.safewrite("smua.measure.filter.count = 4")
        self.safewrite("smub.measure.filter.count = 4")
        self.safewrite("smua.measure.filter.enable = smua.FILTER_ON")
        self.safewrite("smub.measure.filter.enable = smub.FILTER_ON")
        self.safewrite("smua.measure.filter.type = smua.FILTER_REPEAT_AVG")
        self.safewrite("smub.measure.filter.type = smub.FILTER_REPEAT_AVG")

        self.safewrite(f"{s['source']}.measure.autorangei = {s['source']}.AUTORANGE_ON")
        self.safewrite(f"{s['source']}.measure.autorangev = {s['source']}.AUTORANGE_ON")
        self.safewrite(f"{s['drain']}.measure.autorangei = {s['drain']}.AUTORANGE_ON")
        self.safewrite(f"{s['drain']}.measure.autorangev = {s['drain']}.AUTORANGE_ON")

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

        self.safewrite("smua.source.settling = smua.SETTLE_FAST_RANGE")
        self.safewrite("smub.source.settling = smub.SETTLE_FAST_RANGE")
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
        self.safewrite(
            f"{s['drain']}.trigger.measure.iv({s['drain']}.nvbuffer1, {s['drain']}.nvbuffer2)"
        )
        self.safewrite(f"{s['drain']}.trigger.measure.action = {s['drain']}.ENABLE")
        self.safewrite(f"{s['drain']}.trigger.source.action = {s['drain']}.DISABLE")

        self.safewrite(f"{s['source']}.measure.nplc = {s['nplc']}")
        self.safewrite(
            f"{s['source']}.trigger.endsweep.action = {s['source']}.SOURCE_IDLE"
        )

        if s["delay"] == "off":
            self.safewrite(f"{s['drain']}.measure.delay = {s['drain']}.DELAY_AUTO")
            if s["pulse"] == "off":
                self.safewrite(f"{s['drain']}.measure.delayfactor = 28.0")
            else:
                self.safewrite(f"{s['drain']}.measure.delayfactor = 1.0")
        else:
            self.safewrite(f"{s['drain']}.measure.delay = {s['delay']}")

        self.safewrite(f"{s['drain']}.measure.nplc = {s['nplc']}")
        self.safewrite(
            f"{s['drain']}.trigger.measure.stimulus = {s['source']}.trigger.SOURCE_COMPLETE_EVENT_ID"
        )
        self.safewrite(
            f"{s['source']}.trigger.measure.stimulus = {s['source']}.trigger.SOURCE_COMPLETE_EVENT_ID"
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

        if s["highC"]:
            self.safewrite(f"{s['source']}.source.highc = {s['source']}.ENABLE")
            self.safewrite(f"{s['drain']}.source.highc = {s['drain']}.ENABLE")

    def KeithleyRunSingleChSweep(self, s: dict):
        with self.lock:

            readsteps = s["steps"]
            waitDelay = float(s["pulse"]) if s["pulse"] != "off" else 1

            self.safewrite(f"{s['source']}.nvbuffer1.clear()")
            self.safewrite(f"{s['source']}.nvbuffer2.clear()")
            self.safewrite(f"{s['source']}.trigger.count = {s['steps']}")
            self.safewrite(f"{s['source']}.trigger.arm.count = {s['repeat']}")
            self.safewrite(
                f"{s['source']}.trigger.source.linear{s['type']}({s['start']},{s['end']},{s['steps']})"
            )
            # FIXME: Might be a problem with datatypes, since start and end are strings.
            if s["type"] == "i":
                if abs(s["start"]) < 1.5 and abs(s["end"]) < 1.5:
                    self.safewrite(
                        f"{s['source']}.trigger.source.limitv = {s['limit']}"
                    )
                    self.safewrite(f"{s['source']}.source.limitv = {s['limit']}")
                else:
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
            else:
                if abs(s["limit"]) < 1.5:
                    self.safewrite(
                        f"{s['source']}.trigger.source.limiti = {s['limit']}"
                    )
                    self.safewrite(f"{s['source']}.source.limiti = {s['limit']}")
                else:
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

            self.safewrite(f"{s['source']}.source.output = {s['source']}.OUTPUT_ON")
            self.safewrite(f"{s['source']}.trigger.initiate()")
            time.sleep(waitDelay)

            buffer_prev = 0
            iv = []
            while True:
                if not self.busy():
                    self.safewrite(f"{s['source']}.abort()")
                    self.safewrite(
                        f"{s['source']}.source.output = {s['source']}.OUTPUT_OFF"
                    )
                    return iv

                self.safewrite(f"print({s['source']}.nvbuffer2.n)")
                buffern = int(s["handle"].read())

                if buffern >= s["steps"] * s["repeat"]:
                    break

                if buffern > buffer_prev:
                    self.safewrite(
                        f"printbuffer({buffern}, {buffern}, {s['source']}.nvbuffer1)"
                    )
                    i_tmp = float(s["handle"].read())
                    self.safewrite(
                        f"printbuffer({buffern}, {buffern}, {s['source']}.nvbuffer2)"
                    )
                    v_tmp = float(s["handle"].read())
                    iv.append((v_tmp, i_tmp))

                    if (s["type"] == "i" and abs(v_tmp) > 0.95 * abs(s["limit"])) or (
                        s["type"] == "v" and abs(i_tmp) > 0.95 * abs(s["limit"])
                    ):
                        self.safewrite(f"{s['source']}.abort()")
                        readsteps = buffern
                        break

                    buffer_prev = buffern

                time.sleep(0.5)

            time.sleep(waitDelay * 1.2)
            self.safewrite(f"{s['source']}.source.output = {s['source']}.OUTPUT_OFF")
            self.safewrite(f"printbuffer(1, {readsteps}, {s['source']}.nvbuffer1)")
            iv[:, 0] = [float(x) for x in s["handle"].read().split()]
            self.safewrite(f"printbuffer(1, {readsteps}, {s['source']}.nvbuffer2)")
            iv[:, 1] = [float(x) for x in s["handle"].read().split()]

            return iv



    def KeithleyRunDualChSweep(self, s: dict):
        readsteps = s['steps']
        waitDelay = float(s['pulse']) if s['pulse'] != "off" else 1

        self.safewrite(f"{s['source']}.nvbuffer1.clear()")
        self.safewrite(f"{s['source']}.nvbuffer2.clear()")
        self.safewrite(f"{s['drain']}.nvbuffer1.clear()")
        self.safewrite(f"{s['drain']}.nvbuffer2.clear()")
        self.safewrite(f"{s['source']}.trigger.count = {s['steps']}")
        self.safewrite(f"{s['source']}.trigger.arm.count = {s['repeat']}")
        self.safewrite(f"{s['drain']}.trigger.count = {s['steps']}")
        self.safewrite(f"{s['drain']}.trigger.arm.count = {s['repeat']}")
        self.safewrite(f"display.{s['drain']}.measure.func = display.MEASURE_DCAMPS")
        self.safewrite(
            f"{s['source']}.trigger.source.linear{s['type']}({s['start']},{s['end']},{s['steps']})"
        )

        if s['type'] == "i":
            if s['pulse'] == "off" or (abs(s['start']) < 1.5 and abs(s['end']) < 1.5):
                self.safewrite(f"{s['source']}.trigger.source.limitv = {s['limit']}")
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
            self.safewrite(f"display.{s['source']}.measure.func = display.MEASURE_DCVOLTS")
        else:
            if s['pulse'] == "off" or abs(s['limit']) < 1.5:
                self.safewrite(f"{s['source']}.trigger.source.limiti = {s['limit']}")
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
            self.safewrite(f"display.{s['source']}.measure.func = display.MEASURE_DCAMPS")
        # FIXME: check the what value is read into this value
        if s['drain']Voltage != "off":
            self.safewrite(f"{s['drain']}.source.func = {s['drain']}.OUTPUT_DCVOLTS")
            self.safewrite(f"{s['drain']}.source.levelv = {s['drain']Voltage}")
            self.safewrite(f"{s['drain']}.source.limiti = {s['drain']Limit}")
            drainLimitVoltage = float(s['drain']Limit)
        else:
            self.safewrite(f"{s['drain']}.source.func = {s['drain']}.OUTPUT_DCVOLTS")
            self.safewrite(f"{s['drain']}.source.levelv = 0")
            if s['type'] == "v" and s['limit'] > 1.5:
                self.safewrite(f"{s['drain']}.source.limiti = 1.5")
                drainLimitVoltage = 1.5
            else:
                self.safewrite(f"{s['drain']}.source.limiti = {s['limit']}")
                drainLimitVoltage = s['limit']
            if s['type'] == "i":
                self.safewrite(f"{s['drain']}.source.limiti = {s['end']}")
                drainLimitVoltage = s['end']

        self.safewrite(f"{s['source']}.source.output = {s['source']}.OUTPUT_ON")
        self.safewrite(f"{s['drain']}.source.output = {s['drain']}.OUTPUT_ON")
        self.safewrite(f"{s['drain']}.trigger.initiate()")
        self.safewrite(f"{s['source']}.trigger.initiate()")
        time.sleep(waitDelay)

        buffer_prev = 0

        while True:
            if running == 0:
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

            self.safewrite(f'print({s["source"]}.nvbuffer2.n)')
            buffern = int(smu_handle.read())

            if buffern >= s["steps"] * s["repeat"]:
                break

            if buffern > buffer_prev:
                self.safewrite(
                    f'printbuffer({buffern}, {buffern}, {s["source"]}.nvbuffer1)'
                )
                i_tmp_source = float(smu_handle.read())
                self.safewrite(
                    f'printbuffer({buffern}, {buffern}, {s["source"]}.nvbuffer2)'
                )
                v_tmp_source = float(smu_handle.read())
                self.safewrite(
                    f'printbuffer({buffern}, {buffern}, {s["drain"]}.nvbuffer1)'
                )
                i_tmp_drain = float(smu_handle.read())
                self.safewrite(
                    f'printbuffer({buffern}, {buffern}, {s["drain"]}.nvbuffer2)'
                )
                v_tmp_drain = float(smu_handle.read())

                if (
                    (s["type"] == "i" and abs(v_tmp_source) > 0.95 * abs(s["limit"]))
                    or (s["type"] == "v" and abs(i_tmp_source) > 0.95 * abs(s["limit"]))
                    or (abs(i_tmp_drain) > 0.95 * abs(drainLimitVoltage))
                ):
                    self.safewrite(f'{s["source"]}.abort()')
                    self.safewrite(f'{s["drain"]}.abort()')
                    break

                if buffer_prev == 0:
                    result_handles["resultTR_handle"] = plotAddNewCurve(
                        result_handles["resultTR_handle"], v_tmp_source, i_tmp_source, "-o"
                    )
                    result_handles["resultBL_handle"] = plotAddNewCurve(
                        result_handles["resultBL_handle"], v_tmp_drain, i_tmp_drain, "-o"
                    )
                    if i_tmp_source != 0:
                        result_handles["resultBR_handle"] = plotAddNewCurve(
                            result_handles["resultBR_handle"],
                            v_tmp_source,
                            i_tmp_drain / i_tmp_source,
                            "-o",
                        )
                    else:
                        result_handles["resultBR_handle"] = plotAddNewCurve(
                            result_handles["resultBR_handle"],
                            v_tmp_source,
                            i_tmp_drain / 1e-10,
                            "-o",
                        )
                else:
                    if buffern > buffer_prev:
                        iv_tmp_buf = []
                        self.safewrite(
                            f'printbuffer({buffern - buffer_prev}, {buffern}, {s["source"]}.nvbuffer1)'
                        )
                        iv_tmp_buf.append(float(smu_handle.read()))
                        self.safewrite(
                            f'printbuffer({buffern - buffer_prev}, {buffern}, {s["source"]}.nvbuffer2)'
                        )
                        iv_tmp_buf.append(float(smu_handle.read()))
                        self.safewrite(
                            f'printbuffer({buffern - buffer_prev}, {buffern}, {s["drain"]}.nvbuffer1)'
                        )
                        iv_tmp_buf.append(float(smu_handle.read()))
                        self.safewrite(
                            f'printbuffer({buffern - buffer_prev}, {buffern}, {s["drain"]}.nvbuffer2)'
                        )
                        iv_tmp_buf.append(float(smu_handle.read()))
                        stop_condition = IVinProc([iv_tmp_buf, save_filename])
                        if stop_condition:
                            self.safewrite(f'{s["source"]}.abort()')
                            self.safewrite(f'{s["drain"]}.abort()')
                            break

                    result_handles["resultTR_handle"] = updatePlotCurve(
                        result_handles["resultTR_handle"], v_tmp_source, i_tmp_source
                    )
                    result_handles["resultBL_handle"] = updatePlotCurve(
                        result_handles["resultBL_handle"], v_tmp_drain, i_tmp_drain
                    )
                    if i_tmp_source != 0:
                        result_handles["resultBR_handle"] = updatePlotCurve(
                            result_handles["resultBR_handle"],
                            v_tmp_source,
                            i_tmp_drain / i_tmp_source,
                        )
                    else:
                        result_handles["resultBR_handle"] = updatePlotCurve(
                            result_handles["resultBR_handle"],
                            v_tmp_source,
                            i_tmp_drain / 1e-10,
                        )

                buffer_prev = buffern

            time.sleep(0.5)

        time.sleep(0.1)
        time.sleep(waitDelay * 1.2)

        self.safewrite(f'print({s["source"]}.nvbuffer2.n)')
        readsteps = int(smu_handle.read())
        self.safewrite(f'{s["source"]}.source.output = {s["source"]}.OUTPUT_OFF')
        self.safewrite(f'{s["drain"]}.source.output = {s["drain"]}.OUTPUT_OFF')
        self.safewrite(f'printbuffer(1, {readsteps}, {s["source"]}.nvbuffer1)')
        iv = np.zeros((readsteps, 4))
        iv[:, 0] = [float(x) for x in smu_handle.read().split()]
        self.safewrite(f'printbuffer(1, {readsteps}, {s["source"]}.nvbuffer2)')
        iv[:, 1] = [float(x) for x in smu_handle.read().split()]
        self.safewrite(f'printbuffer(1, {readsteps}, {s["drain"]}.nvbuffer1)')
        iv[:, 2] = [float(x) for x in smu_handle.read().split()]
        self.safewrite(f'printbuffer(1, {readsteps}, {s["drain"]}.nvbuffer2)')
        iv[:, 3] = [float(x) for x in smu_handle.read().split()]
