"""
Comprehensive tests for plugin_components.py

This module tests the following classes:
- FileManager: File header creation functionality
- GuiMapper: Dynamic GUI field mapping with bidirectional conversion
- DependencyManager: Plugin dependency management and validation
- LoggingHelper: Logging functionality with Qt signals
- SMUHelper: SMU initialization helper
- DataOrder: Enum for data ordering
- PluginException: Custom exception class
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch

# Add the plugins directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "plugins"))

try:
    from plugin_components import (
        FileManager,
        GuiMapper,
        DependencyManager,
        LoggingHelper,
        PluginException,
    )
    from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QCheckBox, QComboBox, QSpinBox, QDoubleSpinBox
    from PyQt6.QtCore import QObject
    import sys

    # Create QApplication if it doesn't exist (needed for Qt widgets)
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

except ImportError as e:
    pytest.skip(f"Cannot import required modules: {e}", allow_module_level=True)


class TestFileManager:
    """Test the FileManager class for file header creation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.file_manager = FileManager()

    def test_create_file_header_voltage_single_channel(self):
        """Test file header creation for voltage mode, single channel."""
        settings = {
            "samplename": "TestSample",
            "channel": "smua",
            "inject": "voltage",
            "sourcevalue": 1.0,
            "sourcelimit": 0.1,
            "sourcedelaymode": "auto",
            "sourcenplc": 0.01,
            "timestep": 0.1,
            "singlechannel": True,
            "sourcesensemode": "2 wire",
            "stoptimer": True,
            "stopafter": 10,
            "comment": "Test measurement",
        }

        smu_settings = {"lineFrequency": 50, "sourcehighc": False}

        header = self.file_manager.create_file_header(settings, smu_settings)

        # Check that header contains expected elements
        assert "TestSample" in header
        assert "smua" in header
        assert "voltage injection mode" in header
        assert "Test measurement" in header
        assert "1.0 V" in header  # Source value with voltage unit
        assert "0.1 A" in header  # Limit with current unit
        assert "AUTO mode" in header
        assert "stime, IS, VS" in header  # Single channel output format
        assert "2 point measurement mode" in header
        assert "Timer set for 10 minutes" in header

    def test_create_file_header_current_dual_channel(self):
        """Test file header creation for current mode, dual channel."""
        settings = {
            "samplename": "DualChannelTest",
            "channel": "smub",
            "inject": "current",
            "sourcevalue": 0.001,
            "sourcelimit": 10.0,
            "sourcedelaymode": "manual",
            "sourcedelay": 500,
            "sourcenplc": 0.02,
            "timestep": 0.5,
            "singlechannel": False,
            "draininject": "voltage",
            "drainvalue": 5.0,
            "drainlimit": 0.05,
            "draindelaymode": "auto",
            "drainnplc": 0.015,
            "sourcesensemode": "4 wire",
            "drainsensemode": "2 wire",
            "stoptimer": False,
            "comment": "Dual channel test",
        }

        smu_settings = {"lineFrequency": 60, "sourcehighc": True, "drainhighc": False}

        header = self.file_manager.create_file_header(settings, smu_settings)

        # Check dual channel specific elements
        assert "DualChannelTest" in header
        assert "current injection mode" in header
        assert "voltage injection mode" in header  # Drain mode
        assert "0.001 A" in header  # Source value with current unit
        assert "10.0 V" in header  # Source limit with voltage unit
        assert "5.0 V" in header  # Drain value with voltage unit
        assert "0.05 A" in header  # Drain limit with current unit
        assert "stime, IS, VS, ID, VD" in header  # Dual channel output format
        assert "4 point measurement mode" in header
        assert "2 point measurement mode" in header  # Drain sense mode
        assert "high capacitance mode" in header
        assert "0.5 ms" in header  # Manual delay (500ms converted to 0.5s)

    def test_create_file_header_empty_sample_name(self):
        """Test file header creation with empty sample name."""
        settings = {
            "samplename": "",
            "channel": "smua",
            "inject": "voltage",
            "sourcevalue": 2.5,
            "sourcelimit": 0.2,
            "sourcedelaymode": "auto",
            "sourcenplc": 0.01,
            "timestep": 0.1,
            "singlechannel": True,
            "sourcesensemode": "2 wire",
            "stoptimer": False,
            "comment": "No sample name test",
        }

        smu_settings = {"lineFrequency": 50, "sourcehighc": False}

        header = self.file_manager.create_file_header(settings, smu_settings)

        # Check that empty sample name is handled correctly
        assert "{noname}" in header
        assert "No sample name test" in header


