import os
import copy
from touchDetect import touchDetect
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QComboBox, QGroupBox
from plugins.plugin_components import public, ConnectionIndicatorStyle
from components.worker_thread import WorkerThread
import time


class touchDetectGUI(QObject):
    
    non_public_methods = []
    public_methods = ["move_to_contact", "parse_settings_widget", "sequenceStep", "setSettings", "_check_saved_positions", "clear_saved_positions"]
    green_style = ConnectionIndicatorStyle.GREEN_CONNECTED.value
    red_style = ConnectionIndicatorStyle.RED_DISCONNECTED.value

    ########Signals
    # signals retained since this plugins needs to send errors to main window.
    log_message = pyqtSignal(str)
    info_message = pyqtSignal(str)

    def emit_log(self, status: int, state: dict) -> None:
        """
        Emits a standardized log message for status dicts or error lists.
        Args:
            status (int): status code, 0 for success, non-zero for error.
            state (dict): dictionary in the standard pyIVLS format

        """
        plugin_name = self.__class__.__name__
        msg = state.get("Error message", "Unknown error")
        exception = state.get("Exception", "Not provided")

        if status == 0:
            log = f"{plugin_name} : INFO : {msg} : Exception: {exception}"
        else:
            log = f"{plugin_name} : WARN : {msg} : Exception: {exception}"

        self.log_message.emit(log)

    def _log_verbose(self, message: str) -> None:
        """Log verbose messages with VERBOSE flag"""
        plugin_name = self.__class__.__name__
        log = f"{plugin_name} : VERBOSE : {message}"
        self.log_message.emit(log)

    def _log_info(self, message: str) -> None:
        """Log informational messages with INFO flag"""
        plugin_name = self.__class__.__name__
        log = f"{plugin_name} : INFO : {message}"
        self.log_message.emit(log)

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
        self.functionality = touchDetect(log=self._log_verbose)

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

        self.manipulator_boxes = [[man1, man1_smu_box, man1_con_box], [man2, man2_smu_box, man2_con_box], [man3, man3_smu_box, man3_con_box], [man4, man4_smu_box, man4_con_box]]

        self.settings = [{}, {}, {}, {}]

        # Thread management for monitoring
        self.monitoring_thread = None
        self.is_monitoring = False

        # find threshold line edit
        self.threshold = self.settingsWidget.reshold
        self.stride = self.settingsWidget.stride
        self.sample_width = self.settingsWidget.sampleWidth  # New field for max distance

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
        self._log_verbose("Updating plugin status")
        mm, smu, con = self._fetch_dep_plugins()
        self.channel_names = smu.smu_channelNames()
        if self.channel_names is not None:
            self.smu_indicator.setStyleSheet(self.green_style)
            self._log_verbose(f"SMU channels available: {self.channel_names}")
        status, state = mm.mm_devices()

        if status == 0:
            self.mm_indicator.setStyleSheet(self.green_style)
            self._log_info(f"Micromanipulator devices detected: {state}")
            for i, status in enumerate(state):
                if status:
                    box, smu_box, con_box = self.manipulator_boxes[i]
                    box.setVisible(True)
                    smu_box.clear()
                    con_box.clear()
                    smu_box.addItems(self.channel_names)
                    con_box.addItems(["Hi", "Lo"])

                    settings = self.settings[i]
                    if "channel_smu" in settings:
                        smu_box.setCurrentText(settings["channel_smu"])
                    if "channel_con" in settings:
                        con_box.setCurrentText(settings["channel_con"])
        else:
            self.emit_log(status, state)
        con_status, con_state = con.deviceConnect()
        if con_status == 0:
            self.con_indicator.setStyleSheet(self.green_style)
            self._log_info("Contact detection device connected successfully")
            con_status, con_state = con.deviceDisconnect()
        else:
            self.emit_log(con_status, con_state)

    def dependencies_changed(self):
        self._log_verbose("Dependencies changed, updating combo boxes")
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
        self._log_info("Plugin dependencies updated successfully")

    ########Functions
    ########plugins interraction

    def _getLogSignal(self):
        return self.log_message

    def _getInfoSignal(self):
        return self.info_message

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
            except ValueError:
                # this is here to make sure that only _1, _2, etc. are parsed for manipulator settings
                continue
        stride = settings.get("stride", "")
        threshold = settings.get("res_threshold", "")
        sample_width = settings.get("sample_width", "")
        return temp, threshold, stride, sample_width
    
    def setup(self, settings) -> QWidget:
        """
        Sets up the GUI for the plugin. This function is called by hook to initialize the GUI.
        """


        for box, _, _ in self.manipulator_boxes:
            box.setVisible(False)
        # save the settings dict to be used later
        self.settings, threshold, stride, sample_width = self._parse_ini(settings)
        self.threshold.setText(threshold)
        self.stride.setText(stride)
        self.sample_width.setText(sample_width)

        # Set initial button text
        self.settingsWidget.pushButton_2.setText("Start Monitoring")

        self.settingsWidget.initButton.clicked.connect(self.update_status)
        self.settingsWidget.pushButton.clicked.connect(self._test)
        self.settingsWidget.pushButton_2.clicked.connect(self._monitor_threaded)
        return self.settingsWidget

    def _monitor_worker(self, worker_thread):
        """
        Worker function that runs the monitoring in a separate thread.
        This function contains the actual monitoring logic.

        Args:
            worker_thread: The WorkerThread instance for communication and stop checking
        """
        try:
            mm, smu, con = self._fetch_dep_plugins()

            # Connect to devices
            status, state = con.deviceConnect()
            if status != 0:
                worker_thread.error.emit(f"Contact detection connection failed: {state}")
                return (status, {"Error message": f"{state}"})

            status_smu, state_smu = smu.smu_connect()
            if status_smu != 0:
                worker_thread.error.emit(f"SMU connection failed: {state_smu}")
                return (status_smu, {"Error message": f"{state_smu}"})

            status, state = mm.mm_open()
            if status != 0:
                worker_thread.error.emit(f"Micromanipulator connection failed: {state}")
                return (status, {"Error message": f"{state}"})

            worker_thread.progress.emit("All devices connected successfully")

            # Get configured manipulators
            status, settings = self.parse_settings_widget()
            if status != 0:
                worker_thread.error.emit(f"Settings parsing failed: {settings}")
                return (status, settings)

            # Process each configured manipulator
            for i, (box, smu_box, con_box) in enumerate(self.manipulator_boxes):
                if worker_thread.is_stop_requested():
                    break

                manipulator_name = i + 1
                smu_channel = smu_box.currentText()
                con_channel = con_box.currentText()

                # Skip if manipulator is not configured
                if not smu_channel or not con_channel:
                    continue

                threshold = float(settings.get("res_threshold", 150))
                worker_thread.progress.emit(f"Starting monitoring for manipulator {manipulator_name} (SMU: {smu_channel}, Con: {con_channel}, Threshold: {threshold})")

                # Set up contact detection channel
                con.deviceLoCheck(False)
                con.deviceHiCheck(False)
                if con_channel == "Hi":
                    con.deviceHiCheck(True)
                elif con_channel == "Lo":
                    con.deviceLoCheck(True)
                else:
                    worker_thread.error.emit(f"Invalid contact detection channel {con_channel} for manipulator {manipulator_name}")
                    continue

                # Set up SMU for resistance measurement
                status, state = smu.smu_setup_resmes(smu_channel)
                if status != 0:
                    worker_thread.error.emit(f"Failed to setup SMU for manipulator {manipulator_name}: {state}")
                    continue

                # Set active manipulator
                mm.mm_change_active_device(manipulator_name)

                worker_thread.progress.emit(f"MANUAL CONTROL: Move manipulator {manipulator_name} manually until contact is detected")
                worker_thread.progress.emit(f"Monitoring resistance on {smu_channel} with threshold {threshold}...")

                # Monitor loop for this manipulator
                contact_detected = False
                while not contact_detected and not worker_thread.is_stop_requested():
                    try:
                        status, r = smu.smu_resmes(smu_channel)
                        if status != 0:
                            worker_thread.error.emit(f"Resistance measurement failed for manipulator {manipulator_name}: {r}")
                            break

                        r = float(r)
                        # Emit resistance update less frequently to avoid overwhelming the GUI
                        if hasattr(self, "_last_resistance_log"):
                            if abs(r - self._last_resistance_log) > threshold * 0.1:  # Only log if significant change
                                worker_thread.progress.emit(f"Manipulator {manipulator_name} resistance: {r:.1f} Ω (threshold: {threshold} Ω)")
                                self._last_resistance_log = r
                        else:
                            worker_thread.progress.emit(f"Manipulator {manipulator_name} resistance: {r:.1f} Ω (threshold: {threshold} Ω)")
                            self._last_resistance_log = r

                        if r < threshold:
                            # Contact detected! Save the z-position
                            _, _, z_position = mm.mm_current_position()
                            self.functionality.last_z[manipulator_name] = z_position

                            worker_thread.progress.emit(f"CONTACT DETECTED: Manipulator {manipulator_name} at z={z_position} saved as baseline position")
                            contact_detected = True

                        time.sleep(0.1)

                    except Exception as e:
                        worker_thread.error.emit(f"Exception during monitoring for manipulator {manipulator_name}: {str(e)}")
                        break

                # Clean up for this manipulator
                con.deviceLoCheck(False)
                con.deviceHiCheck(False)
                smu.smu_outputOFF()

            if not worker_thread.is_stop_requested():
                worker_thread.progress.emit("Monitoring completed for all configured manipulators")
                worker_thread.progress.emit(f"Saved positions: {self.functionality.last_z}")
                return (0, {"Error message": "Monitoring completed successfully"})
            else:
                worker_thread.progress.emit("Monitoring stopped by user")
                return (0, {"Error message": "Monitoring stopped by user"})

        except Exception as e:
            error_msg = f"Exception during monitoring: {str(e)}"
            worker_thread.error.emit(error_msg)
            return (2, {"Error message": error_msg, "Exception": str(e)})

        finally:
            # clean up
            try:
                con.deviceLoCheck(False)
                con.deviceHiCheck(False)
                smu.smu_outputOFF()
                con.deviceDisconnect()
                worker_thread.progress.emit("Disconnected from all devices")
            except Exception:
                pass  # Ignore cleanup errors

    def _monitor_threaded(self):
        """
        Starts or stops the monitoring process in a separate thread.
        This keeps the GUI responsive during monitoring.
        """
        if not self.is_monitoring:
            # Start monitoring
            self._log_info("Starting threaded resistance monitoring for all manipulators")
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
            self._log_info("Stopping monitoring thread")
            if self.monitoring_thread:
                self.monitoring_thread.stop()
                # Don't wait here as it would block the GUI
                # The finished signal will handle cleanup

    def _on_monitoring_progress(self, message):
        """Handle progress updates from the monitoring thread."""
        self._log_info(message)

    def _on_monitoring_error(self, error_message):
        """Handle error messages from the monitoring thread."""
        self._log_info(f"WARN : {error_message}")

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
        self._log_info("Monitoring thread finished")

    def _test(self):
        self._log_info("Testing move to contact functionality")

        # First check if we have saved positions for all configured manipulators
        status, result = self._check_saved_positions()
        if status != 0:
            error_msg = f"Cannot test: {result.get('Error message', 'Unknown error')}"
            self._log_info(f"TEST FAILED: {error_msg}")
            self.emit_log(status, {"Error message": error_msg})
            return

        # Proceed with the test
        status, state = self.move_to_contact()
        if status == 0:
            self._log_info("Move to contact test completed successfully")
        else:
            self._log_info(f"Move to contact test failed: {state.get('Error message', 'Unknown error')}")
        self.emit_log(status, state)

    def parse_settings_widget(self) -> tuple[int, dict]:
        """
        Parses the settings widget and returns error code and settings as a dictionary matching .ini keys.
        """
        settings = {}
        # Collect manipulator settings
        for i, (box, smu_box, con_box) in enumerate(self.manipulator_boxes):
            smu_channel = smu_box.currentText()
            con_channel = con_box.currentText()
            # Only add if either is non-empty
            if smu_channel or con_channel:
                settings[f"{i + 1}_smu"] = smu_channel
                settings[f"{i + 1}_con"] = con_channel

        # Check that the same con channel does not appear twice (excluding empty)
        con_channels = [settings[f"{i + 1}_con"] for i in range(4) if f"{i + 1}_con" in settings and settings[f"{i + 1}_con"]]
        if len(con_channels) != len(set(con_channels)):
            return (1, {"Error message": "Contact detection channels must be unique across manipulators."})

        # Check that the threshold is a float
        try:
            threshold = float(self.threshold.text())
        except ValueError:
            return (1, {"Error message": "TouchDetect: Threshold must be a number."})
        settings["res_threshold"] = threshold

        # Check that the stride is an integer
        try:
            stride = int(self.stride.text())
        except ValueError:
            return (1, {"Error message": "TouchDetect: Stride must be an integer."})
        settings["stride"] = stride

        # Check that the sample width is a float
        try:
            sample_width = float(self.sample_width.text())
        except ValueError:
            return (1, {"Error message": "TouchDetect: Sample width must be a number."})
        settings["sample_width"] = sample_width

        return (0, settings)

    @public
    def setSettings(self, settings: dict) -> tuple[int, dict]:
        """
        Sets the plugin settings from the sequence builder.

        Args:
            settings (dict): Settings dictionary with plugin configuration

        Returns:
            tuple[int, dict]: (status, settings) - status 0 for success, settings dict
        """
        
        """
        The settings dictionary is expected to have the following structure:
        [{}, {}, {}, {}]
        where each dictionary corresponds to a manipulator and contains:
        - "channel_smu": SMU channel name (string)
        - "channel_con": Contact detection channel name (string)
        - "res_threshold": Resistance threshold (float)
        - "stride": Stride for monitoring (int)
        - "sample_width": Sample width for monitoring (float)   

        Parse settings widget returns the settings in the format of:
        {
            "1_smu": "SMU1",
            "1_con": "Hi",
            "2_smu": "SMU2",
            "2_con": "Lo",
            "res_threshold": 150.0,
            "stride": 10,
            "sample_width": 0.1
        }
        """
        self._log_verbose("Setting settings for touchDetect plugin: " + str(settings))
        # Deep copy to avoid modifying original data
        settings_to_parse = copy.deepcopy(settings)
        # Parse settings into the expected format
        self.settings, threshold, stride, sample_width = self._parse_ini(settings_to_parse)
        return (0, self.settings)

    ########Functions to be used externally
    def move_to_contact(self):
        self._log_info("Starting move to contact operation")

        # SAFETY CHECK: Ensure all configured manipulators have saved positions
        status, result = self._check_saved_positions()
        if status != 0:
            error_msg = f"Cannot move to contact: {result.get('Error message', 'Unknown error')}"
            self._log_info(f"SAFETY: {error_msg}")
            self.emit_log(status, {"Error message": error_msg})
            return (status, {"Error message": error_msg, "safety_check": "failed"})

        def create_dict():
            # check settings
            self._log_verbose("Parsing settings for move to contact")
            status, settings = self.parse_settings_widget()
            if status == 0:
                # convert settings to a format that self.functionality expects
                temp = []
                for i in range(len(self.manipulator_boxes)):
                    smu_key = f"{i + 1}_smu"
                    con_key = f"{i + 1}_con"
                    smu_val = settings.get(smu_key, "")
                    con_val = settings.get(con_key, "")
                    threshold = float(settings["res_threshold"])
                    stride = int(settings["stride"])
                    sample_width = float(settings["sample_width"])
                    temp.append((smu_val, con_val, threshold, stride, sample_width))
                self._log_verbose(f"Created manipulator info: {temp}")
                return temp
            else:
                self.emit_log(status, settings)
                return []

        mm, smu, con = self._fetch_dep_plugins()
        manipulator_info = create_dict() # will be empty if invalid

        status, state = self.functionality.move_to_contact(mm, con, smu, manipulator_info)

        if status != 0:
            self.emit_log(status, state)
            return (status, state)
        self._log_info("Move to contact operation completed successfully")
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
        self._log_info(f"Cleared saved positions: {old_positions}")
        return (0, {"message": "Saved positions cleared", "cleared_positions": old_positions})

    def _check_saved_positions(self) -> tuple[int, dict]:
        """
        Checks if all configured manipulators have saved z-positions from previous monitoring.

        Returns:
            tuple[int, dict]: (status, result) - 0 for success with all positions saved,
                             1 for error with missing positions
        """
        status, settings = self.parse_settings_widget()
        if status != 0:
            return (status, settings)

        missing_positions = []
        configured_manipulators = []

        # Check each configured manipulator
        for i, (box, smu_box, con_box) in enumerate(self.manipulator_boxes):
            manipulator_name = i + 1
            smu_channel = smu_box.currentText()
            con_channel = con_box.currentText()

            # Skip if manipulator is not configured
            if not smu_channel or not con_channel:
                continue

            configured_manipulators.append(manipulator_name)

            # Check if this manipulator has a saved position
            if manipulator_name not in self.functionality.last_z:
                missing_positions.append(manipulator_name)

        if missing_positions:
            error_msg = f"Missing saved positions for manipulators: {missing_positions}. Run manual monitoring first to establish baseline positions."
            self._log_info(f"WARN : {error_msg}")
            return (1, {"Error message": error_msg, "missing_positions": missing_positions, "configured_manipulators": configured_manipulators})

        self._log_info(f"All configured manipulators ({configured_manipulators}) have saved positions: {self.functionality.last_z}")
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
        self._log_info(f"Starting touchDetect sequence step with postfix: {postfix}")

        # Ensure all configured manipulators have saved positions
        status, result = self._check_saved_positions()
        if status != 0:
            error_msg = f"TouchDetect sequence step failed: {result.get('Error message', 'Unknown error')}"
            return (status, {"Error message": error_msg, "safety_check": "failed", "details": result})


        # Execute move to contact for all configured manipulators
        status, state = self.move_to_contact()

        if status != 0:
            self._log_info(f"TouchDetect sequence step failed: {state}")
            return (status, state)

        self._log_info("TouchDetect sequence step completed successfully")
        return (0, {"message": "TouchDetect sequence step completed successfully", "safety_check": "passed"})
