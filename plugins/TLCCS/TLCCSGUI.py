# TODO: Add checks that return value errors if public functions are called while preview is happening.

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
from pathvalidate import is_valid_filename
from PyQt6 import uic
from PyQt6.QtCore import QObject, pyqtSignal, Qt, QTimer, pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout, QFileDialog
from MplCanvas import MplCanvas
import copy
from worker_thread import WorkerThread
from plugin_components import public, get_public_methods, LoggingHelper, ConnectionIndicatorStyle, FileManager
from TLCCS import CCSDRV


class TLCCS_GUI(QObject):
    """spectrometer plugin for pyIVLS"""

    ########Signals
    closeLock = pyqtSignal(bool)
    connectionStateChanged = pyqtSignal(bool)  # signal to update state of connection
    data_recieved_signal = pyqtSignal(list)  # signal emitted when new data is received, list includes [wavelengths, intensities]

    # class variables
    #    filedelimeter = "\t"
    filedelimeter = ";"
    default_timerInterval = 20  # ms, it is close to 24*2 fps (twice the standard for movies and TV)
    # limits for auto time detection
    autoTime_min = 0.004  # s, used to be 4
    autoTime_max = 30  # s, used to be 10000
    autoValue_min = 0.2  # spectrum value in arb.(?) units
    autoValue_max = 0.8  # spectrum value in arb.(?) units
    intTimeMaxIterations = 10

    @property
    def settingsWidget(self):
        if self._settingsWidget is None:
            raise RuntimeError("Settings widget not initialized.")
        return self._settingsWidget

    @property
    def previewWidget(self):
        if self._previewWidget is None:
            raise RuntimeError("Preview widget not initialized.")
        return self._previewWidget

    def notify_user(self, message: str):
        """Utility to create popup and corresponding log entry for events that should be clearly visible"""
        self.logger.log_info(message)
        self.logger.info_popup(message)

    def log_verbose(self, message: str) -> None:
        self.logger.log_info(message)

    ########Functions
    def __init__(self):
        super(QObject, self).__init__()
        # Load the ui files based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        self._settingsWidget = None
        self._previewWidget = None
        self._settingsWidget = uic.loadUi(self.path + "TLCCS_settingsWidget.ui")  # type: ignore
        self._previewWidget = uic.loadUi(self.path + "TLCCS_MDIWidget.ui")  # type: ignore

        # create the driver
        self.drv = CCSDRV()

        # create fm for saving files
        self.fm = FileManager()

        self._connect_signals()
        self._create_plt()

        # instance variables
        self.lastspectrum = []  # data for saving from preview
        self.preview_running = False
        self.integrationTimeChanged = False
        self.auto_time_thread = None
        self._gettime_preview_status = False
        self._auto_time_result_handled = False

        # load correction file and init settings
        correction_file = r"SC175_correction"
        self.correction = np.loadtxt(self.path + correction_file)
        self.settings = {}

        # logger
        self.logger = LoggingHelper(self)

        # timer-based preview
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(False)
        self._preview_timer.timeout.connect(self._on_preview_tick)

    def _connect_signals(self):
        """Connect GUI signals to their respective slots."""
        self.settingsWidget.connectButton.clicked.connect(self.spectrometerConnect)
        self.settingsWidget.disconnectButton.clicked.connect(self.spectrometerDisconnect)
        self.settingsWidget.setIntegrationTimeButton.clicked.connect(self._setIntTimeAction)
        self.settingsWidget.previewButton.clicked.connect(self._previewAction)
        self.settingsWidget.saveButton.clicked.connect(self._saveAction)
        self.settingsWidget.correctionCheck.stateChanged.connect(self._correctionChanged)
        self.settingsWidget.directoryButton.clicked.connect(self._getAddress)
        self.settingsWidget.getIntegrationTime_combo.currentIndexChanged.connect(self._integrationTime_mode_changed)
        self.settingsWidget.getTime_button.clicked.connect(self._getTimeAction)
        # https://stackoverflow.com/questions/11476267/segmentation-fault-while-emitting-signal-from-other-thread-in-qt
        # if facing the dreaded segfault again, chekc the type of connection since we are not threading with qthread
        self.connectionStateChanged.connect(self._GUIchange_deviceConnected)
        self.data_recieved_signal.connect(self._on_data_recieved)

    def _create_plt(self):
        """Inits the matplotlib canvas in the preview widget."""
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

    def _render_preview(self, intensities):
        """Render the preview plot given intensities array."""
        if self.settings.get("previewCorrection", False):
            preview_data = [m * n * 1000 for m, n in zip(intensities, self.correction[:, 1])]
        else:
            preview_data = intensities

        xmin, xmax = self.axes.get_xlim()
        ymin, ymax = self.axes.get_ylim()
        self.axes.cla()
        self.axes.set_xlabel("Wavelength (nm)")
        self.axes.set_ylabel("Intensity (calib. arb. un.)")
        self.axes.plot(self.correction[:, 0], preview_data, "b-")
        self.axes.set_xlim(xmin, xmax)
        self.axes.set_ylim(ymin, ymax)
        self.sc.draw()
        self.lastspectrum = [intensities, self.settings]
        return [0, [self.correction[:, 0], intensities]]

    @pyqtSlot(list)
    def _on_data_recieved(self, payload: list):
        """Slot for data_recieved_signal. Payload: [wavelengths, intensities]."""
        try:
            if not isinstance(payload, (list, tuple)) or len(payload) != 2:
                return
            wavelengths, intensities = payload
            # render with existing logic
            self._render_preview(intensities)
        except Exception as e:
            self.log_verbose(f"Failed updating preview from signal: {e}")

    ########Functions
    ########GUI Slots

    def _previewAction(self) -> tuple[int, dict]:
        self.log_verbose("Preview button clicked.")
        if self.preview_running:
            self.preview_running = False
            if self._preview_timer.isActive():
                self._preview_timer.stop()
            # stop automatic scanning by issuing a command that isnt a fetch for data or status
            _ = self.drv.get_integration_time()

            statuses = self.drv.get_device_status()
            if "SCAN_TRANSFER" in statuses or "SCAN_TRIGGERED" in statuses:
                # read leftover data
                self.log_verbose("Reading leftover data after stopping preview: statuses: " + str(statuses))
                self.spectrometerGetSpectrum()
                statuses_after = self.drv.get_device_status()
                self.log_verbose("Statuses after reading leftover data: " + str(statuses_after))

            self._enableSaveButton()
            self.closeLock.emit(self.preview_running)
            self.settingsWidget.previewButton.setText("Preview")
            return (0, {})
        else:
            self.log_verbose("Starting preview.")
            [status, info] = self.parse_settings_preview()
            if status:
                self.notify_user("Failed to parse preview settings: " + str(info))
                return (status, info)

            self.integrationTimeChanged = True
            self.preview_running = True
            self.closeLock.emit(self.preview_running)
            self.settingsWidget.saveButton.setEnabled(False)
            # request continous scan start from dev
            self.drv.start_scan_continuous()

            integration_ms = int(self.settings["integrationtime"] * 1000)
            interval_ms = int(max(self.default_timerInterval, integration_ms))
            self._preview_timer.start(interval_ms)
            self.log_verbose(f"Preview started with timer interval {interval_ms} ms.")
            self.settingsWidget.previewButton.setText("Stop preview")

            return (0, {})

    def _setIntTimeAction(self):
        if self.preview_running:  # this function is useful only in preview mode
            [status, info] = self._parse_settings_integrationTime()
            if status:
                self.notify_user("Failed to parse integration time settings: " + str(info))
                return [status, info]
            self.integrationTimeChanged = True
            return [0, "OK"]

    def _saveAction(self):
        [status, info] = self._parseSaveData()
        if status:
            self.notify_user("TLCCS plugin : " + str(info["Error message"]))
            return [status, info]
        varDict = {}
        varDict["integrationtime"] = self.lastspectrum[1]["integrationtime"]
        varDict["triggermode"] = 1 if self.lastspectrum[1]["externalTrigger"] else 0
        varDict["name"] = self.settings["samplename"]
        varDict["comment"] = self.settings["comment"]
        status, state = self.createFile(
            varDict,
            self.filedelimeter,
            address=self.settings["address"] + os.sep + self.settings["filename"] + ".csv",
            data=self.lastspectrum[0],
        )
        if status:
            self.notify_user("Failed to save spectrum: " + str(state))
            return [status, state]
        return [0, "OK"]

    def _getTimeAction(self) -> None:
        """No returns since this is an internal function and the return cannot be checked.

        Returns:
            None: None
        """
        if self.auto_time_thread is not None and self.auto_time_thread.isRunning():
            self.notify_user("Auto integration time is already running.")
            return None

        preview_status = False
        [status, info] = self._parse_settings_autoTime()
        if status:
            self.notify_user("Failed to parse auto integration time settings: " + str(info))
            return None
        if self.preview_running:
            # stop preview to safely get autotime
            preview_status = self.preview_running
            self._previewAction()
        self.settingsWidget.saveButton.setEnabled(False)
        self.closeLock.emit(True)
        # check if get time may be used (spectrometer IDLE)
        statuses = self.drv.get_device_status()
        if "SCAN_IDLE" in statuses:
            self._gettime_preview_status = preview_status
            self._auto_time_result_handled = False
            self.settingsWidget.getTime_button.setEnabled(False)
            self.auto_time_thread = WorkerThread(self._auto_time_worker)
            self.auto_time_thread.result_signal.connect(self._on_auto_time_result)
            self.auto_time_thread.error.connect(self._on_auto_time_error)
            self.auto_time_thread.finished.connect(self._on_auto_time_finished)
            self.auto_time_thread.start()
            return None
        else:
            self.closeLock.emit(False)
            self.notify_user("Cannot calculate auto integration time while spectrometer is busy. Please stop any ongoing scans and try again.")
            return None

    def _auto_time_worker(self, worker_thread) -> tuple[int, float | dict]:
        return self.getAutoTime()

    @pyqtSlot(object)
    def _on_auto_time_result(self, result):
        if self._auto_time_result_handled:
            return
        self._auto_time_result_handled = True

        if not isinstance(result, tuple) or len(result) != 2:
            self.notify_user(f"Auto integration time returned unexpected result: {result}")
            return

        status, auto_time = result
        if status == 0 and isinstance(auto_time, (float, int)):
            self.settingsWidget.lineEdit_Integ.setText(f"{round(float(auto_time) * 1000)}")
        else:
            self.notify_user(f"Failed to calculate auto integration time: {auto_time}")

    @pyqtSlot(str)
    def _on_auto_time_error(self, error_message: str):
        self.notify_user(f"Auto integration time failed: {error_message}")

    @pyqtSlot()
    def _on_auto_time_finished(self):
        self.settingsWidget.getTime_button.setEnabled(True)
        if self._gettime_preview_status:
            # update preview back, this reads integration time from GUI and restarts preview.
            self._previewAction()
        else:
            self.settingsWidget.saveButton.setEnabled(True)
        self.closeLock.emit(False)
        self.auto_time_thread = None
        self._gettime_preview_status = False

    @public
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
            last_integration_time (float): Optional initial guess for integration time in seconds.

        Returns:
            tuple[int, float | dict]: Status and integration time or error information.
        """
        self.logger.log_debug("Calculating auto integration time.")
        low = self.autoTime_min  # time min s
        high = self.autoTime_max  # time max s
        low_spectrum = self.autoValue_min  # min spectrum value
        high_spectrum = self.autoValue_max  # max spectrum value

        if self.settings["integrationtimetype"] == "auto":
            # initial guess for time if not provided
            if last_integration_time is None:
                if self.settings["useintegrationtimeguess"]:
                    # guess from current value
                    guessIntTime = self.settings["integrationtime"]  # s
                else:
                    # guess from min and max
                    guessIntTime = (self.autoTime_min + self.autoTime_max) / 2  # s
            # initial guess provided as argument, use that.
            else:
                guessIntTime = last_integration_time  # ms

            # start iterating through integration times using guessIntTime as initial guess
            for iter in range(self.intTimeMaxIterations):
                self.logger.log_debug(f"Iteration {iter + 1}: Current guess = {guessIntTime} s.")
                self.settings["integrationtime"] = guessIntTime  # needed for keeping self.lastspectrum in order
                [status, info] = self.spectrometerSetIntegrationTime(guessIntTime)  # s
                if status:
                    self.logger.log_debug(f"getAutoTime: Failed to set integration time. {status}, {info}")
                    return (status, info)
                # charging the spectrometer in case of external trigger
                if self.settings["externaltrigger"]:
                    self.logger.log_debug("Charging a new  HW trig scan.")
                    self.drv.start_scan_ext_trigger()
                    time.sleep(0.02)  # just a precaution, duration does not mean anything specific, does not affect the measurement as smu is off
                    if external_action_args is None:
                        return (1, {"Error message": "External action arguments are required for hardware trigger mode."})
                    mydict = external_action_args[0]
                    mydict["integrationtime"] = guessIntTime  # in s
                # external action if needed
                if external_action:
                    self.log_verbose("getAutoTime: Executing external action.")
                    try:
                        if external_action_args:
                            status, info = external_action(*external_action_args)
                        else:
                            status, info = external_action()
                        if status:
                            self.log_verbose(f"getAutoTime: External action failed. {status}, {info}")
                            return status, info
                    except TypeError:
                        self.log_verbose("getAutoTime: External action completed without standard return value")

                [status, info] = self.spectrometerGetScan()
                if status:
                    self.log_verbose(f"getAutoTime: Failed to update spectrum. {status}, {info}")
                    error_info = info if isinstance(info, dict) else {"Error message": str(info)}
                    return (status, error_info)
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
                        data=info,
                    )
                    if status:
                        self.notify_user(f"Failed to save auto time attempt: {state}")
                        return (status, state)
                # external cleanup if needed
                if external_cleanup:
                    self.logger.log_debug("getAutoTime: Executing external cleanup.")
                    if self.settings["externaltrigger"]:
                        time.sleep(2 * mydict["postwait"])  # for the case if postwait is comparable with integration time, to make sure that the smu finished all the operations
                    try:
                        if external_cleanup_args:
                            status, info = external_cleanup(*external_cleanup_args)
                        else:
                            status, info = external_cleanup()
                        if status:
                            self.log_verbose(f"getAutoTime: External cleanup failed. {status}, {info}")
                    except TypeError:
                        self.log_verbose("getAutoTime: External cleanup completed without standard return value")
                # pause if needed
                if pause_duration > 0:
                    self.log_verbose(f"getAutoTime: Pausing for {pause_duration} seconds.")
                    time.sleep(pause_duration)

                target = max(info)  # target value to optimize
                # if spectrum is in the range, found good integration time
                if low_spectrum <= target <= high_spectrum:
                    self.logger.log_debug(f"Optimal integration time found: {guessIntTime} seconds.")
                    return [0, guessIntTime]  # return in seconds
                # if spectrum is below the range, increase integration time
                if target < low_spectrum:
                    self.log_verbose(f"Spectrum value {target} is below the range ({low_spectrum}), increasing integration time.")
                    if guessIntTime >= high:
                        self.logger.log_debug(f"Integration time is too high, returning: {guessIntTime} seconds.")
                        return [1, {"Error message": "Integration time too high"}]
                    low = guessIntTime
                # if spectrum is above the range, decrease integration time
                else:
                    self.log_verbose(f"Spectrum value {target} is above the range ({high_spectrum}), decreasing integration time.")
                    if guessIntTime <= low:
                        self.logger.log_debug(f"Integration time is too low, returning: {guessIntTime} seconds.")
                        return [1, {"Error message": "Integration time too low"}]
                    high = guessIntTime
                # Compute new guess in milliseconds, rounded to nearest millisecond
                guessIntTime = int(round((low + high) / 2))

            self.logger.log_debug(f"Auto integration time calculation completed: {guessIntTime} seconds.")
            return [0, guessIntTime]  # return in seconds
        else:
            self.log_verbose("Integration time mode is not set to auto, cannot calculate auto integration time.")
            return (1, {"Error message": "TLCCSGUI: integration time mode is not set to auto"})  # error if not auto mode

    ########Functions
    ###############GUI setting up

    def _initGUI(self, plugin_info: dict):
        """Initializes the GUI with the given plugin information.

        Args:
            plugin_info (dict):  dictionary with settings obtained from plugin_data in pyIVLS_*_plugin
        """
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK
        integration_time_ms = int(float(plugin_info["integrationtime"]) * 1000)
        self.settingsWidget.lineEdit_Integ.setText(str(integration_time_ms))
        self.log_verbose(f"Initializing GUI with integration time: {integration_time_ms} ms")
        if plugin_info["externaltrigger"] == "True":
            self.settingsWidget.extTriggerCheck.setChecked(True)
        if plugin_info["usecorrection"] == "True":
            self.settingsWidget.correctionCheck.setChecked(True)
        currentIndex = self.settingsWidget.getIntegrationTime_combo.findText(plugin_info["integrationtimetype"], Qt.MatchFlag.MatchFixedString)
        if currentIndex > -1:
            self.settingsWidget.getIntegrationTime_combo.setCurrentIndex(currentIndex)
        if plugin_info["useintegrationtimeguess"]:
            self.settingsWidget.useIntegrationTimeGuess_check.setChecked(True)
        if plugin_info["saveattempts_check"] == "True" or plugin_info["saveattempts_check"] is True:
            self.settingsWidget.saveAttempts_check.setChecked(True)
        self.settingsWidget.saveButton.setEnabled(False)
        self.settingsWidget.lineEdit_path.setText(plugin_info["address"])
        self.settingsWidget.lineEdit_filename.setText(plugin_info["filename"])
        self.settingsWidget.lineEdit_sampleName.setText(plugin_info["samplename"])
        self.settingsWidget.lineEdit_comment.setText(plugin_info["comment"])

        self.setSettings(plugin_info)  # set settings dict from plugin_info for internal use

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
            self.settingsWidget.connectionIndicator.setStyleSheet(ConnectionIndicatorStyle.GREEN_CONNECTED.value)
        else:
            self.settingsWidget.connectionIndicator.setStyleSheet(ConnectionIndicatorStyle.RED_DISCONNECTED.value)
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
        return get_public_methods(self)

    def _getCloseLockSignal(self):
        return self.closeLock

    def _parse_settings_integrationTime(self) -> tuple[int, dict]:
        """
        Parses the integration time from the GUI line edit and stores it in the settings dictionary.

        stored in self.settings["integrationtime"] as float in seconds

        Returns:
            list: [0, "OK"] on success, or [1, {"Error message": ...}] on error.
        """
        try:
            integration_time_ms = int(self.settingsWidget.lineEdit_Integ.text())
        except ValueError:
            return (1, {"Error message": "Value error in TLCCS plugin: integration time field should be integer"})
        if integration_time_ms > const.CCS_SERIES_MAX_INT_TIME * 1000:
            return (1, {"Error message": f"Value error in TLCCS plugin: integration time should can not be greater than maximum integration time {const.CCS_SERIES_MAX_INT_TIME} s"})
        if integration_time_ms < 1:
            return (1, {"Error message": "Value error in TLCCS plugin: integration time should can not be smaller than 1 ms"})
        self.settings["integrationtime"] = integration_time_ms / 1000  # stored in seconds
        return (0, {})

    def _parse_settings_autoTime(self) -> tuple[int, dict]:
        self.settings["integrationtimetype"] = self.settingsWidget.getIntegrationTime_combo.currentText()
        self.settings["saveattempts_check"] = self.settingsWidget.saveAttempts_check.isChecked()
        self.settings["useintegrationtimeguess"] = self.settingsWidget.useIntegrationTimeGuess_check.isChecked()
        if self.settings["saveattempts_check"]:
            [status, info] = self._parseSaveData()
            if status:
                return (status, info)
        if self.settings["useintegrationtimeguess"]:
            [status, info] = self._parse_settings_integrationTime()
            if status:
                return (status, info)

        return (0, {})

    def _parse_spectrumCorrection(self):
        if self.settingsWidget.correctionCheck.isChecked():
            return True
        else:
            return False

    def _parseSaveData(self) -> tuple[int, dict]:
        self.settings["address"] = self.settingsWidget.lineEdit_path.text()
        if not os.path.isdir(self.settings["address"] + os.sep):
            self.notify_user("Provided address is not valid. Please select a valid directory for saving data.")
            return (1, {"Error message": "TLCCS plugin : address string should point to a valid directory"})
        self.settings["filename"] = self.settingsWidget.lineEdit_filename.text()
        if not is_valid_filename(self.settings["filename"]):
            self.notify_user("Filename is not valid. Please enter a valid filename")
            return (1, {"Error message": "TLCCS plugin : filename is not valid"})

        self.settings["samplename"] = self.settingsWidget.lineEdit_sampleName.text()
        self.settings["comment"] = self.settingsWidget.lineEdit_comment.text()
        self.settings["externaltrigger"] = self.settingsWidget.extTriggerCheck.isChecked()  # this is here since this is written into the header

        return (0, {"Error message": "OK"})

    def parse_settings_preview(self) -> tuple[int, dict]:
        """Parses the settings widget for the spectrometer. Extracts current values

        Returns:
            0 - no error
            ~0 - error (add error code later on if needed)
        """
        self.settings = {}
        [status, info] = self._parse_settings_autoTime()
        if status:
            return (status, info)
        if not self.settings["useintegrationtimeguess"]:
            [status, info] = self._parse_settings_integrationTime()
            if status:
                return (status, info)
        if not self.settings["saveattempts_check"]:
            [status, info] = self._parseSaveData()
            if status:
                return (status, info)
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
        return (0, self.settings)

    @public
    def parse_settings_widget(self) -> tuple[int, dict]:
        """Parses the settings widget for the spectrometer. Extracts current values

        Returns:
            0 - no error
            ~0 - error (add error code later on if needed)
        """
        self.settings = {}
        [status, info] = self._parse_settings_autoTime()
        if status:
            return (status, info)
        if not self.settings["useintegrationtimeguess"]:
            [status, info] = self._parse_settings_integrationTime()
            if status:
                return (status, info)
        if not self.settings["saveattempts_check"]:
            [status, info] = self._parseSaveData()
            if status:
                return (status, info)
        if self.settingsWidget.extTriggerCheck.isChecked():
            self.settings["externaltrigger"] = True
        else:
            self.settings["externaltrigger"] = False
        self.settings["usecorrection"] = self._parse_spectrumCorrection()
        # duplicate value for spectrum correction since i don't want to break anything now. This is used to save the value to the ini.

        return (0, self.settings)

    @public
    def setSettings(self, settings):  #### settings from external call
        self.settings = {}
        self.settings = copy.deepcopy(settings)

    @public
    def set_gui_from_settings(self):
        print("TODO SET GUI FROM SETTINGS")

    ########Functions
    ########device functions
    @public
    def spectrometerConnect(self, integrationTime=None):
        # Parse settings to ensure integration time and related flags are current
        parsed_status, info = self.parse_settings_widget()
        if parsed_status:
            return [parsed_status, info]

        if integrationTime is not None:
            self.settings["integrationtime"] = integrationTime

        status = self.drv.open(const.CCS175_VID, const.CCS175_PID, self.settings["integrationtime"])
        if not status:
            return (4, {"Error message": "Can not connect to spectrometer"})

        # Notify GUI about successful connection
        self.connectionStateChanged.emit(True)
        return (0, {"Error message": "OK"})

    @public
    def spectrometerDisconnect(self):
        # ensure preview is stopped before closing device
        if self.preview_running:
            self._previewAction()

        self.drv.close()
        # Notify GUI about successful disconnection
        self.connectionStateChanged.emit(False)
        return (0, {"Error message": "OK"})

    @public
    def spectrometerSetIntegrationTime(self, integrationTime):
        self.drv.set_integration_time(integrationTime)
        # single scan to make sure the time is correctly set
        self.spectrometerStartScan()
        self.spectrometerGetSpectrum()

        return (0, {"Error message": "OK"})

    @public
    def spectrometerGetIntegrationTime(self):
        # return current integration time in seconds
        intTime = self.drv.get_integration_time()
        return [0, intTime]

    @public
    def spectrometerTrigScan(self):
        # arm the spectrometer to perform a scan on external trigger
        try:
            self.drv.start_scan_ext_trigger()
            return [0, "OK"]
        except Exception as e:
            return [4, {"Error message": f"{e}"}]

    @public
    def spectrometerStartScan(self):
        """Starts a spectro scan"""
        status = self.drv.get_device_status()
        if "SCAN_IDLE" not in status:
            return [0, {"Error message": "scan is already running"}]

        self.drv.start_scan()
        return [0, {"Error message": "OK"}]

    @public
    def spectrometerStartScanExternal(self):
        """
        Starts an external trigger spectro scan
        returns:
            tuple: (status, info)
        """
        status = self.drv.get_device_status()
        if "SCAN_EXT_TRIGGER" in status:
            return [0, {"Error message": "External trigger scan is already running"}]

        self.drv.start_scan_ext_trigger()
        return [0, {"Error message": "OK"}]

    @public
    def spectrometerGetSpectrum(self):
        """Reads the spectrum from the spectrometer, waits for the scan to finish if necessary."""
        iterations = 0
        MAX_ITER = 5
        while "SCAN_TRANSFER" not in self.drv.get_device_status():
            self.log_verbose("Waiting for scan to finish.")
            time.sleep(self.settings["integrationtime"])
            iterations += 1
            if iterations > MAX_ITER:
                raise TimeoutError("Timeout waiting for scan to finish.")

        data = self.drv.get_scan_data()
        # Emit data for preview update: [wavelengths, intensities]
        self.data_recieved_signal.emit([self.correction[:, 0], data])
        return [0, data]

    @public
    def spectrometerGetScan(self):
        """Atomically get a spectrum to prevent weird behavior when a scan is already running."""
        self.drv.start_scan()
        data = self.drv.get_scan_data()
        # Emit data for preview update: [wavelengths, intensities]
        self.data_recieved_signal.emit([self.correction[:, 0], data])
        return (0, data)

    @public
    def spectrometerGetStatus(self):
        return 0, self.drv.get_device_status()

    ########Functions
    ###############save data

    @public
    def createFile(self, varDict, filedelimeter, address, data):
        # check if the file already exists, if yes, return error
        if os.path.isfile(address):
            return (1, {"Error message": "File already exists at the specified address."})
        fileheader = self.fm.create_spectrometer_header(varDict, separator=filedelimeter)
        self.log_verbose(f"Creating file at {address} with data shape {data.shape}")
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

    ######## Timer callback ########
    def _on_preview_tick(self):
        """Timer tick handler: apply pending integration time and get data for new scan"""
        try:
            if self.integrationTimeChanged:
                self.spectrometerSetIntegrationTime(self.settings["integrationtime"])
                self.integrationTimeChanged = False
                # since setting the integration time causes a SINGLE scan read, we need to restart continous scanning
                self.drv.start_scan_continuous()

                # reset the timer interval in case integration time is higher than default interval
                integration_ms = int(self.settings["integrationtime"] * 1000)
                interval_ms = int(max(self.default_timerInterval, integration_ms))
                self._preview_timer.start(interval_ms)
            # trigger and emit via spectrometerGetScan
            self.spectrometerGetSpectrum()
        except Exception as e:
            self.log_verbose(f"Preview timer error: {e}")
