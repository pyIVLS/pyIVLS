# File: pyIVLS_pluginloader.py
# dialog and functionality for the plugins action from the Tools menu
# This represents the single window opened.

import sys
from os.path import sep

from PyQt6 import QtGui, QtWidgets, uic
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot


class pyIVLS_pluginloader(QtWidgets.QDialog):
    """Gui for the plugin loader"""

    #### Signals for communication

    # Request available plugins from the container
    request_available_plugins_signal = pyqtSignal()
    # Tell the container to register the plugins
    register_plugins_signal = pyqtSignal(list)

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
            plugin_name = f"{properties.get('type')}: {item} ({properties.get('function')}) - Dependencies: {dependencies}"
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

    #### Internal functions
    def __init__(self, path):
        super().__init__()
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
