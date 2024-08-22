#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets

from plugins.plugin import Plugin
from plugins.VenusUSB2.venusUSB2 import VenusUSB2
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
        preview_button = self.camera.settingsWidget.findChild(
            QtWidgets.QPushButton, "cameraPreview"
        )
        save_button = self.camera.settingsWidget.findChild(
            QtWidgets.QPushButton, "cameraSave"
        )
        # Connect widget buttons to functions
        preview_button.clicked.connect(self.camera.preview_button)
        save_button.clicked.connect(self.camera.save_button)

        return {"VenusUSB2": self.camera.settingsWidget}

    def open(self, **kwargs) -> tuple[str, bool]:
        """Open the device.

        Returns:
            bool: True if open
        """
        if self.camera.open_camera():
            return ("VenusUSB2", True)
        return ("VenusUSB2", False)

    def camera_get_image(self) -> cv2.typing.MatLike:
        """returns the image from the camera

        :return: image from the camera
        """
        print("Camera hookcall")
        return self.camera.capture_image()

    @hookimpl
    def get_functions(self, args):
        if args.get("function") == "camera":
            return {
                "camera_get_image": self.camera.capture_image,
                "camera_open": self.open,
            }
