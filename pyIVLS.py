#!/home/ivarad/git_pyIVLS/.venv/bin/python3
import sys
from os.path import dirname, sep

from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication, Qt, pyqtSlot

from pyIVLS_container import pyIVLS_container
from pyIVLS_GUI import pyIVLS_GUI

IVLS_path = dirname(__file__) + sep
sys.path.append(IVLS_path)
sys.path.append(dirname(__file__) + sep + "components" + sep)


###################################### slots
@pyqtSlot()
def update_settings_widget():
    # update settings tabs
    settings_windows = pluginsContainer.get_plugin_info_for_settingsGUI()
    GUI_mainWindow.clearDockWidget()
    GUI_mainWindow.setSettingsWidget(settings_windows)
    # update MDI widgets
    mdi_windows = pluginsContainer.get_plugin_info_for_MDIarea()
    GUI_mainWindow.setMDIArea(mdi_windows)
    # update plugin list
    GUI_mainWindow.pluginloader.refresh()


    # when pluginlist updates, call hooks to connect all data/log signals 
    for logSignal in pluginsContainer.getLogSignals():
        logSignal.connect(GUI_mainWindow.addDataLog)

    for infoSignal in pluginsContainer.getInfoSignals():
        infoSignal.connect(GUI_mainWindow.show_message)

    for closeLockSignal in pluginsContainer.getCloseLockSignals():
        closeLockSignal.connect(GUI_mainWindow.setCloseLock)

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

    pluginsContainer.show_message_signal.connect(GUI_mainWindow.show_message)

    pluginsContainer.log_message.connect(GUI_mainWindow.addDataLog)
    GUI_mainWindow.seqBuilder.info_message.connect(GUI_mainWindow.show_message)

    pluginsContainer.register_start_up()

    for logSignal in pluginsContainer.getLogSignals():
        logSignal.connect(GUI_mainWindow.addDataLog)

    for infoSignal in pluginsContainer.getInfoSignals():
        infoSignal.connect(GUI_mainWindow.show_message)

    for closeLockSignal in pluginsContainer.getCloseLockSignals():
       closeLockSignal.connect(GUI_mainWindow.setCloseLock)
    
    pluginsContainer.seqComponents_signal.connect(GUI_mainWindow.seqBuilder.getPluginFunctions)
    
    pluginsContainer.public_function_exchange()
    ### init interfaces
    whatAmI = pluginsContainer.get_plugin_info_for_settingsGUI()
    GUI_mainWindow.setSettingsWidget(whatAmI)
    GUI_mainWindow.setMDIArea(pluginsContainer.get_plugin_info_for_MDIarea())

    GUI_mainWindow.window.show()

    pluginsContainer.cleanup()
    sys.exit(app.exec())
