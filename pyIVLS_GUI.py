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
    pyqtSlot
)
from PyQt6.QtWidgets import QVBoxLayout

import pyIVLS_constants
from pyIVLS_container import pyIVLS_container
from pyIVLS_pluginloader import pyIVLS_pluginloader


class pyIVLS_GUI(QObject):



    ############################### GUI functions
    def show_message(self, txt):
        msg = QtWidgets.QMessageBox()
        msg.setText(txt)
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    ################ Menu actions
    def actionPlugins(self):
        self.pluginloader.window.show()

    ############### end of Menu actions

    def setSettingsWidget(self, widget):
        assert isinstance(widget, QtWidgets.QWidget)
        self.window.dockWidget.setWidget(widget)

    def __init__(self):
        super(pyIVLS_GUI, self).__init__()
        self.path = dirname(__file__) + sep

        self.window = uic.loadUi(self.path + "pyIVLS_GUI.ui")
        self.pluginloader = pyIVLS_pluginloader(self.path)


        self.window.actionPlugins.triggered.connect(self.actionPlugins)
