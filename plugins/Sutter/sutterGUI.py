import os
import queue

from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from Sutter import Mpc325
from plugin_components import LoggingHelper

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


class SutterMoveWorker(QThread):
    """CURRENTLY UNUSED

    Args:
        QThread (_type_): _description_
    """

    def __init__(self, hal, log_signal=None):
        super().__init__()
        self.hal = hal
        self.log_signal = log_signal
        self.command_queue = queue.Queue()
        self._running = True

    def run(self):
        while self._running:
            try:
                cmd, args = self.command_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            try:
                result = cmd(*args)
                if self.log_signal and result is not None:
                    self.log_signal.emit(str(result))
            except Exception as e:
                if self.log_signal:
                    self.log_signal.emit(f"Sutter HW error: {str(e)}")
            self.command_queue.task_done()

    def stop(self):
        self._running = False
        self.wait()

    def enqueue(self, cmd, args=()):
        self.command_queue.put((cmd, args))


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

    log_message = pyqtSignal(str)
    info_message = pyqtSignal(str)
    closeLock = pyqtSignal(bool)

    # FIXME: kinda stupid to import the names here
    def __init__(self, name, function):
        super().__init__()
        self.hal = Mpc325()
        self.plugin_name = name
        self.plugin_function = function
        # self._move_worker = SutterMoveWorker(self.hal, self.log_message)
        self.logger = LoggingHelper(self)
        self.settings = {}

    def setup(self, settings):
        """
        Setup the sutter GUI by loading ui and initializing the hal. Connect buttons to functions.
        """
        path = os.path.dirname(__file__) + os.path.sep
        self.settingsWidget = uic.loadUi(path + "Sutter_settingsWidget.ui")

        # connect buttons to functions
        self.settingsWidget.connectButton.clicked.connect(self._connect_button)
        self.settingsWidget.statusButton.clicked.connect(self._status_button)
        self.settingsWidget.stopButton.clicked.connect(self._stop_button)
        self.settingsWidget.calibrateButton.clicked.connect(self._calibrate_button)
        self.settingsWidget.quickBox.toggled.connect(self._quickmove_changed)
        self.settingsWidget.speedComboBox.currentIndexChanged.connect(self.speed_changed)
        self.settingsWidget.devnumCombo.currentIndexChanged.connect(self._devnum_changed)

        # save input fields. Explicit typing here just so I get type hints in vscode
        self.quickmove_input: QtWidgets.QCheckBox = self.settingsWidget.quickBox
        self.source_input: QtWidgets.QLineEdit = self.settingsWidget.sourceInput
        self.speed_input: QtWidgets.QComboBox = self.settingsWidget.speedComboBox
        self.devnum_combo: QtWidgets.QComboBox = self.settingsWidget.devnumCombo

        # fill combobox
        speeds = self.hal._MOVE_SPEEDS
        for speed_key, speed_value in speeds.items():
            self.speed_input.addItem(f"{speed_key}: {int(speed_value)} µm/s")

        # set default values, try to read from settings.
        quickmove = settings.get("quickmove", False)
        self.quickmove_input.setChecked(quickmove == "True" or quickmove is True)
        source = settings.get("address", "")
        self.source_input.setText(source)
        speed = settings["speed_text"]
        self.speed_input.setCurrentText(speed)

        # read the default settings from the GUI
        self.parse_settings_widget()

        self._gui_change_device_connected(self.hal.is_connected())

        return self.settingsWidget

    # GUI interactions

    def parse_settings_widget(self) -> tuple[int, dict]:
        """Parses the settings widget and sets the values in the class."""
        try:
            quick_move = bool(self.quickmove_input.isChecked())
            speed_text = self.speed_input.currentText()
            speed = int(speed_text.split(":")[0])
            source = self.source_input.text()
            settings = {"quickmove": quick_move, "speed": speed, "address": source, "speed_text": speed_text}
            self.hal.update_internal_state(quick_move, speed, source)

            return [0, settings]
        except Exception as e:
            return [1, {"Error message": f"SutterGUI: {str(e)}"}]

    def _gui_change_device_connected(self, connected: bool):
        if connected:
            self.settingsWidget.connectionIndicator.setStyleSheet("border-radius: 10px; background-color: rgb(38, 162, 105); min-height: 20px; min-width: 20px;")

        else:
            self.settingsWidget.connectionIndicator.setStyleSheet("border-radius: 10px; background-color: rgb(165, 29, 45); min-height: 20px; min-width: 20px;")

        self.source_input.setEnabled(not connected)
        self.settingsWidget.connectButton.setText("Disconnect" if connected else "Connect")
        self.settingsWidget.basicBox.setEnabled(connected)
        self.settingsWidget.saveBox.setEnabled(connected)
        if connected:
            dev_count, dev_statuses = self.hal.get_connected_devices_status()
            self.devnum_combo.clear()
            for i in range(dev_count):
                dev_status = dev_statuses[i]
                if dev_status == 1:
                    self.devnum_combo.addItem(f"{i + 1}")

            current_dev = self.hal.get_active_device()
            self.devnum_combo.setCurrentIndex(current_dev - 1)
        else:
            self.devnum_combo.clear()
        self.closeLock.emit(connected)

    def _quickmove_changed(self, checked: bool):
        """Called when the quickmove checkbox is changed,
        sets visibility of the speed combobox."""
        if checked:
            self.settingsWidget.speedComboBox.setEnabled(False)
        else:
            self.settingsWidget.speedComboBox.setEnabled(True)

        self.hal.update_internal_state(self.quickmove_input.isChecked(), None, None)

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
        speed = int(speed_text.split(":")[0])
        self.hal.update_internal_state(None, speed, None)

    ## Button functionality:

    def _connect_button(self):
        """Called when the connect button is pressed. Opens the device and sets the connection indicator color."""
        try:
            if self.hal.is_connected():
                self.hal.close()
            else:
                self.hal.open(self.source_input.text())

        except Exception as e:
            self.logger.info_popup(f"Sutter connection error: {str(e)}")

        finally:
            if self.hal.is_connected():
                self._gui_change_device_connected(True)
                # self._move_worker.start()  # Removed move worker from public API

            else:
                self._gui_change_device_connected(False)

    def _status_button(self):
        pos = self.hal.get_current_position()
        status, state = self.mm_move(x=pos[0] + 1000)
        print(f"status: {status}, state: {state} for positive x move")
        status, state = self.mm_move(x=pos[0] - 1000)
        print(f"status: {status}, state: {state} for negative x move")
        status, state = self.mm_move(y=pos[1] + 1000)
        print(f"status: {status}, state: {state} for positive y move")
        status, state = self.mm_move(y=pos[1] - 1000)
        print(f"status: {status}, state: {state} for negative y move")
        status, state = self.mm_move(z=pos[2] + 1000)
        print(f"status: {status}, state: {state} for positive z move")
        status, state = self.mm_move(z=pos[2] - 1000)
        print(f"status: {status}, state: {state} for negative z move")
        status, state = self.mm_move_relative(x_change=1000, y_change=1000, z_change=1000)
        print(f"status: {status}, state: {state} for positive relative move")
        status, state = self.mm_move_relative(x_change=-1000, y_change=-1000, z_change=-1000)
        print(f"status: {status}, state: {state} for negative relative move")
        status, state = self.mm_zmove(z_change=1000, absolute=True)
        print(f"status: {status}, state: {state} for absolute z move down")
        status, state = self.mm_zmove(z_change=0, absolute=True)
        print(f"status: {status}, state: {state} for absolute z move up")
        status, state = self.mm_zmove(z_change=1000, absolute=False)
        print(f"status: {status}, state: {state} for relative z move down")
        status, state = self.mm_up_max()
        print(f"status: {status}, state: {state} for move to max z")

    def _stop_button(self):
        self.logger.info_popup("Stop button pressed WIP")
        # self._move_worker.stop()

    def _calibrate_button(self):
        self.hal.calibrate()

    ## hook functionality

    def _get_public_methods(self):
        """
        Returns a a list of public methods of the class.
        """
        # FIXME: magic constant in kind of a stupid place:
        prefix = "mm_"
        methods = {method: getattr(self, method) for method in dir(self) if callable(getattr(self, method)) and not method.startswith("__") and not method.startswith("_") and method.startswith(prefix)}
        return methods

    def _get_log_signal(self):
        """Returns the log signal."""
        return self.logger.logger_signal

    def _get_info_signal(self):
        """Returns the info signal."""
        return self.logger.info_popup_signal

    def _get_close_lock_signal(self):
        """Returns the close lock signal."""
        return self.closeLock

    ## function API
    def mm_open(self) -> tuple:
        """Open the device.

        Returns:
            status: tuple of (status, error message)
        """
        if self.hal.is_connected():
            return [0, {"Error message": "Sutter already connected"}]
        try:
            self.hal.open(self.source_input.text())
            self.parse_settings_widget()
            self._gui_change_device_connected(True)
            return [0, {"Error message": "Sutter connected"}]

        except Exception as e:
            return [4, {"Error message": "Sutter HW error", "Exception": str(e)}]

    def mm_change_active_device(self, dev_num: int):
        """Micromanipulator active device change.

        Args:
            *args: device number (1-4)

        Returns:
            Status: tuple of (status, error message)

        """
        try:
            # commented out since this will be called from a separate thread
            # self.devnum_combo.setCurrentIndex(dev_num - 1)
            if self.hal.change_active_device(dev_num):
                return [0, {"Error message": "Sutter device changed to " + str(dev_num)}]
            return [4, {"Error message": "Sutter device change error"}]

        except ValueError as e:
            return [1, {"Error message": "Value error in Sutter plugin", "Exception": str(e)}]
        except Exception as e:
            return [4, {"Error message": "Sutter HW error", "Exception": str(e)}]

    def mm_move(self, x=None, y=None, z=None):
        """Micromanipulator move.

        Args:
            *args: x, y, z
        """
        try:
            self.hal.move(x, y, z)
            return [0, {"Error message": "Sutter moved"}]
        except Exception as e:
            return [4, {"Error message": "Sutter HW error", "Exception": str(e)}]

    def mm_move_relative(self, x_change=0, y_change=0, z_change=0):
        """Micromanipulator move relative to the current position.

        Args:
            *args: x_change, y_change, z_change
        """
        try:
            (x, y, z) = self.hal.get_current_position()
            self.hal.move(x + x_change, y + y_change, z + z_change)
            return [0, {"Error message": "Sutter moved"}]
        except Exception as e:
            return [4, {"Error message": "Sutter HW error", "Exception": str(e)}]

    def mm_calibrate(self, all=False):
        if not all:
            try:
                _ = self.hal.calibrate()
                return [0, {"Error message": "Sutter calibrated"}]
            except Exception as e:
                return [4, {"Error message": "Sutter HW error", "Exception": str(e)}]

    def mm_stop(self):
        """Micromanipulator stop."""
        try:
            self.hal.stop()
            return [0, {"Error message": "Sutter stopped"}]
        except Exception as e:
            return [4, {"Error message": "Sutter HW error", "Exception": str(e)}]

    def mm_zmove(self, z_change, absolute=False):
        """Moves the micromanipulator in the z axis. If the move is out of bounds, it will return False.

        Args:
            z_change (float): change in z axis in micron (or absolute z position if absolute=True)
            absolute (bool): If True, z_change is treated as absolute z position

        Returns:
            status
        """
        try:
            (x, y, z) = self.hal.get_current_position()

            if absolute:
                # For absolute positioning, z_change is the target z position
                target_z = z_change
                if target_z > self.hal._MAXIMUM_M or target_z < self.hal._MINIMUM_MS:
                    return [1, {"Error message": "Sutter move out of bounds"}]
                self.hal.move(x, y, target_z)
                return [0, {"Error message": "Sutter moved"}]
            else:
                # For relative positioning, z_change is the offset
                target_z = z + z_change
                if target_z > self.hal._MAXIMUM_M or target_z < self.hal._MINIMUM_MS:
                    return [1, {"Error message": "Sutter move out of bounds"}]
                self.hal.move(x, y, target_z)
                return [0, {"Error message": "Sutter moved"}]
        except Exception as e:
            return [4, {"Error message": "Sutter HW error", "Exception": str(e)}]

    def mm_up_max(self):
        """DEPRECATED"""
        """Moves to z = 0"""
        try:
            x, y, z = self.hal.get_current_position()
            if z == 0:
                return [0, {"Error message": "Sutter already at max"}]
            self.hal.move(x, y, 0)
            return [0, {"Error message": "Sutter moved up to max"}]
        except Exception as e:
            return [4, {"Error message": "Sutter HW error", "Exception": str(e)}]

    def mm_current_position(self):
        """Returns the current position of the micromanipulator.

        Returns:
            tuple: (x, y, z) position in microns
        """
        try:
            return self.hal.get_current_position()
        except Exception as e:
            return [4, {"Error message": "Sutter HW error", "Exception": str(e)}]

    def mm_devices(self):
        """Returns the number of connected devices and their statuses.

        Returns:
            tuple: (number of devices, list of device statuses)
        """
        try:
            code, status = self.mm_open()  # Ensure the device is open before fetching statuses
            if code != 0:
                return [code, status]  # Return error if opening failed
            dev_count, dev_statuses = self.hal.get_connected_devices_status()
            return [0, (dev_count, dev_statuses)]
        except Exception as e:
            return [4, {"Error message": "Sutter HW error", "Exception": str(e)}]
