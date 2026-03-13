"""
This is a GUI plugin for CCS175 spectrometer

This file should provide
- functions for interaction with other plugins (those that will be exported on get_functions hook call, these should not start with "_")
- functions that will implement functionality of the hooks (see pyIVLS_TLCCS)
- GUI functionality - code that interracts with Qt GUI elements from widgets

This plugin should have double functionality
(i) it may be independently used to run spectrometer preview and save individual spectra
(ii) it provides functionality of getting spectra for other plugins

Because of (i) it requires to send log and message signals, i.e. it is a child of QObject

IMPORTANT:
settings["integrationtime"] is in s
value of integrationtime in tlccs.ini is in s
value of integration time in settings comming from JSON from seqBuilder is the same as settings["integrationtime"], i.e. s
value of guessIntTime is in s
value of integration time in GUI is in ms

version 0.2
2025.03.07
ivarad

version 0.3
added spectrometerGetIntegrationTime
added auto detection for integration time
ivarad
2025.06.11

version 0.4
added spectrometerGetScan as a safer way to start a scan and get a spectrum

version 0.5
implemented hw trigger in auto time
2026 02 23
ivarad
"""

from typing import Optional
import TLCCS_const as const

import time
import os
import numpy as np
from datetime import datetime
from pathvalidate import is_valid_filename
from PyQt6 import uic
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtWidgets import QVBoxLayout, QFileDialog
from MplCanvas import MplCanvas
from threadStopped import ThreadStopped, thread_with_exception
from threading import Lock
import copy
from plugin_components import LoggingHelper, CloseLockSignalProvider
from TLCCS import CCSDRV


