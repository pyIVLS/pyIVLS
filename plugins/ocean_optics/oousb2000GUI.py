from typing import Optional
import oo_utils as utils
from oo_utils import ms_to_s, s_to_ms
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
from oousb2000 import OODRV, trigger_mode

from plugin_components import public, get_public_methods, LoggingHelper, CloseLockSignalProvider, GuiMapper, ConnectionIndicatorStyle


class OOUSB2000_GUI:
    """spectrometer plugin for pyIVLS"""

    #    filedelimeter = "\t"
    filedelimeter = ";"

    default_timerInterval = 20  # ms, it is close to 24*2 fps (twice the standard for movies and TV)
    # limits for auto time detection
    autoTime_min = 0.004  # s, used to be 4
    autoTime_max = 30  # s, used to be 10000
    autoValue_min = 0.2  # spectrum value in arb.(?) units
    autoValue_max = 0.8  # spectrum value in arb.(?) units
    intTimeMaxIterations = 10

    ########Functions
    def __init__(self, verbose=False):
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        self.settingsWidget = uic.loadUi(self.path + "oousb2000_settingsWidget.ui")
        self.previewWidget = uic.loadUi(self.path + "oousb2000_MDIWidget.ui")

        # create the driver
        self.drv = OODRV()

        self.logger = LoggingHelper(self)
        self.cl = CloseLockSignalProvider()
        self.closeLock = self.cl.closeLock
        self.mapper = GuiMapper(self.settingsWidget, "oousb2000")
        self._connect_signals()
        self._create_plt()

        self.lastspectrum = []  # data for saving from preview
        self.preview_running = False
        self.integrationTimeChanged = False
        self.scanRunning = False
        self.settings = {}

        self.settings_map = {
            "integrationtime": "integ_spinBox",
            "externaltrigger": "extTriggerCheck",
            "integrationtimetype": "getIntegrationTime_combo",
            "useintegrationtimeguess": "useIntegrationTimeGuess_check",
            "saveattempts_check": "saveAttempts_check",
            "correctdarkcounts": "correctionCheck",
            "address": "lineEdit_path",
            "filename": "lineEdit_filename",
            "samplename": "lineEdit_sampleName",
            "comment": "lineEdit_comment",
        }
        self.validation_rules = {
            "address": {"validator": lambda x: os.path.exists(x), "error_message": "Address is not a valid path"},
            "filename": {"validator": lambda x: is_valid_filename(x), "error_message": "filename must be a valid filename"},
        }

    def _connect_signals(self):
        self.settingsWidget.connectButton.clicked.connect(self._connectAction)
        self.settingsWidget.disconnectButton.clicked.connect(self._disconnectAction)
        self.settingsWidget.setIntegrationTimeButton.clicked.connect(self._setIntTimeAction)
        self.settingsWidget.previewButton.clicked.connect(self._previewAction)
        self.settingsWidget.saveButton.clicked.connect(self._saveAction)
        self.settingsWidget.directoryButton.clicked.connect(self._getAddress)
        self.settingsWidget.getTime_button.clicked.connect(self._getTimeAction)
        self.settingsWidget.correctionCheck.stateChanged.connect(self._correctionChanged)
        self.settingsWidget.getIntegrationTime_combo.currentIndexChanged.connect(self._integrationTime_mode_changed)

    def _create_plt(self):
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.axes = self.sc.fig.add_subplot(111)

        self.axes.set_xlabel("Wavelength (nm)")
        self.axes.set_ylabel("Intensity (calib. arb. un.)")

        self.axes.set_xlim(utils.OO_MIN_WL, utils.OO_MAX_WL)  # limits are given by spectral range of the device

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
        status, info = self.spectrometerGetScan()
        if status:
            self.scanRunning = False
            self.logger.info_popup(f"Error getting spectrum: {info['Error message']}")
            return [status, info]
        else:
            spectrum = info

        try:
            xmin, xmax = self.axes.get_xlim()
            ymin, ymax = self.axes.get_ylim()
            self.axes.cla()
            self.axes.set_xlabel("Wavelength (nm)")
            self.axes.set_ylabel("Intensity (calib. arb. un.)")
            self.axes.plot(spectrum, "b-")
            self.axes.set_xlim(xmin, xmax)
            self.axes.set_ylim(ymin, ymax)
            self.sc.draw()
            self.lastspectrum = [info, self.settings]
            return [0, [spectrum, self.settings]]
        except Exception as e:
            return [3, self.lastspectrum]

    ########Functions
    ########GUI Slots

    def _connectAction(self):
        status, state = self.spectrometerConnect()
        if status:
            self.logger.info_popup(f"Error connecting to spectrometer: {state['Error message']}")
        else:
            self.settingsWidget.connectionIndicator.setStyleSheet(ConnectionIndicatorStyle.GREEN_CONNECTED.value)

    def _disconnectAction(self):
        pass

    def _previewAction(self):
        # FIXME: The integration time seems to be Doubled. For example, with integ at 5 s, the logs show an update happening only every 10 s
        if self.preview_running:
            self.preview_running = False
            if hasattr(self, "run_thread") and self.run_thread.is_alive():
                self.run_thread.join(timeout=2)  # Wait up to 2 seconds for the thread to finish
            self._enableSaveButton()
            self.closeLock.emit(self.preview_running)
            self.settingsWidget.previewButton.setText("Preview")
        else:
            [status, info] = self.parse_settings_preview()
            if status:
                return [status, info]
            self.integrationTimeChanged = True
            self.preview_running = True
            self.closeLock.emit(self.preview_running)
            self.settingsWidget.saveButton.setEnabled(False)
            self.run_thread = thread_with_exception(self._previewIteration)
            self.run_thread.start()
            self.settingsWidget.previewButton.setText("Stop preview")

    def _previewIteration(self):
        try:
            while self.preview_running:
                if self.integrationTimeChanged:
                    [status, info] = self.spectrometerSetIntegrationTime(self.settings["integrationTime"])
                    self.integrationTimeChanged = False
                    # FIXME: sleep_time currently unused for debugging
                    if self.settings["integrationTime"] * 1000 < self.default_timerInterval:
                        self.sleep_time = self.default_timerInterval / 1000
                    else:
                        self.sleep_time = self.settings["integrationTime"]
                    if status:
                        self.preview_running = False
                        return [status, info]
                # time.sleep(self.sleep_time)
                [status, info] = self._update_spectrum()
                if status:
                    self.preview_running = False
                    return [status, info]
            # If preview_running is set to False, finish the current scan and exit
            return [0, "preview stopped"]
        except ThreadStopped:
            return [0, "preview stopped"]

    def _setIntTimeAction(self):
        if self.preview_running:  # this function is useful only in preview mode
            [status, info] = self._parse_settings_integrationTime()
            if status:
                return [status, info]
            self.integrationTimeChanged = True
            return [0, "OK"]

    def _saveAction(self):
        [status, info] = self._parseSaveData()
        if status:
            return [status, info]
        varDict = {}
        varDict["integrationtime"] = self.lastspectrum[1]["integrationTime"]
        varDict["triggermode"] = 1 if self.lastspectrum[1]["externalTrigger"] else 0
        varDict["name"] = self.settings["samplename"]
        varDict["comment"] = self.settings["comment"]
        self.createFile(
            varDict,
            self.filedelimeter,
            address=self.settings["address"] + os.sep + self.settings["filename"] + ".csv",
            data=self.lastspectrum[0],
        )
        return [0, "OK"]

    def _getTimeAction(self):
        preview_status = False
        [status, info] = self._parse_settings_autoTime()
        if status:
            return [status, info]
        if self.preview_running:
            preview_status = self.preview_running
            self._previewAction()
        self.settingsWidget.saveButton.setEnabled(False)
        self.closeLock.emit(True)
        # check if get time may be used (spectrometer IDLE)
        statuses = self.drv.get_device_status()
        if "SCAN_IDLE" in statuses:
            status, autoTime = self.getAutoTime()
            if not status:
                self.settingsWidget.lineEdit_Integ.setText(f"{round(autoTime * 1000)}")
            if preview_status:
                self._previewAction()
            else:
                self.settingsWidget.saveButton.setEnabled(True)
            self.closeLock.emit(False)
            return [0, "OK"]
        else:
            self.closeLock.emit(False)
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
        low = self.autoTime_min * 1000  # time min ms
        high = self.autoTime_max * 1000  # time max ms
        low_spectrum = self.autoValue_min  # min spectrum value
        high_spectrum = self.autoValue_max  # max spectrum value

        if self.settings["integrationtimetype"] == "auto":
            # initial guess for time if not provided
            if last_integration_time is None:
                if self.settings["useintegrationtimeguess"]:
                    # guess from current value
                    guessIntTime = self.settings["integrationTime"] * 1000  # ms
                else:
                    # guess from min and max
                    guessIntTime = (self.autoTime_min + self.autoTime_max) / 2 * 1000  # ms
            # initial guess provided as argument, use that.
            else:
                guessIntTime = last_integration_time * 1000  # ms

            # start iterating through integration times using guessIntTime as initial guess
            for iter in range(self.intTimeMaxIterations):
                self.settings["integrationTime"] = guessIntTime / 1000.0  # needed for keeping self.lastspectrum in order
                [status, info] = self.spectrometerSetIntegrationTime(guessIntTime / 1000.0)  # s
                if status:
                    return [status, info]
                # external action if needed
                if external_action:
                    try:
                        if external_action_args:
                            status, info = external_action(*external_action_args)
                        else:
                            status, info = external_action()
                        if status:
                            return status, info
                    except TypeError:
                        pass

                [status, info] = self._update_spectrum()
                if status:
                    return [status, info]
                # save the spectrum if needed
                if self.settings["saveattempts_check"]:
                    varDict = {}
                    varDict["integrationtime"] = guessIntTime / 1000.0
                    varDict["triggermode"] = 1 if self.settings["externalTrigger"] else 0
                    varDict["name"] = self.settings["samplename"]
                    varDict["comment"] = self.settings["comment"] + " Auto adjust of integration time."
                    self.createFile(
                        varDict=varDict,
                        filedelimeter=self.filedelimeter,
                        address=self.settings["address"] + os.sep + self.settings["filename"] + f"_{int(guessIntTime)}ms.csv",
                        data=info[1],
                    )
                # external cleanup if needed
                if external_cleanup:
                    try:
                        if external_cleanup_args:
                            status, info = external_cleanup(*external_cleanup_args)
                        else:
                            status, info = external_cleanup()
                        if status:
                            return status, info
                    except TypeError:
                        pass
                # pause if needed
                if pause_duration > 0:
                    time.sleep(pause_duration)

                target = max(info[1])  # target value to optimize
                # if spectrum is in the range, found good integration time
                if low_spectrum <= target <= high_spectrum:
                    return [0, guessIntTime / 1000.0]  # return in seconds
                # if spectrum is below the range, increase integration time
                if target < low_spectrum:
                    if guessIntTime >= high:
                        return [1, {"Error message": "Integration time too high"}]
                    low = guessIntTime
                # if spectrum is above the range, decrease integration time
                else:
                    if guessIntTime <= low:
                        return [1, {"Error message": "Integration time too low"}]
                    high = guessIntTime
                # Compute new guess in milliseconds, rounded to nearest millisecond
                guessIntTime = int(round((low + high) / 2))

            return [0, guessIntTime / 1000.0]  # return in seconds
        else:
            return (
                1,
                {"Error message": "TLCCSGUI: integration time mode is not set to auto"},
            )  # error if not auto mode

    ########Functions
    ###############GUI setting up

    def _initGUI(self, plugin_info: dict):
        """Initializes the GUI with the given plugin information.

        Args:
            plugin_info (dict):  dictionary with settings obtained from plugin_data in pyIVLS_*_plugin
        """
        status, state = self.mapper.set_values(plugin_info, self.settings_map, validation_rules={})
        assert not status, f"Failed to set GUI values: {state}"

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

    def _correctionChanged(self):
        print("correction changed")

    def _integrationTime_mode_changed(self):
        print("integration time mode changed")

    ########Functions
    ########plugins interraction

    def _get_public_methods(self):
        """
        Returns a nested dictionary of public methods for the plugin
        """
        # if the plugin type matches the requested type, return the functions

        return get_public_methods(self)

    def parse_settings_widget(self) -> tuple[int, dict]:
        status, state = self.mapper.get_values(field_mapping=self.settings_map, validation_rules=self.validation_rules)
        # junction: Info if bad, update internal if good
        if status:
            self.logger.info_popup(f"Invalid settings: {state['Error message']}")
        else:
            self.settings = state
        return (0, self.settings)

    def setSettings(self, settings):  #### settings from external call
        self.settings = {}
        self.settings = copy.deepcopy(settings)
        self.mapper.schedule_gui_update(self.settings, self.settings_map, validation_rules={})

    # Spectrometer functions    @public
    def spectrometerConnect(self) -> tuple[int, dict]:
        self.drv.open()
        return (0, {"Error message": "ok"})

    def spectrometerDisconnect(self) -> tuple[int, dict]:
        return (0, {"Error message": "ok"})

    def spectrometerSetIntegrationTime(self, integ_time: float) -> tuple[int, dict]:
        """Set the integration time in seconds (just because the corresponding func in tlccsdrv uses seconds).

        Args:
            intg_time (float): Integration time in seconds

        Returns:
            tuple[int, dict]: status, info
        """
        self.drv.set_integration_time(s_to_ms(integ_time))  # convert to microseconds
        return (0, {"Error message": "ok"})

    def spectrometerGetIntegrationTime(self) -> tuple:
        """Get the current integration time.

        Returns:
            tuple[int, dict]: status, integration time in seconds
        """
        return (0, ms_to_s(self.drv.get_integration_time()))

    def spectrometerStartScan(self):
        return (0, {"Error message": "ok"})

    def spectrometerGetSpectrum(self):
        return (0, self.drv.get_spectrum(correct_dark_counts=self.settings["correctDarkCounts"]))

    def spectrometerGetScan(self):
        return (0, self.drv.get_spectrum(correct_dark_counts=self.settings["correctDarkCounts"]))

    ########Functions
    ###############save data

    def createFile(self, varDict, filedelimeter, address, data):
        fileheader = self._spectrometerMakeHeader(varDict, separator=filedelimeter)
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
