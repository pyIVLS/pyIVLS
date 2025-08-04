"""
Tests for specTimeIV_utils.py components.

This module tests the following classes:
- FileManager: File header creation functionality
- GuiMapper: Dynamic GUI field mapping with bidirectional conversion
- DependencyManager: Plugin dependency management and validation
- LoggingHelper: Logging functionality with Qt signals
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the plugins directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'plugins', 'specTimeIV-0.0.0'))

try:
    from specTimeIV_utils import FileManager, GuiMapper, DependencyManager, LoggingHelper, DataOrder, PluginException
    from PyQt6.QtWidgets import QLineEdit, QCheckBox, QComboBox, QSpinBox, QDoubleSpinBox
    from PyQt6.QtCore import QObject
except ImportError as e:
    pytest.skip(f"Cannot import required modules: {e}", allow_module_level=True)


class TestFileManager:
    """Test the FileManager class for file header creation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.file_manager = FileManager()
        
    def test_create_file_header_basic(self):
        """Test basic file header creation with minimal settings."""
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
            "comment": "Test measurement"
        }
        
        smu_settings = {
            "lineFrequency": 50,
            "sourcehighc": False
        }
        
        header = self.file_manager.create_file_header(settings, smu_settings)
        
        # Check that header contains expected elements
        assert "TestSample" in header
        assert "smua" in header
        assert "voltage injection mode" in header
        assert "Test measurement" in header
        assert "stime, IS, VS" in header  # Single channel output format
        
    def test_create_file_header_dual_channel(self):
        """Test file header creation with dual channel configuration."""
        settings = {
            "samplename": "",  # Test empty sample name
            "channel": "smua",
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
            "comment": "Dual channel test"
        }
        
        smu_settings = {
            "lineFrequency": 60,
            "sourcehighc": True,
            "drainhighc": False
        }
        
        header = self.file_manager.create_file_header(settings, smu_settings)
        
        # Check dual channel specific elements
        assert "{noname}" in header  # Empty sample name handling
        assert "current injection mode" in header
        assert "voltage injection mode" in header  # Drain mode
        assert "stime, IS, VS, ID, VD" in header  # Dual channel output format
        assert "4 point measurement mode" in header
        assert "high capacitance mode" in header
        
    def test_create_file_header_units_voltage_mode(self):
        """Test that units are correctly set for voltage injection mode."""
        settings = {
            "samplename": "UnitTest",
            "channel": "smub",
            "inject": "voltage",
            "sourcevalue": 2.5,
            "sourcelimit": 0.2,
            "sourcedelaymode": "auto",
            "sourcenplc": 0.01,
            "timestep": 0.1,
            "singlechannel": True,
            "sourcesensemode": "2 wire",
            "stoptimer": False,
            "comment": "Voltage mode test"
        }
        
        smu_settings = {
            "lineFrequency": 50,
            "sourcehighc": False
        }
        
        header = self.file_manager.create_file_header(settings, smu_settings)
        
        # In voltage mode: source value in V, limit in A
        assert "2.5 V" in header
        assert "0.2 A" in header
        
    def test_create_file_header_units_current_mode(self):
        """Test that units are correctly set for current injection mode."""
        settings = {
            "samplename": "UnitTest",
            "channel": "smub",
            "inject": "current",
            "sourcevalue": 0.001,
            "sourcelimit": 10.0,
            "sourcedelaymode": "auto",
            "sourcenplc": 0.01,
            "timestep": 0.1,
            "singlechannel": True,
            "sourcesensemode": "2 wire",
            "stoptimer": False,
            "comment": "Current mode test"
        }
        
        smu_settings = {
            "lineFrequency": 50,
            "sourcehighc": False
        }
        
        header = self.file_manager.create_file_header(settings, smu_settings)
        
        # In current mode: source value in A, limit in V
        assert "0.001 A" in header
        assert "10.0 V" in header


