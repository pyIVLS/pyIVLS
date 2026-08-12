import logging

from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QCloseEvent

from components.pyIVLS_dockWindow import pyIVLS_dockWindow

logger = logging.getLogger(__name__)


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
        self.blocking = set()  # Initialize blocking as an empty set

    def setCloseOK(self, value: bool, blocking: set | None = None):
        self.closeOK = value
        if blocking is not None:
            self.blocking = blocking

    def closeEvent(self, a0: QCloseEvent | None):

        logger.debug(f"closeEvent called with closeOK={self.closeOK}")
        # ask for confirmation if closeOK is False
        if not self.closeOK:
            logger.debug("Close not allowed, asking for confirmation.")
            reply = QtWidgets.QMessageBox.question(
                self,
                "Confirm Close",
                f"Are you sure you want to close the application? The following plugins are still active: {self.blocking}",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No,
            )
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                logger.debug("User confirmed close, setting closeOK to True and accepting the event.")
                self.closeOK = True
                self.seqBuilder_dockWidget.setCloseLock(False)
                self.dockWidget.setCloseLock(False)
                if a0:
                    a0.accept()
            else:
                logger.debug("User canceled close, ignoring the event.")
                if a0:
                    a0.ignore()
        else:
            logger.debug("Closing main window, setting closeLock to False for dock widgets.")
            self.seqBuilder_dockWidget.setCloseLock(False)
            self.dockWidget.setCloseLock(False)
            if a0:
                a0.accept()
