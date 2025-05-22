from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import pyqtSignal


class pyIVLS_mdiWindow(QtWidgets.QMdiSubWindow):
    closeSignal = pyqtSignal()
    closeLock = True

    def __init__(self, parent=None):
        super().__init__(parent)

    def setCloseLock(self, status):
        self.closeLock = status

    def closeEvent(self, event):
        print("MDI WINDOW CLOSE EVENT -------------------------------------------")
        if self.closeLock:
            print("Hiding MDI window without closing it")
            self.setVisible(False)
            self.closeSignal.emit()
            event.ignore()
        else:
            print("Closing MDI window for real")
            event.accept()
