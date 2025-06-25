# File: pyIVLS_pluginloader.py
# dialog and functionality for the plugins action from the Tools menu
# This represents the single window opened.

import sys
from os.path import sep
import os

from PyQt6 import QtGui, QtWidgets, uic
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot


class pyIVLS_pluginloader(QtWidgets.QDialog):
    """Gui for the plugin loader"""

    def show_message(self, str):
        msg = QtWidgets.QMessageBox()
        msg.setText(str)
        msg.setWindowTitle("Warning")
        msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msg.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowShadeButtonHint)
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg.exec()

    #### Signals for communication

    # Request available plugins from the container
    request_available_plugins_signal = pyqtSignal()
    # Tell the container to register the plugins
    register_plugins_signal = pyqtSignal(list)
    # Signal to update the config file with a new plugin
    update_config_signal = pyqtSignal(list)

    #### Slots for communication
    @pyqtSlot(dict)
    def populate_list(self, plugins):
        """Populates the list of plugins in the plugin GUI. This is called from the container signal "available_plugins_signal".

        Args:
            plugins (dict): dictionary of plugin information from the container.
        """
        self.model.clear()  # Clear the existing items in the model

        for item, properties in plugins.items():
            dependencies = properties.get("dependencies", "")
            if not dependencies:
                dependencies = "None"
            plugin_name = f"{properties.get('type')}: {item} {properties.get('version', '')} ({properties.get('function')}) - Dependencies: {dependencies}"
            list_item = QtGui.QStandardItem(plugin_name)
            list_item.setCheckable(True)
            list_item.setCheckState(Qt.CheckState.Unchecked)
            list_item.setFlags(list_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if properties.get("load") == "True":
                list_item.setCheckState(Qt.CheckState.Checked)

            list_item.setToolTip(item)
            list_item.setData(item, Qt.ItemDataRole.UserRole)

            self.model.appendRow(list_item)

    @pyqtSlot(str)
    def state_changed(self, plugin_name):
        """NOTE: Currently unused. This function is planned called when a plugin is activated or deactivated.

        Args:
            plugin_name (str): plugin name
        """
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == plugin_name:
                item.setCheckState(Qt.CheckState.Checked)

    #### Button actions
    def refresh(self):
        """Tells the container to send the available plugins. The container the emits a signal that leads to the populate_list() method."""
        self.request_available_plugins_signal.emit()

    def apply(self):
        """Interface for the apply button. Activates the selected plugins and refreshes the list.
        The container is then told to register the plugins.
        The list is then repopulated with refresh()
        """
        plugins = []
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                plugin_name = item.data(Qt.ItemDataRole.UserRole)
                plugin = plugin_name + "_plugin"
                plugins.append(plugin)
        self.register_plugins_signal.emit(plugins)
        self.refresh()

    def upload(self):
        """Uploads a plugin from a directory. Opens a file dialog to select the plugin directory."""

        start_dir = os.path.join(self.path, "plugins")
        plugin_dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Plugin Directory", start_dir, QtWidgets.QFileDialog.Option.ShowDirsOnly)
        if not plugin_dir:
            return  # if no directory is selected, return

        # Make plugin_address relative to the plugins folder if possible, else use absolute path
        try:
            plugin_address = os.path.relpath(plugin_dir, start_dir)
        except ValueError:
            plugin_address = plugin_dir  # fallback to absolute path if relpath fails

        # find .ini file in the plugin directory by iterating through the files
        ini_file = None
        plugin_name = None
        for file in os.listdir(plugin_dir):
            if file.endswith(".ini"):
                ini_file = os.path.join(plugin_dir, file)
            elif file.startswith("pyIVLS_") and file.endswith(".py"):
                plugin_name = file.removeprefix("pyIVLS_").removesuffix(".py")
        if ini_file is None:
            self.show_message("No .ini file found in the plugin directory.")
            return
        if plugin_name is None:
            self.show_message("No file of the form 'pyIVLS_*.py' found in the plugin directory.")
            return
        self.update_config_signal.emit([plugin_address, ini_file, plugin_name])

    #### Internal functions
    def __init__(self, path):
        super().__init__()
        self.path = path
        ui_file_name = path + "components" + sep + "pyIVLS_pluginloader.ui"
        window_option = uic.loadUi(ui_file_name, self)
        if window_option is None:
            print("Cannot open pyIVLS_pluginloader")
            sys.exit(-1)
        else:
            self.window = window_option
            self.listView = self.window.findChild(QtWidgets.QListView, "pluginList")

            self.model = QtGui.QStandardItemModel()
            self.listView.setModel(self.model)

            # Link buttons
            self.applyButton.clicked.connect(self.apply)
            self.uploadButton.clicked.connect(self.upload)
