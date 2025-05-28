"""
This is a template for a plugin GUI implementation in pyIVLS

This file should provide
- functions for interaction with other plugins (those that will be exported on get_functions hook call, these should not start with "_")
- functions that will implement functionality of the hooks (see pyIVLS_pluginTemplate)
- GUI functionality - code that interracts with Qt GUI elements from widgets

The standard implementation may (but not must) include
- GUI a Qt widget implementation
- GUI functionality (e.g. pluginTemplateGUI.py) - code that interracts with Qt GUI elements from widgets
- plugin core implementation - a set of functions that may be used outside of GUI
"""

import os

from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6 import uic  # for loading .ui files


class affineMoveGUI(QObject):


    non_public_methods = []  
    public_methods = []  

    ########Signals
    # signals retained since this plugins needs to communicate during sutter calibration.
    log_message = pyqtSignal(str)
    info_message = pyqtSignal(str)

    ########Functions
    def __init__(self):
        super().__init__()
        self.path = os.path.dirname(__file__) + os.path.sep
        self.settingsWidget = uic.loadUi(self.path + "affineMove_Settings.ui")
        self.MDIWidget = uic.loadUi(self.path + "affineMove_MDI.ui")






    ########Functions
    ########GUI Slots


    ########Functions
    ################################### internal

    ########Functions
    ###############GUI setting up


    ########Functions
    ###############GUI react to change

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

    ########Functions to be used externally
    ###############get settings from GUI
