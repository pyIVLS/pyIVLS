"""
Using composition instead of multiple inheritance,
mostly because this is similar to the existing implementations.
"""

import os
import pandas as pd
from datetime import datetime
from pathvalidate import is_valid_filename
from typing import Dict, Any, Tuple, List, Optional, Callable, Union
from enum import Enum

from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QObject, pyqtSignal


class DataOrder(Enum):
    """Enum for data ordering."""

    VOLTAGE = 1
    CURRENT = 0


class PluginException(Exception):
    """Base exception for plugin errors."""

    pass


class LoggingHelper(QObject):
    """Helper class for standard logging functionality."""

    logger_signal = pyqtSignal(str)
    info_popup_signal = pyqtSignal(str)

    def __init__(self, plugin_instance):
        self.plugin_name = plugin_instance.__class__.__name__
        super().__init__()

    def log_info(self, message: str) -> None:
        """Log informational messages with INFO flag"""
        log = f"{self.plugin_name} : INFO : {message}"
        self.logger_signal.emit(log)

    def log_debug(self, message: str) -> None:
        """Log debug messages with DEBUG flag"""
        log = f"{self.plugin_name} : DEBUG : {message}"
        self.logger_signal.emit(log)

    def log_warn(self, message: str) -> None:
        """Log warning messages with WARN flag"""
        log = f"{self.plugin_name} : WARN : {message}"
        self.logger_signal.emit(log)

    def info_popup(self, message: str) -> None:
        """show info popup, if provided"""
        self.info_popup_signal.emit(message)


class SettingsValidator:
    """Validates and parses settings with comprehensive error handling."""

    @staticmethod
    def validate_float_positive(value: str, param_name: str) -> float:
        """Validate that a string represents a positive float."""
        try:
            float_val = float(value)
            if float_val <= 0:
                raise ValueError(f"{param_name} must be positive, got {float_val}")
            return float_val
        except ValueError as e:
            raise ValueError(f"Invalid {param_name}: {e}")

    @staticmethod
    def validate_float(value: str, param_name: str) -> float:
        """Validate that a string represents a float."""
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"Invalid {param_name}: must be a number")

    @staticmethod
    def validate_directory(path: str) -> Tuple[int, str]:
        """Validate that a path points to an existing directory."""
        if not os.path.isdir(path):
            return (1, f"Directory {path} does not exist")
        return (0, "Ok")

    @staticmethod
    def validate_filename(filename: str) -> Tuple[int, str]:
        """Validate that a filename is valid."""
        if not is_valid_filename(filename):
            return (1, f"Invalid filename: {filename}")
        return (0, "Ok")

    @staticmethod
    def validate_save_data(address: str, filename: str) -> Tuple[int, str]:
        """Validate save data settings."""
        dir_status, dir_msg = SettingsValidator.validate_directory(address + os.sep)
        if dir_status:
            return (dir_status, dir_msg)

        file_status, file_msg = SettingsValidator.validate_filename(filename)
        if file_status:
            return (file_status, file_msg)

        return (0, "Ok")


class DependencyManager:
    """Manages plugin dependencies and validation."""

    def __init__(self, dependencies: Dict[str, List[str]]):
        self.dependencies = dependencies
        self.missing_functions = []

    def validate_dependencies(self, function_dict: Dict[str, Any]) -> List[str]:
        """Validate that all required dependencies are available."""
        self.missing_functions = []

        for dependency_plugin, required_functions in self.dependencies.items():
            if dependency_plugin not in function_dict:
                self.missing_functions.append(dependency_plugin)
                continue

            for function_name in required_functions:
                if function_name not in function_dict[dependency_plugin]:
                    self.missing_functions.append(f"{dependency_plugin}.{function_name}")

        return self.missing_functions

    def get_plugin_function(self, function_dict: Dict[str, Any], plugin_name: str, function_name: str):
        """Safely get a plugin function."""
        try:
            return function_dict[plugin_name][function_name]
        except KeyError:
            raise PluginException(f"Required function {function_name} not found in {plugin_name} plugin")


