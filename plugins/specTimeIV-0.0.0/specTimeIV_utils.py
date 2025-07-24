"""
Using composition instead of multiple inheritance,
mostly because this is similar to the existing implementations.
"""

from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from enum import Enum

from PyQt6.QtWidgets import QLineEdit, QCheckBox, QComboBox, QSpinBox, QDoubleSpinBox
from PyQt6.QtCore import QObject, pyqtSignal


class FileManager:
    """Handles file operations for plugins."""

    def __init__(self):
        pass

    def create_file_header(self, settings: Dict[str, Any], smu_settings: Dict[str, Any]) -> str:
        """Create a standardized file header for data files."""
        header_lines = []
        header_lines.append("# Time IV measurement data")
        header_lines.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        header_lines.append(f"# Sample: {settings.get('samplename', 'Unknown')}")
        header_lines.append(f"# Comment: {settings.get('comment', '')}")
        header_lines.append("#")
        header_lines.append("# Measurement settings:")
        header_lines.append(f"# - Time step: {settings.get('timestep', 0)} s")
        header_lines.append(f"# - Stop after: {settings.get('stopafter', 0)} s")
        header_lines.append(f"# - Auto save interval: {settings.get('autosaveinterval', 0)} s")
        header_lines.append("#")
        header_lines.append("# SMU settings:")
        if smu_settings:
            for key, value in smu_settings.items():
                header_lines.append(f"# - {key}: {value}")
        header_lines.append("#")
        header_lines.append("# Source settings:")
        header_lines.append(f"# - Value: {settings.get('sourcevalue', 0)}")
        header_lines.append(f"# - Limit: {settings.get('sourcelimit', 0)}")
        header_lines.append(f"# - NPLC: {settings.get('sourcenplc', 0)}")
        header_lines.append(f"# - Delay: {settings.get('sourcedelay', 0)} s")
        header_lines.append("#")
        if not settings.get("singlechannel", False):
            header_lines.append("# Drain settings:")
            header_lines.append(f"# - Value: {settings.get('drainvalue', 0)}")
            header_lines.append(f"# - Limit: {settings.get('drainlimit', 0)}")
            header_lines.append(f"# - NPLC: {settings.get('drainnplc', 0)}")
            header_lines.append(f"# - Delay: {settings.get('draindelay', 0)} s")
            header_lines.append("#")

        # Data column headers
        if settings.get("singlechannel", False):
            header_lines.append("# Time(s)\tSource_I(A)\tSource_V(V)")
        else:
            header_lines.append("# Time(s)\tSource_I(A)\tSource_V(V)\tDrain_I(A)\tDrain_V(V)")

        return "\n".join(header_lines) + "\n"


