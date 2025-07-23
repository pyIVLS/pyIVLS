"""
This is a specTimeIV plugin implementation for pyIVLS

The function of the plugin is to measure current, voltage and spectrum change in time
Combines SMU and spectrometer functionality

This file provides:
- functions that implement functionality of the hooks
- GUI functionality - code that interacts with Qt GUI elements
"""

import os
import copy
from typing import Optional, Tuple, Dict, Any, List

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject, pyqtSignal

# Import utility classes and functions
from specTimeIV_utils import PluginException, LoggingHelper, PluginBaseTemplate


class SpecTimeIVGUI(QObject):
    """GUI implementation for specTimeIV plugin."""

    non_public_methods = []
    public_methods = ["parse_settings_widget", "set_running", "setSettings", "sequenceStep", "set_gui_from_settings"]

    # Signals
    log_message = pyqtSignal(str)
    info_message = pyqtSignal(str)

    def __init__(self):
        super(SpecTimeIVGUI, self).__init__()
        self.verbose = True

        # Define dependencies
        self.dependency = {
            "smu": ["parse_settings_widget", "smu_connect", "smu_init", "smu_outputOFF", "smu_outputON", "smu_disconnect", "set_running", "smu_setOutput", "smu_channelNames", "smu_getIV"],
            "spectrometer": ["parse_settings_widget", "setSettings", "spectrometerConnect", "spectrometerDisconnect", "spectrometerSetIntegrationTime", "spectrometerGetIntegrationTime", "spectrometerStartScan", "spectrometerGetSpectrum", "spectrometerGetScan"],
        }

        # Initialize path
        self.path = os.path.dirname(__file__) + os.path.sep

        # Create settings widget - would need to import appropriate UI class
        self.settingsWidget = QWidget()
        # self.ui = Ui_Form()  # Would need proper UI class import
        # self.ui.setupUi(self.settingsWidget)

        # For now, create a placeholder UI object
        class PlaceholderUI:
            pass

        self.ui = PlaceholderUI()

        # Initialize template with all utilities
        self.template = PluginBaseTemplate(self.ui, self.dependency)

        # Initialize state
        self.settings = {}
        self.function_dict = {}
        self.missing_functions = []
        self.smu_settings = {}
        self.spectro_settings = {}

    def emit_log(self, status: int, state: Dict[str, Any]) -> None:
        """Emit a standardized log message."""
        LoggingHelper.emit_log(self, status, state)

    def _log_verbose(self, message: str) -> None:
        """Log a message if verbose mode is enabled."""
        LoggingHelper.log_verbose(self, message)

    def _connect_signals(self) -> None:
        """Connect UI signals to slots."""
        signal_map = {
            "stopTimerCheckBox": ("stateChanged", self._stopTimerChanged),
            "smuBox": ("currentIndexChanged", self._smu_plugin_changed),
            "spectroBox": ("currentIndexChanged", self._spectrometer_plugin_changed),
            "comboBox_inject": ("currentIndexChanged", self._source_inject_changed),
        }

        try:
            self.template.signal_connector.connect_common_signals(signal_map)
        except AttributeError as e:
            # Let missing widgets fail clearly
            self._log_verbose(f"Signal connection failed: {e}")

    def parse_settings_widget(self) -> Tuple[int, Any]:
        """Parse the settings widget for the specTimeIV plugin."""
        self._log_verbose("Entering parse_settings_widget")

        if not self.function_dict:
            return (1, "Function dictionary not initialized")

        # Validate dependencies
        missing = self.template.validate_dependencies(self.function_dict)
        if missing:
            return (3, {"Error message": "Missing functions", "Missing functions": missing})

        try:
            # Parse plugin selections
            self.settings["smu"] = self.template.ui_accessor.get_current_text("smuBox")
            self.settings["spectrometer"] = self.template.ui_accessor.get_current_text("spectroBox")

            # Validate plugin selections
            if self.settings["smu"] not in self.function_dict.get("smu", {}):
                return (3, {"Error message": "SMU plugin not found"})
            if self.settings["spectrometer"] not in self.function_dict.get("spectrometer", {}):
                return (3, {"Error message": "Spectrometer plugin not found"})

            # Parse dependency settings
            status, result = self.template.settings_manager.parse_dependency_settings(self.function_dict, self.settings)
            if status:
                return (status, result)

            # Safely update settings if result is a dictionary
            if isinstance(result, dict):
                self.settings.update(result)

            # Parse basic time settings
            time_settings = self.template.settings_manager.parse_basic_time_settings()
            self.settings.update(time_settings)

            # Parse SMU settings
            smu_settings = self.template.settings_manager.parse_smu_basic_settings()
            self.settings.update(smu_settings)

            # Store sub-settings for later use
            self.smu_settings = self.settings.get("smu_settings", {})
            self.spectro_settings = self.settings.get("spectro_settings", {})

            self._log_verbose("Successfully parsed settings")
            return (0, self.settings.copy())

        except Exception as e:
            error_msg = f"Error parsing settings: {e}"
            self._log_verbose(error_msg)
            return (1, {"Error message": error_msg})

    def setSettings(self, settings: Dict[str, Any]) -> None:
        """Set the settings for the plugin."""
        self._log_verbose(f"Setting settings: {settings}")
        self.settings = copy.deepcopy(settings)
        self.smu_settings = settings.get("smu_settings", {})
        self.spectro_settings = settings.get("spectro_settings", {})

    def set_gui_from_settings(self) -> None:
        """Update GUI from internal settings."""
        try:
            # Set basic settings
            if "timestep" in self.settings:
                self.template.ui_accessor.set_text("step_lineEdit", str(self.settings["timestep"]))

            if "stoptimer" in self.settings:
                self.template.ui_accessor.set_checked("stopTimerCheckBox", self.settings["stoptimer"])

            if "stopafter" in self.settings and self.settings["stoptimer"]:
                self.template.ui_accessor.set_text("stopAfterLineEdit", str(self.settings["stopafter"]))

            # Set SMU settings
            if "channel" in self.settings:
                self.template.ui_accessor.set_current_text("comboBox_channel", self.settings["channel"])

            if "inject" in self.settings:
                self.template.ui_accessor.set_current_text("comboBox_inject", self.settings["inject"])

            # Update GUI state
            self._update_GUI_state()

        except Exception as e:
            self._log_verbose(f"Error setting GUI from settings: {e}")

    def _update_GUI_state(self) -> None:
        """Update GUI state based on current settings."""
        try:
            # Update timer widgets
            timer_enabled = self.template.ui_accessor.is_checked("stopTimerCheckBox")
            self.template.gui_manager.update_timer_widgets(timer_enabled)

            # Update inject labels
            inject_type = self.template.ui_accessor.get_current_text("comboBox_inject")
            self.template.gui_manager.update_inject_labels(inject_type, "source")

        except Exception as e:
            self._log_verbose(f"Error updating GUI state: {e}")

    def _stopTimerChanged(self, state: int) -> None:
        """Handle stop timer checkbox state change."""
        enabled = self.template.ui_accessor.is_checked("stopTimerCheckBox")
        self.template.gui_manager.update_timer_widgets(enabled)

    def _source_inject_changed(self, index: int) -> None:
        """Handle source inject type change."""
        inject_type = self.template.ui_accessor.get_current_text("comboBox_inject")
        self.template.gui_manager.update_inject_labels(inject_type, "source")

    def _smu_plugin_changed(self, index: Optional[int] = None) -> None:
        """Handle SMU plugin selection change."""
        smu_selection = self.template.ui_accessor.get_current_text("smuBox")
        if smu_selection in self.function_dict.get("smu", {}):
            try:
                available_channels = self.function_dict["smu"][smu_selection]["smu_channelNames"]()
                # Clear and populate channel combo box
                channel_combo = getattr(self.ui, "comboBox_channel")
                channel_combo.clear()
                channel_combo.addItems(available_channels)
            except Exception as e:
                self._log_verbose(f"Error updating SMU channels: {e}")

    def _spectrometer_plugin_changed(self, index: Optional[int] = None) -> None:
        """Handle spectrometer plugin selection change."""
        self._log_verbose("Spectrometer plugin changed")

    def set_running(self, status: bool) -> None:
        """Set the running state of the plugin."""
        try:
            group_widgets = ["groupBox", "groupBox_SMUGeneral"]
            self.template.gui_manager.set_running_state(status, "runButton", "stopButton", group_widgets)
            if status:
                self._update_GUI_state()
        except Exception as e:
            self._log_verbose(f"Error setting running state: {e}")

    def _getPublicFunctions(self, function_dict: Dict[str, Any]) -> List[str]:
        """Validate public functions."""
        self.missing_functions = self.template.validate_dependencies(function_dict)
        self.function_dict = function_dict if not self.missing_functions else {}
        return self.missing_functions

    def _getLogSignal(self):
        """Get log signal."""
        return self.log_message

    def _getInfoSignal(self):
        """Get info signal."""
        return self.info_message

    def _get_public_methods(self) -> Dict[str, Any]:
        """Get public methods for the plugin."""
        return self.template.get_public_methods(self.public_methods, self.non_public_methods)

    def sequenceStep(self, postfix: str) -> None:
        """Execute a sequence step."""
        self._log_verbose(f"Executing sequence step with postfix: {postfix}")

        smu_name = None
        spectro_name = None

        try:
            # Update filenames with postfix
            if "spectro_settings" in self.settings:
                self.spectro_settings["filename"] = self.spectro_settings.get("filename", "") + postfix

            smu_name = self.settings["smu"]
            spectro_name = self.settings["spectrometer"]

            # Connect SMU
            status, message = self.function_dict["smu"][smu_name]["smu_connect"]()
            if status:
                raise PluginException(f"SMU connection failed: {message}")

            # Connect spectrometer
            self.function_dict["spectrometer"][spectro_name]["setSettings"](self.spectro_settings)
            status, message = self.function_dict["spectrometer"][spectro_name]["spectrometerConnect"]()
            if status:
                raise PluginException(f"Spectrometer connection failed: {message}")

            # Initialize SMU
            self._smuInit()

            # Execute measurement implementation
            self._specTimeIVImplementation()

        except Exception as e:
            self._log_verbose(f"Sequence step failed: {e}")
        finally:
            # Cleanup connections
            try:
                if smu_name:
                    self.function_dict["smu"][smu_name]["smu_outputOFF"]()
                    self.function_dict["smu"][smu_name]["smu_disconnect"]()
                if spectro_name:
                    self.function_dict["spectrometer"][spectro_name]["spectrometerDisconnect"]()
            except Exception as e:
                self._log_verbose(f"Cleanup failed: {e}")

    def _smuInit(self) -> None:
        """Initialize SMU with current settings."""
        self._log_verbose("Initializing SMU")

        smu_config = {
            "pulse": False,
            "source": self.settings["channel"],
            "type": "v" if self.settings["inject"] == "voltage" else "i",
            "single_ch": True,  # Simplified for this implementation
            "sourcenplc": self.settings.get("sourcenplc", 1.0),
            "delay": True,  # Auto delay
            "limit": self.settings.get("sourcelimit", 1.0),
            "sourcehighc": self.smu_settings.get("sourcehighc", False),
            "start": self.settings.get("sourcesetvalue", 0.0),
            "sourcesense": 1 if self.settings.get("sourcesensemode") == "4 wire" else 0,
        }

        smu_name = self.settings["smu"]
        status = self.function_dict["smu"][smu_name]["smu_init"](smu_config)
        if status:
            raise PluginException("SMU initialization failed")

    def _specTimeIVImplementation(self) -> None:
        """Main measurement implementation."""
        self._log_verbose("Starting specTimeIV measurement")

        # This is a simplified implementation - would need to be expanded
        # based on actual measurement requirements

        timestep = self.settings.get("timestep", 1.0)
        stop_time = self.settings.get("stopafter", 10.0) if self.settings.get("stoptimer") else 60.0

        smu_name = self.settings["smu"]
        spectro_name = self.settings["spectrometer"]

        # Measurement loop would go here
        start_time = 0
        while start_time < stop_time:
            # Get SMU measurements
            status, iv_data = self.function_dict["smu"][smu_name]["smu_getIV"](self.settings["channel"])
            if status:
                break

            # Get spectrum measurement
            status, spectrum = self.function_dict["spectrometer"][spectro_name]["spectrometerGetSpectrum"]()
            if status:
                break

            # Process and save data here

            start_time += timestep

        self._log_verbose("Measurement completed")
