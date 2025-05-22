import os
from datetime import datetime

from Sutter import Mpc325
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QBrush, QImage, QPen, QPixmap
from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QMenu


class SutterGUI(QObject):
    """
    GUI implementation of the sutter microman plugin for pyIVLS.

    public API:

    - WRITE

    version 0.1
    2025.05.22
    otsoha
    """

    log_message = pyqtSignal(str)
    info_message = pyqtSignal(str)
    closeLock = pyqtSignal(bool)

    # FIXME: kinda stupid to import the names here.
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
        self.settingsWidget.connectButton.clicked.connect(self.connect_button)
        self.settingsWidget.statusButton.clicked.connect(self.status_button)
        self.settingsWidget.stopButton.clicked.connect(self.stop_button)
        self.settingsWidget.calibrateButton.clicked.connect(self.calibrate_button)
        self.settingsWidget.saveButton.clicked.connect(self.save_button)
        self.settingsWidget.quickBox.toggled.connect(self._quickmove_changed)

        # save input fields. Explicit typing here just so I get type hints in vscode
        self.quickmove_input: QtWidgets.QCheckBox = self.settingsWidget.quickBox
        self.source_input: QtWidgets.QLineEdit = self.settingsWidget.sourceInput
        self.speed_input: QtWidgets.QComboBox = self.settingsWidget.speedComboBox

        # fill combobox
        speeds = self.hal._MOVE_SPEEDS
        for speed_key, speed_value in speeds.items():
            self.speed_input.addItem(f"{speed_key}: {int(speed_value)} µm/s")

        # set default values, try to read from settings.
        quickmove = int(settings.get("quickmove", 0))
        self.quickmove_input.setChecked(bool(quickmove))
        self.source_input.setText(settings.get("address", ""))
        speed = int(settings.get("speed_idx", 0))
        self.speed_input.setCurrentIndex(speed)

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

        print(f"quick move: {quick_move}, speed: {speed}, source: {source}")

    def _gui_change_device_connected(self, status: bool):
        # NOTE: status is inverted, i.e. when preview is started received status should False, when preview is stopped status should be True
        if status:
            self.settingsWidget.connectionIndicator.setStyleSheet(
                "border-radius: 10px; background-color: rgb(165, 29, 45); min-height: 20px; min-width: 20px;"
            )
        else:
            self.settingsWidget.connectionIndicator.setStyleSheet(
                "border-radius: 10px; background-color: rgb(38, 162, 105); min-height: 20px; min-width: 20px;"
            )
        self.settingsWidget.sourceBox.setEnabled(status)
        self.closeLock.emit(not status)
        print("sutter emitted close lock signal ", not status)

    def _quickmove_changed(self, checked: bool):
        """Called when the quickmove checkbox is changed, 
        sets visibility of the speed combobox."""
        if checked:
            self.settingsWidget.speedComboBox.setEnabled(False)
        else:
            self.settingsWidget.speedComboBox.setEnabled(True)
    

    ## Button functionality:

    def connect_button(self):
        """Called when the connect button is pressed. Opens the device and sets the connection indicator color."""
        self.hal.open(self.source_input.text())
        if self.hal.is_connected():
            self._gui_change_device_connected(True)
            self.log_message.emit("Connected to Sutter micromanipulator")
        else:
            self._gui_change_device_connected(False)
            self.log_message.emit("Failed to connect to Sutter micromanipulator")


    def status_button(self):
        print("status button pressed")

    def stop_button(self):
        print("stop button pressed")

    def calibrate_button(self):
        print("calibrate button pressed")

    def save_button(self):
        self.parse_settings_widget()

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
            tuple: name, success
        """
        if self.hal.open():
            return (self.plugin_name, True)
        return (self.plugin_name, False)

    def mm_change_active_device(self, dev_num):
        """Micromanipulator active device change.

        Args:
            *args: device number
        """
        if self.hal.change_active_device(dev_num):
            return True
        return False

    def mm_move(self, x, y, z):
        """Micromanipulator move.

        Args:
            *args: x, y, z
        """
        if self.hal.move(x, y, z):
            return True
        return False

    def mm_stop(self):
        """Micromanipulator stop."""
        self.hal.stop()

    def mm_lower(self, z_change) -> bool:
        """Moves the micromanipulator in the z axis. If the move is out of bounds, it will return False.

        Args:
            z_change (float): change in z axis in micron

        Returns:
            bool: Moved or not
        """

        (x, y, z) = self.hal.get_current_position()
        if z + z_change > self.hal._MAXIMUM_M or z + z_change < self.hal._MINIMUM_MS:
            return False
        else:
            self.hal.slow_move_to(x, y, z + z_change, speed=0)
            return True
