# File: pyIVLS_pluginloader.py
# dialog and functionality for the plugins action from the Tools menu
# This represents the single window opened.

import sys
from os.path import sep
import os

from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot


class pyIVLS_pluginloader(QtWidgets.QDialog):
    """Gui for the plugin loader"""

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
            self.window: QtWidgets.QDialog = window_option
            self.table_widget: QtWidgets.QTableWidget = self.window.pluginList
            # Link buttons
            self.applyButton.clicked.connect(self.apply)
            self.uploadButton.clicked.connect(self.upload)

    def show_message(self, str):
        msg = QtWidgets.QMessageBox()
        msg.setText(str)
        msg.setWindowTitle("Warning")
        msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msg.setWindowFlags(
            Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowShadeButtonHint
        )
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg.exec()

    #### Signals for communication

    # Request available plugins from the container
    request_available_plugins_signal = pyqtSignal()
    # Tell the container to register the plugins
    register_plugins_signal = pyqtSignal(list, list)
    # Signal to update the config file with a new plugin
    update_config_signal = pyqtSignal(list)

    #### Slots for communication
    @pyqtSlot(dict)
    def populate_list(self, plugins: dict[str, dict[str, str]]):
        """Populates the list of plugins in the plugin GUI. This is called from the container signal "available_plugins_signal".

        Args:
            plugins (dict): dictionary of plugin information from the container.
        """
        self.table_widget.clear()
        self.table_widget.setRowCount(len(plugins))
        self.table_widget.setColumnCount(7)

        # set header labels
        self.table_widget.setHorizontalHeaderLabels(
            ["load", "hidden", "Plugin Name", "Type", "Version", "Function", "Dependencies"]
        )

        for row, (item, properties) in enumerate(plugins.items()):
            # Create the items for each column
            load_item = QtWidgets.QTableWidgetItem()
            hidden_item = QtWidgets.QTableWidgetItem()
            name_item = QtWidgets.QTableWidgetItem(item)
            type_item = QtWidgets.QTableWidgetItem(properties.get("type", "Unknown"))
            version_item = QtWidgets.QTableWidgetItem(properties.get("version", "Unknown"))
            function_item = QtWidgets.QTableWidgetItem(properties.get("function", "Unknown"))
            dependencies_item = QtWidgets.QTableWidgetItem(properties.get("dependencies", "None"))

            # Set checkable for load item and hidden item
            load_item.setFlags(load_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            load_item.setCheckState(Qt.CheckState.Checked if properties["load"] == "True" else Qt.CheckState.Unchecked)
            hidden_item.setFlags(hidden_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            hidden_item.setCheckState(
                Qt.CheckState.Checked if properties["hidden"] == "True" else Qt.CheckState.Unchecked
            )

            # Set the items in the row
            self.table_widget.setItem(row, 0, load_item)
            self.table_widget.setItem(row, 1, hidden_item)
            self.table_widget.setItem(row, 2, name_item)
            self.table_widget.setItem(row, 3, type_item)
            self.table_widget.setItem(row, 4, version_item)
            self.table_widget.setItem(row, 5, function_item)
            self.table_widget.setItem(row, 6, dependencies_item)
        self.table_widget.resizeColumnsToContents()
        # self.table_widget.resizeRowsToContents()
        """        
        self.model.clear()  # Clear the existing items in the model

        for item, properties in plugins.items():
            dependencies = properties.get("dependencies", "")
            if not dependencies:
                dependencies = "None"
            plugin_name = f"{properties.get('type')}: {item} {properties.get('version', '')} ({properties.get('function')}) - Dependencies: {dependencies}"
            list_item = QtGui.QStandardItem(plugin_name)
            list_item.setCheckable(True)
            list_item.setUserTristate(True)  # Allow tristate for checkboxes
            list_item.setCheckState(Qt.CheckState.Unchecked)
            list_item.setFlags(list_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            print(f"Plugin: {item}, Load: {properties.get('load')}, Load Widget: {properties.get('load_widget')}")
            if properties.get("load") == "True":
                if properties.get("load_widget") == "True":
                    list_item.setCheckState(Qt.CheckState.Checked)
                else:
                    list_item.setCheckState(Qt.CheckState.PartiallyChecked)


            

            list_item.setToolTip(item)
            list_item.setData(item, Qt.ItemDataRole.UserRole)

            self.model.appendRow(list_item)
        """

    @pyqtSlot(str)
    def state_changed_asfasfasfasf(self, plugin_name):
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
        hidden = []

        for i in range(self.table_widget.rowCount()):
            load_item = self.table_widget.item(i, 0)
            hidden_item = self.table_widget.item(i, 1)
            if load_item.checkState() == Qt.CheckState.Checked:
                plugin_name = self.table_widget.item(i, 2).text()
                plugin = plugin_name + "_plugin"
                plugins.append(plugin)
                if hidden_item.checkState() == Qt.CheckState.Checked:
                    hidden.append(plugin)
        self.register_plugins_signal.emit(plugins, hidden)
        self.refresh()

    def upload(self):
        """Uploads a plugin from a directory. Opens a file dialog to select the plugin directory."""

        start_dir = os.path.join(self.path, "plugins")
        plugin_dir = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Plugin Directory", start_dir, QtWidgets.QFileDialog.Option.ShowDirsOnly
        )
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
