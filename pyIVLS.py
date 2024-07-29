#!/usr/bin/python3.8
import sys
from os.path import dirname, sep
from os import sep
IVLS_path = dirname(__file__) + sep 
sys.path.append(IVLS_path)

from PyQt6.QtCore import QCoreApplication, Qt
from PyQt6 import QtWidgets

from pyIVLS_GUI import pyIVLS_GUI
from pyIVLS_container import pyIVLS_container
######################################

############################### main function

if __name__ == "__main__":

    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    
    pluginsContainer = pyIVLS_container()
    GUI_mainWindow = pyIVLS_GUI(pluginsContainer)
    



    
    ###init interfaces
    GUI_mainWindow.setSettingsWidget(pluginsContainer.getPluginInfoFromSettings())
    GUI_mainWindow.window.show()
    
    sys.exit(app.exec())
