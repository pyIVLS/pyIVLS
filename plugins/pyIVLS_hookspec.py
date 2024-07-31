#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets


class pyIVLS_hookspec:
    hookspec = pluggy.HookspecMarker("pyIVLS")

    @hookspec
    def get_setup_interface(self) -> dict:
        """returns a widget for a tab in setup, and probably data for the setup structure

        :plugin_type: as all the plugins will be rolled in one loop, but plugins will be of different types, not all of them should return smth.
        This argument will allow the specific implementation of the hook to identify if any response is needed or not.
        :return: dict containing widget and setup structure
        """

    @hookspec
    def camera_preview(self):
        """Preview the camera stream"""

    @hookspec
    def camera_set_source(self, source: str) -> bool:
        """Set the camera source"""

    @hookspec
    def camera_set_exposure(self, exposure: int) -> bool:
        """Set the camera exposure"""

    @hookspec
    def parse_settings_widget(self, settings: QtWidgets.QWidget) -> dict:
        """Parse the settings widget"""
