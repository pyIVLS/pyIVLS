from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal


class pyIVLS_mdiWindow(QtWidgets.QMdiSubWindow):
    closeSignal = pyqtSignal()
    closeLock = True

    def __init__(self, parent=None):
        super().__init__(parent)

    def setCloseLock(self, status):
        self.closeLock = status

    def closeEvent(self, event):
        if self.closeLock:
            self.setVisible(False)
            self.closeSignal.emit()
            event.ignore()
        else:
            event.accept()
