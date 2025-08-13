import os
import itertools
import numpy as np
import cv2

from PyQt6.QtCore import QObject, QEventLoop, QEvent
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QComboBox, QGraphicsScene, QGraphicsView
from PyQt6.QtGui import QImage, QPixmap, QPen, QBrush, QColor, QFont
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem
from PyQt6.QtCore import Qt

from plugin_components import public, get_public_methods, LoggingHelper, CloseLockSignalProvider, ConnectionIndicatorStyle
from .collisionDetection import CollisionDetector


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
    """Affine Move GUI.
    TODO: Uses the object based dependency system, not the method based one.
    TODO: Does not use the standard settings format. The movement points are fetched from the positioning plugin and stored in a list.
    """

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

        self.logger = LoggingHelper(self)
        self.closelock = CloseLockSignalProvider()

        self.settingsWidget = uic.loadUi(self.path + "affinemove_Settings.ui")  # type: ignore
        self.MDIWidget = uic.loadUi(self.path + "affinemove_MDI.ui")  # type: ignore
        assert self.settingsWidget is not None, "AffineMove: settingsWidget is None"
        assert self.MDIWidget is not None, "AffineMove: MDIWidget is None"

        # connect buttons to functions
        self.settingsWidget.findSutter.clicked.connect(self._find_sutter_functionality)
        self.settingsWidget.fetchMaskButton.clicked.connect(self._fetch_mask_functionality)
        self.settingsWidget.previewButton.clicked.connect(self._initialize_camera_preview)
        self.settingsWidget.saveCalibrationButton.clicked.connect(self._save_calibration)
        self.settingsWidget.loadCalibrationButton.clicked.connect(self._load_calibration)

        # bounding box UI connections
        self.settingsWidget.setBoundingBoxButton.clicked.connect(self._on_set_bounding_box_clicked)
        self.settingsWidget.clearBoundingBoxButton.clicked.connect(self._on_clear_bounding_box_clicked)
        self.settingsWidget.showBoundingBoxesCheckBox.toggled.connect(self._on_show_bounding_boxes_toggled)
        self.settingsWidget.refreshPositionsButton.clicked.connect(self._on_refresh_positions_clicked)

        # Initialize the combo boxes for dependencies
        self.camera_box: QComboBox = self.settingsWidget.cameraBox
        self.micromanipulator_box: QComboBox = self.settingsWidget.micromanipulatorBox
        self.positioning_box: QComboBox = self.settingsWidget.positioningBox
        self.manipulator_combo_box: QComboBox = self.settingsWidget.manipulatorComboBox
        self.show_bounding_boxes_checkbox = self.settingsWidget.showBoundingBoxesCheckBox
        self.camera_graphic_view: QGraphicsView = self.MDIWidget.cameraview

        # Initialize manipulator combo box with default options
        self._populate_manipulator_combo_box()
        self.camera_graphic_scene: QGraphicsScene = QGraphicsScene()
        self.camera_graphic_view.setScene(self.camera_graphic_scene)

        # initialize internal state:
        self.iter = 0
        self.measurement_points = []
        self.measurement_point_names = []
        self.calibrations = {}  # manipulator 1, manipulator 2, ... calibration points
        self.settings = {}  # settings dictionary for sequence builder

        # Initialize collision detection system
        self.collision_detector = CollisionDetector(self.logger)
        self.bounding_boxes_path = os.path.join(self.path, "bounding_boxes_data.npy")

        # Initialize position caching system
        self.cached_manipulator_positions = {}

        # Load bounding boxes from file on startup
        self._load_bounding_boxes_from_file()

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

        status, state = mm.mm_open()
        if status:
            self.logger.log_info(f"{state['Error message']} {state.get('Exception', '')}")
            return
        status, ret = mm.mm_devices()
        if status:
            self.logger.log_info(f"{state['Error message']} {state.get('Exception', '')}")
            return
        dev_count, dev_statuses = ret
        # calibrate every available manipulator
        for i, status in enumerate(dev_statuses):
            if status == 1:
                code, status = mm.mm_change_active_device(i + 1)
                self.logger.info_popup(f"AffineMove: calibrating manipulator {i + 1}.\nClick on the camera view to set calibration points (Esc to cancel)")
                # calibrate
                status, state = mm.mm_calibrate()
                self.logger.log_debug(f"Calibration status manipulator {i + 1}: {state.get('Error message', 'Success')}")
                """                
                # move to "home"
                status, state = mm.mm_move(12500, 12500)
                self.logger.log_debug(f"Moved manipulator {i + 1} to home position: {state.get('Error message', 'Success')}")
                """

                points = []
                moves = [(0, 0), (3000, 0), (0, 3000)]
                for move in moves:
                    status, state = mm.mm_move_relative(z_change=-100)  # slightly up to avoid collisions
                    if status:
                        self.logger.log_info(f"Error moving manipulator {i + 1} to calibration position: {state.get('Error message', 'Unknown error')}")
                        return
                    status, state = mm.mm_move_relative(x_change=move[0], y_change=move[1])
                    if status:
                        self.logger.log_info(f"Error moving manipulator {i + 1} to calibration position: {state.get('Error message', 'Unknown error')}")
                        return

                    # Update cached position after move
                    try:
                        current_pos = mm.mm_current_position()
                        if current_pos and len(current_pos) >= 3:
                            self.update_manipulator_position(i + 1, current_pos)
                    except Exception as e:
                        self.logger.log_debug(f"Could not update cached position during calibration: {e}")

                    point = self._wait_for_input()
                    if point is None:
                        self.logger.info_popup("Calibration cancelled by user.")
                        return
                    x, y, z = mm.mm_current_position()
                    self.logger.log_debug(f"Clicked point: {point}, current position: ({x}, {y}, {z})")
                    mm_point = (x, y)
                    points.append((mm_point, point))

                # Compute the affine transformation
                mm_points = np.array([pt[0] for pt in points], dtype=np.float32)
                view_points = np.array([pt[1] for pt in points], dtype=np.float32)
                affine_transform = cv2.getAffineTransform(view_points, mm_points)
                self.calibrations[i + 1] = affine_transform

                """
                # back to home
                mm.mm_move(12500, 12500)
                """

        self.update_status()

    def _fetch_mask_functionality(self):
        self.logger.log_debug("Fetching mask functionality from positioning plugin...")
        _, _, pos = self._fetch_dep_plugins()
        if pos is None:
            self.logger.log_warn("Positioning plugin is None in _fetch_mask_functionality")
            return
        points, names = pos.positioning_measurement_points()
        if points is None or names is None:
            self.logger.info_popup("AffineMove: No measurement points available in positioning plugin")
            self.logger.log_error("No measurement points or names returned from positioning plugin")
            return
        self.measurement_points = points
        self.measurement_point_names = names
        self.logger.log_info(f"Fetched {len(points)} measurement points from positioning plugin.")
        self.update_status()

    def _initialize_camera_preview(self):
        """
        Initializes the camera preview by starting the and updating the graphics view.
        This function is called when the camera plugin is selected.
        """
        self.logger.log_debug("Initializing camera preview")
        _, cam, _ = self._fetch_dep_plugins()
        thread = cam.camera_thread
        # connect signal to update the graphics view
        thread.new_frame.connect(self.update_graphics_view)
        # starts the thread
        cam._previewAction()
        self.logger.log_info("Camera preview started")

    def _on_set_bounding_box_clicked(self):
        """Handle the Set Bounding Box button click"""
        # Get currently selected manipulator
        current_text = self.manipulator_combo_box.currentText()
        if not current_text:
            self.logger.info_popup("Please select a manipulator first")
            return

        # Extract manipulator number from text like "Manipulator 1", "Manipulator 2", etc.
        try:
            manipulator_id = int(current_text.split()[-1])
        except (ValueError, IndexError):
            self.logger.info_popup("Invalid manipulator selection")
            return

        self.setup_manipulator_bounding_box(manipulator_id)

    def _on_clear_bounding_box_clicked(self):
        """Handle the Clear Bounding Box button click"""
        # Get currently selected manipulator
        current_text = self.manipulator_combo_box.currentText()
        if not current_text:
            self.logger.info_popup("Please select a manipulator first")
            return

        # Extract manipulator number from text
        try:
            manipulator_id = int(current_text.split()[-1])
        except (ValueError, IndexError):
            self.logger.info_popup("Invalid manipulator selection")
            return

        self.clear_manipulator_bounding_box(manipulator_id)

    def _on_show_bounding_boxes_toggled(self, checked: bool):
        """Handle the Show Bounding Boxes checkbox toggle"""
        # Force a redraw of the overlay to show/hide bounding boxes
        if hasattr(self, "camera_graphic_view") and self.camera_graphic_view:
            self._add_visual_overlays()

    def _populate_manipulator_combo_box(self):
        """Populate the manipulator combo box with available manipulators"""
        self.manipulator_combo_box.clear()

        # Add default options (these can be updated when manipulators are detected)
        for i in range(1, 5):  # Support up to 4 manipulators
            self.manipulator_combo_box.addItem(f"Manipulator {i}")

    def _on_refresh_positions_clicked(self):
        """Handle the Refresh Positions button click"""
        success_count = self.refresh_all_manipulator_positions()
        if success_count > 0:
            self._add_visual_overlays()  # Redraw overlays with updated positions
        else:
            self.logger.info_popup("No manipulator positions updated")

    def _save_calibration(self):
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

    def _load_calibration(self) -> tuple[int, dict[str, str]]:
        """Load the calibration data from a file. This implemetation keeps a single calibration file
        for all manipulators instead of multiple files to choose from. TODO: implement a way to choose where to load from and with what name (if really necessary)
        """
        file_path = os.path.join(self.calibration_path)

        if not os.path.exists(file_path):
            self.logger.log_info(f"No calibration data found at {file_path}")
            return 1, {"Error message": f"No calibration data found at {file_path}"}

        # calibrate all manipulators
        mm, _, _ = self._fetch_dep_plugins()
        status, state = mm.mm_open()
        if status:
            self.logger.log_info(f"{state['Error message']} {state.get('Exception', '')}")
            return status, state
        status, ret = mm.mm_devices()
        if status:
            self.logger.log_info(f"{state['Error message']} {state.get('Exception', '')}")
            return status, state
        dev_count, dev_statuses = ret
        # calibrate every available manipulator
        for i, status in enumerate(dev_statuses):
            self.logger.log_info(f"Loading calibration for manipulator {i + 1}, status: {status}")
            if status == 1:
                code, status = mm.mm_change_active_device(i + 1)
                self.logger.log_info(f"{code} - Changing active device to {i + 1} {status}")
                if code != 0:
                    return 1, {"Error message": f"Error changing active device to {i + 1}: {status.get('Error message', 'Unknown error')}"}
                status, state = mm.mm_calibrate()

        # Load the calibration data
        self.calibrations = np.load(file_path, allow_pickle=True).item()
        self.update_status()
        return 0, {"message": f"Calibration data loaded from {file_path}"}

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
            self.logger.log_info(f"No calibration data for manipulator {mm_dev}")
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
            self.logger.log_info(f"No calibration data for manipulator {mm_dev}")
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
                    return 1, "Bounding box setup cancelled"
                corners.append(click_pos)
                self.logger.log_info(f"Corner {i + 1}: ({click_pos[0]:.1f}, {click_pos[1]:.1f})")

            # Convert two corner points to axis-aligned bounding box coordinates
            x1, y1 = corners[0]
            x2, y2 = corners[1]

            # Create axis-aligned bounding box using min/max coordinates
            min_x, max_x = min(x1, x2), max(x1, x2)
            min_y, max_y = min(y1, y2), max(y1, y2)

            # Define relative coordinates as (min_x, min_y) and (max_x, max_y)
            relative_coords = [(min_x, min_y), (max_x, max_y)]

            # Set the bounding box
            status, message = self.set_manipulator_bounding_box(manipulator_idx, relative_coords)
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

    def clear_all_bounding_boxes(self) -> tuple[int, str]:
        """
        Clear all manipulator bounding boxes.

        Returns:
            tuple: (status, message)
        """
        # Get count before clearing
        indices = self.collision_detector.get_manipulator_indices()
        count = len(indices)

        # Clear all from CollisionDetector
        for manipulator_idx in indices:
            self.collision_detector.clear_manipulator_bounding_box(manipulator_idx)

        # Save to file
        self._save_bounding_boxes_to_file()
        self._add_visual_overlays()  # Refresh visual overlays
        return 0, f"Cleared {count} bounding box(es)"

    def _save_bounding_boxes_to_file(self):
        """Save the current bounding box data to a file."""
        try:
            # Get current bounding boxes from CollisionDetector (source of truth)
            current_boxes = self.collision_detector.get_manipulator_bounding_boxes()

            if not current_boxes:
                self.logger.log_debug("No bounding boxes to save")
                return

            # Save to file
            np.save(self.bounding_boxes_path, current_boxes, allow_pickle=True)
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
                # Check if coords is in old format (4 corners) or new format (2 coords)
                if len(coords) == 4:
                    # Convert from old 4-corner format to new 2-coordinate format
                    self.logger.log_info(f"Converting bounding box for manipulator {manipulator_idx} from old format")
                    # Extract min/max coordinates from the 4 corners
                    x_coords = [corner[0] for corner in coords]
                    y_coords = [corner[1] for corner in coords]
                    min_x, max_x = min(x_coords), max(x_coords)
                    min_y, max_y = min(y_coords), max(y_coords)
                    converted_coords = [(min_x, min_y), (max_x, max_y)]
                elif len(coords) == 2:
                    # Already in new format
                    converted_coords = coords
                else:
                    self.logger.log_warn(f"Invalid bounding box format for manipulator {manipulator_idx}: {len(coords)} coordinates")
                    continue

                # Store in CollisionDetector
                if self.collision_detector.set_manipulator_bounding_box(manipulator_idx, converted_coords):
                    loaded_count += 1

            self.logger.log_info(f"Loaded {loaded_count} bounding box(es) from {file_path}")
        except Exception as e:
            self.logger.log_warn(f"Failed to load bounding box data: {e}")

    ########Functions
    ###############GUI setting up

    def setup(self, settings) -> tuple[QWidget, QWidget]:
        """
        Sets up the GUI for the plugin. This function is called by hook to initialize the GUI."""

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

        # Refresh manipulator positions when micromanipulator plugin becomes available
        try:
            if self.micromanipulator_box.count() > 0:
                self.refresh_all_manipulator_positions()
                self.logger.log_debug("Refreshed manipulator positions after dependency change")
        except Exception as e:
            self.logger.log_debug(f"Could not refresh positions after dependency change: {e}")

    def update_graphics_view(self, img):
        """
        Updates the graphics view with the camera image and visual overlays.
        This function is called by the camera plugin when a new image is captured.
        """
        if img is not None:
            h, w, ch = img.shape
            bytes_per_line = ch * w
            qt_image = QImage(img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.camera_graphic_scene.clear()
            self.camera_graphic_scene.addPixmap(pixmap)

            # Add visual overlays
            self._add_visual_overlays()
        else:
            self.logger.log_warn("Camera image is None in update_graphics_view.")

    def _add_visual_overlays(self):
        """
        Adds visual overlays to the camera view showing manipulator positions,
        target coordinates, and movement trajectories.
        """
        try:
            mm, cam, pos = self._fetch_dep_plugins()
            if mm is None:
                return

            # Get current manipulator positions in camera coordinates
            manipulator_positions = self._get_manipulator_positions_in_camera(mm)

            # Get target coordinates if measurement points are available
            target_coords = self._get_target_coords_in_camera()

            # Draw manipulator position dots
            for i, (mm_idx, cam_pos) in enumerate(manipulator_positions.items()):
                if cam_pos is not None:
                    self._draw_manipulator_dot(cam_pos, mm_idx)

            # Draw target coordinate dots and trajectory lines
            if target_coords and len(self.measurement_points) > 0:
                current_targets = target_coords.get(self.iter, {}) if hasattr(self, "iter") else {}
                for mm_idx, target_pos in current_targets.items():
                    if target_pos is not None:
                        # Draw target dot
                        self._draw_target_dot(target_pos, mm_idx)

                        # Draw trajectory line if we have both current and target positions
                        if mm_idx in manipulator_positions and manipulator_positions[mm_idx] is not None:
                            self._draw_trajectory_line(manipulator_positions[mm_idx], target_pos, mm_idx)

                            # Check for potential collision
                            self._check_and_visualize_collision(mm_idx, manipulator_positions, current_targets)

            # Draw manipulator bounding boxes
            self._draw_manipulator_bounding_boxes()

        except Exception as e:
            self.logger.log_warn(f"Error adding visual overlays: {e}")

    def _get_manipulator_positions_in_camera(self, mm):
        """
        Get current positions of all manipulators in camera coordinates using cached positions.

        Args:
            mm: Micromanipulator plugin instance (kept for compatibility but not used for position queries)

        Returns:
            dict: Dictionary mapping manipulator index to camera coordinates (x, y) or None
        """
        positions = {}
        try:
            # Use cached positions instead of querying hardware
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

    def _get_target_coords_in_camera(self):
        """
        Get target coordinates for all measurement points in camera coordinates.

        Returns:
            dict: Dictionary mapping measurement point index to {manipulator_index: camera_coordinates}
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
                            camera_x, camera_y = pos.positioning_coords(point)
                            target_coords[point_idx][device_idx] = (float(camera_x), float(camera_y))
                            self.logger.log_debug(f"Point {point_idx}, manipulator {device_idx}: mask {point} → camera ({camera_x:.1f}, {camera_y:.1f})")
                        except Exception as e:
                            self.logger.log_debug(f"Error converting mask coordinates {point} to camera coordinates: {e}")
                            target_coords[point_idx][device_idx] = None
                    else:
                        target_coords[point_idx][device_idx] = None

        except Exception as e:
            self.logger.log_warn(f"Error getting target coordinates: {e}")

        return target_coords

    def _draw_manipulator_dot(self, cam_pos, mm_idx):
        """Draw a dot representing current manipulator position."""
        if cam_pos is None:
            return

        x, y = cam_pos
        dot_size = 10

        # Different colors for different manipulators
        colors = [QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255), QColor(255, 255, 0)]
        color = colors[(mm_idx - 1) % len(colors)]

        pen = QPen(color, 2)
        brush = QBrush(color)

        ellipse = QGraphicsEllipseItem(x - dot_size / 2, y - dot_size / 2, dot_size, dot_size)
        ellipse.setPen(pen)
        ellipse.setBrush(brush)
        self.camera_graphic_scene.addItem(ellipse)

    def _draw_target_dot(self, target_pos, mm_idx):
        """Draw a dot representing target position."""
        if target_pos is None:
            return

        x, y = target_pos
        dot_size = 8

        # Same colors as manipulator dots but with hollow center
        colors = [QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255), QColor(255, 255, 0)]
        color = colors[(mm_idx - 1) % len(colors)]

        pen = QPen(color, 2)
        brush = QBrush(Qt.BrushStyle.NoBrush)  # Hollow

        ellipse = QGraphicsEllipseItem(x - dot_size / 2, y - dot_size / 2, dot_size, dot_size)
        ellipse.setPen(pen)
        ellipse.setBrush(brush)
        self.camera_graphic_scene.addItem(ellipse)

    def _draw_trajectory_line(self, current_pos, target_pos, mm_idx):
        """Draw a faint line between current and target positions."""
        if current_pos is None or target_pos is None:
            return

        x1, y1 = current_pos
        x2, y2 = target_pos

        # Same colors as manipulator dots but more transparent
        colors = [QColor(255, 0, 0, 80), QColor(0, 255, 0, 80), QColor(0, 0, 255, 80), QColor(255, 255, 0, 80)]
        color = colors[(mm_idx - 1) % len(colors)]

        pen = QPen(color, 1, Qt.PenStyle.DashLine)

        line = QGraphicsLineItem(x1, y1, x2, y2)
        line.setPen(pen)
        self.camera_graphic_scene.addItem(line)

    def _draw_manipulator_bounding_boxes(self):
        """
        Draw bounding boxes for all manipulators that have them defined.
        Uses CollisionDetector to get current bounding boxes.
        """
        # Check if bounding boxes should be shown
        if not self.show_bounding_boxes_checkbox.isChecked():
            return

        # Get all manipulators with bounding boxes from CollisionDetector
        for manipulator_idx in self.collision_detector.get_manipulator_indices():
            # Get absolute bounding box coordinates based on current manipulator position
            absolute_coords = self.get_absolute_bounding_box(manipulator_idx)
            if absolute_coords:
                self._draw_bounding_box(absolute_coords, manipulator_idx)
            else:
                self.logger.log_debug(f"Cannot draw bounding box for manipulator {manipulator_idx}: position not available")

    def _draw_bounding_box(self, coords: list[tuple[float, float]], manipulator_idx: int):
        """
        Draw a single axis-aligned bounding box on the camera view.

        Args:
            coords: List of 2 coordinates [(min_x, min_y), (max_x, max_y)] in camera coordinates
            manipulator_idx: Manipulator index for color coding
        """
        if len(coords) != 2:
            self.logger.log_warn(f"Invalid bounding box coordinates for manipulator {manipulator_idx}: expected 2 coords, got {len(coords)}")
            return

        (min_x, min_y), (max_x, max_y) = coords

        # Validate coordinates
        if min_x >= max_x or min_y >= max_y:
            self.logger.log_warn(f"Invalid bounding box for manipulator {manipulator_idx}: min >= max")
            return

        # Choose color based on manipulator index
        colors = [
            QColor(255, 0, 0),  # Red for manipulator 1
            QColor(0, 255, 0),  # Green for manipulator 2
            QColor(0, 0, 255),  # Blue for manipulator 3
            QColor(255, 255, 0),  # Yellow for manipulator 4
        ]
        color = colors[(manipulator_idx - 1) % len(colors)]

        # Create pen for drawing
        pen = QPen(color, 2, Qt.PenStyle.SolidLine)

        # Calculate all four corners of the axis-aligned rectangle
        corners = [
            (min_x, min_y),  # Top-left
            (max_x, min_y),  # Top-right
            (max_x, max_y),  # Bottom-right
            (min_x, max_y),  # Bottom-left
        ]

        # Draw the bounding box as connected lines
        for i in range(4):
            start_point = corners[i]
            end_point = corners[(i + 1) % 4]

            line = QGraphicsLineItem(start_point[0], start_point[1], end_point[0], end_point[1])
            line.setPen(pen)
            self.camera_graphic_scene.addItem(line)

        # Add a label for the manipulator
        text_pos = (min_x, min_y)  # Use top-left corner for text position
        text_item = self.camera_graphic_scene.addText(f"M{manipulator_idx}", QFont("Arial", 10))
        if text_item:
            text_item.setPos(text_pos[0], text_pos[1] - 20)
            text_item.setDefaultTextColor(color)

    def update_status(self):
        """
        Updates the status of the micromanipulator, sample and points.
        This function is called by the micromanipulator plugin when the status changes.
        """
        mm, cam, pos = self._fetch_dep_plugins()
        if self.calibrations == {}:
            self.mm_indicator.setStyleSheet(ConnectionIndicatorStyle.RED_DISCONNECTED.value)
        else:
            self.mm_indicator.setStyleSheet(ConnectionIndicatorStyle.GREEN_CONNECTED.value)

        if pos.positioning_coords((0, 0)) == (-1, -1):
            self.sample_indicator.setStyleSheet(ConnectionIndicatorStyle.RED_DISCONNECTED.value)
        else:
            self.sample_indicator.setStyleSheet(ConnectionIndicatorStyle.GREEN_CONNECTED.value)

        if len(self.measurement_points) == 0:
            self.points_indicator.setStyleSheet(ConnectionIndicatorStyle.RED_DISCONNECTED.value)
        else:
            self.points_indicator.setStyleSheet(ConnectionIndicatorStyle.GREEN_CONNECTED.value)

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
        corresponding to the current iteration.

        Args:
            currentIteration (int): The current iteration index (0-based)

        Returns:
            tuple: [status, namePostfix] where status is 0 for success, namePostfix for file naming
        """
        try:
            mm, _, pos = self._fetch_dep_plugins()

            # check if plugins are available
            if mm is None or pos is None:
                return [3, f"_error_iter{currentIteration}"]

            # open mm and check for errors
            status, state = mm.mm_open()
            if status:
                self.logger.log_info(f"Error opening micromanipulator: {state.get('Error message', str(state))}")
                return [1, f"_error_iter{currentIteration}"]

            # check if there are measurement points available
            if len(self.measurement_points) == 0:
                self.logger.log_info("No measurement points available")
                return [3, f"_error_iter{currentIteration}"]

            # check if currentIteration is valid
            if currentIteration >= len(self.measurement_points):
                self.logger.log_info(f"Invalid iteration {currentIteration}, only {len(self.measurement_points)} points available")
                return [3, f"_error_iter{currentIteration}"]

            points = self.measurement_points[currentIteration]
            point_name = self.measurement_point_names[currentIteration]

            # Check for bounding box collision before movement and get safe movement sequence
            is_safe, collision_info, safe_moves = self._check_bounding_box_collision(mm, points)

            if not is_safe:
                if safe_moves:
                    # Execute collision avoidance sequence
                    self.logger.log_info(f"Bounding box collision detected in iteration {currentIteration}, executing safe movement sequence with {len(safe_moves)} steps")

                    # Execute safe movement sequence
                    status, message = self._execute_safe_movement_sequence_with_positioning(mm, pos, safe_moves, points)
                    if status != 0:
                        self.logger.log_info(f"Safe movement failed in iteration {currentIteration}: {message}")
                        return [status, f"_error_iter{currentIteration}"]
                else:
                    # No safe sequence could be generated
                    collision_details = []
                    for collision in collision_info:
                        if "error" in collision:
                            collision_details.append(f"Error: {collision['error']}")
                        elif "colliding_pairs" in collision:
                            pairs_str = ", ".join([f"M{p[0]}<->M{p[1]}" for p in collision["colliding_pairs"]])
                            collision_details.append(f"Bounding box collision: {pairs_str}")

                    collision_msg = "Bounding box collision detected and no safe sequence found! " + "; ".join(collision_details)
                    self.logger.log_warn(collision_msg)
                    return [2, f"_collision_iter{currentIteration}"]
            else:
                # No collisions, execute direct movement using safe move functions
                for i, point in enumerate(points):
                    manipulator_idx = i + 1

                    # Convert the point to camera coordinates, then to MM coordinates
                    x, y = pos.positioning_coords(point)
                    mm_coords = self.convert_to_mm_coords((x, y), manipulator_idx)
                    if mm_coords is None:
                        self.logger.log_info(f"No calibration data for manipulator {manipulator_idx}")
                        return [2, f"_error_iter{currentIteration}"]

                    # Execute safe move using the new function
                    status = self._execute_single_move(mm, manipulator_idx, mm_coords)
                    if status != 0:
                        return [2, f"_error_iter{currentIteration}"]

            self.logger.log_info(f"Moved to measurement point {point_name} (iteration {currentIteration})")
            return [0, f"_{point_name}"]

        except Exception as e:
            self.logger.log_info(f"Error in loopingIteration: {str(e)}")
            return [2, f"_error_iter{currentIteration}"]