class TLCCS_GUI(QObject):
    """spectrometer plugin for pyIVLS"""

    non_public_methods = []  # add function names here, if they should not be exported as public to another plugins
    public_methods = [
        "parse_settings_preview",
        "parse_settings_widget",
        "set_gui_from_settings",
        "setSettings",
        "spectrometerConnect",
        "spectrometerDisconnect",
        "spectrometerSetIntegrationTime",
        "spectrometerGetIntegrationTime",
        "spectrometerStartScan",
        "spectrometerGetScan",
        "spectrometerGetSpectrum",
        "spectrometerTrigScan",
        "createFile",
        "getAutoTime",
    ]  # necessary for descendents of QObject, otherwise _get_public_methods returns a lot of QObject methods

    ########Signals

    #    filedelimeter = "\t"
    filedelimeter = ";"

    default_timerInterval = 0.020  # s, it is close to 24*2 fps (twice the standard for movies and TV)
    # limits for auto time detection
    autoTime_min = 0.004  # s, used to be 4
    autoTime_max = 30  # s, used to be 10000
    autoValue_min = 0.2  # spectrum value in arb.(?) units
    autoValue_max = 0.8  # spectrum value in arb.(?) units
    intTimeMaxIterations = 10

    ########Functions
    def __init__(self, verbose=False):
        super(QObject, self).__init__()
        self.verbose = True  # Enable verbose logging
        self.logger = LoggingHelper(self)
        self.closelock = CloseLockSignalProvider()
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        ##IRtothink#### I do not like have filename hardly coded,
        ############### but in any case the refrences to the GUI elements will be hardly coded, so it may be OK
        self.settingsWidget = uic.loadUi(self.path + "TLCCS_settingsWidget.ui")
        self.previewWidget = uic.loadUi(self.path + "TLCCS_MDIWidget.ui")

        # create the driver
        self.drv = CCSDRV()

        self._connect_signals()
        self._create_plt()

        self.lastspectrum = []  # data for saving from preview
        self.preview_running = False
        self.integrationTimeChanged = False
        self.scanRunning = False

        correction_file = r"SC175_correction"
        self.correction = np.loadtxt(self.path + correction_file)
        self.logger.log_debug(f"Loaded correction data from {correction_file} with shape {self.correction.shape}")
        self.settings = {}

        self._scan_lock = Lock()

    def _connect_signals(self):
        self.settingsWidget.connectButton.clicked.connect(self._connectAction)
        self.settingsWidget.disconnectButton.clicked.connect(self._disconnectAction)
        self.settingsWidget.setIntegrationTimeButton.clicked.connect(self._setIntTimeAction)
        self.settingsWidget.previewButton.clicked.connect(self._previewAction)
        self.settingsWidget.saveButton.clicked.connect(self._saveAction)
        self.settingsWidget.correctionCheck.stateChanged.connect(self._correctionChanged)
        self.settingsWidget.directoryButton.clicked.connect(self._getAddress)
        self.settingsWidget.getIntegrationTime_combo.currentIndexChanged.connect(self._integrationTime_mode_changed)
        self.settingsWidget.getTime_button.clicked.connect(self._getTimeAction)

    def _create_plt(self):
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.axes = self.sc.fig.add_subplot(111)

        self.axes.set_xlabel("Wavelength (nm)")
        self.axes.set_ylabel("Intensity (calib. arb. un.)")

        self.axes.set_xlim(const.CCS175_MIN_WV, const.CCS175_MAX_WV)  # limits are given by spectral range of the device

        layout = QVBoxLayout()
        layout.addWidget(self.sc._create_toolbar(self.previewWidget))
        layout.addWidget(self.sc)
        self.previewWidget.setLayout(layout)

    ########Functions
    ################################### internal

    def _update_spectrum(self):
        """Updates the spectrum in the preview window.

        Returns:
            _type_: _description_
        """
        [status, info] = self.spectrometerGetScan()
        if status:
            self.scanRunning = False
            return [status, info]
        if self.settings["usecorrection"]:
            preview_data = [m * n * 1000 for m, n in zip(info, self.correction[:, 1])]
        else:
            preview_data = info
        try:
            xmin, xmax = self.axes.get_xlim()
            ymin, ymax = self.axes.get_ylim()
            self.axes.cla()
            self.axes.set_xlabel("Wavelength (nm)")
            self.axes.set_ylabel("Intensity (calib. arb. un.)")
            self.axes.plot(self.correction[:, 0], preview_data, "b-")
            self.axes.set_xlim(xmin, xmax)
            self.axes.set_ylim(ymin, ymax)
            self.sc.draw()
            self.lastspectrum = [info, self.settings]
            return [0, [self.correction[:, 0], info]]
        except Exception as e:
            self.logger.log_debug(f"Error occurred while updating spectrum: {e}")
            return [3, self.lastspectrum]

    ########Functions
    ########GUI Slots

    def _connectAction(self):
        self.logger.log_debug("Attempting to connect to the spectrometer.")
        [status, info] = self.parse_settings_widget()
        if status:
            self.logger.log_debug(f"Failed to parse settings: {info}")
            self.logger.log_debug(datetime.now().strftime("%H:%M:%S.%f") + f" : TLCCS plugin : {info}, status = {status}")
            self.logger.log_info(f"TLCCS plugin : {info['Error message']}")
            return [status, info]
        [status, info] = self.spectrometerConnect()
        if status:
            self.logger.log_debug(f"Failed to connect to spectrometer: {info}")
            self.logger.log_debug(datetime.now().strftime("%H:%M:%S.%f") + f" : TLCCS plugin : {info}, status = {status}")
            self.logger.log_info(f"TLCCS plugin : {info['Error message']}")
            return [status, info]
        self._GUIchange_deviceConnected(True)  # see comment in _GUIchange_deviceConnected

    def _disconnectAction(self):
        self.logger.log_debug("Attempting to disconnect the spectrometer.")
        if self.preview_running:
            self.logger.log_debug("Cannot disconnect while preview is running.")
            self.logger.log_info("Stop preview before disconnecting")
        else:
            [status, info] = self.spectrometerDisconnect()
            if status:  ##IRtodo## some error handling is necessary, as connected devices will not allow to switch off the GUI
                self.logger.log_debug(f"Failed to disconnect spectrometer: {info}")
                self.logger.log_debug(datetime.now().strftime("%H:%M:%S.%f") + f" : TLCCS plugin : {info}, status = {status}")
                self.logger.log_info(f"TLCCS plugin : {info['Error message']}")
            self.logger.log_debug("Spectrometer disconnected successfully.")
            self._GUIchange_deviceConnected(False)  # see comment in _GUIchange_deviceConnected

    def _previewAction(self):
        # FIXME: The integration time seems to be Doubled. For example, with integ at 5 s, the logs show an update happening only every 10 s
        self.logger.log_debug("Preview button clicked.")
        if self.preview_running:
            self.logger.log_debug("Stopping preview. Waiting for scan to finish if in progress.")
            self.preview_running = False
            if hasattr(self, "run_thread") and self.run_thread.is_alive():
                self.run_thread.join(timeout=2)  # Wait up to 2 seconds for the thread to finish
            self._enableSaveButton()
            self.closelock.emit_close_lock(self.preview_running)
            self.settingsWidget.previewButton.setText("Preview")
        else:
            self.logger.log_debug("Starting preview.")
            [status, info] = self.parse_settings_preview()
            if status:
                self.logger.log_debug(f"Failed to parse preview settings: {info}")
                self.logger.log_debug(datetime.now().strftime("%H:%M:%S.%f") + f" : TLCCS plugin : {info}, status = {status}")
                self.logger.log_info(f"TLCCS plugin : {info['Error message']}")
                return [status, info]
            self.integrationTimeChanged = True
            self.preview_running = True
            self.closelock.emit_close_lock(self.preview_running)
            self.settingsWidget.saveButton.setEnabled(False)
            self.run_thread = thread_with_exception(self._previewIteration)
            self.run_thread.start()
            self.logger.log_debug("Preview started successfully.")
            self.settingsWidget.previewButton.setText("Stop preview")

    def _previewIteration(self):
        try:
            while self.preview_running:
                if self.integrationTimeChanged:
                    [status, info] = self.spectrometerSetIntegrationTime(self.settings["integrationtime"])
                    self.integrationTimeChanged = False
                    # FIXME: sleep_time currently unused for debugging
                    if self.settings["integrationtime"] < self.default_timerInterval:
                        self.sleep_time = self.default_timerInterval
                    else:
                        self.sleep_time = self.settings["integrationtime"]
                    if status:
                        self.logger.log_debug(datetime.now().strftime("%H:%M:%S.%f") + f" : TLCCS plugin : {info}, status = {status}")
                        self.logger.log_info(f"TLCCS plugin : {info['Error message']}")
                        self.preview_running = False
                        return [status, info]
                # time.sleep(self.sleep_time)
                [status, info] = self._update_spectrum()
                if status:
                    self.logger.log_debug(datetime.now().strftime("%H:%M:%S.%f") + f" : TLCCS plugin : {info}, status = {status}")
                    if not status == 1:
                        self.logger.log_info(f"TLCCS plugin : {info}")
                    self.preview_running = False
                    return [status, info]
            # If preview_running is set to False, finish the current scan and exit
            self.logger.log_debug("Preview stopped gracefully after finishing current scan.")
            return [0, "preview stopped"]
        except ThreadStopped:
            return [0, "preview stopped"]

    def _setIntTimeAction(self):
        if self.preview_running:  # this function is useful only in preview mode
            [status, info] = self._parse_settings_integrationTime()
            if status:
                self.logger.log_debug(datetime.now().strftime("%H:%M:%S.%f") + f" : TLCCS plugin : {info}, status = {status}")
                self.logger.log_info(f"TLCCS plugin : {info['Error message']}")
                return [status, info]
            self.integrationTimeChanged = True
            return [0, "OK"]

    def _saveAction(self):
        [status, info] = self._parseSaveData()
        if status:
            self.logger.log_info(f"TLCCS plugin : {info['Error message']}")
            return [status, info]
        varDict = {}
        varDict["integrationtime"] = self.lastspectrum[1]["integrationtime"]
        varDict["triggermode"] = 1 if self.lastspectrum[1]["externaltrigger"] else 0
        varDict["name"] = self.settings["samplename"]
        varDict["comment"] = self.settings["comment"]
        status, state = self.createFile(
            varDict,
            self.filedelimeter,
            address=self.settings["address"] + os.sep + self.settings["filename"] + ".csv",
            data=self.lastspectrum[0],
        )
        if status:
            self.logger.log_debug(f"Error occurred while saving file: {state}")
            self.logger.log_info(f"Error occurred while saving file: {state}")
            return [status, state]
        return [0, "OK"]

    def _getTimeAction(self):
        preview_status = False
        [status, info] = self._parse_settings_autoTime()
        if status:
            self.logger.log_debug(datetime.now().strftime("%H:%M:%S.%f") + f" : TLCCS plugin : {info}, status = {status}")
            self.logger.log_info(f"TLCCS plugin : {info['Error message']}")
            return [status, info]
        if self.preview_running:
            preview_status = self.preview_running
            self._previewAction()
        self.settingsWidget.saveButton.setEnabled(False)
        self.closelock.emit_close_lock(True)
        # check if get time may be used (spectrometer IDLE)
        statuses = self.drv.get_device_status()
        if "SCAN_IDLE" in statuses:
            status, autoTime = self.getAutoTime()
            if not status:
                self.settingsWidget.lineEdit_Integ.setText(f"{round(autoTime)}")
            if preview_status:
                self._previewAction()
            else:
                self.settingsWidget.saveButton.setEnabled(True)
            self.closelock.emit_close_lock(False)
            return [0, "OK"]
        else:
            self.closelock.emit_close_lock(False)
            return [
                4,
                {"Error message": "TLCCSGUI: spectrometer is not in IDLE state when setting auto integration time"},
            ]

    def getAutoTime(
        self,
        external_action=None,
        external_action_args=None,
        external_cleanup=None,
        external_cleanup_args=None,
        pause_duration: float = 0.0,
        last_integration_time: Optional[float] = None,
    ) -> tuple[int, float | dict]:
        """
        Calculates the optimal integration time, allowing external actions and cleanup with arguments.

        Args:
            external_action (callable): External function to execute during auto time calculation.
            external_action_args (tuple): Arguments for the external action.
            external_cleanup (callable): External cleanup function to execute after auto time calculation.
            external_cleanup_args (tuple): Arguments for the external cleanup function.
            pause_duration (float): Duration to pause after each iteration.

        Returns:
            tuple[int, float | dict]: Status and integration time or error information.
        """
        self.logger.log_debug("Calculating auto integration time.")
        low = self.autoTime_min# time min s
        high = self.autoTime_max# time max s
        low_spectrum = self.autoValue_min  # min spectrum value
        high_spectrum = self.autoValue_max  # max spectrum value

        if self.settings["integrationtimetype"] == "auto":
            # initial guess for time if not provided
            if last_integration_time is None:
                if self.settings["useintegrationtimeguess"]:
                    # guess from current value
                    guessIntTime = self.settings["integrationtime"] #s
                else:
                    # guess from min and max
                    guessIntTime = (self.autoTime_min + self.autoTime_max) / 2 #s
            # initial guess provided as argument, use that.
            else:
                guessIntTime = last_integration_time # ms

            # start iterating through integration times using guessIntTime as initial guess
            for iter in range(self.intTimeMaxIterations):
                self.logger.log_debug(f"Iteration {iter + 1}: Current guess = {guessIntTime} s.")
                self.settings["integrationtime"] = guessIntTime# needed for keeping self.lastspectrum in order
                [status, info] = self.spectrometerSetIntegrationTime(guessIntTime)  # s
                if status:
                    self.logger.log_debug(f"getAutoTime: Failed to set integration time. {status}, {info}")
                    return [status, info]
                # charging the spectrometer in case of external trigger
                if self.settings["externaltrigger"]:
                    self.logger.log_debug("Charging a new  HW trig scan.")
                    self.drv.start_scan_ext_trigger()
                    time.sleep(0.02) #just a precaution, duration does not mean anything specific, does not affect the measurement as smu is off
                    mydict = external_action_args[0]
                    mydict['integrationtime'] = guessIntTime #in s
                # external action if needed
                if external_action:
                    self.logger.log_debug("getAutoTime: Executing external action.")
                    try:
                        if external_action_args:
                            status, info = external_action(*external_action_args)
                        else:
                            status, info = external_action()
                        if status:
                            self.logger.log_debug(f"getAutoTime: External action failed. {status}, {info}")
                            return status, info
                    except TypeError:
                        self.logger.log_debug("getAutoTime: External action completed without standard return value")

                [status, info] = self._update_spectrum()
                self.logger.log_debug(f"getAutoTime: Retrieved spectrum with shape {info[1].shape} and max value {max(info[1])}.")
                if status:
                    self.logger.log_debug(f"getAutoTime: Failed to update spectrum. {status}, {info}")
                    return (status, info)
                # save the spectrum if needed
                if self.settings["saveattempts_check"]:
                    varDict = {}
                    varDict["integrationtime"] = guessIntTime
                    varDict["triggermode"] = 1 if self.settings["externaltrigger"] else 0
                    varDict["name"] = self.settings["samplename"]
                    varDict["comment"] = self.settings["comment"] + " Auto adjust of integration time."
                    status, state = self.createFile(
                        varDict=varDict,
                        filedelimeter=self.filedelimeter,
                        address=self.settings["address"] + os.sep + self.settings["filename"] + f"_{int(guessIntTime)}ms.csv",
                        data=info[1],
                    )
                    if status:
                        self.logger.log_debug(f"getAutoTime: Failed to save spectrum. {status}, {state}")
                        self.logger.log_info(f"Failed to save spectrum during auto integration time calculation: {state}")
                        return (status, state)
                # external cleanup if needed
                if external_cleanup:
                    self.logger.log_debug("getAutoTime: Executing external cleanup.")
                    try:
                        if external_cleanup_args:
                            status, info = external_cleanup(*external_cleanup_args)
                        else:
                            status, info = external_cleanup()
                        if status:
                            self.logger.log_debug(f"getAutoTime: External cleanup failed. {status}, {info}")
                    except TypeError:
                        self.logger.log_debug("getAutoTime: External cleanup completed without standard return value")
                # pause if needed
                if pause_duration > 0:
                    self.logger.log_debug(f"getAutoTime: Pausing for {pause_duration} seconds.")
                    time.sleep(pause_duration)

                target = max(info[1])  # target value to optimize
                # if spectrum is in the range, found good integration time
                if low_spectrum <= target <= high_spectrum:
                    self.logger.log_debug(f"Optimal integration time found: {guessIntTime} seconds.")
                    return [0, guessIntTime]  # return in seconds
                # if spectrum is below the range, increase integration time
                if target < low_spectrum:
                    self.logger.log_debug(f"Spectrum value {target} is below the range ({low_spectrum}), increasing integration time.")
                    if guessIntTime >= high:
                        self.logger.log_debug(f"Integration time is too high, returning: {guessIntTime} seconds.")
                        return [1, {"Error message": "Integration time too high"}]
                    low = guessIntTime
                # if spectrum is above the range, decrease integration time
                else:
                    self.logger.log_debug(f"Spectrum value {target} is above the range ({high_spectrum}), decreasing integration time.")
                    if guessIntTime <= low:
                        self.logger.log_debug(f"Integration time is too low, returning: {guessIntTime} seconds.")
                        return [1, {"Error message": "Integration time too low"}]
                    high = guessIntTime
                # Compute new guess in milliseconds, rounded to nearest millisecond
                guessIntTime = int(round((low + high) / 2))

            self.logger.log_debug(f"Auto integration time calculation completed: {guessIntTime} seconds.")
            return [0, guessIntTime]  # return in seconds
        else:
            self.logger.log_debug("Integration time mode is not set to auto, cannot calculate auto integration time.")
            return [
                1,
                {"Error message": "TLCCSGUI: integration time mode is not set to auto"},
            ]  # error if not auto mode

    ########Functions
    ###############GUI setting up

    def _initGUI(self, plugin_info: dict):
        """Initializes the GUI with the given plugin information.

        Args:
            plugin_info (dict):  dictionary with settings obtained from plugin_data in pyIVLS_*_plugin
        """
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK
        self.logger.log_debug(f"Initializing GUI with plugin_info: {plugin_info}")
        self.settings.update(plugin_info)
        self.settings = {key.lower(): value for key, value in self.settings.items()}

        self.set_gui_from_settings()
        return 0

    def set_gui_from_settings(self) -> None:
        """
        Updates the GUI fields based on the provided settings dictionary.

        Args:
            settings (dict): Dictionary containing settings to update the GUI.
        """

        def to_bool(value):
            """
            Helper function to make sure that the "True"|"False" values from ini files or JSON structures are bool.

            Args:
                value bool or str "True"|"False"

            Returns:
                bool: True if the value (str)"True" or (bool)True
            """

            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.strip().lower() == "true"
            return False

        def set_combobox_value(combobox, value):
            """
            Helper function to set the value of a QComboBox in a case-insensitive manner.

            Args:
                combobox (QComboBox): The combobox to set the value for.
                value (str): The value to set.

            Returns:
                bool: True if the value was found and set, False otherwise.
            """
            self.logger.log_debug(f"Setting combobox {combobox.objectName()} to value: {value}")
            index = combobox.findText(value, Qt.MatchFlag.MatchFixedString)
            if index != -1:
                combobox.setCurrentIndex(index)
                return True
            return False

        self.logger.log_debug(f"populating GUI from settings")
        # values from autoTime settings
        set_combobox_value(self.settingsWidget.getIntegrationTime_combo, self.settings["integrationtimetype"])
        self.settings["saveattempts_check"] = to_bool(self.settings["saveattempts_check"])
        self.settingsWidget.saveAttempts_check.setChecked(self.settings["saveattempts_check"])
        self.settings["useintegrationtimeguess"] = to_bool(self.settings["useintegrationtimeguess"])
        self.settingsWidget.useIntegrationTimeGuess_check.setChecked(self.settings["useintegrationtimeguess"])

        # values from saveData settings
        self.settingsWidget.lineEdit_path.setText(self.settings["address"])
        self.settingsWidget.lineEdit_filename.setText(self.settings["filename"])
        self.settingsWidget.lineEdit_sampleName.setText(self.settings["comment"])
        ##IRtodo## temporary compatability issue. Should be removed or adjusted in a systematic way
        self.settings["externaltrigger"] = to_bool(self.settings["externaltrigger"])
        self.settingsWidget.extTriggerCheck.setChecked(self.settings["externaltrigger"])
        self.settingsWidget.lineEdit_sampleName.setText(self.settings["samplename"])

        #values from integrationTime settings
        try:
            self.settingsWidget.lineEdit_Integ.setText(f"{float(self.settings["integrationtime"])*1000}")
        except:
            self.logger.log_warn(f"Setting GUI from settings conversion failed. integrationtime is set as it is in settings")
            self.settingsWidget.lineEdit_Integ.setText(f"{self.settings["integrationtime"]}")

        # values from spectrumCorrection
        self.settings["usecorrection"] = to_bool(self.settings["usecorrection"])
        self.settingsWidget.correctionCheck.setChecked(self.settings["usecorrection"])

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

    def _GUIchange_deviceConnected(self, status):
        # NOTE: status is direct, i.e. when spectrometer is connected received status should True, when disconnected status should be False
        if status:
            self.settingsWidget.connectionIndicator.setStyleSheet("border-radius: 10px; background-color: rgb(38, 162, 105); min-height: 20px; min-width: 20px;")
        else:
            self.settingsWidget.connectionIndicator.setStyleSheet("border-radius: 10px; background-color: rgb(165, 29, 45); min-height: 20px; min-width: 20px;")
        self.settingsWidget.setIntegrationTimeButton.setEnabled(status)
        self.settingsWidget.previewBox.setEnabled(status)
        if status:
            self._integrationTime_mode_changed()
        self.settingsWidget.disconnectButton.setEnabled(status)
        self.settingsWidget.connectButton.setEnabled(not status)

    def _enableSaveButton(self):
        if not self.lastspectrum:
            self.settingsWidget.saveButton.setEnabled(False)
        else:
            self.settingsWidget.saveButton.setEnabled(True)
        if not self.lastspectrum:
            self.settingsWidget.saveButton.setEnabled(False)
        else:
            self.settingsWidget.saveButton.setEnabled(True)

    def _correctionChanged(self, int):
        if self.preview_running:  # this function is useful only in preview mode
            self.settings["usecorrection"] = self._parse_spectrumCorrection()

    def _integrationTime_mode_changed(self):
        integrationTimeMode = self.settingsWidget.getIntegrationTime_combo.currentText()
        if integrationTimeMode == "manual":
            self.settingsWidget.autoIntegrationTime_box.setEnabled(False)
            self.settingsWidget.getTime_button.setEnabled(False)
        else:
            self.settingsWidget.autoIntegrationTime_box.setEnabled(True)
            self.settingsWidget.getTime_button.setEnabled(True)

    ########Functions
    ########plugins interraction

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

    def _getLogSignal(self):
        return self.logger.logger_signal

    def _getInfoSignal(self):
        return self.logger.info_popup_signal

    def _getCloseLockSignal(self):
        return self.closelock.closeLock

    def _parse_settings_integrationTime(self) -> tuple[int, dict]:
        """
        Parses the integration time from the GUI line edit and stores it in the settings dictionary.

        stored in self.settings["integrationtime"] as float in seconds

        Returns:
            list: [0, "OK"] on success, or [1, {"Error message": ...}] on error.
        """
        try:
            self.settings["integrationtime"] = float(self.settingsWidget.lineEdit_Integ.text())/1000
        except ValueError:
            return [1, {"Error message": "Value error in TLCCS plugin: integration time field should be a number"}]
        if self.settings["integrationtime"] > const.CCS_SERIES_MAX_INT_TIME:
            return [
                1,
                {"Error message": f"Value error in TLCCS plugin: integration time should can not be greater than maximum integration time {const.CCS_SERIES_MAX_INT_TIME} s"},
            ]
        if self.settings["integrationtime"] < 0.001:
            return [
                1,
                {"Error message": "Value error in TLCCS plugin: integration time should can not be smaller than 1 ms"},
            ]
        return [0, "OK"]

    def _parse_settings_autoTime(self) -> tuple[int, dict]:
        self.settings["integrationtimetype"] = self.settingsWidget.getIntegrationTime_combo.currentText()
        self.settings["saveattempts_check"] = self.settingsWidget.saveAttempts_check.isChecked()
        self.settings["useintegrationtimeguess"] = self.settingsWidget.useIntegrationTimeGuess_check.isChecked()
        if self.settings["saveattempts_check"]:
            [status, info] = self._parseSaveData()
            if status:
                return [status, info]
        if self.settings["useintegrationtimeguess"]:
            [status, info] = self._parse_settings_integrationTime()
            if status:
                return [status, info]

        return [0, "OK"]

    def _parse_spectrumCorrection(self):
        if self.settingsWidget.correctionCheck.isChecked():
            return True
        else:
            return False

    def _parseSaveData(self) -> tuple[int, dict]:
        self.settings["address"] = self.settingsWidget.lineEdit_path.text()
        if not os.path.isdir(self.settings["address"] + os.sep):
            self.logger.log_debug(datetime.now().strftime("%H:%M:%S.%f") + " : TLCCS plugin : address string should point to a valid directory")
            return [1, {"Error message": "TLCCS plugin : address string should point to a valid directory"}]
        self.settings["filename"] = self.settingsWidget.lineEdit_filename.text()
        if not is_valid_filename(self.settings["filename"]):
            self.logger.log_debug(datetime.now().strftime("%H:%M:%S.%f") + " : TLCCS plugin : filename is not valid")
            self.logger.log_info("TLCCS plugin : filename is not valid")
            return [1, {"Error message": "TLCCS plugin : filename is not valid"}]

        self.settings["samplename"] = self.settingsWidget.lineEdit_sampleName.text()
        self.settings["comment"] = self.settingsWidget.lineEdit_comment.text()
        self.settings["externaltrigger"] = self.settingsWidget.extTriggerCheck.isChecked()  # this is here since this is written into the header

        return [0, {"Error message": "OK"}]

    def parse_settings_preview(self) -> tuple[int, dict]:
        """Parses the settings widget for the spectrometer. Extracts current values

        Returns:
            0 - no error
            ~0 - error (add error code later on if needed)
        """
        self.settings = {}
        [status, info] = self._parse_settings_autoTime()
        if status:
            return [status, info]
        if not self.settings["useintegrationtimeguess"]:
            [status, info] = self._parse_settings_integrationTime()
            if status:
                return [status, info]
        if not self.settings["saveattempts_check"]:
            [status, info] = self._parseSaveData()
            if status:
                return [status, info]
        if self.settingsWidget.extTriggerCheck.isChecked():
            self.settings["externaltrigger"] = True
        else:
            self.settings["externaltrigger"] = False
        self.settings["usecorrection"] = self._parse_spectrumCorrection()
        self.settings["autoTime_min"] = self.autoTime_min
        self.settings["autoTime_max"] = self.autoTime_max
        self.settings["autoValue_min"] = self.autoValue_min
        self.settings["autoValue_max"] = self.autoValue_max
        self.settings["intTimeMaxIterations"] = self.intTimeMaxIterations
        return [0, self.settings]

    def parse_settings_widget(self) -> tuple[int, dict]:
        """Parses the settings widget for the spectrometer. Extracts current values

        Returns:
            0 - no error
            ~0 - error (add error code later on if needed)
        """
        self.settings = {}
        [status, info] = self._parse_settings_autoTime()
        if status:
            return [status, info]
        if not self.settings["useintegrationtimeguess"]:
            [status, info] = self._parse_settings_integrationTime()
            if status:
                return [status, info]
        if not self.settings["saveattempts_check"]:
            [status, info] = self._parseSaveData()
            if status:
                return [status, info]
        if self.settingsWidget.extTriggerCheck.isChecked():
            self.settings["externaltrigger"] = True
        else:
            self.settings["externaltrigger"] = False
        self.settings["usecorrection"] = self._parse_spectrumCorrection()
        # duplicate value for spectrum correction since i don't want to break anything now. This is used to save the value to the ini.

        return [0, self.settings]

    def setSettings(self, settings):  #### settings from external call
        self.settings = {}
        self.settings = copy.deepcopy(settings)
        self.settings = {key.lower(): value for key, value in self.settings.items()}

