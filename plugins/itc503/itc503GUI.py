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
from PyQt6.QtWidgets import QVBoxLayout, QFileDialog
from itc503 import itc503
from MplCanvas import MplCanvas  # this should be moved to some pluginsShare
from worker_thread import WorkerThread
from threadStopped import ThreadStopped, thread_with_exception
import numpy as np

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
    arrayT = []
    arraytemp = []
    runningFlag = False
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
        self.settings = {}
        self._create_plt()
        # Set a timer for the temperature display
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_display)

    def _connect_signals(self):
        self.settingsWidget.connectButton.clicked.connect(self._connectAction)
        self.settingsWidget.disconnectButton.clicked.connect(self._disconnectAction)
        self.settingsWidget.setTButton.clicked.connect(self._setTAction)
        self.settingsWidget.directoryButton.clicked.connect(self._getAddress)
        self.settingsWidget.periodCheck.clicked.connect(self._displayAction)
        self.settingsWidget.saveButton.clicked.connect(self._createFile)


    def _create_plt(self):
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.axes = self.sc.fig.add_subplot(111)
        self.axes.set_xlabel("time (s)")
        self.axes.set_ylabel("Temperature (K)")
        self.axes.set_ylim(0, 350) 
        
        #self.axes.text(0.9, 0.1, f'{self.arraytemp[-1]}', dict(size=20))
        layout = QVBoxLayout()
        layout.addWidget(self.sc._create_toolbar(self.MDIWidget))
        layout.addWidget(self.sc)
        self.MDIWidget.setLayout(layout)
        #self._GUIchange_deviceConnected(True)

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
        """if self.timer.isActive():
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
                self._GUIchange_display(True)"""
        [status, info] = self._parse_settings_display()
        if self.timer.isActive():
            self.timer.stop()
            return [1, "Running already"]
        if status:
            self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : itc503 : {info}, status = {status}")
            self.info_message.emit(f"itc503 plugin : {info}")
        else:
            self.run_thread = thread_with_exception(self._run_check)
            self.run_thread.start()
            self.runningFlag = True
            
            
            #self._GUIchange_display(True)

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

    def _parse_settings_save(self):
        self.settings["filename"] = self.settingsWidget.fileNameLine.text()
        self.settings["comment"] = self.settingsWidget.commentLine.text()
        self.settings["samplename"] = self.settingsWidget.sampleNameLine.text()
        self.settings["address"] = self.settingsWidget.addressLine.text()
        self.settings["log"] = self.settingsWidget.logCheckBox.isChecked()
        self.settings["wholetime"] = self.settingsWidget.logWholeBox.isChecked()
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





    def _run_check(self):
        timeNow = time.time()
        #timeDelta = 0  add in the future
        points = int(self.settings["periodpts"]/self.settings["period"])
        for i in range(points):
            self.arraytemp.append(self.itc503.getData())
            self.arrayT.append(time.time() - timeNow)
            self._render_mdi()
            time.sleep(self.settings["period"])
        self.runningFlag = False
        self._createFileLoop()
        self.run_thread.thread_stop()
    
    def _run_check_long(self):
        timeNow = time.time()
        #timeDelta = 0  add in the future
        points = int(3600/self.settings["period"])
        for i in range(points):
            self.arraytemp.append(self.itc503.getData())
            self.arrayT.append(time.time() - timeNow)
            self._render_mdi()
            time.sleep(self.settings["period"])
        self.runningFlag = False
        self._createFileLoop()
        self.run_thread.thread_stop()

    

    def _render_mdi(self):
        xmin, xmax = self.axes.get_xlim()
        ymin, ymax = self.axes.get_ylim()
        xmax = max(self.arrayT)
        self.axes.cla()
        self.axes.set_xlabel("time (HH:MM)")
        self.axes.set_ylabel("Temperature (K)")
        self.axes.plot(self.arrayT, self.arraytemp, "o")
        self.axes.set_xlim(xmin, xmax)
        self.axes.set_ylim(ymin, ymax)
        self.axes.set_title(f'T = {self.arraytemp[-1]} K')
        self.sc.draw()
        return [0]


    def _update_display(self):
        xmin, xmax = self.axes.get_xlim()
        ymin, ymax = self.axes.get_ylim()
        self.axes.cla()
        self.axes.set_xlabel("Wavelength (nm)")
        self.axes.set_ylabel("Intensity (calib. arb. un.)")
        self.axes.plot(self.arrayT, self.arraytemp, "b-")
        self.axes.set_xlim(xmin, xmax)
        self.axes.set_ylim(ymin, ymax)
        self.sc.draw()
        return [0]

    def _setT(self):
        try:
            self.itc503.setT(self.settings["sett"])
            return [0, "OK"]
        except Exception as e:
            return [4, {"Error message": f"{e}"}]

    ####Functions to do with saving
    def _getAddress(self):
        address = self.settingsWidget.addressLine.text()
        if not (os.path.exists(address)):
            address = self.path
        address = QFileDialog.getExistingDirectory(
            None,
            "Select directory for saving",
            address,
            options=QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks,
        )
        if address:
            self.settingsWidget.addressLine.setText(address)


    def _createFile(self):
        fileheader = self._itcMakeHeader()

        saveAddress = self.settingsWidget.addressLine.text() + os.path.sep + self.settingsWidget.fileNameLine.text()+".txt"
        np.savetxt(
            saveAddress,
            list(zip(self.arrayT, self.arraytemp)),
            fmt="%.9e",
            delimiter=";",
            newline="\n",
            header=fileheader,
            footer="#[EndOfFile]",
            comments="#",
        )
    def _createFileLoop(self):
        fileheader = self._itcMakeHeader()

        saveAddress = self.settings["address"] + os.path.sep + self.settings["filename"] + str(self.arrayT[1]) + "K" + ".txt"
        np.savetxt(
            saveAddress,
            list(zip(self.arrayT, self.arraytemp)),
            fmt="%.9e",
            delimiter=";",
            newline="\n",
            header=fileheader,
            footer="#[EndOfFile]",
            comments="#",
        )
        

    def _itcMakeHeader(self):
        ###following the structure of files generated by Thorlabs software
        ### a part of values are just const, they may be replaces with real values
        #
        # structure of the varDict
        #
        # varDict['average'] - int:averaging
        # varDict['integrationtime'] - float:integration time in seconds
        # varDict['triggermode'] - external trigger = 1 / internal = 0
        # varDict['name'] - str:sample name
        # varDict['comment'] - str:comment
        comment = "ITC403 operated by pyIVSL\n"
        comment = f"{comment}#[SpectrumHeader]\n"
        comment = f"{comment}Date;{datetime.now().strftime('%Y%m%d')}\n"
        comment = f"{comment}Time;{datetime.now().strftime('%H%M%S%f')[:-4]}\n"
        comment = f"{comment}GMTTime;{datetime.utcnow().strftime('%H%M%S%f')[:-4]}\n"
        comment = f"{comment}XAxisUnit;time(s)\n"
        comment = f"{comment}YAxisUnit;temperature(K)\n"
        comment = f"{comment}Average;0\n"
        comment = f"{comment}RollingAverage;0\n"
        comment = f"{comment}SpectrumSmooth;0\n"
        comment = f"{comment}SSmoothParam1;0\n"
        comment = f"{comment}SSmoothParam2;0\n"
        comment = f"{comment}SSmoothParam3;0\n"
        comment = f"{comment}SSmoothParam4;0\n"
        comment = f"{comment}IntegrationTime;0\n"
        comment = f"{comment}TriggerMode;0\n"
        comment = f"{comment}InterferometerSerial;M00903839\n"
        comment = f"{comment}Source\n"
        comment = f"{comment}AirMeasureOpt;0\n"
        comment = f"{comment}WnrMin;0\n"
        comment = f"{comment}WnrMax;0\n"
        comment = f"{comment}Length;3648\n"
        comment = f"{comment}Resolution;0\n"
        comment = f"{comment}ADC;0\n"
        comment = f"{comment}Instrument;0\n"
        comment = f"{comment}Model;itc503 smart \n"
        comment = f"{comment}Type;emission\n"
        comment = f"{comment}AirTemp;0\n"
        comment = f"{comment}AirPressure;0\n"
        comment = f"{comment}AirRelHum;0\n"
        comment = f"{comment}Name;{self.settings['samplename']}\n"
        comment = f"{comment}Comment;{self.settings['comment']}\n"
        comment = f"{comment}#[Data]\n"
        return comment



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
        self.settingsWidget.addressLine.setText(plugin_info["address"])
        self.settingsWidget.sampleNameLine.setText(plugin_info["samplename"])
        self.settingsWidget.commentLine.setText(plugin_info["comment"])
        self.settingsWidget.fileNameLine.setText(plugin_info["filename"])
        self.settingsWidget.logCheckBox.setChecked(False)
        self.settingsWidget.logWholeBox.setChecked(False)


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
        self._parse_settings_save()
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
        if self.runningFlag:
            self.run_thread.thread_stop()
            self._createFileLoop()
            self.runningFlag = False
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
        if self.settings["log"]:
            if self.settings["wholetime"]:
                self.run_thread = thread_with_exception(self._run_check_long)
                self.run_thread.start()
            else:
                self.run_thread = thread_with_exception(self._run_check)
                self.run_thread.start()
            self.runningFlag = True
        return [0, f"_{info}K"]

    """def loopingIteration(self, iteration): # test
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
        return [0, f"_{info}K"]"""
