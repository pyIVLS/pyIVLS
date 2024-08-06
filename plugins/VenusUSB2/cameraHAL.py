import cv2 as cv
import os

import numpy as np
from PyQt6 import uic
from PyQt6 import QtWidgets
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

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


class VenusUSB2(QObject):
    """Handles communication with the VenusUSB2 camera

    Args:
        QObject (QObject): Inherits from QObject
    """

    def __init__(self):
        # FIXME check the exposures
        self.source = "/dev/video2"
        self.exposures = [0, 1, 2, 5, 10, 20, 39, 78, 156, 312]
        self.pm: Optional[pluggy.PluginManager] = None

        # Initialize the settings widget
        QObject.__init__(self)
        self.path = os.path.dirname(__file__) + os.path.sep
        self.settingsWidget = uic.loadUi(self.path + "camera_settingsWidget.ui")

        # Initialize labels that might be modified:
        self.source_label = self.settingsWidget.findChild(
            QtWidgets.QLabel, "sourceLabel"
        )
        self.pm = None

    def open_camera(self) -> bool:
        """Opens the camera using the source

        Returns:
            bool: pass/fail
        """
        # Method to open the camera
        self.cap = cv.VideoCapture(self.source)
        if self.cap.isOpened():
            self.source_label.setText(f"Source open: {self.source}")
            return True
        self.source_label.setText(f"Failed to open source: {self.source}")
        return False

    def close_camera(self):
        """Pretty self explanatory"""
        self.cap.release()

    # FIXME: hard crash when trying to capture image without opening camera.
    def capture_image(self) -> cv.typing.MatLike:
        """Captures an image from the camera. NOTE: returns color image

        Returns:
            matlike: The image
        """
        # Method to capture an image
        if self.cap.isOpened():
            ret, frame = self.cap.read()
        else:
            self.open_camera()
            ret, frame = self.cap.read()
        return frame

    def _preview(self):
        """Preview the opened camera feed. Open() needs to called before this. 'q' exits the preview."""
        # Method to preview the camera feed
        while True:
            frame = self.capture_image()
            cv.imshow("Camera Feed", frame)
            if cv.waitKey(1) & 0xFF == ord("q"):
                break

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

        # Verify the exposure value
        current_exposure = self.cap.get(cv.CAP_PROP_EXPOSURE)
        print(f"Current exposure: {current_exposure}")

    def get_exposure(self):
        """Getter for the current exposure value

        Returns:
            _type_: current exposure as set in the camera
        """
        # Method to get the exposure value
        return self.cap.get(cv.CAP_PROP_EXPOSURE)

    # FIXME: just for windows, remove the int conversion when porting to linux
    def _set_source(self, source):
        """Sets the camera feed source

        Args:
            source (str): device string for the camera
        """
        # Method to set the source
        self.source = source

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

        print(f"Exposure: {exposure_value}, Source: {source_input}")

        return {"exposure": exposure_value, "source": source_input}

    def preview_button(self):
        """interface for the preview button. Opens the camera, sets the exposure and previews the feed"""
        settings = self.parse_settings_widget()
        self._set_source(settings["source"])
        if self.open_camera():
            self._set_exposure(settings["exposure"])
            self._preview()

    def save_button(self) -> bool:
        """interface for the save button. Opens the camera, sets the exposure and returns True if successful. Can be called multiple times and just replaces the current self.cap

        Returns:
            bool: pass/fail
        """
        settings = self.parse_settings_widget()
        self._set_source(settings["source"])
        if self.open_camera():
            self._set_exposure(settings["exposure"])
            return True
        return False
