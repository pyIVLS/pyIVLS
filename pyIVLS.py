#!/home/ivls/git_pyIVLS/pyIVLS/.venv/bin/python3
import sys
from os.path import dirname, sep

# wizardy on PATH for components imports, this means we dont have to write from components.pyIVLScontainer import pyIVLS_container.
# There was a reason behind this that I cannot recall, but Chesterton's fence so no modifications for now.
IVLS_path = dirname(__file__) + sep
sys.path.append(IVLS_path)
sys.path.append(dirname(__file__) + sep + "components" + sep)

# logs
import logging
from logging.handlers import RotatingFileHandler

logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("PySide6").setLevel(logging.WARNING)
logging.getLogger("pyvisa").setLevel(logging.WARNING)

# py-/ˈkjuːt/6
from PySide6 import QtWidgets
from PySide6.QtCore import QCoreApplication, Qt, Slot

from pyIVLS_container import pyIVLS_container
from pyIVLS_GUI import pyIVLS_GUI

import argparse

parser = argparse.ArgumentParser(description="pyIVLS Application")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output (display DEBUG logs in terminal)")
# parse_known_args allows PySide6/Qt flags to pass through without errors
args, unknown = parser.parse_known_args()

formatter = logging.Formatter("%(asctime)s : %(name)s : %(levelname)s : %(message)s")
console_level = logging.DEBUG if args.verbose else logging.INFO

# Create file handler (logs everything to file)
file_handler = RotatingFileHandler("pyIVLS.log", maxBytes=1024 * 1024, backupCount=2)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Create stream handler (logs DEBUG if -v is passed, otherwise INFO)
try:
    from rich.logging import RichHandler

    rich_formatter = logging.Formatter("[bold magenta]%(name)s[/bold magenta] › %(message)s")
    stream_handler = RichHandler(level=console_level, rich_tracebacks=True, tracebacks_show_locals=args.verbose, show_path=False, markup=True)
    stream_handler.setFormatter(rich_formatter)
except ImportError:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(console_level)
    stream_handler.setFormatter(formatter)

# Configure root logger
logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, stream_handler])
logger = logging.getLogger(__name__)


###################################### slots
@Slot()
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
        plugin_name = next(iter(closeLockSignal_dict))
        signal = closeLockSignal_dict[plugin_name]
        # Use lambda to capture plugin_name
        signal.connect(lambda value, name=plugin_name: GUI_mainWindow.setCloseLock(value, name))


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
    # signals to the main window
    pluginsContainer.plugins_updated_signal.connect(update_settings_widget)
    pluginsContainer.show_message_signal.connect(GUI_mainWindow.show_message)
    pluginsContainer.log_message.connect(GUI_mainWindow.addDataLog)

    # connect signals for seqbuilder
    GUI_mainWindow.seqBuilder.info_message.connect(GUI_mainWindow.show_message)
    GUI_mainWindow.seqBuilder.log_message.connect(GUI_mainWindow.addDataLog)
    pluginsContainer.seqComponents_signal.connect(GUI_mainWindow.seqBuilder.getPluginFunctions)

    # connect main window action signals to container
    GUI_mainWindow.window.ui.actionWrite_settings_to_file.triggered.connect(pluginsContainer.save_settings)
    GUI_mainWindow.import_config_signal.connect(pluginsContainer.import_config_file)
    GUI_mainWindow.export_config_signal.connect(pluginsContainer.export_config_file)

    # register plugins
    pluginsContainer.register_start_up()

    # This hooks the available GUIs and sets them to the main window. It also connects logging, closelock, info signals.
    update_settings_widget()

    # exchange public methods between plgs.
    pluginsContainer.public_function_exchange()

    # show main window, which owns all GUI widgets
    GUI_mainWindow.window.show()

    # write config to file after startup if config valid. This is done to update the file if incomplete plugins resulted in an incomplete config file.
    pluginsContainer.cleanup()

    # start event loop
    sys.exit(app.exec())
