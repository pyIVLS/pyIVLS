import os
import numpy as np
import cv2
import copy

from PyQt6.QtCore import QObject, QEventLoop, QEvent, pyqtSignal
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QComboBox, QGraphicsScene, QGraphicsView
from PyQt6.QtCore import Qt

from plugin_components import (
    public,
    get_public_methods,
    LoggingHelper,
    CloseLockSignalProvider,
    ConnectionIndicatorStyle,
    DependencyManager,
)
from collisionDetection import CollisionDetector
from affineMoveVisualization import AffineMoveVisualization
from components.threadStopped import ThreadStopped


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


class cameraCoordinate:
    def __init__(self, x, y) -> None:
        self._x = x
        self._y = y

    def camera_coords(self) -> tuple[float, float]:
        return (self._x, self._y)

    def mm_coords(self, calibration: np.ndarray) -> tuple[float, float]:
        """
        Converts the camera coordinates to micromanipulator coordinates
        using the provided affine transformation.

        Args:
            calibration (np.ndarray): 2x3 affine transformation matrix.
        """
        # Ensure point is shape (1, 2) — cv2.transform expects shape (N, 2) for 2x3 matrices
        point_np = np.array([(self._x, self._y)], dtype=np.float32)  # shape (1, 2)

        # Apply affine transformation
        mm_point = cv2.transform(point_np[None, :, :], calibration)[0][0]  # (1,1,2) -> (2,)

        return tuple(mm_point)


class manipulatorHandler:
    # Currently unused, but integrating this would help organize this code.
    def __init__(self, idx):
        self.idx = idx
        self.name = f"Manipulator {idx}"
        self.current_position = (0.0, 0.0, 0.0)  # x, y, z
        self.calibration = None  # 2x3 affine transformation matrix
        self.bounding_box = None  # Axis-aligned bounding box in relative coordinates
        self.targets = []  # List of planned target positions

    def get_position_hw(self, mm: dict) -> tuple[float, float, float]:
        """Fetch current position from hardware using micromanipulator plugin functions."""
        status, ret = mm["mm_change_active_device"](self.idx)
        if status != 0:
            raise RuntimeError(f"Error changing active device to {self.idx}: {ret}")
        pos = mm["mm_current_position"]()
        if len(pos) < 3:
            raise RuntimeError(f"Could not retrieve current position for manipulator {self.idx}: {pos}")
        self.current_position = pos
        return pos

    def move_to_position_hw(self, mm: dict, target_mm_pos: tuple[float, float, float]) -> tuple[int, dict]:
        """Move manipulator to target position using micromanipulator plugin functions."""
        status, ret = mm["mm_change_active_device"](self.idx)
        if status != 0:
            return status, ret
        status, ret = mm["mm_move"](target_mm_pos)
        if status != 0:
            return status, ret
        self.current_position = target_mm_pos
        return 0, {"Error message": f"{self.name} moved to mm-coords: {target_mm_pos}"}

    def get_position_camera_coords(self) -> tuple[float, float]:
        """Return camera coordinates of the manipulator"""
        if self.calibration is None:
            raise RuntimeError(f"Manipulator {self.idx} is not calibrated.")
        mm_x, mm_y, _ = self.current_position
        camera_coords = self.convert_mm_to_camera_coords((mm_x, mm_y))
        if camera_coords is None:
            raise RuntimeError(f"Could not convert manipulator {self.idx} position to camera coordinates.")
        return camera_coords

    def convert_to_mm_coords(self, camera_point: tuple[float, float]) -> tuple[float, float]:
        """
        Converts a point from camera coordinates to micromanipulator coordinates
        using the previously computed affine transformation.

        Args:
            camera_point (tuple): (x, y) point in camera coordinates.
            mm_dev (int): Manipulator device index.

        Returns:
            tuple: Transformed point in manipulator coordinates.
        """
        if self.calibration is None:
            raise RuntimeError(f"{self.name} is not calibrated.")

        # Ensure point is shape (1, 2) — cv2.transform expects shape (N, 2) for 2x3 matrices
        point_np = np.array([camera_point], dtype=np.float32)  # shape (1, 2)

        # Apply affine transformation
        mm_point = cv2.transform(point_np[None, :, :], self.calibration)[0][0]  # (1,1,2) -> (2,)

        return tuple(mm_point)

    def convert_mm_to_camera_coords(self, mm_point: tuple[float, float]) -> tuple[float, float]:
        """
        Converts a point from micromanipulator coordinates to camera coordinates
        using the previously computed affine transformation.

        Args:
            point (tuple): (x, y) point in micromanipulator coordinates.
            mm_dev (int): Manipulator device index.

        Returns:
            tuple: Transformed point in camera coordinates.
        """
        if self.calibration is None:
            raise RuntimeError(f"{self.name} is not calibrated.")

        # Invert the affine transformation matrix
        inverse_calibration = cv2.invertAffineTransform(self.calibration)
        # Ensure point is shape (1, 2) — cv2.transform expects shape (N, 2) for 2x3 matrices
        point_np = np.array([mm_point], dtype=np.float32)  # shape (1, 2)

        # Apply affine transformation
        camera_point = cv2.transform(point_np[None, :, :], inverse_calibration)[0][0]  # (1,1,2) -> (2,)

        return tuple(camera_point)


