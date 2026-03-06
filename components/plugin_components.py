"""
Using composition instead of multiple inheritance,
mostly because this is similar to the existing implementations.
The added benefit is that classes don't need to inherit from QObject,
since that is handled by the logger that actually uses QObject functionality.

Core ideas:
- plugin functionality implemented in a low level class that works by itself. The low level should not use the components in this file.
- plugin GUI functionality implemented in a separate class that uses the low level class. The plugin GUI class can use these components.
This also helps in keeping the GUI implementation relatively clean.
- Most of the common functionality should be moved to a component, since:
    1. Reduce repetitive code, make it easier to maintain with a single point of change (not rewriting all plugins on all changes)
    2. Make it easier to implement new plugins, since the common functionality is already implemented
    3. Way way way easier to test the components than all plugins by themselves.


This file includes:
- ConnectionIndicatorStyle: Enum for connection indicator styles
- CloseLockSignalProvider: Component to provide closelock signal functionality without QObject inheritance
- public: Decorator to mark a function as public in the plugin system. Also checks that the return type is annotated correctly.
- get_public_methods: Function to get a dict of public methods in an object instance that are marked with the @public
- filter_to_valid_methods: Function to filter a function dictionary to only include valid methods based on required functions.
- PyIVLSReturnCode: Enum for standard return codes for pyIVLS plugins.
- FileManager: Class for handling file operations for plugins, including creating headers for CSV files and spectrometer files.
- DependencyManager: Class to handle dependencies between plugins, including checking for missing dependencies and handling dependency-related GUI changes
- LoggingHelper: Class for logging messages with different severity levels


"""

import sys
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor as Qcolor

# Qcolors for manipulators as list
MANIPULATOR_COLORS = (Qcolor(255, 0, 0), Qcolor(0, 255, 0), Qcolor(0, 0, 255), Qcolor(255, 255, 0))


class ConnectionIndicatorStyle(Enum):
    """Enum for connection indicator styles."""

    GREEN_CONNECTED = "border-radius: 10px; background-color: rgb(38, 162, 105); min-height: 20px; min-width: 20px;"
    RED_DISCONNECTED = "border-radius: 10px; background-color: rgb(165, 29, 45); min-height: 20px; min-width: 20px;"


class CloseLockSignalProvider(QObject):
    """Component to provide closelock signal functionality without QObject inheritance."""

    closeLock = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

    def emit_close_lock(self, locked: bool):
        """Emit the close lock signal."""
        self.closeLock.emit(locked)


def public(func):
    """Decorator to mark a function as public in the plugin system. Also checks that the return type is annotated correctly.
    HOX: this does not enforce anything but that the annotation is correct. The user can still return anything, but any IDE or linter should at least warn the developer about it.
    """
    # currently enforcement of the return type is not active.
    """
    expected_type = PyIVLSReturn
    sig = inspect.signature(func)

    assert sig.return_annotation == expected_type, f"Function '{func.__name__}' must have return type annotation {expected_type}, but got {sig.return_annotation}"
    """
    func._is_public = True
    return func


def get_public_methods(obj) -> Dict:
    """
    Get a dict of public methods in an object instance that are marked with the @public decorator.

    Args:
        obj: Object instance to inspect

    Returns:
        Dict of method names to their callable objects
    """
    return {name: getattr(obj, name) for name in dir(obj) if callable(getattr(obj, name, None)) and getattr(getattr(obj, name, None), "_is_public", False)}


