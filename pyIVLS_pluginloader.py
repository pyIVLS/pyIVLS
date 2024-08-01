# File: pyIVLS_pluginloader.py
# dialog and functionality for the plugins action from the Tools menu
# This represents the single window opened.

from os.path import sep
import sys
import pyIVLS_constants
from configparser import SafeConfigParser

from PyQt6 import QtWidgets, uic, QtGui
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot


class pyIVLS_pluginloader(QtWidgets.QDialog):

    #### Signals for communication
    request_available_plugins_signal = pyqtSignal()
    register_plugins_signal = pyqtSignal(list)

    #### Slots for communication
    @pyqtSlot(dict)
    def populate_list(self, plugins):
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
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == plugin_name:
                item.setCheckState(Qt.CheckState.Checked)

    @pyqtSlot(str)
    def show_message(self, txt):
        msg = QtWidgets.QMessageBox()
        msg.setText(txt)
        msg.setWindowTitle("Warning")
        msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg.exec()

    #### Button actions
    def refresh(self):
        self.request_available_plugins_signal.emit()

    def apply(self):
        plugins = []
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                plugins.append(item.data(Qt.ItemDataRole.UserRole))
        self.register_plugins_signal.emit(plugins)
        self.refresh()

    def configure(self):
        print("Configure button clicked")
        pass

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
            # FIXME: cheking to remove the refresh button. It is not needed.
            # self.refreshButton.clicked.connect(self.refresh)
            self.applyButton.clicked.connect(self.apply)
            self.listView.doubleClicked.connect(self.configure)

    """"
    #### redefine close event####
    ##### https://stackoverflow.com/questions/52747229/pyside-uiloader-capture-close-event-signals
    ##### in fact this is very buggy and not recommended in pyQt, if smth like this is needed GUI classes should be written manually
    def eventFilter(self, watched, event):
        if watched is self.window and event.type() == QEvent.Type.Close:
            self.redefined_closeEvent(event)
            return True
        try:
            return super(pyIVLS_pluginloader, self).eventFilter(watched, event)
        except:
            return True

    def redefined_closeEvent(self, event):
        # if self.window.disconnectButton.isEnabled() or  self.window.stopButton.isEnabled(): #or stop button is enabled
        #   self.show_message("Disconnect RTA first")
        #   event.ignore()
        # else:
        #   self.pyRTAadvancedView.window_advanced.close()
        #   event.accept()
        print("Close button clicked")

    def OK_button_action(self):
        print("OK button clicked")

    def Cancel_button_action(self):
        print("Cancel button clicked")
        
    
    def __init__(self, path):
        super(pyIVLS_pluginloader, self).__init__()
        print("OK")
        ui_file_name = path + "components" + sep + "pyIVLS_pluginloader.ui"
        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODevice.OpenModeFlag.ReadOnly):
            print("Cannot open pyIVLS_pluginloader: {ui_file.errorString()}")
            sys.exit(-1)
        self.window = uic.loadUi(ui_file)
        ui_file.close()
        if not self.window:
            print(loader.errorString())
            sys.exit(-1)


        self.window.installEventFilter(self)

        # redefining the buttons looks like a workaround. In the reality to validate the data you can use done() method of QDialog, but there is no access to it when the class is imported from *.ui
        self.window.OKButton.clicked.connect(self.OK_button_action)
        self.window.cancelButton.clicked.connect(self.Cancel_button_action)

        self.listWidget = self.findChild(QtWidgets.QListWidget, 'pluginList')
        self.populate_plugins(['item1', 'item2', 'item3'])

    def populate_plugins(self, items):
        self.listWidget.clear()
        for item in items:
            list_item = QtWidgets.QListWidgetItem(item)
            list_item.setCheckState(Qt.CheckState.Unchecked)
            self.listWidget.addItem(list_item)
    """
