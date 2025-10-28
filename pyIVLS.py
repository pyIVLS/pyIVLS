#!/home/ivls/git_pyIVLS/pyIVLS/.venv/bin/python3
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
    # NOTE: type of UniqueConnection is set to prevent plugins from reconnecting every time the plugin list is updated.
    # Multiple connections result in multiple info/log messages being sent to the GUI.
    # flag throws an error if the signal is already connected, so the exception is caught and ignored.

    for logSignal in pluginsContainer.getLogSignals():
        try:
            logSignal.connect(GUI_mainWindow.addDataLog, type=Qt.ConnectionType.UniqueConnection)
        except TypeError:
            pass

    for infoSignal in pluginsContainer.getInfoSignals():
        try:
            infoSignal.connect(GUI_mainWindow.show_message, type=Qt.ConnectionType.UniqueConnection)
        except TypeError:
            pass

    # Connect close lock signals with plugin names
    plugin_closeLockSignals = pluginsContainer.pm.hook.get_closeLock()
    for closeLockSignal_dict in plugin_closeLockSignals:
        try:
            plugin_name = list(closeLockSignal_dict.keys())[0]
            signal = closeLockSignal_dict[plugin_name]
            # Use lambda to capture plugin_name
            signal.connect(lambda value, name=plugin_name: GUI_mainWindow.setCloseLock(value, name), type=Qt.ConnectionType.UniqueConnection)
        except TypeError:
            pass


############################### main function

if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)

    pluginsContainer = pyIVLS_container()
    GUI_mainWindow = pyIVLS_GUI()
    # log startup
    GUI_mainWindow.addDataLog("pyIVLS session started")
    ### initalize signals for pluginloader <-> container communication
    GUI_mainWindow.pluginloader.request_available_plugins_signal.connect(pluginsContainer.read_available_plugins)
    GUI_mainWindow.pluginloader.update_config_signal.connect(pluginsContainer.update_config)
    pluginsContainer.available_plugins_signal.connect(GUI_mainWindow.pluginloader.populate_list)
    GUI_mainWindow.pluginloader.register_plugins_signal.connect(pluginsContainer.update_registration)
    pluginsContainer.plugins_updated_signal.connect(update_settings_widget)

    pluginsContainer.show_message_signal.connect(GUI_mainWindow.show_message)

    pluginsContainer.log_message.connect(GUI_mainWindow.addDataLog)
    GUI_mainWindow.seqBuilder.info_message.connect(GUI_mainWindow.show_message)
    GUI_mainWindow.seqBuilder.log_message.connect(GUI_mainWindow.addDataLog)

    GUI_mainWindow.window.actionWrite_settings_to_file.triggered.connect(pluginsContainer.save_settings)
    GUI_mainWindow.update_config_signal.connect(pluginsContainer.update_config_file)
    pluginsContainer.register_start_up()

    update_settings_widget()


    pluginsContainer.seqComponents_signal.connect(GUI_mainWindow.seqBuilder.getPluginFunctions)

    pluginsContainer.public_function_exchange()
    ### init interfaces
    whatAmI = pluginsContainer.get_plugin_info_for_settingsGUI()
    GUI_mainWindow.setSettingsWidget(whatAmI)
    GUI_mainWindow.setMDIArea(pluginsContainer.get_plugin_info_for_MDIarea())

    GUI_mainWindow.window.show()

    pluginsContainer.cleanup()
    sys.exit(app.exec())
