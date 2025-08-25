import os
import copy
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QComboBox, QGroupBox, QSpinBox, QLabel, QPushButton
from plugins.plugin_components import public, ConnectionIndicatorStyle, get_public_methods, LoggingHelper, DependencyManager, PyIVLSReturn


class verifyContactGUI:
    green_style = ConnectionIndicatorStyle.GREEN_CONNECTED.value
    red_style = ConnectionIndicatorStyle.RED_DISCONNECTED.value

    def __init__(self):
        self.path = os.path.dirname(__file__) + os.path.sep

        # Initialize LoggingHelper first
        self.logger = LoggingHelper(self)

        # Load UI
        self.settingsWidget: QWidget = uic.loadUi(self.path + "verifyContact_Settings.ui")  # type: ignore

        # Initialize DependencyManager
        dependencies = {"contactingmove": ["important"]}
        dependency_mapper = {"contactingmove": "touchDetBox"}
        self.dm = DependencyManager("verifyContact", dependencies, self.settingsWidget, dependency_mapper)

        # Internal settings storage
        self.settings = {}

    def _get_public_methods(self):
        return get_public_methods(self)

    def setup(self, settings: dict) -> QWidget:
        self.settings = settings
        # Setup the UI elements with the provided settings
        self.dm.setup(settings)

        return self.settingsWidget

    @public
    def parse_settings_widget(self) -> tuple[int, dict]:
        """Parses the current settings from the settings widget.

        Returns:
            tuple: (status_code, settings_dict)
                status_code: 0 if successful, 1 if error
                settings_dict: dictionary of current settings
        """
        print(f"verifyContact current settings before validation: {self.settings}")
        status, state = self.dm.validate_and_extract_dependency_settings(self.settings)
        if status != 0:
            return status, state
        print(f"verifyContact settings parsed: {self.settings}, status: {status}, state: {state}")
        return 0, self.settings