class DynamicGuiFieldMapper:
    """Enhanced GUI field mapper with dynamic type detection and simplified configuration."""

    def __init__(self, widget, plugin_name: str = "plugin"):
        self.widget = widget
        self.plugin_name = plugin_name

    def get_values(self, field_mapping: Dict[str, str], validation_rules: Optional[Dict[str, Dict[str, Any]]] = None) -> Tuple[int, Dict[str, Any]]:
        """Extract values from GUI widgets with dynamic type detection.

        Args:
            field_mapping: Dict mapping setting names to widget attribute names
                          {"setting_name": "widget_attribute_name"}
            validation_rules: Optional validation rules for each setting
                            {"setting_name": {"required": True, "validator": lambda x: x > 0}}

        Returns:
            Tuple[int, Dict]: (status, result_dict_or_error_message)
        """
        result = {}
        validation_rules = validation_rules or {}

        for setting_name, widget_name in field_mapping.items():
            try:
                # Get the widget
                widget_obj = getattr(self.widget, widget_name)

                # Dynamically determine type and extract value
                value = self._extract_value_dynamic(widget_obj)

                # Apply validation if specified
                if setting_name in validation_rules:
                    status, validated_value = self._validate_value_dynamic(setting_name, value, validation_rules[setting_name])
                    if status:
                        return (status, validated_value)
                    value = validated_value

                result[setting_name] = value

            except AttributeError:
                return (1, {"Error message": f"Widget '{widget_name}' not found for {setting_name}"})
            except Exception as e:
                return (1, {"Error message": f"Error processing {setting_name}: {str(e)}"})

        return (0, result)

    def set_values(self, settings: Dict[str, Any], field_mapping: Dict[str, str]) -> None:
        """Set GUI widget values from settings dictionary with dynamic type detection."""
        for setting_name, widget_name in field_mapping.items():
            if setting_name not in settings:
                continue

            try:
                widget_obj = getattr(self.widget, widget_name)
                value = settings[setting_name]

                # Dynamically set value based on widget type
                self._set_value_dynamic(widget_obj, value)

            except AttributeError:
                # Widget not found, skip silently
                pass
            except Exception:
                # Other errors, skip silently for robustness
                pass

    def _extract_value_dynamic(self, widget_obj) -> Any:
        """Dynamically extract value based on widget type."""
        if isinstance(widget_obj, QLineEdit):
            text = widget_obj.text().strip()
            # Try to convert to number if possible
            try:
                if "." in text:
                    return float(text)
                else:
                    return int(text)
            except ValueError:
                return text
        elif isinstance(widget_obj, QCheckBox):
            return widget_obj.isChecked()
        elif isinstance(widget_obj, QComboBox):
            return widget_obj.currentText()
        elif isinstance(widget_obj, (QSpinBox, QDoubleSpinBox)):
            return widget_obj.value()
        else:
            # Fallback: try common methods
            if hasattr(widget_obj, "text"):
                return widget_obj.text()
            elif hasattr(widget_obj, "isChecked"):
                return widget_obj.isChecked()
            elif hasattr(widget_obj, "currentText"):
                return widget_obj.currentText()
            elif hasattr(widget_obj, "value"):
                return widget_obj.value()
            else:
                raise ValueError(f"Unsupported widget type: {type(widget_obj)}")

    def _set_value_dynamic(self, widget_obj, value: Any) -> None:
        """Dynamically set value based on widget type."""
        if isinstance(widget_obj, QLineEdit):
            widget_obj.setText(str(value))
        elif isinstance(widget_obj, QCheckBox):
            widget_obj.setChecked(bool(value))
        elif isinstance(widget_obj, QComboBox):
            widget_obj.setCurrentText(str(value))
        elif isinstance(widget_obj, QSpinBox):
            widget_obj.setValue(int(value))
        elif isinstance(widget_obj, QDoubleSpinBox):
            widget_obj.setValue(float(value))
        else:
            # Fallback: try common methods
            if hasattr(widget_obj, "setText"):
                widget_obj.setText(str(value))
            elif hasattr(widget_obj, "setChecked"):
                widget_obj.setChecked(bool(value))
            elif hasattr(widget_obj, "setCurrentText"):
                widget_obj.setCurrentText(str(value))
            elif hasattr(widget_obj, "setValue"):
                widget_obj.setValue(value)

    def _validate_value_dynamic(self, setting_name: str, value: Any, validation_config: Dict[str, Any]) -> Tuple[int, Any]:
        """Validate a value using dynamic validation rules."""

        # Check if required
        if validation_config.get("required", False):
            if value is None or (isinstance(value, str) and value.strip() == ""):
                return (1, {"Error message": f"Value error in {self.plugin_name}: {setting_name} is required"})

        # Apply custom validator function
        if "validator" in validation_config:
            validator_func = validation_config["validator"]
            try:
                if not validator_func(value):
                    error_msg = validation_config.get("error_message", f"{setting_name} failed validation")
                    return (1, {"Error message": f"Value error in {self.plugin_name}: {error_msg}"})
            except Exception as e:
                return (1, {"Error message": f"Value error in {self.plugin_name}: validation failed for {setting_name}: {str(e)}"})

        # Apply conversion function if specified
        if "converter" in validation_config:
            try:
                value = validation_config["converter"](value)
            except Exception as e:
                return (1, {"Error message": f"Value error in {self.plugin_name}: conversion failed for {setting_name}: {str(e)}"})

        return (0, value)


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