class UIWidgetAccessor:
    """Provides safe access to UI widgets with clear error messages when widgets don't exist."""

    def __init__(self, ui_object):
        self.ui = ui_object

    def get_text(self, widget_name: str) -> str:
        """Get text from a line edit or similar widget."""
        widget = getattr(self.ui, widget_name)
        return widget.text()

    def set_text(self, widget_name: str, text: str) -> None:
        """Set text for a line edit or similar widget."""
        widget = getattr(self.ui, widget_name)
        widget.setText(text)

    def get_current_text(self, widget_name: str) -> str:
        """Get current text from a combo box."""
        widget = getattr(self.ui, widget_name)
        return widget.currentText()

    def set_current_text(self, widget_name: str, text: str) -> None:
        """Set current text for a combo box."""
        widget = getattr(self.ui, widget_name)
        widget.setCurrentText(text)

    def is_checked(self, widget_name: str) -> bool:
        """Get checked state of a checkbox."""
        widget = getattr(self.ui, widget_name)
        return widget.isChecked()

    def set_checked(self, widget_name: str, checked: bool) -> None:
        """Set checked state of a checkbox."""
        widget = getattr(self.ui, widget_name)
        widget.setChecked(checked)

    def set_enabled(self, widget_name: str, enabled: bool) -> None:
        """Set enabled state of a widget."""
        widget = getattr(self.ui, widget_name)
        widget.setEnabled(enabled)

    def connect_signal(self, widget_name: str, signal_name: str, slot: Callable) -> None:
        """Connect a widget signal to a slot."""
        widget = getattr(self.ui, widget_name)
        signal = getattr(widget, signal_name)
        signal.connect(slot)


class SettingsParser:
    """Parses settings from UI widgets using standardized patterns."""

    def __init__(self, ui_accessor: UIWidgetAccessor, validator: SettingsValidator):
        self.ui = ui_accessor
        self.validator = validator

    def parse_float_settings(self, widget_map: Dict[str, str]) -> Dict[str, float]:
        """Parse float settings from line edit widgets."""
        result = {}
        for widget_name, setting_key in widget_map.items():
            value = self.ui.get_text(widget_name)
            result[setting_key] = self.validator.validate_float(value, setting_key)
        return result

    def parse_positive_float_settings(self, widget_map: Dict[str, str]) -> Dict[str, float]:
        """Parse positive float settings from line edit widgets."""
        result = {}
        for widget_name, setting_key in widget_map.items():
            value = self.ui.get_text(widget_name)
            result[setting_key] = self.validator.validate_float_positive(value, setting_key)
        return result

    def parse_combo_settings(self, widget_map: Dict[str, str], to_lower: bool = True) -> Dict[str, str]:
        """Parse combo box settings."""
        result = {}
        for widget_name, setting_key in widget_map.items():
            value = self.ui.get_current_text(widget_name)
            result[setting_key] = value.lower() if to_lower else value
        return result

    def parse_checkbox_settings(self, widget_map: Dict[str, str]) -> Dict[str, bool]:
        """Parse checkbox settings."""
        result = {}
        for widget_name, setting_key in widget_map.items():
            result[setting_key] = self.ui.is_checked(widget_name)
        return result

    def parse_text_settings(self, widget_map: Dict[str, str]) -> Dict[str, str]:
        """Parse text settings from line edit widgets."""
        result = {}
        for widget_name, setting_key in widget_map.items():
            result[setting_key] = self.ui.get_text(widget_name)
        return result


