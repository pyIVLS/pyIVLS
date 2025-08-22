import os
import copy
from touchDetect import touchDetect, ManipulatorInfo
from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QComboBox, QGroupBox, QSpinBox
from plugins.plugin_components import public, ConnectionIndicatorStyle, get_public_methods, LoggingHelper
from components.worker_thread import WorkerThread


class ManipulatorInfoWrapper(QObject):
    update_gui_signal = pyqtSignal(dict, list, list)

    def __init__(self, settingsWidget: QWidget, mm_number: int):
        super().__init__()
        self.man_box = settingsWidget.findChild(QGroupBox, f"manipulator{mm_number}")
        self.smu_channel = self.man_box.findChild(QComboBox, f"mansmu_{mm_number}")
        self.con_channel = self.man_box.findChild(QComboBox, f"mancon_{mm_number}")
        self.threshold = self.man_box.findChild(QSpinBox, f"manres_{mm_number}")

        # Find Global settings
        self.stride = settingsWidget.findChild(QSpinBox, "stride")
        self.sample_width = settingsWidget.findChild(QSpinBox, "sample_width")
        self.spectro_height = settingsWidget.findChild(QSpinBox, "spectro_height")

        assert self.stride is not None, "touchDetectGui: stride SpinBox not found"
        assert self.sample_width is not None, "touchDetectGui: sample_width SpinBox not found"
        assert self.spectro_height is not None, "touchDetectGui: spectro_height SpinBox not found"

        # internal state
        self.mi = ManipulatorInfo(mm_number=mm_number, smu_channel=self.smu_channel.currentText(), condet_channel=self.con_channel.currentText(), threshold=self.threshold.value(), stride=self.stride.value(), sample_width=self.sample_width.value(), spectrometer_height=self.spectro_height.value(), function="")

        # connect signal
        self.update_gui_signal.connect(self._update_gui_slot)

    def update_settings(self, settings: dict):
        """Update settings from standardized format (1_smu, 1_con, etc.)"""
        # Extract settings for this specific manipulator
        manipulator_settings = {}
        mm_num = self.mi.mm_number

        # Map standardized keys to ManipulatorInfo parameters
        key_mapping = {f"{mm_num}_smu": "smu_channel", f"{mm_num}_con": "condet_channel", f"{mm_num}_res": "threshold", f"{mm_num}_last_z": "last_z", "stride": "stride", "sample_width": "sample_width", "spectrometer_height": "spectrometer_height"}

        # Extract relevant settings for this manipulator
        for std_key, mi_key in key_mapping.items():
            if std_key in settings:
                manipulator_settings[mi_key] = settings[std_key]
        # Update the ManipulatorInfo object
        self.mi = self.mi.with_new_settings(**manipulator_settings)

    def update_settings_from_gui(self):
        """Update settings from GUI controls"""
        self.mi = self.mi.with_new_settings(smu_channel=self.smu_channel.currentText(), condet_channel=self.con_channel.currentText(), threshold=self.threshold.value(), stride=self.stride.value(), sample_width=self.sample_width.value(), spectrometer_height=self.spectro_height.value())

    def is_configured(self) -> bool:
        return self.mi.is_configured()

    def validate(self) -> list[str]:
        return self.mi.validate()
    
    def is_visible(self) -> bool:
        return self.man_box.isVisible()

    def get_standardized_settings(self) -> dict:
        """Export current settings in standardized format (1_smu, 1_con, etc.)"""
        if self.is_visible:
            return self.mi.to_named_dict()
        return {}

    def queue_update(self, smu_channel_list: list = [], con_channel_list: list = []):
        self.update_gui_signal.emit(self.mi.to_named_dict(), smu_channel_list, con_channel_list)

    @pyqtSlot(dict, list, list)
    def _update_gui_slot(self, settings: dict, smu_channel_list: list, con_channel_list: list):
        # fill comboboxes
        self.smu_channel.clear()
        self.smu_channel.addItems(smu_channel_list)
        self.con_channel.clear()
        self.con_channel.addItems(con_channel_list)
        # get the settings for this specific instance using the manipulator number
        mm_num = self.mi.mm_number
        self.smu_channel.setCurrentText(settings.get(f"{mm_num}_smu", ""))
        self.con_channel.setCurrentText(settings.get(f"{mm_num}_con", ""))
        self.threshold.setValue(int(settings.get(f"{mm_num}_res", 0)))

        # general settings
        self.stride.setValue(int(settings["stride"]))
        self.sample_width.setValue(int(settings["sample_width"]))
        self.spectro_height.setValue(int(settings["spectrometer_height"]))

    def set_visible(self, visible: bool):
        self.man_box.setVisible(visible)


