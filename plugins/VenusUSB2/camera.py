import cv2 as cv
import os

import numpy as np
from PyQt6 import uic
from PyQt6 import QtWidgets
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QImage, QPixmap

from typing import Optional
import pluggy

"""
    User Controls

                        brightness 0x00980900 (int)    : min=0 max=255 step=1 default=128 value=128
                        contrast 0x00980901 (int)    : min=0 max=255 step=1 default=128 value=128
                        saturation 0x00980902 (int)    : min=0 max=255 step=1 default=64 value=64
        white_balance_automatic 0x0098090c (bool)   : default=1 value=1
        white_balance_temperature 0x0098091a (int)    : min=1 max=5 step=1 default=1 value=1 flags=inactive
                        sharpness 0x0098091b (int)    : min=0 max=255 step=1 default=128 value=128

    Camera Controls

                    auto_exposure 0x009a0901 (menu)   : min=0 max=3 default=3 value=1 (Manual Mode)
                1: Manual Mode
            exposure_time_absolute 0x009a0902 (int)    : min=0 max=320 step=1 default=20 value=10
        focus_automatic_continuous 0x009a090c (bool)   : default=0 value=0
"""


class VenusUSB2:
    """Handles communication with the VenusUSB2 camera

    Args:
        QObject (QObject): Inherits from QObject
    """

    def __init__(self):
        # FIXME check the exposures
        self.exposures = [1, 1, 2, 5, 10, 20, 39, 78, 156, 312]
        self.pm: Optional[pluggy.PluginManager] = None

        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        filename = (
            os.path.splitext(os.path.basename(__file__))[0] + "_settingsWidget.ui"
        )
        self.settingsWidget = uic.loadUi(self.path + filename)

        # Initialize labels that might be modified:
        self.source_label = self.settingsWidget.findChild(
            QtWidgets.QLabel, "sourceLabel"
        )

        self.preview_label = self.settingsWidget.findChild(
            QtWidgets.QLabel, "previewLabel"
        )

        self.pm = None
        # Initialize cap as empty capture
        self.cap = cv.VideoCapture()
        self.save_button()

        # Set a timer for the camera feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.preview_running = False

    def open_camera(self, source=None, exposure=None) -> bool:
        """Opens the camera using current settings.

        Returns:
            bool: pass/fail
        """
        if source is None:
            source = self.settings["source"]
        if exposure is None:
            exposure = self.settings["exposure"]

        self.cap.open(source)
        if self.cap.isOpened():
            self.source_label.setText(f"Source open: {source}")
            self._set_exposure(exposure)
            # Set buffer size to 1.
            self.cap.set(cv.CAP_PROP_BUFFERSIZE, 1)
            return True
        self.source_label.setText(f"Failed to open source: {source}")
        return False

    def close_camera(self):
        """Pretty self explanatory"""
        self.cap.release()

    # FIXME: Maybe this should send more info if an error is encountered.
    # Info could be used in AFFINE to display a message to the user.
    def capture_image(self) -> cv.typing.MatLike:
        """Captures an image from the camera. NOTE: returns color image

        Returns:
            matlike: The image
        """
        # is the cap opened?
        # HACK: Camera is set to buffer 1 frame, so 1 frame is discarded to get current state.
        if self.cap.isOpened():
            self.cap.read()
            _, frame = self.cap.read()
        elif self.open_camera():
            self.cap.read()
            _, frame = self.cap.read()
        else:
            frame = np.zeros((480, 640, 3), np.uint8)
        return frame

    def _preview(self):
        if self.preview_running:
            self.timer.stop()
            self.preview_label.setText("Preview stopped")
            self.preview_running = False
        else:
            self.timer.start(30)
            self.preview_running = True

    def update_frame(self):
        frame = self.capture_image()
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.preview_label.setPixmap(QPixmap.fromImage(q_img))

    # FIXME: Might not work on windows
    def _set_exposure(self, exposure):
        """Sets the exposure for the camera

        Args:
            exposure (int): index of the possible exposure. See self.exposures for the values
        """
        # Method to set the exposure
        assert 0 <= exposure <= 9, "Error: Exposure value out of range"

        # Check if the camera supports setting exposure
        if not self.cap.get(cv.CAP_PROP_EXPOSURE):
            print("Camera does not support setting exposure.")
            return

        # Set the exposure
        success = self.cap.set(cv.CAP_PROP_EXPOSURE, self.exposures[exposure])
        if success:
            print(f"Exposure set to {self.exposures[exposure]}")
        else:
            print("Failed to set exposure.")

    def get_exposure(self):
        """Getter for the current exposure value

        Returns:
            _type_: current exposure as set in the camera
        """
        # Method to get the exposure value
        return self.cap.get(cv.CAP_PROP_EXPOSURE)

    def parse_settings_widget(self) -> dict:
        """Parses the settings widget for the camera. Extracts current values

        Returns:
            dict: setting -> value
        """
        exposureSlider = self.settingsWidget.findChild(
            QtWidgets.QSlider, "cameraExposure"
        )
        sourceInput = self.settingsWidget.findChild(QtWidgets.QLineEdit, "cameraSource")
        exposure_value = exposureSlider.value()
        source_input = sourceInput.text()

        return {"exposure": exposure_value, "source": source_input}

    def preview_button(self):
        """interface for the preview button. Opens the camera, sets the exposure and previews the feed"""
        settings = self.parse_settings_widget()
        if self.open_camera(source=settings["source"], exposure=settings["exposure"]):
            self._preview()
            self.close_camera()

    def save_button(self) -> None:
        """interface for the save button. Updates the settings and saves them to internal dict.

        Returns:
            bool: pass/fail
        """
        self.settings = self.parse_settings_widget()
        self.close_camera()
