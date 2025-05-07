from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import pyqtSignal

class pyIVLS_mainWindow(QtWidgets.QMainWindow):

        closeSignal = pyqtSignal()
        
        def __init__(self, uipath):
                QtWidgets.QMainWindow.__init__(self)
                uic.loadUi(uipath + 'pyIVLS_GUI.ui', self)
                self.closeOK = True

        def setCloseOK(self, value):
                self.closeOK = value

        def closeEvent(self, event):
                if self.closeOK:
                        event.accept()
                else:
                        self.closeSignal.emit()
                        event.ignore()
