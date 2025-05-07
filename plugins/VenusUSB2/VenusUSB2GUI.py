'''
This is a GUI plugin for VenusUSB2 camera for pyIVLS

This file should provide
- functions for interaction with other plugins (those that will be exported on get_functions hook call, these should not start with "_")
- functions that will implement functionality of the hooks (see pyIVLS_VenusUSB2)
- GUI functionality - code that interracts with Qt GUI elements from widgets

This plugin should have double functionality
(i) it may be independently used to run camera preview
(ii) it provides functionality of getting images for other plugins

Because of (i) it requires to send log and message signals, i.e. it is a child of QObject

version 0.4
2025.02.28
ivarad
'''

import os

import numpy as np
from datetime import datetime
from PyQt6 import uic
from PyQt6 import QtWidgets
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from VenusUSB2 import VenusUSB2

import cv2 as cv
from typing import Optional

##IRtothink#### should some kind of zoom to the image part be added for the preview?

class VenusUSB2GUI(QObject):
    """GUI for the VenusUSB2 camera"""
    non_public_methods = [] # add function names here, if they should not be exported as public to another plugins
    default_timerInterval = 42 # ms, it is close to 24 fps that is standard for movies and TV
########Signals

    log_message = pyqtSignal(str)     
    info_message = pyqtSignal(str) 
    closeLock = pyqtSignal(bool)

########Functions       
    def __init__(self):
        super(VenusUSB2GUI,self).__init__()
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        ##IRtothink#### I do not like have filename hardly coded, 
        ############### but in any case the refrences to the GUI elements will be hardly coded, so it may be OK
        self.settingsWidget = uic.loadUi(self.path + "VenusUSB2_settingsWidget.ui")
        self.previewWidget = uic.loadUi(self.path + "VenusUSB2_previewWidget.ui")

        self.settings = {}

        # Initialize cap as empty capture
        self.camera = VenusUSB2()

        # Connect widget buttons to functions
        GUI_preview_button = self.settingsWidget.findChild(
            QtWidgets.QPushButton, "cameraPreview"
        )
        GUI_preview_button.clicked.connect(self._previewAction)

        # Set a timer for the camera feed
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        self.preview_running = False

########Functions
################################### internal

    def _update_frame(self):
        frame = self.camera.capture_image()
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        height, width, channel = frame.shape
        bytes_per_line = channel * width
        q_img = QImage(
            frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
        )
        self.previewWidget.previewLabel.setPixmap(QPixmap.fromImage(q_img))

    def _parse_settings_preview(self) -> "status":
        """Parses the settings widget for the camera. Extracts current values

        Returns:
            0 - no error
            ~0 - error (add error code later on if needed)
        """   
        self.settings["exposure"] = self.camera.exposures[int(self.settingsWidget.cameraExposure.value())]
        self.settings["source"] = self.settingsWidget.cameraSource.text()
	##no value checks are possible here as the source should be just address and exposure is given by a set of values
        return [0, self.settings]

########Functions 
########GUI Slots

    def _previewAction(self):
        """interface for the preview button. Opens the camera, sets the exposure and previews the feed"""
        if self.preview_running:
            self.timer.stop()
            self._GUIchange_deviceConnected(self.preview_running)
            self.preview_running = False
            self.camera.close()
        else:
            self._parse_settings_preview()
            [status, message] = self.camera.open(source=self.settings["source"], exposure=self.settings["exposure"])
            if status:
              self.log_message.emit(datetime.now().strftime("%H:%M:%S.%f") + f" : VenusUSB2 plugin : {message}, status = {status}")
              self.info_message.emit(f"VenusUSB2 plugin : {message}")
            else:  
            	if self.settings["exposure"] < self.default_timerInterval:
            		self.timer.start(self.default_timerInterval)
            	else:
            		self.timer.start(self.default_timerInterval + self.settings["exposure"])
            	self._GUIchange_deviceConnected(self.preview_running)
            	self.preview_running = True

########Functions
###############GUI setting up
           	
    def _initGUI(self, plugin_info:"dictionary with settings obtained from plugin_data in pyIVLS_*_plugin"):
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK
        self.settingsWidget.cameraExposure.setValue(self.camera.exposures.index(int(plugin_info["exposure"])))
        self.settingsWidget.cameraSource.setText(plugin_info["source"])

########Functions
###############GUI react to change

    def _GUIchange_deviceConnected(self, status):
        #NOTE: status is inverted, i.e. when preview is started received status should False, when preview is stopped status should be True
        if status:
                        self.settingsWidget.connectionIndicator.setStyleSheet("border-radius: 10px; background-color: rgb(165, 29, 45); min-height: 20px; min-width: 20px;")
        else:
                        self.settingsWidget.connectionIndicator.setStyleSheet("border-radius: 10px; background-color: rgb(38, 162, 105); min-height: 20px; min-width: 20px;")
        self.settingsWidget.exposureBox.setEnabled(status)
        self.settingsWidget.sourceBox.setEnabled(status)
        self.closeLock.emit(not status)

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

    def _getCloseLockSignal(self):
        return self.closeLock