def filter_to_valid_methods(function_dict: Dict[str, Any], required_functions: Dict[str, list]) -> Tuple[bool, List[str]]:
    """
    Filter a function dictionary to only include valid methods based on required functions. UPDATING IS DONE IN PLACE FOR FUNCTION_DICT ARGUMENT.

    Args:
        function_dict: Dict of available functions from plugins
        required_functions: Dict mapping dependency types to required function lists
                         e.g., {"smu": ["connect", "init"], "spectro": ["measure"]}

    Returns:
        Tuple of (is_valid, missing_functions_list) where missing_functions_list contains
        unresolved methods per dependency type. A method is unresolved when no single plugin
        can satisfy the full required method set for that dependency type.
    """
    missing_functions: List[str] = []
    is_valid = True

    for dependency_type, required_funcs in required_functions.items():
        # missing an entire dep type wrecks leads to immediate fail.
        if dependency_type not in function_dict:
            missing_functions.extend([f"{dependency_type}.{func}" for func in required_funcs])
            is_valid = False
            # epic fail
            continue

        # filter to plgs of dep type
        available_plugins = function_dict[dependency_type]
        valid_plugins = {plugin_name: plugin_funcs for plugin_name, plugin_funcs in available_plugins.items() if all(func in plugin_funcs for func in required_funcs)}

        # Update in place to only include plugins that satisfy all required functions.
        function_dict[dependency_type] = valid_plugins

        # If no plugin satisfies the full required set, dependency is invalid.
        if not valid_plugins:
            is_valid = False
            missing_functions.extend([f"{dependency_type}.{func}" for func in required_funcs])

    return is_valid, missing_functions


class PyIVLSReturnCode(Enum):
    """Standard return codes for pyIVLS plugins."""

    SUCCESS = 0
    VALUE_ERROR = 1
    DEPENDENCY_ERROR = 2
    MISSING_DEPENDENCY = 3
    HARDWARE_ERROR = 4
    THREAD_STOPPED = 5


