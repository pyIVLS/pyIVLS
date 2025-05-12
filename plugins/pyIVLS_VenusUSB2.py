#!/usr/bin/python3.8
import pluggy

from plugins.plugin import Plugin_hookspec
from plugins.VenusUSB2.VenusUSB2GUI import VenusUSB2GUI


class pyIVLS_VenusUSB2_plugin(Plugin_hookspec):
    """Hooks for VenusUSB2 camera plugin"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        super().__init__("VenusUSB2", [], "camera")
        self.camera_control = VenusUSB2GUI()

    @hookimpl
    def get_setup_interface(self, plugin_data: dict) -> dict:
        """Returns GUI
        Args:
            plugin_data (dict): plugin data read from .ini to read initial settings.

        Returns:
            dict: name, widget
        """
        self.camera_control._initGUI(plugin_data[self.name]["settings"])
        return {self.name: self.camera_control.settingsWidget}

    @hookimpl
    def get_MDI_interface(self, args=None) -> dict:
        """Returns MDI window for camera preview

        Returns:
            dict: name, widget
        """
        return {self.name: self.camera_control.previewWidget}

    @hookimpl
    def get_functions(self, args=None):
        """Returns a dictionary of publicly accessible functions.

        Args:
            args (dict): function

        Returns:
            dict: functions
        """
        if args is None or args.get("function") == self.plugin_function:
            return {self.name: self._get_public_methods()}

    @hookimpl
    def get_log(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.name: self.camera_control._getLogSignal()}

    @hookimpl
    def get_info(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.name: self.camera_control._getInfoSignal()}

    @hookimpl
    def get_closeLock(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.name: self.camera_control._getCloseLockSignal()}

    ####
    # functions accessible from other plugins:
    # not hooks, but public functions.
    ####

    def camera_open(self) -> tuple:
        """Open the device.

        Returns:
            tuple: name, success
        """
        if self.camera.open_camera():
            return (self.name, True)
        return (self.name, False)

    def camera_get_image(self):
        """returns the image from the camera

        :return: image from the camera
        """
        return self.camera.capture_image()