class TestGuiMapper:
    """Test the GuiMapper class for dynamic GUI field mapping."""

    def setup_method(self):
        """Set up test fixtures with real Qt widgets."""
        # Create a real QWidget container
        self.widget = QWidget()
        self.plugin_name = "TestPlugin"
        self.gui_mapper = GuiMapper(self.widget, self.plugin_name)

        # Create real PyQt6 widgets
        self.line_edit = QLineEdit()
        self.checkbox = QCheckBox()
        self.combobox = QComboBox()
        self.spinbox = QSpinBox()
        self.double_spinbox = QDoubleSpinBox()

        # Add some options to combobox for testing
        self.combobox.addItems(["Option1", "Option2", "Option3"])

        # Set reasonable ranges for spinboxes
        self.spinbox.setRange(-1000, 1000)
        self.double_spinbox.setRange(-1000.0, 1000.0)
        self.double_spinbox.setDecimals(5)

    def teardown_method(self):
        """Clean up Qt widgets."""
        self.widget.deleteLater()
        # Process Qt events to ensure cleanup
        if QApplication.instance():
            QApplication.processEvents()

    def test_extract_value_dynamic_line_edit_float(self):
        """Test value extraction from QLineEdit with float conversion."""
        self.line_edit.setText("3.14")

        result = self.gui_mapper._extract_value_dynamic(self.line_edit)

        assert result == 3.14
        assert isinstance(result, float)

    def test_extract_value_dynamic_line_edit_integer(self):
        """Test value extraction from QLineEdit with integer value."""
        self.line_edit.setText("42")

        result = self.gui_mapper._extract_value_dynamic(self.line_edit)

        assert result == 42.0
        assert isinstance(result, float)

    def test_extract_value_dynamic_line_edit_string(self):
        """Test value extraction from QLineEdit with string fallback."""
        self.line_edit.setText("test_string")

        result = self.gui_mapper._extract_value_dynamic(self.line_edit)

        assert result == "test_string"
        assert isinstance(result, str)

    def test_extract_value_dynamic_line_edit_empty(self):
        """Test value extraction from QLineEdit with empty string."""
        self.line_edit.setText("  ")  # Whitespace only

        result = self.gui_mapper._extract_value_dynamic(self.line_edit)

        assert result == ""  # Should be stripped to empty

    def test_extract_value_dynamic_checkbox_true(self):
        """Test value extraction from QCheckBox when checked."""
        self.checkbox.setChecked(True)

        result = self.gui_mapper._extract_value_dynamic(self.checkbox)

        assert result is True

    def test_extract_value_dynamic_checkbox_false(self):
        """Test value extraction from QCheckBox when unchecked."""
        self.checkbox.setChecked(False)

        result = self.gui_mapper._extract_value_dynamic(self.checkbox)

        assert result is False

    def test_extract_value_dynamic_combobox(self):
        """Test value extraction from QComboBox."""
        self.combobox.setCurrentText("Option1")

        result = self.gui_mapper._extract_value_dynamic(self.combobox)

        assert result == "Option1"

    def test_extract_value_dynamic_spinbox(self):
        """Test value extraction from QSpinBox."""
        self.spinbox.setValue(42)

        result = self.gui_mapper._extract_value_dynamic(self.spinbox)

        assert result == 42
        assert isinstance(result, int)

    def test_extract_value_dynamic_double_spinbox(self):
        """Test value extraction from QDoubleSpinBox."""
        self.double_spinbox.setValue(3.14159)

        result = self.gui_mapper._extract_value_dynamic(self.double_spinbox)

        assert result == 3.14159

    def test_extract_value_dynamic_unsupported_widget(self):
        """Test that unsupported widget types raise ValueError."""
        unsupported_widget = QWidget()  # Use a real widget that's not supported

        with pytest.raises(ValueError, match=f"Unsupported widget type: {type(unsupported_widget)}"):
            self.gui_mapper._extract_value_dynamic(unsupported_widget)

    def test_set_value_dynamic_line_edit(self):
        """Test setting value to QLineEdit."""
        self.gui_mapper._set_value_dynamic(self.line_edit, 42.5)

        assert self.line_edit.text() == "42.5"

    def test_set_value_dynamic_checkbox_true(self):
        """Test setting True value to QCheckBox."""
        self.gui_mapper._set_value_dynamic(self.checkbox, True)

        assert self.checkbox.isChecked() is True

    def test_set_value_dynamic_checkbox_string_true(self):
        """Test setting string 'True' value to QCheckBox."""
        self.gui_mapper._set_value_dynamic(self.checkbox, "True")

        assert self.checkbox.isChecked() is True

    def test_set_value_dynamic_checkbox_false(self):
        """Test setting False value to QCheckBox."""
        self.gui_mapper._set_value_dynamic(self.checkbox, False)

        assert self.checkbox.isChecked() is False

    def test_set_value_dynamic_checkbox_string_false(self):
        """Test setting non-True string to QCheckBox."""
        self.gui_mapper._set_value_dynamic(self.checkbox, "False")

        assert self.checkbox.isChecked() is False

    def test_set_value_dynamic_combobox(self):
        """Test setting value to QComboBox."""
        self.gui_mapper._set_value_dynamic(self.combobox, "Option2")

        assert self.combobox.currentText() == "Option2"

    def test_set_value_dynamic_spinbox(self):
        """Test setting value to QSpinBox."""
        self.gui_mapper._set_value_dynamic(self.spinbox, 42.7)

        assert self.spinbox.value() == 42  # Should convert to int

    def test_set_value_dynamic_double_spinbox(self):
        """Test setting value to QDoubleSpinBox."""
        self.gui_mapper._set_value_dynamic(self.double_spinbox, 3.14159)

        assert self.double_spinbox.value() == 3.14159

    def test_set_value_dynamic_unsupported_widget(self):
        """Test that unsupported widget types raise ValueError."""
        unsupported_widget = QWidget()  # Use a real widget that's not supported

        with pytest.raises(ValueError, match=f"Unsupported widget type for setting value: {type(unsupported_widget)}"):
            self.gui_mapper._set_value_dynamic(unsupported_widget, "value")

    def test_validate_value_dynamic_with_converter(self):
        """Test value validation with converter function."""
        validation_config = {
            "converter": lambda x: x * 2,
            "validator": lambda x: x > 0,
            "error_message": "Value must be positive",
        }

        result = self.gui_mapper._validate_value_dynamic("test_field", 5, validation_config)

        assert result.is_success
        assert result.get_data_value("validated_value") == 10  # 5 * 2

    def test_validate_value_dynamic_converter_failure(self):
        """Test validation when converter function fails."""
        validation_config = {
            "converter": lambda x: x / 0,  # Division by zero
            "validator": lambda x: True,
        }

        result = self.gui_mapper._validate_value_dynamic("test_field", 5, validation_config)

        assert result.is_error
        assert "conversion failed" in result.error_message

    def test_validate_value_dynamic_validator_success(self):
        """Test validation when validator passes."""
        validation_config = {"validator": lambda x: x > 0, "error_message": "Value must be positive"}

        result = self.gui_mapper._validate_value_dynamic("test_field", 5, validation_config)

        assert result.is_success
        assert result.get_data_value("validated_value") == 5

    def test_validate_value_dynamic_validator_failure(self):
        """Test validation when validator function fails."""
        validation_config = {"validator": lambda x: x > 10, "error_message": "Value must be greater than 10"}

        result = self.gui_mapper._validate_value_dynamic("test_field", 5, validation_config)

        assert result.is_error
        assert "Value must be greater than 10" in result.error_message

    def test_validate_value_dynamic_validator_exception(self):
        """Test validation when validator function raises exception."""
        validation_config = {
            "validator": lambda x: x.non_existent_method(),  # This will raise AttributeError
        }

        result = self.gui_mapper._validate_value_dynamic("test_field", 5, validation_config)

        assert result.is_error
        assert "validation failed" in result.error_message

    def test_get_values_success(self):
        """Test successful value extraction from multiple widgets."""
        # Set up real widgets
        setattr(self.widget, "lineEdit1", self.line_edit)
        setattr(self.widget, "checkBox1", self.checkbox)

        self.line_edit.setText("42.5")
        self.checkbox.setChecked(True)

        field_mapping = {"value1": "lineEdit1", "value2": "checkBox1"}

        validation_rules = {"value1": {"validator": lambda x: x > 0, "error_message": "Must be positive"}}

        result = self.gui_mapper.get_values(field_mapping, validation_rules)

        assert result.is_success
        data = result.data
        assert data["value1"] == 42.5
        assert data["value2"] is True

    def test_get_values_widget_not_found(self):
        """Test error handling when widget extraction fails."""
        field_mapping = {"value1": "nonexistent_widget"}

        result = self.gui_mapper.get_values(field_mapping)

        assert result.is_error
        assert "Widget 'nonexistent_widget' not found" in result.error_message

    def test_get_values_validation_failure(self):
        """Test error handling when validation fails."""
        setattr(self.widget, "lineEdit1", self.line_edit)
        self.line_edit.setText("-5")

        field_mapping = {"value1": "lineEdit1"}
        validation_rules = {"value1": {"validator": lambda x: x > 0, "error_message": "Must be positive"}}

        result = self.gui_mapper.get_values(field_mapping, validation_rules)

        assert result.is_error
        assert "Must be positive" in result.error_message

    def test_set_values_success(self):
        """Test successful value setting to multiple widgets."""
        # Set up real widgets
        setattr(self.widget, "lineEdit1", self.line_edit)
        setattr(self.widget, "checkBox1", self.checkbox)

        settings = {"value1": 42.5, "value2": True}

        field_mapping = {"value1": "lineEdit1", "value2": "checkBox1"}

        validation_rules = {}

        result = self.gui_mapper.set_values(settings, field_mapping, validation_rules)

        assert result.is_success
        assert self.line_edit.text() == "42.5"
        assert self.checkbox.isChecked() is True

    def test_set_values_with_display_converter(self):
        """Test value setting with display converter."""
        setattr(self.widget, "lineEdit1", self.line_edit)

        settings = {"value1": 1000}  # Stored in milliseconds
        field_mapping = {"value1": "lineEdit1"}
        validation_rules = {
            "value1": {
                "display_converter": lambda x: x / 1000  # Convert to seconds for display
            }
        }

        result = self.gui_mapper.set_values(settings, field_mapping, validation_rules)

        assert result.is_success
        assert self.line_edit.text() == "1.0"

    def test_set_values_display_converter_failure(self):
        """Test error handling when display converter fails."""
        setattr(self.widget, "lineEdit1", self.line_edit)

        settings = {"value1": "not_a_number"}
        field_mapping = {"value1": "lineEdit1"}
        validation_rules = {
            "value1": {
                "display_converter": lambda x: x / 1000  # Will fail with string
            }
        }

        result = self.gui_mapper.set_values(settings, field_mapping, validation_rules)

        assert result.is_error
        assert "Display conversion failed" in result.error_message

    def test_set_values_widget_not_found(self):
        """Test error handling when widget setting fails."""
        settings = {"value1": 42}
        field_mapping = {"value1": "nonexistent_widget"}
        validation_rules = {}

        result = self.gui_mapper.set_values(settings, field_mapping, validation_rules)

        assert result.is_error
        assert "Widget 'nonexistent_widget' not found" in result.error_message


