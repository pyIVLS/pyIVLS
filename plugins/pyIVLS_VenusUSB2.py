#!/usr/bin/python3.8
import pluggy

from plugins.VenusUSB2.VenusUSB2GUI import VenusUSB2GUI


class pyIVLS_VenusUSB2_plugin:
    """Hooks for VenusUSB2 camera plugin"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.plugin_name = "VenusUSB2"
        self.plugin_function = "camera"
        self.camera_control = VenusUSB2GUI()
        super().__init__()

    @hookimpl
    def get_setup_interface(self, plugin_data) -> dict:
        """Returns GUI

        Returns:
            dict: name, widget
        """
        self.camera_control._initGUI(plugin_data[self.plugin_name]["settings"])
        return {self.plugin_name: self.camera_control.settingsWidget}

    @hookimpl
    def get_MDI_interface(self, args=None) -> dict:
        """Returns MDI window for camera preview

        Returns:
            dict: name, widget
        """
        return {self.plugin_name: self.camera_control.previewWidget}

    @hookimpl
    def get_functions(self, args=None):
        """Returns a dictionary of publicly accessible functions.

        Args:
            args (dict): function

        Returns:
            dict: functions
        """
        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.camera_control._get_public_methods()}

    @hookimpl
    def get_log(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.camera_control._getLogSignal()}

    @hookimpl
    def get_info(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.camera_control._getInfoSignal()}

    @hookimpl
    def get_closeLock(self, args=None):
        """provides the signal for logging to main app

        :return: dict that includes the log signal
        """

        if args is None or args.get("function") == self.plugin_function:
            return {self.plugin_name: self.camera_control._getCloseLockSignal()}

    def open(self) -> tuple:
        """Open the device.

        Returns:
            tuple: name, success
        """
        if self.camera.open_camera():
            return (self.plugin_name, True)
        return (self.plugin_name, False)

    def camera_get_image(self):
        """returns the image from the camera

        :return: image from the camera
        """
        return self.camera.capture_image()
