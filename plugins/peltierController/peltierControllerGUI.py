"""
This is a GUI plugin for peltierController for pyIVLS

This file should provide
- functions for interaction with other plugins (those that will be exported on get_functions hook call, these should not start with "_")
- functions that will implement functionality of the hooks (see pyIVLS_peltierController)
- GUI functionality - code that interracts with Qt GUI elements from widgets

This plugin should have double functionality
(i) it may be independently used to set up and display the temperature
(ii) it provides functionality of settting up the temperature to external plugins

Because of (i) it requires to send log and message signals, i.e. it is a child of QObject

version 0.2
2025.02.06
ivarad
"""

import os
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from PyQt6 import uic
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from peltierController import peltierController
from MplCanvas import MplCanvas  # this should be moved to some pluginsShare


class peltierControllerGUI(QObject):
    """Peltier element controller"""

    non_public_methods = []  # add function names here, if they should not be exported as public to another plugins
    ########Signals

    log_message = pyqtSignal(str)
    info_message = pyqtSignal(str)

    ########Functions
    def __init__(self):
        super(peltierControllerGUI, self).__init__()
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep

        self.settingsWidget = uic.loadUi(self.path + "peltierController_settingsWidget.ui")
        self.MDIWidget = uic.loadUi(self.path + "peltierController_MDIWidget.ui")

        # Initialize the functionality core that should be independent on GUI
        self.peltierController = peltierController()

        self._connect_signals()
        self._create_plt()

        # Set a timer for the temperature display
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_display)

    def _connect_signals(self):
        self.settingsWidget.connectButton.clicked.connect(self._connectAction)
        self.settingsWidget.disconnectButton.clicked.connect(self._disconnectAction)
        self.settingsWidget.setTButton.clicked.connect(self._setTAction)
        self.settingsWidget.setPButton.clicked.connect(self._setPAction)
        self.settingsWidget.periodCheck.clicked.connect(self._displayAction)
        self.settingsWidget.PIDbutton.clicked.connect(self._setPIDAction)

    def _create_plt(self):
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.axes = self.sc.fig.add_subplot(111)
        self.axes.set_xlabel("time (HH:MM)")

        degree_sign = "\N{DEGREE SIGN}"
        self.axes.set_ylabel(f"Temperature ({degree_sign}C)")

        self.MDIWidget.displayLayout.addWidget(self.sc._create_toolbar(self.MDIWidget))
        self.MDIWidget.displayLayout.addWidget(self.sc)

    ########Functions
    ########GUI Slots
    def _connectAction(self):
        self._parse_settings_source()
        self.settings["source"] = self.settingsWidget.peltierSource.text()
        [status, message] = self.peltierController.open(self.settings["source"])
        if status:
            self.log_message.emit(
                datetime.now().strftime("%H:%M:%S.%f") + f" : peltierController plugin : {message}, status = {status}"
            )
            self.info_message.emit(f"peltierController plugin : {message}")
        else:
            self._GUIchange_deviceConnected(True)

    def _disconnectAction(self):
        if self.timer.isActive():
            self._displayAction()
        [status, message] = self.peltierController.close()
        if status:
            self.log_message.emit(
                datetime.now().strftime("%H:%M:%S.%f") + f" : peltierController plugin : {message}, status = {status}"
            )
            self.info_message.emit(f"peltierController plugin : {message}")
        else:
            self._GUIchange_deviceConnected(False)

    def _setTAction(self):
        [status, info] = self._parse_settings_setT()
        if status:
            self.info_message.emit(f"peltierController plugin : {info}")
        else:
            [status, message] = self.peltierController.setT(self.settings["sett"])
            if status:
                self.log_message.emit(
                    datetime.now().strftime("%H:%M:%S.%f")
                    + f" : peltierController plugin : {message}, status = {status}"
                )
                self.info_message.emit(f"peltierController plugin : {message}")

    def _setPAction(self):
        [status, info] = self._parse_settings_setP()
        if status:
            self.info_message.emit(f"peltierController plugin : {info}")
        else:
            [status, message] = self.peltierController.setP(self.settings["setp"])
            if status:
                self.log_message.emit(
                    datetime.now().strftime("%H:%M:%S.%f")
                    + f" : peltierController plugin : {message}, status = {status}"
                )
                self.info_message.emit(f"peltierController plugin : {message}")

    def _setPIDAction(self):
        [status, info] = self._parse_settings_setPID()
        if status:
            self.info_message.emit(f"peltierController plugin : {info}")
        else:
            [status, message] = self.peltierController.setPID(
                self.settings["kp"], self.settings["ki"], self.settings["kd"]
            )
            if status:
                self.log_message.emit(
                    datetime.now().strftime("%H:%M:%S.%f")
                    + f" : peltierController plugin : {message}, status = {status}"
                )
                self.info_message.emit(f"peltierController plugin : {message}")

    def _displayAction(self):
        if self.timer.isActive():
            self.timer.stop()
            self._GUIchange_display(False)
        else:
            [status, info] = self._parse_settings_display()
            if status:
                self.info_message.emit(f"peltierController plugin : {info}")
                self.log_message.emit(
                    datetime.now().strftime("%H:%M:%S.%f") + f" : peltierController plugin : {info}, status = {status}"
                )
            else:
                self.Xdata = []
                self.Ydata = []
                self._update_display()
                self.timer.start(self.settings["period"] * 1000)
                self._GUIchange_display(True)

    ########Functions
    ################################### internal

    def _parse_settings_source(self):
        self.settings = {}
        self.settings["source"] = self.settingsWidget.peltierSource.text()

        return [0, self.settings]

    def _parse_settings_setT(self):
        try:
            self.settings["sett"] = float(self.settingsWidget.setTEdit.text())
        except ValueError:
            return [1, {"Error message": "Value error: set temperature field should be numeric"}]

        return [0, self.settings]

    def _parse_settings_setP(self):
        try:
            self.settings["setp"] = float(self.settingsWidget.setPEdit.text())
        except ValueError:
            return [1, {"Error message": "Value error: set power field should be numeric"}]
        if abs(self.settings["setp"]) > 100:
            return [1, {"Error message": "Value error: set power field can not be larger than 100"}]

        return [0, self.settings]

    def _parse_settings_setPID(self):
        try:
            self.settings["kp"] = float(self.settingsWidget.KPlineEdit.text())
        except ValueError:
            return [1, {"Error message": "Value error: Kp field should be numeric"}]
        try:
            self.settings["ki"] = float(self.settingsWidget.KIlineEdit.text())
        except ValueError:
            return [1, {"Error message": "Value error: Ki field should be numeric"}]
        try:
            self.settings["kd"] = float(self.settingsWidget.KDlineEdit.text())
        except ValueError:
            return [1, {"Error message": "Value error: Kd field should be numeric"}]

        return [0, self.settings]

    def _parse_settings_display(self):
        try:
            self.settings["period"] = int(self.settingsWidget.periodEdit.text())
        except ValueError:
            return [1, {"Error message": "Value error: check period field should be integer"}]
        if self.settings["period"] < 1:
            return [1, {"Error message": "Value error: check period field should be greater than 0"}]

        try:
            self.settings["periodpts"] = int(self.settingsWidget.periodPtsEdit.text())
        except ValueError:
            return [1, {"Error message": "Value error: points to show field should be integer"}]
        if self.settings["periodpts"] < 1:
            return [1, {"Error message": "Value error: points to show field should be greater than 0"}]

        return [0, self.settings]

    def _update_display(self):
        [status, info] = self.peltierController.getData()
        if status:
            self.log_message.emit(
                datetime.now().strftime("%H:%M:%S.%f") + f" : peltierController plugin : {info}, status = {status}"
            )
            self.info_message.emit(f"peltierController plugin : {info}")
            self.timer.stop()
        else:
            self.MDIWidget.peltierOutputEdit.clear()
            self.MDIWidget.peltierOutputEdit.append(info["raw"])
            temperature = info["T1"]
            if not self.Xdata:
                self.axes.cla()
                self.Xdata = [datetime.now()]
                self.Ydata = [temperature]
                plot_refs = self.axes.plot(self.Xdata, self.Ydata, "bo")
                self.axes.set_xlabel("time (HH:MM)")
                degree_sign = "\N{DEGREE SIGN}"
                self.axes.set_ylabel(f"Temperature ({degree_sign}C)")
                self._plot_temperature = plot_refs[0]
                self.axes.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                self.axes.set_xlim(
                    self.Xdata[-1] - timedelta(seconds=self.settings["period"]),
                    self.Xdata[-1] + timedelta(seconds=self.settings["period"]) * self.settings["periodpts"],
                )
            else:
                self.Xdata.append(datetime.now())
                self.Ydata.append(temperature)
                self._plot_temperature.set_xdata(self.Xdata)
                self._plot_temperature.set_ydata(self.Ydata)
                if len(self.Xdata) > self.settings["periodpts"]:
                    self.axes.set_xlim(
                        self.Xdata[-1] - timedelta(seconds=self.settings["period"] * self.settings["periodpts"]),
                        self.Xdata[-1] + timedelta(seconds=self.settings["period"]),
                    )
            self.axes.set_ylim(min(self.Ydata) - 10, max(self.Ydata) + 10)  # +/- 10 just a random margin for plotting
            self.sc.draw()

    ########Functions
    ###############GUI setting up

    def _initGUI(self, plugin_info: dict) -> None:
        """Initialize the GUI components with the provided plugin information.

        Args:
            plugin_info (dict): dictionary with settings obtained from plugin_data in pyIVLS_*_plugin
        """
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK

        #### for example
        self.settingsWidget.peltierSource.setText(plugin_info["source"])
        self.settingsWidget.setTEdit.setText(plugin_info["sett"])
        self.settingsWidget.setPEdit.setText(plugin_info["setp"])
        self.settingsWidget.periodEdit.setText(plugin_info["period"])
        self.settingsWidget.periodPtsEdit.setText(plugin_info["periodpts"])
        self.settingsWidget.sweepStartEdit.setText(plugin_info["sweepstart"])
        self.settingsWidget.sweepEndEdit.setText(plugin_info["sweepend"])
        self.settingsWidget.sweepPtsEdit.setText(plugin_info["sweeppts"])
        self.settingsWidget.sweepStabilizationEdit.setText(plugin_info["sweepstabilization"])
        self.settingsWidget.KPlineEdit.setText(plugin_info["pidkp"])
        self.settingsWidget.KIlineEdit.setText(plugin_info["pidki"])
        self.settingsWidget.KDlineEdit.setText(plugin_info["pidkd"])

    ########Functions
    ###############GUI react to change

    def _GUIchange_deviceConnected(self, status):
        if status:
            self.settingsWidget.connectionIndicator.setStyleSheet(
                "border-radius: 10px; background-color: rgb(38, 162, 105); min-height: 20px; min-width: 20px;"
            )
        else:
            self.settingsWidget.connectionIndicator.setStyleSheet(
                "border-radius: 10px; background-color: rgb(165, 29, 45); min-height: 20px; min-width: 20px;"
            )
        self.settingsWidget.settingsGroupBox.setEnabled(status)
        self.settingsWidget.DisplayGroupBox.setEnabled(status)
        self.settingsWidget.disconnectButton.setEnabled(status)
        self.settingsWidget.connectButton.setEnabled(not (status))
        self.settingsWidget.setTButton.setEnabled(status)
        self.settingsWidget.setPButton.setEnabled(status)
        self.settingsWidget.PIDbox.setEnabled(status)

    def _GUIchange_display(self, status):
        if status:
            self.settingsWidget.periodCheck.setText("Stop check")
        else:
            self.settingsWidget.periodCheck.setText("Start check")

    ########Functions
    ########plugins interraction

    def _get_public_methods(self):
        """
        Returns a nested dictionary of public methods for the plugin
        """
        # if the plugin type matches the requested type, return the functions

        methods = {
            method: getattr(self, method)
            for method in dir(self)
            if callable(getattr(self, method))
            and not method.startswith("__")
            and not method.startswith("_")
            and method not in self.non_public_methods
        }
        return methods

    def _getLogSignal(self):
        return self.log_message

    def _getInfoSignal(self):
        return self.info_message

    ########Functions to be used externally
    ###############get settings from GUI

    def parse_settings_widget(self):
        """Parses the settings widget for the plugin. Extracts current values. Checks if values are allowed. Provides settings of peltierController plugin to an external plugin

        Returns [status, settings_dict]:
            status: 0 - no error, ~0 - error (add error code later on if needed)
            self.settings
        """
        self._parse_settings_source()

        try:
            self.settings["sweepstart"] = float(self.settingsWidget.sweepStartEdit.text())
        except ValueError:
            return [1, {"Error message": "Value error: sweep start field should be numeric"}]

        try:
            self.settings["sweepend"] = float(self.settingsWidget.sweepEndEdit.text())
        except ValueError:
            return [1, {"Error message": "Value error: sweep end field should be numeric"}]

        try:
            self.settings["sweeppts"] = int(self.settingsWidget.periodPtsEdit.text())
        except ValueError:
            return [1, {"Error message": "Value error: sweep points field should be integer"}]
        if self.settings["sweeppts"] < 1:
            return [2, {"Error message": "Value error: sweep points field should be greater than 0"}]

        try:
            self.settings["sweepstabilization"] = int(self.settingsWidget.periodEdit.text())
        except ValueError:
            return [1, {"Error message": "Value error: stabilization time field should be integer"}]
        if self.settings["sweepstabilization"] < 1:
            return [2, {"Error message": "Value error: stabilization time field should be greater than 0"}]

        return [0, self.settings]


########Functions
########Tsweep implementation