class TestDependencyManager:
    """Test the DependencyManager class for plugin dependency management."""

    def setup_method(self):
        """Set up test fixtures."""
        self.plugin_name = "TestPlugin"
        self.dependencies = {"smu": ["connect", "init", "measure"], "spectro": ["scan", "get_spectrum"]}
        self.mock_widget = Mock()
        self.mapping = {"smu": "smuComboBox", "spectro": "spectroComboBox"}

        # Set up mock comboboxes
        self.mock_smu_combo = Mock()
        self.mock_spectro_combo = Mock()
        self.mock_widget.smuComboBox = self.mock_smu_combo
        self.mock_widget.spectroComboBox = self.mock_spectro_combo

        self.dependency_manager = DependencyManager(self.plugin_name, self.dependencies, self.mock_widget, self.mapping)

    def test_init(self):
        """Test DependencyManager initialization."""
        assert self.dependency_manager.plugin_name == "TestPlugin"
        assert self.dependency_manager.dependencies == self.dependencies
        assert self.dependency_manager.widget == self.mock_widget
        assert self.dependency_manager.combobox_mapping == self.mapping
        assert self.dependency_manager.function_dict == {}

    def test_function_dict_property_setter(self):
        """Test that setting function_dict property triggers update_comboboxes."""
        with patch.object(self.dependency_manager, "update_comboboxes") as mock_update:
            test_dict = {"smu": {"plugin1": ["connect", "init"]}}
            self.dependency_manager.function_dict = test_dict

            assert self.dependency_manager._function_dict == test_dict
            mock_update.assert_called_once()

    def test_set_function_dict(self):
        """Test set_function_dict method."""
        with patch.object(self.dependency_manager, "update_comboboxes") as mock_update:
            test_dict = {"smu": {"plugin1": ["connect", "init"]}}
            self.dependency_manager.set_function_dict(test_dict)

            assert self.dependency_manager.function_dict == test_dict
            mock_update.assert_called_once()

    def test_validate_dependencies_success(self):
        """Test successful dependency validation."""
        function_dict = {
            "smu": {"plugin1": ["connect", "init", "measure", "extra_function"]},
            "spectro": {"plugin2": ["scan", "get_spectrum", "calibrate"]},
        }
        self.dependency_manager.set_function_dict(function_dict)

        is_valid, missing = self.dependency_manager.validate_dependencies()

        assert is_valid is True
        assert missing == []

    def test_validate_dependencies_missing_plugin_type(self):
        """Test dependency validation when plugin type is missing."""
        function_dict = {
            "smu": {"plugin1": ["connect", "init", "measure"]}
            # Missing "spectro" plugin type
        }
        self.dependency_manager.set_function_dict(function_dict)

        is_valid, missing = self.dependency_manager.validate_dependencies()

        assert is_valid is False
        assert "spectro.scan" in missing
        assert "spectro.get_spectrum" in missing

    def test_validate_dependencies_missing_functions(self):
        """Test dependency validation when required functions are missing."""
        function_dict = {
            "smu": {
                "plugin1": ["connect", "init"]  # Missing "measure"
            },
            "spectro": {
                "plugin2": ["scan"]  # Missing "get_spectrum"
            },
        }
        self.dependency_manager.set_function_dict(function_dict)

        is_valid, missing = self.dependency_manager.validate_dependencies()

        assert is_valid is False
        assert "smu.measure" in missing
        assert "spectro.get_spectrum" in missing

    def test_update_comboboxes(self):
        """Test combobox updating with available plugins."""
        function_dict = {
            "smu": {"smu_plugin1": ["connect", "init"], "smu_plugin2": ["connect", "init", "measure"]},
            "spectro": {"spectro_plugin1": ["scan", "get_spectrum"]},
        }

        self.dependency_manager.set_function_dict(function_dict)

        # Verify SMU combobox was updated
        self.mock_smu_combo.clear.assert_called()
        self.mock_smu_combo.addItems.assert_called_with(["smu_plugin1", "smu_plugin2"])

        # Verify Spectro combobox was updated
        self.mock_spectro_combo.clear.assert_called()
        self.mock_spectro_combo.addItems.assert_called_with(["spectro_plugin1"])

    def test_update_comboboxes_no_widget(self):
        """Test update_comboboxes when widget is None."""
        dependency_manager = DependencyManager("TestPlugin", self.dependencies, None, self.mapping)

        # Should not raise an exception
        dependency_manager.update_comboboxes()

    def test_get_selected_dependencies(self):
        """Test getting selected dependencies from comboboxes."""
        self.mock_smu_combo.currentText.return_value = "selected_smu_plugin"
        self.mock_spectro_combo.currentText.return_value = "selected_spectro_plugin"

        selected = self.dependency_manager.get_selected_dependencies()

        expected = {"smu": "selected_smu_plugin", "spectro": "selected_spectro_plugin"}
        assert selected == expected

    def test_get_selected_dependencies_no_widget(self):
        """Test get_selected_dependencies when widget is None."""
        dependency_manager = DependencyManager("TestPlugin", self.dependencies, None, self.mapping)

        selected = dependency_manager.get_selected_dependencies()

        assert selected == {}

    def test_validate_selection_success(self):
        """Test successful selection validation."""
        function_dict = {"smu": {"plugin1": ["connect", "init", "measure", "extra"]}}
        self.dependency_manager.set_function_dict(function_dict)

        is_valid, error = self.dependency_manager.validate_selection("smu", "plugin1")

        assert is_valid is True
        assert error == ""

    def test_validate_selection_unknown_dependency_type(self):
        """Test validation with unknown dependency type."""
        function_dict = {"smu": {"plugin1": ["connect", "init"]}}
        self.dependency_manager.set_function_dict(function_dict)

        is_valid, error = self.dependency_manager.validate_selection("unknown_type", "plugin1")

        assert is_valid is False
        assert "Unknown dependency type" in error

    def test_validate_selection_plugin_not_found(self):
        """Test validation when plugin is not found."""
        function_dict = {"smu": {"plugin1": ["connect", "init", "measure"]}}
        self.dependency_manager.set_function_dict(function_dict)

        is_valid, error = self.dependency_manager.validate_selection("smu", "nonexistent_plugin")

        assert is_valid is False
        assert "not found" in error

    def test_validate_selection_missing_functions(self):
        """Test validation when plugin is missing required functions."""
        function_dict = {
            "smu": {
                "plugin1": ["connect", "init"]  # Missing "measure"
            }
        }
        self.dependency_manager.set_function_dict(function_dict)

        is_valid, error = self.dependency_manager.validate_selection("smu", "plugin1")

        assert is_valid is False
        assert "missing functions" in error

    def test_get_function_dict_for_dependencies(self):
        """Test getting filtered function dictionary."""
        function_dict = {
            "smu": {"plugin1": ["connect", "init"]},
            "spectro": {"plugin2": ["scan"]},
            "other": {"plugin3": ["other_func"]},  # Not in dependencies
        }
        self.dependency_manager.set_function_dict(function_dict)

        filtered = self.dependency_manager.get_function_dict_for_dependencies()

        expected = {"smu": {"plugin1": ["connect", "init"]}, "spectro": {"plugin2": ["scan"]}}
        assert filtered == expected

    def test_validate_and_extract_dependency_settings_success(self):
        """Test successful dependency settings extraction."""
        # Mock dependencies and comboboxes
        mock_smu_combo = Mock()
        mock_smu_combo.currentText.return_value = "smu_plugin"
        mock_spec_combo = Mock()
        mock_spec_combo.currentText.return_value = "spec_plugin"

        # Set up dependency manager with both dependencies (list of required functions)
        dependencies = {"smu": ["parse_settings_widget"], "spectrometer": ["parse_settings_widget"]}
        mapping = {"smu": "smu_combo", "spectrometer": "spec_combo"}
        mock_widget = Mock()
        mock_widget.smu_combo = mock_smu_combo
        mock_widget.spec_combo = mock_spec_combo
        dep_manager = DependencyManager("test_plugin", dependencies, mock_widget, mapping)

        # Mock function dict with parse_settings_widget functions
        mock_function_dict = {
            "smu": {"smu_plugin": {"parse_settings_widget": Mock(return_value=(0, {"param1": "value1"}))}},
            "spectrometer": {"spec_plugin": {"parse_settings_widget": Mock(return_value=(0, {"param2": "value2"}))}},
        }
        dep_manager.set_function_dict(mock_function_dict)

        # Test the method
        target_settings = {}
        status, result = dep_manager.validate_and_extract_dependency_settings(target_settings)

        assert status == 0
        assert "smu_settings" in result
        assert "spectrometer_settings" in result
        assert result["smu_settings"] == {"param1": "value1"}
        assert result["spectrometer_settings"] == {"param2": "value2"}
        assert target_settings["smu"] == "smu_plugin"
        assert target_settings["spectrometer"] == "spec_plugin"

    def test_validate_and_extract_dependency_settings_no_function_dict(self):
        """Test error when function dict is not available."""
        dependencies = {"smu": ["parse_settings_widget"]}
        mapping = {"smu": "smu_combo"}
        mock_widget = Mock()
        dep_manager = DependencyManager("test_plugin", dependencies, mock_widget, mapping)

        target_settings = {}
        status, result = dep_manager.validate_and_extract_dependency_settings(target_settings)

        assert status == 3
        assert "Error message" in result
        assert "Missing functions" in result["Error message"]

    def test_validate_and_extract_dependency_settings_no_selection(self):
        """Test error when no dependency is selected."""
        mock_smu_combo = Mock()
        mock_smu_combo.currentText.return_value = ""

        dependencies = {"smu": ["parse_settings_widget"]}
        mapping = {"smu": "smu_combo"}
        mock_widget = Mock()
        mock_widget.smu_combo = mock_smu_combo
        dep_manager = DependencyManager("test_plugin", dependencies, mock_widget, mapping)
        dep_manager.set_function_dict({"smu": {"smu_plugin": {"parse_settings_widget": Mock()}}})

        target_settings = {}
        status, result = dep_manager.validate_and_extract_dependency_settings(target_settings)

        assert status == 3
        assert "Error message" in result
        assert "No smu plugin selected" in result["Error message"]

    def test_validate_and_extract_dependency_settings_validation_failure(self):
        """Test error when dependency validation fails."""
        mock_smu_combo = Mock()
        mock_smu_combo.currentText.return_value = "invalid_plugin"

        dependencies = {"smu": ["parse_settings_widget"]}
        mapping = {"smu": "smu_combo"}
        mock_widget = Mock()
        mock_widget.smu_combo = mock_smu_combo
        dep_manager = DependencyManager("test_plugin", dependencies, mock_widget, mapping)
        dep_manager.set_function_dict({"smu": {"smu_plugin": {"parse_settings_widget": Mock()}}})

        target_settings = {}
        status, result = dep_manager.validate_and_extract_dependency_settings(target_settings)

        assert status == 3
        assert "Error message" in result
        assert "validation failed" in result["Error message"]

    def test_validate_and_extract_dependency_settings_missing_function(self):
        """Test error when parse_settings_widget function is missing."""
        mock_smu_combo = Mock()
        mock_smu_combo.currentText.return_value = "smu_plugin"

        dependencies = {"smu": ["parse_settings_widget"]}
        mapping = {"smu": "smu_combo"}
        mock_widget = Mock()
        mock_widget.smu_combo = mock_smu_combo
        dep_manager = DependencyManager("test_plugin", dependencies, mock_widget, mapping)

        # Mock function dict without parse_settings_widget
        mock_function_dict = {
            "smu": {
                "smu_plugin": {}  # Missing parse_settings_widget
            }
        }
        dep_manager.set_function_dict(mock_function_dict)

        target_settings = {}
        status, result = dep_manager.validate_and_extract_dependency_settings(target_settings)

        assert status == 3
        assert "Error message" in result
        assert "parse_settings_widget" in result["Error message"]


