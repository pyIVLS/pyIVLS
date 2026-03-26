import os
import copy
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from plugin_components import public, ConnectionIndicatorStyle, get_public_methods, LoggingHelper, DependencyManager


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
        dependencies = {"contactingmove": ["parse_settings_widget", "setSettings", "verify_contact"]}
        self.dm = DependencyManager("verifyContact", dependencies)

        # Internal settings storage
        self.settings = {}

        # connect button
        self.settingsWidget.pushButton.clicked.connect(self._on_verify_contact)

    def _on_verify_contact(self):
        status, state = self.parse_settings_widget()
        if status != 0:
            self.logger.log_warn(f"Parse settings failed: {state}")
            return

        status, state = self._verify_functionality()

        if status != 0:
            self.logger.log_warn(f"Verify contact failed: {state}")
        else:
            self.logger.log_info(f"Verify contact successful: {state}")

    def _verify_functionality(self):
        func_dict = self.dm.function_dict
        contacting_functions = func_dict["contactingmove"]
        contacting_functions = contacting_functions[self.settings["contactingmove"]]
        contacting_functions["setSettings"](self.settings["contactingmove_settings"])  # no return
        status, state = contacting_functions["verify_contact"]()
        return status, state

    def _get_public_methods(self):
        return get_public_methods(self)

    def setup(self, settings: dict) -> QWidget:
        self.settings = settings
        # Setup the UI elements with the provided settings
        self.dm.initialize_dependency_selection(settings)
        self._refresh_dependency_box(settings)

        return self.settingsWidget

    def _refresh_dependency_box(self, settings: dict | None = None) -> None:
        available = self.dm.get_available_dependency_plugins().get("contactingmove", [])
        self.settingsWidget.touchDetBox.clear()
        self.settingsWidget.touchDetBox.addItems(available)
        selected = (settings or {}).get("contactingmove", "")
        if selected and selected in available:
            self.settingsWidget.touchDetBox.setCurrentText(selected)

    @public
    def parse_settings_widget(self) -> tuple[int, dict]:
        """Parses the current settings from the settings widget.

        Returns:
            tuple: (status_code, settings_dict)
                status_code: 0 if successful, 1 if error
                settings_dict: dictionary of current settings
        """
        parsed = copy.deepcopy(self.settings)
        parsed["contactingmove"] = self.settingsWidget.touchDetBox.currentText()
        result = self.dm.parse_dependencies(parsed)
        status, state = result
        if status != 0:
            return status, state
        self.settings = state
        return 0, self.settings

    @public
    def setSettings(self, settings: dict) -> None:
        """Sets the plugin settings from the sequence builder in .ini format."""
        self.logger.log_debug(f"Setting settings for touchDetect plugin: {settings}")
        self.settings = copy.deepcopy(settings)

    @public
    def sequenceStep(self, postfix: str) -> tuple[int, dict]:
        """Performs the sequence step by moving all configured manipulators to contact."""
        self.logger.log_info(f"Starting touchDetect sequence step with postfix: {postfix}")

        # Execute move to contact for all configured manipulators
        status, state = self._verify_functionality()

        if status != 0:
            return (status, state)

        return (0, {"Error message": "ok"})
