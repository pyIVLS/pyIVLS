from os.path import dirname, sep

from PyQt6 import QtWidgets
from PyQt6.QtGui import QAction
from PyQt6.QtCore import (
    QObject,
    Qt,
    pyqtSlot
)

from components.pyIVLS_mainWindow import pyIVLS_mainWindow
from pyIVLS_pluginloader import pyIVLS_pluginloader
from pyIVLS_seqBuilder import pyIVLS_seqBuilder

# move this to mainwindow?
from components.pyIVLS_mdiWindow import pyIVLS_mdiWindow
from components.pyIVLS_mainWindow import pyIVLS_mainWindow


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
        # reverted closelock, since plugins return True when they are not ready to close
        self.window.setCloseOK(not value)

    @pyqtSlot()
    def seqBuilderReactClose(self):
        self.window.actionSequence_builder.setChecked(False)

    @pyqtSlot()
    def dockWidgetReactClose(self):
        self.window.actionDockWidget.setChecked(False)

    @pyqtSlot()
    def mdi_window_react_close(self):
        # check if all mdi windows are hidden
        all_hidden = True
        for subwindow in self.window.mdiArea.subWindowList():
            if subwindow.isVisible():
                all_hidden = False
                break
        if all_hidden:
            self.window.actionMDI_windows.setChecked(False)

    ################ Menu actions
    def actionPlugins(self):
        self.pluginloader.refresh()
        self.pluginloader.window.show()

    def actionSequence_builder(self):
        self.window.seqBuilder_dockWidget.setVisible(
            self.window.actionSequence_builder.isChecked()
        )

    def actionDockWidget(self):
        self.window.dockWidget.setVisible(self.window.actionDockWidget.isChecked())

    def action_MDIShow_to_open(self):
        self.window.mdiWindowsMenu.clear()

        for subwindow in self.window.mdiArea.subWindowList():
            checkbox = QtWidgets.QCheckBox(subwindow.windowTitle())
            checkbox.setChecked(subwindow.isVisible())

            # Connect the checkbox state to the subwindow's visibility
            checkbox.stateChanged.connect(lambda state, sw=subwindow: sw.setVisible(state))

            # Wrap the checkbox in a QWidgetAction
            widget_action = QtWidgets.QWidgetAction(self.window)
            widget_action.setDefaultWidget(checkbox)

            self.window.mdiWindowsMenu.addAction(widget_action)



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

        subwindows = self.window.mdiArea.subWindowList()
        subwindow_names = [subwindow.windowTitle() for subwindow in subwindows]

        for name, widget in widgets.items():
            if name not in subwindow_names:
                subwindow = pyIVLS_mdiWindow(self.window.mdiArea)
                subwindow.setWidget(widget)
                widget.show()
                subwindow.setWindowTitle(name)
                subwindow.closeSignal.connect(self.mdi_window_react_close)
                subwindow.setVisible(True) # set window to be visible upon loading.
            else:
                # subwindow already exists, do nothing. Widget should be set and correct
                pass

        # close subwindows that are not in the widgets dict
        for sw in subwindows:
            if sw.windowTitle() not in widgets:
                self.window.mdiArea.removeSubWindow(
                    sw
                )  # Remove subwindow because the subwindow list is used to iterate over existing windows
                sw.setCloseLock(False)  # closelock is set to False to allow closing
                sw.close()  # actually close

    def setSeqBuilder(self):
        self.window.seqBuilder_dockWidget.setWidget(self.seqBuilder.widget)

    def clearDockWidget(self):
        """
        Clear the dock widget by removing all tabs and setting its widget to None.
        """
        dock_widget = self.window.dockWidget.widget()
        if isinstance(dock_widget, QtWidgets.QTabWidget):
            dock_widget.clear()  # Clear all tabs
        self.window.dockWidget.setWidget(None)

    def __init__(self):
        super(pyIVLS_GUI, self).__init__()
        self.path = dirname(__file__) + sep

        self.window = pyIVLS_mainWindow(self.path)
        self.pluginloader = pyIVLS_pluginloader(self.path)
        self.seqBuilder = pyIVLS_seqBuilder(self.path)

        self.setSeqBuilder()

        self.window.actionPlugins.triggered.connect(self.actionPlugins)
        self.window.actionSequence_builder.triggered.connect(
            self.actionSequence_builder
        )
        self.window.menuShow.aboutToShow.connect(
            self.action_MDIShow_to_open
        )
        self.window.actionDockWidget.triggered.connect(self.actionDockWidget)
        self.window.closeSignal.connect(self.reactClose)
        self.window.seqBuilder_dockWidget.closeSignal.connect(self.seqBuilderReactClose)
        self.window.dockWidget.closeSignal.connect(self.dockWidgetReactClose)

        self.pluginloader.request_available_plugins_signal

        self.initial_widget_state = {}