class SignalConnector:
    """Handles signal connections for UI widgets."""

    def __init__(self, ui_accessor: UIWidgetAccessor):
        self.ui = ui_accessor

    def connect_common_signals(self, signal_map: Dict[str, Tuple[str, Callable]]) -> None:
        """Connect common UI signals to slots.

        Args:
            signal_map: Dict mapping widget_name to (signal_name, slot_function)
        """
        for widget_name, (signal_name, slot) in signal_map.items():
            try:
                self.ui.connect_signal(widget_name, signal_name, slot)
            except AttributeError:
                # Widget doesn't exist - let it fail clearly
                raise AttributeError(f"Widget '{widget_name}' or signal '{signal_name}' not found")


class FileManager:
    """Handles file operations and path management."""

    @staticmethod
    def get_directory_dialog(parent, title: str, initial_path: str = "") -> Optional[str]:
        """Show directory selection dialog."""
        if not os.path.exists(initial_path):
            initial_path = os.getcwd()

        directory = QFileDialog.getExistingDirectory(parent, title, initial_path, QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks)
        return directory if directory else None

    @staticmethod
    def create_file_header(settings, smu_settings):
        """
        creates a header for the csv file in the old measuremnt system style

        input	smu_settings dictionary for Keithley2612GUI.py class (see Keithley2612BGUI.py)
            settings dictionary for the sweep plugin

        str containing the header

        """

        ## header may not be optimal, this is because it should repeat the structure of the headers produced by the old measurement station
        comment = "#####################"
        if settings["samplename"] == "":
            comment = f"{comment}\n#\n# measurement of {{noname}}\n#\n#"
        else:
            comment = f"{comment}\n#\n# measurement of {settings['samplename']}\n#\n#"
        comment = f"{comment}date {datetime.now().strftime('%d-%b-%Y, %H:%M:%S')}\n#"
        comment = f"{comment}Keithley source {settings['channel']}\n#"
        comment = f"{comment}Source in {settings['inject']} injection mode\n#"
        if settings["inject"] == "voltage":
            stepunit = "V"
            limitunit = "A"
        else:
            stepunit = "A"
            limitunit = "V"
        comment = f"{comment}\n#\n#"
        comment = f"{comment}Set value for time check {settings['sourcevalue']} {stepunit}\n#"
        comment = f"{comment}\n#"
        comment = f"{comment}Limit for step {settings['sourcelimit']} {limitunit}\n#"
        if settings["sourcedelaymode"] == "auto":
            comment = f"{comment}Measurement acquisition period is done in AUTO mode\n#"
        else:
            comment = f"{comment}Measurement stabilization period is{settings['sourcedelay'] / 1000} ms\n#"
        comment = f"{comment}NPLC value {settings['sourcenplc'] * 1000 / smu_settings['lineFrequency']} ms (for detected line frequency {smu_settings['lineFrequency']} Hz is {settings['sourcenplc']})\n#"
        comment = f"{comment}\n#\n#"
        comment = f"{comment}Continuous operation of the source with step time settings['timestep'] \n#\n#\n#"

        if not settings["singlechannel"]:
            comment = f"{comment}Drain in {settings['draininject']} injection mode\n#"
            if settings["inject"] == "voltage":
                stepunit = "V"
                limitunit = "A"
            else:
                stepunit = "A"
                limitunit = "V"
            comment = f"{comment}Set value for drain {settings['drainvalue']} {stepunit}\n#"
            comment = f"{comment}Limit for drain {settings['drainlimit']} {limitunit}\n#"
            if settings["draindelaymode"] == "auto":
                comment = f"{comment}Measurement acquisition period for drain is done in AUTO mode\n#"
            else:
                comment = f"{comment}Measurement stabilization period for drain is{settings['draindelay'] / 1000} ms\n#"
            comment = f"{comment}NPLC value {settings['drainnplc'] * 1000 / smu_settings['lineFrequency']} ms (for detected line frequency {smu_settings['lineFrequency']} Hz is {settings['drainnplc']})\n#"
        else:
            comment = f"{comment}\n#\n#\n#\n#\n#"

        comment = f"{comment}\n#"
        comment = f"{comment}Comment: {settings['comment']}\n#"
        comment = f"{comment}\n#"

        comment = f"{comment}\n#\n#\n#"

        if smu_settings["sourcehighc"]:
            comment = f"{comment}Source in high capacitance mode"
        else:
            comment = f"{comment}Source not in HighC mode (normal operation)"
        if not settings["singlechannel"]:
            if smu_settings["drainhighc"]:
                comment = f"{comment}. Drain in high capacitance mode\n#"
            else:
                comment = f"{comment}. Drain not in HighC mode (normal operation)\n#"
        else:
            comment = f"{comment}\n#"

        comment = f"{comment}\n#\n#\n#\n#\n#\n#\n#\n#\n#"

        if settings["stoptimer"]:
            comment = f"{comment}Timer set for {settings['stopafter']} minutes\n#"
        else:
            comment = f"{comment}\n#"

        if settings["sourcesensemode"] == "2 wire":
            comment = f"{comment}Sourse in 2 point measurement mode\n#"
        elif settings["sourcesensemode"] == "4 wire":
            comment = f"{comment}Sourse in 4 point measurement mode\n#"
        if not (settings["singlechannel"]):
            if settings["drainsensemode"] == "2 wire":
                comment = f"{comment}Drain in 2 point measurement mode\n"
            elif settings["drainsensemode"] == "4 wire":
                comment = f"{comment}Drain in 4 point measurement mode\n"
        else:
            comment = f"{comment}\n"

        if settings["singlechannel"]:
            comment = f"{comment}stime, IS, VS"
        else:
            comment = f"{comment}stime, IS, VS, ID, VD"

        return comment

    @staticmethod
    def save_data_to_file(filepath: str, header: str, data: pd.DataFrame) -> None:
        """Save data to file with header."""
        with open(filepath, "w") as f:
            f.write(header)
            data.to_csv(f, index=False, sep="\t")


