#!/usr/bin/python3.8
import pluggy
from plugins.VenusUSB2.cameraHAL import VenusUSB2


class pyIVLS_VenusUSB2_plugin:
    hookimpl = pluggy.HookimplMarker("pyIVLS")

    @hookimpl
    def get_setup_interface(self):
        """returns a widget for a tab in setup, and probably data for the setup structure

        :plugin_type: as all the plugins will be rolled in one loop, but plugins will be of different types, not all of them should return smth.
        This argument will allow the specific implementation of the hook to identify if any response is needed or not.
        :return: dict containing widget and setup structure
        """
        self.camera = VenusUSB2()
        print("I am getting info for the camera plugin")

        return {VenusUSB2: self.camera.settingsWidget}
