import os
import copy
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QComboBox, QGroupBox, QSpinBox, QLabel, QPushButton
from plugins.plugin_components import public, ConnectionIndicatorStyle, get_public_methods, LoggingHelper, GuiMapper, DependencyManager, PyIVLSReturn


class verifyContactGUI():
    green_style = ConnectionIndicatorStyle.GREEN_CONNECTED.value
    red_style = ConnectionIndicatorStyle.RED_DISCONNECTED.value

    def __init__(self):
        self.path = os.path.dirname(__file__) + os.path.sep
        
        # Initialize LoggingHelper first
        self.logger = LoggingHelper(self)
        
        # Load UI
        self.settingsWidget = uic.loadUi(self.path + "verifyContact_Settings.ui")  # type: ignore
        
        # Initialize functionality
        

        # Initialize DependencyManager
        dependencies = {"contactingMove": []}
        dependency_mapper = {"contactingMove": "touchDetBox"}
        self.dm = DependencyManager("verifyContact", dependencies, self.settingsWidget, dependency_mapper)


        # Internal settings storage
        self.current_settings = {}


    ########Functions
    ########GUI Slots

    ########Functions
    ################################### internal

    def _getPublicFunctions(self, function_dict: dict):
        """Public function callback for dependency injection.
        
        Args:
            function_dict: Dictionary of plugin functions
        """
        # Set function dict in dependency manager (this automatically updates dependency comboboxes)
        self.dm.function_dict = function_dict
        
        # Trigger initial update of manipulator channel comboboxes
        self._on_smu_dependency_changed()

    def _on_smu_dependency_changed(self):
        """Called when SMU dependency selection changes - update manipulator channel comboboxes."""
        self.logger.log_debug("SMU dependency changed, updating manipulator channel comboboxes")
        
        # Get selected SMU plugin
        selected_deps = self.dm.get_selected_dependencies()
        smu_plugin = selected_deps.get("smu")
        
        if smu_plugin and "smu" in self.dm.function_dict:
            try:
                # The structure is nested: plugin_type -> plugin_name -> functions
                if smu_plugin in self.dm.function_dict["smu"]:
                    smu_functions = self.dm.function_dict["smu"][smu_plugin]
                    
                    # Fetch channels from the selected SMU plugin
                    smu_channels = smu_functions["smu_channelNames"]()
                    self.logger.log_debug(f"SMU channels fetched for {smu_plugin}: {smu_channels}")
                else:
                    self.logger.log_warn(f"Plugin {smu_plugin} not found in SMU functions")
                    return
                    
                # Store the channels for later use
                self.channel_names = smu_channels
                self.smu_channels = smu_channels + ["none", "spectrometer"]
                
                # Update all manipulator SMU channel comboboxes
                self._update_manipulator_comboboxes()
                
            except Exception as e:
                self.logger.log_error(f"Error fetching SMU channels: {str(e)}")
        else:
            self.logger.log_debug("No SMU plugin selected or functions not available")
            self.logger.log_debug("No SMU plugin selected or functions not available")

    def _update_manipulator_comboboxes(self):
        """Update manipulator comboboxes with available channels."""
        # Update all SMU channel dropdowns with available channels from SMU plugin
        for i in range(1, 5):
            smu_combo = getattr(self.settingsWidget, f"mansmu_{i}")
            smu_combo.clear()
            # Use the channels we got from the SMU plugin if available
            if hasattr(self, 'channel_names') and self.channel_names:
                smu_channels = self.channel_names + ["none", "spectrometer"]
                smu_combo.addItems(smu_channels)
            else:
                smu_combo.addItems(self.smu_channels)

            # Update contacting channel dropdowns (these are static)
            con_combo = getattr(self.settingsWidget, f"mancon_{i}")
            con_combo.clear()
            con_combo.addItems(self.con_channels)

    def _create_manipulator_info(self, manipulator_num: int) -> ManipulatorInfo:
        """Create ManipulatorInfo object from current GUI settings for a specific manipulator."""
        status, settings = self.gm.get_values(self.field_mapping)

        
        return ManipulatorInfo(
            mm_number=manipulator_num,
            smu_channel=settings.get(f"{manipulator_num}_smu", "none"),  # type: ignore
            condet_channel=settings.get(f"{manipulator_num}_con", "none"),  # type: ignore
            threshold=settings.get(f"{manipulator_num}_res", 10),  # type: ignore
            stride=10,  # Default value since not in UI
            sample_width=1,  # Default value since not in UI  
            spectrometer_height=0,  # Default value since not in UI
            function="verify_contact"
        )

    def _fetch_dep_plugins(self):
        """Returns the micromanipulator, smu and contacting function dictionaries wrapped as objects.

        Returns:
            tuple[mm, smu, con]: micromanipulator, smu and con objects with methods.
        Raises:
            AssertionError: if any of the plugins is not found.
        """
        # Get selected dependencies from DependencyManager
        selected_deps = self.dm.get_selected_dependencies()
        
        smu_name = selected_deps.get("smu")
        contacting_name = selected_deps.get("contact detection")
        
        assert smu_name, "verifyContact: No SMU plugin selected"
        assert contacting_name, "verifyContact: No contact detection plugin selected"
        
        # Get function dictionaries directly
        function_dict = self.dm.function_dict
        
        assert "smu" in function_dict, "verifyContact: SMU functions not available"
        assert "contact detection" in function_dict, "verifyContact: contact detection functions not available"
        
        smu_functions = function_dict["smu"]
        contacting_functions = function_dict["contact detection"]
        
        # Create simple wrapper objects that expose functions as methods
        class FunctionWrapper:
            def __init__(self, functions):
                for name, func in functions.items():
                    setattr(self, name, func)
        
        smu_obj = FunctionWrapper(smu_functions)
        contacting_obj = FunctionWrapper(contacting_functions)
        
        # Return placeholder for micromanipulator (not used in verify contact)
        placeholder = {}
        return placeholder, smu_obj, contacting_obj

    ########Functions
    ########GUI changes

    def update_status(self):
        """
        Updates the status of the smu and contacting plugins.
        This function is called when the status changes.
        """
        self.logger.log_debug("Updating plugin status")
        
        # Validate dependencies first
        is_valid, missing = self.dm.validate_dependencies()
        if not is_valid:
            self.logger.log_warn(f"Missing dependencies: {missing}")
            return
            
        mm, smu, con = self._fetch_dep_plugins()
        
        # Test SMU connection and get channels
        try:
            self.channel_names = smu.smu_channelNames()  # type: ignore
            if self.channel_names is not None:
                self.smu_indicator.setStyleSheet(self.green_style)
                self.logger.log_debug(f"SMU channels available: {self.channel_names}")
            else:
                self.smu_indicator.setStyleSheet(self.red_style)
                self.logger.log_warn("SMU channels not available")
                return
        except Exception as e:
            self.smu_indicator.setStyleSheet(self.red_style)
            self.logger.log_error(f"Error getting SMU channels: {str(e)}")
            return

        self.smu_channels = self.channel_names + ["none", "spectrometer"]

        # Update manipulator comboboxes with available channels
        self._update_manipulator_comboboxes()

        # Test contact detection connection
        try:
            con_status, con_state = con.deviceConnect()  # type: ignore
            if con_status == 0:
                self.con_indicator.setStyleSheet(self.green_style)
                self.logger.log_info("Contact detection device connected successfully")
                con_status, con_state = con.deviceDisconnect()  # type: ignore
            else:
                self.con_indicator.setStyleSheet(self.red_style)
                self.logger.log_error(f"Contact detection connection failed: {con_state}")
        except Exception as e:
            self.con_indicator.setStyleSheet(self.red_style)
            self.logger.log_error(f"Error testing contact detection: {str(e)}")

    def dependencies_changed(self):
        """Called when dependencies change - update comboboxes via DependencyManager."""
        self.logger.log_debug("Dependencies changed, updating dependency combo boxes")
        self.dm.update_comboboxes()
        self.logger.log_info("Plugin dependencies updated successfully")

    ########Functions
    ########plugins interraction

    def _getLogSignal(self):
        return self.logger.logger_signal

    def _getInfoSignal(self):
        return self.logger.info_popup_signal

    def _get_public_methods(self) -> dict:
        """
        Returns a nested dictionary of public methods for the plugin
        """
        return get_public_methods(self)
        
    def _set_function_dict(self, function_dict: dict):
        """Set the function dictionary from the plugin system and update dependencies."""
        self.dm.set_function_dict(function_dict)
        # This will automatically trigger combobox updates via the DependencyManager
        
    def _get_dependencies(self) -> dict:
        """Return the dependencies required by this plugin."""
        return self.dm.dependencies

    def setup(self, settings) -> QWidget:
        """
        Sets up the GUI for the plugin. This function is called by hook to initialize the GUI.
        """
        # Set settings using the new approach
        self.setSettings(settings)
        
        # Update comboboxes if channels are available
        # Update comboboxes after getting channels
        self._update_manipulator_comboboxes()

        return self.settingsWidget  # type: ignore

    @public
    def parse_settings_widget(self):
        """Parse current GUI settings into dictionary format using GuiMapper.
        
        Returns:
            tuple: (status_code, settings_dict) where status_code 0 = success, 1 = failure
        """
        self.logger.log_debug("Parsing settings widget for verifyContact plugin")
        
        # Get values using GuiMapper  
        status, result = self.gm.get_values(self.field_mapping)
        settings = result  # type: ignore
            
        if not settings:
            return (1, {"Error message": "Failed to parse settings from GUI"})

        # Create list of configured manipulators for validation
        configured_manipulators = []
        for i in range(1, 5):
            smu_channel = settings.get(f"{i}_smu", "none") if hasattr(settings, 'get') else settings[f"{i}_smu"] if f"{i}_smu" in settings else "none"  # type: ignore
            con_channel = settings.get(f"{i}_con", "none") if hasattr(settings, 'get') else settings[f"{i}_con"] if f"{i}_con" in settings else "none"  # type: ignore
            threshold = settings.get(f"{i}_res", 10) if hasattr(settings, 'get') else settings[f"{i}_res"] if f"{i}_res" in settings else 10  # type: ignore
            
            # Check if manipulator is configured (has non-none channels)
            if smu_channel != "none" or con_channel != "none":
                manipulator_info = self._create_manipulator_info(i)
                
                # Validate the manipulator
                errors = manipulator_info.validate()
                if errors:
                    error_msg = f"Validation errors in manipulator {i}: {errors}"
                    self.logger.log_warn(error_msg)
                    return (1, {"Error message": error_msg})
                
                configured_manipulators.append(manipulator_info)

        # Validate unique contact detection channels
        con_channels = [m.condet_channel for m in configured_manipulators if m.condet_channel != "none"]
        if len(con_channels) != len(set(con_channels)):
            return (1, {"Error message": "Contact detection channels must be unique across manipulators."})
        
        # Store current settings internally
        self.current_settings = settings.copy()  # type: ignore
        
        return (0, settings)

    @public
    def setSettings(self, settings: dict):
        """Set settings using GuiMapper."""
        self.logger.log_debug("Setting settings for verifyContact plugin: " + str(settings))

        # Deep copy to avoid modifying original data
        settings_to_parse = copy.deepcopy(settings)
        
        # Store settings internally
        self.current_settings = settings_to_parse.copy()
        
        # Update dependency selections if present
        if "smu" in settings_to_parse:
            smu_box = getattr(self.settingsWidget, "smuBox", None)
            if smu_box:
                index = smu_box.findText(settings_to_parse["smu"])
                if index >= 0:
                    smu_box.setCurrentIndex(index)
                    
        if "contact detection" in settings_to_parse:
            condet_box = getattr(self.settingsWidget, "condetBox", None)  
            if condet_box:
                index = condet_box.findText(settings_to_parse["contact detection"])
                if index >= 0:
                    condet_box.setCurrentIndex(index)
        
        # Update GUI using GuiMapper  
        self.gm.schedule_gui_update(settings_to_parse, self.field_mapping, {})

    @public 
    def set_gui_from_settings(self) -> tuple[int, dict]:
        """
        Updates the GUI controls based on the internal settings.
        This method should be called after setSettings to refresh the GUI.

        Returns:
            tuple[int, dict]: (status, result) - status 0 for success
        """
        try:
            # Update manipulator GUI elements
            self._update_manipulator_comboboxes()
            
            return (0, {"message": "GUI updated successfully"})
        except Exception as e:
            error_msg = f"Error updating GUI from settings: {str(e)}"
            self.logger.log_error(error_msg)
            return (1, {"Error message": error_msg})

    ########Functions to be used externally
    def verify(self) -> tuple[int, dict]:
        self.logger.log_info("Starting VerifyContact verification")
        mm, smu, con = self._fetch_dep_plugins()
        
        # Parse settings from GUI to get current values
        status, settings = self.parse_settings_widget()
        if status != 0:
            return (status, settings)  # type: ignore

        # Create ManipulatorInfo objects for configured manipulators
        configured_manipulators = []
        for i in range(1, 5):
            manipulator_info = self._create_manipulator_info(i)
            if manipulator_info.is_configured():
                configured_manipulators.append(manipulator_info)

        if not configured_manipulators:
            error_msg = "No configured manipulators found"
            self.logger.log_warn(error_msg)
            return (1, {"Error message": error_msg})

        # Execute contact verification for all configured manipulators
        status = self.functionality.check_all_contacting(smu, con, configured_manipulators)

        if status is False:
            self.logger.log_warn(f"verifyContact sequence step failed")
            return (4, {"Error_message": "no contact after sweep"})
        self.logger.log_debug("VerifyContact OK")
        return (0, {"message": "VerifyContact OK"})

    @public
    def sequenceStep(self, postfix: str) -> tuple[int, dict]:
        self.logger.log_info(f"Starting VerifyContact sequence step with postfix: {postfix}")
        mm, smu, con = self._fetch_dep_plugins()

        # Create ManipulatorInfo objects for configured manipulators
        configured_manipulators = []
        for i in range(1, 5):
            manipulator_info = self._create_manipulator_info(i)
            if manipulator_info.is_configured():
                configured_manipulators.append(manipulator_info)

        if not configured_manipulators:
            error_msg = "No configured manipulators found"
            self.logger.log_warn(error_msg)
            return (1, {"Error message": error_msg})

        # Execute contact verification for all configured manipulators
        status = self.functionality.check_all_contacting(smu, con, configured_manipulators)

        if status is False:
            self.logger.log_warn(f"verifyContact sequence step failed")
            return (4, {"Error_message": "no contact after sweep"})

        self.logger.log_info("verifyContact sequence step completed successfully")
        return (0, {"message": "verifyContact sequence step completed successfully", "safety_check": "passed"})
