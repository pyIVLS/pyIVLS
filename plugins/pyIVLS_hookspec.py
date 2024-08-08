#!/usr/bin/python3.8
import pluggy
import cv2


class pyIVLS_hookspec:
    hookspec = pluggy.HookspecMarker("pyIVLS")

    @hookspec
    def get_setup_interface(self, pm: pluggy.PluginManager) -> dict:
        """returns a widget for a tab in setup, and probably data for the setup structure

        :plugin_type: as all the plugins will be rolled in one loop, but plugins will be of different types, not all of them should return smth.
        This argument will allow the specific implementation of the hook to identify if any response is needed or not.
        :return: dict containing widget and setup structure
        """

    @hookspec
    def camera_get_image(self) -> cv2.typing.MatLike:
        """returns the image from the camera. If function = camera, this must be implemented

        :return: image from the camera
        """

    @hookspec
    def mm_change_active_device(self, dev_num):
        """Micromanipulator active device change.
        if function = micromanipulator, this must be implemented

        Args:
            *args: device number
        """

    @hookspec
    def mm_move(self, speed, x, y, z):
        """Micromanipulator move.
        if function = micromanipulator, this must be implemented

        Args:
            *args: x, y, z
        """

    @hookspec
    def mm_stop(self):
        """Micromanipulator stop.
        if function = micromanipulator, this must be implemented
        """

    @hookspec
    def get_functions(self, *args):
        """Returns available functions for a plugin. FIXME: Deprecated, use specific hooks instead.

        Returns:
            dict: _description_
        """

    @hookspec
    def affine_coords(self, x, y):
        """Affine coordinates.

        Args:
            x (float): x coordinate
            y (float): y coordinate
        """
