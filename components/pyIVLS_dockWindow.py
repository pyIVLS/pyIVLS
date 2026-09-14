from PySide6 import QtWidgets
from PySide6.QtCore import Signal


class pyIVLS_dockWindow(QtWidgets.QDockWidget):
    closeSignal = Signal()
    closeLock = True

    def __init__(self, position, parent=None):
        """
        position is initial docking position, i.e.
        Qt.DockWidgetArea.RightDockWidgetArea, Qt.DockWidgetArea.BottomDockWidgetArea, etc.
        """
        super().__init__(parent)
        self.setFloating(False)
        self.setDockLocation(position)

    def setCloseLock(self, status):
        self.closeLock = status

    def closeEvent(self, event):
        if self.closeLock:
            self.closeSignal.emit()
            self.setVisible(False)
            event.ignore()
        else:
            event.accept()
