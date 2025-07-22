"""
This is a GUI plugin for connection detecor multiplexor for pyIVLS

The main idea of the multiplexor is to be able to check the resistance between sense and current wires in 4 wire measurement to detect the connection.

This file should provide
- functions for interaction with other plugins (those that will be exported on get_functions hook call, these should not start with "_")
- functions that will implement functionality of the hooks (see pyIVLS_conDetect)
- GUI functionality - code that interracts with Qt GUI elements from widgets

This plugin should have double functionality
(i) it may be independently used to run camera preview
(ii) it provides functionality of getting images for other plugins

Because of (i) it requires to send log and message signals, i.e. it is a child of QObject

version 0.2
2025.05.12
ivarad
"""

import os
from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6 import uic

from conDetect import conDetect


class conDetectGUI(QObject):
    non_public_methods = []  # add function names here, if they should not be exported as public to another plugins
    public_methods = []  # add function names here, necessary for descendents of QObject, otherwise _get_public_methods returns a lot of QObject methods

    ########Signals

    log_message = pyqtSignal(str)
    info_message = pyqtSignal(str)
    closeLock = pyqtSignal(bool)

    ########Functions

    def __init__(self):
        super(conDetectGUI, self).__init__()  ### this is needed if the class is a child of QObject
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep

        self.settingsWidget = uic.loadUi(self.path + "conDetect_settingsWidget.ui")

        # Initialize the functionality core that should be independent on GUI
        self.functionality = conDetect()

        self._connect_signals()

        self.settings = {}

        self.connected = False
        self.hiCheck = False
        self.loCheck = False

    def _connect_signals(self):
        # Connect widget buttons to functions
        self.settingsWidget.connectButton.clicked.connect(self._connectAction)
        self.settingsWidget.disconnectButton.clicked.connect(self._disconnectAction)
        self.settingsWidget.hiConnectionButton.clicked.connect(self._hiConnectionCheck)
        self.settingsWidget.loConnectionButton.clicked.connect(self._loConnectionCheck)

    ########Functions
    ################################### internal

    def parse_settings_widget(self) -> "status":
        """Parses the settings widget for the conDetect. Extracts current values

        Returns:
            0 - no error
            ~0 - error (add error code later on if needed)
        """
        self.settings["source"] = self.settingsWidget.sourceLine.text()
        ##no value checks are possible here as the source should be just address and exposure is given by a set of values
        return [0, self.settings]

    ########Functions
    ########GUI Slots

    def _connectAction(self):
        self.parse_settings_widget()
        # try to open device
        [status, info] = self.deviceConnect()
        if status:
            self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : conDetect plugin :  {info}, status = {status}")
            self.info_message.emit(f"conDetect plugin : {info['Error message']}")
            return
        self.connected = True
        self._GUIchange_deviceConnected(self.connected)
        self.closeLock.emit(self.connected)

    def _disconnectAction(self):
        [status, info] = self.deviceDisconnect()
        self.connected = False
        self._GUIchange_deviceConnected(self.connected)
        self.closeLock.emit(self.connected)
        if status:
            self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : conDetect plugin :  {info}, status = {status}")
            self.info_message.emit(f"conDetect plugin : {info['Error message']}")
            self.settingsWidget.connectButton.setEnabled(self.connected)

    def _hiConnectionCheck(self):
        if self.loCheck:
            self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : conDetect plugin :  {'Error message':'Simultaneous check of Hi and Lo not permitted'}, status = 1")
            self.info_message.emit(f"conDetect plugin : {info['Simultaneous check of Hi and Lo not permitted']}")
        else:
            [status, info] = self.deviceHiCheck(not self.hiCheck)
            if status:
                self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : conDetect plugin :  {info}, status = {status}")
                self.info_message.emit(f"conDetect plugin : {info['Error message']}")
                return [status, info]
            else:
                self.hiCheck = not self.hiCheck
                return [0, "OK"]

    def _loConnectionCheck(self):
        if self.hiCheck:
            self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : conDetect plugin :  {'Error message':'Simultaneous check of Hi and Lo not permitted'}, status = 1")
            self.info_message.emit(f"conDetect plugin : {info['Simultaneous check of Hi and Lo not permitted']}")
        else:
            [status, info] = self.deviceLoCheck(not self.loCheck)
            if status:
                self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : conDetect plugin :  {info}, status = {status}")
                self.info_message.emit(f"conDetect plugin : {info['Error message']}")
                return [status, info]
            else:
                self.loCheck = not self.loCheck
                return [0, "OK"]

    ########Functions
    ###############GUI setting up

    def _initGUI(
        self,
        plugin_info: "dictionary with settings obtained from plugin_data in pyIVLS_*_plugin",
    ):
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK
        self.settingsWidget.sourceLine.setText(plugin_info["source"])

    ########Functions
    ###############GUI react to change

    def _GUIchange_deviceConnected(self, status):
        # NOTE: status is inverted, i.e. when preview is started received status should False, when preview is stopped status should be True
        if status:
            self.settingsWidget.connectionIndicator.setStyleSheet("border-radius: 10px; background-color: rgb(38, 162, 105); min-height: 20px; min-width: 20px;")
        else:
            self.settingsWidget.connectionIndicator.setStyleSheet("border-radius: 10px; background-color: rgb(165, 29, 45); min-height: 20px; min-width: 20px;")
        self.settingsWidget.sourceText.setEnabled(not status)
        self.settingsWidget.sourceLabel.setEnabled(not status)
        self.settingsWidget.sourceLine.setEnabled(not status)
        self.settingsWidget.connectButton.setEnabled(not status)
        self.settingsWidget.disconnectButton.setEnabled(status)
        self.settingsWidget.statusBox.setEnabled(status)

    ########Functions
    ########plugins interraction

    def _get_public_methods(self):
        """
        Returns a nested dictionary of public methods for the plugin
        """
        # if the plugin type matches the requested type, return the functions

        methods = {method: getattr(self, method) for method in dir(self) if callable(getattr(self, method)) and not method.startswith("__") and not method.startswith("_") and method not in self.non_public_methods and method in self.public_methods}
        return methods

    def _getLogSignal(self):
        return self.log_message

    def _getInfoSignal(self):
        return self.info_message

    def _getCloseLockSignal(self):
        return self.closeLock

    ########Functions
    ########device functions

    def deviceConnect(self):
        status, state = self.parse_settings_widget()
        if status:
            return [status, {"Error message": f"{state}"}]
        if self.settings.get("source", "") == "":
            return [1, {"Error message": "Source address is empty"}]
        try:
            self.functionality.connect(self.settings["source"])
            self.functionality.setDefault()
            self.connected = True
            self._GUIchange_deviceConnected(self.connected)
            return [0, "OK"]
        except Exception as e:
            return [4, {"Error message": f"{e}"}]

    def deviceDisconnect(self):
        try:
            self.functionality.setDefault()
            self.settingsWidget.hiConnectionIndicator.setStyleSheet("border-radius: 10px; background-color: rgb(165, 29, 45); min-height: 20px; min-width: 20px;")  # red
            self.settingsWidget.loConnectionIndicator.setStyleSheet("border-radius: 10px; background-color: rgb(165, 29, 45); min-height: 20px; min-width: 20px;")  # red
            self.functionality.disconnect()
            self.connected = False
            self._GUIchange_deviceConnected(self.connected)
            return [0, "OK"]
        except Exception as e:
            return [4, {"Error message": f"{e}"}]

    def deviceHiCheck(self, status):
        try:
            self.functionality.hiCheck(status)
            if status:
                self.settingsWidget.hiConnectionIndicator.setStyleSheet("border-radius: 10px; background-color: rgb(38, 162, 105); min-height: 20px; min-width: 20px;")  # green
            else:
                self.settingsWidget.hiConnectionIndicator.setStyleSheet("border-radius: 10px; background-color: rgb(165, 29, 45); min-height: 20px; min-width: 20px;")  # red
            return [0, "OK"]
        except Exception as e:
            return [4, {"Error message": f"{e}"}]

    def deviceLoCheck(self, status):
        try:
            self.functionality.loCheck(status)
            if status:
                self.settingsWidget.loConnectionIndicator.setStyleSheet("border-radius: 10px; background-color: rgb(38, 162, 105); min-height: 20px; min-width: 20px;")
            else:
                self.settingsWidget.loConnectionIndicator.setStyleSheet("border-radius: 10px; background-color: rgb(165, 29, 45); min-height: 20px; min-width: 20px;")
            return [0, "OK"]
        except Exception as e:
            return [4, {"Error message": f"{e}"}]