class TestGuiMapper:
    """Test the GuiMapper class for dynamic GUI field mapping."""
    
    def setup_method(self):
        """Set up test fixtures with mock widgets."""
        self.mock_widget = Mock()
        self.plugin_name = "TestPlugin"
        self.gui_mapper = GuiMapper(self.mock_widget, self.plugin_name)
        
        # Create mock PyQt6 widgets
        self.mock_line_edit = Mock(spec=QLineEdit)
        self.mock_checkbox = Mock(spec=QCheckBox)
        self.mock_combobox = Mock(spec=QComboBox)
        self.mock_spinbox = Mock(spec=QSpinBox)
        self.mock_double_spinbox = Mock(spec=QDoubleSpinBox)
        
    def test_extract_value_dynamic_line_edit_float(self):
        """Test value extraction from QLineEdit with float conversion."""
        self.mock_line_edit.text.return_value = "3.14"
        
        result = self.gui_mapper._extract_value_dynamic(self.mock_line_edit)
        
        assert result == 3.14
        assert isinstance(result, float)
        
    def test_extract_value_dynamic_line_edit_string(self):
        """Test value extraction from QLineEdit with string fallback."""
        self.mock_line_edit.text.return_value = "test_string"
        
        result = self.gui_mapper._extract_value_dynamic(self.mock_line_edit)
        
        assert result == "test_string"
        assert isinstance(result, str)
        
    def test_extract_value_dynamic_checkbox(self):
        """Test value extraction from QCheckBox."""
        self.mock_checkbox.isChecked.return_value = True
        
        result = self.gui_mapper._extract_value_dynamic(self.mock_checkbox)
        
        assert result is True
        
    def test_extract_value_dynamic_combobox(self):
        """Test value extraction from QComboBox."""
        self.mock_combobox.currentText.return_value = "Option1"
        
        result = self.gui_mapper._extract_value_dynamic(self.mock_combobox)
        
        assert result == "Option1"
        
    def test_extract_value_dynamic_spinbox(self):
        """Test value extraction from QSpinBox."""
        self.mock_spinbox.value.return_value = 42
        
        result = self.gui_mapper._extract_value_dynamic(self.mock_spinbox)
        
        assert result == 42.0
        assert isinstance(result, float)
        
    def test_extract_value_dynamic_double_spinbox(self):
        """Test value extraction from QDoubleSpinBox."""
        self.mock_double_spinbox.value.return_value = 3.14159
        
        result = self.gui_mapper._extract_value_dynamic(self.mock_double_spinbox)
        
        assert result == 3.14159
        
    def test_extract_value_dynamic_unsupported_widget(self):
        """Test that unsupported widget types raise ValueError."""
        unsupported_widget = Mock()
        
        with pytest.raises(ValueError, match="Tried to access unsupported widget type"):
            self.gui_mapper._extract_value_dynamic(unsupported_widget)
            
    def test_set_value_dynamic_line_edit(self):
        """Test setting value to QLineEdit."""
        self.gui_mapper._set_value_dynamic(self.mock_line_edit, 42.5)
        
        self.mock_line_edit.setText.assert_called_once_with("42.5")
        
    def test_set_value_dynamic_checkbox_true(self):
        """Test setting True value to QCheckBox."""
        self.gui_mapper._set_value_dynamic(self.mock_checkbox, True)
        
        self.mock_checkbox.setChecked.assert_called_once_with(True)
        
    def test_set_value_dynamic_checkbox_string_true(self):
        """Test setting string 'True' value to QCheckBox."""
        self.gui_mapper._set_value_dynamic(self.mock_checkbox, "True")
        
        self.mock_checkbox.setChecked.assert_called_once_with(True)
        
    def test_set_value_dynamic_checkbox_false(self):
        """Test setting False value to QCheckBox."""
        self.gui_mapper._set_value_dynamic(self.mock_checkbox, False)
        
        self.mock_checkbox.setChecked.assert_called_once_with(False)
        
    def test_set_value_dynamic_combobox(self):
        """Test setting value to QComboBox."""
        self.gui_mapper._set_value_dynamic(self.mock_combobox, "Option2")
        
        self.mock_combobox.setCurrentText.assert_called_once_with("Option2")
        
    def test_set_value_dynamic_spinbox(self):
        """Test setting value to QSpinBox."""
        self.gui_mapper._set_value_dynamic(self.mock_spinbox, 42.7)
        
        self.mock_spinbox.setValue.assert_called_once_with(42)
        
    def test_set_value_dynamic_double_spinbox(self):
        """Test setting value to QDoubleSpinBox."""
        self.gui_mapper._set_value_dynamic(self.mock_double_spinbox, 3.14159)
        
        self.mock_double_spinbox.setValue.assert_called_once_with(3.14159)
        
    def test_set_value_dynamic_unsupported_widget(self):
        """Test that unsupported widget types raise ValueError."""
        unsupported_widget = Mock()
        
        with pytest.raises(ValueError, match="Unsupported widget type called for guimapper"):
            self.gui_mapper._set_value_dynamic(unsupported_widget, "value")
            
    def test_validate_value_dynamic_with_converter(self):
        """Test value validation with converter function."""
        validation_config = {
            "converter": lambda x: x * 2,
            "validator": lambda x: x > 0,
            "error_message": "Value must be positive"
        }
        
        status, result = self.gui_mapper._validate_value_dynamic("test_field", 5, validation_config)
        
        assert status == 0
        assert result == 10  # 5 * 2
        
    def test_validate_value_dynamic_converter_failure(self):
        """Test validation when converter function fails."""
        validation_config = {
            "converter": lambda x: x / 0,  # This will raise ZeroDivisionError
            "validator": lambda x: True
        }
        
        status, result = self.gui_mapper._validate_value_dynamic("test_field", 5, validation_config)
        
        assert status == 1
        assert "conversion failed" in result["Error message"]
        
    def test_validate_value_dynamic_validator_failure(self):
        """Test validation when validator function fails."""
        validation_config = {
            "validator": lambda x: x > 10,
            "error_message": "Value must be greater than 10"
        }
        
        status, result = self.gui_mapper._validate_value_dynamic("test_field", 5, validation_config)
        
        assert status == 1
        assert "Value must be greater than 10" in result["Error message"]
        
    def test_validate_value_dynamic_validator_exception(self):
        """Test validation when validator function raises exception."""
        validation_config = {
            "validator": lambda x: x.non_existent_method(),  # This will raise AttributeError
        }
        
        status, result = self.gui_mapper._validate_value_dynamic("test_field", 5, validation_config)
        
        assert status == 1
        assert "validation failed" in result["Error message"]
        
    def test_get_values_success(self):
        """Test successful value extraction from multiple widgets."""
        # Set up mock widgets
        self.mock_widget.lineEdit1 = self.mock_line_edit
        self.mock_widget.checkBox1 = self.mock_checkbox
        
        self.mock_line_edit.text.return_value = "42.5"
        self.mock_checkbox.isChecked.return_value = True
        
        field_mapping = {
            "value1": "lineEdit1",
            "value2": "checkBox1"
        }
        
        validation_rules = {
            "value1": {
                "validator": lambda x: x > 0,
                "error_message": "Must be positive"
            }
        }
        
        status, result = self.gui_mapper.get_values(field_mapping, validation_rules)
        
        assert status == 0
        assert result["value1"] == 42.5
        assert result["value2"] is True
        
    def test_get_values_widget_not_found(self):
        """Test error handling when widget is not found."""
        # Create a mock widget that doesn't have the attribute we're looking for
        mock_widget_without_attr = Mock(spec=[])  # Empty spec means no attributes
        gui_mapper = GuiMapper(mock_widget_without_attr, "TestPlugin")
        
        field_mapping = {"value1": "nonexistent_widget"}
        
        status, result = gui_mapper.get_values(field_mapping)
        
        assert status == 1
        assert "Widget 'nonexistent_widget' not found" in result["Error message"]
        
    def test_set_values_success(self):
        """Test successful value setting to multiple widgets."""
        # Set up mock widgets
        self.mock_widget.lineEdit1 = self.mock_line_edit
        self.mock_widget.checkBox1 = self.mock_checkbox
        
        settings = {
            "value1": 42.5,
            "value2": True
        }
        
        field_mapping = {
            "value1": "lineEdit1",
            "value2": "checkBox1"
        }

        validation_rules = {}

        status, result = self.gui_mapper.set_values(settings, field_mapping, validation_rules)

        assert status == 0
        self.mock_line_edit.setText.assert_called_once_with("42.5")
        self.mock_checkbox.setChecked.assert_called_once_with(True)
        
    def test_set_values_with_display_converter(self):
        """Test value setting with display converter."""
        self.mock_widget.lineEdit1 = self.mock_line_edit
        
        settings = {"value1": 1000}  # Stored in milliseconds
        field_mapping = {"value1": "lineEdit1"}
        validation_rules = {
            "value1": {
                "display_converter": lambda x: x / 1000  # Convert to seconds for display
            }
        }
        
        status, result = self.gui_mapper.set_values(settings, field_mapping, validation_rules)
        
        assert status == 0
        self.mock_line_edit.setText.assert_called_once_with("1.0")
        
    def test_set_values_display_converter_failure(self):
        """Test error handling when display converter fails."""
        self.mock_widget.lineEdit1 = self.mock_line_edit
        
        settings = {"value1": "not_a_number"}
        field_mapping = {"value1": "lineEdit1"}
        validation_rules = {
            "value1": {
                "display_converter": lambda x: x / 1000  # This will fail with string
            }
        }
        
        status, result = self.gui_mapper.set_values(settings, field_mapping, validation_rules)
        
        assert status == 1
        assert "Display conversion failed" in result["Error message"]


