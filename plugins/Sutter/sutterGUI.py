import os
from datetime import datetime

from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QObject, pyqtSignal
from Sutter import Mpc325

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
        self.settingsWidget.speedComboBox.currentIndexChanged.connect(
            self.speed_changed
        )
        self.settingsWidget.devnumCombo.currentIndexChanged.connect(
            self._devnum_changed
        )

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
        quickmove = int(settings.get("quickmove", 0))
        self.quickmove_input.setChecked(bool(quickmove))
        source = settings.get("address", "")
        self.source_input.setText(source)
        speed = int(settings.get("speed_idx", 0))
        self.speed_input.setCurrentIndex(speed)

        # read the default settings from the GUI
        quickmove, speed, source = self.parse_settings_widget()
        self.hal.update_internal_state(quickmove, speed, source)

        self._gui_change_device_connected(self.hal.is_connected())

        return self.settingsWidget

    # GUI interactions

    def parse_settings_widget(self):
        """Parses the settings widget and sets the values in the class."""

        quick_move = False
        if self.quickmove_input.isChecked():
            quick_move = True

        speed_text = self.speed_input.currentText()
        speed = int(speed_text.split(":")[0])

        source = self.source_input.text()

        return quick_move, speed, source

    def _gui_change_device_connected(self, connected: bool):
        if connected:
            self.settingsWidget.connectionIndicator.setStyleSheet(
                "border-radius: 10px; background-color: rgb(38, 162, 105); min-height: 20px; min-width: 20px;"
            )

        else:
            self.settingsWidget.connectionIndicator.setStyleSheet(
                "border-radius: 10px; background-color: rgb(165, 29, 45); min-height: 20px; min-width: 20px;"
            )

        self.source_input.setEnabled(not connected)
        self.settingsWidget.connectButton.setText(
            "Disconnect" if connected else "Connect"
        )
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
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_message.emit(f"{timestamp}: Sutter error: {str(e)}")

        finally:
            if self.hal.is_connected():
                self._gui_change_device_connected(True)
            else:
                self._gui_change_device_connected(False)

    def _status_button(self):
        print("status button pressed WIP")
        pos = self.hal.get_current_position()
        print(f"Current position: {pos}")
        self.hal.move(pos[0] + 2000, pos[1], pos[2])

    def _stop_button(self):
        print("stop button pressed WIP")
        self.hal.stop()

    def _calibrate_button(self):
        print("calibrate button pressed WIP")
        self.hal.calibrate()

    ## hook functionality

    def _get_public_methods(self):
        """
        Returns a a list of public methods of the class.
        """
        # FIXME: magic constant in kind of a stupid place:
        prefix = "mm_"
        methods = {
            method: getattr(self, method)
            for method in dir(self)
            if callable(getattr(self, method))
            and not method.startswith("__")
            and not method.startswith("_")
            and method.startswith(prefix)
        }
        return methods

    def _get_log_signal(self):
        """Returns the log signal."""
        return self.log_message

    def _get_info_signal(self):
        """Returns the info signal."""
        return self.info_message

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
            if self.hal.is_connected():
                self._gui_change_device_connected(True)
                return [0, {"Error message": "Sutter connected"}]
            return [4, {"Error message": "Sutter connection error"}]

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
            self.devnum_combo.setCurrentIndex(dev_num - 1)
            if self.hal.change_active_device(dev_num):
                return [
                    0,
                    {"Error message": "Sutter device changed to " + str(dev_num)},
                ]
            return [4, {"Error message": "Sutter device change error"}]

        except ValueError as e:
            return [
                1,
                {"Error message": "Value error in Sutter plugin", "Exception": str(e)},
            ]
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

    def mm_stop(self):
        """Micromanipulator stop."""
        try:
            self.hal.stop()
            return [0, {"Error message": "Sutter stopped"}]
        except Exception as e:
            return [4, {"Error message": "Sutter HW error", "Exception": str(e)}]

    def mm_zmove(self, z_change):
        """Moves the micromanipulator in the z axis. If the move is out of bounds, it will return False.

        Args:
            z_change (float): change in z axis in micron

        Returns:
            status
        """
        try:
            (x, y, z) = self.hal.get_current_position()
            if (
                z + z_change > self.hal._MAXIMUM_M
                or z + z_change < self.hal._MINIMUM_MS
            ):
                return [1, {"Error message": "Sutter move out of bounds"}]
            else:
                self.hal.move(x, y, z + z_change)
                return [0, {"Error message": "Sutter moved"}]
        except Exception as e:
            return [4, {"Error message": "Sutter HW error", "Exception": str(e)}]
        
    def mm_up_max(self):
        """Moves to z = 0 
        """
        try:
            x,y,z = self.hal.get_current_position()
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
        

