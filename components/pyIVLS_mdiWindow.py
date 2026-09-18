from PySide6 import QtWidgets
from PySide6.QtCore import Signal


class pyIVLS_mdiWindow(QtWidgets.QMdiSubWindow):
    closeSignal = Signal()
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
