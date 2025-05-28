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

from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6 import uic  
from PyQt6.QtWidgets import QWidget, QComboBox, QGraphicsScene, QGraphicsView
from PyQt6.QtGui import QImage, QPixmap



class affineMoveGUI(QObject):


    non_public_methods = []  
    public_methods = []  

    ########Signals
    # signals retained since this plugins needs to communicate during sutter calibration.
    log_message = pyqtSignal(str)
    info_message = pyqtSignal(str)

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
        self._dependencies = [None, None]


        self.settingsWidget = uic.loadUi(self.path + "affineMove_Settings.ui")
        self.MDIWidget = uic.loadUi(self.path + "affineMove_MDI.ui")
        assert self.settingsWidget is not None, "AffineMove: settingsWidget is None"
        assert self.MDIWidget is not None, "AffineMove: MDIWidget is None"

        # Initialize the combo boxes for dependencies
        self.camera_box: QComboBox = self.settingsWidget.cameraBox
        self.micromanipulator_box: QComboBox = self.settingsWidget.micromanipulatorBox
        self.positioning_box: QComboBox = self.settingsWidget.positioningBox
        camera_graphic_view: QGraphicsView = self.MDIWidget.cameraview
        self.camera_graphic_scene: QGraphicsScene = QGraphicsScene()
        camera_graphic_view.setScene(self.camera_graphic_scene)








    ########Functions
    ########GUI Slots


    ########Functions
    ################################### internal

    def dependencies_changed(self):
        self.camera_box.clear()
        self.micromanipulator_box.clear()
        self.positioning_box.clear()
        
        for plugin, metadata in self.dependency:
            if metadata.get("function") == "micromanipulator":
                self.micromanipulator_box.addItem(metadata.get("name"))
            elif metadata.get("function") == "camera":
                self.camera_box.addItem(metadata.get("name"))
            elif metadata.get("function") == "positioning":
                self.positioning_box.addItem(metadata.get("name"))
        self.micromanipulator_box.setCurrentIndex(0)
        self.camera_box.setCurrentIndex(0)
        self.positioning_box.setCurrentIndex(0)

    

    def fetch_dep_plugins(self):
        """returns the micromanipulator, camera and positioning plugins based on the current selection in the combo boxes.

        Returns:
            Tuple[mm, cam, pos]: micromanipulator, camera and positioning plugins.
        """

        micromanipulator = None
        camera = None
        positioning = None
        for plugin, metadata in self.dependency:


            if metadata.get("function") == "micromanipulator":
                current_text = self.micromanipulator_box.currentText()
                if current_text == metadata.get("name"):
                    micromanipulator = plugin
            elif metadata.get("function") == "camera":
                if self.camera_box.currentText() == metadata.get("name"):
                    camera = plugin
            elif metadata.get("function") == "positioning":
                if self.positioning_box.currentText() == metadata.get("name"):
                    positioning = plugin
        return micromanipulator, camera, positioning


    def find_sutter_functionality(self):
        mm, cam, pos = self.fetch_dep_plugins()


        status,state = mm.mm_open()
        print(f"Status: {status}, State: {state}")
        if status:
            self.log_message.emit(state["Error message"])

        status, state = mm.mm_up_max()
        if status:
            self.log_message.emit(state["Error message"])

        camera_status, camera_state = cam.camera_open()
        if camera_status:
            self.log_message.emit(camera_state["Error message"])

        img = cam.camera_capture_image()


        # update the camera view with the captured image
        self.camera_graphic_scene.clear()
        if img is not None:
            h, w, ch = img.shape
            bytes_per_line = ch * w
            qt_image = QImage(img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.camera_graphic_scene.addPixmap(pixmap)
        else:
            self.log_message.emit("Camera image is None")



        coord_list = pos.positioning_measurement_points()
        print(f"Coord list: {coord_list}")


        
        




        

        
        


    ########Functions
    ###############GUI setting up

    def setup(self, settings) -> tuple[QWidget, QWidget]:
        """
        Sets up the GUI for the plugin. This function is called by hook to initialize the GUI."""

        # connect buttons to functions
        self.settingsWidget.findSutter.clicked.connect(self.find_sutter_functionality)


        return self.settingsWidget, self.MDIWidget



    ########Functions
    ###############GUI react to change



    ########Functions
    ########plugins interraction
    def _get_public_methods(self):
        """
        Returns a nested dictionary of public methods for the plugin
        """
        # if the plugin type matches the requested type, return the functions

        methods = {
            method: getattr(self, method)
            for method in dir(self)
            if callable(getattr(self, method))
            and not method.startswith("__")
            and not method.startswith("_")
            and method not in self.non_public_methods
            and method in self.public_methods
        }
        return methods

    def _getLogSignal(self):
        return self.log_message

    def _getInfoSignal(self):
        return self.info_message




    ########Functions to be used externally
    
