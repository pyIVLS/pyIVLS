from functools import wraps
from multiprocessing import connection
import os

from PyQt6 import QtWidgets, uic
from PyQt6 import QtCore
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSlot
import importlib.util
from Sutter import Mpc325
from plugin_components import (
    LoggingHelper,
    ConnectionIndicatorStyle,
    public,
    get_public_methods,
    CloseLockSignalProvider,
)
import copy
from components.threadStopped import ThreadStopped
import threading
from typing import Optional

"""
From readme:
0 = no error, 
1 = Value error, 
2 = Any error reported by dependent plugin, 
3 = missing functions or plugins, 
4 = harware error 
plugins return errors in form of list [number, {"Error message":"Error text", "Exception":f"e"}]
e.g. [1, {"Error message":"Value error in sweep plugin: SMU limit prescaler field should be numeric"}] 
error text will be shown in the dialog message in the interaction plugin, 
so the error text should contain the plugin name,
e.g. return [1, {"Error message":"Value error in Keithley plugin: 
drain nplc field should be numeric"}]

"Error message" : message to display in info box
"Missing functions" : list of missing functions from other plugins
"Exception" : exception from called function

"""


def handle_sutter_exceptions(func):
    """Decorator to handle Sutter-specific exceptions while letting ThreadStopped pass through"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except ThreadStopped:
            # Re-raise ThreadStopped without catching it
            raise
        except InterruptedError as e:
            # Handle move interruption as a successful stop operation
            return (0, {"Error message": f"Sutter move interrupted: {str(e)}"})
        except ValueError as e:
            return (1, {"Error message": f"Value error in Sutter plugin: {str(e)}", "Exception": str(e)})
        except Exception as e:
            return (4, {"Error message": f"Sutter HW error: {str(e)}", "Exception": str(e)})

    return wrapper


class SutterGUI(QObject):
    """
    GUI implementation of the sutter microman plugin for pyIVLS.

    public API:

    - mm_open
    - mm_change_active_device
    - mm_devices
    - mm_move
    - mm_move_relative
    - mm_zmove
    - mm_stop
    - mm_up_max
    - mm_current_position



    hooks:
    - get_setup_interface
    - get_functions
    - get_log
    - get_info
    - get_closeLock



    revision 0.1
    2025.05.22
    otsoha
    """

    GREEN_STYLE = ConnectionIndicatorStyle.GREEN_CONNECTED.value
    RED_STYLE = ConnectionIndicatorStyle.RED_DISCONNECTED.value
    update_gui_signal = QtCore.pyqtSignal()
    change_active_device_signal = QtCore.pyqtSignal(int)
    connection_status_signal = QtCore.pyqtSignal(bool)

    @property
    def settingsWidget(self) -> QtWidgets.QWidget:
        if self._settingsWidget is None:
            raise ValueError("Settings widget has not been initialized yet. Call setup() first.")
        return self._settingsWidget

    def __init__(self):
        super().__init__()
        self.hal = Mpc325()
        self.logger = LoggingHelper(self)
        self.cl = CloseLockSignalProvider()
        self.settings = {}
        self._settingsWidget: Optional[QtWidgets.QWidget] = None

    def setup(self, settings):
        """
        Setup the sutter GUI by loading ui and initializing the hal. Connect buttons to functions.
        """
        path = os.path.dirname(__file__) + os.path.sep
        self._settingsWidget = uic.loadUi(path + "Sutter_settingsWidget.ui")  # type: ignore

        # Store settings internally in .ini format
        self.settings = copy.deepcopy(settings)

        # Optional: allow switching to mock via settings (e.g., plugin.ini)
        self._switch_hal_if_mock_requested(self.settings)

        # connect buttons to functions
        self.settingsWidget.connectButton.clicked.connect(self._connect_button)  # type: ignore
        self.settingsWidget.statusButton.clicked.connect(self._status_button)  # type: ignore
        self.settingsWidget.stopButton.clicked.connect(self._stop_button)  # type: ignore
        self.settingsWidget.calibrateButton.clicked.connect(self._calibrate_button)  # type: ignore
        self.settingsWidget.quickBox.toggled.connect(self._quickmove_changed)  # type: ignore
        self.settingsWidget.speedComboBox.currentIndexChanged.connect(self.speed_changed)  # type: ignore
        self.settingsWidget.devnumCombo.currentIndexChanged.connect(self._devnum_changed)  # type: ignore

        # save input fields. Explicit typing here just so I get type hints in vscode
        self.quickmove_input: QtWidgets.QCheckBox = self.settingsWidget.quickBox  # type: ignore
        self.source_input: QtWidgets.QLineEdit = self.settingsWidget.sourceInput  # type: ignore
        self.speed_input: QtWidgets.QComboBox = self.settingsWidget.speedComboBox  # type: ignore
        self.devnum_combo: QtWidgets.QComboBox = self.settingsWidget.devnumCombo  # type: ignore

        # save references to important components so that if they are missing it is caught early
        self.connectionIndicator: QtWidgets.QLabel = self.settingsWidget.connectionIndicator  # type: ignore
        self.connectButton: QtWidgets.QPushButton = self.settingsWidget.connectButton  # type: ignore
        self.basicBox: QtWidgets.QGroupBox = self.settingsWidget.basicBox  # type: ignore
        self.saveBox: QtWidgets.QGroupBox = self.settingsWidget.saveBox  # type: ignore

        # connect gui update signal to slot
        self.update_gui_signal.connect(self._apply_settings_to_gui)
        self.change_active_device_signal.connect(self._change_active_device_gui)
        self.connection_status_signal.connect(self._gui_change_device_connected)

        # fill combobox
        speeds = self.hal._MOVE_SPEEDS
        for speed_key, speed_value in speeds.items():
            self.speed_input.addItem(f"{speed_key}: {int(speed_value)} microns/s")

        # Apply settings to GUI from internal settings
        self.update_gui_signal.emit()
        # update gui based on connection status
        self.connection_status_signal.emit(self.hal.is_connected())

        return self.settingsWidget

    def _switch_hal_if_mock_requested(self, settings: dict | None = None):
        """Switch HAL to mock backend when requested via env or settings.

        Triggers when env `PYIVLS_SUTTER_BACKEND` is 'mock'/'virtual' or
        settings contains key `use_mock` truthy.
        """
        try:
            use_mock_env = os.getenv("PYIVLS_SUTTER_BACKEND", "").lower() in ("mock", "virtual", "software")
            use_mock_setting = False
            if settings is not None:
                val = settings.get("use_mock", False)
                use_mock_setting = (str(val).lower() in ("true", "1", "yes")) if isinstance(val, str) else bool(val)
            if use_mock_env or use_mock_setting:
                print("Switching Sutter HAL to mock backend as requested")
                # Load mock class directly from sibling file to avoid package import issues
                mock_path = os.path.join(os.path.dirname(__file__), "mock.py")
                spec = importlib.util.spec_from_file_location("SutterMock", mock_path)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    self.hal = mod.Mpc325Mock()
                else:
                    raise ImportError("Unable to load Sutter mock backend module")
                # carry over existing settings into the mock
                q = self.settings.get("quickmove")
                s = self.settings.get("speed")
                a = self.settings.get("address")
                self.hal.update_internal_state(q, s, a)
        except Exception as e:
            # Non-fatal; default to real HAL
            self.logger.log_warn(f"Failed to switch to Sutter mock backend: {e}")

    # GUI interactions
    @pyqtSlot()
    def _apply_settings_to_gui(self):
        """Apply internal settings to GUI controls."""
        try:
            # Handle quickmove setting - can be boolean or string
            quickmove = self.settings.get("quickmove", False)
            if isinstance(quickmove, str):
                self.quickmove_input.setChecked(quickmove.lower() == "true")
            else:
                self.quickmove_input.setChecked(bool(quickmove))

            # Set address
            address = self.settings.get("address", "")
            self.source_input.setText(address)

            # Set speed text
            speed_text = self.settings.get("speed_text", "")
            if speed_text:
                self.speed_input.setCurrentText(speed_text)

            # Update HAL internal state based on current settings
            self._update_hal_from_settings()

        except Exception as e:
            self.logger.log_warn(f"Error applying settings to GUI: {str(e)}")

    @pyqtSlot(int)
    def _change_active_device_gui(self, dev_num: int):
        """Slot to change active device from a non-GUI thread."""
        # block signals from changing the combobox index while we update it
        # in order to not trigger the _devnum_changed function.
        self.devnum_combo.blockSignals(True)
        self.devnum_combo.setCurrentIndex(dev_num - 1)
        self.devnum_combo.blockSignals(False)

    def _update_hal_from_settings(self):
        """Update HAL internal state from current settings."""
        try:
            # Parse quickmove
            quickmove = self.settings["quickmove"]
            if isinstance(quickmove, str):
                quickmove = quickmove.lower() == "true"
            else:
                quickmove = bool(quickmove)

            # Get speed
            speed = self.settings["speed"]
            # Get address
            address = self.settings["address"]
            self.hal.update_internal_state(quickmove, speed, address)

        except Exception as e:
            self.logger.log_warn(f"Error updating HAL from settings: {str(e)}")

    @public
    def parse_settings_widget(self) -> tuple[int, dict]:
        """Parse GUI controls into plugin settings format.

        Args:
            None

        Returns:
            tuple[int, dict]:
                - (0, settings) on success, where settings contains:
                  address (str), speed (int), quickmove (bool), speed_text (str).
                - (1, {"Error message": str}) if parsing fails.

        Edge cases:
            - If the speed combobox text does not contain a parsable integer prefix,
              parsing fails with status 1.
            - This method updates both internal settings and HAL state on success.
        """
        try:
            quick_move = bool(self.quickmove_input.isChecked())
            speed_text = self.speed_input.currentText()
            speed = int(speed_text.split(":")[0])
            address = self.source_input.text()

            # Return settings in .ini format (same as sutter.ini)
            settings = {"address": address, "speed": speed, "quickmove": quick_move, "speed_text": speed_text}

            # Update internal settings
            self.settings.update(settings)

            # Update HAL internal state
            self.hal.update_internal_state(quick_move, speed, address)

            return (0, settings)
        except Exception as e:
            return (1, {"Error message": f"{str(e)}"})

    @pyqtSlot(bool)
    def _gui_change_device_connected(self, connected: bool):
        if connected:
            self.connectionIndicator.setStyleSheet(self.GREEN_STYLE)

        else:
            self.connectionIndicator.setStyleSheet(self.RED_STYLE)

        self.source_input.setEnabled(not connected)
        self.connectButton.setText("Disconnect" if connected else "Connect")
        self.basicBox.setEnabled(connected)
        self.saveBox.setEnabled(connected)
        if connected:
            dev_count, dev_statuses = self.hal.get_connected_devices_status()
            self.devnum_combo.clear()
            for i in range(dev_count):
                dev_status = dev_statuses[i]
                if dev_status == 1:
                    self.devnum_combo.addItem(f"{i + 1}")

            current_dev = self.hal.get_active_device()
            # block signals to not trigger the _devnum_changed function when setting the current index
            self.devnum_combo.blockSignals(True)
            self.devnum_combo.setCurrentIndex(current_dev - 1)
            self.devnum_combo.blockSignals(False)
        else:
            self.devnum_combo.clear()
        self.cl.emit_close_lock(connected)

    # The following methods handle GUI events, but also update the internal state of the plugin.
    # kind of non-standard.
    def _quickmove_changed(self, checked: bool):
        """Called when the quickmove checkbox is changed,
        sets visibility of the speed combobox."""
        if checked:
            self.speed_input.setEnabled(False)
        else:
            self.speed_input.setEnabled(True)

        # Update internal settings
        self.settings["quickmove"] = checked
        self.hal.update_internal_state(checked, None, None)

    def _devnum_changed(self):
        """Called when the device number combobox is changed, sets the device number in the hal."""
        curr_text = self.devnum_combo.currentText()
        if curr_text == "":
            return
        dev_num = int(curr_text)
        self.hal.change_active_device(dev_num)

    def speed_changed(self):
        """Called when the speed combobox is changed, sets the speed in the hal."""
        speed_text = self.speed_input.currentText()
        speed = int(speed_text.split(":")[0]) if ":" in speed_text else 13

        # Update internal settings
        self.settings["speed"] = speed
        self.settings["speed_text"] = speed_text

        self.hal.update_internal_state(None, speed, None)

    ## Button functionality:

    def _connect_button(self):
        """Called when the connect button is pressed. Opens the device and sets the connection indicator color."""
        try:
            if self.hal.is_connected():
                self.hal.close()
            else:
                address = self.source_input.text()
                # Update settings with current address
                self.settings["address"] = address
                self.hal.open(address)

        except Exception as e:
            self.logger.info_popup(f"Sutter connection error: {str(e)}")

        finally:
            if self.hal.is_connected():
                self.connection_status_signal.emit(True)
            else:
                self.connection_status_signal.emit(False)

    def _status_button(self):
        def check_fast_moves():
            import time
            import numpy as np

            # Running this shows that speeds up to 12 work when using specified wait time between command1 and 2. When using wait time * 4 modes up to 13 work.
            for i in range(12, 16):
                n = 1000
                pos = self.hal.get_current_position()
                move_times = []
                initial = self.hal.quick_move
                self.hal.quick_move = False
                initial_speed = self.hal.speed
                self.hal.speed = i
                # move n microns, track time:
                start_time = time.perf_counter()
                self.mm_move(x=pos[0] + n)
                end_time = time.perf_counter()
                move_times.append(end_time - start_time)
                """
                start_time = time.perf_counter()
                self.mm_move(x=pos[0])
                end_time = time.perf_counter()
                move_times.append(end_time - start_time)
                """
                print(f"moved with speed {i}: {np.mean(move_times)} seconds")
                self.hal.quick_move = initial
                self.hal.speed = initial_speed

        # run move sequence in a thread
        move_thread = threading.Thread(target=check_fast_moves)
        move_thread.start()

    def _stop_button(self):
        """Called when the stop button is pressed. Stops any ongoing movement."""
        try:
            status, result = self.mm_stop()
            if status == 0:
                self.logger.info_popup("Sutter movement stopped successfully")
            else:
                self.logger.info_popup(f"Stop command failed: {result.get('Error message', 'Unknown error')}")
        except Exception as e:
            self.logger.info_popup(f"Error stopping Sutter: {str(e)}")

    def _calibrate_button(self):
        self.mm_calibrate()

    ## hook functionality

    def _get_public_methods(self):
        """
        Returns a a list of public methods of the class.
        """
        return get_public_methods(self)

    ## API
    @public
    def setSettings(self, settings: dict) -> None:
        """Set plugin settings from sequence-builder style configuration.

        Args:
            settings (dict): Expected keys include address (str), speed (int),
                and quickmove (bool|str). Additional keys are preserved.

        Returns:
            None

        Edge cases:
            - Missing expected keys are handled by _update_hal_from_settings() and
              logged as warnings; this method itself does not raise on malformed
              settings.
            - A deep copy is used to avoid mutating caller-owned dictionaries.
        """
        self.settings = copy.deepcopy(settings)
        # Update HAL internal state based on new settings
        self._update_hal_from_settings()

    @public
    def set_gui_from_settings(self) -> tuple[int, dict]:
        """Schedule a GUI refresh from internal settings.

        Args:
            None

        Returns:
            tuple[int, dict]: Always (0, {"Error message": "GUI updated scheduled"}).

        Edge cases:
            - This call schedules updates through a Qt signal; it does not guarantee
              the GUI update has already been applied when the method returns.
        """
        self.update_gui_signal.emit()
        return (0, {"Error message": "GUI updated scheduled"})

    @public
    @handle_sutter_exceptions
    def mm_open(self) -> tuple[int, dict]:
        """Open the configured Sutter serial connection.

        Args:
            None

        Returns:
            tuple[int, dict]:
                - (0, {"Error message": str}) on success.
                - (1, {...}) for value/argument errors.
                - (4, {...}) for hardware/serial errors.

        Edge cases:
            - If already connected, returns success without reconnecting.
            - If settings has no address, reads from GUI source input.
            - ThreadStopped is re-raised by the exception decorator.
        """
        if self.hal.is_connected():
            return (0, {"Error message": "Sutter already connected"})
        address = self.settings.get("address", "")
        if not address:
            address = self.source_input.text()
            self.settings["address"] = address

        self.hal.open(address)
        # Update settings from GUI after successful connection
        status, parsed_settings = self.parse_settings_widget()
        if status == 0:
            self.settings.update(parsed_settings)
        self.connection_status_signal.emit(self.hal.is_connected())
        return (0, {"Error message": "Sutter connected"})

    @public
    @handle_sutter_exceptions
    def mm_change_active_device(self, dev_num: int) -> tuple[int, dict]:
        """Changes active device.

        Args:
            dev_num: device number (1-4)

        Returns:
            Status: tuple of (status, error message)

        Edge cases:
            - Invalid device numbers are validated in HAL and mapped by the
              exception decorator to status 1.
            - If HAL returns False for a change request, status 4 is returned.
            - ThreadStopped is re-raised by the exception decorator.

        """
        if self.hal.change_active_device(dev_num):
            # signal gui update
            self.change_active_device_signal.emit(dev_num)
            return (0, {"Error message": "Sutter device changed to " + str(dev_num)})
        return (4, {"Error message": "Sutter device change error"})

    @public
    @handle_sutter_exceptions
    def mm_move(self, x=None, y=None, z=None) -> tuple[int, dict]:
        """Move manipulator to absolute coordinates.

        Args:
            x (float | None): Target X position in microns.
            y (float | None): Target Y position in microns.
            z (float | None): Target Z position in microns.

        Returns:
            tuple[int, dict]:
                - (0, {"Error message": "Sutter moved"}) on success.
                - (1, {...}) for value/argument errors.
                - (4, {...}) for hardware/serial errors.

        Edge cases:
            - Any axis set to None is preserved at current position.
            - If target equals current position after HAL handrails, HAL performs
              no movement and this method still returns success.
            - ThreadStopped is re-raised by the exception decorator.
        """
        # Perform direct move
        self.hal.move(x, y, z)

        return (0, {"Error message": "Sutter moved"})

    @public
    @handle_sutter_exceptions
    def mm_move_relative(self, x_change=0, y_change=0, z_change=0) -> tuple[int, dict]:
        """Move manipulator relative to current position.

        Args:
            x_change (float): Delta X in microns.
            y_change (float): Delta Y in microns.
            z_change (float): Delta Z in microns.

        Returns:
            tuple[int, dict]:
                - (0, {"Error message": "Sutter moved"}) on success.
                - (1, {...}) for value/argument errors.
                - (4, {...}) for hardware/serial errors.

        Edge cases:
            - Relative target is calculated from live HAL position at call time.
            - Bounds are enforced by underlying HAL move routines.
            - ThreadStopped is re-raised by the exception decorator.
        """
        (x, y, z) = self.hal.get_current_position()
        self.mm_move(x + x_change, y + y_change, z + z_change)
        return (0, {"Error message": "Sutter moved"})

    @public
    @handle_sutter_exceptions
    def mm_calibrate(self, all=False) -> tuple[int, dict]:
        """Calibrate currently active manipulator.

        Args:
            all (bool): If False, calibrate active manipulator only. If True,
                all-device calibration is requested but not implemented.

        Returns:
            tuple[int, dict]:
                - (0, {"Error message": "Sutter calibrated"}) on success.
                - (1, {...}) for value/argument errors.
                - (4, {...}) for hardware/serial errors.

        Edge cases:
            - Performs a pre-calibration move to minimum Z before calibrating.
            - all=True raises NotImplementedError, which is mapped to status 4 by
              the exception decorator.
            - ThreadStopped is re-raised by the exception decorator.
        """
        if not all:
            # move first in the z axis to the minimum position
            self.mm_move(z=self.hal._MINIMUM_MS)
            # finally calibrate the device
            _ = self.hal.calibrate()
            return (0, {"Error message": "Sutter calibrated"})
        else:
            raise NotImplementedError("Sutter calibration for all devices is not implemented yet.")

    @public
    @handle_sutter_exceptions
    def mm_stop(self) -> tuple[int, dict]:
        """Request stop for ongoing movement/read operations.

        Args:
            None

        Returns:
            tuple[int, dict]:
                - (0, {"Error message": "Sutter stopped"}) if stop command was sent.
                - (4, {...}) if stop command fails.

        Edge cases:
            - HAL stop uses a stop-event and input/output buffer flush.
            - Safe to call when no movement is active; still returns success if
              HAL stop completes without error.
        """
        try:
            self.hal.stop()
            return (0, {"Error message": "Sutter stopped"})
        except Exception as e:
            return (4, {"Error message": f"Sutter stop error: {str(e)}", "Exception": str(e)})

    @public
    @handle_sutter_exceptions
    def mm_zmove(self, z_change, absolute=False) -> tuple[int, dict]:
        """Move manipulator along Z axis.

        Args:
            z_change (float): Delta Z in microns, or absolute Z target when
                absolute is True.
            absolute (bool): When True, z_change is interpreted as absolute target.

        Returns:
            tuple[int, dict]:
                - (0, {"Error message": "Sutter moved"}) on success.
                - (1, {"Error message": "Sutter move out of bounds"}) if target
                  is outside allowed range.
                - (4, {...}) for hardware/serial errors.

        Edge cases:
            - Bounds are checked against HAL _MINIMUM_MS and _MAXIMUM_M before move.
            - In relative mode, target is computed from current live position.
            - ThreadStopped is re-raised by the exception decorator.
        """
        (x, y, z) = self.hal.get_current_position()

        if absolute:
            # For absolute positioning, z_change is the target z position
            target_z = z_change
            if target_z > self.hal._MAXIMUM_M or target_z < self.hal._MINIMUM_MS:
                return (1, {"Error message": "Sutter move out of bounds"})
            self.mm_move(x, y, target_z)
            return (0, {"Error message": "Sutter moved"})
        else:
            # For relative positioning, z_change is the offset
            target_z = z + z_change
            if target_z > self.hal._MAXIMUM_M or target_z < self.hal._MINIMUM_MS:
                return (1, {"Error message": "Sutter move out of bounds"})
            self.mm_move(x, y, target_z)
            return (0, {"Error message": "Sutter moved"})

    @public
    @handle_sutter_exceptions
    def mm_get_active_device(self) -> tuple[int, dict]:
        """Get currently active manipulator index.

        Args:
            None

        Returns:
            tuple[int, int]: (0, device_index) on success.

        Edge cases:
            - Device index is 1-based.
            - Hardware/serial errors are mapped by the exception decorator.
            - ThreadStopped is re-raised by the exception decorator.
        """
        return (0, self.hal.get_active_device())

    @public
    @handle_sutter_exceptions
    def mm_up_max(self) -> tuple[int, dict]:
        """Move currently active manipulator tip to maximum-up position (z = 0).

        Args:
            None

        Returns:
            tuple[int, dict]:
                - (0, {"Error message": ...}) on success or if already at z=0.
                - (1, {...}) for value/argument errors.
                - (4, {...}) for hardware/serial errors.

        Edge cases:
            - If already at z=0, no movement is performed and success is returned.
            - ThreadStopped is re-raised by the exception decorator.
        """
        x, y, z = self.hal.get_current_position()
        if z == 0:
            return (0, {"Error message": "Sutter already at max"})
        self.mm_move(x, y, 0)
        return (0, {"Error message": "Sutter moved up to max"})

    @public
    @handle_sutter_exceptions
    def mm_current_position(self, manipulator_name=None):
        """Get current manipulator position.

        Args:
            manipulator_name (int | None): Optional 1-based manipulator index to
                query. When provided, active device is switched temporarily.

        Returns:
            tuple[float, float, float] | tuple[int, dict]:
                - (x, y, z) in microns on success.
                - (4, {"Error message": ...}) if a requested device switch fails.

        Edge cases:
            - Return type is intentionally non-standard for compatibility with
              existing callers.
            - If manipulator_name is provided, previous active device is restored
              after reading position.
            - Hardware/serial errors are mapped by the exception decorator.
            - ThreadStopped is re-raised by the exception decorator.
        """
        # FIXME: nonstandard return type.
        if manipulator_name is not None:
            old_device = self.hal.get_active_device()
            success = self.hal.change_active_device(manipulator_name)
            if not success:
                return (4, {"Error message": f"Failed to change to device {manipulator_name}"})
            pos = self.hal.get_current_position()
            self.hal.change_active_device(old_device)  # Restore previous device
        else:
            pos = self.hal.get_current_position()
        return pos

    @public
    @handle_sutter_exceptions
    def mm_devices(self):
        """Get count and availability flags for connected manipulators.

        Args:
            None

        Returns:
            list: [status_code, payload]
                - [0, (device_count, device_statuses)] on success.
                - [code, status_dict] if opening device fails.

        Edge cases:
            - Calls mm_open() first; if connection cannot be established, the
              same error is returned unchanged.
            - Uses list return format for legacy compatibility.
            - ThreadStopped is re-raised by the exception decorator.
        """
        code, status = self.mm_open()  # Ensure the device is open before fetching statuses
        if code != 0:
            return [code, status]  # Return error if opening failed
        dev_count, dev_statuses = self.hal.get_connected_devices_status()
        return [0, (dev_count, dev_statuses)]

    @public
    @handle_sutter_exceptions
    def mm_get_positions(self):
        """Get current positions of connected manipulators.

        Args:
            None

        Returns:
            tuple[int, dict]:
                - (0, {device_idx: (x, y, z)}) on first successful read.
                - (4, {"Error message": ...}) if device switch/position read fails.

        Edge cases:
            - Current implementation returns after the first connected manipulator
              instead of aggregating all positions.
            - If no devices are connected, method may return None.
            - ThreadStopped is re-raised by the exception decorator.
        """
        connected_devices = self.hal.get_connected_devices_status()[1]
        for i, status in enumerate(connected_devices):
            if status == 1:
                success = self.hal.change_active_device(i + 1)
                if not success:
                    return 4, {"Error message": f"Failed to change to device {i + 1}"}
                else:
                    pos = self.hal.get_current_position()
                    if pos is None:
                        return 4, {"Error message": f"Failed to get position for device {i + 1}"}
                    return 0, {i + 1: pos}

    @public
    @handle_sutter_exceptions
    def mm_get_num_manipulators(self):
        """Get total number of connected manipulators.

        Args:
            None

        Returns:
            int: Number of manipulators reported by HAL.

        Edge cases:
            - Return type is raw int for legacy compatibility (not status tuple).
            - Hardware/serial errors are mapped by the exception decorator.
            - ThreadStopped is re-raised by the exception decorator.
        """
        dev_count, _ = self.hal.get_connected_devices_status()
        return dev_count

    @public
    @handle_sutter_exceptions
    def mm_slow_move(self, x=None, y=None, z=None):
        """Execute slow move at fixed speed for stop-testing.

        Args:
            x (float | None): Target X in microns.
            y (float | None): Target Y in microns.
            z (float | None): Target Z in microns.

        Returns:
            list: [status_code, payload]
                - [0, {"Error message": "Sutter moved"}] on success.
                - [1, {"Error message": ...}] if all coordinates are None.
                - [4, {...}] for hardware/serial errors.

        Edge cases:
            - Missing axes are backfilled from current position.
            - Uses fixed speed 7 via HAL slow_move_to.
            - Uses list return format for legacy compatibility.
            - ThreadStopped is re-raised by the exception decorator.
        """
        if x is None and y is None and z is None:
            return [1, {"Error message": "Sutter slow move requires at least one coordinate"}]
        if x is None:
            x = self.hal.get_current_position()[0]
        if y is None:
            y = self.hal.get_current_position()[1]
        if z is None:
            z = self.hal.get_current_position()[2]
        self.hal.slow_move_to(x, y, z, 7)
        return [0, {"Error message": "Sutter moved"}]
