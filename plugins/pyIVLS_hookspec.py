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
        """returns the image from the camera

        :return: image from the camera
        """
