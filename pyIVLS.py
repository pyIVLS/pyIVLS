#!/usr/bin/python3.8
import sys
from os.path import dirname, sep

IVLS_path = dirname(__file__) + sep
sys.path.append(IVLS_path)

from PyQt6.QtCore import QCoreApplication, Qt, pyqtSlot
from PyQt6 import QtWidgets

from pyIVLS_GUI import pyIVLS_GUI
from pyIVLS_container import pyIVLS_container


###################################### slots
@pyqtSlot()
def update_settings_widget():
    what_am_i = pluginsContainer.get_plugin_info_from_settings()
    GUI_mainWindow.clearDockWidget()
    GUI_mainWindow.setSettingsWidget(what_am_i)
    GUI_mainWindow.pluginloader.refresh()


############################### main function

if __name__ == "__main__":

    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)

    pluginsContainer = pyIVLS_container()
    GUI_mainWindow = pyIVLS_GUI()

    ### initalize signals for pluginloader <-> container communication
    GUI_mainWindow.pluginloader.request_available_plugins_signal.connect(
        pluginsContainer.read_available_plugins
    )
    pluginsContainer.available_plugins_signal.connect(
        GUI_mainWindow.pluginloader.populate_list
    )
    GUI_mainWindow.pluginloader.register_plugins_signal.connect(
        pluginsContainer.update_registration
    )
    pluginsContainer.plugins_updated_signal.connect(update_settings_widget)

    pluginsContainer.show_message_signal.connect(
        GUI_mainWindow.pluginloader.show_message
    )

    # Think about this. The plugins need to communicate with each other. This *should* happen through the pluginscontainer pluginmanager.
    # The issue begins with the fact that the settings widgets are parsed inside the plugins themselves, which have no way of knowing about the other plugins.
    # Signals and slots are not great for this, since they are not dynamic. Should

    ### init interfaces
    whatAmI = pluginsContainer.get_plugin_info_from_settings()
    GUI_mainWindow.setSettingsWidget(whatAmI)
    GUI_mainWindow.window.show()

    pluginsContainer.cleanup()
    sys.exit(app.exec())
