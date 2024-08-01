from PyQt6 import QtWidgets, uic
from os.path import dirname, sep

from PyQt6.QtCore import (
    QObject,
    QFile,
    QIODevice,
    QCoreApplication,
    Qt,
    QEvent,
    pyqtSignal,
    pyqtSlot,
)
from PyQt6.QtWidgets import QVBoxLayout

import pyIVLS_constants
from pyIVLS_container import pyIVLS_container
from pyIVLS_pluginloader import pyIVLS_pluginloader


class pyIVLS_GUI(QObject):

    ############################### GUI functions
    # FIXME: incorrect, see pyIVLS_pluginloader.py
    def show_message(self, txt):
        msg = QtWidgets.QMessageBox()
        msg.setText(txt)
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    ################ Menu actions
    def actionPlugins(self):
        self.pluginloader.refresh()
        self.pluginloader.window.show()

    ############### Settings Widget

    def setSettingsWidget(self, widgets: dict):
        """
        Set a list of widgets in a tabbed QDockWidget.

        :param widgets: dict of QtWidgets.QWidget instances to be tabbed
        """

        # Create a QTabWidget to hold the widgets
        tab_widget = QtWidgets.QTabWidget()

        # Add each widget to the QTabWidget as a new tab
        for name, widget in widgets.items():
            tab_widget.addTab(widget, str(name))  # Ensure name is a string

        # Set the QTabWidget as the widget for the QDockWidget
        self.window.dockWidget.setWidget(tab_widget)
        self.window.dockWidget.show()  # Ensure the dock widget is visible

    def clearDockWidget(self):
        """
        Clear the dock widget by removing all tabs and setting its widget to None.
        """
        dock_widget = self.window.dockWidget.widget()
        if isinstance(dock_widget, QtWidgets.QTabWidget):
            dock_widget.clear()  # Clear all tabs
        self.window.dockWidget.setWidget(None)

    def __init__(self):
        super().__init__()
        self.path = dirname(__file__) + sep

        self.window = uic.loadUi(self.path + "pyIVLS_GUI.ui")
        self.pluginloader = pyIVLS_pluginloader(self.path)

        self.window.actionPlugins.triggered.connect(self.actionPlugins)

        self.initial_widget_state = {}
