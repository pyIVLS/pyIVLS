"""
Using composition instead of multiple inheritance,
mostly because this is similar to the existing implementations.
The added benefit is that classes don't need to inherit from QObject,
since that is handled by the logger that actually uses QObject functionality.
"""

from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from enum import Enum

from PyQt6.QtWidgets import QLineEdit, QCheckBox, QComboBox, QSpinBox, QDoubleSpinBox
from PyQt6.QtCore import QObject, pyqtSignal


class FileManager:
    """Handles file operations for plugins."""

    @staticmethod
    def create_file_header(settings: Dict[str, Any], smu_settings: Dict[str, Any]) -> str:
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
    def get_address() -> str:
        """Returns the address of the SMU device."""
        return "Not implemented"


class GuiMapper:
    """Enhanced GUI field mapper with dynamic type detection and bidirectional conversion."""

    def __init__(self, widget, plugin_name):
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

    def set_values(self, settings: Dict[str, Any], field_mapping: Dict[str, str], validation_rules: Dict[str, Dict[str, Any]]) -> Tuple[int, Dict[str, Any]]:
        """Set GUI widget values from settings dictionary with dynamic type detection and conversion.
        
        Args:
            settings: Settings dictionary with values to set
            field_mapping: Dict mapping setting names to widget attribute names
            validation_rules: Optional rules for converting stored values to display format
                {"setting_name": {"display_converter": lambda x: ...}}
        """
        validation_rules = validation_rules
        for setting_name, widget_name in field_mapping.items():
            try:
                widget_obj = getattr(self.widget, widget_name)
                value = settings[setting_name]
                # Apply display conversion if specified
                if setting_name in validation_rules and "display_converter" in validation_rules[setting_name]:
                    try:
                        value = validation_rules[setting_name]["display_converter"](value)
                    except Exception as e:
                        return (1, {"Error message": f"Display conversion failed for {setting_name}: {str(e)}"})

                # Dynamically set value based on widget type
                self._set_value_dynamic(widget_obj, value)

            except AttributeError:
                return (1, {"Error message": f"Widget '{widget_name}' not found for {setting_name}"})
            except Exception as e:
                return (1, {"Error message": f"Error processing {setting_name}: {str(e)}"})
        return (0, {})

    def _extract_value_dynamic(self, widget_obj) -> Any:
        """Dynamically extract value based on widget type."""
        if isinstance(widget_obj, QLineEdit):
            text = widget_obj.text().strip()
            # Try to convert to number if possible
            try:
                return float(text)
            except ValueError:
                # must be text, or a bad value. Will be validated later
                return text
        elif isinstance(widget_obj, QCheckBox):
            return widget_obj.isChecked()
        elif isinstance(widget_obj, QComboBox):
            # assuming that QCombobox is just for text.
            return widget_obj.currentText()
        elif isinstance(widget_obj, (QSpinBox, QDoubleSpinBox)):
            return float(widget_obj.value())
        else:
            # what is that widget??
            raise ValueError(f"Tried to access unsupported widget type: {type(widget_obj)}")

    def _set_value_dynamic(self, widget_obj, value: Any) -> None:
        """Dynamically set value based on widget type."""
        if isinstance(widget_obj, QLineEdit):
            widget_obj.setText(str(value))
        elif isinstance(widget_obj, QCheckBox):
            # handle various truths, since a pure conversion to bool for a string evaluates to True for any non-empty string
            widget_obj.setChecked(value in [True, "True", "true"]) 
        elif isinstance(widget_obj, QComboBox):
            widget_obj.setCurrentText(str(value))
        elif isinstance(widget_obj, QSpinBox):
            widget_obj.setValue(int(value))
        elif isinstance(widget_obj, QDoubleSpinBox):
            widget_obj.setValue(float(value))
        else:
            # what is that widget??
            raise ValueError(f"Unsupported widget type called for guimapper: {value}: {type(widget_obj)}")
    
    def _validate_value_dynamic(self, setting_name: str, value: Any, validation_config: Dict[str, Any]) -> Tuple[int, Any]:
        """Validate a value using dynamic validation rules."""

        # Apply conversion function if specified
        if "converter" in validation_config:
            try:
                value = validation_config["converter"](value)
            except Exception as e:
                return (1, {"Error message": f"Value error in {self.plugin_name}: conversion failed for {setting_name}: {str(e)}"})


        # Apply custom validator function
        if "validator" in validation_config:
            validator_func = validation_config["validator"]
            try:
                if not validator_func(value):
                    error_msg = validation_config.get("error_message", f"{setting_name} failed validation")
                    return (1, {"Error message": f"Value error in {self.plugin_name}: {error_msg}"})
            except Exception as e:
                return (1, {"Error message": f"Value error in {self.plugin_name}: validation failed for {setting_name}: {str(e)}"})


        return (0, value)


class DataOrder(Enum):
    """Enum for data ordering."""

    VOLTAGE = 1
    CURRENT = 0


class PluginException(Exception):
    """Base exception for plugin errors."""

    pass


