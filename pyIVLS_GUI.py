from os.path import dirname, sep
import logging
import re

from PyQt6 import QtWidgets
from PyQt6.QtCore import QObject, Qt, pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtGui import QIcon
from components.pyIVLS_mainWindow import pyIVLS_mainWindow
from pyIVLS_pluginloader import pyIVLS_pluginloader
from pyIVLS_seqBuilder import pyIVLS_seqBuilder

# move this to mainwindow?
from components.pyIVLS_mdiWindow import pyIVLS_mdiWindow

# Create file handler (logs everything)
file_handler = logging.FileHandler("pyIVLS.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(asctime)s : %(levelname)s : %(message)s"))

# Create stream handler (logs INFO and above)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter("%(asctime)s : %(levelname)s : %(message)s"))

# Configure logger, print all to file and info and above to the console
logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, stream_handler])


class pyIVLS_GUI(QObject):
    mdiWidgets = {}
    dockWidgets = {}
    ############################### GUI functions

    ############################### Signals

    # signal plugincontainer to read new config file
    update_config_signal = pyqtSignal(str)

    ############################### Slots
    @pyqtSlot(str)
    def show_message(self, str):
        msg = QtWidgets.QMessageBox()
        msg.setText(str)
        msg.setWindowTitle("Warning")
        msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msg.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowShadeButtonHint | Qt.WindowType.WindowStaysOnTopHint)
        msg.raise_()
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg.exec()

    @pyqtSlot(str)
    def addDataLog(self, message: str):
        """
        Logs a message to both stdout and a log file, using flags in the message to determine log level.

        Args:
            message (str): The message to log.
        """
        # Define mapping of flags to logging functions
        flag_map = {
            ": verbose :": logging.debug,
            ": debug :": logging.debug,
            ": info :": logging.info,
            ": warn :": logging.warning,
            ": error :": logging.error,
        }

        # Search for a flag in the message (case-insensitive)
        match = re.search(r": (verbose|debug|info|warn|error) :", message, re.IGNORECASE)
        if match:
            flag = match.group(0).lower()
            log_func = flag_map.get(flag, logging.info)
            # Remove the flag from the message for cleaner output
            clean_message = re.sub(re.escape(flag), ":", message, flags=re.IGNORECASE)
            log_func(clean_message)
        else:
            # Default to info if no flag is found
            logging.info(message)

    @pyqtSlot()
    def reactClose(self):
        if self._blocking_plugins:
            plugin_list = ", ".join(sorted(self._blocking_plugins))
            self.show_message(f"Cannot close: The following plugins are still active: {plugin_list}. Stop running processes and disconnect devices before closing.")
        else:
            self.show_message("Stop running processes and disconnect devices before close")

    def setCloseLock(self, value, plugin_name=None):
        # Track which plugins are blocking closure
        if plugin_name:
            if value:
                self._blocking_plugins.add(plugin_name)
                logging.debug(f"Plugin {plugin_name} is blocking closure")
            else:
                self._blocking_plugins.discard(plugin_name)
                logging.debug(f"Plugin {plugin_name} no longer blocking closure")
        else:
            logging.debug(f"Close lock signal received without plugin name: {value}")

        # reverted closelock, since plugins return True when they are not ready to close
        any_blocked = len(self._blocking_plugins) > 0
        self.window.setCloseOK(not any_blocked)
        logging.debug(f"Current blocking plugins: {list(self._blocking_plugins)}, Close allowed: {not any_blocked}")

    @pyqtSlot()
    def seqBuilderReactClose(self):
        self.window.actionSequence_builder.setChecked(False)

    @pyqtSlot()
    def dockWidgetReactClose(self):
        self.window.actionDockWidget.setChecked(False)

    @pyqtSlot()
    def mdi_window_react_close(self):
        # check if all mdi windows are hidden
        all_hidden = True
        for subwindow in self.window.mdiArea.subWindowList():
            if subwindow.isVisible():
                all_hidden = False
                break
        if all_hidden:
            self.window.actionMDI_windows.setChecked(False)

    ################ Menu actions
    def actionPlugins(self):
        self.pluginloader.refresh()
        self.pluginloader.window.show()

    def actionSequence_builder(self):
        self.window.seqBuilder_dockWidget.setVisible(self.window.actionSequence_builder.isChecked())

    def actionDockWidget(self):
        self.window.dockWidget.setVisible(self.window.actionDockWidget.isChecked())

    def action_MDIShow_to_open(self):
        self.window.mdiWindowsMenu.clear()

        for subwindow in self.window.mdiArea.subWindowList():
            checkbox = QtWidgets.QCheckBox(subwindow.windowTitle())
            checkbox.setChecked(subwindow.isVisible())

            # Connect the checkbox state to the subwindow's visibility
            checkbox.stateChanged.connect(lambda state, sw=subwindow: sw.setVisible(state))

            # Wrap the checkbox in a QWidgetAction
            widget_action = QtWidgets.QWidgetAction(self.window)
            widget_action.setDefaultWidget(checkbox)

            self.window.mdiWindowsMenu.addAction(widget_action)

    def action_read_config_file(self) -> None:
        """Prompts user to select a configuration file through QFileDialog. Path emitted as signal(str)"""
        # https://forum.qt.io/topic/143116/qfiledialog-getopenfilename-causing-program-to-crash/14
        path, _ = QFileDialog.getOpenFileName(self.window, "Select Configuration File", self.path, "Configuration Files (*.ini)", options=QFileDialog.Option.DontUseNativeDialog | QFileDialog.Option.ReadOnly)
        if path:
            self.update_config_signal.emit(path)

    ############### Settings Widget

    def setSettingsWidget(self, widgets: dict):
        """
        Set a list of widgets in a tabbed QDockWidget.

        :param widgets: dict of QtWidgets.QWidget instances to be tabbed
        """

        # Create a QTabWidget to hold the widgets
        tab_widget = QtWidgets.QTabWidget()
        # Add each widget to the QTabWidget as a new tab
        for name, widget in widgets.items():
            tab_widget.addTab(widget, str(name))  # Ensure name is a string

        # Set the QTabWidget as the widget for the QDockWidget
        self.window.dockWidget.setWidget(tab_widget)
        self.window.dockWidget.show()  # Ensure the dock widget is visible

    def setMDIArea(self, widgets: dict):
        """
        Set a list of widgets in MDI area

        :param widgets: dict of QtWidgets.QWidget instances to be added to MDI windows
        """

        subwindows = self.window.mdiArea.subWindowList()
        subwindow_names = [subwindow.windowTitle() for subwindow in subwindows]

        default_width = 400  # Default width for MDI widgets
        default_height = 300  # Default height for MDI widgets
        vertical_spacing = 30  # Spacing between stacked widgets
        # FIXME: Have a hard think on wheter a fixed size is good or not
        for index, (name, widget) in enumerate(widgets.items()):
            if name not in subwindow_names:
                subwindow = pyIVLS_mdiWindow(self.window.mdiArea)
                subwindow.setWidget(widget)
                subwindow.setWindowTitle(name)
                subwindow.resize(default_width, default_height)  # Set default size

                # Position the subwindow to stack vertically
                subwindow.move(0, index * (vertical_spacing))

                subwindow.closeSignal.connect(self.mdi_window_react_close)
                subwindow.setVisible(True)  # Set window to be visible upon loading.
            else:
                # Subwindow already exists, do nothing. Widget should be set and correct
                pass

        # Close subwindows that are not in the widgets dict
        for sw in subwindows:
            if sw.windowTitle() not in widgets:
                self.window.mdiArea.removeSubWindow(sw)  # Remove subwindow because the subwindow list is used to iterate over existing windows
                sw.close()  # Actually close

    def setSeqBuilder(self):
        self.window.seqBuilder_dockWidget.setWidget(self.seqBuilder.widget)

    def clearDockWidget(self):
        """
        Clear the dock widget by removing all tabs and setting its widget to None.
        """
        dock_widget = self.window.dockWidget.widget()
        if isinstance(dock_widget, QtWidgets.QTabWidget):
            dock_widget.clear()  # Clear all tabs
        self.window.dockWidget.setWidget(None)

    def __init__(self):
        super(pyIVLS_GUI, self).__init__()
        self.path = dirname(__file__) + sep
        self._blocking_plugins = set()  # Track plugins that block closure for user visibility
        self.window = pyIVLS_mainWindow(self.path)
        self.pluginloader = pyIVLS_pluginloader(self.path)
        self.seqBuilder = pyIVLS_seqBuilder(self.path)
        icon_path = self.path + "components" + sep + "icon.png"
        self.window.setWindowIcon(QIcon(icon_path))

        self.setSeqBuilder()

        self.window.actionPlugins.triggered.connect(self.actionPlugins)
        self.window.actionSequence_builder.triggered.connect(self.actionSequence_builder)
        self.window.menuShow.aboutToShow.connect(self.action_MDIShow_to_open)
        self.window.actionDockWidget.triggered.connect(self.actionDockWidget)
        self.window.actionRead_config_file.triggered.connect(self.action_read_config_file)
        self.window.closeSignal.connect(self.reactClose)
        self.window.seqBuilder_dockWidget.closeSignal.connect(self.seqBuilderReactClose)
        self.window.dockWidget.closeSignal.connect(self.dockWidgetReactClose)

        self.pluginloader.request_available_plugins_signal

        self.initial_widget_state = {}
