#!/usr/bin/python3.8
import pluggy
from plugins.VenusUSB2.cameraHAL import VenusUSB2

# For parsing the settings widget
from PyQt6 import QtWidgets


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

        return {"VenusUSB2": self.camera.settingsWidget}

    @hookimpl
    def camera_preview(self):
        """Preview the camera stream"""
        self.camera.preview()

    @hookimpl
    def camera_set_source(self, source: str) -> bool:
        """Set the camera source"""
        return self.camera.set_source(source)

    @hookimpl
    def camera_set_exposure(self, exposure: int) -> bool:
        """Set the camera exposure"""
        return self.camera.set_exposure(exposure)

    @hookimpl
    def parse_settings_widget(self, settings: QtWidgets.QWidget) -> dict:
        exposureSlider = settings.findChild(QtWidgets.QSlider, "exposureSlider")
        sourceInput = settings.findChild(QtWidgets.QComboBox, "sourceInput")
        exposure_value = exposureSlider.value()
        source_input = sourceInput.currentText()

        print(f"Exposure: {exposure_value}, Source: {source_input}")
