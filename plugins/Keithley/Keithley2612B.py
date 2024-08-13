import sys
import os
import time

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QCheckBox, QComboBox, QLineEdit
from PyQt6.QtCore import QObject

from keithley2600 import Keithley2600


class Keithley2612B(QObject):

    ####################################  threads

    ################################### internal functions

    ########Slots

    ########Signals

    ########Functions
    def __init__(self):

        QObject.__init__(self)
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        filename = (
            os.path.splitext(os.path.basename(__file__))[0] + "_settingsWidget.ui"
        )
        self.settingsWidget = uic.loadUi(self.path + filename)

        # Extract settings from settingsWidget
        self.settings = self._get_settings_dict()

        self.PLACEHOLDER = "Enter VISA address"

    def _get_settings_dict(self):
        checkboxes = self.settingsWidget.findChildren(QCheckBox)
        comboboxes = self.settingsWidget.findChildren(QComboBox)
        lineedits = self.settingsWidget.findChildren(QLineEdit)

        settings = {}

        # Extract the settings into a dict
        # Format: settings[objectName] = function to get current value
        for checkbox in checkboxes:
            settings[checkbox.objectName()] = lambda cb=checkbox: cb.isChecked()
        for combobox in comboboxes:
            settings[combobox.objectName()] = lambda cb=combobox: cb.currentText()
        for lineedit in lineedits:
            settings[lineedit.objectName()] = lambda le=lineedit: le.text()

        return settings

    def connect(self):
        print("Connecting to Keithley 2612B")
        self.k = Keithley2600(self.PLACEHOLDER)

    def disconnect(self):
        print("Disconnecting from Keithley 2612B")
        self.k.disconnect()

    def measure(self):
        print("Measuring from Keithley 2612B")
        self.k.smua.
