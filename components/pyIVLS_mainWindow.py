from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import pyqtSignal, Qt
from components.pyIVLS_dockWindow import pyIVLS_dockWindow


class pyIVLS_mainWindow(QtWidgets.QMainWindow):
    closeSignal = pyqtSignal()

    def __init__(self, uipath):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi(uipath + "pyIVLS_GUI.ui", self)
        self.seqBuilder_dockWidget = pyIVLS_dockWindow(
            parent=self, position=Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.dockWidget = pyIVLS_dockWindow(
            parent=self, position=Qt.DockWidgetArea.BottomDockWidgetArea
        )

        # add a menu for MDI windows under the view -> show menu
        menuShow = self.findChild(QtWidgets.QMenu, "menuShow")
        self.mdiWindowsMenu = QtWidgets.QMenu("MDI windows", self)
        self.mdiWindowsMenu.setObjectName("mdiWindowsMenu")
        menuShow.addMenu(self.mdiWindowsMenu)
        


        self.closeOK = True

    def setCloseOK(self, value):
        self.closeOK = value

    def closeEvent(self, event):
        if self.closeOK:
            self.seqBuilder_dockWidget.setCloseLock(False)
            self.dockWidget.setCloseLock(False)
            event.accept()
        else:
            self.closeSignal.emit()
            event.ignore()
