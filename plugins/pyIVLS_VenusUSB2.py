#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets

from plugins.VenusUSB2.cameraHAL import VenusUSB2
import cv2


class pyIVLS_VenusUSB2_plugin:
    """Hooks for VenusUSB2 camera plugin"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.camera = VenusUSB2()

    @hookimpl
    def get_setup_interface(self, pm) -> dict:
        """Sets up camera, preview, and save buttons for VenusUSB2 camera plugin

        Returns:
            dict: name, widget
        """
        print("VenusUSB2 plugin is here")
        preview_button = self.camera.settingsWidget.findChild(
            QtWidgets.QPushButton, "cameraPreview"
        )
        save_button = self.camera.settingsWidget.findChild(
            QtWidgets.QPushButton, "cameraSave"
        )
        # Connect widget buttons to functions
        preview_button.clicked.connect(self.camera.preview_button)
        save_button.clicked.connect(self.camera.save_button)

        self.camera.pm = pm

        return {"VenusUSB2": self.camera.settingsWidget}

    @hookimpl
    def camera_get_image(self) -> cv2.typing.MatLike:
        """returns the image from the camera

        :return: image from the camera
        """
        print("Getting image from VenusUSB2 camera")
        return self.camera.capture_image()
