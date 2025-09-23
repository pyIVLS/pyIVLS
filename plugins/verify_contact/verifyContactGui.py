import os
import copy
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from plugins.plugin_components import public, ConnectionIndicatorStyle, get_public_methods, LoggingHelper, DependencyManager


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
        dependency_mapper = {"contactingmove": "touchDetBox"}
        self.dm = DependencyManager("verifyContact", dependencies, self.settingsWidget, dependency_mapper)

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
        func_dict = self.dm.get_function_dict_for_dependencies()
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
        result = self.dm.validate_and_extract_dependency_settings(self.settings)
        status, state = result
        if status != 0:
            return status, state
        self.settings.update(state)
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
