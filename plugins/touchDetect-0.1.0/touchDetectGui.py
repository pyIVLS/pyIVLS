import os
import copy
from touchDetect import touchDetect, ManipulatorInfo
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QComboBox, QGroupBox, QSpinBox
from plugins.plugin_components import public, ConnectionIndicatorStyle, get_public_methods, LoggingHelper
from components.worker_thread import WorkerThread
import time


class touchDetectGUI(QObject):
    non_public_methods = []
    public_methods = ["move_to_contact", "parse_settings_widget", "sequenceStep", "setSettings", "set_gui_from_settings", "_check_saved_positions", "clear_saved_positions"]
    green_style = ConnectionIndicatorStyle.GREEN_CONNECTED.value
    red_style = ConnectionIndicatorStyle.RED_DISCONNECTED.value

    ########Signals
    # Keep the original signals for backward compatibility
    # but they will now be connected to LoggingHelper's signals
    log_message = pyqtSignal(str)
    info_message = pyqtSignal(str)

    def emit_log(self, status: int, state: dict) -> None:
        """
        Emits a standardized log message for status dicts or error lists.
        Args:
            status (int): status code, 0 for success, non-zero for error.
            state (dict): dictionary in the standard pyIVLS format

        """
        msg = state.get("Error message", "Unknown error")
        exception = state.get("Exception", "Not provided")

        if status == 0:
            self.logger.log_info(f"{msg} : Exception: {exception}")
        else:
            self.logger.log_warn(f"{msg} : Exception: {exception}")

    @property
    def dependency(self):
        return self._dependencies

    @dependency.setter
    def dependency(self, value):
        if isinstance(value, list):
            self._dependencies = value
            self.dependencies_changed()
        else:
            raise TypeError("touchDetectGUI : dependencies must be a list")

    ########Functions
    def __init__(self):
        super().__init__()
        self.path = os.path.dirname(__file__) + os.path.sep
        # depenenies are in format plugin: object, metadata: dict.
        self._dependencies = [None, None]

        # Initialize LoggingHelper
        self.logger = LoggingHelper(self)

        # Connect LoggingHelper signals to the existing signals for backward compatibility
        self.logger.logger_signal.connect(self.log_message.emit)
        self.logger.info_popup_signal.connect(self.info_message.emit)

        self.functionality = touchDetect(log=self.logger.log_debug)

        self.settingsWidget = uic.loadUi(self.path + "touchDetect_Settings.ui")

        # Initialize the combo boxes for dependencies
        self.smu_box: QComboBox = self.settingsWidget.smuBox
        self.micromanipulator_box: QComboBox = self.settingsWidget.micromanipulatorBox
        self.condet_box: QComboBox = self.settingsWidget.condetBox

        # find status labels and indicators
        self.smu_indicator = self.settingsWidget.smuIndicator
        self.mm_indicator = self.settingsWidget.mmIndicator
        self.con_indicator = self.settingsWidget.conIndicator

        # find manipulator boxes
        man1: QGroupBox = self.settingsWidget.manipulator1
        man2: QGroupBox = self.settingsWidget.manipulator2
        man3: QGroupBox = self.settingsWidget.manipulator3
        man4: QGroupBox = self.settingsWidget.manipulator4

        # find comboboxes in manipulator boxes
        man1_smu_box: QComboBox = man1.findChild(QComboBox, "mansmu_1")
        man1_con_box: QComboBox = man1.findChild(QComboBox, "mancon_1")
        man2_smu_box: QComboBox = man2.findChild(QComboBox, "mansmu_2")
        man2_con_box: QComboBox = man2.findChild(QComboBox, "mancon_2")
        man3_smu_box: QComboBox = man3.findChild(QComboBox, "mansmu_3")
        man3_con_box: QComboBox = man3.findChild(QComboBox, "mancon_3")
        man4_smu_box: QComboBox = man4.findChild(QComboBox, "mansmu_4")
        man4_con_box: QComboBox = man4.findChild(QComboBox, "mancon_4")

        # find spinboxes
        man1_res: QSpinBox = man1.findChild(QSpinBox, "manres_1")
        man2_res: QSpinBox = man2.findChild(QSpinBox, "manres_2")
        man3_res: QSpinBox = man3.findChild(QSpinBox, "manres_3")
        man4_res: QSpinBox = man4.findChild(QSpinBox, "manres_4")

        self.manipulator_boxes = [[man1, man1_smu_box, man1_con_box, man1_res], [man2, man2_smu_box, man2_con_box, man2_res], [man3, man3_smu_box, man3_con_box, man3_res], [man4, man4_smu_box, man4_con_box, man4_res]]
        for box, smu_box, con_box, res_spin in self.manipulator_boxes:
            assert box is not None, f"Manipulator box {box} is None"
            assert smu_box is not None, f"SMU box {box.title()} is None"
            assert con_box is not None, f"Con box {box.title()} is None"
            assert res_spin is not None, f"Res spin {box.title()} is None"
        self.settings = [{}, {}, {}, {}]

        # Internal settings storage for separation of concerns
        self._internal_stride = ""
        self._internal_sample_width = ""
        self._internal_spectro_height = ""

        # Thread management for monitoring
        self.monitoring_thread = None
        self.is_monitoring = False

        # line edits
        self.stride = self.settingsWidget.stride
        self.sample_width = self.settingsWidget.sample_width
        self.spectro_height = self.settingsWidget.spectro_height

    ########Functions
    ########GUI Slots

    ########Functions
    ################################### internal

    def _fetch_dep_plugins(self):
        """returns the micromanipulator, smu and contacting plugins based on the current selection in the combo boxes.

        Returns:
            tuple[mm, smu, con]: micromanipulator, smu and con plugins.
        Raises:
            AssertionError: if any of the plugins is not found.
        """

        micromanipulator = None
        smu = None
        condet = None
        for plugin, metadata in self.dependency:
            if metadata.get("function") == "micromanipulator":
                current_text = self.micromanipulator_box.currentText()
                if current_text == metadata.get("name"):
                    micromanipulator = plugin
            elif metadata.get("function") == "smu":
                if self.smu_box.currentText() == metadata.get("name"):
                    smu = plugin
            elif metadata.get("function") == "contacting":
                if self.condet_box.currentText() == metadata.get("name"):
                    condet = plugin

        assert micromanipulator is not None, "touchDetect: micromanipulator plugin is None"
        assert smu is not None, "touchDetect: smu plugin is None"
        assert condet is not None, "touchDetect: contacting plugin is None"

        return micromanipulator, smu, condet

    ########Functions
    ########GUI changes

    def update_status(self):
        """
        Updates the status of the mm, smu and contacting plugins.
        This function is called when the status changes.
        """
        self.logger.log_debug("Updating plugin status")
        mm, smu, con = self._fetch_dep_plugins()
        self.channel_names = smu.smu_channelNames()
        if self.channel_names is not None:
            self.smu_indicator.setStyleSheet(self.green_style)
            self.logger.log_debug(f"SMU channels available: {self.channel_names}")
        status, state = mm.mm_devices()

        if status == 0:
            self.mm_indicator.setStyleSheet(self.green_style)
            self.logger.log_info(f"Micromanipulator devices detected: {state}")
            num_dev, active_list = state
            for i, status in enumerate(active_list):
                if status:
                    box, smu_box, con_box, res_spin = self.manipulator_boxes[i]
                    self.logger.log_info(f"Micromanipulator {i + 1} is active. Box: {box}, SMU Box: {smu_box}, Con Box: {con_box}, Res Spin: {res_spin}")
                    box.setVisible(True)
                    self.logger.log_info(f"Set {box} visible for manipulator {i + 1}")
                    smu_box.clear()
                    con_box.clear()
                    smu_box.addItems(self.channel_names)
                    con_box.addItems(["Hi", "Lo"])
                    # add options none and spectrometer
                    con_box.addItems(["none", "spectrometer"])
                    smu_box.addItems(["none", "spectrometer"])

                    settings = self.settings[i]
                    if "channel_smu" in settings:
                        smu_box.setCurrentText(settings["channel_smu"])
                    if "channel_con" in settings:
                        con_box.setCurrentText(settings["channel_con"])
                    if "res_threshold" in settings:
                        res_spin.setValue(int(settings["res_threshold"]))
        else:
            self.emit_log(status, state)
        con_status, con_state = con.deviceConnect()
        if con_status == 0:
            self.con_indicator.setStyleSheet(self.green_style)
            self.logger.log_info("Contact detection device connected successfully")
            con_status, con_state = con.deviceDisconnect()
        else:
            self.emit_log(con_status, con_state)

    def dependencies_changed(self):
        self.logger.log_debug("Dependencies changed, updating combo boxes")
        self.smu_box.clear()
        self.micromanipulator_box.clear()
        self.condet_box.clear()

        for plugin, metadata in self.dependency:
            if metadata.get("function") == "micromanipulator":
                self.micromanipulator_box.addItem(metadata.get("name"))
            elif metadata.get("function") == "smu":
                self.smu_box.addItem(metadata.get("name"))
            elif metadata.get("function") == "contacting":
                self.condet_box.addItem(metadata.get("name"))
        self.micromanipulator_box.setCurrentIndex(0)
        self.smu_box.setCurrentIndex(0)
        self.condet_box.setCurrentIndex(0)
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
        methods = {method: getattr(self, method) for method in dir(self) if callable(getattr(self, method)) and not method.startswith("__") and not method.startswith("_") and method not in self.non_public_methods and method in self.public_methods}
        return methods

    def _parse_ini(self, settings: dict):
        temp = [{}, {}, {}, {}]
        for key, value in settings.items():
            try:
                # split at "_"
                number, func = key.split("_")
                number = int(number)
                if func == "smu":
                    temp[number - 1]["channel_smu"] = value
                elif func == "con":
                    temp[number - 1]["channel_con"] = value
                elif func == "res":
                    # Convert to appropriate type
                    if isinstance(value, str) and value.strip():
                        temp[number - 1]["res_threshold"] = float(value)
                    elif isinstance(value, (int, float)):
                        temp[number - 1]["res_threshold"] = float(value)
            except (ValueError, TypeError):
                # this is here to make sure that only _1, _2, etc. are parsed for manipulator settings
                # and to handle invalid values gracefully
                continue

        stride = settings.get("stride", "")
        sample_width = settings.get("sample_width", "")
        spectro_height = settings.get("spectro_height", "")

        # Convert stride, sample_width, and spectro_height to strings if they're not already
        if isinstance(stride, (int, float)):
            stride = str(stride)
        if isinstance(sample_width, (int, float)):
            sample_width = str(sample_width)
        if isinstance(spectro_height, (int, float)):
            spectro_height = str(spectro_height)

        return temp, stride, sample_width, spectro_height

    def setup(self, settings) -> QWidget:
        """
        Sets up the GUI for the plugin. This function is called by hook to initialize the GUI.
        """

        for box, _, _, _ in self.manipulator_boxes:
            box.setVisible(False)

        # Parse and store settings internally
        self.settings, stride, sample_width, spectro_height = self._parse_ini(settings)
        self._internal_stride = stride
        self._internal_sample_width = sample_width
        self._internal_spectro_height = spectro_height

        # Apply settings to GUI
        self.stride.setValue(int(stride) if stride else 10)
        self.sample_width.setValue(int(sample_width) if sample_width else 1)
        self.spectro_height.setValue(int(spectro_height) if spectro_height else 0)

        # Set initial button text
        self.settingsWidget.pushButton_2.setText("Start Monitoring")

        self.settingsWidget.initButton.clicked.connect(self.update_status)
        self.settingsWidget.pushButton.clicked.connect(self._test)
        self.settingsWidget.pushButton_2.clicked.connect(self._monitor_threaded)
        return self.settingsWidget

    def _monitor_worker(self, worker_thread):
        """
        Worker function that runs the monitoring in a separate thread.
        This function now uses the touchDetect.monitor_manual_contact_detection method.

        Args:
            worker_thread: The WorkerThread instance for communication and stop checking
        """
        try:
            mm, smu, con = self._fetch_dep_plugins()

            # Get configured manipulators and convert to ManipulatorInfo objects
            status, settings = self.parse_settings_widget()
            if status != 0:
                worker_thread.error.emit(f"Settings parsing failed: {settings}")
                return (status, settings)

            # Create ManipulatorInfo objects from the settings
            manipulator_infos = []
            validation_errors = []

            for i, (box, smu_box, con_box, res_box) in enumerate(self.manipulator_boxes):
                manipulator_name = i + 1
                smu_channel = smu_box.currentText()
                con_channel = con_box.currentText()
                threshold = int(res_box.value())
                stride = settings["stride"]
                sample_width = settings["sample_width"]
                spectro_height = settings["spectro_height"]

                # Create ManipulatorInfo object and let it handle all validation
                manipulator_info = ManipulatorInfo(
                    mm_number=manipulator_name,
                    smu_channel=smu_channel,
                    condet_channel=con_channel,
                    threshold=threshold,
                    stride=stride,
                    sample_width=sample_width,
                    spectrometer_height=spectro_height,
                )

                # Use ManipulatorInfo's built-in validation
                errors = manipulator_info.validate()
                if errors:
                    validation_errors.extend([f"Manipulator {manipulator_name}: {error}" for error in errors])
                    continue

                # Only add configured manipulators
                if manipulator_info.is_configured():
                    manipulator_infos.append(manipulator_info)

            # Report validation errors if any
            if validation_errors:
                error_msg = "; ".join(validation_errors)
                worker_thread.error.emit(f"Validation errors: {error_msg}")
                return (1, {"Error message": f"Validation errors: {error_msg}"})

            if not manipulator_infos:
                worker_thread.error.emit("No configured manipulators found")
                return (1, {"Error message": "No configured manipulators found"})

            # Define callbacks for the monitoring
            def progress_callback(message):
                worker_thread.progress.emit(message)

            def error_callback(message):
                worker_thread.error.emit(message)

            def stop_requested_callback():
                return worker_thread.is_stop_requested()

            # Use the touchDetect monitor_manual_contact_detection method
            status, result = self.functionality.monitor_manual_contact_detection(mm=mm, smu=smu, con=con, manipulator_infos=manipulator_infos, progress_callback=progress_callback, error_callback=error_callback, stop_requested_callback=stop_requested_callback)

            # Update the functionality.last_z with the saved positions from ManipulatorInfo objects
            for info in manipulator_infos:
                if info.last_z is not None:
                    self.functionality.last_z[info.mm_number] = info.last_z

            return (status, result)

        except Exception as e:
            error_msg = f"Exception during monitoring: {str(e)}"
            worker_thread.error.emit(error_msg)
            return (2, {"Error message": error_msg, "Exception": str(e)})

    def _monitor_threaded(self):
        """
        Starts or stops the monitoring process in a separate thread.
        This keeps the GUI responsive during monitoring.
        """
        if not self.is_monitoring:
            # Start monitoring
            self.logger.log_info("Starting threaded resistance monitoring for all manipulators")
            self.is_monitoring = True

            # Update button text to show stop option
            self.settingsWidget.pushButton_2.setText("Stop Monitoring")

            # Create and start the worker thread
            self.monitoring_thread = WorkerThread(self._monitor_worker)

            # Connect thread signals
            self.monitoring_thread.progress.connect(self._on_monitoring_progress)
            self.monitoring_thread.error.connect(self._on_monitoring_error)
            self.monitoring_thread.finished.connect(self._on_monitoring_finished)
            self.monitoring_thread.result.connect(self._on_monitoring_result)

            # Start the thread
            self.monitoring_thread.start()

        else:
            # Stop monitoring
            self.logger.log_info("Stopping monitoring thread")
            if self.monitoring_thread:
                self.monitoring_thread.stop()
                # Don't wait here as it would block the GUI
                # The finished signal will handle cleanup

    def _on_monitoring_progress(self, message):
        """Handle progress updates from the monitoring thread."""
        self.logger.log_info(message)

    def _on_monitoring_error(self, error_message):
        """Handle error messages from the monitoring thread."""
        self.logger.log_warn(error_message)

    def _on_monitoring_result(self, result):
        """Handle the final result from the monitoring thread."""
        status, state = result
        if status != 0:
            self.emit_log(status, state)

    def _on_monitoring_finished(self):
        """Handle monitoring thread completion."""
        self.is_monitoring = False
        self.monitoring_thread = None
        self.settingsWidget.pushButton_2.setText("Start Monitoring")
        self.logger.log_info("Monitoring thread finished")

    def _test(self):
        self.logger.log_info("Testing move to contact functionality")

        # First check if we have saved positions for all configured manipulators
        status, result = self._check_saved_positions()
        if status != 0:
            error_msg = f"Cannot test: {result.get('Error message', 'Unknown error')}"
            self.logger.log_warn(f"TEST FAILED: {error_msg}")
            self.emit_log(status, {"Error message": error_msg})
            return

        # Proceed with the test
        status, state = self.move_to_contact()
        if status == 0:
            self.logger.log_info("Move to contact test completed successfully")
        else:
            self.logger.log_warn(f"Move to contact test failed: {state.get('Error message', 'Unknown error')}")
        self.emit_log(status, state)

    def parse_settings_widget(self) -> tuple[int, dict]:
        """
        Parses the settings widget and returns error code and settings as a dictionary matching .ini keys.
        """
        settings = {}
        # Collect manipulator settings
        for i, (box, smu_box, con_box, res_box) in enumerate(self.manipulator_boxes):
            smu_channel = smu_box.currentText()
            con_channel = con_box.currentText()
            res_value = res_box.value()
            # Only add if either is non-empty
            if smu_channel or con_channel:
                settings[f"{i + 1}_smu"] = smu_channel
                settings[f"{i + 1}_con"] = con_channel
                settings[f"{i + 1}_res"] = res_value

        # Check that the same con channel does not appear twice (excluding empty)
        con_channels = [settings[f"{i + 1}_con"] for i in range(4) if f"{i + 1}_con" in settings and settings[f"{i + 1}_con"]]
        if len(con_channels) != len(set(con_channels)):
            return (1, {"Error message": "Contact detection channels must be unique across manipulators."})

        # Get values from QSpinBox controls (no validation needed as spinboxes have proper limits)
        stride = self.stride.value()
        sample_width = self.sample_width.value()
        spectro_height = self.spectro_height.value()

        settings["stride"] = stride
        settings["sample_width"] = sample_width
        settings["spectro_height"] = spectro_height

        self.logger.log_debug(str(settings))
        return (0, settings)

    @public
    def setSettings(self, settings: dict):
        """
        Sets the plugin settings from the sequence builder.
        This method only updates internal settings without modifying the GUI.

        Args:
            settings (dict): Settings dictionary with plugin configuration

        Returns:
            tuple[int, dict]: (status, settings) - status 0 for success, settings dict
        """

        """
        The settings dictionary is expected to have the following structure from parse_settings_widget:
        {
            "1_smu": "SMU1",
            "1_con": "Hi",
            "1_res": 150,
            "2_smu": "SMU2", 
            "2_con": "Lo",
            "2_res": 200,
            "stride": 10,
            "sample_width": 0.1,
            "spectro_height": 100
        }
        
        This method converts it to internal format and stores it.
        """
        self.logger.log_debug("Setting settings for touchDetect plugin: " + str(settings))

        # Deep copy to avoid modifying original data
        settings_to_parse = copy.deepcopy(settings)

        # Parse settings into the expected format and store internally
        self.settings, stride, sample_width, spectro_height = self._parse_ini(settings_to_parse)

        # Store the global settings internally
        self._internal_stride = stride
        self._internal_sample_width = sample_width
        self._internal_spectro_height = spectro_height

    @public
    def set_gui_from_settings(self) -> tuple[int, dict]:
        """
        Updates the GUI controls based on the internal settings.
        This method should be called after setSettings to refresh the GUI.

        Returns:
            tuple[int, dict]: (status, result) - status 0 for success
        """
        try:
            # Update stride, sample_width, and spectro_height QSpinBox controls
            if hasattr(self, "_internal_stride") and self._internal_stride:
                self.stride.setValue(int(self._internal_stride))
            if hasattr(self, "_internal_sample_width") and self._internal_sample_width:
                self.sample_width.setValue(int(self._internal_sample_width))
            if hasattr(self, "_internal_spectro_height") and self._internal_spectro_height:
                self.spectro_height.setValue(int(self._internal_spectro_height))

            # Update manipulator settings in GUI
            for i, (box, smu_box, con_box, res_spin) in enumerate(self.manipulator_boxes):
                if i < len(self.settings) and self.settings[i]:
                    settings_for_manipulator = self.settings[i]

                    # Set SMU channel if available
                    if "channel_smu" in settings_for_manipulator:
                        smu_channel = settings_for_manipulator["channel_smu"]
                        if smu_channel:  # Only set if not empty
                            # Find the item in the combobox
                            index = smu_box.findText(smu_channel)
                            if index >= 0:
                                smu_box.setCurrentIndex(index)
                            else:
                                # Add the item if it doesn't exist (this handles cases where dependencies aren't loaded yet)
                                smu_box.addItem(smu_channel)
                                smu_box.setCurrentText(smu_channel)

                    # Set contact detection channel if available
                    if "channel_con" in settings_for_manipulator:
                        con_channel = settings_for_manipulator["channel_con"]
                        if con_channel:  # Only set if not empty
                            index = con_box.findText(con_channel)
                            if index >= 0:
                                con_box.setCurrentIndex(index)
                            else:
                                # Add the item if it doesn't exist
                                con_box.addItem(con_channel)
                                con_box.setCurrentText(con_channel)

                    # Set resistance threshold if available - simple validation since QSpinBox handles limits
                    if "res_threshold" in settings_for_manipulator:
                        threshold_value = settings_for_manipulator["res_threshold"]
                        try:
                            threshold = int(threshold_value)
                            res_spin.setValue(threshold)
                        except (ValueError, TypeError):
                            self.logger.log_warn(f"Invalid resistance threshold for manipulator {i + 1}: {threshold_value} - not a valid number")

            self.logger.log_debug("GUI updated from internal settings successfully")
            return (0, {"message": "GUI updated from settings"})

        except Exception as e:
            error_msg = f"Error updating GUI from settings: {str(e)}"
            self.logger.log_warn(error_msg)
            return (1, {"Error message": error_msg, "Exception": str(e)})

    ########Functions to be used externally
    def move_to_contact(self):
        self.logger.log_info("Starting move to contact operation")

        # SAFETY CHECK: Ensure all configured manipulators have saved positions
        status, result = self._check_saved_positions()
        if status != 0:
            error_msg = f"Cannot move to contact: {result.get('Error message', 'Unknown error')}"
            self.logger.log_warn(f"SAFETY: {error_msg}")
            self.emit_log(status, {"Error message": error_msg})
            return (status, {"Error message": error_msg, "safety_check": "failed"})

        def create_manipulator_infos():
            # check settings
            self.logger.log_debug("Parsing settings for move to contact")
            status, settings = self.parse_settings_widget()
            if status == 0:
                # Create ManipulatorInfo objects from settings
                manipulator_infos = []
                validation_errors = []

                for i, (box, smu_box, con_box, res_box) in enumerate(self.manipulator_boxes):
                    manipulator_name = i + 1
                    smu_channel = smu_box.currentText()
                    con_channel = con_box.currentText()
                    threshold = int(res_box.value())
                    stride = settings.get("stride", 10)
                    sample_width = settings.get("sample_width", 0.1)
                    spectro_height = settings.get("spectro_height", 0)

                    # Get the last known position from functionality.last_z
                    last_z = self.functionality.last_z.get(manipulator_name, None)

                    # Create ManipulatorInfo object and let it handle all validation
                    manipulator_info = ManipulatorInfo(mm_number=manipulator_name, smu_channel=smu_channel, condet_channel=con_channel, threshold=threshold, stride=stride, sample_width=sample_width, last_z=last_z, spectrometer_height=spectro_height)

                    # Use ManipulatorInfo's built-in validation
                    errors = manipulator_info.validate()
                    if errors:
                        validation_errors.extend([f"Manipulator {manipulator_name}: {error}" for error in errors])
                        continue

                    # Only add configured manipulators
                    if manipulator_info.is_configured():
                        manipulator_infos.append(manipulator_info)

                # Report validation errors if any
                if validation_errors:
                    error_msg = "; ".join(validation_errors)
                    self.logger.log_warn(f"Validation errors: {error_msg}")
                    self.emit_log(1, {"Error message": f"Validation errors: {error_msg}"})
                    return []

                self.logger.log_debug(f"Created {len(manipulator_infos)} ManipulatorInfo objects")
                return manipulator_infos
            else:
                self.emit_log(status, settings)
                return []

        mm, smu, con = self._fetch_dep_plugins()
        manipulator_infos = create_manipulator_infos()  # will be empty if invalid

        status, state = self.functionality.move_to_contact(mm, con, smu, manipulator_infos)

        if status != 0:
            self.emit_log(status, state)
            return (status, state)
        self.logger.log_info("Move to contact operation completed successfully")
        return (status, state)

    @public
    def clear_saved_positions(self) -> tuple[int, dict]:
        """
        Clears all saved z-positions. Useful for resetting the plugin state.

        Returns:
            tuple[int, dict]: (0, message) for success
        """
        old_positions = dict(self.functionality.last_z)
        self.functionality.last_z.clear()
        self.logger.log_info(f"Cleared saved positions: {old_positions}")
        return (0, {"message": "Saved positions cleared", "cleared_positions": old_positions})

    def _check_saved_positions(self) -> tuple[int, dict]:
        """
        Checks if all configured manipulators have saved z-positions from previous monitoring.
        Uses ManipulatorInfo to determine which manipulators are configured.

        Returns:
            tuple[int, dict]: (status, result) - 0 for success with all positions saved,
                             1 for error with missing positions
        """
        status, settings = self.parse_settings_widget()
        if status != 0:
            return (status, settings)

        missing_positions = []
        configured_manipulators = []

        # Create ManipulatorInfo objects to determine which manipulators are configured
        for i, (box, smu_box, con_box, res_box) in enumerate(self.manipulator_boxes):
            manipulator_name = i + 1
            smu_channel = smu_box.currentText()
            con_channel = con_box.currentText()
            threshold = int(res_box.value())
            stride = settings.get("stride", 10)
            sample_width = settings.get("sample_width", 0.1)
            spectro_height = settings.get("spectro_height", 0)

            # Create ManipulatorInfo object to check if configured
            manipulator_info = ManipulatorInfo(
                mm_number=manipulator_name,
                smu_channel=smu_channel,
                condet_channel=con_channel,
                threshold=threshold,
                stride=stride,
                sample_width=sample_width,
                spectrometer_height=spectro_height,
            )

            # Only check configured manipulators (use ManipulatorInfo's built-in logic)
            if not manipulator_info.is_configured():
                continue

            configured_manipulators.append(manipulator_name)

            # Check if this manipulator has a saved position
            if manipulator_name not in self.functionality.last_z:
                missing_positions.append(manipulator_name)

        if missing_positions:
            error_msg = f"Missing saved positions for manipulators: {missing_positions}. Run manual monitoring first to establish baseline positions."
            self.logger.log_warn(error_msg)
            return (1, {"Error message": error_msg, "missing_positions": missing_positions, "configured_manipulators": configured_manipulators})

        self.logger.log_info(f"All configured manipulators ({configured_manipulators}) have saved positions: {self.functionality.last_z}")
        return (0, {"configured_manipulators": configured_manipulators, "saved_positions": dict(self.functionality.last_z)})

    @public
    def sequenceStep(self, postfix: str) -> tuple[int, dict]:
        """
        Performs the sequence step by moving all configured manipulators to contact.
        This function is called during sequence execution.

        SAFETY: This function will fail if any configured manipulator doesn't have
        a previously saved z-position from manual monitoring. This prevents the
        slow automatic first-location algorithm from running during sequence execution.

        Args:
            postfix (str): Filename postfix from sequence builder for identification

        Returns:
            tuple[int, dict]: (status, state) - 0 for success, error dict for failure
        """
        self.logger.log_info(f"Starting touchDetect sequence step with postfix: {postfix}")

        # Ensure all configured manipulators have saved positions
        status, result = self._check_saved_positions()
        if status != 0:
            error_msg = f"TouchDetect sequence step failed: {result.get('Error message', 'Unknown error')}"
            return (status, {"Error message": error_msg, "safety_check": "failed", "details": result})

        # Execute move to contact for all configured manipulators
        status, state = self.move_to_contact()

        if status != 0:
            self.logger.log_warn(f"TouchDetect sequence step failed: {state}")
            return (status, state)

        self.logger.log_info("TouchDetect sequence step completed successfully")
        return (0, {"message": "TouchDetect sequence step completed successfully", "safety_check": "passed"})