class FileManager:
    """Component that builds standard file headers for plugins. Provides headers for standard IV and standard spectro."""

    @staticmethod
    def create_file_header(settings: Dict[str, Any], smu_settings: Dict[str, Any]) -> str:
        """Creates a legacy compatible SMU file header. The args accept standard SWEEP settings dict and SMU settings dict.

        Args:
            settings (Dict[str, Any]): Dictionary with keys:
                - samplename: str, name of the sample
                - channel: str, source channel used
                - inject: str, injection mode for source (voltage or current)
                - sourcevalue: float, set value for source
                - sourcelimit: float, limit for source step
                - sourcedelaymode: str, "auto" or "manual" for source delay
                - sourcedelay: int, stabilization period for source in s
                - sourcenplc: float, NPLC value for source measurement time
                - singlechannel: bool, whether only one channel is used
                - draininject: str, injection mode for drain (voltage or current)
                - drainvalue: float, set value for drain (if not singlechannel)
                - drainlimit: float, limit for drain step (if not singlechannel)
                - draindelaymode: str, "auto" or "manual" for drain delay (if not singlechannel)
                - draindelay: int, stabilization period for drain in s (if manual and not singlechannel)
                - drainnplc: float, NPLC value for drain measurement time (if not singlechannel)
                - stopsignal: bool, whether a stop timer is set
                - stopafter: int, minutes after which to stop if stopsignal is True
                - sourcesensemode: str, "2 wire" or "4 wire" for source sensing mode
                - drainsensemode: str, "2 wire" or "4 wire" for drain sensing mode
                - comment: str, user comment to include in header
            smu_settings (Dict[str, Any]): Dictionary with keys:
                - lineFrequency: int, line frequency in Hz

        Returns:
            str: header for SMU measurement file
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
            comment = f"{comment}Measurement stabilization period is {settings['sourcedelay'] / 1000} ms\n#"
        comment = (
            f"{comment}NPLC value {settings['sourcenplc'] * 1000 / smu_settings['lineFrequency']} ms (for detected line frequency {smu_settings['lineFrequency']} Hz is {settings['sourcenplc']})\n#"
        )
        comment = f"{comment}\n#\n#"
        comment = f"{comment}Continuous operation of the source with step time settings['timestep'] \n#\n#\n#"

        if not settings["singlechannel"]:
            comment = f"{comment}Drain in {settings['draininject']} injection mode\n#"
            if settings["draininject"] == "voltage":
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
                comment = f"{comment}Measurement stabilization period for drain is {settings['draindelay'] / 1000} ms\n#"
            comment = (
                f"{comment}NPLC value {settings['drainnplc'] * 1000 / smu_settings['lineFrequency']} ms (for detected line frequency {smu_settings['lineFrequency']} Hz is {settings['drainnplc']})\n#"
            )
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
    def create_spectrometer_header(varDict: Optional[Dict[str, Any]] = None, separator: str = ";") -> str:
        """Build a standard spectrometer header from a dictionary

        Args:
            varDict (Dict[str, Any], optional): Contains optional keys:
            - average
            - integrationtime
            - triggermode
            - name
            - comment
            - timestamp
            separator (str, optional): Defaults to ";".

        Returns:
            str: header for spectrometer measurement file
        """

        if varDict is None:
            varDict = {}

        comment = "Thorlabs FTS operated by pyIVSL\n"
        comment = f"{comment}#[SpectrumHeader]\n"
        comment = f"{comment}Date{separator}{datetime.now().strftime('%Y%m%d')}\n"
        comment = f"{comment}Time{separator}{datetime.now().strftime('%H%M%S%f')[:-4]}\n"
        comment = f"{comment}GMTTime{separator}{datetime.utcnow().strftime('%H%M%S%f')[:-4]}\n"
        comment = f"{comment}XAxisUnit{separator}nm_air\n"
        comment = f"{comment}YAxisUnit{separator}intensity\n"

        if "average" in varDict:
            comment = f"{comment}Average{separator}{varDict['average']}\n"
        else:
            comment = f"{comment}Average{separator}0\n"

        comment = f"{comment}RollingAverage{separator}0\n"
        comment = f"{comment}SpectrumSmooth{separator}0\n"
        comment = f"{comment}SSmoothParam1{separator}0\n"
        comment = f"{comment}SSmoothParam2{separator}0\n"
        comment = f"{comment}SSmoothParam3{separator}0\n"
        comment = f"{comment}SSmoothParam4{separator}0\n"
        comment = f"{comment}IntegrationTime{separator}{varDict.get('integrationtime', 0)}\n"
        comment = f"{comment}TriggerMode{separator}{varDict.get('triggermode', 0)}\n"
        comment = f"{comment}InterferometerSerial{separator}M00903839\n"
        comment = f"{comment}Source\n"
        comment = f"{comment}AirMeasureOpt{separator}0\n"
        comment = f"{comment}WnrMin{separator}0\n"
        comment = f"{comment}WnrMax{separator}0\n"
        comment = f"{comment}Length{separator}3648\n"
        comment = f"{comment}Resolution{separator}0\n"
        comment = f"{comment}ADC{separator}0\n"
        comment = f"{comment}Instrument{separator}0\n"
        comment = f"{comment}Model{separator}CCS175\n"
        comment = f"{comment}Type{separator}emission\n"
        comment = f"{comment}AirTemp{separator}0\n"
        comment = f"{comment}AirPressure{separator}0\n"
        comment = f"{comment}AirRelHum{separator}0\n"

        if "name" in varDict:
            comment = f"{comment}Name{separator}{varDict['name']}\n"
        else:
            comment = f"{comment}Name{separator}\n"

        if "comment" in varDict:
            comment = f'{comment}Comment{separator}"{varDict["comment"]}"\n'
        else:
            comment = f'{comment}Comment{separator} ""\n'

        # Add timestamp if provided
        if "timestamp" in varDict:
            comment = f"{comment}Timestamp{separator}{varDict['timestamp']}\n"

        comment = f"{comment}#[Data]\n"
        return comment


class DataOrder(Enum):
    """Enum for data ordering."""

    V = 1
    I = 0  # noqa: E741


class PluginException(Exception):
    """Base exception for plugin errors."""

    pass


class DependencyManager:
    """
    Wrapper to manage gathering dependencies, parsing dep settings and providing a consistent interface for plugins to access the methods they need.
    USAGE:
    - Initialize with or without widget and with the declared dependencies.
    - When loading data from .ini, call initialize_dependency_selection to set the initial state of the dependency comboboxes based on saved settings.
    - When receiving the function dict from the plugin system, call set_available_dependency_functions to set the available functions and check for missing dependencies. This will also update the comboboxes to only show valid options.
    - Access available function_dict through the property. This includes all plugins that satify the required method sets, and should be filtered after fetching
    - "validate_and_extract_dependency_settings" is used to parse the settings widgets for plugins and add their settings to the settings dict.


    """

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
        self.last_selected = {}

    @property
    def function_dict(self) -> Dict[str, Any]:
        """Get the current function dictionary."""
        return self._function_dict

    @function_dict.setter
    def function_dict(self, value: Dict[str, Any]) -> None:
        """Set available dependency functions, pruning invalid providers first."""
        pruned_function_dict, is_valid, missing_functions = self._prune_dependency_function_dict(value)
        self._function_dict = pruned_function_dict
        self.missing_functions = missing_functions
        self._update_comboboxes()

    def _prune_dependency_function_dict(self, function_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, List[str]]:
        """Keep only declared dependency types and plugins that satisfy required methods."""
        dependency_function_dict = {dependency_type: function_dict.get(dependency_type, {}) for dependency_type in self.dependencies.keys()}
        is_valid, missing_functions = filter_to_valid_methods(dependency_function_dict, self.dependencies)
        return dependency_function_dict, is_valid, missing_functions

    def set_available_dependency_functions(self, function_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Set and validate dependency functions from the plugin system.

        Returns:
            Tuple[bool, List[str]]: (is_valid, missing_functions)
        """
        self.function_dict = function_dict
        return len(self.missing_functions) == 0, self.missing_functions

    def initialize_dependency_selection(self, settings: Dict[str, Any]):
        """Initialize remembered dependency selections from settings and refresh comboboxes."""
        self.last_selected = settings.copy()
        self._update_comboboxes()
        return (0, {})

    def _update_comboboxes(self) -> None:
        """Update all dependency comboboxes with available plugins."""
        if not self.widget:
            return

        for dependency_type, combobox_name in self.combobox_mapping.items():
            if dependency_type in self._function_dict:
                combobox = getattr(self.widget, combobox_name)
                combobox.clear()
                available_plugins = list(self._function_dict[dependency_type].keys())
                combobox.addItems(available_plugins)
                # Try to restore previous selection if it's still available
                if dependency_type in self.last_selected:
                    last_selection = self.last_selected[dependency_type]
                    if last_selection in available_plugins:
                        combobox.setCurrentText(last_selection)

    def get_selected_dependency_plugins(self) -> Dict[str, str]:
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

    def validate_and_extract_dependency_settings(self, target_settings_dict: Dict[str, Any]):
        """
        Validates all dependency selections and extracts their settings.

        This method:
        1. Checks if function_dict is available
        2. Gets selected dependencies from comboboxes
        3. Validates each dependency selection
        4. Calls parse_settings_widget for each valid dependency
        5. Updates target_settings_dict with dependency names and settings

        Args:
            target_settings_dict: Dictionary to update with dependency information

        Returns:
            Tuple[int, dict]: (status, dependency_settings)
        """
        if not self._function_dict:
            return (PyIVLSReturnCode.MISSING_DEPENDENCY.value, f"Missing functions in {self.plugin_name} plugin. Check log")

        # Get selected dependencies from GUI
        selected_deps = self.get_selected_dependency_plugins()
        dependency_settings = {}

        # Validate and extract settings for each dependency type
        for dependency_type in self.dependencies.keys():
            if dependency_type not in selected_deps or not selected_deps[dependency_type]:
                return (PyIVLSReturnCode.MISSING_DEPENDENCY.value, f"No {dependency_type} plugin selected")

            selected_plugin = selected_deps[dependency_type]

            # Selection existence check. Method-level validation is already guaranteed by pruned function_dict.
            if dependency_type not in self._function_dict:
                return (PyIVLSReturnCode.MISSING_DEPENDENCY.value, f"No {dependency_type} plugins available")

            if selected_plugin not in self._function_dict[dependency_type]:
                return (PyIVLSReturnCode.MISSING_DEPENDENCY.value, f"{dependency_type} plugin '{selected_plugin}' not available")

            # Update target settings with selected plugin name
            target_settings_dict[dependency_type] = selected_plugin

            # Extract settings from the dependency plugin
            try:
                status, state = self._function_dict[dependency_type][selected_plugin]["parse_settings_widget"]()
                if status:
                    return (status, state)  # propagate error from dependency
                else:
                    settings = state

                # Store settings with a standardized key
                settings_key = f"{dependency_type}_settings"
                dependency_settings[settings_key] = settings

            except KeyError as e:
                return (PyIVLSReturnCode.DEPENDENCY_ERROR.value, f"Required function 'parse_settings_widget' not found in {dependency_type} plugin '{selected_plugin}': {str(e)}")
            except Exception as e:
                return (PyIVLSReturnCode.DEPENDENCY_ERROR.value, f"Error calling parse_settings_widget for {dependency_type} plugin '{selected_plugin}': {str(e)}")
        # combine the target settings dict with the dependency settings to return to the plugin.
        target_settings_dict.update(dependency_settings)
        return (0, target_settings_dict)


