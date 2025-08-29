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


version 0.6
2025.05.12
ivarad
version 0.7
2025.06.11
otsoha
"""

import numpy as np
import os
from pathvalidate import is_valid_filename
from plugin_components import (
    public,
    get_public_methods,
    LoggingHelper,
    CloseLockSignalProvider,
    ConnectionIndicatorStyle,
)
from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QObject, pyqtSignal, Qt, QThread
from PyQt6.QtGui import QImage, QPixmap
from VenusUSB2 import VenusUSB2

##IRtothink#### should some kind of zoom to the image part be added for the preview?


# This solves some issues but might create others.
# Pros: slots are fast and good, GUI remains unblocked
# Cons: Creating multiple connections to this might cause overhead issues.
# It would probably be better to create a single thread or worker for one preview session.
# but then the new thread would have to be connected again back to the other plugins.
class CameraThread(QThread):
    new_frame = pyqtSignal(np.ndarray)

    def __init__(self, camera, interval_ms):
        super().__init__()
        self.camera = camera
        self.interval_ms = interval_ms
        self._running = False
        self.finished.connect(self.deleteLater)

    def run(self):
        self._running = True
        while self._running:
            status, frame = self.camera.capture_buffered()
            if status == 0:
                self.new_frame.emit(frame)
            self.msleep(self.interval_ms)
        # finished when running flag set to false via .stop()

    def stop(self):
        self._running = False
        self.wait()


class VenusUSB2GUI(QObject):
    """GUI for the VenusUSB2 camera"""

    # Signal emitted when a new camera thread is created
    new_camera_thread = pyqtSignal(object)  # Emits the new camera thread

    non_public_methods = []  # add function names here, if they should not be exported as public to another plugins
    public_methods = [
        "camera_open",
        "camera_close",
        "camera_capture_image",
        "get_thread",
        "connect_to_new_frame_signal",
    ]  # necessary for descendents of QObject, otherwise _get_public_methods returns a lot of QObject methods
    default_timerInterval = 42  # ms, it is close to 24 fps that is standard for movies and TV

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
        self.settingsWidget = uic.loadUi(self.path + os.path.sep + "VenusUSB2_settingsWidget.ui")
        self.previewWidget = uic.loadUi(self.path + "VenusUSB2_previewWidget.ui")

        self.settings = {"source": None, "exposure": None}
        self.q_img = None

        # Initialize cap as empty capture
        self.camera = VenusUSB2()

        # Camera thread will be created per session, not in init
        self.camera_thread = None
        self.preview_running = False

        self.exposure = self.settingsWidget.findChild(QtWidgets.QComboBox, "exposure")
        assert self.exposure is not None, "Exposure combobox not found in settingsWidget"

        # get possible exposures from the camera
        exposures = self.camera.exposures

        # add possible exposures to the combobox
        for exposure in exposures:
            self.exposure.addItem(str(exposure))

        self._exp_slider_change()

        self._connect_signals()

        self.preview_label = self.previewWidget.previewLabel
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setScaledContents(False)

        self.logger = LoggingHelper(self)
        self.cl = CloseLockSignalProvider()

    ########Functions
    ################################### internal

    def _connect_signals(self):
        # Connect widget buttons to functions
        self.settingsWidget.cameraPreview.clicked.connect(self._previewAction)
        self.settingsWidget.saveButton.clicked.connect(self._saveAction)
        self.settingsWidget.directoryButton.clicked.connect(self._getAddress)
        self.settingsWidget.exposure.currentIndexChanged.connect(self._exp_slider_change)
        # Camera thread connection will be made when thread is created

    def _update_frame(self, frame: np.ndarray):
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

    @public
    def parse_settings_widget(self) -> tuple[int, dict]:
        """Parses the settings widget for the camera. Extracts current values

        Returns:
            0 - no error
            ~0 - error (add error code later on if needed)
        """
        self.settings["exposure"] = int(self.exposure.currentText())
        self.settings["source"] = self.settingsWidget.cameraSource.text()
        self.settings["filename"] = self.settingsWidget.lineEdit_filename.text()
        self.settings["address"] = self.settingsWidget.lineEdit_path.text()
        ##no value checks are possible here as the source should be just address and exposure is given by a set of values
        return [0, self.settings]

    ########Functions
    ########GUI Slots

    def _create_new_camera_thread(self):
        """Create a new camera thread for this preview session"""
        # Stop and clean up any existing thread
        if self.camera_thread is not None:
            self.camera_thread.stop()
            self.camera_thread = None

        # Create new thread
        self.camera_thread = CameraThread(self.camera, interval_ms=self.default_timerInterval)
        # Connect the new thread to the local update method
        self.camera_thread.new_frame.connect(self._update_frame)

        # Emit signal to notify other plugins about the new thread
        self.new_camera_thread.emit(self.camera_thread)

        return self.camera_thread

    def _previewAction(self):
        """interface for the preview button. Opens the camera, sets the exposure and previews the feed"""
        if self.preview_running:
            self._GUIchange_deviceConnected(self.preview_running)
            self.cl.closeLock.emit(not self.preview_running)
            self.preview_running = False
            self._enableSaveButton()
            if self.camera_thread is not None:
                self.camera_thread.stop()
                self.camera_thread = None
            self.camera.close()
        else:
            self.camera.close()  # close any existing connection
            self.parse_settings_widget()
            [status, message] = self.camera.open(source=self.settings["source"], exposure=self.settings["exposure"])
            if status:
                self.logger.log_error(message)
                self.logger.info_popup(f"VenusUSB2 plugin : {message}")
            else:
                self.settingsWidget.saveButton.setEnabled(False)
                self._GUIchange_deviceConnected(self.preview_running)
                self.cl.closeLock.emit(not self.preview_running)
                # Create new thread for this session
                self._create_new_camera_thread()
                self.camera_thread.start()
                self.preview_running = True

    def _saveAction(self):
        [status, info] = self._parseSaveData()
        if status:
            self.logger.info_popup(f"VenusUSB2 plugin : {info['Error message']}")
            return [status, info]
        self.q_img.save(
            self.settings["address"] + os.sep + self.settings["filename"] + ".jpeg",
            format="jpeg",
        )

    ########Functions
    ###############GUI setting up

    def _initGUI(
        self,
        plugin_info: dict,
    ):
        """Initialize the GUI with the provided plugin information.

        Args:
            plugin_info (dict): A dictionary containing plugin settings.
        """
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK

        self.settingsWidget.cameraSource.setText(plugin_info["source"])
        self.settingsWidget.saveButton.setEnabled(False)
        self.settingsWidget.lineEdit_path.setText(plugin_info["address"])
        self.settingsWidget.lineEdit_filename.setText(plugin_info["filename"])
        self.settingsWidget.exposure.setCurrentText(str(plugin_info["exposure"]))

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
        # NOTE: status is inverted, i.e. when preview is started received status should False, when preview is stopped status should be True
        if status:
            self.settingsWidget.connectionIndicator.setStyleSheet(ConnectionIndicatorStyle.RED_DISCONNECTED.value)
        else:
            self.settingsWidget.connectionIndicator.setStyleSheet(ConnectionIndicatorStyle.GREEN_CONNECTED.value)
        self.settingsWidget.sourceBox.setEnabled(status)

    def _enableSaveButton(self):
        if not self.q_img:
            self.settingsWidget.saveButton.setEnabled(False)
        else:
            self.settingsWidget.saveButton.setEnabled(True)

    def _exp_slider_change(self):
        self.parse_settings_widget()
        self.camera.set_exposure(self.settings["exposure"])

    ########Functions
    ########plugins interraction
    # These are hooked to the plugin container and sent to the main app. Then they are connected to the msg slots.

    def _get_public_methods(self, function: str) -> dict:
        """
        Returns a nested dictionary of public methods for the plugin
        """

        return get_public_methods(self)

    @public
    def camera_open(self):
        """Opens the camera using current settings.
        Returns:
            0 - no error
            ~0 - error (add error code later on if needed)
        """
        self.parse_settings_widget()
        source = self.settings["source"]
        exposure = self.settings["exposure"]
        status, message = self.camera.open(source=source, exposure=exposure)
        if status:
            return status, message
        else:
            self._GUIchange_deviceConnected(False)
            return [0, "VenusUSB2 ok"]

    @public
    def camera_close(self):
        self.camera.close()
        self._GUIchange_deviceConnected(True)

    @public
    def camera_capture_image(self):
        parse_status, settings = self.parse_settings_widget()
        if parse_status == 0:
            source = settings["source"]
            exposure = settings["exposure"]
            try:
                status, img = self.camera.capture_image(source, exposure)
                if status != 0:
                    img = {"Error message": f"VenusUSB2 plugin : {img}"}
            except Exception as e:
                status = 4
                img = {"Error message": f"VenusUSB2 plugin : exception in capturing image: {str(e)}"}
        else:
            status = 1
            img = {"Error message": "value error in parsing settings"}

        return status, img

    @public
    def get_thread(self):
        return self.camera_thread

    def _parseSaveData(self) -> tuple[int, dict]:
        self.settings["address"] = self.settingsWidget.lineEdit_path.text()
        if not os.path.isdir(self.settings["address"] + os.sep):
            self.logger.log_error("address string should point to a valid directory")
            return [
                1,
                {"Error message": "VenusUSB2 plugin : address string should point to a valid directory"},
            ]
        self.settings["filename"] = self.settingsWidget.lineEdit_filename.text()
        if not is_valid_filename(self.settings["filename"]):
            self.logger.log_error("filename is not valid")
            self.logger.info_popup("VenusUSB2 plugin : filename is not valid")
            return [1, {"Error message": "VenusUSB2 plugin : filename is not valid"}]
        return [0, {"Error message": "OK"}]