class affineMoveGUI(QObject):
    """Affine Move GUI with dictionary-based plugin architecture."""

    # Signals for thread-safe communication
    update_planned_moves_signal = pyqtSignal(list)  # List of (manipulator_idx, current_pos, target_pos)
    clear_planned_moves_signal = pyqtSignal()
    sequence_completed_signal = pyqtSignal()

    ########Functions
    def __init__(self):
        super().__init__()
        self.path = os.path.dirname(__file__) + os.path.sep
        self.calibration_path = os.path.join(self.path, "calibration_data.npy")

        self.logger = LoggingHelper(self)
        self.cl = CloseLockSignalProvider()

        self.settingsWidget = uic.loadUi(self.path + "affinemove_Settings.ui")  # type: ignore
        self.MDIWidget = uic.loadUi(self.path + "affinemove_MDI.ui")  # type: ignore
        assert self.settingsWidget is not None, "AffineMove: settingsWidget is None"
        assert self.MDIWidget is not None, "AffineMove: MDIWidget is None"

        # Initialize dependency manager
        dependencies = {
            "micromanipulator": ["parse_settings_widget", "mm_get_num_manipulators"],
            "camera": ["parse_settings_widget"],
            "positioning": ["parse_settings_widget"],
        }
        dependency_map = {
            "micromanipulator": "micromanipulatorBox",
            "camera": "cameraBox",
            "positioning": "positioningBox",
        }
        self.dm = DependencyManager("affineMove", dependencies, self.settingsWidget, dependency_map)

        # connect buttons to functions
        self.settingsWidget.findSutter.clicked.connect(self._find_sutter_functionality)
        self.settingsWidget.fetchMaskButton.clicked.connect(self._fetch_mask_functionality)
        self.settingsWidget.previewButton.clicked.connect(self._initialize_camera_preview_functionality)
        self.settingsWidget.saveCalibrationButton.clicked.connect(self._save_calibration_functionality)
        self.settingsWidget.loadCalibrationButton.clicked.connect(self._load_calibration_functionality)
        self.settingsWidget.goToClickButton.clicked.connect(self._go_to_click_functionality)
        self.settingsWidget.updateManipulatorsButton.clicked.connect(self._update_manipulators_functionality)

        # bounding box UI connections
        self.settingsWidget.setBoundingBoxButton.clicked.connect(self._on_set_bounding_box_clicked)
        self.settingsWidget.clearBoundingBoxButton.clicked.connect(self._on_clear_bounding_box_clicked)
        self.settingsWidget.showBoundingBoxesCheckBox.toggled.connect(self._on_show_bounding_boxes_toggled)
        self.settingsWidget.refreshPositionsButton.clicked.connect(self._on_refresh_positions_clicked)
        self.settingsWidget.recalibrateManipulatorButton.clicked.connect(self._on_recalibrate_manipulator_clicked)

        # Initialize the combo boxes for dependencies
        self.camera_box: QComboBox = self.settingsWidget.cameraBox
        self.micromanipulator_box: QComboBox = self.settingsWidget.micromanipulatorBox
        self.positioning_box: QComboBox = self.settingsWidget.positioningBox
        self.manipulator_combo_box: QComboBox = self.settingsWidget.manipulatorComboBox
        self.show_bounding_boxes_checkbox = self.settingsWidget.showBoundingBoxesCheckBox
        self.camera_graphic_view: QGraphicsView = self.MDIWidget.cameraview

        # Initialize manipulator combo box with placeholder warning about non-initialization
        self.manipulator_combo_box.addItem("Select manipulator after updating")

        self.camera_graphic_scene: QGraphicsScene = QGraphicsScene()
        self.camera_graphic_view.setScene(self.camera_graphic_scene)

        # Initialize visualization system
        self.visualization = AffineMoveVisualization(self.camera_graphic_view, self.camera_graphic_scene)

        # initialize internal state:
        self.iter = 0
        self.measurement_points = []
        self.measurement_point_names = []
        self.calibrations = {}  # (manipulator) 1, (manipulator) 2, ... calibration points
        self.settings = {}  # settings dictionary for sequence builder

        # Initialize collision detection system
        self.collision_detector = CollisionDetector()
        self.bounding_boxes_path = os.path.join(self.path, "bounding_boxes_data.npy")

        # Initialize position caching system
        self.cached_manipulator_positions = {}

        # Initialize planned moves tracking
        self.current_sequence = []  # Full sequence of planned moves
        self.sequence_iter = 0  # Current position in sequence
        self.planned_moves_cache = []  # Cache for next moves to display

        # Connect signals for thread-safe communication
        self.update_planned_moves_signal.connect(self._update_planned_moves_slot)
        self.clear_planned_moves_signal.connect(self._clear_planned_moves_slot)
        self.sequence_completed_signal.connect(self._sequence_completed_slot)

        # Load bounding boxes from file on startup
        self._load_bounding_boxes_from_file()

        # find status labels and indicators
        self.mm_status = self.settingsWidget.mmStatus
        self.sample_status = self.settingsWidget.sampleStatus
        self.points_status = self.settingsWidget.pointsStatus
        self.mm_indicator = self.settingsWidget.mmIndicator
        self.sample_indicator = self.settingsWidget.sampleIndicator
        self.points_indicator = self.settingsWidget.pointsIndicator

        # camera status
        self.cam_preview_running = False

    ########Functions
    ########GUI Slots
    # region slots
    def _update_planned_moves_slot(self, planned_moves):
        """
        Thread-safe slot to update planned moves visualization.
        Args:
            planned_moves: List of (manipulator_idx, current_pos, target_pos) tuples
        """
        self.planned_moves_cache = planned_moves
        self._add_visual_overlays()  # Redraw overlays with new planned moves

    def _clear_planned_moves_slot(self):
        """Thread-safe slot to clear planned moves visualization."""
        self.planned_moves_cache = []
        self._add_visual_overlays()  # Redraw overlays without planned moves

    def _sequence_completed_slot(self):
        """Thread-safe slot called when movement sequence is completed."""
        self.current_sequence = []
        self.sequence_iter = 0
        self.planned_moves_cache = []
        self._add_visual_overlays()  # Redraw overlays

    # endregion slots

    ########Functions
    ################################### internal
    # region internal functions
    def _wait_for_input(self) -> tuple[float, float] | None:
        """
        Waits for a mouse click on the camera graphics view and returns the (x, y)
        position in scene coordinates. This method blocks until a click is received or Esc is pressed.
        Returns None if cancelled.
        """
        catcher = ViewportClickCatcher(self.camera_graphic_view)
        return catcher.wait_for_click()

    def _fetch_dep_plugins(self):
        """Returns the micromanipulator, camera and positioning plugins as dictionaries."""

        result = self.dm.validate_and_extract_dependency_settings(self.settings)
        status, state = result
        if status != 0:
            self.logger.log_warn(f"Dependency validation failed: {state}")
            return None, None, None

        func_dict = self.dm.get_function_dict_for_dependencies()
        mm_functions = func_dict["micromanipulator"]
        camera_functions = func_dict["camera"]
        positioning_functions = func_dict["positioning"]

        # Filter to include only the selected plugins of each type
        mm_functions = mm_functions[self.settings["micromanipulator"]]
        camera_functions = camera_functions[self.settings["camera"]]
        positioning_functions = positioning_functions[self.settings["positioning"]]

        self._populate_manipulator_combo_box(mm_functions)

        return mm_functions, camera_functions, positioning_functions

    def calibrate_manipulator(self, idx: int):
        """Calibrate a single manipulator

        Args:
            idx (int): 1-4 manipulator index as named by sutter
        """
        try:
            mm, _, _ = self._fetch_dep_plugins()
            assert mm is not None, "Micromanipulator plugin not available"
            status, state = mm["mm_open"]()
            assert not status, f"Error opening micromanipulator: {state}"
            status, ret = mm["mm_devices"]()
            assert not status, f"Error getting micromanipulator devices: {ret}"
            status, state = mm["mm_change_active_device"](idx)
            assert not status, f"Error changing active micromanipulator device: {state}"
            self.logger.info_popup(f"AffineMove: calibrating manipulator {idx}.\nClick on the camera view to set calibration points (Esc to cancel)")
            points = []
            # get 3 different points
            for i in range(3):
                try:
                    current_pos = mm["mm_current_position"]()
                    if current_pos and len(current_pos) >= 3:
                        self.update_manipulator_position(idx, current_pos)
                except Exception as e:
                    self.logger.log_debug(f"Could not update cached position during calibration: {e}")

                point = self._wait_for_input()
                if point is None:
                    self.logger.info_popup("Calibration cancelled by user.")
                    return
                ret = mm["mm_current_position"]()
                if len(ret) < 3:
                    self.logger.log_warn(f"Could not retrieve current position for manipulator {idx}: {ret}")
                    return
                x, y, z = ret

                self.logger.log_info(f"Clicked point: {point}, current position: ({x}, {y}, {z})")
                mm_point = (x, y)
                points.append((mm_point, point))

            # Compute the affine transformation
            mm_points = np.array([pt[0] for pt in points], dtype=np.float32)
            view_points = np.array([pt[1] for pt in points], dtype=np.float32)
            affine_transform = cv2.getAffineTransform(view_points, mm_points)
            self.calibrations[idx] = affine_transform
            self.logger.info_popup(f"Calibration for manipulator {idx} completed.")

            # finally, refresh all manipulator positions
            self.update_manipulator_position(idx, mm["mm_current_position"]())

        except AssertionError as e:
            self.logger.log_warn(f"Calibration failed: {e}")
        finally:
            # send call to update status which checks whether all manipulators are calibrated
            self.update_status()

    def _on_show_bounding_boxes_toggled(self, checked: bool):
        """Handle the Show Bounding Boxes checkbox toggle"""
        # Force a redraw of the overlay to show/hide bounding boxes
        if hasattr(self, "camera_graphic_view") and self.camera_graphic_view:
            self._add_visual_overlays()

    def _populate_manipulator_combo_box(self, mm_funcs=None):
        """Populate the manipulator combo box with available manipulators"""
        # fetch current idx to preserve selection
        self.manipulator_combo_box.blockSignals(True)
        current_idx = self.manipulator_combo_box.currentIndex()

        if mm_funcs is not None:
            dev_count = mm_funcs["mm_get_num_manipulators"]()
            n = dev_count + 1  # +1 to make it 1-indexed
        else:
            n = 5  # Default to 4 manipulators if no micromanipulator plugin is provided

        self.manipulator_combo_box.clear()
        # Add default options (these can be updated when manipulators are detected)
        for i in range(1, n):
            self.manipulator_combo_box.addItem(f"Manipulator {i}", i)  # userdata contains the idx

        # Restore previous selection if possible
        self.manipulator_combo_box.setCurrentIndex(min(current_idx, self.manipulator_combo_box.count() - 1))  # if previously selected idx is out of range, select last available
        self.manipulator_combo_box.blockSignals(False)

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
            return None

        calibration = self.calibrations[mm_dev]  # 2x3 matrix

        # Ensure point is shape (1, 2) — cv2.transform expects shape (N, 2) for 2x3 matrices
        point_np = np.array([point], dtype=np.float32)  # shape (1, 2)

        # Apply affine transformation
        mm_point = cv2.transform(point_np[None, :, :], calibration)[0][0]  # (1,1,2) -> (2,)

        return tuple(mm_point)

    def convert_mm_to_camera_coords(self, point: tuple[float, float], mm_dev: int) -> tuple[float, float] | None:
        """
        Converts a point from micromanipulator coordinates to camera coordinates
        using the previously computed affine transformation.

        Args:
            point (tuple): (x, y) point in micromanipulator coordinates.
            mm_dev (int): Manipulator device index.

        Returns:
            tuple: Transformed point in camera coordinates.
        """
        if mm_dev not in self.calibrations:
            return None

        calibration = self.calibrations[mm_dev]  # 2x3 matrix
        # Invert the affine transformation matrix
        inverse_calibration = cv2.invertAffineTransform(calibration)
        # Ensure point is shape (1, 2) — cv2.transform expects shape (N, 2) for 2x3 matrices
        point_np = np.array([point], dtype=np.float32)  # shape (1, 2)

        # Apply affine transformation
        camera_point = cv2.transform(point_np[None, :, :], inverse_calibration)[0][0]  # (1,1,2) -> (2,)

        return tuple(camera_point)

    def setup_manipulator_bounding_box(self, manipulator_idx: int) -> tuple[int, str]:
        """
        Interactive setup of manipulator bounding box by clicking two opposite corners on camera view.
        Creates an axis-aligned bounding box defined by two relative coordinates.

        Args:
            manipulator_idx: Manipulator index (1-based)

        Returns:
            tuple: (status, message)
        """
        try:
            self.logger.info_popup(f"Click 2 opposite corners to define axis-aligned bounding box for manipulator {manipulator_idx}. Press ESC to cancel.")

            corners = []
            for i in range(2):
                self.logger.log_info(f"Waiting for corner {i + 1}/2...")
                click_pos = self._wait_for_input()
                if click_pos is None:
                    self.logger.log_info("Bounding box setup cancelled by user.")
                    return 1, "Bounding box setup cancelled"
                corners.append(click_pos)
                self.logger.log_info(f"Corner {i + 1}: ({click_pos[0]:.1f}, {click_pos[1]:.1f})")

            # Convert two corner points to axis-aligned bounding box coordinates
            x1, y1 = corners[0]
            x2, y2 = corners[1]

            # Create axis-aligned bounding box using min/max coordinates
            min_x, max_x = min(x1, x2), max(x1, x2)
            min_y, max_y = min(y1, y2), max(y1, y2)

            # Get current manipulator position in camera coordinates to compute relative coordinates
            current_tip_pos = None
            try:
                mm, _, _ = self._fetch_dep_plugins()
                assert mm is not None, "Micromanipulator plugin not available"
                # Switch to the manipulator and get its position
                code, status = mm["mm_change_active_device"](manipulator_idx)
                if code == 0:
                    mm_pos = mm["mm_current_position"]()
                    if mm_pos and len(mm_pos) >= 2 and manipulator_idx in self.calibrations:
                        # Convert MM coordinates to camera coordinates
                        current_tip_pos = self.convert_mm_to_camera_coords((mm_pos[0], mm_pos[1]), manipulator_idx)
                        if current_tip_pos:
                            self.logger.log_info(f"Current tip position for manipulator {manipulator_idx}: {current_tip_pos}")
                            # Update cached position
                            self.update_manipulator_position(manipulator_idx, mm_pos)
            except Exception as e:
                self.logger.log_debug(f"Could not get current manipulator position: {e}")

            if current_tip_pos:
                # Calculate relative coordinates from tip position
                tip_x, tip_y = current_tip_pos
                relative_coords = [(min_x - tip_x, min_y - tip_y), (max_x - tip_x, max_y - tip_y)]
                self.logger.log_info(f"Storing relative coordinates: {relative_coords}")
            else:
                raise ValueError("Current manipulator position not available, cannot set relative bounding box")

            # Set the bounding box
            status, message = self.set_manipulator_bounding_box(manipulator_idx, relative_coords)

            # If we have tip position, update the collision detector with it
            if current_tip_pos and status == 0:
                self.collision_detector.update_manipulator_tip_position(manipulator_idx, current_tip_pos[0], current_tip_pos[1])

            if status == 0:
                self._add_visual_overlays()  # Refresh visual overlays
                self.logger.info_popup(f"Axis-aligned bounding box set for manipulator {manipulator_idx}")

            return status, message

        except Exception as e:
            return 1, f"Error setting up bounding box: {e}"

    def set_manipulator_bounding_box(self, manipulator_idx: int, relative_coords: list[tuple[float, float]]) -> tuple[int, str]:
        """
        Set a manipulator's bounding box using two relative coordinates.

        Args:
            manipulator_idx: Manipulator index (1-based)
            relative_coords: List of two tuples representing (min_x, min_y) and (max_x, max_y)

        Returns:
            tuple: (status, message)
        """
        try:
            if len(relative_coords) != 2:
                return 1, "Bounding box must be defined by exactly 2 coordinates"

            # Validate coordinates are axis-aligned
            (min_x, min_y), (max_x, max_y) = relative_coords
            if min_x >= max_x or min_y >= max_y:
                return 1, "Invalid bounding box coordinates: min values must be less than max values"

            # Store in CollisionDetector (source of truth)
            success = self.collision_detector.set_manipulator_bounding_box(manipulator_idx, relative_coords)

            if success:
                # Save to file
                self._save_bounding_boxes_to_file()
                return 0, f"Bounding box set for manipulator {manipulator_idx}"
            else:
                return 1, f"Failed to set bounding box for manipulator {manipulator_idx}"

        except Exception as e:
            return 1, f"Error setting bounding box: {e}"

    def clear_manipulator_bounding_box(self, manipulator_idx: int) -> tuple[int, str]:
        """
        Clear the bounding box for a manipulator.

        Args:
            manipulator_idx: Manipulator index (1-based)

        Returns:
            tuple: (status, message)
        """
        # Clear from CollisionDetector (source of truth)
        success = self.collision_detector.clear_manipulator_bounding_box(manipulator_idx)

        if success:
            self._save_bounding_boxes_to_file()  # Save updated bounding boxes to file
            self._add_visual_overlays()  # Refresh visual overlays
            return 0, f"Bounding box cleared for manipulator {manipulator_idx}"
        else:
            return 1, f"No bounding box found for manipulator {manipulator_idx}"

    def _save_bounding_boxes_to_file(self):
        """Save the current bounding box data to a file."""
        try:
            # Get current bounding boxes from CollisionDetector (source of truth)
            current_boxes = self.collision_detector.get_all_bounding_boxes()

            if not current_boxes:
                self.logger.log_debug("No bounding boxes to save")
                return

            # Convert AABB objects to serializable format
            serializable_boxes = {}
            for manipulator_idx, aabb in current_boxes.items():
                serializable_boxes[manipulator_idx] = aabb.get_corners()

            # Save to file
            np.save(self.bounding_boxes_path, serializable_boxes, allow_pickle=True)
            self.logger.log_info(f"Saved {len(current_boxes)} bounding box(es) to {self.bounding_boxes_path}")
        except Exception as e:
            self.logger.log_warn(f"Failed to save bounding box data: {e}")

    def _load_bounding_boxes_from_file(self):
        """Load bounding box data from file on startup and sync with CollisionDetector."""
        file_path = self.bounding_boxes_path

        if not os.path.exists(file_path):
            self.logger.log_debug(f"No bounding box data found at {file_path}")
            return

        try:
            loaded_boxes = np.load(file_path, allow_pickle=True).item()

            # Load bounding boxes into CollisionDetector
            loaded_count = 0
            for manipulator_idx, coords in loaded_boxes.items():
                if len(coords) == 2:
                    converted_coords = coords
                else:
                    self.logger.log_warn(f"Invalid bounding box format for manipulator {manipulator_idx}: {len(coords)} coordinates")
                    continue

                # Store in CollisionDetector
                if self.collision_detector.set_manipulator_bounding_box(manipulator_idx, converted_coords):
                    loaded_count += 1

                # try to update the probe position if available
                try:
                    mm, _, _ = self._fetch_dep_plugins()
                    assert mm is not None, "Micromanipulator plugin not available"
                    code, status = mm["mm_change_active_device"](manipulator_idx)
                    if code == 0:
                        mm_pos = mm["mm_current_position"]()
                        if mm_pos and len(mm_pos) >= 2:
                            self.update_manipulator_position(manipulator_idx, mm_pos)
                            self.collision_detector.update_manipulator_tip_position(manipulator_idx, mm_pos[0], mm_pos[1])
                except Exception as e:
                    self.logger.log_info(f"Could not update cached tip position for manipulator {manipulator_idx}: {e}")

            self.logger.log_info(f"Loaded {loaded_count} bounding box(es) from {file_path}")
        except Exception as e:
            self.logger.log_warn(f"Failed to load bounding box data: {e}")

    # endregion internal functions

    ########Functions
    ############### Button functionality
    # region Button functionalities
    def _find_sutter_functionality(self):
        """Functionality for the find sutter button.
        checks all available manipulators, calibrates all of them.
        """
        mm, _, _ = self._fetch_dep_plugins()
        if mm is None:
            self.logger.log_warn("Micromanipulator plugin not available")
            return

        status, state = mm["mm_open"]()
        if status:
            self.logger.log_info(f"{state['Error message']} {state.get('Exception', '')}")
            return
        status, ret = mm["mm_devices"]()
        if status:
            self.logger.log_info(f"{state['Error message']} {state.get('Exception', '')}")
            return
        dev_count, dev_statuses = ret
        # calibrate every available manipulator
        for i, status in enumerate(dev_statuses):
            if status == 1:
                self.calibrate_manipulator(i + 1)  # + 1 since sutter manipulators are 1-indexed


    def _fetch_mask_functionality(self):
        self.logger.log_debug("Fetching mask functionality from positioning plugin...")
        _, _, pos = self._fetch_dep_plugins()
        if pos is None:
            self.logger.log_warn("Positioning plugin is None in _fetch_mask_functionality")
            return
        points, names = pos["positioning_measurement_points"]()
        if points is None or names is None:
            self.logger.info_popup("AffineMove: No measurement points available in positioning plugin")
            self.logger.log_error("No measurement points or names returned from positioning plugin")
            return
        self.measurement_points = points
        self.measurement_point_names = names
        self.logger.log_info(f"Fetched {len(points)} measurement points from positioning plugin.")
        self.update_status()

    def _initialize_camera_preview_functionality(self):
        """
        Initializes the camera preview by starting the and updating the graphics view.
        This function is called when the camera plugin is selected.
        """
        self.logger.log_debug("Initializing camera preview")
        _, cam, _ = self._fetch_dep_plugins()
        if cam is None:
            self.logger.log_warn("Camera plugin is None in _initialize_camera_preview")
            return
        thread = cam["get_thread"]()
        if thread is None:
            self.logger.log_warn("No active camera thread found")
            self.logger.info_popup("Start camera preview on the camera tab first")
            return
        # connect signal to update the graphics view
        thread.new_frame.connect(self.update_graphics_view)
        self.logger.log_info("Camera preview started")
        self.cam_preview_running = True

    def _save_calibration_functionality(self):
        """Write the current calibration data to a file. This implemetation keeps a single calibration file
        for all manipulators instead of multiple files to choose from. TODO: implement a way to choose where to save and with what name (if really necessary)
        """
        if not self.calibrations:
            self.logger.log_info("No calibration data to save.")
            return

        # Define the file path
        file_path = os.path.join(self.calibration_path)

        # Save the calibration data
        np.save(file_path, self.calibrations)
        self.logger.info_popup(f"Calibration data saved to {file_path}")

    def _go_to_click_functionality(self):
        """Handles the 'Go to Click' button functionality."""
        self.logger.log_debug("Go to Click button pressed")
        try:
            manipulator_idx = self.manipulator_combo_box.currentData()
            assert manipulator_idx is not None, "No manipulator selected."
            mm, _, _ = self._fetch_dep_plugins()
            # check that camera thread is active and plugin is available
            assert self.cam_preview_running, "Camera preview is not running. Start camera preview first."
            assert mm is not None, "Micromanipulator plugin not available"
            self.settingsWidget.goToClickButton.setEnabled(False)  # type: ignore
            self.settingsWidget.goToClickButton.setText("Waiting for click...")  # type: ignore

            click_pos_cam_coords = self._wait_for_input()
            assert click_pos_cam_coords is not None, "Go to Click cancelled by user."

            # convert cam coords to mm coords for selected manipulator
            target_mm_coords = self.convert_to_mm_coords(click_pos_cam_coords, manipulator_idx)
            assert target_mm_coords is not None, f"Manipulator {manipulator_idx} is not calibrated."
            self.logger.log_info(f"Moving manipulator {manipulator_idx} to camera coords {click_pos_cam_coords}, mm coords {target_mm_coords}")
            self.move_manipulator_and_update_bounding_box(manipulator_idx, x=target_mm_coords[0], y=target_mm_coords[1], z=0)
 
            # visual update of cached position
            self._add_visual_overlays()
            return

        except AssertionError as e:
            self.logger.log_warn(f"Error during Go to Click: {e}")
            self.logger.info_popup(f"Error during Go to Click: {e}")
            return

        finally:
            self.settingsWidget.goToClickButton.setEnabled(True)  # type: ignore
            self.settingsWidget.goToClickButton.setText("Go to clicked position")  # type: ignore

    def _update_manipulators_functionality(self):
        """Handles the 'Update Manipulators' button functionality."""
        self.logger.log_debug("Update Manipulators button pressed")
        mm, _, _ = self._fetch_dep_plugins()
        if mm is None:
            self.logger.log_warn("Micromanipulator plugin not available")
            return
        self._populate_manipulator_combo_box(mm_funcs=mm)

    def _load_calibration_functionality(self) -> tuple[int, dict[str, str]]:
        """Load the calibration data from a file. This implemetation keeps a single calibration file
        for all manipulators instead of multiple files to choose from. TODO: implement a way to choose where to load from and with what name (if really necessary)
        """
        file_path = os.path.join(self.calibration_path)

        if not os.path.exists(file_path):
            self.logger.log_info(f"No calibration data found at {file_path}")
            return 1, {"Error message": f"No calibration data found at {file_path}"}

        # calibrate all manipulators
        mm, _, _ = self._fetch_dep_plugins()
        if mm is None:
            self.logger.log_warn("Micromanipulator plugin not available")
            return 1, {"Error message": "Micromanipulator plugin not available"}
        status, state = mm["mm_open"]()
        if status:
            self.logger.log_info(f"{state['Error message']} {state.get('Exception', '')}")
            return status, state
        status, ret = mm["mm_devices"]()
        if status:
            self.logger.log_info(f"{state['Error message']} {state.get('Exception', '')}")
            return status, state
        dev_count, dev_statuses = ret
        # calibrate every available manipulator
        for i, status in enumerate(dev_statuses):
            self.logger.log_info(f"Loading calibration for manipulator {i + 1}, status: {status}")
            if status == 1:
                code, status = mm["mm_change_active_device"](i + 1)
                self.logger.log_info(f"{code} - Changing active device to {i + 1} {status}")
                if code != 0:
                    return 1, {"Error message": f"Error changing active device to {i + 1}: {status.get('Error message', 'Unknown error')}"}
                status, state = mm["mm_calibrate"]()

        # Load the calibration data
        self.calibrations = np.load(file_path, allow_pickle=True).item()
        self.update_status()
        return 0, {"message": f"Calibration data loaded from {file_path}"}

    def _on_set_bounding_box_clicked(self):
        """Handle the Set Bounding Box button click"""
        # Get currently selected manipulator
        manipulator_id = self.manipulator_combo_box.currentData()
        self.setup_manipulator_bounding_box(manipulator_id)

    def _on_clear_bounding_box_clicked(self):
        """Handle the Clear Bounding Box button click"""
        manipulator_id = self.manipulator_combo_box.currentData()
        self.clear_manipulator_bounding_box(manipulator_id)

    def _on_refresh_positions_clicked(self):
        """Handle the Refresh Positions button click"""
        success_count = self.refresh_all_manipulator_positions()
        if success_count > 0:
            self._add_visual_overlays()  # Redraw overlays with updated positions
        else:
            self.logger.info_popup("No manipulator positions updated")

    def _on_recalibrate_manipulator_clicked(self):
        """Handle the Recalibrate Manipulator button click"""
        # Get currently selected manipulator
        manipulator_id = self.manipulator_combo_box.currentData()
        self.calibrate_manipulator(manipulator_id)

    # endregion

    ########Functions
    ###############GUI setting up
    def setup(self, settings):
        """Sets up the GUI for the plugin. This function is called by hook to initialize the GUI."""
        self.logger.log_debug("Setting up affineMove GUI")
        self.dm.setup(settings)

        # Store settings internally (maintain .ini format)
        self.settings = copy.deepcopy(settings)

        self.logger.log_debug("AffineMove GUI setup completed")
        return self.settingsWidget

    ########Functions
    ###############GUI react to change

    def update_graphics_view(self, img):
        """Updates the graphics view with a new camera image using the visualization class."""
        self.visualization.update_graphics_view(img)
        self._add_visual_overlays()  # Redraw overlays after updating image

    def _add_visual_overlays(self):
        """Adds visual overlays using the visualization class."""
        try:
            draw_bounding_boxes = self.show_bounding_boxes_checkbox.isChecked()
            draw_targets = self.settingsWidget.showTargetsCheckBox.isChecked()
            draw_positions = self.settingsWidget.showPositionsCheckBox.isChecked()

            # Get current manipulator positions in camera coordinates
            if draw_positions:
                manipulator_positions = self._get_manipulator_positions_in_camera()
            else:
                manipulator_positions = None

            # Get target coordinates if measurement points are available
            if draw_targets:
                target_coords = self._get_target_coords_in_camera()
            else:
                target_coords = None

            # Prepare data for visualization
            if draw_bounding_boxes:
                bounding_boxes = self.collision_detector.get_all_bounding_boxes()
            else:
                bounding_boxes = None

            # Use visualization class to draw overlays
            self.visualization.add_visual_overlays(
                manipulator_positions=manipulator_positions,
                target_positions=target_coords,
                planned_moves=self.planned_moves_cache,
                bounding_boxes=bounding_boxes,
            )

        except Exception as e:
            self.logger.log_warn(f"Error adding visual overlays: {e}")

    def _get_manipulator_positions_in_camera(self):
        """
        Get current positions of all manipulators in camera coordinates using cached positions.


        Returns:
            dict: Dictionary mapping manipulator index to camera coordinates (x, y) or None
        """
        positions = {}
        try:
            for manipulator_idx in self.cached_manipulator_positions.keys():
                try:
                    cached_pos = self.get_cached_manipulator_position(manipulator_idx)
                    if cached_pos and len(cached_pos) >= 2:
                        # Convert to camera coordinates
                        cam_pos = self.convert_mm_to_camera_coords((cached_pos[0], cached_pos[1]), manipulator_idx)
                        positions[manipulator_idx] = cam_pos
                    else:
                        positions[manipulator_idx] = None
                except Exception as e:
                    self.logger.log_debug(f"Could not convert cached position for manipulator {manipulator_idx}: {e}")
                    positions[manipulator_idx] = None

        except Exception as e:
            self.logger.log_warn(f"Error getting cached manipulator positions: {e}")

        return positions

    def update_manipulator_position(self, manipulator_idx: int, position: tuple) -> None:
        """Update cached position for a manipulator"""
        self.cached_manipulator_positions[manipulator_idx] = position
        # also update collision detector tip position if calibration exists
        if manipulator_idx in self.calibrations:
            try:
                cam_pos = self.convert_mm_to_camera_coords((position[0], position[1]), manipulator_idx)
                if cam_pos:
                    self.collision_detector.update_manipulator_tip_position(manipulator_idx, cam_pos[0], cam_pos[1])
                    self.logger.log_debug(f"Updated bounding box tip for manipulator {manipulator_idx}: {cam_pos}")
            except Exception as e:
                self.logger.log_debug(f"Could not update bounding box tip for manipulator {manipulator_idx}: {e}")

    def get_cached_manipulator_position(self, manipulator_idx: int) -> tuple | None:
        """Get cached position for a manipulator"""
        return self.cached_manipulator_positions.get(manipulator_idx)

    def refresh_all_manipulator_positions(self) -> int:
        """
        Refresh cached positions for all manipulators by querying hardware.
        This should only be called when the user explicitly requests it via the refresh button.
        Returns count of successfully updated positions.
        """
        success_count = 0
        mm, _, _ = self._fetch_dep_plugins()
        if mm is None:
            self.logger.log_warn("Micromanipulator plugin not available")
            return 0
        self.logger.log_info("Querying manipulator positions from hardware...")
        # get currently active manipulator
        status, active_manipulator = mm["mm_get_active_device"]()
        assert status == 0, f"Failed to get active manipulator: {active_manipulator.get('Error message', 'Unknown error')}"
        try:
            # Try to get positions for manipulators 1-4
            for manipulator_idx in range(1, 5):
                try:
                    # Change to this manipulator
                    code, status = mm["mm_change_active_device"](manipulator_idx)
                    if code == 0:  # Success
                        # Get current position from hardware
                        position = mm["mm_current_position"]()
                        if position and len(position) >= 3:
                            self.update_manipulator_position(manipulator_idx, position)

                            # Update bounding box tip position if calibration exists
                            if manipulator_idx in self.calibrations:
                                try:
                                    # Convert MM coordinates to camera coordinates
                                    cam_pos = self.convert_mm_to_camera_coords((position[0], position[1]), manipulator_idx)
                                    if cam_pos:
                                        # Update collision detector with new tip position
                                        self.collision_detector.update_manipulator_tip_position(manipulator_idx, cam_pos[0], cam_pos[1])
                                        self.logger.log_debug(f"Updated bounding box tip for manipulator {manipulator_idx}: {cam_pos}")
                                except Exception as e:
                                    self.logger.log_debug(f"Could not update bounding box tip for manipulator {manipulator_idx}: {e}")

                            success_count += 1
                            self.logger.log_debug(f"Updated position for manipulator {manipulator_idx}: {position}")
                except Exception as e:
                    self.logger.log_debug(f"Could not refresh position for manipulator {manipulator_idx}: {e}")

        except Exception as e:
            self.logger.log_warn(f"Error refreshing manipulator positions: {e}")

        # reset back to original manipulator
        if mm is not None:
            mm["mm_change_active_device"](active_manipulator)
        self.logger.log_info(f"Successfully updated {success_count} manipulator position(s)")
        return success_count

    def move_manipulator_and_update_bounding_box(self, manipulator_idx: int, x: float, y: float, z: float | None = None) -> tuple[int, dict]:
        """
        Wrapper for moving a manipulator that also updates the bounding box tip position.

        Args:
            manipulator_idx: Manipulator index (1-based)
            x, y: Target coordinates in MM coordinates
            z: Optional Z coordinate, if None uses current Z

        Returns:
            tuple: (status, state_dict) from the movement operation
        """
        mm, _, _ = self._fetch_dep_plugins()
        if mm is None:
            return 1, {"Error message": "Micromanipulator plugin not available"}

        # Change to the target manipulator
        code, status = mm["mm_change_active_device"](manipulator_idx)
        if code != 0:
            return code, {"Error message": f"Failed to change to manipulator {manipulator_idx}"}
        if z is not None:
            mm["mm_move"](z=z)  # move z first to prevent scratches
        # Perform the move
        status, state = mm["mm_move"](x=x, y=y)
        if status == 0:  # Success
            # Update cached position
            final_pos = mm["mm_current_position"]()
            if final_pos and len(final_pos) >= 3:
                self.update_manipulator_position(manipulator_idx, final_pos)

                # Update bounding box tip position if calibration exists
                if manipulator_idx in self.calibrations:
                    # Convert MM coordinates to camera coordinates
                    cam_pos = self.convert_mm_to_camera_coords((final_pos[0], final_pos[1]), manipulator_idx)
                    if cam_pos:
                        # Update collision detector with new tip position
                        self.collision_detector.update_manipulator_tip_position(manipulator_idx, cam_pos[0], cam_pos[1])
                        self.logger.log_debug(f"Updated bounding box tip for manipulator {manipulator_idx} to camera coords: {cam_pos}")

            self.logger.log_debug(f"Successfully moved manipulator {manipulator_idx} to ({x}, {y})")

        return status, state

    def _get_target_coords_in_camera(self):
        """
        Get target coordinates for ALL measurement points in camera coordinates.

        Returns:
            dict: Dictionary mapping manipulator_index to camera_coordinates (x, y)
        """
        target_coords = {}

        if not self.measurement_points:
            return target_coords

        try:
            # Get positioning plugin to convert mask coordinates to camera coordinates
            _, _, pos = self._fetch_dep_plugins()
            if pos is None:
                self.logger.log_warn("No positioning plugin available for coordinate conversion")
                return target_coords

            for point_idx, point_set in enumerate(self.measurement_points):
                target_coords[point_idx] = {}

                for device_idx, point in enumerate(point_set, 1):  # device_idx starts from 1
                    if point and len(point) >= 2:
                        # Convert from mask coordinates to camera coordinates using positioning plugin
                        try:
                            camera_x, camera_y = pos["positioning_coords"](point)
                            target_coords[point_idx][device_idx] = (float(camera_x), float(camera_y))
                        except Exception as e:
                            self.logger.log_debug(f"Error converting mask coordinates {point} to camera coordinates: {e}")

        except Exception as e:
            self.logger.log_warn(f"Error getting target coordinates: {e}")

        return target_coords

    def update_status(self):
        """
        Updates the status of the micromanipulator, sample and points.
        This function is called by the micromanipulator plugin when the status changes.
        """
        try:
            mm, cam, pos = self._fetch_dep_plugins()
            assert pos is not None, "Positioning plugin not available"
            assert mm is not None, "Micromanipulator plugin not available"
            self.mm_indicator.setStyleSheet(ConnectionIndicatorStyle.GREEN_CONNECTED.value)

            num_manipulators = mm["mm_get_num_manipulators"]()
            for i in range(1, num_manipulators + 1):
                if i not in self.calibrations.keys():
                    self.mm_indicator.setStyleSheet(ConnectionIndicatorStyle.RED_DISCONNECTED.value)
                    self.logger.log_info(f"Manipulator {i} not calibrated")
                    break

            if pos["positioning_coords"]((0, 0)) == (-1, -1):
                self.sample_indicator.setStyleSheet(ConnectionIndicatorStyle.RED_DISCONNECTED.value)
            else:
                self.sample_indicator.setStyleSheet(ConnectionIndicatorStyle.GREEN_CONNECTED.value)

            if len(self.measurement_points) == 0:
                self.points_indicator.setStyleSheet(ConnectionIndicatorStyle.RED_DISCONNECTED.value)
            else:
                self.points_indicator.setStyleSheet(ConnectionIndicatorStyle.GREEN_CONNECTED.value)
        except AssertionError as e:
            self.logger.log_warn(f"Error updating status indicators: {e}")

    ########Functions
    ########plugins interraction
    def _get_public_methods(self):
        """
        Returns a nested dictionary of public methods for the plugin
        """
        # if the plugin type matches the requested type, return the functions

        return get_public_methods(self)

    def _getLogSignal(self):
        return self.logger.logger_signal

    def _getInfoSignal(self):
        return self.logger.info_popup_signal

    ########Functions to be used externally
    # region public API
    @public
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

        # store targets in settings
        settings["measurement_points"] = self.measurement_points
        settings["measurement_point_names"] = self.measurement_point_names

        # store calibrations in settings
        settings["calibrations"] = self.calibrations

        return 0, settings

    @public
    def setSettings(self, settings):
        """
        Sets the settings for the affineMove plugin. Called by the sequence builder.

        Args:
            settings (dict): A dictionary containing the settings for the affineMove plugin.
        """
        self.settings = settings
        self.logger.log_info(f"AffineMove settings updated: {settings}")
        self.calibrations = settings["calibrations"]
        self.measurement_points = settings["measurement_points"]
        self.measurement_point_names = settings["measurement_point_names"]
        self.update_status()  # segfault?

    @public
    def getIterations(self) -> int:
        """Get the number of iterations for the affineMove plugin. This is the number of measurement points available.

        Returns:
            int: The number of iterations.
        """
        return len(self.measurement_points)

    @public
    def loopingIteration(self, currentIteration):
        """
        Called by the sequence builder during loop execution. Moves to the measurement point
        corresponding to the current iteration with collision detection.

        Args:
            currentIteration (int): The current iteration index (0-based)

        Returns:
            tuple: [status, namePostfix] where status is 0 for success, namePostfix for file naming
        """
        try:
            mm, _, pos = self._fetch_dep_plugins()

            # check if plugins are available
            if mm is None or pos is None:
                return [3, "Dependencies not set for AffineMove"]

            # open mm and check for errors
            status, state = mm["mm_open"]()
            if status:
                self.logger.log_info(f"Error opening micromanipulator: {state.get('Error message', str(state))}")
                return [1, "Sutter HW error"]

            # check if there are measurement points available
            if len(self.measurement_points) == 0:
                self.logger.log_info("No measurement points available")
                return [3, "No measurement points available"]

            # check if currentIteration is valid
            if currentIteration >= len(self.measurement_points):
                self.logger.log_info(f"Invalid iteration {currentIteration}, only {len(self.measurement_points)} points available")
                return [3, f"Invalid iteration {currentIteration}"]

            points = self.measurement_points[currentIteration]  # these are stored as mask coordinates
            point_name = self.measurement_point_names[currentIteration]

            self.logger.log_info(f"Processing iteration {currentIteration}: {point_name}")

            # Convert mask coordinates to camera coordinates
            camera_target_points = []
            for device_idx, mask_point in enumerate(points, 1):
                # Convert mask coordinates to camera coordinates
                camera_coords = pos["positioning_coords"](mask_point)
                if camera_coords == (-1, -1):
                    self.logger.log_warn(f"Failed to convert mask coordinates {mask_point} for manipulator {device_idx}")
                    continue
                camera_target_points.append((device_idx, camera_coords))

            if not camera_target_points:
                self.logger.log_warn("No valid target points after coordinate conversion")
                return [3, f"Invalid iteration {currentIteration}"]

            # Get current positions of all manipulators in camera coordinates
            current_positions = {}
            moves_dict = {}

            for manip_idx, target_camera_coords in camera_target_points:
                try:
                    current_mm_pos = mm["mm_current_position"](manip_idx)
                    if status != 0 or current_mm_pos is None:
                        self.logger.log_warn(f"Failed to get current position for manipulator {manip_idx}")
                        continue
                    # Cache the fresh position
                    self.update_manipulator_position(manip_idx, current_mm_pos)
                except Exception as e:
                    self.logger.log_warn(f"Exception getting position for manipulator {manip_idx}: {e}")
                    continue

                # Convert current MM position to camera coordinates
                current_camera_coords = self.convert_mm_to_camera_coords(current_mm_pos[:2], manip_idx)
                if current_camera_coords is None:
                    self.logger.log_warn(f"Failed to convert current position to camera coordinates for manipulator {manip_idx}")
                    continue

                # Store for collision detection
                current_positions[manip_idx] = current_camera_coords
                moves_dict[manip_idx] = (current_camera_coords, target_camera_coords)

                self.logger.log_info(
                    f"Manipulator {manip_idx}: Current camera ({current_camera_coords[0]:.1f}, {current_camera_coords[1]:.1f}) -> Target ({target_camera_coords[0]:.1f}, {target_camera_coords[1]:.1f})"
                )

            if not moves_dict:
                self.logger.log_warn("No valid moves to execute after position validation")
                return [3, f"Invalid iteration {currentIteration}"]

            # Use collision detection to determine safe movement sequence
            self.logger.log_info("Starting collision detection analysis...")

            # Log bounding box information
            bbox_info = []
            for manip_idx in moves_dict.keys():
                bbox = self.collision_detector.get_bounding_box(manip_idx)
                if bbox:
                    corners = bbox.get_absolute_corners()
                    bbox_info.append(f"M{manip_idx}: tip=({bbox.tip_x:.1f},{bbox.tip_y:.1f}), bbox={corners}")
                else:
                    bbox_info.append(f"M{manip_idx}: no bounding box")
            self.logger.log_info(f"Bounding boxes: {bbox_info}")

            safe_sequence = self.collision_detector.generate_safe_movement_sequence(moves_dict)

            if not safe_sequence:
                self.logger.log_warn("No safe movement sequence found - potential collision risk")
                return [1, f"Invalid iteration {currentIteration} - no safe sequence"]

            self.logger.log_info(f"Safe movement sequence found with {len(safe_sequence)} moves: {safe_sequence}")

            # Preview the planned sequence before execution
            self._preview_planned_sequence(safe_sequence)

            # Execute the moves in the safe sequence
            status, message = self.execute_move_list(safe_sequence)

            if status == 0:
                self.logger.log_info(f"Successfully completed iteration {currentIteration}: {point_name}")
                return [0, f"_iter{currentIteration}_{point_name}"]
            else:
                self.logger.log_warn(f"Movement execution failed: {message}")
                return [1, "Error in movement execution"]

        except ThreadStopped as e:
            mm, _, _ = self._fetch_dep_plugins()
            if mm:
                mm["mm_stop"]()
            self.logger.log_info("Movement thread stopped by user")
            raise e  # re-raise to to signal to seqbuilder
        except Exception as e:
            self.logger.log_info(f"Error in loopingIteration: {str(e)}")
            return [2, f"Error in looping iteration: {str(e)}"]

    @public
    def set_gui_from_settings(self, settings: dict) -> None:
        # placeholder since drawing of points is done straight from the settings, so all updates are automatic.
        pass

    # endregion public API
    def execute_move_list(self, move_sequence: list[tuple[int, tuple[float, float]]]) -> tuple[int, str]:
        """
        Execute a list of manipulator movements in the specified order.

        Args:
            move_sequence: List of (manipulator_idx, target_position) tuples from collision detector.
                          target_position is (x, y) in camera coordinates.

        Returns:
            tuple: (status, message) where status is 0 for success, 1+ for errors
        """
        mm, _, _ = self._fetch_dep_plugins()
        if mm is None:
            return 1, "Micromanipulator plugin not available"

        # Store the full sequence and reset iterator
        self.current_sequence = move_sequence.copy()
        self.sequence_iter = 0

        successful_moves = 0
        total_moves = len(move_sequence)

        self.logger.log_info(f"Executing {total_moves} manipulator moves in sequence")

        for move_idx, (manip_idx, (target_cam_x, target_cam_y)) in enumerate(move_sequence):
            # Update planned moves visualization for the NEXT move
            self._update_planned_moves_visualization(move_idx)

            # Convert target camera coordinates to MM coordinates
            target_mm_coords = self.convert_to_mm_coords((target_cam_x, target_cam_y), manip_idx)
            if target_mm_coords is None:
                self.logger.log_warn(f"Failed to convert coordinates for manipulator {manip_idx}, skipping")
                continue

            target_mm_x, target_mm_y = target_mm_coords

            self.logger.log_info(f"Moving manipulator {manip_idx}: Camera ({target_cam_x:.1f}, {target_cam_y:.1f}) -> MM ({target_mm_x:.3f}, {target_mm_y:.3f})")

            # Execute the move using the wrapper that updates bounding box
            status, state = self.move_manipulator_and_update_bounding_box(manip_idx, target_mm_x, target_mm_y, z=0)

            if status == 0:  # Success
                successful_moves += 1
                self.sequence_iter += 1
                self.logger.log_info(f"Successfully moved manipulator {manip_idx}")

                # Update collision detector with new position
                if manip_idx in self.collision_detector.bounding_boxes:
                    self.collision_detector.bounding_boxes[manip_idx].move_bbox(target_cam_x, target_cam_y)
            else:
                error_msg = state.get("Error message", str(state))
                self.logger.log_warn(f"Failed to move manipulator {manip_idx}: {error_msg}")
                return 1, f"Movement failed for manipulator {manip_idx}: {error_msg}"

        # Signal that sequence is completed
        self.sequence_completed_signal.emit()

        if successful_moves == total_moves:
            self.logger.log_info(f"All {total_moves} manipulator movements completed successfully")
            return 0, f"Successfully completed {successful_moves}/{total_moves} moves"
        else:
            return 1, f"Only {successful_moves}/{total_moves} moves completed successfully"

    def _update_planned_moves_visualization(self, current_move_idx: int):
        """
        Update the visualization to show only the next planned move.
        Thread-safe: emits signal to update UI from main thread.

        Args:
            current_move_idx: Index of the move currently being executed
        """
        if current_move_idx >= len(self.current_sequence):
            # No more moves, clear visualization
            self.clear_planned_moves_signal.emit()
            return

        # Get the current move being executed
        manip_idx, (target_cam_x, target_cam_y) = self.current_sequence[current_move_idx]

        # Get current position in camera coordinates
        cached_pos = self.get_cached_manipulator_position(manip_idx)
        if cached_pos and len(cached_pos) >= 2:
            current_cam_pos = self.convert_mm_to_camera_coords((cached_pos[0], cached_pos[1]), manip_idx)
            if current_cam_pos:
                # Create planned move data: (manipulator_idx, current_pos, target_pos)
                planned_moves = [(manip_idx, current_cam_pos, (target_cam_x, target_cam_y))]

                # Emit signal to update visualization from main thread
                self.update_planned_moves_signal.emit(planned_moves)
                return

        # If we couldn't get current position, clear visualization
        self.clear_planned_moves_signal.emit()

    def _preview_planned_sequence(self, move_sequence: list[tuple[int, tuple[float, float]]]):
        """
        Preview the entire planned sequence by showing trajectory lines for all moves.
        This gives a visual overview before execution starts.

        Args:
            move_sequence: List of (manipulator_idx, target_position) tuples
        """
        preview_moves = []

        for manip_idx, (target_cam_x, target_cam_y) in move_sequence:
            # Get current position in camera coordinates
            cached_pos = self.get_cached_manipulator_position(manip_idx)
            if cached_pos and len(cached_pos) >= 2:
                current_cam_pos = self.convert_mm_to_camera_coords((cached_pos[0], cached_pos[1]), manip_idx)
                if current_cam_pos:
                    preview_moves.append((manip_idx, current_cam_pos, (target_cam_x, target_cam_y)))

        if preview_moves:
            # Emit signal to show preview
            self.update_planned_moves_signal.emit(preview_moves)
            self.logger.log_info(f"Previewing planned sequence with {len(preview_moves)} moves")
