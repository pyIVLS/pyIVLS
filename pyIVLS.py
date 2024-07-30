#!/usr/bin/python3.8
import sys
from os.path import dirname, sep
from os import sep
IVLS_path = dirname(__file__) + sep 
sys.path.append(IVLS_path)

from PyQt6.QtCore import QCoreApplication, Qt, pyqtSlot
from PyQt6 import QtWidgets

from pyIVLS_GUI import pyIVLS_GUI
from pyIVLS_container import pyIVLS_container
######################################

@pyqtSlot()
def update_settings_widget(self):
    raise NotImplementedError

############################### main function

if __name__ == "__main__":

    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    
    pluginsContainer = pyIVLS_container()
    GUI_mainWindow = pyIVLS_GUI()
    

    ###init signals for pluginloader <-> container communication
    GUI_mainWindow.pluginloader.request_available_plugins_signal.connect(
        pluginsContainer.read_available_plugins
    )
    pluginsContainer.available_plugins_signal.connect(GUI_mainWindow.pluginloader.populate_list)
    GUI_mainWindow.pluginloader.register_plugins_signal.connect(
        pluginsContainer.update_registration
    )
    

    
    ###init interfaces
    whatAmI = pluginsContainer.getPluginInfoFromSettings()
    print(whatAmI)
    GUI_mainWindow.window.show()
    
    sys.exit(app.exec())
