#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets

from plugins.plugin import Plugin
from plugins.VenusUSB2.VenusUSB2 import VenusUSB2
import cv2


class pyIVLS_VenusUSB2_plugin(Plugin):
    """Hooks for VenusUSB2 camera plugin"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.camera = VenusUSB2()
        super().__init__()

    @hookimpl
    def get_setup_interface(self, pm, plugin_data) -> dict:
        """Sets up camera, preview, and save buttons for VenusUSB2 camera plugin

        Returns:
            dict: name, widget
        """
        self.setup(pm, plugin_data)

        return {self.plugin_name: self._connect_buttons(self.camera.settingsWidget)}

    @hookimpl
    def get_functions(self, args):
        """Returns a dictionary of publicly accessible functions.

        Args:
            args (dict): function

        Returns:
            dict: functions
        """

        if args.get("function") == self.plugin_info["function"]:
            return self.get_public_methods()

    def _connect_buttons(self, settingsWidget):
        preview_button = settingsWidget.findChild(
            QtWidgets.QPushButton, "cameraPreview"
        )
        save_button = settingsWidget.findChild(QtWidgets.QPushButton, "cameraSave")
        # Connect widget buttons to functions
        preview_button.clicked.connect(self.camera.preview_button)
        save_button.clicked.connect(self.camera.save_button)
        return settingsWidget

    def open(self) -> tuple:
        """Open the device.

        Returns:
            tuple: name, success
        """
        if self.camera.open_camera():
            return (self.plugin_name, True)
        return (self.plugin_name, False)

    def camera_get_image(self) -> cv2.typing.MatLike:
        """returns the image from the camera

        :return: image from the camera
        """
        return self.camera.capture_image()