class PluginSettingsManager:
    """Manages plugin settings parsing and validation."""

    def __init__(self, ui_accessor: UIWidgetAccessor, dependency_manager: DependencyManager):
        self.ui = ui_accessor
        self.dependency_manager = dependency_manager
        self.validator = SettingsValidator()
        self.parser = SettingsParser(ui_accessor, self.validator)

    def parse_dependency_settings(self, function_dict: Dict[str, Any], settings: Dict[str, Any]) -> Tuple[int, Union[str, Dict[str, Any]]]:
        """Parse settings from dependency plugins."""
        try:
            # Get SMU settings if SMU is selected
            if "smu" in settings:
                smu_name = settings["smu"]
                if smu_name in function_dict.get("smu", {}):
                    status, smu_settings = function_dict["smu"][smu_name]["parse_settings_widget"]()
                    if status:
                        return (status, f"SMU settings error: {smu_settings}")
                    settings["smu_settings"] = smu_settings

            # Get spectrometer settings if spectrometer is selected
            if "spectrometer" in settings:
                spectro_name = settings["spectrometer"]
                if spectro_name in function_dict.get("spectrometer", {}):
                    status, spectro_settings = function_dict["spectrometer"][spectro_name]["parse_settings_widget"]()
                    if status:
                        return (status, f"Spectrometer settings error: {spectro_settings}")
                    settings["spectro_settings"] = spectro_settings

            return (0, settings)
        except Exception as e:
            return (1, f"Error parsing dependency settings: {e}")

    def parse_basic_time_settings(self) -> Dict[str, Any]:
        """Parse basic time-related settings."""
        time_widgets = {
            "step_lineEdit": "timestep",
            "stopAfterLineEdit": "stopafter",
        }
        return self.parser.parse_positive_float_settings(time_widgets)

    def parse_smu_basic_settings(self) -> Dict[str, Any]:
        """Parse basic SMU settings."""
        settings = {}

        # Combo box settings
        combo_widgets = {
            "comboBox_channel": "channel",
            "comboBox_inject": "inject",
            "comboBox_sourceSenseMode": "sourcesensemode",
        }
        settings.update(self.parser.parse_combo_settings(combo_widgets))

        # Source value settings
        source_widgets = {
            "lineEdit_sourceSetValue": "sourcesetvalue",
            "lineEdit_sourceLimit": "sourcelimit",
            "lineEdit_sourceNPLC": "sourcenplc",
        }
        settings.update(self.parser.parse_float_settings(source_widgets))

        # Checkbox settings
        checkbox_widgets = {
            "stopTimerCheckBox": "stoptimer",
        }
        settings.update(self.parser.parse_checkbox_settings(checkbox_widgets))

        return settings


