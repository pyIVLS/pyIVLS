# File: pyIVLS_pluginloader.py
# dialog and functionality for the plugins action from the Tools menu
# This represents the single window opened.

import logging
import os

from compiled_ui.pyivls_pluginloader import Ui_pyIVLSpluginloader
from PySide6 import QtWidgets
from PySide6.QtCore import Qt, Signal, Slot

logger = logging.getLogger(__name__)


class pyIVLS_pluginloader(QtWidgets.QDialog, Ui_pyIVLSpluginloader):
    """Gui for the plugin loader"""

    #### Internal functions
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.setupUi(self)
        # Link buttons
        self.applyButton.clicked.connect(self.apply)
        self.uploadButton.clicked.connect(self.upload)

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
    request_available_plugins_signal = Signal()
    # Tell the container to register the plugins
    register_plugins_signal = Signal(list, list)
    # Signal to update the config file with a new plugin
    update_config_signal = Signal(list)

    #### Slots for communication
    @Slot(dict)
    def populate_list(self, plugins: dict[str, dict[str, str]]):
        """Populates the list of plugins in the plugin GUI. This is called from the container signal "available_plugins_signal".

        Args:
            plugins (dict): dictionary of plugin information from the container.
        """
        self.pluginList.clear()
        self.pluginList.setRowCount(len(plugins))
        self.pluginList.setColumnCount(7)

        # set header labels
        self.pluginList.setHorizontalHeaderLabels(["load", "hidden", "Plugin Name", "Type", "Version", "Function", "Dependencies"])

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
            hidden_item.setCheckState(Qt.CheckState.Checked if properties["hidden"] == "True" else Qt.CheckState.Unchecked)

            # Set the items in the row
            self.pluginList.setItem(row, 0, load_item)
            self.pluginList.setItem(row, 1, hidden_item)
            self.pluginList.setItem(row, 2, name_item)
            self.pluginList.setItem(row, 3, type_item)
            self.pluginList.setItem(row, 4, version_item)
            self.pluginList.setItem(row, 5, function_item)
            self.pluginList.setItem(row, 6, dependencies_item)
        self.pluginList.resizeColumnsToContents()
        # self.table_widget.resizeRowsToContents()

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

        for i in range(self.pluginList.rowCount()):
            load_item = self.pluginList.item(i, 0)
            hidden_item = self.pluginList.item(i, 1)
            name_item = self.pluginList.item(i, 2)
            if load_item is None or hidden_item is None or name_item is None:
                raise ValueError(f"One of the items in row {i} is None. load_item: {load_item}, hidden_item: {hidden_item}, name_item: {name_item}")
            if load_item.checkState() == Qt.CheckState.Checked:
                plugin_name = name_item.text()
                plugin = plugin_name + "_plugin"
                plugins.append(plugin)
                if hidden_item.checkState() == Qt.CheckState.Checked:
                    hidden.append(plugin)
        self.register_plugins_signal.emit(plugins, hidden)
        self.refresh()

    def upload(self):
        """Uploads a plugin from a directory. Opens a file dialog to select the plugin directory."""

        def _process_directory(plugin_dir, start_dir):

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

        start_dir = os.path.join(self.path, "plugins")
        plugin_dir = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select the directory containing the plugins, or a subdirectory to upload a single plugin", start_dir, QtWidgets.QFileDialog.Option.ShowDirsOnly
        )
        # convert both to Path objects for easier comparison (Otherwise we get an error where / \ mismatches on Windows)
        plugin_dir = os.path.abspath(plugin_dir)
        start_dir = os.path.abspath(start_dir)
        if not plugin_dir:
            return  # if no directory is selected, return

        # here we handle the case where the user selects the top directory which contains all plugins.
        print(f"Selected plugin directory: {plugin_dir}, Start directory: {start_dir}")
        if plugin_dir == start_dir:
            logger.debug("User selected the top-level plugins directory. Processing all subdirectories.")
            # iterate through all subdirectories of the plugins directory
            for subdir in os.listdir(start_dir):
                full_subdir = os.path.join(start_dir, subdir)
                if os.path.isdir(full_subdir):
                    _process_directory(full_subdir, start_dir)
        else:
            logger.debug(f"User selected a specific plugin directory: {plugin_dir}. Processing this directory.")
            _process_directory(plugin_dir, start_dir)
