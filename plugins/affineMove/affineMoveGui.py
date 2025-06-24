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
        self._cancelled = False
        self._loop = QEventLoop()
        self.view.viewport().installEventFilter(self)
        self.view.installEventFilter(self)  # To catch key events

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                scene_pos = self.view.mapToScene(event.pos())
                self._clicked_pos = (scene_pos.x(), scene_pos.y())
                self._loop.quit()
                return True
        elif event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                self._cancelled = True
                self._loop.quit()
                return True
        return False

    def wait_for_click(self):
        self._loop.exec()
        self.view.viewport().removeEventFilter(self)
        self.view.removeEventFilter(self)
        if self._cancelled:
            return None
        return self._clicked_pos





class affineMoveGUI(QObject):


    non_public_methods = []  
    public_methods = ["parse_settings_widget", "affine_move", "setSettings", "getIterations", "sequenceStep", "loopingIteration"]  
    green_style = "border-radius: 10px; background-color: rgb(38, 162, 105); min-height: 20px; min-width: 20px;"
    red_style = "border-radius: 10px; background-color: rgb(165, 29, 45); min-height: 20px; min-width: 20px;"


    ########Signals
    # signals retained since this plugins needs to communicate during sutter calibration.
    log_message = pyqtSignal(str)
    info_message = pyqtSignal(str)
    def emit_log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        plugin_name = "AffineMove"
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
        self._dependencies = [None, None]
        self.calibration_path = os.path.join(self.path, "calibration_data.npy")

        self.settingsWidget = uic.loadUi(self.path + "affinemove_Settings.ui")
        self.MDIWidget = uic.loadUi(self.path + "affinemove_MDI.ui")
        assert self.settingsWidget is not None, "AffineMove: settingsWidget is None"
        assert self.MDIWidget is not None, "AffineMove: MDIWidget is None"

        # Initialize the combo boxes for dependencies
        self.camera_box: QComboBox = self.settingsWidget.cameraBox
        self.micromanipulator_box: QComboBox = self.settingsWidget.micromanipulatorBox
        self.positioning_box: QComboBox = self.settingsWidget.positioningBox
        self.camera_graphic_view: QGraphicsView = self.MDIWidget.cameraview
        self.camera_graphic_scene: QGraphicsScene = QGraphicsScene()
        self.camera_graphic_view.setScene(self.camera_graphic_scene)

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
    def _wait_for_input(self) -> tuple[float, float] | None:
        """
        Waits for a mouse click on the camera graphics view and returns the (x, y)
        position in scene coordinates. This method blocks until a click is received or Esc is pressed.
        Returns None if cancelled.
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
        mm, _, _ = self._fetch_dep_plugins()

        status,state = mm.mm_open()
        if status:
            self.emit_log(f"{state["Error message"]} {state.get("Exception", "")}")
            return
        status, ret = mm.mm_devices()
        if status:
            self.emit_log(f"{state["Error message"]} {state.get("Exception", "")}")
            return
        dev_count, dev_statuses = ret
        # calibrate every available manipulator
        for i, status in enumerate(dev_statuses):
            if status == 1:
                code, status = mm.mm_change_active_device(i+1)
                self.info_message.emit(f"AffineMove: calibrating manipulator {i + 1}.\nClick on the camera view to set calibration points (Esc to cancel)")
                # calibrate
                status, state = mm.mm_calibrate()
                # move to "home"
                status, state = mm.mm_move(12500, 12500)

                points = []
                moves = [(0,0),(3000,0), (0, 3000)]
                for move in moves:
                    status, state = mm.mm_move_relative(x_change=move[0], y_change=move[1])
                    point = self._wait_for_input()
                    if point is None:
                        self.info_message.emit("Calibration cancelled by user.")
                        return
                    x, y, z = mm.mm_current_position()
                    mm_point = (x, y)
                    points.append((mm_point, point))

                # Compute the affine transformation
                mm_points = np.array([pt[0] for pt in points], dtype=np.float32)
                view_points = np.array([pt[1] for pt in points], dtype=np.float32)
                affine_transform = cv2.getAffineTransform(view_points, mm_points)
                self.calibrations[i + 1] = affine_transform

                # back to home
                mm.mm_move(12500, 12500)

        self.update_status()
  
    def _fetch_mask_functionality(self):
        _, _, pos = self._fetch_dep_plugins()
        if pos is None:
            return
        points, names = pos.positioning_measurement_points()
        if points is None or names is None:
            self.info_message.emit("AffineMove: No measurement points available in positioning plugin")
            return
        self.measurement_points = points
        self.measurement_point_names = names

        self.update_status()

    def _initialize_camera_preview(self):
        """
        Initializes the camera preview by starting the and updating the graphics view.
        This function is called when the camera plugin is selected.
        """
        _, cam, _ = self._fetch_dep_plugins()
        thread = cam.camera_thread
        thread.new_frame.connect(self.update_graphics_view)
        cam._previewAction()

    def _save_calibration(self):
        """Write the current calibration data to a file. This implemetation keeps a single calibration file 
        for all manipulators instead of multiple files to choose from. TODO: implement a way to choose where to save and with what name (if really necessary)
        """
        if not self.calibrations:
            self.emit_log("No calibration data to save.")
            return
        
        # Define the file path
        file_path = os.path.join(self.calibration_path)
        
        # Save the calibration data
        np.save(file_path, self.calibrations)
        self.info_message.emit(f"Calibration data saved to {file_path}")

    def _load_calibration(self):
        """Load the calibration data from a file. This implemetation keeps a single calibration file 
        for all manipulators instead of multiple files to choose from. TODO: implement a way to choose where to load from and with what name (if really necessary)
        """
        file_path = os.path.join(self.calibration_path)
        
        if not os.path.exists(file_path):
            self.emit_log(f"No calibration data found at {file_path}")
            return
        
        # Load the calibration data
        self.calibrations = np.load(file_path, allow_pickle=True).item()
        self.info_message.emit(f"Calibration data loaded from {file_path}")
        self.update_status()


        # calibrate all manipulators
        mm, _, _ = self._fetch_dep_plugins()
        status,state = mm.mm_open()
        if status:
            self.emit_log(f"{state["Error message"]} {state.get("Exception", "")}")
            return
        status, ret = mm.mm_devices()
        if status:
            self.emit_log(f"{state["Error message"]} {state.get("Exception", "")}")
            return
        dev_count, dev_statuses = ret
        # calibrate every available manipulator
        for i, status in enumerate(dev_statuses):
            if status == 1:
                code, status = mm.mm_change_active_device(i+1)
                status, state = mm.mm_calibrate()




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
            self.emit_log(f"No calibration data for manipulator {mm_dev}")
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
        self.settingsWidget.fetchMaskButton.clicked.connect(self._fetch_mask_functionality)
        self.settingsWidget.debugButton.clicked.connect(self.affine_move)
        self.settingsWidget.previewButton.clicked.connect(self._initialize_camera_preview)
        self.settingsWidget.saveCalibrationButton.clicked.connect(self._save_calibration)
        self.settingsWidget.loadCalibrationButton.clicked.connect(self._load_calibration)


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

    def update_graphics_view(self, img):
        """
        Updates the graphics view with the camera image.
        This function is called by the camera plugin when a new image is captured.
        """

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
            self.mm_indicator.setStyleSheet(self.red_style)
        else:
            self.mm_indicator.setStyleSheet(self.green_style)

        if pos.positioning_coords((0,0)) == (-1, -1):
            self.sample_indicator.setStyleSheet(self.red_style)
        else:
            self.sample_indicator.setStyleSheet(self.green_style)

        if len(self.measurement_points) == 0:
            self.points_indicator.setStyleSheet(self.red_style)
        else:
            self.points_indicator.setStyleSheet(self.green_style)

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

    def parse_settings_widget(self) -> tuple[int, dict]:
        """
        Parses the settings widget and returns the settings as a dictionary.
        This function is called by the seq builder to get the settings for the plugin.
        """
        settings = {
            "micromanipulator": self.micromanipulator_box.currentText(),
            "camera": self.camera_box.currentText(),
            "positioning": self.positioning_box.currentText(),
        }
        # check if some dependencies are not set
        if not all(settings.values()):
            return 1, {"Error message": "AffineMove : Some dependencies are not set."}
        return 0, settings


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
                return [1, state["Error message"]]
            
            # check if there are measurement points available
            if len(self.measurement_points) == 0:
                return [3, "No measurement points available"]
            
            # reset the iteration if it exceeds the number of measurement points. The goal is in (my opinion) to be able to just call this and it works.
            if self.iter == len(self.measurement_points):
                self.iter = 0
            
            points = self.measurement_points[self.iter]
            point_name = self.measurement_point_names[self.iter]

            # TODO: Add checking for the relative positions of the points and the manipulators. 
            # Should be done to avoid collisions if trying to reach a point on the other side.
            for i, point in enumerate(points):
                mm.mm_change_active_device(i + 1) # manipulators indexed from 0
                mm.mm_up_max()
                # convert the point to camera coordinates
                x, y = pos.positioning_coords(point)
                # convert camera point to micromanipulator coordinates
                x, y = self.convert_to_mm_coords((x, y), i + 1)
                status, state = mm.mm_move(x, y)
                if status:
                    self.emit_log(state["Error message"])
                    return [2, state["Error message"]]
        except Exception as e:
            self.emit_log(f"Error in affine_move: {str(e)}")
            return [2, f"Affine_move: {str(e)}"]
        finally:
            self.iter += 1

        
    # dummy:
    def setSettings(self, settings):
        print(f"set affineMove settings: {settings}")

    def getIterations(self):
        return 10
    
    def sequenceStep(self, namePostfix):
        print(f"sequenceStep called with namePostfix: {namePostfix}")
        return [0, "affineMove: sequenceStep executed"]

    def loopingIteration(self, currentIteration):
        print(f"loopingIteration called with currentIteration: {currentIteration}")
        return [0, f"_iter{currentIteration}"]

