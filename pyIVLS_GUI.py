from os.path import dirname, sep

from PyQt6 import QtWidgets
from PyQt6.QtCore import (
    QObject,
    Qt,
    pyqtSlot,
)

from components.pyIVLS_mainWindow import pyIVLS_mainWindow
from pyIVLS_pluginloader import pyIVLS_pluginloader


class pyIVLS_GUI(QObject):
    mdiWidgets = {}
    dockWidgets = {}
    ############################### GUI functions

    ############################### Slots
    @pyqtSlot(str)
    def show_message(self, str):
        msg = QtWidgets.QMessageBox()
        msg.setText(str)
        msg.setWindowTitle("Warning")
        msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msg.setWindowFlags(
            Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowShadeButtonHint
        )
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg.exec()

    @pyqtSlot(str)
    def addDataLog(self, str):
        print(str)

    @pyqtSlot()
    def reactClose(self):
        self.show_message("Stop running processes and disconnect devices before close")

    def setCloseLock(self, value):
        self.window.setCloseOK(value)
    
    @pyqtSlot()
    def seqBuilderReactClose(self):
        self.window.actionSequence_builder.setChecked(False)
    
    @pyqtSlot()
    def dockWidgetReactClose(self):
        self.window.actionDockWidget.setChecked(False)
        

    ################ Menu actions
    def actionPlugins(self):
        self.pluginloader.refresh()
        self.pluginloader.window.show()


    def actionSequence_builder(self):
        self.window.seqBuilder_dockWidget.setVisible(self.window.actionSequence_builder.isChecked())

    def actionDockWidget(self):
        self.window.dockWidget.setVisible(self.window.actionDockWidget.isChecked())

    def actionReopen_MDI(self):
        """
        Reopen the MDI area with the widgets stored in self.mdiWidgets.
        """
        self.clearMDIArea()
        for name, widget in self.mdiWidgets.items():
            widget.show()


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

    def setMDIArea(self, widgets: dict):
        """
        Set a list of widgets in MDI area

        :param widgets: dict of QtWidgets.QWidget instances to be added to MDI windows
        """

        # Add each widget to the MDI area as subwindows
        for name, widget in widgets.items():
            MDIwindow = self.window.mdiArea.addSubWindow(widget)
            MDIwindow.setWindowTitle(name)

            # so this is the flag that makes it possible to reopen the MDI windows
            # NOTE: this could lead to memory bloat if running multiple widgets and never closing the main window?
            # Although i think this will not be a problem.
            MDIwindow.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
            widget.show()  

        self.mdiWidgets = widgets

    def clearDockWidget(self):
        """
        Clear the dock widget by removing all tabs and setting its widget to None.
        """
        dock_widget = self.window.dockWidget.widget()
        if isinstance(dock_widget, QtWidgets.QTabWidget):
            dock_widget.clear()  # Clear all tabs
        self.window.dockWidget.setWidget(None)

    def clearMDIArea(self):
        """
        Clear the MDI area by closing all subwindows.
        """
        for subwindow in self.window.mdiArea.subWindowList():
            subwindow.close()
            

    def __init__(self):
        super(pyIVLS_GUI, self).__init__()
        self.path = dirname(__file__) + sep

        #        self.window = uic.loadUi(self.path + "pyIVLS_GUI.ui")
        self.window = pyIVLS_mainWindow(self.path)
        self.pluginloader = pyIVLS_pluginloader(self.path)

        self.window.actionPlugins.triggered.connect(self.actionPlugins)
        self.window.actionSequence_builder.triggered.connect(self.actionSequence_builder)
        self.window.actionDockWidget.triggered.connect(self.actionDockWidget)
        self.window.closeSignal.connect(self.reactClose)
        self.window.seqBuilder_dockWidget.closeSignal.connect(self.seqBuilderReactClose)
        self.window.dockWidget.closeSignal.connect(self.dockWidgetReactClose)

        self.initial_widget_state = {}