class touchDetectGUI(QObject):
    green_style = ConnectionIndicatorStyle.GREEN_CONNECTED.value
    red_style = ConnectionIndicatorStyle.RED_DISCONNECTED.value

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

        # initialize internal state:
        self.manipulator_wrappers: list[ManipulatorInfoWrapper] = []
        for i in range(1, 5):
            self.manipulator_wrappers.append(ManipulatorInfoWrapper(self.settingsWidget, i))
            self.manipulator_wrappers[-1].set_visible(False)

        # Thread management for monitoring
        self.monitoring_thread = None
        self.is_monitoring = False

        # connect signals:
        self.settingsWidget.initButton.clicked.connect(self.update_status)
        self.settingsWidget.pushButton.clicked.connect(self._test)
        self.settingsWidget.pushButton_2.clicked.connect(self._monitor_threaded)

        self.con_channels = ["Hi", "Lo", "none", "spectrometer"]
        self.smu_channels = ["none", "spectrometer"]

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

        self.smu_channels = self.channel_names + ["none", "spectrometer"]

        if status == 0:
            self.mm_indicator.setStyleSheet(self.green_style)
            self.logger.log_info(f"Micromanipulator devices detected: {state}")
            num_dev, active_list = state
            for i, status in enumerate(active_list):
                if status:
                    wrap = self.manipulator_wrappers[i]
                    wrap.set_visible(True)
                    wrap.queue_update(self.smu_channels, self.con_channels)
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
        self.logger.log_debug("Dependencies changed, updating dependency combo boxes")
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
        return get_public_methods(self)

    def setup(self, settings) -> QWidget:
        """
        Sets up the GUI for the plugin. This function is called by hook to initialize the GUI.
        """
        for wrap in self.manipulator_wrappers:
            wrap.update_settings(settings)
            wrap.queue_update(self.smu_channels, self.con_channels)

        # Set initial button text
        self.settingsWidget.pushButton_2.setText("Start Monitoring")

        return self.settingsWidget

    def _monitor_worker(self, worker_thread: WorkerThread):
        """
        Worker function that runs the monitoring in a separate thread.
        This function now uses the touchDetect.monitor_manual_contact_detection method.

        Args:
            worker_thread: The WorkerThread instance for communication and stop checking
        """
        try:
            mm, smu, con = self._fetch_dep_plugins()

            # Get current settings from GUI and update all wrappers
            for wrapper in self.manipulator_wrappers:
                wrapper.update_settings_from_gui()

            # Get configured manipulator wrappers (use the actual wrapper ManipulatorInfo objects)
            configured_wrappers = [wrapper for wrapper in self.manipulator_wrappers if wrapper.is_configured()]

            if not configured_wrappers:
                worker_thread.error.emit("No configured manipulators found")
                return (1, {"Error message": "No configured manipulators found"})

            # Extract the ManipulatorInfo objects from configured wrappers
            manipulator_infos = [wrapper.mi for wrapper in configured_wrappers]

            # remove manipulators that don't need z-position
            manipulator_infos = [info for info in manipulator_infos if info.needs_z_pos()]
            if not manipulator_infos:
                worker_thread.error.emit("No manipulators require z-position monitoring")
                return (1, {"Error message": "No manipulators require z-position monitoring"})

            # Define callbacks for the monitoring
            def progress_callback(message):
                worker_thread.progress.emit(message)

            def error_callback(message):
                worker_thread.error.emit(message)

            def stop_requested_callback():
                return worker_thread.is_stop_requested()

            # Use the touchDetect monitor_manual_contact_detection method
            status, result = self.functionality.monitor_manual_contact_detection(mm=mm, smu=smu, con=con, manipulator_infos=manipulator_infos, progress_callback=progress_callback, error_callback=error_callback, stop_requested_callback=stop_requested_callback)

            # Update the wrappers with the saved z-positions from the monitoring result
            if status == 0:
                # Log summary of saved positions
                saved_positions = {w.mi.mm_number: w.mi.last_z for w in configured_wrappers if w.mi.last_z is not None}
                if saved_positions:
                    worker_thread.progress.emit(f"Monitoring completed. Saved positions: {saved_positions}")

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
            self.parse_settings_widget()
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
            self.settingsWidget.pushButton_2.setText("Start Monitoring")
            if self.monitoring_thread:
                self.monitoring_thread.stop()

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

        status, state = self.move_to_contact()
        if status == 0:
            self.logger.log_info("Move to contact test completed successfully")
        else:
            self.logger.log_warn(f"Move to contact test failed: {state.get('Error message', 'Unknown error')}")

    @public
    def parse_settings_widget(self) -> tuple[int, dict]:
        settings = {}
        # Collect manipulator settings
        for wrap in self.manipulator_wrappers:
            # do nothing if box is not visible.
            if wrap.is_visible():
                wrap.update_settings_from_gui()  # Update ManipulatorInfo with current GUI values
                errors = wrap.mi.validate()
                if errors:
                    self.logger.log_warn(f"Validation errors found in manipulator {wrap.mi.mm_number}: {errors}")
                    return(1, {"Error message": f"Validation errors found in manipulator {wrap.mi.mm_number}: {errors}"})
                else:
                    wrap_set = wrap.get_standardized_settings()
                    settings.update(wrap_set)

        # extract channels
        con_channels = []
        for key, value in settings.items():
            # split at "_" and check if ends in con
            if key.endswith("_con"):
                con_channels.append(value)

        # filter nones
        con_channels = [ch for ch in con_channels if ch != "none"]

        # check that channels are unique across manipulators, except "none" can be present more than once
        if len(con_channels) != len(set(con_channels)):
            return (1, {"Error message": "Contact detection channels must be unique across manipulators."})
        print(settings)
        return (0, settings)

    @public
    def setSettings(self, settings: dict):
        self.logger.log_debug("Setting settings for touchDetect plugin: " + str(settings))
        print(settings)
        # Deep copy to avoid modifying original data
        settings_to_parse = copy.deepcopy(settings)
        for wrap in self.manipulator_wrappers:
            wrap.update_settings(settings_to_parse)

    @public
    def set_gui_from_settings(self) -> tuple[int, dict]:
        """
        Updates the GUI controls based on the internal settings.
        This method should be called after setSettings to refresh the GUI.

        Returns:
            tuple[int, dict]: (status, result) - status 0 for success
        """
        for wrap in self.manipulator_wrappers:
            wrap.queue_update(self.smu_channels, self.con_channels)

    ########Functions to be used externally
    def move_to_contact(self):
        self.logger.log_info("Starting move to contact operation")

        mm, smu, con = self._fetch_dep_plugins()
        # Get configured manipulator wrappers and their ManipulatorInfo objects
        configured_wrappers = [wrapper for wrapper in self.manipulator_wrappers if wrapper.is_configured()]
        print(len(configured_wrappers))
        manipulator_infos = [wrapper.mi for wrapper in configured_wrappers]
        print(manipulator_infos)
        if not manipulator_infos:
            error_msg = "No configured manipulators found"
            self.logger.log_warn(error_msg)
            return (1, {"Error message": error_msg})
        # validate infos
        for info in manipulator_infos:
            validation_errors = info.validate()
            if validation_errors:
                self.logger.log_warn(f"Validation errors found: {validation_errors}")
                return (1, {"Error message": f"Validation errors found: {validation_errors}"})

        status, state = self.functionality.move_to_contact(mm, con, smu, manipulator_infos)

        if status != 0:
            self.emit_log(status, state)
            return (status, state)
        self.logger.log_info("Move to contact operation completed successfully")
        return (status, state)

    @public
    def sequenceStep(self, postfix: str) -> tuple[int, dict]:
        self.logger.log_info(f"Starting touchDetect sequence step with postfix: {postfix}")

        # Execute move to contact for all configured manipulators
        status, state = self.move_to_contact()

        if status != 0:
            self.logger.log_warn(f"TouchDetect sequence step failed: {state}")
            return (status, state)

        self.logger.log_info("TouchDetect sequence step completed successfully")
        return (0, {"message": "TouchDetect sequence step completed successfully", "safety_check": "passed"})
