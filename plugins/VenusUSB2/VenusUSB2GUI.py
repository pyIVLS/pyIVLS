"""
This is a GUI plugin for VenusUSB2 camera for pyIVLS

This file should provide
- functions for interaction with other plugins (those that will be exported on get_functions hook call, these should not start with "_")
- functions that will implement functionality of the hooks (see pyIVLS_VenusUSB2)
- GUI functionality - code that interracts with Qt GUI elements from widgets

This plugin should have double functionality
(i) it may be independently used to run camera preview
(ii) it provides functionality of getting images for other plugins

Because of (i) it requires to send log and message signals, i.e. it is a child of QObject

public API:
- camera_open() -> "error"
- camera_close() -> None
- camera_capture_image() -> image / None

public API:
- camera_open() -> "error"
- camera_close() -> None
- camera_capture_image() -> image / None

version 0.6
2025.05.12
ivarad
version 0.5
2025.05.22
otsoha
"""

import os
from datetime import datetime
from pathvalidate import is_valid_filename

from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QImage, QPixmap
from VenusUSB2 import VenusUSB2, venusStatus

##IRtothink#### should some kind of zoom to the image part be added for the preview?


class VenusUSB2GUI(QObject):
    """GUI for the VenusUSB2 camera"""

    non_public_methods = []  # add function names here, if they should not be exported as public to another plugins
    public_methods = [
        "camera_open",
        "camera_close",
        "camera_capture_image",
    ]  # necessary for descendents of QObject, otherwise _get_public_methods returns a lot of QObject methods
    default_timerInterval = (
        42  # ms, it is close to 24 fps that is standard for movies and TV
    )
    ########Signals

    # used to send messages to the main app
    log_message = pyqtSignal(str)
    info_message = pyqtSignal(str)
    closeLock = pyqtSignal(bool)

    ########Functions
    def __init__(self):
        super(VenusUSB2GUI, self).__init__()
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        ##IRtothink#### I do not like have filename hardly coded,
        ############### but in any case the refrences to the GUI elements will be hardly coded, so it may be OK

        """Changes here:
        - widgets are loaded from the same directory, and assume to have relevant suffixes. 
        I thinks this is easier than to just hardcode the names, now they just have to be in 
        the same directory and have the correct suffixes. This can be copied to other plugins.
        """
        for _, _, files in os.walk(self.path):
            for file in files:
                if file.endswith(".ui"):
                    if file.split("_")[1] == "settingsWidget.ui":
                        self.settingsWidget = uic.loadUi(self.path + file)
                    elif file.split("_")[1] == "previewWidget.ui":
                        self.previewWidget = uic.loadUi(self.path + file)

        self.settings = {"source": None, "exposure": None}
        self.q_img = None

        # Initialize cap as empty capture
        self.camera = VenusUSB2()

        self.exposure = self.settingsWidget.findChild(QtWidgets.QComboBox, "exposure")
        assert self.exposure is not None, (
            "Exposure combobox not found in settingsWidget"
        )

        # get possible exposures from the camera
        exposures = self.camera.exposures

        # add possible exposures to the combobox
        for exposure in exposures:
            self.exposure.addItem(str(exposure))

        self._exp_slider_change()

        self._connect_signals()

        # Set a timer for the camera feed
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        self.preview_running = False
        self.preview_label = self.previewWidget.previewLabel
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setScaledContents(False)

    ########Functions
    ################################### internal

    def _connect_signals(self):
        # Connect widget buttons to functions
        self.settingsWidget.cameraPreview.clicked.connect(self._previewAction)
        self.settingsWidget.saveButton.clicked.connect(self._saveAction)
        self.settingsWidget.directoryButton.clicked.connect(self._getAddress)
        self.settingsWidget.exposure.currentIndexChanged.connect(
            self._exp_slider_change
        )

    def _update_frame(self):


        ret, frame = self.camera.capture_buffered()  # Capture a frame from the camera
        if not ret:
            self.log_message.emit(
                datetime.now().strftime("%H:%M:%S.%f")
                + " : VenusUSB2 plugin : Error capturing frame"
            )
            return
        label = self.preview_label
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(
            label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        label.setPixmap(scaled_pixmap)
        self.q_img = qt_image  # Store the QImage for saving later

    def _parse_settings_preview(self) -> "status":
        """Parses the settings widget for the camera. Extracts current values

        Returns:
            0 - no error
            ~0 - error (add error code later on if needed)
        """
        self.settings["exposure"] = int(self.exposure.currentText())
        self.settings["source"] = self.settingsWidget.cameraSource.text()
        ##no value checks are possible here as the source should be just address and exposure is given by a set of values
        return [0, self.settings]

    ########Functions
    ########GUI Slots

    def _previewAction(self):
        """interface for the preview button. Opens the camera, sets the exposure and previews the feed"""
        if self.preview_running:
            self.timer.stop()
            self._GUIchange_deviceConnected(self.preview_running)
            self.closeLock.emit(not self.preview_running)
            self.preview_running = False
            self._enableSaveButton()
            self.camera.close()
        else:
            self._parse_settings_preview()
            [status, message] = self.camera.open(
                source=self.settings["source"], exposure=self.settings["exposure"]
            )
            if status:
                self.log_message.emit(
                    datetime.now().strftime("%H:%M:%S.%f")
                    + f" : VenusUSB2 plugin : {message}, status = {status}"
                )
                self.info_message.emit(f"VenusUSB2 plugin : {message}")
            else:
                if self.settings["exposure"] < self.default_timerInterval:
                    self.timer.start(self.default_timerInterval)
                else:
                    self.timer.start(
                        self.default_timerInterval + self.settings["exposure"]
                    )
                self.settingsWidget.saveButton.setEnabled(False)
                self._GUIchange_deviceConnected(self.preview_running)
                self.closeLock.emit(not self.preview_running)
                self.preview_running = True

    def _saveAction(self):
        [status, info] = self._parseSaveData()
        if status:
            self.info_message.emit(f"VenusUSB2 plugin : {info['Error message']}")
            return [status, info]
        self.q_img.save(
            self.settings["address"] + os.sep + self.settings["filename"] + ".jpeg",
            format="jpeg",
        )

    ########Functions
    ###############GUI setting up

    def _initGUI(
        self,
        plugin_info: "dictionary with settings obtained from plugin_data in pyIVLS_*_plugin",
    ):
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK

        self.settingsWidget.cameraSource.setText(plugin_info["source"])
        self.settingsWidget.saveButton.setEnabled(False)
        self.settingsWidget.lineEdit_path.setText(plugin_info["address"])
        self.settingsWidget.lineEdit_filename.setText(plugin_info["filename"])

    def _getAddress(self):
        address = self.settingsWidget.lineEdit_path.text()
        if not (os.path.exists(address)):
            address = self.path
        address = QFileDialog.getExistingDirectory(
            None,
            "Select directory for saving",
            address,
            options=QFileDialog.Option.ShowDirsOnly
            | QFileDialog.Option.DontResolveSymlinks,
        )
        if address:
            self.settingsWidget.lineEdit_path.setText(address)

    ########Functions
    ###############GUI react to change

    def _GUIchange_deviceConnected(self, status):
        # NOTE: status is inverted, i.e. when preview is started received status should False, when preview is stopped status should be True
        if status:
            self.settingsWidget.connectionIndicator.setStyleSheet(
                "border-radius: 10px; background-color: rgb(165, 29, 45); min-height: 20px; min-width: 20px;"
            )
        else:
            self.settingsWidget.connectionIndicator.setStyleSheet(
                "border-radius: 10px; background-color: rgb(38, 162, 105); min-height: 20px; min-width: 20px;"
            )
        self.settingsWidget.sourceBox.setEnabled(status)

    def _enableSaveButton(self):
        if not self.q_img:
            self.settingsWidget.saveButton.setEnabled(False)
        else:
            self.settingsWidget.saveButton.setEnabled(True)

    def _exp_slider_change(self):
        self._parse_settings_preview()
        self.camera.set_exposure(self.settings["exposure"])

    ########Functions
    ########plugins interraction
    # These are hooked to the plugin container and sent to the main app. Then they are connected to the msg slots.

    def _getLogSignal(self):
        return self.log_message

    def _getInfoSignal(self):
        return self.info_message

    def _getCloseLockSignal(self):
        return self.closeLock

    def _get_public_methods(self, function: str) -> dict:
        """
        Returns a nested dictionary of public methods for the plugin
        """
        methods = {
            method: getattr(self, method)
            for method in dir(self)
            if callable(getattr(self, method))
            and not method.startswith("__")
            and not method.startswith("_")
            and method not in self.non_public_methods
            and method in self.public_methods
        }
        return methods

    # HOX: Functions for the camera are exported when they have the prefix "camera_"
    def camera_open(self):
        """Opens the camera using current settings.
        Returns:
            0 - no error
            ~0 - error (add error code later on if needed)
        """
        self._parse_settings_preview()
        source = self.settings["source"]
        exposure = self.settings["exposure"]
        status, message = self.camera.open(source=source, exposure=exposure)
        if status:
            return status, message
        else:
            self._GUIchange_deviceConnected(False)
            return [0, "VenusUSB2 ok"]

    def camera_close(self):
        self.camera.close()
        self._GUIchange_deviceConnected(True)

    def camera_capture_image(self, full_size=False):
        parse_status, settings = self._parse_settings_preview()
        if parse_status == 0:
            source = settings["source"]
            exposure = settings["exposure"]
            try:
                img = self.camera.capture_image(source, exposure, full_size=full_size)
            except venusStatus as e:
                self.log_message.emit(e.message)
                img = None
        else:
            img = None
            self.log_message.emit(
                datetime.now().strftime("%H:%M:%S.%f")
                + f" : VenusUSB2 plugin settings error, status = {parse_status}"
            )

        return img
    
    def camera_capture_buffered(self):
        return self.camera.capture_buffered()

    def _parseSaveData(self) -> "status":
        self.settings["address"] = self.settingsWidget.lineEdit_path.text()
        if not os.path.isdir(self.settings["address"] + os.sep):
            self.log_message.emit(
                datetime.now().strftime("%H:%M:%S.%f")
                + f" : VenusUSB2 plugin : address string should point to a valid directory"
            )
            return [
                1,
                {
                    "Error message": f"VenusUSB2 plugin : address string should point to a valid directory"
                },
            ]
        self.settings["filename"] = self.settingsWidget.lineEdit_filename.text()
        if not is_valid_filename(self.settings["filename"]):
            self.log_message.emit(
                datetime.now().strftime("%H:%M:%S.%f")
                + f" : VenusUSB2 plugin : filename is not valid"
            )
            self.info_message.emit(f"VenusUSB2 plugin : filename is not valid")
            return [1, {"Error message": f"VenusUSB2 plugin : filename is not valid"}]
        return [0, "Ok"]