class TestDependencyManager:
    """Test the DependencyManager class for plugin dependency management."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.plugin_name = "TestPlugin"
        self.dependencies = {
            "smu": ["connect", "init", "measure"],
            "spectro": ["scan", "get_spectrum"]
        }
        self.mock_widget = Mock()
        self.mapping = {
            "smu": "smuComboBox",
            "spectro": "spectroComboBox"
        }
        
        # Set up mock comboboxes
        self.mock_smu_combo = Mock()
        self.mock_spectro_combo = Mock()
        self.mock_widget.smuComboBox = self.mock_smu_combo
        self.mock_widget.spectroComboBox = self.mock_spectro_combo
        
        self.dependency_manager = DependencyManager(
            self.plugin_name, self.dependencies, self.mock_widget, self.mapping
        )
        
    def test_init(self):
        """Test DependencyManager initialization."""
        assert self.dependency_manager.plugin_name == "TestPlugin"
        assert self.dependency_manager.dependencies == self.dependencies
        assert self.dependency_manager.widget == self.mock_widget
        assert self.dependency_manager.combobox_mapping == self.mapping
        assert self.dependency_manager.function_dict == {}
        
    def test_validate_dependencies_success(self):
        """Test successful dependency validation."""
        function_dict = {
            "smu": {
                "plugin1": {"connect": Mock(), "init": Mock(), "measure": Mock(), "extra": Mock()}
            },
            "spectro": {
                "plugin2": {"scan": Mock(), "get_spectrum": Mock()}
            }
        }
        
        self.dependency_manager.function_dict = function_dict
        
        is_valid, missing = self.dependency_manager.validate_dependencies()
        
        assert is_valid is True
        assert missing == []
        
    def test_validate_dependencies_missing_plugin_type(self):
        """Test dependency validation when plugin type is missing."""
        function_dict = {
            "smu": {
                "plugin1": {"connect": Mock(), "init": Mock(), "measure": Mock()}
            }
            # Missing "spectro" type
        }
        
        self.dependency_manager.function_dict = function_dict
        
        is_valid, missing = self.dependency_manager.validate_dependencies()
        
        assert is_valid is False
        assert "spectro.scan" in missing
        assert "spectro.get_spectrum" in missing
        
    def test_validate_dependencies_missing_functions(self):
        """Test dependency validation when functions are missing."""
        function_dict = {
            "smu": {
                "plugin1": {"connect": Mock(), "init": Mock()}  # Missing "measure"
            },
            "spectro": {
                "plugin2": {"scan": Mock()}  # Missing "get_spectrum"
            }
        }
        
        self.dependency_manager.function_dict = function_dict
        
        is_valid, missing = self.dependency_manager.validate_dependencies()
        
        assert is_valid is False
        assert "smu.measure" in missing
        assert "spectro.get_spectrum" in missing
        
    def test_update_comboboxes(self):
        """Test combobox updates when function dict is set."""
        function_dict = {
            "smu": {
                "smu_plugin1": {"connect": Mock()},
                "smu_plugin2": {"connect": Mock()}
            },
            "spectro": {
                "spectro_plugin1": {"scan": Mock()}
            }
        }
        
        self.dependency_manager.function_dict = function_dict
        
        # Check that comboboxes were updated
        self.mock_smu_combo.clear.assert_called_once()
        self.mock_smu_combo.addItems.assert_called_once_with(["smu_plugin1", "smu_plugin2"])
        
        self.mock_spectro_combo.clear.assert_called_once()
        self.mock_spectro_combo.addItems.assert_called_once_with(["spectro_plugin1"])
        
    def test_update_comboboxes_restore_selection(self):
        """Test that previous selection is restored when updating comboboxes."""
        self.mock_smu_combo.currentText.return_value = "smu_plugin1"
        
        function_dict = {
            "smu": {
                "smu_plugin1": {"connect": Mock()},
                "smu_plugin2": {"connect": Mock()}
            }
        }
        
        self.dependency_manager.function_dict = function_dict
        
        # Should try to restore the previous selection
        self.mock_smu_combo.setCurrentText.assert_called_with("smu_plugin1")
        
    def test_get_selected_dependencies(self):
        """Test getting currently selected dependencies."""
        self.mock_smu_combo.currentText.return_value = "selected_smu"
        self.mock_spectro_combo.currentText.return_value = "selected_spectro"
        
        selected = self.dependency_manager.get_selected_dependencies()
        
        assert selected == {
            "smu": "selected_smu",
            "spectro": "selected_spectro"
        }
        
        
    def test_validate_selection_success(self):
        """Test successful plugin selection validation."""
        function_dict = {
            "smu": {
                "good_plugin": {"connect": Mock(), "init": Mock(), "measure": Mock()}
            }
        }
        
        self.dependency_manager.function_dict = function_dict
        
        is_valid, error = self.dependency_manager.validate_selection("smu", "good_plugin")
        
        assert is_valid is True
        assert error == ""
        
    def test_validate_selection_unknown_dependency_type(self):
        """Test validation with unknown dependency type."""
        is_valid, error = self.dependency_manager.validate_selection("unknown", "plugin")
        
        assert is_valid is False
        assert "Unknown dependency type" in error
        
    def test_validate_selection_plugin_not_found(self):
        """Test validation when plugin is not found."""
        function_dict = {
            "smu": {
                "existing_plugin": {"connect": Mock()}
            }
        }
        
        self.dependency_manager.function_dict = function_dict
        
        is_valid, error = self.dependency_manager.validate_selection("smu", "nonexistent_plugin")
        
        assert is_valid is False
        assert "plugin 'nonexistent_plugin' not found" in error
        
    def test_validate_selection_missing_functions(self):
        """Test validation when plugin is missing required functions."""
        function_dict = {
            "smu": {
                "incomplete_plugin": {"connect": Mock()}  # Missing "init" and "measure"
            }
        }
        
        self.dependency_manager.function_dict = function_dict
        
        is_valid, error = self.dependency_manager.validate_selection("smu", "incomplete_plugin")
        
        assert is_valid is False
        assert "missing functions" in error
        assert "init" in error
        assert "measure" in error
        
        

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
        with patch.object(self.logging_helper, 'logger_signal') as mock_signal:
            self.logging_helper.log_info("Test info message")
            
            mock_signal.emit.assert_called_once_with("TestPlugin : INFO : Test info message")
            
    def test_log_debug(self):
        """Test debug logging."""
        with patch.object(self.logging_helper, 'logger_signal') as mock_signal:
            self.logging_helper.log_debug("Test debug message")
            
            mock_signal.emit.assert_called_once_with("TestPlugin : DEBUG : Test debug message")
            
    def test_log_warn(self):
        """Test warning logging."""
        with patch.object(self.logging_helper, 'logger_signal') as mock_signal:
            self.logging_helper.log_warn("Test warning message")
            
            mock_signal.emit.assert_called_once_with("TestPlugin : WARN : Test warning message")
            



class TestDataOrder:
    """Test the DataOrder enum."""
    
    def test_data_order_values(self):
        """Test DataOrder enum values."""
        assert DataOrder.VOLTAGE.value == 1
        assert DataOrder.CURRENT.value == 0


class TestPluginException:
    """Test the PluginException class."""
    
    def test_plugin_exception(self):
        """Test PluginException can be raised and caught."""
        with pytest.raises(PluginException):
            raise PluginException("Test error message")
            
    def test_plugin_exception_with_message(self):
        """Test PluginException with error message."""
        try:
            raise PluginException("Custom error message")
        except PluginException as e:
            assert str(e) == "Custom error message"


class TestIntegration:
    """Integration tests that test multiple components working together."""
    
    def test_gui_mapper_with_dependency_manager(self):
        """Test GuiMapper and DependencyManager working together."""
        # Set up mock widget with both regular fields and dependency comboboxes
        mock_widget = Mock()
        mock_widget.lineEdit1 = Mock(spec=QLineEdit)
        mock_widget.smuComboBox = Mock(spec=QComboBox)
        
        mock_widget.lineEdit1.text.return_value = "42.5"
        mock_widget.smuComboBox.currentText.return_value = "selected_smu"
        
        # Create GuiMapper
        gui_mapper = GuiMapper(mock_widget, "TestPlugin")
        
        # Create DependencyManager
        dependencies = {"smu": ["connect", "measure"]}
        mapping = {"smu": "smuComboBox"}
        dep_manager = DependencyManager("TestPlugin", dependencies, mock_widget, mapping)
        
        # Set up function dict
        function_dict = {
            "smu": {
                "selected_smu": {"connect": Mock(), "measure": Mock()}
            }
        }
        dep_manager.function_dict = function_dict
        
        # Test that both work together
        field_mapping = {"value1": "lineEdit1"}
        status, values = gui_mapper.get_values(field_mapping)
        
        selected_deps = dep_manager.get_selected_dependencies()
        is_valid, missing = dep_manager.validate_dependencies()
        
        assert status == 0
        assert values["value1"] == 42.5
        assert selected_deps["smu"] == "selected_smu"
        assert is_valid is True
        assert missing == []


if __name__ == "__main__":
    pytest.main([__file__])