#    def get_current_gui_settings(self):
#        """Reads the current settings from the settingswidget, returns a dict.
#        Returns:
#            tuple: (status, settings_dict)
#        """
#        [status, info] = self.parse_settings_widget()
#        if status:
#            return [status, info]
#        retset = self.settings.copy()
#        retset["integrationtime"] = int(self.settings["integrationtime"] * 1000)
#        return [0, retset]

    ########Functions
    ########device functions
    def spectrometerConnect(self, integrationTime=None):
        self.logger.log_debug(f"Connecting to spectrometer with integration time: {integrationTime}")
        if integrationTime:
            self.settings["integrationtime"] = integrationTime
        try:
            status = self.drv.open(const.CCS175_VID, const.CCS175_PID, self.settings["integrationtime"])
            if not status:
                self.logger.log_debug("Connection to spectrometer failed.")
                self.logger.log_debug(datetime.now().strftime("%H:%M:%S.%f") + " : TLCCS plugin : can not connect to spectrometer")
                self.logger.log_info("TLCCS plugin : can not connect to spectrometer")
                return [4, {"Error message": "Can not connect to spectrometer"}]
            self.logger.log_debug("Spectrometer connected successfully.")
            return [0, "OK"]
        except Exception as e:
            self.logger.log_debug(f"Exception during connection: {e}")
            return [4, {"Error message": f"{e}"}]

    def spectrometerDisconnect(self):
        self.logger.log_debug("Disconnecting spectrometer.")
        try:
            self.drv.close()
            self.logger.log_debug("Spectrometer disconnected successfully.")
            return [0, "OK"]
        except Exception as e:
            self.logger.log_debug(f"Exception during disconnection: {e}")
            return [4, {"Error message": "Can not disconnect the spectrometer"}]

    def spectrometerSetIntegrationTime(self, integrationTime):
        try:
            self.logger.log_debug(f"Setting integration time to {integrationTime} seconds.")
            self.drv.set_integration_time(integrationTime)
            # single scan to make sure the time is correctly set
            self.drv.start_scan()
            self.drv.get_scan_data()

            return [0, "OK"]
        except ThreadStopped:
            pass
        except Exception as e:
            return [4, {"Error message": f"{e}"}]

    def spectrometerGetIntegrationTime(self):
        # return current integration time in seconds
        try:
            intTime = self.drv.get_integration_time()
            return [0, intTime]
        except ThreadStopped:
            pass
        except Exception as e:
            return [4, {"Error message": f"{e}"}]

    def spectrometerTrigScan(self):
        # arm the spectrometer to perform a scan on external trigger
        try:
            self.drv.start_scan_ext_trigger()
            return [0, "OK"]
        except ThreadStopped:
            pass
        except Exception as e:
            return [4, {"Error message": f"{e}"}]

    def spectrometerStartScan(self):
        """Starts a spectro scan

        Returns:
            _type_: _description_
        """
        self.logger.log_debug("Starting spectrometer scan.")
        try:
            if self.scanRunning:
                self.logger.log_debug("Scan is already running.")
                self.logger.log_debug(f"Device status: {self.drv.get_device_status()}")
                return [1, {"Error message": "Scan is already running"}]

            self.drv.start_scan()
            self.scanRunning = True
            self.logger.log_debug("Spectrometer scan started successfully.")
            self.logger.log_debug(f"Device status: {self.drv.get_device_status()}")
            return [0, "OK"]
        except ThreadStopped:
            return [0, "ThreadStopped"]
        except Exception as e:
            self.logger.log_debug(f"Exception during scan start: {e}")
            return [4, {"Error message": "Can not start scan"}]

    def spectrometerGetSpectrum(self):
        """Reads the spectrum from the spectrometer, waits for the scan to finish if necessary.

        Returns:
            _type_: _description_
        """
        self.logger.log_debug("Getting spectrum from spectrometer.")
        self.logger.log_debug(f"Device status: {self.drv.get_device_status()}")

        try:
            while self.scanRunning:
                if "SCAN_TRANSFER" not in self.drv.get_device_status():
                    self.logger.log_debug("Waiting for scan to finish.")
                    time.sleep(self.settings["integrationtime"])
                else:
                    break
            if not self.scanRunning:
                self.logger.log_debug("Scan stopped before completion.")
                return [1, {"Error message": "Scan stopped"}]
            else:
                self.logger.log_debug("Spectrum retrieved successfully.")
                return [0, self.drv.get_scan_data()]
        except ThreadStopped:
            pass
        except Exception as e:
            self.logger.log_debug(f"Exception during spectrum retrieval: {e}")
            self.scanRunning = False
            return [4, {"Error message": "Can not get spectrum"}]

    def spectrometerGetScan(self):
        """Atomically get a spectrum to prevent weird behavior when a scan is already running."""
        # with self._scan_lock:
        try:
            self.logger.log_debug("combined start / fetch to get spectrum")
            # No scan running, start a new scan
            if not self.settings["externaltrigger"]:
                self.logger.log_debug("Starting a new scan.")
                self.drv.start_scan()
            else:
                self.logger.log_debug("External trigger should be already charged before, only reading the data out")
            self.logger.log_debug(f"Device status: {self.drv.get_device_status()} directly after scan start")
            data = self.drv.get_scan_data()
            self.logger.log_debug(f"Device status immediately after calling get_scan_data: {self.drv.get_device_status()}")
            self.logger.log_debug(f"Scan data shape: {data.shape}, max value: {max(data)}")
            self.scanRunning = False
            return [0, data]
        except ThreadStopped:
            return [0, "ThreadStopped"]
        except Exception as e:
            return [4, {"Error message": f"Can not get scan: {e}"}]

    ########Functions
    ###############save data

    def createFile(self, varDict, filedelimeter, address, data):
        fileheader = self._spectrometerMakeHeader(varDict, separator=filedelimeter)
        self.logger.log_debug(f"Creating file at {address} with data shape {data.shape}")
        self.logger.log_debug(f"Correction data has shape {self.correction.shape}")
        if os.path.exists(address):
            self.logger.log_debug(f"File {address} already exists")
            self.logger.log_info(f"File {address} already exists, choose a different name or address.")
            return (1, {"Error message": f"File {address} already exists"})

        np.savetxt(
            address,
            list(zip(self.correction[:, 0], data)),
            fmt="%.9e",
            delimiter=filedelimeter,
            newline="\n",
            header=fileheader,
            footer="#[EndOfFile]",
            comments="#",
        )
        return (0, {})

    def _spectrometerMakeHeader(self, varDict={}, separator=";"):
        ###following the structure of files generated by Thorlabs software
        ### a part of values are just const, they may be replaces with real values
        #
        # structure of the varDict
        #
        # varDict['average'] - int:averaging
        # varDict['integrationtime'] - float:integration time in seconds
        # varDict['triggermode'] - external trigger = 1 / internal = 0
        # varDict['name'] - str:sample name
        # varDict['comment'] - str:comment
        comment = "Thorlabs FTS operated by pyIVSL\n"
        comment = f"{comment}#[SpectrumHeader]\n"
        comment = f"{comment}Date{separator}{datetime.now().strftime('%Y%m%d')}\n"
        comment = f"{comment}Time{separator}{datetime.now().strftime('%H%M%S%f')[:-4]}\n"
        comment = f"{comment}GMTTime{separator}{datetime.utcnow().strftime('%H%M%S%f')[:-4]}\n"
        comment = f"{comment}XAxisUnit{separator}nm_air\n"
        comment = f"{comment}YAxisUnit{separator}intensity\n"
        if "average" in varDict:
            comment = f"{comment}Average{separator}{varDict['average']}\n"
        else:
            comment = f"{comment}Average{separator}0\n"
        comment = f"{comment}RollingAverage{separator}0\n"
        comment = f"{comment}SpectrumSmooth{separator}0\n"
        comment = f"{comment}SSmoothParam1{separator}0\n"
        comment = f"{comment}SSmoothParam2{separator}0\n"
        comment = f"{comment}SSmoothParam3{separator}0\n"
        comment = f"{comment}SSmoothParam4{separator}0\n"
        comment = f"{comment}IntegrationTime{separator}{varDict['integrationtime']}\n"
        comment = f"{comment}TriggerMode{separator}{varDict['triggermode']}\n"
        comment = f"{comment}InterferometerSerial{separator}M00903839\n"
        comment = f"{comment}Source\n"
        comment = f"{comment}AirMeasureOpt{separator}0\n"
        comment = f"{comment}WnrMin{separator}0\n"
        comment = f"{comment}WnrMax{separator}0\n"
        comment = f"{comment}Length{separator}3648\n"
        comment = f"{comment}Resolution{separator}0\n"
        comment = f"{comment}ADC{separator}0\n"
        comment = f"{comment}Instrument{separator}0\n"
        comment = f"{comment}Model{separator}CCS175\n"
        comment = f"{comment}Type{separator}emission\n"
        comment = f"{comment}AirTemp{separator}0\n"
        comment = f"{comment}AirPressure{separator}0\n"
        comment = f"{comment}AirRelHum{separator}0\n"
        if "name" in varDict:
            comment = f"{comment}Name{separator}{varDict['name']}\n"
        else:
            comment = f"{comment}Name{separator}\n"
        if "comment" in varDict:
            comment = f'{comment}Comment{separator}"{varDict["comment"]}"\n'
        else:
            comment = f'{comment}Comment{separator} ""\n'
        comment = f"{comment}#[Data]\n"
        return comment