class DependencyManager:
    """Enhanced dependency manager that handles multiple dependency types and validation."""

    def __init__(self, plugin_name: str, dependencies: Dict[str, list], widget, mapping: Dict[str, str]):
        """
        Initialize dependency manager.
        
        Args:
            plugin_name: Name of the plugin using this manager
            dependencies: Dict mapping dependency types to required function lists
                         e.g., {"smu": ["connect", "init"], "spectro": ["measure"]}
            widget: Optional widget containing comboboxes for dependency selection
            mapping: Dict mapping dependency type to combobox widget name
        """
        self.plugin_name = plugin_name
        self.dependencies = dependencies
        self.widget = widget
        self._function_dict = {}
        self.missing_functions = []
        self.dependency_settings = {}
        self.combobox_mapping = mapping
        # connect 
        
    @property
    def function_dict(self) -> Dict[str, Any]:
        """Get the current function dictionary."""
        return self._function_dict
        
    @function_dict.setter
    def function_dict(self, value: Dict[str, Any]) -> None:
        """Set the function dictionary and automatically update GUI comboboxes."""
        self._function_dict = value
        # Automatically update comboboxes when function dict is set
        self.update_comboboxes()
        
    def set_function_dict(self, function_dict: Dict[str, Any]) -> None:
        """Set the available function dictionary from plugin system."""
        self.function_dict = function_dict
        
        
    def validate_dependencies(self) -> Tuple[bool, list]:
        """
        Validate that all required dependencies are available.
        
        Returns:
            Tuple[bool, list]: (is_valid, missing_functions_list)
        """
        self.missing_functions = []
        
        for dependency_type, required_functions in self.dependencies.items():
            if dependency_type not in self._function_dict:
                self.missing_functions.extend([f"{dependency_type}.{func}" for func in required_functions])
                continue
                
            available_plugins = self._function_dict[dependency_type]
            
            # Check if any plugin provides all required functions
            has_valid_plugin = False
            for plugin_name, plugin_functions in available_plugins.items():
                if all(func in plugin_functions for func in required_functions):
                    has_valid_plugin = True
                    break
                    
            if not has_valid_plugin:
                missing_for_type = []
                for func in required_functions:
                    if not any(func in plugin_funcs for plugin_funcs in available_plugins.values()):
                        missing_for_type.append(f"{dependency_type}.{func}")
                self.missing_functions.extend(missing_for_type)
        
        return len(self.missing_functions) == 0, self.missing_functions
        
    def update_comboboxes(self) -> None:
        """Update all dependency comboboxes with available plugins."""
        if not self.widget:
            return
            
        for dependency_type, combobox_name in self.combobox_mapping.items():
            if dependency_type in self._function_dict:
                try:
                    combobox = getattr(self.widget, combobox_name)
                    # Store current selection to restore if possible
                    current_selection = combobox.currentText()
                    
                    combobox.clear()
                    available_plugins = list(self._function_dict[dependency_type].keys())
                    combobox.addItems(available_plugins)
                    
                    # Try to restore previous selection if it's still available
                    if current_selection in available_plugins:
                        combobox.setCurrentText(current_selection)
                except AttributeError:
                    # Combobox not found, skip silently
                    continue
                # add custom implementations here 
    

    def get_selected_dependencies(self) -> Dict[str, str]:
        """
        Get currently selected dependencies from comboboxes.
        
        Returns:
            Dict mapping dependency type to selected plugin name
        """
        selected = {}
        if not self.widget:
            return selected
            
        for dependency_type, combobox_name in self.combobox_mapping.items():
            try:
                combobox = getattr(self.widget, combobox_name)
                selected[dependency_type] = combobox.currentText()
            except AttributeError:
                continue
                
        return selected
                          
    def validate_selection(self, dependency_type: str, plugin_name: str) -> Tuple[bool, str]:
        """
        Validate that a selected plugin provides all required functions.
        
        Args:
            dependency_type: Type of dependency (e.g., "smu")
            plugin_name: Name of selected plugin
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if dependency_type not in self.dependencies:
            return False, f"Unknown dependency type: {dependency_type}"
            
        if dependency_type not in self._function_dict:
            return False, f"No {dependency_type} plugins available"
            
        if plugin_name not in self._function_dict[dependency_type]:
            return False, f"{dependency_type} plugin '{plugin_name}' not found"
            
        plugin_functions = self._function_dict[dependency_type][plugin_name]
        required_functions = self.dependencies[dependency_type]
        
        missing_functions = [func for func in required_functions if func not in plugin_functions]
        
        if missing_functions:
            return False, f"{dependency_type} plugin '{plugin_name}' missing functions: {', '.join(missing_functions)}"
            
        return True, ""
        
    def get_function_dict_for_dependencies(self) -> Dict[str, Any]:
        """
        Get a filtered function dictionary containing only the dependencies needed by this plugin.
        
        Returns:
            Dict containing only the dependency types this plugin needs
        """
        filtered_dict = {}
        for dependency_type in self.dependencies.keys():
            if dependency_type in self._function_dict:
                filtered_dict[dependency_type] = self._function_dict[dependency_type]
        return filtered_dict


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
        message = f"{self.plugin_name}: {message}"
        self.info_popup_signal.emit(message)


class smuHelper