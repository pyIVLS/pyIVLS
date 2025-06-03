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





class affineMoveGUI(QObject):


    non_public_methods = []  
    public_methods = []  
    default_timerInterval = 42 # ms

    ########Signals
    # signals retained since this plugins needs to communicate during sutter calibration.
    log_message = pyqtSignal(str)
    info_message = pyqtSignal(str)
    def emit_log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_message.emit(f"{timestamp}: {message}")

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

        # set up timer for camera view
        self.timer = QTimer()
        self.timer.setInterval(self.default_timerInterval)
        self.timer.timeout.connect(lambda: self.update_graphics_view(self._fetch_dep_plugins()[1]))

        # initialize internal state:
        self.iter = 0
        self.measurement_points = []
        self.measurement_point_names = []
        self.calibrations = {} # manipulator 1, manipulator 2, ... calibration points

        # find status labels and indicators
        self.mm_status = self.settingsWidget.mmStatus
        self.sample_status = self.settingsWidget.sampleStatus
        self.points_status = self.settingsWidget.pointsStatus
        self.mm_indicator = self.settingsWidget.mmIndicator
        self.sample_indicator = self.settingsWidget.sampleIndicator
        self.points_indicator = self.settingsWidget.pointsIndicator
        




    ########Functions
    ########GUI Slots


    ########Functions
    ################################### internal
    def _wait_for_input(self) -> tuple[float, float]:
        """
        Waits for a mouse click on the camera graphics view and returns the (x, y)
        position in scene coordinates. This method blocks until a click is received.
        """
        catcher = ViewportClickCatcher(self.camera_graphic_view)
        return catcher.wait_for_click()

    def _fetch_dep_plugins(self):
        """returns the micromanipulator, camera and positioning plugins based on the current selection in the combo boxes.

        Returns:
            tuple[mm, cam, pos]: micromanipulator, camera and positioning plugins.
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

    def _find_sutter_functionality(self):
        mm, cam, _ = self._fetch_dep_plugins()

        status,state = mm.mm_open()
        print(f"Status: {status}, State: {state}")
        if status:
            self.emit_log(state["Error message"])
        status, state = cam.camera_open()
        print(f"Status: {status}, State: {state}")
        self.timer.start(self.default_timerInterval)
        status, ret = mm.mm_devices()
        if status:
            self.emit_log(ret["Error message"])
            return
        dev_count, dev_statuses = ret
        print(f"Device count: {dev_count}, Device statuses: {dev_statuses}")
        # calibrate every available manipulator
        for i, status in enumerate(dev_statuses):
            print(f"Device {i+1} status: {status}")
            if status == 1:
                print(f"Calibrating manipulator {i+1}")
                code, status = mm.mm_change_active_device(i+1)
                print(f"Status: {code}, State: {status}")
                # move to "home"
                status, state = mm.mm_move(12500, 12500, 0)

                points = []
                moves = [(0,0),(3000,0), (0, 3000)]
                for move in moves:
                    status, state = mm.mm_up_max()
                    if status:
                        self.emit_log(state["Error message"])
                    status, state = mm.mm_move_relative(x_change=move[0], y_change=move[1])
                    point = self._wait_for_input()
                    x, y, z = mm.mm_current_position()
                    mm_point = (x, y)
                    points.append((mm_point, point))


                # Compute the affine transformation
                mm_points = np.array([pt[0] for pt in points], dtype=np.float32)
                view_points = np.array([pt[1] for pt in points], dtype=np.float32)
                affine_transform = cv2.getAffineTransform(view_points, mm_points)
                self.calibrations[i + 1] = affine_transform

                # back to home
                mm.mm_move(12500, 12500, 0)



        self.update_status()
        # removed timer stop so that preview keeps going. 
        # self.timer.stop()    
        
    def _fetch__mask_functionality(self):
        _, _, pos = self._fetch_dep_plugins()
        if pos is None:
            return
        points, names = pos.positioning_measurement_points()
        self.measurement_points = points
        self.measurement_point_names = names

        print(f"Measurement points: {self.measurement_points}")
        print(f"Measurement point names: {self.measurement_point_names}")
        self.update_status()

    def convert_to_mm_coords(self, point: tuple[float, float], mm_dev: int) -> tuple[float, float] | None:
        """
        Converts a point from camera coordinates to micromanipulator coordinates
        using the previously computed affine transformation.

        Args:
            point (tuple): (x, y) point in camera coordinates.
            mm_dev (int): Manipulator device index.

        Returns:
            tuple: Transformed point in manipulator coordinates.
        """
        if mm_dev not in self.calibrations:
            self.emit_log(f"AffineMove: No calibration data for manipulator {mm_dev}")
            return None

        calibration = self.calibrations[mm_dev]  # 2x3 matrix

        # Ensure point is shape (1, 2) — cv2.transform expects shape (N, 2) for 2x3 matrices
        point_np = np.array([point], dtype=np.float32)  # shape (1, 2)

        # Apply affine transformation
        mm_point = cv2.transform(point_np[None, :, :], calibration)[0][0]  # (1,1,2) -> (2,)
        
        return tuple(mm_point)

    ########Functions
    ###############GUI setting up

    def setup(self, settings) -> tuple[QWidget, QWidget]:
        """
        Sets up the GUI for the plugin. This function is called by hook to initialize the GUI."""

        # connect buttons to functions
        self.settingsWidget.findSutter.clicked.connect(self._find_sutter_functionality)
        self.settingsWidget.fetchMaskButton.clicked.connect(self._fetch__mask_functionality)
        self.settingsWidget.debugButton.clicked.connect(self.affine_move)


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
            self.emit_log("Camera plugin is None")
            return
        img = cam.camera_capture_buffered()
        if img is not None:
            h, w, ch = img.shape
            bytes_per_line = ch * w
            qt_image = QImage(img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.camera_graphic_scene.clear()
            self.camera_graphic_scene.addPixmap(pixmap)
        else:
            self.emit_log("Camera image is None")

    def update_status(self):
        """
        Updates the status of the micromanipulator, sample and points.
        This function is called by the micromanipulator plugin when the status changes.
        """
        mm, cam, pos = self._fetch_dep_plugins()
        if self.calibrations == {}:
            self.mm_indicator.setStyleSheet("background-color: red;")
        else:
            self.mm_indicator.setStyleSheet("background-color: green;")

        if pos.positioning_coords((0,0)) == (-1, -1):
            self.sample_indicator.setStyleSheet("background-color: red;")
        else:
            self.sample_indicator.setStyleSheet("background-color: green;")

        if len(self.measurement_points) == 0:
            self.points_indicator.setStyleSheet("background-color: red;")
        else:
            self.points_indicator.setStyleSheet("background-color: green;")

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

    def affine_move(self):
        """This function is the main entry point. It is called from the seq builder to excecute the next measurement point movement. 
        # NOTE: currently accepts no arguments, but might be wise to add some in the future. For instance keeping track of the current iteration?
        # might be implementable with keeping internal track of the current iteration and resetting it to 0 after the last point is reached.
        """
        try:
            mm, _, pos = self._fetch_dep_plugins()

            # check if plugins are available
            if mm is None or pos is None:
                return [3, "AffineMove: micromanipulator or positioning plugin is None"]
            
            # open mm and check for errors
            status, state = mm.mm_open()
            if status:
                print(f"DEBUG: micromanipulator open failed with status {status} and state {state}")
                return [1, state["Error message"]]
            
            # check if there are measurement points available
            if len(self.measurement_points) == 0:
                print("DEBUG: No measurement points available")
                return [3, "No measurement points available"]
            
            # reset the iteration if it exceeds the number of measurement points. The goal is in (my opinion) to be able to just call this and it works.
            if self.iter == len(self.measurement_points):
                print("DEBUG: last point reached, resetting iteration to 0")
                self.iter = 0
            
            points = self.measurement_points[self.iter]
            point_name = self.measurement_point_names[self.iter]
            print(f"DEBUG: Moving to point {point_name} at {points}")

            # TODO: Add checking for the relative positions of the points and the manipulators. 
            # Should be done to avoid collisions if trying to reach a point on the other side.
            for i, point in enumerate(points):
                print(f"DEBUG: Moving manipulator {i + 1} to point {point}")
                mm.mm_change_active_device(i + 1) # manipulators indexed from 0
                # convert the point to camera coordinates
                x, y = pos.positioning_coords(point)
                print(f"DEBUG: Converted point to camera coordinates: {x}, {y}")
                # convert camera point to micromanipulator coordinates
                x, y = self.convert_to_mm_coords((x, y), i + 1)
                print(f"DEBUG: Converted point to micromanipulator coordinates: {x}, {y}")
                status, state = mm.mm_move(x, y)
                if status:
                    self.emit_log(state["Error message"])
                    return [2, state["Error message"]]
        except Exception as e:
            self.emit_log(f"AffineMove: Error in affine_move: {str(e)}")
            return [2, f"Affine_move: {str(e)}"]
        finally:
            self.iter += 1

        