"""
Comprehensive tests for plugin_components.py

This module tests the following classes:
- FileManager: File header creation functionality
- DependencyManager: Plugin dependency management and validation
- LoggingHelper: Logging functionality with Qt signals
- DataOrder: Enum for data ordering
- PluginException: Custom exception class
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch

# Add the components directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "components"))

try:
    from plugin_components import (
        FileManager,
        DependencyManager,
        LoggingHelper,
        PluginException,
        filter_to_valid_methods,
    )
    from PyQt6.QtWidgets import QApplication
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


class TestFilterToValidMethods:
    """Test filtering of function dictionaries by required methods."""

    def test_filters_to_valid_plugins(self):
        function_dict = {
            "smu": {
                "valid": {"connect": Mock(), "init": Mock(), "measure": Mock()},
                "partial": {"connect": Mock()},
            }
        }
        required = {"smu": ["connect", "init"]}

        is_valid, missing = filter_to_valid_methods(function_dict, required)

        assert is_valid is True
        assert missing == []
        assert list(function_dict["smu"].keys()) == ["valid"]

    def test_missing_dependency_type(self):
        function_dict = {"spectro": {"ocean": {"measure": Mock()}}}
        required = {"smu": ["connect"]}

        is_valid, missing = filter_to_valid_methods(function_dict, required)

        assert is_valid is False
        assert missing == ["smu.connect"]
        assert "smu" not in function_dict

    def test_missing_methods_when_no_valid_plugins(self):
        function_dict = {
            "smu": {
                "partial": {"connect": Mock()},
                "also_partial": {"init": Mock()},
            }
        }
        required = {"smu": ["connect", "init"]}

        is_valid, missing = filter_to_valid_methods(function_dict, required)

        assert is_valid is False
        assert missing == ["smu.connect", "smu.init"]
        assert function_dict["smu"] == {}


class TestDependencyManager:
    """Simple tests for DependencyManager behavior."""

    def setup_method(self):
        self.plugin_name = "TestPlugin"
        self.dependencies = {"smu": ["connect", "init", "measure"], "spectro": ["scan", "get_spectrum"]}
        self.dependency_manager = DependencyManager(self.plugin_name, self.dependencies)

    def test_set_available_dependency_functions_prunes_and_reports_missing(self):
        function_dict = {
            "smu": {
                "invalid": ["connect", "init"],
                "valid": ["connect", "init", "measure"],
            },
            "spectro": {
                "invalid": ["scan"],
            },
            "extra": {"ignored": ["x"]},
        }

        is_valid, missing = self.dependency_manager.set_available_dependency_functions(function_dict)

        assert is_valid is False
        assert "spectro.scan" in missing
        assert "spectro.get_spectrum" in missing
        assert self.dependency_manager.function_dict["smu"] == {"valid": ["connect", "init", "measure"]}
        assert self.dependency_manager.function_dict["spectro"] == {}
        assert "extra" not in self.dependency_manager.function_dict

    def test_function_dict_property_prunes_invalid_plugins(self):
        """Setting function_dict directly should keep only valid providers for each dependency type."""
        self.dependency_manager.function_dict = {
            "smu": {
                "ok": ["connect", "init", "measure"],
                "missing_measure": ["connect", "init"],
            },
            "spectro": {
                "ok": ["scan", "get_spectrum"],
                "missing_get": ["scan"],
            },
            "unused": {"plugin": ["noop"]},
        }

        assert self.dependency_manager.function_dict == {
            "smu": {"ok": ["connect", "init", "measure"]},
            "spectro": {"ok": ["scan", "get_spectrum"]},
        }

    def test_function_dict_property_updates_missing_functions(self):
        """Setting function_dict directly should update missing_functions for unresolved dependencies."""
        self.dependency_manager.function_dict = {
            "smu": {"partial": ["connect", "init"]},
            # spectro dependency type intentionally absent
        }

        assert "smu.connect" in self.dependency_manager.missing_functions
        assert "smu.init" in self.dependency_manager.missing_functions
        assert "smu.measure" in self.dependency_manager.missing_functions
        assert "spectro.scan" in self.dependency_manager.missing_functions
        assert "spectro.get_spectrum" in self.dependency_manager.missing_functions

    def test_initialize_dependency_selection_restores_last_choice(self):
        function_dict = {
            "smu": {"smu_ok": ["connect", "init", "measure"]},
            "spectro": {"spec_ok": ["scan", "get_spectrum"]},
        }
        self.dependency_manager.set_available_dependency_functions(function_dict)
        self.dependency_manager.initialize_dependency_selection({"smu": "smu_ok", "spectro": "spec_ok"})
        # initialize stores remembered selection only; active selection updates on parse.
        assert self.dependency_manager.get_selected_dependency_plugins() == {}

    def test_get_selected_dependency_plugins(self):
        self.dependency_manager.set_selected_dependency_plugins({"smu": "selected_smu", "spectro": "selected_spec"})

        selected = self.dependency_manager.get_selected_dependency_plugins()

        assert selected == {"smu": "selected_smu", "spectro": "selected_spec"}

    def test_parse_dependencies_success(self):
        """Test successful dependency settings extraction."""
        # Mock dependencies and comboboxes
        mock_smu_combo = Mock()
        mock_smu_combo.currentText.return_value = "smu_plugin"
        mock_spec_combo = Mock()
        mock_spec_combo.currentText.return_value = "spec_plugin"

        # Set up dependency manager with both dependencies (list of required functions)
        dependencies = {"smu": ["parse_settings_widget"], "spectrometer": ["parse_settings_widget"]}
        dep_manager = DependencyManager("test_plugin", dependencies)
        dep_manager.set_selected_dependency_plugins({"smu": "smu_plugin", "spectrometer": "spec_plugin"})

        # Mock function dict with parse_settings_widget functions
        mock_function_dict = {
            "smu": {"smu_plugin": {"parse_settings_widget": Mock(return_value=(0, {"param1": "value1"}))}},
            "spectrometer": {"spec_plugin": {"parse_settings_widget": Mock(return_value=(0, {"param2": "value2"}))}},
        }
        dep_manager.set_available_dependency_functions(mock_function_dict)

        # Test the method
        target_settings = {}
        status, result = dep_manager.parse_dependencies(target_settings)

        assert status == 0
        assert "smu_settings" in result
        assert "spectrometer_settings" in result
        assert result["smu_settings"] == {"param1": "value1"}
        assert result["spectrometer_settings"] == {"param2": "value2"}
        assert target_settings["smu"] == "smu_plugin"
        assert target_settings["spectrometer"] == "spec_plugin"

    def test_parse_dependencies_no_function_dict(self):
        """Test error when function dict is not available."""
        dependencies = {"smu": ["parse_settings_widget"]}
        dep_manager = DependencyManager("test_plugin", dependencies)

        target_settings = {}
        status, result = dep_manager.parse_dependencies(target_settings)

        assert status == 3
        assert "Missing functions" in result["Error message"]

    def test_parse_dependencies_no_selection(self):
        """Test error when no dependency is selected."""
        mock_smu_combo = Mock()
        mock_smu_combo.currentText.return_value = ""

        dependencies = {"smu": ["parse_settings_widget"]}
        dep_manager = DependencyManager("test_plugin", dependencies)
        dep_manager.set_available_dependency_functions({"smu": {"smu_plugin": {"parse_settings_widget": Mock()}}})

        target_settings = {}
        status, result = dep_manager.parse_dependencies(target_settings)

        assert status == 3
        assert "No smu plugin selected" in result["Error message"]

    def test_parse_dependencies_plugin_not_available(self):
        """Test error when selected dependency plugin is not available."""
        mock_smu_combo = Mock()
        mock_smu_combo.currentText.return_value = "invalid_plugin"

        dependencies = {"smu": ["parse_settings_widget"]}
        dep_manager = DependencyManager("test_plugin", dependencies)
        dep_manager.set_selected_dependency_plugins({"smu": "invalid_plugin"})
        dep_manager.set_available_dependency_functions({"smu": {"smu_plugin": {"parse_settings_widget": Mock()}}})

        target_settings = {}
        status, result = dep_manager.parse_dependencies(target_settings)

        assert status == 3
        assert "not available" in result["Error message"]

    def test_parse_dependencies_missing_function(self):
        """Test error when parse_settings_widget function is missing in selected plugin."""
        mock_smu_combo = Mock()
        mock_smu_combo.currentText.return_value = "smu_plugin"

        dependencies = {"smu": ["parse_settings_widget"]}
        dep_manager = DependencyManager("test_plugin", dependencies)
        dep_manager.set_selected_dependency_plugins({"smu": "smu_plugin"})

        # Mock function dict without parse_settings_widget
        mock_function_dict = {
            "smu": {
                "smu_plugin": {}  # Missing parse_settings_widget
            }
        }
        dep_manager.set_available_dependency_functions(mock_function_dict)

        target_settings = {}
        status, result = dep_manager.parse_dependencies(target_settings)

        assert status == 3
        assert "smu plugin 'smu_plugin' not available" in result["Error message"]


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
    """Simple integration tests for plugin components."""

    def test_dependency_manager_selection_integration(self):
        """Test that explicit selections are preserved by DependencyManager."""
        dependencies = {"smu": ["connect", "init"]}
        dep_manager = DependencyManager("TestPlugin", dependencies)
        dep_manager.set_selected_dependency_plugins({"smu": "selected_smu"})

        selected = dep_manager.get_selected_dependency_plugins()
        assert selected["smu"] == "selected_smu"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