class GuiStateManager:
    """Manages GUI state updates and widget visibility."""

    def __init__(self, ui_accessor: UIWidgetAccessor):
        self.ui = ui_accessor

    def update_inject_labels(self, inject_type: str, prefix: str = "source") -> None:
        """Update unit labels based on injection type."""
        if inject_type.lower() == "voltage":
            self.ui.set_text(f"label_{prefix}SetValue", "U")
            self.ui.set_text(f"label_{prefix}SetValueUnits", "V")
            self.ui.set_text(f"label_{prefix}LimitUnits", "A")
        else:
            self.ui.set_text(f"label_{prefix}SetValue", "I")
            self.ui.set_text(f"label_{prefix}SetValueUnits", "A")
            self.ui.set_text(f"label_{prefix}LimitUnits", "V")

    def update_delay_mode_widgets(self, is_auto: bool, prefix: str = "source") -> None:
        """Update delay mode widgets based on auto/manual selection."""
        enabled = not is_auto
        widgets = [f"label_{prefix}Delay", f"lineEdit_{prefix}Delay", f"label_{prefix}DelayUnits"]
        for widget_name in widgets:
            self.ui.set_enabled(widget_name, enabled)

    def update_timer_widgets(self, timer_enabled: bool) -> None:
        """Update timer-related widgets."""
        widgets = ["stopAfterLineEdit", "stopAfterlabel", "stopAfteUnitslabel"]
        for widget_name in widgets:
            self.ui.set_enabled(widget_name, timer_enabled)

    def set_running_state(self, is_running: bool, run_button: str = "runButton", stop_button: str = "stopButton", group_widgets: Optional[List[str]] = None) -> None:
        """Set the running state of the GUI."""
        self.ui.set_enabled(run_button, not is_running)
        self.ui.set_enabled(stop_button, is_running)

        if group_widgets:
            for widget_name in group_widgets:
                self.ui.set_enabled(widget_name, not is_running)


class PluginBaseTemplate:
    """Base template for plugin functionality that can be inherited or composed."""

    def __init__(self, ui_object, dependencies: Dict[str, List[str]]):
        self.ui_accessor = UIWidgetAccessor(ui_object)
        self.dependency_manager = DependencyManager(dependencies)
        self.settings_manager = PluginSettingsManager(self.ui_accessor, self.dependency_manager)
        self.gui_manager = GuiStateManager(self.ui_accessor)
        self.signal_connector = SignalConnector(self.ui_accessor)

        self.settings = {}
        self.function_dict = {}
        self.missing_functions = []

    def validate_dependencies(self, function_dict: Dict[str, Any]) -> List[str]:
        """Validate plugin dependencies."""
        self.function_dict = function_dict
        self.missing_functions = self.dependency_manager.validate_dependencies(function_dict)
        return self.missing_functions

    def get_public_methods(self, public_methods: List[str], non_public_methods: Optional[List[str]] = None) -> Dict[str, Callable]:
        """Get public methods for the plugin."""
        if non_public_methods is None:
            non_public_methods = []

        methods = {}
        for method_name in public_methods:
            if hasattr(self, method_name) and method_name not in non_public_methods:
                methods[method_name] = getattr(self, method_name)
        return methods
