from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import pyqtSignal, Qt
from components.pyIVLS_dockWindow import pyIVLS_dockWindow
from PyQt6.QtGui import QCloseEvent, QAction

class pyIVLS_mainWindow(QtWidgets.QMainWindow):
    closeSignal = pyqtSignal()

    def __init__(self, uipath):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi(uipath + "pyIVLS_GUI.ui", self)
        self.seqBuilder_dockWidget = pyIVLS_dockWindow(parent=self, position=Qt.DockWidgetArea.RightDockWidgetArea)
        self.dockWidget = pyIVLS_dockWindow(parent=self, position=Qt.DockWidgetArea.BottomDockWidgetArea)

        # Ensure mdiArea and actions are accessible
        self.mdiArea = self.findChild(QtWidgets.QMdiArea, "mdiArea")
        self.actionPlugins = self.findChild(QAction, "actionPlugins")
        self.actionSequence_builder = self.findChild(QAction, "actionSequence_builder")
        self.actionDockWidget = self.findChild(QAction, "actionDockWidget")

        # add a menu for MDI windows under the view -> show menu
        menuShow = self.findChild(QtWidgets.QMenu, "menuShow")
        self.mdiWindowsMenu = QtWidgets.QMenu("MDI windows", self)
        self.mdiWindowsMenu.setObjectName("mdiWindowsMenu")
        menuShow.addMenu(self.mdiWindowsMenu)

        self.closeOK = True

    def setCloseOK(self, value):
        self.closeOK = value

    def closeEvent(self, a0: QCloseEvent | None):
        if self.closeOK:
            self.seqBuilder_dockWidget.setCloseLock(False)
            self.dockWidget.setCloseLock(False)
            if a0:
                a0.accept()
        else:
            self.closeSignal.emit()
            if a0:
                a0.ignore()
