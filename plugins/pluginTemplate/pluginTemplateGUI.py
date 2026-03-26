"""
This is a template for a plugin GUI implementation in pyIVLS

This file should provide
- functions for interaction with other plugins (those that will be exported on get_functions hook call, these should not start with "_")
- functions that will implement functionality of the hooks (see pyIVLS_pluginTemplate)
- GUI functionality - code that interracts with Qt GUI elements from widgets

The standard implementation may (but not must) include
- GUI a Qt widget implementation
- GUI functionality (e.g. pluginTemplateGUI.py) - code that interracts with Qt GUI elements from widgets
- plugin core implementation - a set of functions that may be used outside of GUI
"""

import os
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget
from pluginTemplate import pluginTemplate
from plugin_components import (
    CloseLockSignalProvider,
    public,
    get_public_methods,
    load_widget,
    ini_to_bool,
    LoggingHelper,
    ConnectionIndicatorStyle,
    PyIVLSReturnCode,
    DependencyManager,
)
from MplCanvas import MplCanvas
# this is loade from components directory that contains shared classes


class pluginTemplateGUI(QObject):
    @property
    def settingsWidget(self) -> QWidget:
        if not hasattr(self, "_settingsWidget"):
            raise NotImplementedError("Settings widget not implemented, remove this function if settings widget is not needed.")
        if self._settingsWidget is None:
            raise RuntimeError("Settings widget not initialized.")
        return self._settingsWidget

    @property
    def MDIWidget(self) -> QWidget:
        if not hasattr(self, "_mdiWidget"):
            raise NotImplementedError("MDI widget not implemented, remove this function if MDI widget is not needed.")
        if self._mdiWidget is None:
            raise RuntimeError("MDI widget not initialized.")
        return self._mdiWidget

    def notify_user(self, message: str):
        """Utility to create popup and corresponding log entry for events that should be clearly visible"""
        self.logger.log_info(message)
        self.logger.info_popup(message)

    update_gui_signal = pyqtSignal()

    ########Functions
    def __init__(self):
        super(pluginTemplateGUI, self).__init__()  ### this is needed if the class is a child of QObject

        self.path = os.path.dirname(__file__) + os.path.sep
        # remove load_widget if no widgets are needed
        self._settingsWidget, self._mdiWidget = load_widget(settings=True, mdi=True, path=self.path)

        # Initialize the functionality core that should be independent on GUI
        self.templateFunctionality = pluginTemplate()

        # init settings
        self.settings = {}

        # connect signals and slots
        self._connect_signals()

        # create plot
        self._create_plt()

        # initialize logger
        self.logger = LoggingHelper(self)

        # initialize dependency manager
        self.dm = DependencyManager(
            "pluginTemplate",
            {"camera": ["parse_settings_widget", "setSettings", "set_gui_from_settings"]},
        )
        # initialize closelock if needed
        self.cl = CloseLockSignalProvider()

        # prepare GUI
        self.settingsWidget.doubleSpinBox_float.setRange(0, 1)
        self.settingsWidget.comboBox_categorical.addItems(["option1", "option2", "option3"])
        # HOX: things such as adding items for comboboxes MUST be done here to prevent duplicate entries
        # when initGUI is repeatedly called from pyIVLS_container when plugin list is updated.

    def _connect_signals(self):
        self.settingsWidget.pushButton_doStuff.clicked.connect(self._exampleAction)
        self.update_gui_signal.connect(self._update_gui)

    def _create_plt(self):
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.axes = self.sc.fig.add_subplot(111)
        self.axes.set_xlabel("time (HH:MM)")
        self.axes.set_ylabel(r"Temperature ($^\circ$C)")

        # self.MDIWidget.previewForm.addWidget(self.sc._create_toolbar(self.MDIWidget))
        # self.MDIWidget.previewForm.addWidget(self.sc)

    ########Functions
    ########GUI Slots
    # This section should contain functions that should react to GUI events.

    @pyqtSlot()
    def _exampleAction(self):
        # do something
        print("Button clicked!!")

    @pyqtSlot()
    def _update_gui(self):
        # update GUI elements based on the internal state of the plugin. No type checking here since the internal is always safe.
        self.settingsWidget.doubleSpinBox_float.setValue(self.settings["float"])
        self.settingsWidget.spinBox_integer.setValue(self.settings["int"])
        self.settingsWidget.lineEdit_str.setText(self.settings["str"])
        self.settingsWidget.comboBox_categorical.setCurrentText(self.settings["category"])

        # update combobox for deps
        self.dm.initialize_dependency_selection(self.settings)
        self._refresh_dependency_comboboxes(self.settings)

    def _refresh_dependency_comboboxes(self, settings: dict | None = None):
        available = self.dm.get_available_dependency_plugins().get("camera", [])
        self.settingsWidget.camBox.clear()
        self.settingsWidget.camBox.addItems(available)

        preferred = ""
        if settings is not None:
            preferred = settings.get("camera", "")
        if not preferred:
            preferred = self.settings.get("camera", "") if hasattr(self, "settings") else ""

        if preferred and preferred in available:
            self.settingsWidget.camBox.setCurrentText(preferred)

    @pyqtSlot()
    def _update_plot(self, x, y):
        self.axes.clear()
        self.axes.plot(x, y)
        self.sc.draw()

    ########Functions
    ################################### internal
    def _validate_settings(self, settings: dict) -> tuple[int, str]:
        """Validate settings dict and convert values to correct dtype

        Args:
            settings (dict): settings dict with correct data types, so not the initial .ini dict

        Returns:
            tuple[int, str]: status code, error message (empty if no error)
        """
        try:
            settings["float"] = float(settings["float"])
            settings["int"] = int(settings["int"])
            if not (0 <= settings["float"] <= 1):
                return (1, "Float value should be between 0 and 1.")
            if settings["category"] not in ["option1", "option2", "option3"]:
                return (1, "Category should be one of the following: option1, option2, option3.")
            if settings["int"] < 0:
                return (1, "Integer value should be non-negative.")
            if len(settings["str"]) == 0:
                return (1, "String value should not be empty.")
            return (0, "")
        # catch conversion errors if values read from gui
        except ValueError as e:
            return (1, f"Invalid data type in settings: {e}")

    ########Functions
    ###############GUI setting up
    def _initGUI(
        self,
        plugin_info: dict,
    ):
        """Initialize the GUI components with the provided plugin information.
        This should not set the internal state of the plugin, but only set the GUI elements.
        It should be possible to call this function multiple times without
        side effects. This will in fact be called multiple times, since pyIVLS_container calls get_setup_interface
        every time the pluginlist is updated.

        Args:
            plugin_info (dict): dictionary with settings obtained from plugin_data in pyIVLS_
        """
        # initialize dependency manager with the provided settings to initialize combobox
        self.dm.initialize_dependency_selection(plugin_info)
        self._refresh_dependency_comboboxes(plugin_info)

        # These are unguarded, meaning that a user messing around in the .ini file
        # can cause an unhandled exception here.
        # IMO this is the best way to handle wrong settings on startup, since the crash happens early and before data loss and
        # the error is fairly descriptive. Besides, handling these errors would involve
        # guessing what the value should actually be which could just lead to more pain down the line.

        # set actual values to GUI from plugin info
        self.settingsWidget.doubleSpinBox_float.setValue(float(plugin_info["float"]))
        self.settingsWidget.spinBox_integer.setValue(int(plugin_info["int"]))
        self.settingsWidget.lineEdit_str.setText(plugin_info["str"])
        self.settingsWidget.comboBox_categorical.setCurrentText(plugin_info["category"])

    ########Functions
    ###############GUI react to change

    ########Functions
    ########plugins interraction
    def _get_public_methods(self):
        return get_public_methods(self)

    @public
    def setSettings(self, settings: dict):
        """Set the settings for the templatePlugin.

        Args:
            settings (dict): dictionary with settings for the templatePlugin.
        """
        status, error_message = self._validate_settings(settings)
        if status != 0:
            return (1, {"Error message": error_message})
        self.settings = settings

        # update settings for deps:
        self.dm.set_dependency_settings(settings)

        return (0, {"Error message": "ok"})

    @public
    def set_gui_from_settings(self):
        """Set the GUI elements from the internal settings. This can be used after settings have been updated from an external plugin to update the GUI accordingly."""
        # Here we can assume that self.settings contains the values in correct datatype since they are checked before writing to settings.
        self.update_gui_signal.emit()
        self.dm.update_dep_guis()

    ########Functions to be used externally
    ########Public API
    @public
    def parse_settings_widget(self) -> tuple[int, dict]:
        """Parses the settings widget for the templatePlugin. Extracts current values.
        Checks if values are allowed. Provides settings of template plugin to an external plugin

        Returns (status, settings_dict):
            status: 0 - no error, ~0 - error (add error code later on if needed)
            self.settings
        """
        ts = {}  # init temporary settings dict to store the values before writing to internal

        ts["float"] = self.settingsWidget.doubleSpinBox_float.value()  # doublespinbox returns float
        ts["int"] = self.settingsWidget.spinBox_integer.value()  # spinbox returns int
        ts["str"] = self.settingsWidget.lineEdit_str.text()  # lineedit returns str
        ts["category"] = self.settingsWidget.comboBox_categorical.currentText()  # combobox returns str
        ts["camera"] = self.settingsWidget.camBox.currentText()
        self.dm.set_selected_dependency_plugins({"camera": ts["camera"]})

        # checking may not be necessary if widgets are selected/designed in a way that they do not allow wrong values
        # but checking here might be useful.
        status, error_message = self._validate_settings(ts)
        if status != 0:
            self.notify_user(f"Error in settings: {error_message}")
            return (status, {"Error message": error_message})

        # parse dependency settings:
        status, ts = self.dm.parse_dependencies(ts)
        print("Dependency parsing result: ", ts)
        if status != 0:
            # non zero status means error in parsing dependencies, error message is included in ts dict
            self.notify_user(f"Error in dependency settings: {ts['Error message']}")
            return status, ts

        # all good, write to internal and return
        self.settings = ts
        return (0, ts)
