import os

import numpy as np
from PyQt6 import uic
from PyQt6 import QtWidgets
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QImage, QPixmap
from VenusUSB2 import VenusUSB2

import cv2 as cv
from typing import Optional

##IRtothink#### should some kind of zoom to the image part be added for the preview?

class VenusUSB2GUI():
    """GUI for the VenusUSB2 camera"""
    non_public_methods = [] # add function names here, if they should not be exported as public to another plugins
    
    ##IRtothink#### should this be changed to a GUI setting? 
    default_timerInterval = 30
    
    def __init__(self):

        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        ##IRtothink#### I do not like have filename hardly coded, 
        ############### but in any case the refrences to the GUI elements will be hardly coded, so it may be OK
        self.settingsWidget = uic.loadUi(self.path + "VenusUSB2_settingsWidget.ui")
        self.previewWidget = uic.loadUi(self.path + "VenusUSB2_previewWidget.ui")

        # Initialize cap as empty capture
        self.camera = VenusUSB2()

        # Connect widget buttons to functions
        GUI_preview_button = self.settingsWidget.findChild(
            QtWidgets.QPushButton, "cameraPreview"
        )
        GUI_save_button = self.settingsWidget.findChild(QtWidgets.QPushButton, "cameraSave")
        GUI_preview_button.clicked.connect(self.previewAction)
        GUI_save_button.clicked.connect(self.saveButtonAction)


        # Set a timer for the camera feed
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        self.preview_running = False

    def _update_frame(self):
        frame = self.camera.capture_image()
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        height, width, channel = frame.shape
        bytes_per_line = channel * width
        q_img = QImage(
            frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
        )
        self.previewWidget.previewLabel.setPixmap(QPixmap.fromImage(q_img))

    def _parse_settings_widget(self) -> "status":
        """Parses the settings widget for the camera. Extracts current values

        Returns:
            0 - no error
            ~0 - error (add error code later on if needed)
        """       
        self.settings["exposure"] = self.camera.exposures[int(self.settingsWidget.cameraExposure.value())]
        self.settings["source"] = self.settingsWidget.cameraSource.text()
	##IRtodo######### add here checks that the values are allowed
        return 0

    def previewAction(self):
        """interface for the preview button. Opens the camera, sets the exposure and previews the feed"""
        if self.preview_running:
            self.timer.stop()
            self.settingsWidget.connectionIndicator.setStyleSheet("border-radius: 10px; background-color: rgb(165, 29, 45); min-height: 20px; min-width: 20px;")
            ##IRtodo#### enable GUI controls
            self.preview_running = False
            self.camera.close()
        else:
            self._parse_settings_widget()
            ##IRtodo#### add check if not(settings OK) return error
            if not(self.camera.open(source=self.settings["source"], exposure=self.settings["exposure"])):
              self.settingsWidget.connectionIndicator.setStyleSheet("border-radius: 10px; background-color: rgb(38, 162, 105); min-height: 20px; min-width: 20px;")
            if self.settings["exposure"] < self.default_timerInterval:
              self.timer.start(self.default_timerInterval)
            else:
              self.timer.start(self.default_timerInterval + self.settings["exposure"])
            ##IRtodo#### disable GUI controls
            self.preview_running = True

    def saveButtonAction(self) -> None:
        ##IRtothink#### Is this really needed?
    
        """interface for the save button. Updates the settings and saves them to internal dict.

        Returns:
            bool: pass/fail
        """
        self.settings = self._parse_settings_widget()
        ##IRtodo#### should be something different, e.g. check if the camera is open then restart with new settings, else do nothing
        self.close_camera()
           	
    def _initGUI(self, plugin_info:"dictionary with settings obtained from plugin_data in pyIVLS_*_plugin"):
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK
        self.settingsWidget.cameraExposure.setValue(self.camera.exposures.index(int(plugin_info["exposure"])))
        self.settingsWidget.cameraSource.setText(plugin_info["source"])
        
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
