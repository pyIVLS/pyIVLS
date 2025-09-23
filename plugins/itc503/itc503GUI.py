"""
This is a GUI plugin for itc503 for pyIVLS. The plugin is based on peltierController (version 0.2 from 2025.02.06)

This file should provide
- functions for interaction with other plugins (those that will be exported on get_functions hook call, these should not start with "_")
- functions that will implement functionality of the hooks (see pyIVLS_itc503)
- GUI functionality - code that interracts with Qt GUI elements from widgets

This plugin should have double functionality
(i) it may be independently used to set up and display the temperature
(ii) it provides functionality of settting up the temperature to external plugins

Because of (i) it requires to send log and message signals, i.e. it is a child of QObject

version 0.2
2025.05.13
ivarad
"""

import os
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from PyQt6 import uic
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from itc503 import itc503
from MplCanvas import MplCanvas  # this should be moved to some pluginsShare

# from mock import itc503  # for testing without the real device
import time


class itc503GUI(QObject):
    """itc503 controller"""

    non_public_methods = []  # add function names here, if they should not be exported as public to another plugins
    public_methods = [
        "parse_settings_widget",
        "setSettings",
        "getIterations",
        "loopingIteration",
    ]  # add function names here, necessary for descendents of QObject, otherwise _get_public_methods returns a lot of QObject methods
    ########Signals

    log_message = pyqtSignal(str)
    info_message = pyqtSignal(str)
    closeLock = pyqtSignal(bool)

    ########Functions
    def __init__(self):
        super(itc503GUI, self).__init__()
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep

        self.settingsWidget = uic.loadUi(self.path + "itc503_settingsWidget.ui")
        self.MDIWidget = uic.loadUi(self.path + "itc503_MDIWidget.ui")

        # Initialize the functionality core that should be independent on GUI
        self.itc503 = itc503()

        self._connect_signals()
        self._create_plt()

        # Set a timer for the temperature display
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_display)

    def _connect_signals(self):
        self.settingsWidget.connectButton.clicked.connect(self._connectAction)
        self.settingsWidget.disconnectButton.clicked.connect(self._disconnectAction)
        self.settingsWidget.setTButton.clicked.connect(self._setTAction)
        self.settingsWidget.periodCheck.clicked.connect(self._displayAction)

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
        self.settings["source"] = self.settingsWidget.source.text()
        try:
            self.itc503.open(self.settings["source"])
            self._GUIchange_deviceConnected(True)
            self.closeLock.emit(True)
            return [0, "OK"]
        except Exception as e:
            self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : itc503 plugin : {e}, status = 4")
            self.info_message.emit(f"itc503 plugin : {e}")
            return [e, {"Error message": f"{e}"}]

    def _disconnectAction(self):
        if self.timer.isActive():
            self.info_message.emit("itc503 plugin : stop temperture monitor before disconnecting")
            return [1, {"Error message": "Temperature monitor is running"}]
        else:
            try:
                self.itc503.close()
                self._GUIchange_deviceConnected(False)
                self.closeLock.emit(False)
                return [0, "OK"]
            except Exception as e:
                self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : itc503 plugin : {e}, status = 4")
                self.info_message.emit(f"itc503 plugin : {e}")
                return [4, {"Error message": f"{e}"}]

    def _setTAction(self):
        [status, info] = self._parse_settings_setT()
        if status:
            self.log_message.emit(
                datetime.now().strftime("%H:%M:%S.%f") + f" : itc503 plugin : {info}, status = {status}"
            )
            self.info_message.emit(f"itc503 plugin : {info}")
            return [status, info]
        [status, info] = self._setT()
        if status:
            self.log_message.emit(
                datetime.now().strftime("%H:%M:%S.%f") + f" : itc503 plugin : {info}, status = {status}"
            )
            self.info_message.emit(f"itc503 plugin : {info}")
            return [status, info]
        return [0, "OK"]

    def _displayAction(self):
        if self.timer.isActive():
            self.timer.stop()
            self._GUIchange_display(False)
        else:
            [status, info] = self._parse_settings_display()
            if status:
                self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : itc503 : {info}, status = {status}")
                self.info_message.emit(f"itc503 plugin : {info}")
            else:
                self.Xdata = []
                self.Ydata = []
                self.display_data = ""
                self._update_display()
                self.timer.start(self.settings["period"] * 1000)
                self._GUIchange_display(True)

    ########Functions
    ################################### internal

    def _parse_settings_source(self):
        self.settings = {}
        self.settings["source"] = self.settingsWidget.source.text()

        return [0, self.settings]

    def _parse_settings_setT(self):
        try:
            self.settings["sett"] = float(self.settingsWidget.setTEdit.text())
        except ValueError:
            return [
                1,
                {"Error message": "Value error: set temperature field should be numeric"},
            ]

        return [0, self.settings]

    def _parse_settings_display(self):
        try:
            self.settings["period"] = int(self.settingsWidget.periodEdit.text())
        except ValueError:
            return [
                1,
                {"Error message": "Value error: check period field should be integer"},
            ]
        if self.settings["period"] < 1:
            return [
                1,
                {"Error message": "Value error: check period field should be greater than 0"},
            ]

        try:
            self.settings["periodpts"] = int(self.settingsWidget.periodPtsEdit.text())
        except ValueError:
            return [
                1,
                {"Error message": "Value error: points to show field should be integer"},
            ]
        if self.settings["periodpts"] < 1:
            return [
                1,
                {"Error message": "Value error: points to show field should be greater than 0"},
            ]

        return [0, self.settings]

    def _update_display(self):
        try:
            info = self.itc503.getData()
        except Exception as e:
            self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : itc503 plugin : {e}, status = 4")
            self.info_message.emit(f"itc503 plugin : {e}")
            self.timer.stop()
            self._GUIchange_display(False)
            return [e, {"Error message": f"{e}"}]

        timeNow = datetime.now()
        if self.display_data.count("\n") == self.settings["periodpts"]:
            self.display_data = self.display_data[self.display_data.find("\n") + 1 :]
        self.display_data = self.display_data + timeNow.strftime("%H:%M:%S.%f") + f": {info}K\n"
        self.MDIWidget.outputEdit.clear()
        self.MDIWidget.outputEdit.append(self.display_data)
        temperature = info
        if not self.Xdata:
            self.axes.cla()
            self.Xdata = [timeNow]
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
            self.Xdata.append(timeNow)
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

    def _setT(self):
        try:
            self.itc503.setT(self.settings["sett"])
            return [0, "OK"]
        except Exception as e:
            return [4, {"Error message": f"{e}"}]

    ########Functions
    ###############GUI setting up

    def _initGUI(
        self,
        plugin_info: dict,
    ):
        """Initialize the GUI with the provided plugin information.

        Args:
            plugin_info (dict): A dictionary containing plugin settings.
        """
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK

        #### for example
        self.settingsWidget.source.setText(plugin_info["source"])
        self.settingsWidget.setTEdit.setText(plugin_info["sett"])
        self.settingsWidget.periodEdit.setText(plugin_info["period"])
        self.settingsWidget.periodPtsEdit.setText(plugin_info["periodpts"])
        self.settingsWidget.sweepStartEdit.setText(plugin_info["sweepstart"])
        self.settingsWidget.sweepEndEdit.setText(plugin_info["sweepend"])
        self.settingsWidget.sweepPtsEdit.setText(plugin_info["sweeppts"])
        self.settingsWidget.sweepStabilizationEdit.setText(plugin_info["sweepstabilization"])

    def _setGUIfromSettings(self):
        ##populates GUI with values stored in settings

        self.settingsWidget.source.setText(f"{self.settings['source']}")
        self.settingsWidget.setTEdit.setText(f"{self.settings['sett']}")
        self.settingsWidget.periodEdit.setText(f"{self.settings['period']}")
        self.settingsWidget.periodPtsEdit.setText(f"{self.settings['periodpts']}")
        self.settingsWidget.sweepStartEdit.setText(f"{self.settings['sweepstart']}")
        self.settingsWidget.sweepEndEdit.setText(f"{self.settings['sweepend']}")
        self.settingsWidget.sweepPtsEdit.setText(f"{self.settings['sweeppts']}")
        self.settingsWidget.sweepStabilizationEdit.setText(f"{self.settings['sweepstabilization']}")

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
            and method in self.public_methods
        }
        return methods

    def _getLogSignal(self):
        return self.log_message

    def _getInfoSignal(self):
        return self.info_message

    def _getCloseLockSignal(self):
        return self.closeLock

    def _get_current_gui_values(self):
        """Returns a dictionary with the current values of all input boxes in the settings widget."""
        values = {
            "source": self.settingsWidget.source.text(),
            "sett": self.settingsWidget.setTEdit.text(),
            "period": self.settingsWidget.periodEdit.text(),
            "periodpts": self.settingsWidget.periodPtsEdit.text(),
            "sweepstart": self.settingsWidget.sweepStartEdit.text(),
            "sweepend": self.settingsWidget.sweepEndEdit.text(),
            "sweeppts": self.settingsWidget.sweepPtsEdit.text(),
            "sweepstabilization": self.settingsWidget.sweepStabilizationEdit.text(),
        }
        return 0, values

        #########IRtodo: workaround, make a proper update display
        tic = time.time()
        while (time.time() - tic) < self.settings["sweepstabilization"]:
            try:
                info = self.itc503.getData()
            except Exception as e:
                return [4, {"Error message": f"{e}"}]
            print(info)
        return [0, f"_{info}K"]

    ########Functions to be used externally
    ###############get settings from GUI

    def parse_settings_widget(self):
        """Parses the settings widget for the plugin. Extracts current values. Checks if values are allowed. Provides settings of itc503 plugin to an external plugin

        Returns [status, settings_dict]:
            status: 0 - no error, ~0 - error (add error code later on if needed)
            self.settings
        """
        self._parse_settings_source()
        self._parse_settings_display()
        self._parse_settings_setT()

        try:
            self.settings["sweepstart"] = float(self.settingsWidget.sweepStartEdit.text())
        except ValueError:
            return [
                1,
                {"Error message": "Value error: sweep start field should be numeric"},
            ]

        try:
            self.settings["sweepend"] = float(self.settingsWidget.sweepEndEdit.text())
        except ValueError:
            return [
                1,
                {"Error message": "Value error: sweep end field should be numeric"},
            ]

        try:
            self.settings["sweeppts"] = int(self.settingsWidget.sweepPtsEdit.text())
        except ValueError:
            return [
                1,
                {"Error message": "Value error: sweep points field should be integer"},
            ]
        if self.settings["sweeppts"] < 1:
            return [
                2,
                {"Error message": "Value error: sweep points field should be greater than 0"},
            ]

        try:
            self.settings["sweepstabilization"] = int(self.settingsWidget.sweepStabilizationEdit.text())
        except ValueError:
            return [
                1,
                {"Error message": "Value error: stabilization time field should be integer"},
            ]
        if self.settings["sweepstabilization"] < 1:
            return [
                2,
                {"Error message": "Value error: stabilization time field should be greater than 0"},
            ]

        return [0, self.settings]

    def setSettings(self, settings):
        self.settings = settings

    # this function is called not from the main thread. Direct addressing of qt elements not from te main thread causes segmentation fault crash. Using a signal-slot interface between different threads should make it work
    #        self._setGUIfromSettings()

    ########Functions
    ########Tsweep implementation

    def getIterations(self):
        return self.settings["sweeppts"]

    def loopingIteration(self, iteration):
        if self.settings["sweeppts"] == 1:
            self.settings["sett"] = self.settings["sweepstart"]
        else:
            self.settings["sett"] = self.settings["sweepstart"] + iteration * (
                self.settings["sweepend"] - self.settings["sweepstart"]
            ) / (self.settings["sweeppts"] - 1)
        # this function is called not from the main thread. Direct addressing of qt elements not from te main thread causes segmentation fault crash. Using a signal-slot interface between different threads should make it work
        #        self.settingsWidget.setTEdit.setText(f"{self.settings['sett']}")
        [status, info] = self._setT()
        if status:
            return [status, info]
        #########IRtodo: workaround, make a proper update display
        tic = time.time()
        while (time.time() - tic) < self.settings["sweepstabilization"]:
            try:
                info = self.itc503.getData()
            except Exception as e:
                return [4, {"Error message": f"{e}"}]
            if abs(info - self.settings["sett"]) > 0.2:
                print(datetime.now().strftime("%H:%M:%S.%f") + f" wait for T. T={info} K")
                tic = time.time()
            else:
                print(datetime.now().strftime("%H:%M:%S.%f") + f" Stabilization period. T={info} K")
            time.sleep(20)
        return [0, f"_{info}K"]