class LoggingHelper(QObject):
    """Helper class for standard logging functionality. pass "self" to the helper on plugin init
    Logging levels:
    DEBUG: Detailed information, typically only of interest to a developer trying to diagnose a problem.
    INFO: Confirmation that things are working as expected.
    WARN: An indication that something unexpected happened, or indicative of some problem in the near future (e.g., 'disk space low'). The software is still working as expected.
    ERROR: Due to a more serious problem, the software has not been able to perform some function.
    """

    logger_signal = pyqtSignal(str)
    info_popup_signal = pyqtSignal(str)

    def __init__(self, plugin_instance):
        self.plugin_name = plugin_instance.__class__.__name__
        super().__init__()

    def log_info(self, message: str) -> None:
        """Log informational messages with INFO flag
        INFO: Confirmation that things are working as expected.
        """
        log = f"{self.plugin_name} : INFO : {message}"
        self.logger_signal.emit(log)

    def log_debug(self, message: str) -> None:
        """Log debug messages with DEBUG flag
        DEBUG: Detailed information, typically only of interest to a developer trying to diagnose a problem.
        """
        log = f"{self.plugin_name} : DEBUG : {message}"
        self.logger_signal.emit(log)

    def log_warn(self, message: str) -> None:
        """Log warning messages with WARN flag
        WARN: An indication that something unexpected happened, or indicative of some problem in the near future (e.g., 'disk space low'). The software is still working as expected.
        """
        log = f"{self.plugin_name} : WARN : {message}"
        self.logger_signal.emit(log)

    def log_error(self, message: str, include_trace: bool = True) -> None:
        """Log error messages with ERROR flag.
        ERROR: Due to a more serious problem, the software has not been able to perform some function.
        """
        log = f"{self.plugin_name} : ERROR : {message}"

        if include_trace:
            # Get current exception traceback (if inside except block)
            exc_type, exc_value, exc_tb = sys.exc_info()
            if exc_type is not None:
                trace = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
                log += f"\n{trace}"
            else:
                # Outside of exception block — include current stack
                stack = "".join(traceback.format_stack()[:-1])  # remove the current function call
                log += f"\nStack trace:\n{stack}"

        self.logger_signal.emit(log)

    def info_popup(self, message: str) -> None:
        """show info popup, if provided"""
        message = f"{self.plugin_name}: {message}"
        self.info_popup_signal.emit(message)
