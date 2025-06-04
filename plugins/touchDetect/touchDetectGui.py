import os
import numpy as np
import cv2

from PyQt6.QtCore import pyqtSignal, QObject, QEventLoop, QEvent
from PyQt6 import uic  
from PyQt6.QtWidgets import QWidget, QComboBox, QGraphicsScene, QGraphicsView
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QObject, QEvent, QEventLoop, Qt, QTimer
from PyQt6.QtWidgets import QGraphicsView

from datetime import datetime


class ViewportClickCatcher(QObject):
    def __init__(self, view: QGraphicsView):
        super().__init__()
        self.view = view
        self._clicked_pos = None
        self._loop = QEventLoop()
        self.view.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                scene_pos = self.view.mapToScene(event.pos())
                self._clicked_pos = (scene_pos.x(), scene_pos.y())
                self._loop.quit()
                return True
        return False

    def wait_for_click(self):
        self._loop.exec()
        self.view.viewport().removeEventFilter(self)
        return self._clicked_pos





class touchDetectGUI(QObject):


    non_public_methods = []  
    public_methods = []  
    CT = 10  # contact threshold in Ohm, default value, can be changed in settings.

    ########Signals
    # signals retained since this plugins needs to communicate during sutter calibration.
    log_message = pyqtSignal(str)
    info_message = pyqtSignal(str)
    def emit_log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        plugin_name = "touchDetect"
        self.log_message.emit(f"{timestamp}: {plugin_name} caught: {message}")

    @property
    def dependency(self):
        return self._dependencies
    
    @dependency.setter
    def dependency(self, value):
        if isinstance(value, list):
            self._dependencies = value
            self.dependencies_changed()
        else:
            raise TypeError("AffineMove: Dependencies must be a list")
    
    ########Functions
    def __init__(self):
        super().__init__()
        self.path = os.path.dirname(__file__) + os.path.sep
        # depenenies are in format plugin: object, metadata: dict.
        self._dependencies = [None, None]

        self.settingsWidget = uic.loadUi(self.path + "touchDetect_Settings.ui")

        # Initialize the combo boxes for dependencies
        self.smu_box: QComboBox = self.settingsWidget.smuBox
        self.micromanipulator_box: QComboBox = self.settingsWidget.micromanipulatorBox
        self.condet_box: QComboBox = self.settingsWidget.condetBox

        # find status labels and indicators
        self.smu_indicator = self.settingsWidget.smuIndicator
        self.mm_indicator = self.settingsWidget.mmIndicator
        self.con_indicator = self.settingsWidget.conIndicator

        # sanity checks
        assert self.settingsWidget is not None, "AffineMove: settingsWidget is None"
        assert self.smu_box is not None, "touchDetect: smu_box is None"
        assert self.micromanipulator_box is not None, "touchDetect: micromanipulator_box is None"
        assert self.condet_box is not None, "touchDetect: condet_box is None"
        assert self.smu_indicator is not None, "touchDetect: smu_indicator is None"
        assert self.mm_indicator is not None, "touchDetect: mm_indicator is None"
        assert self.con_indicator is not None, "touchDetect: con_indicator is None"

        

    ########Functions
    ########GUI Slots


    ########Functions
    ################################### internal

    def _fetch_dep_plugins(self):
        """returns the micromanipulator, smu and contacting plugins based on the current selection in the combo boxes.

        Returns:
            tuple[mm, smu, con]: micromanipulator, camera and positioning plugins.
        Raises:
            AssertionError: if any of the plugins is not found.
        """

        micromanipulator = None
        smu = None
        condet = None
        for plugin, metadata in self.dependency:
            if metadata.get("function") == "micromanipulator":
                current_text = self.micromanipulator_box.currentText()
                if current_text == metadata.get("name"):
                    micromanipulator = plugin
            elif metadata.get("function") == "smu":
                if self.smu_box.currentText() == metadata.get("name"):
                    smu = plugin
            elif metadata.get("function") == "contacting":
                if self.condet_box.currentText() == metadata.get("name"):
                    condet = plugin
        
        assert micromanipulator is not None, "touchDetect: micromanipulator plugin is None"
        assert smu is not None, "touchDetect: smu plugin is None"
        assert condet is not None, "touchDetect: contacting plugin is None"
        
        return micromanipulator, smu, condet


    ########Functions
    ########GUI changes

    def update_status(self):
        """
        Updates the status of the micromanipulator, sample and points.
        This function is called by the micromanipulator plugin when the status changes.
        """
        mm, smu, con = self._fetch_dep_plugins()


    def dependencies_changed(self):
        self.smu_box.clear()
        self.micromanipulator_box.clear()
        self.condet_box.clear()
        
        for plugin, metadata in self.dependency:
            if metadata.get("function") == "micromanipulator":
                self.micromanipulator_box.addItem(metadata.get("name"))
            elif metadata.get("function") == "smu":
                self.smu_box.addItem(metadata.get("name"))
            elif metadata.get("function") == "contacting":
                self.condet_box.addItem(metadata.get("name"))
        self.micromanipulator_box.setCurrentIndex(0)
        self.smu_box.setCurrentIndex(0)
        self.condet_box.setCurrentIndex(0)

    ########Functions
    ########plugins interraction

    def _getLogSignal(self):
        return self.log_message

    def _getInfoSignal(self):
        return self.info_message

    def setup(self, settings) -> QWidget:
        """
        Sets up the GUI for the plugin. This function is called by hook to initialize the GUI.
        """



        return self.settingsWidget


    ########Functions to be used externally

    def contact(self, channel)-> bool:
        """Measures the resistance to determine if contact is made with the sample.
        Returns:
            bool: True if contact is made, False otherwise.
        """
        _, smu, con = self._fetch_dep_plugins()
        res = smu.resistance_measurement(channel=channel)
        if res > self.CT:
            self.emit_log(f"Contact detected on channel {channel} with resistance {res} Ohm.")
            return True
        else:
            return False


    def move_to_sample(self):
        """Moves all (active) micromanipulators down until contact with the sample is detected. 
        This is the main entry point for the plugin.
        # FIXME: Add args on which manipulators to move? This does not know which manipulators are active for certain moves. :(
        """
        mm, smu, con = self._fetch_dep_plugins()




        