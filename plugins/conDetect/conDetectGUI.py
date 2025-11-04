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
import copy

from PyQt6.QtCore import QObject
from PyQt6 import uic
from plugin_components import (
    LoggingHelper,
    CloseLockSignalProvider,
    public,
    get_public_methods,
    ConnectionIndicatorStyle,
)
from conDetect import conDetect


class conDetectGUI(QObject):
    def __init__(self):
        super().__init__()
        self.path = os.path.dirname(__file__) + os.path.sep
        self.settingsWidget = uic.loadUi(self.path + "conDetect_settingsWidget.ui")
        self.functionality = conDetect()
        self._connect_signals()
        self.settings = {}
        self.connected = False
        self.hiCheck = False
        self.loCheck = False
        self.logger = LoggingHelper(self)
        self.closelock = CloseLockSignalProvider()
        self.logger.log_info("conDetectGUI initialized.")

    def _connect_signals(self):
        self.settingsWidget.connectButton.clicked.connect(self._connectAction)
        self.settingsWidget.disconnectButton.clicked.connect(self._disconnectAction)
        self.settingsWidget.hiConnectionButton.clicked.connect(self._hiConnectionCheck)
        self.settingsWidget.loConnectionButton.clicked.connect(self._loConnectionCheck)

    ########Functions
    ################################### internal
    @public
    def parse_settings_widget(self) -> tuple:
        """Parses the settings widget for the conDetect. Extracts current values

        Returns:
            0 - no error
            ~0 - error (add error code later on if needed)
        """
        self.settings["source"] = self.settingsWidget.sourceLine.text()
        ##no value checks are possible here as the source should be just address and exposure is given by a set of values
        self.logger.log_debug(f"Parsed settings: {self.settings}")
        return (0, self.settings)

    @public
    def setSettings(self, settings: dict) -> None:
        self.settings = copy.deepcopy(settings)

    ########Functions
    ########GUI Slots

    def _connectAction(self):
        self.logger.log_info("Attempting to connect device.")
        self.parse_settings_widget()
        status, info = self.deviceConnect()
        if status:
            self.logger.log_warn(f"Device connect failed: {info}")
            self.logger.info_popup(f"conDetect plugin : {info['Error message']}")
            return
        self.connected = True
        self._GUIchange_deviceConnected(self.connected)
        self.closelock.emit_close_lock(self.connected)
        self.logger.log_info("Device connected successfully.")

    def _disconnectAction(self):
        self.logger.log_info("Attempting to disconnect device.")
        status, info = self.deviceDisconnect()
        self.connected = False
        self._GUIchange_deviceConnected(self.connected)
        self.closelock.emit_close_lock(self.connected)
        if status:
            self.logger.log_warn(f"Device disconnect failed: {info}")
            self.logger.info_popup(f"conDetect plugin : {info['Error message']}")
            self.settingsWidget.connectButton.setEnabled(self.connected)
        else:
            self.logger.log_info("Device disconnected successfully.")

    def _hiConnectionCheck(self):
        if self.loCheck:
            self.logger.log_warn("Simultaneous check of Hi and Lo not permitted.")
            self.logger.info_popup("conDetect plugin : Simultaneous check of Hi and Lo not permitted")
            return (1, {"Error message": "Simultaneous check of Hi and Lo not permitted"})
        else:
            status, info = self.deviceHiCheck(not self.hiCheck)
            if status:
                self.logger.log_warn(f"Hi connection check failed: {info}")
                self.logger.info_popup(f"conDetect plugin : {info['Error message']}")
                return (status, info)
            else:
                self.hiCheck = not self.hiCheck
                self.logger.log_info("Hi connection toggled.")
                return (0, "OK")

    def _loConnectionCheck(self):
        if self.hiCheck:
            self.logger.log_warn("Simultaneous check of Hi and Lo not permitted.")
            self.logger.info_popup("conDetect plugin : Simultaneous check of Hi and Lo not permitted")
            return (1, {"Error message": "Simultaneous check of Hi and Lo not permitted"})
        else:
            status, info = self.deviceLoCheck(not self.loCheck)
            if status:
                self.logger.log_warn(f"Lo connection check failed: {info}")
                self.logger.info_popup(f"conDetect plugin : {info['Error message']}")
                return (status, info)
            else:
                self.loCheck = not self.loCheck
                self.logger.log_info("Lo connection toggled.")
                return (0, "OK")

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
        self.logger.log_debug("Initializing GUI with plugin_info.")
        self.settingsWidget.sourceLine.setText(plugin_info["source"])

    ########Functions
    ###############GUI react to change

    def _GUIchange_deviceConnected(self, status):
        self.logger.log_debug(f"Device connected status changed: {status}")
        # NOTE: status is inverted, i.e. when preview is started received status should False, when preview is stopped status should be True
        if status:
            self.settingsWidget.connectionIndicator.setStyleSheet(ConnectionIndicatorStyle.GREEN_CONNECTED.value)
        else:
            self.settingsWidget.connectionIndicator.setStyleSheet(ConnectionIndicatorStyle.RED_DISCONNECTED.value)
        self.settingsWidget.sourceText.setEnabled(not status)
        self.settingsWidget.sourceLabel.setEnabled(not status)
        self.settingsWidget.sourceLine.setEnabled(not status)
        self.settingsWidget.connectButton.setEnabled(not status)
        self.settingsWidget.disconnectButton.setEnabled(status)
        self.settingsWidget.statusBox.setEnabled(status)

    ########Functions
    ########plugins interraction

    def _get_public_methods(self):
        return get_public_methods(self)

    def _getLogSignal(self):
        return self.logger.logger_signal

    def _getInfoSignal(self):
        return self.logger.info_popup_signal

    def _getCloseLockSignal(self):
        return self.closelock.closeLock

    ########Functions
    ########device functions

    @public
    def deviceConnect(self):
        self.logger.log_debug("deviceConnect called.")
        status, state = self.parse_settings_widget()
        if status:
            self.logger.log_warn(f"parse_settings_widget failed: {state}")
            return (status, {"Error message": f"{state}"})
        if self.settings.get("source", "") == "":
            self.logger.log_warn("Source address is empty in deviceConnect.")
            return (1, {"Error message": "Source address is empty"})
        try:
            success = self.functionality.connect(self.settings["source"])
            assert success, "Failed to connect to the device"
            self.functionality.setDefault()
            self.connected = True
            self._GUIchange_deviceConnected(self.connected)
            self.logger.log_info("Device connected in deviceConnect.")
            return (0, "OK")
        except Exception as e:
            self.logger.log_warn(f"Exception in deviceConnect: {e}")
            return (4, {"Error message": f"{e}"})

    @public
    def deviceDisconnect(self):
        return (0, "OK")
        self.logger.log_debug("deviceDisconnect called.")
        try:
            self.functionality.setDefault()
            self.settingsWidget.hiConnectionIndicator.setStyleSheet(ConnectionIndicatorStyle.RED_DISCONNECTED.value)
            self.settingsWidget.loConnectionIndicator.setStyleSheet(ConnectionIndicatorStyle.RED_DISCONNECTED.value)
            self.functionality.disconnect()
            self.connected = False
            self._GUIchange_deviceConnected(self.connected)
            self.logger.log_info("Device disconnected in deviceDisconnect.")
            return (0, "OK")
        except Exception as e:
            self.logger.log_warn(f"Exception in deviceDisconnect: {e}")
            return (4, {"Error message": f"{e}"})

    @public
    def deviceHiCheck(self, status):
        self.logger.log_debug(f"deviceHiCheck called with status={status}.")
        try:
            self.functionality.hiCheck(status)
            if status:
                self.settingsWidget.hiConnectionIndicator.setStyleSheet(ConnectionIndicatorStyle.GREEN_CONNECTED.value)
            else:
                self.settingsWidget.hiConnectionIndicator.setStyleSheet(ConnectionIndicatorStyle.RED_DISCONNECTED.value)
            return (0, "OK")
        except Exception as e:
            self.logger.log_warn(f"Exception in deviceHiCheck: {e}")
            return (4, {"Error message": f"{e}"})

    @public
    def deviceLoCheck(self, status):
        self.logger.log_debug(f"deviceLoCheck called with status={status}.")
        try:
            self.functionality.loCheck(status)
            if status:
                self.settingsWidget.loConnectionIndicator.setStyleSheet(ConnectionIndicatorStyle.GREEN_CONNECTED.value)
            else:
                self.settingsWidget.loConnectionIndicator.setStyleSheet(ConnectionIndicatorStyle.RED_DISCONNECTED.value)
            return (0, "OK")
        except Exception as e:
            self.logger.log_warn(f"Exception in deviceLoCheck: {e}")
            return (4, {"Error message": f"{e}"})
