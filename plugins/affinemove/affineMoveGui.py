import os

from PyQt6.QtCore import pyqtSignal, QObject, QEventLoop, QEvent
from PyQt6 import uic  
from PyQt6.QtWidgets import QWidget, QComboBox, QGraphicsScene, QGraphicsView
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QObject, QEvent, QEventLoop, Qt
from PyQt6.QtWidgets import QGraphicsView

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
        self.camera_graphic_view: QGraphicsView = self.MDIWidget.cameraview
        self.camera_graphic_scene: QGraphicsScene = QGraphicsScene()
        self.camera_graphic_view.setScene(self.camera_graphic_scene)







    ########Functions
    ########GUI Slots


    ########Functions
    ################################### internal
    def wait_for_input(self) -> tuple[float, float]:
        """
        Waits for a mouse click on the camera graphics view and returns the (x, y)
        position in scene coordinates. This method blocks until a click is received.
        """
        catcher = ViewportClickCatcher(self.camera_graphic_view)
        return catcher.wait_for_click()

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
        
        assert micromanipulator is not None, "AffineMove: micromanipulator plugin is None"
        assert camera is not None, "AffineMove: camera plugin is None"
        assert positioning is not None, "AffineMove: positioning plugin is None"
        
        return micromanipulator, camera, positioning

    def find_sutter_functionality(self):
        mm, cam, pos = self.fetch_dep_plugins()


        status,state = mm.mm_open()
        print(f"Status: {status}, State: {state}")
        if status:
            self.log_message.emit(state["Error message"])



        points = []
        moves = [(0,0),(3000,0), (0, 3000),]
        for move in moves:
            status, state = mm.mm_up_max()
            if status:
                self.log_message.emit(state["Error message"])
            status, state = mm.mm_move_relative(x_change=move[0], y_change=move[1])
            self.update_graphics_view(cam)
            point = self.wait_for_input()
            print(f"Clicked at: {point}")
            x, y, z = mm.mm_current_position()
            print(f"Current position: {x}, {y}, {z}")
            mm_point = (x, y)
            points.append((mm_point, point))

        import numpy as np
        import cv2
        # Compute the affine transformation
        mm_points = np.array([pt[0] for pt in points], dtype=np.float32)
        view_points = np.array([pt[1] for pt in points], dtype=np.float32)
        affine_transform = cv2.getAffineTransform(view_points, mm_points)

        print(f"Affine Transform Matrix:\n{affine_transform}")

        # Wait for a new input and apply the transform
        self.info_message.emit("Click anywhere to move manipulator to that position...")
        click = self.wait_for_input()
        print(f"New click: {click}")

        src = np.array([[click[0], click[1], 1]], dtype=np.float32).T
        mm_target = (affine_transform @ src).flatten()
        print(f"Transformed to manipulator coords: {mm_target}")

        status, state = mm.mm_move(mm_target[0], mm_target[1])
        if status:
            self.log_message.emit(state["Error message"])
        self.update_graphics_view(cam)










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

    def update_graphics_view(self, cam: object):
        """
        Updates the graphics view with the camera image.
        This function is called by the camera plugin when a new image is captured.
        """
        if cam is None:
            self.log_message.emit("Camera plugin is None")
            return
        img = cam.camera_capture_image()
        if img is not None:
            h, w, ch = img.shape
            bytes_per_line = ch * w
            qt_image = QImage(img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.camera_graphic_scene.clear()
            self.camera_graphic_scene.addPixmap(pixmap)
        else:
            self.log_message.emit("Camera image is None")


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

