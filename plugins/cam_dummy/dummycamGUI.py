"""
This is a GUI plugin for DummyCamera for pyIVLS

This file should provide
- functions for interaction with other plugins (those that will be exported on get_functions hook call, these should not start with "_")
- functions that will implement functionality of the hooks (see pyIVLS_DummyCamera)
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
version 0.7
2025.06.11
otsoha
"""

import numpy as np
import os
from datetime import datetime

from PyQt6 import uic
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from dummycam import DummyCamera

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

    def run(self):
        self._running = True
        while self._running:
            status, frame = self.camera.capture_buffered()
            if status == 0:
                self.new_frame.emit(frame)
            self.msleep(self.interval_ms)

    def stop(self):
        self._running = False
        self.wait()


class DummyCameraGUI(QObject):
    """GUI for the DummyCamera plugin (minimal, only image path selection)"""

    non_public_methods = []
    public_methods = [
        "camera_open",
        "camera_close",
        "camera_capture_image",
    ]  # necessary for descendents of QObject, otherwise _get_public_methods returns a lot of QObject methods

    ########Signals

    # used to send messages to the main app
    log_message = pyqtSignal(str)
    info_message = pyqtSignal(str)
    closeLock = pyqtSignal(bool)

    def emit_log(self, status: int, state: dict) -> None:
        """
        Emits a standardized log message for status dicts or error lists.
        Args:
            status (int): status code, 0 for success, non-zero for error.
            state (dict): dictionary in the standard pyIVLS format

        """
        plugin_name = self.__class__.__name__
        # only emit if error occurred
        if status != 0:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")
            msg = state.get("Error message", "Unknown error")
            exception = state.get("Exception", "Not provided")

            log = f"{timestamp} : {plugin_name} : {status} : {msg} : Exception: {exception}"

            self.log_message.emit(log)

    ########Functions

    def __init__(self):
        super(DummyCameraGUI, self).__init__()
        self.path = os.path.dirname(__file__) + os.path.sep
        self.settingsWidget = uic.loadUi(self.path + "dummycam_settingsWidget.ui")
        self.previewWidget = uic.loadUi(self.path + "dummycam_previewWidget.ui")

        self.settings = {"image_path": ""}

        # Initialize cap as empty capture
        self.camera = DummyCamera()

        # Fill lineEdit from saved path if available
        saved_path = self._load_saved_path()
        self.settings["image_path"] = saved_path
        self.settingsWidget.lineEdit.setPlaceholderText("Select an image file")

        self.settingsWidget.lineEdit.setText(saved_path)

        self.settingsWidget.pushButton.clicked.connect(self._select_image)

    def _select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select Image",
            self.settings["image_path"],
            "Images (*.png *.jpg *.jpeg *.bmp)",
        )
        if file_path:
            self.settings["image_path"] = file_path
            self.settingsWidget.lineEdit.setText(file_path)
            self._save_path(file_path)

    def _load_saved_path(self):
        # Optionally load from a config or file, here just return empty or last used
        config_path = os.path.join(self.path, "dummycam_last_path.txt")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        return ""

    def _save_path(self, path):
        config_path = os.path.join(self.path, "dummycam_last_path.txt")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(path)

    ########Functions
    ########API methods

    def camera_open(self):
        """Open the dummy camera (load the image path)."""
        image_path = self.settingsWidget.lineEdit.text()
        status, msg = self.camera.open(source=image_path)
        if status:
            self.emit_log(status, msg)
        return status, msg

    def camera_close(self):
        self.camera.close()

    def camera_capture_image(self):
        image_path = self.settingsWidget.lineEdit.text()
        if image_path == "":
            image_path = self._load_saved_path()
        status, img = self.camera.capture_image(source=image_path)
        return status, img

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
        methods = {method: getattr(self, method) for method in dir(self) if callable(getattr(self, method)) and not method.startswith("__") and not method.startswith("_") and method in self.public_methods}
        return methods
