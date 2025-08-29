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

from PyQt6 import uic
from PyQt6.QtCore import QObject, pyqtSignal
from pluginTemplate import pluginTemplate
from MplCanvas import (
    MplCanvas,
)  # this is loaded from components directory that contains shared classes


class pluginTemplateGUI(QObject):
    """GUI implementation
    this class may be a child of QObject if Signals or Slot will be needed
    """

    non_public_methods = []  # add function names here, if they should not be exported as public to another plugins
    public_methods = []  # add function names here, necessary for descendents of QObject, otherwise _get_public_methods returns a lot of QObject methods
    ########Signals
    ##remove this if plugin will only provide functions to another plugins, but will not interract with the user directly
    log_message = pyqtSignal(str)
    info_message = pyqtSignal(str)

    ########Functions
    def __init__(self):
        super(pluginTemplateGUI, self).__init__()  ### this is needed if the class is a child of QObject
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep

        self.settingsWidget = uic.loadUi(self.path + "pluginTemplate_settingsWidget.ui")
        self.previewWidget = uic.loadUi(self.path + "pluginTemplate_MDIWidget.ui")

        # Initialize the functionality core that should be independent on GUI
        self.templateFunctionality = pluginTemplate()

        # remove next if no direct interraction with user
        self._connect_sgnals()
        # remove next if no plots
        self._create_plt()

    def _connect_signals(self):
        self.settingsWidget.exampleButton.clicked.connect(self._exampleAction)

    def _create_plt(self):
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.axes = self.sc.fig.add_subplot(111)
        self.axes.set_xlabel("time (HH:MM)")
        self.axes.set_ylabel("Temperature ($^\circ$C)")

        self.MDIWidget.dislpayLayout.addWidget(self.sc._create_toolbar(self.MDIWidget))
        self.MDIWidget.dislpayLayout.addWidget(self.sc)

    ########Functions
    ########GUI Slots

    def _exampleAction(self):
        # do smth
        return 0

    ########Functions
    ################################### internal

    ########Functions
    ###############GUI setting up
    def _initGUI(
        self,
        plugin_info: dict,
    ):
        """Initialize the GUI components with the provided plugin information.

        Args:
            plugin_info (dict): dictionary with settings obtained from plugin_data in pyIVLS_
        """
        ##settings are not initialized here, only GUI
        ## i.e. no settings checks are here. Practically it means that anything may be used for initialization (var types still should be checked), but functions should not work if settings are not OK

        #### for example
        self.settingsWidget.cameraExposure.setValue(self.camera.exposures.index(int(plugin_info["exposure"])))
        self.settingsWidget.cameraSource.setText(plugin_info["source"])

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
    def parse_settings_widget(self) -> tuple[int, dict]:
        """Parses the settings widget for the templatePlugin. Extracts current values. Checks if values are allowed. Provides settings of template plugin to an external plugin

        Returns [status, settings_dict]:
            status: 0 - no error, ~0 - error (add error code later on if needed)
            self.settings
        """
        #### for example
        self.settings["exposure"] = self.camera.exposures[int(self.settingsWidget.cameraExposure.value())]
        self.settings["source"] = self.settingsWidget.cameraSource.text()
        ##IRtodo######### add here checks that the values are allowed
        return [0, self.settings]