class TestLoggingHelper:
    """Test the LoggingHelper class for logging functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_plugin = Mock()
        self.mock_plugin.__class__.__name__ = "TestPlugin"
        self.logging_helper = LoggingHelper(self.mock_plugin)

    def test_init(self):
        """Test LoggingHelper initialization."""
        assert self.logging_helper.plugin_name == "TestPlugin"
        assert isinstance(self.logging_helper, QObject)

    def test_log_info(self):
        """Test info logging."""
        with patch.object(self.logging_helper, "logger_signal") as mock_signal:
            self.logging_helper.log_info("Test info message")

            mock_signal.emit.assert_called_once_with("TestPlugin : INFO : Test info message")

    def test_log_debug(self):
        """Test debug logging."""
        with patch.object(self.logging_helper, "logger_signal") as mock_signal:
            self.logging_helper.log_debug("Test debug message")

            mock_signal.emit.assert_called_once_with("TestPlugin : DEBUG : Test debug message")

    def test_log_warn(self):
        """Test warning logging."""
        with patch.object(self.logging_helper, "logger_signal") as mock_signal:
            self.logging_helper.log_warn("Test warning message")

            mock_signal.emit.assert_called_once_with("TestPlugin : WARN : Test warning message")


class TestPluginException:
    """Test the PluginException class."""

    def test_plugin_exception(self):
        """Test PluginException can be raised."""
        with pytest.raises(PluginException):
            raise PluginException()

    def test_plugin_exception_with_message(self):
        """Test PluginException with custom message."""
        with pytest.raises(PluginException, match="Custom error message"):
            raise PluginException("Custom error message")


class TestIntegration:
    """Integration tests that test multiple components working together."""

    def test_gui_mapper_with_dependency_manager(self):
        """Test integration between GuiMapper and DependencyManager."""
        # Set up mock widget with dependency comboboxes
        mock_widget = Mock()
        mock_smu_combo = Mock(spec=QComboBox)
        mock_widget.smuComboBox = mock_smu_combo
        mock_smu_combo.currentText.return_value = "selected_smu"

        # Set up dependency manager
        dependencies = {"smu": ["connect", "init"]}
        mapping = {"smu": "smuComboBox"}
        dep_manager = DependencyManager("TestPlugin", dependencies, mock_widget, mapping)

        # Set up GUI mapper with the same widget
        gui_mapper = GuiMapper(mock_widget, "TestPlugin")

        # Test that both can work with the same widget
        field_mapping = {"smu_selection": "smuComboBox"}

        # This should extract the combobox value
        status, result = gui_mapper.get_values(field_mapping)
        assert status == 0
        assert result["smu_selection"] == "selected_smu"

        # This should get the selected dependencies
        selected = dep_manager.get_selected_dependencies()
        assert selected["smu"] == "selected_smu"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
