#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets

from plugin import Plugin
from VenusUSB2GUI import VenusUSB2GUI
import cv2


class pyIVLS_VenusUSB2_plugin(Plugin):
    """Hooks for VenusUSB2 camera plugin"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.name = "VenusUSB2"
        self.camera_control = VenusUSB2GUI()
        super().__init__()

    @hookimpl
    def get_setup_interface(self, pm, plugin_data) -> dict:
        """ Returns GUI

        Returns:
            dict: name, widget
        """
        ##IRtodo#### add check if (error) show message and return error
        self.camera_control.initGUI(plugin_data[self.name]["settings"])
        return {self.name: self.camera_control.settingsWidget}

    @hookimpl
    def get_MDI_interface(self, args = None) -> dict:
        """ Returns MDI window for camera preview

        Returns:
            dict: name, widget
        """
        return {self.name: self.camera_control.previewWidget}

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
