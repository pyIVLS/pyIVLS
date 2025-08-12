import os
import time
import itertools
import numpy as np
import cv2

from PyQt6.QtCore import pyqtSignal, QObject, QEventLoop, QEvent
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QComboBox, QGraphicsScene, QGraphicsView
from PyQt6.QtGui import QImage, QPixmap, QPen, QBrush, QColor, QFont
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem
from PyQt6.QtCore import Qt

from plugin_components import public, get_public_methods, LoggingHelper, CloseLockSignalProvider, ConnectionIndicatorStyle


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
        
        # Bounding boxes for collision detection - stored as relative offsets from manipulator tip
        self.manipulator_bounding_boxes = {}  # {manipulator_idx: [(dx1, dy1), (dx2, dy2), (dx3, dy3), (dx4, dy4)]}
        self.bounding_boxes_path = os.path.join(self.path, "bounding_boxes_data.npy")
        self.safe_distance_pixels = 50  # Default safe distance in pixels for collision detection
        
        # Internal position tracking - updated on moves and manual refresh
        self.cached_manipulator_positions = {}  # {manipulator_idx: (x, y, z)}
        self.last_position_update = {}  # {manipulator_idx: timestamp}
        
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
        if hasattr(self, 'camera_graphic_view') and self.camera_graphic_view:
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

    def refresh_all_manipulator_positions(self) -> int:
        """
        Query all available manipulators and update cached positions.
        
        Returns:
            int: Number of manipulators successfully updated
        """
        success_count = 0
        try:
            mm, _, _ = self._fetch_dep_plugins()
            if mm is None:
                self.logger.log_warn("No micromanipulator plugin available")
                return 0

            # Get number of available manipulators
            try:
                status, state = mm.mm_devices()
                assert status == 0, f"Error getting devices: {state.get('Error message', 'Unknown error')}"
                num_manipulators, _ = state
            except AttributeError:
                # Fallback: try to query positions for a reasonable range
                num_manipulators = 4

            current_time = time.time()
            
            for i in range(1, num_manipulators + 1):
                try:
                    position = mm.mm_current_position(i)
                    if position and len(position) >= 3:
                        self.cached_manipulator_positions[i] = (position[0], position[1], position[2])
                        self.last_position_update[i] = current_time
                        success_count += 1
                        self.logger.log_debug(f"Updated position for manipulator {i}: {position}")
                    else:
                        self.logger.log_debug(f"No valid position returned for manipulator {i}")
                        
                except Exception as e:
                    self.logger.log_debug(f"Could not get position for manipulator {i}: {e}")
                    continue

            if success_count > 0:
                self.logger.log_debug(f"Refreshed positions for {success_count} manipulator(s)")
            else:
                self.logger.log_warn("No manipulator positions could be updated")
                
        except Exception as e:
            self.logger.log_warn(f"Error refreshing manipulator positions: {e}")
            
        return success_count

    def update_manipulator_position(self, manipulator_idx: int, new_position: tuple[float, float, float]) -> bool:
        """
        Update the cached position for a specific manipulator.
        Call this after programmatic moves to keep the cache current.
        
        Args:
            manipulator_idx: Manipulator index (1-based)
            new_position: New (x, y, z) position
            
        Returns:
            bool: True if position was updated successfully
        """
        try:
            if len(new_position) >= 3:
                self.cached_manipulator_positions[manipulator_idx] = (new_position[0], new_position[1], new_position[2])
                self.last_position_update[manipulator_idx] = time.time()
                self.logger.log_debug(f"Updated cached position for manipulator {manipulator_idx}: {new_position}")
                return True
            else:
                self.logger.log_warn(f"Invalid position format for manipulator {manipulator_idx}: {new_position}")
                return False
        except Exception as e:
            self.logger.log_warn(f"Error updating position for manipulator {manipulator_idx}: {e}")
            return False

    def get_cached_manipulator_position(self, manipulator_idx: int) -> tuple[float, float, float] | None:
        """
        Get the cached position for a manipulator.
        
        Args:
            manipulator_idx: Manipulator index (1-based)
            
        Returns:
            Cached position (x, y, z) or None if not available
        """
        return self.cached_manipulator_positions.get(manipulator_idx)

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

    # Bounding Box Methods
    def _get_current_manipulator_position_camera(self, manipulator_idx: int) -> tuple[float, float] | None:
        """
        Get the current position of a manipulator in camera coordinates using cached positions.
        
        Args:
            manipulator_idx: Manipulator index (1-based)
            
        Returns:
            Current position in camera coordinates, or None if not available
        """
        try:
            # Get cached position
            cached_pos = self.get_cached_manipulator_position(manipulator_idx)
            if cached_pos is None:
                self.logger.log_debug(f"No cached position for manipulator {manipulator_idx}")
                return None
            
            # Debug logging
            self.logger.log_debug(f"Manipulator {manipulator_idx}: cached MM position: ({cached_pos[0]:.1f}, {cached_pos[1]:.1f}, {cached_pos[2]:.1f})")
                
            # Convert to camera coordinates
            camera_coords = self.convert_mm_to_camera_coords((cached_pos[0], cached_pos[1]), manipulator_idx)
            
            if camera_coords:
                self.logger.log_debug(f"Manipulator {manipulator_idx}: converted to camera coords: ({camera_coords[0]:.1f}, {camera_coords[1]:.1f})")
            
            return camera_coords
            
        except Exception as e:
            self.logger.log_debug(f"Error getting cached position for manipulator {manipulator_idx}: {e}")
            return None

    def set_manipulator_bounding_box(self, manipulator_idx: int, corners: list[tuple[float, float]]) -> tuple[int, str]:
        """
        Set a custom bounding box for a manipulator in camera coordinates.
        The corners will be converted to relative offsets from the current manipulator tip position.
        
        Args:
            manipulator_idx: Manipulator index (1-based)
            corners: List of 4 corner points [(x1, y1), (x2, y2), (x3, y3), (x4, y4)] in absolute camera coordinates
            
        Returns:
            tuple: (status, message)
        """
        if len(corners) != 4:
            return 1, "Bounding box must have exactly 4 corner points"
        
        # Validate that all corners are tuples of two floats
        for i, corner in enumerate(corners):
            if not isinstance(corner, (tuple, list)) or len(corner) != 2:
                return 1, f"Corner {i+1} must be a tuple/list of 2 coordinates"
            try:
                float(corner[0])
                float(corner[1])
            except (TypeError, ValueError):
                return 1, f"Corner {i+1} coordinates must be numeric"
        
        # Get current manipulator position to convert absolute coordinates to relative offsets
        current_position = self._get_current_manipulator_position_camera(manipulator_idx)
        if current_position is None:
            return 1, f"Cannot determine current position of manipulator {manipulator_idx}. Make sure the manipulator is located."
        
        tip_x, tip_y = current_position
        
        # Convert absolute corners to relative offsets from the tip
        relative_corners = []
        for abs_x, abs_y in corners:
            dx = abs_x - tip_x
            dy = abs_y - tip_y
            relative_corners.append((dx, dy))
        
        self.manipulator_bounding_boxes[manipulator_idx] = relative_corners
        self.logger.log_info(f"Set bounding box for manipulator {manipulator_idx} as relative offsets from tip position ({tip_x:.1f}, {tip_y:.1f})")
        
        # Save to file for persistence
        self._save_bounding_boxes_to_file()
        
        return 0, f"Bounding box set for manipulator {manipulator_idx} (relative to tip position)"

    @public
    def setup_manipulator_bounding_box(self, manipulator_idx: int) -> tuple[int, str]:
        """
        Interactive setup of manipulator bounding box by clicking on camera view.
        
        Args:
            manipulator_idx: Manipulator index (1-based)
            
        Returns:
            tuple: (status, message)
        """
        try:
            self.logger.info_popup(f"Click 4 corners to define bounding box for manipulator {manipulator_idx}. Press ESC to cancel.")
            
            corners = []
            for i in range(4):
                self.logger.log_info(f"Waiting for corner {i+1}/4...")
                click_pos = self._wait_for_input()
                if click_pos is None:
                    return 1, "Bounding box setup cancelled"
                corners.append(click_pos)
                self.logger.log_info(f"Corner {i+1}: ({click_pos[0]:.1f}, {click_pos[1]:.1f})")
            
            # Set the bounding box
            status, message = self.set_manipulator_bounding_box(manipulator_idx, corners)
            if status == 0:
                self._add_visual_overlays()  # Refresh visual overlays
                self.logger.info_popup(f"Bounding box set for manipulator {manipulator_idx}")
            
            return status, message
            
        except Exception as e:
            return 1, f"Error setting up bounding box: {e}"

    @public 
    def clear_manipulator_bounding_box(self, manipulator_idx: int) -> tuple[int, str]:
        """
        Clear the bounding box for a manipulator.
        
        Args:
            manipulator_idx: Manipulator index (1-based)
            
        Returns:
            tuple: (status, message)
        """
        if manipulator_idx in self.manipulator_bounding_boxes:
            del self.manipulator_bounding_boxes[manipulator_idx]
            self._save_bounding_boxes_to_file()  # Save updated bounding boxes to file
            self._add_visual_overlays()  # Refresh visual overlays
            return 0, f"Bounding box cleared for manipulator {manipulator_idx}"
        else:
            return 1, f"No bounding box found for manipulator {manipulator_idx}"

    @public
    def clear_all_bounding_boxes(self) -> tuple[int, str]:
        """
        Clear all manipulator bounding boxes.
        
        Returns:
            tuple: (status, message)
        """
        count = len(self.manipulator_bounding_boxes)
        self.manipulator_bounding_boxes.clear()
        self._save_bounding_boxes_to_file()
        self._add_visual_overlays()  # Refresh visual overlays
        return 0, f"Cleared {count} bounding box(es)"

    def get_absolute_bounding_box(self, manipulator_idx: int) -> list[tuple[float, float]] | None:
        """
        Get the absolute bounding box coordinates for a manipulator based on its current position.
        
        Args:
            manipulator_idx: Manipulator index (1-based)
            
        Returns:
            List of absolute corner points in camera coordinates, or None if not available
        """
        # Get the relative bounding box offsets
        relative_bbox = self.manipulator_bounding_boxes.get(manipulator_idx)
        if relative_bbox is None:
            return None
        
        
        # Get current manipulator position in camera coordinates
        current_position_camera = self._get_current_manipulator_position_camera(manipulator_idx)
        if current_position_camera is None:
            return None
        
        tip_x, tip_y = current_position_camera
        
        # Debug logging
        self.logger.log_debug(f"Manipulator {manipulator_idx}: tip position in camera coords: ({tip_x:.1f}, {tip_y:.1f})")
        self.logger.log_debug(f"Manipulator {manipulator_idx}: relative bbox offsets: {relative_bbox}")
        
        # Convert relative offsets to absolute positions
        absolute_bbox = []
        for dx, dy in relative_bbox:
            absolute_x = tip_x + dx
            absolute_y = tip_y + dy
            absolute_bbox.append((absolute_x, absolute_y))
        
        self.logger.log_debug(f"Manipulator {manipulator_idx}: absolute bbox corners: {absolute_bbox}")
        
        return absolute_bbox

    def _save_bounding_boxes_to_file(self):
        """Save the current bounding box data to a file."""
        if not self.manipulator_bounding_boxes:
            self.logger.log_info("No bounding box data to save.")
            return

        file_path = self.bounding_boxes_path
        try:
            np.save(file_path, self.manipulator_bounding_boxes, allow_pickle=True)
            self.logger.log_info(f"Bounding box data saved to {file_path}")
        except Exception as e:
            self.logger.log_warn(f"Failed to save bounding box data: {e}")

    def _load_bounding_boxes_from_file(self):
        """Load bounding box data from file on startup."""
        file_path = self.bounding_boxes_path
        
        if not os.path.exists(file_path):
            self.logger.log_debug(f"No bounding box data found at {file_path}")
            return

        try:
            self.manipulator_bounding_boxes = np.load(file_path, allow_pickle=True).item()
            loaded_count = len(self.manipulator_bounding_boxes)
            self.logger.log_info(f"Loaded {loaded_count} bounding box(es) from {file_path}")
        except Exception as e:
            self.logger.log_warn(f"Failed to load bounding box data: {e}")
            self.manipulator_bounding_boxes = {}  # Reset to empty dict on error

    


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
        Converts relative offsets to absolute positions for drawing.
        """
        # Check if bounding boxes should be shown

        if not self.show_bounding_boxes_checkbox.isChecked():
            return

            
        for manipulator_idx in self.manipulator_bounding_boxes.keys():
            # Get absolute bounding box coordinates based on current manipulator position
            absolute_corners = self.get_absolute_bounding_box(manipulator_idx)
            if absolute_corners:
                self._draw_bounding_box(absolute_corners, manipulator_idx)
            else:
                self.logger.log_debug(f"Cannot draw bounding box for manipulator {manipulator_idx}: position not available")

    def _draw_bounding_box(self, corners: list[tuple[float, float]], manipulator_idx: int):
        """
        Draw a single bounding box on the camera view.
        
        Args:
            corners: List of 4 corner points in camera coordinates
            manipulator_idx: Manipulator index for color coding
        """
        if len(corners) != 4:
            return
        
        # Choose color based on manipulator index
        colors = [
            QColor(255, 0, 0),    # Red for manipulator 1
            QColor(0, 255, 0),    # Green for manipulator 2  
            QColor(0, 0, 255),    # Blue for manipulator 3
            QColor(255, 255, 0),  # Yellow for manipulator 4
        ]
        color = colors[(manipulator_idx - 1) % len(colors)]
        
        # Create pen for drawing
        pen = QPen(color, 2, Qt.PenStyle.SolidLine)
        
        # Draw the bounding box as connected lines
        for i in range(4):
            start_point = corners[i]
            end_point = corners[(i + 1) % 4]
            
            line = QGraphicsLineItem(start_point[0], start_point[1], end_point[0], end_point[1])
            line.setPen(pen)
            self.camera_graphic_scene.addItem(line)
        
        # Add a label for the manipulator
        text_pos = corners[0]  # Use first corner for text position
        text_item = self.camera_graphic_scene.addText(f"M{manipulator_idx}", QFont("Arial", 10))
        if text_item:
            text_item.setPos(text_pos[0], text_pos[1] - 20)
            text_item.setDefaultTextColor(color)

    def _check_and_visualize_collision(self, mm_idx, manipulator_positions, current_targets):
        """
        Check for potential collisions and visualize warnings.
        """
        try:
            # Get this manipulator's current and target positions
            current_pos = manipulator_positions.get(mm_idx)
            target_pos = current_targets.get(mm_idx)

            if current_pos is None or target_pos is None:
                return

            # Convert camera coordinates back to MM coordinates for collision detection
            mm_current = self.convert_to_mm_coords(current_pos, mm_idx)
            mm_target = self.convert_to_mm_coords(target_pos, mm_idx)

            if mm_current is None or mm_target is None:
                return

            # Check collision with other manipulators
            SAFE_DISTANCE = 1000  # microns

            for other_mm_idx, other_current_pos in manipulator_positions.items():
                if other_mm_idx == mm_idx or other_current_pos is None:
                    continue

                # Convert other manipulator position to MM coordinates
                other_mm_pos = self.convert_to_mm_coords(other_current_pos, other_mm_idx)
                if other_mm_pos is None:
                    continue

                # Calculate minimum distance using the existing collision detection function
                distance = self._min_distance_collision_check(mm_current[0], other_mm_pos[0], mm_current[1], other_mm_pos[1], mm_target[0], mm_target[1])

                if distance < SAFE_DISTANCE:
                    # Draw collision warning
                    self._draw_collision_warning(current_pos, target_pos, distance)
                    self.logger.log_warn(f"Potential collision: Manipulator {mm_idx} -> {other_mm_idx}, distance: {distance:.1f} μm")

        except Exception as e:
            self.logger.log_debug(f"Error in collision visualization: {e}")

    def _min_distance_collision_check(self, mm1x, mm2x, mm1y, mm2y, mm1targetx, mm1targety):
        """
        Calculate minimum distance between manipulator trajectory and another manipulator.
        This is the same algorithm used in the collision detection.
        """
        # vector from mm1 to target
        vx, vy = mm1targetx - mm1x, mm1targety - mm1y
        # vector from mm1 to mm2
        sx, sy = mm2x - mm1x, mm2y - mm1y
        seg_len2 = sx * sx + sy * sy
        if seg_len2 == 0:
            return (vx * vx + vy * vy) ** 0.5
        # projection factor t
        t = max(0, min(1, (vx * sx + vy * sy) / seg_len2))
        # closest point on segment
        cx, cy = mm1x + t * sx, mm1y + t * sy
        dx, dy = mm1targetx - cx, mm1targety - cy
        return (dx * dx + dy * dy) ** 0.5

    def _check_bounding_box_collision(self, mm, points):
        """
        Check for bounding box collisions between manipulators during movement.
        Uses camera coordinates as universal coordinate system and checks trajectory intersections.

        Args:
            mm: Micromanipulator plugin instance
            points: List of target points for each manipulator

        Returns:
            tuple: (is_safe, collision_info, safe_moves) where safe_moves is a movement sequence
        """
        try:
            # Get current and target positions in camera coordinates for all manipulators
            current_positions_camera = {}
            target_positions_camera = {}
            
            # Convert positioning points to camera coordinates
            _, _, pos = self._fetch_dep_plugins()
            if pos is None:
                return False, [{"error": "No positioning plugin available"}], []

            for i, point in enumerate(points):
                manipulator_idx = i + 1
                if point is not None:
                    try:
                        # Get current position in camera coordinates
                        current_camera_pos = self._get_current_manipulator_position_camera(manipulator_idx)
                        if current_camera_pos is not None:
                            current_positions_camera[manipulator_idx] = current_camera_pos
                        
                        # Convert mask coordinates to camera coordinates for target
                        target_camera_x, target_camera_y = pos.positioning_coords(point)
                        target_positions_camera[manipulator_idx] = (target_camera_x, target_camera_y)
                        
                    except Exception as e:
                        self.logger.log_debug(f"Error converting coordinates for manipulator {manipulator_idx}: {e}")

            if len(target_positions_camera) <= 1:
                # No collision possible with 0 or 1 manipulator
                return True, [], [{"type": "direct", "moves": target_positions_camera}]

            # Check for trajectory collisions (moving manipulator vs stationary manipulators)
            collision_pairs = self._find_trajectory_collisions(current_positions_camera, target_positions_camera)
            
            if not collision_pairs:
                # No collisions detected
                return True, [], [{"type": "direct", "moves": target_positions_camera}]

            # Find safe movement sequence using permutations
            safe_sequence = self._find_safe_movement_sequence_camera(current_positions_camera, target_positions_camera, collision_pairs)
            
            if safe_sequence is not None:
                collision_info = [{"colliding_pairs": collision_pairs, "resolution": "permutation_based"}]
                return True, collision_info, safe_sequence
            else:
                # No safe sequence found
                collision_info = [{"colliding_pairs": collision_pairs, "error": "No safe movement sequence found"}]
                return False, collision_info, []

        except Exception as e:
            self.logger.log_warn(f"Error in bounding box collision detection: {e}")
            return False, [{"error": str(e)}], []

    def _find_trajectory_collisions(self, current_positions_camera, target_positions_camera):
        """
        Find all pairs of manipulators whose bounding boxes would collide during movement.
        Checks trajectory of moving manipulator against stationary manipulators.
        
        Args:
            current_positions_camera: Dict of {manipulator_idx: (current_x, current_y)} in camera coordinates
            target_positions_camera: Dict of {manipulator_idx: (target_x, target_y)} in camera coordinates
            
        Returns:
            list: List of tuples representing colliding manipulator pairs
        """
        collision_pairs = []
        manipulator_indices = list(target_positions_camera.keys())
        
        # Check each moving manipulator against all stationary ones
        for moving_idx in manipulator_indices:
            if moving_idx not in current_positions_camera:
                continue
                
            for stationary_idx in manipulator_indices:
                if stationary_idx == moving_idx or stationary_idx not in current_positions_camera:
                    continue
                
                # Check if moving manipulator's trajectory intersects with stationary manipulator's bounding box
                if self._trajectory_intersects_bounding_box(
                    moving_idx, 
                    current_positions_camera[moving_idx], 
                    target_positions_camera[moving_idx],
                    stationary_idx,
                    current_positions_camera[stationary_idx]
                ):
                    collision_pairs.append((moving_idx, stationary_idx))
                    self.logger.log_warn(f"Trajectory collision detected: Moving manipulator {moving_idx} -> Stationary manipulator {stationary_idx}")
        
        return collision_pairs

    def _trajectory_intersects_bounding_box(self, moving_idx, start_pos, end_pos, stationary_idx, stationary_pos):
        """
        Check if a moving manipulator's bounding box trajectory intersects with a stationary manipulator's bounding box.
        
        Args:
            moving_idx: Index of moving manipulator
            start_pos: Start position (x, y) in camera coordinates
            end_pos: End position (x, y) in camera coordinates
            stationary_idx: Index of stationary manipulator
            stationary_pos: Position (x, y) in camera coordinates
            
        Returns:
            bool: True if trajectory intersects with stationary bounding box
        """
        # Get bounding boxes
        moving_bbox_relative = self.manipulator_bounding_boxes.get(moving_idx)
        stationary_bbox_relative = self.manipulator_bounding_boxes.get(stationary_idx)
        
        if moving_bbox_relative is None or stationary_bbox_relative is None:
            # If no bounding boxes defined, no collision
            return False
        
        # Get stationary manipulator's absolute bounding box
        stationary_bbox_absolute = self._get_absolute_bounding_box_at_position(
            stationary_bbox_relative, stationary_pos
        )
        
        # Sample multiple points along the trajectory to check for intersections
        # Since we need to check bounding box intersection at ANY point during movement
        num_samples = 20  # Check 20 points along the trajectory
        
        for i in range(num_samples + 1):
            t = i / num_samples  # Parameter from 0 to 1
            
            # Interpolate position along trajectory
            current_x = start_pos[0] + t * (end_pos[0] - start_pos[0])
            current_y = start_pos[1] + t * (end_pos[1] - start_pos[1])
            trajectory_pos = (current_x, current_y)
            
            # Get moving manipulator's bounding box at this position
            moving_bbox_absolute = self._get_absolute_bounding_box_at_position(
                moving_bbox_relative, trajectory_pos
            )
            
            # Check if bounding boxes intersect at this point
            if self._bounding_boxes_intersect(moving_bbox_absolute, stationary_bbox_absolute):
                return True
        
        return False

    def _get_absolute_bounding_box_at_position(self, relative_bbox, position):
        """
        Convert relative bounding box offsets to absolute positions at a specific location.
        
        Args:
            relative_bbox: List of relative offsets [(dx1, dy1), (dx2, dy2), ...]
            position: Position (x, y) in camera coordinates
            
        Returns:
            list: List of absolute corner points in camera coordinates
        """
        tip_x, tip_y = position
        
        absolute_bbox = []
        for dx, dy in relative_bbox:
            absolute_x = tip_x + dx
            absolute_y = tip_y + dy
            absolute_bbox.append((absolute_x, absolute_y))
        
        return absolute_bbox

    def _find_safe_movement_sequence_camera(self, current_positions_camera, target_positions_camera, collision_pairs):
        """
        Find a safe movement sequence using permutations to avoid bounding box collisions.
        Works in camera coordinates.
        
        Args:
            current_positions_camera: Dict of {manipulator_idx: (current_x, current_y)}
            target_positions_camera: Dict of {manipulator_idx: (target_x, target_y)}
            collision_pairs: List of colliding manipulator pairs
            
        Returns:
            list: Safe movement sequence, or None if no safe sequence found
        """
        manipulator_indices = list(target_positions_camera.keys())
        
        # Try all possible permutations of movement order
        for permutation in itertools.permutations(manipulator_indices):
            if self._is_movement_sequence_safe_camera(permutation, current_positions_camera, target_positions_camera):
                # Create sequential movement sequence
                safe_moves = []
                for mm_idx in permutation:
                    safe_moves.append({
                        "type": "sequential",
                        "manipulator": mm_idx,
                        "target_camera": target_positions_camera[mm_idx],
                        "description": f"Moving manipulator {mm_idx} in safe sequence"
                    })
                
                self.logger.log_info(f"Found safe movement sequence: {list(permutation)}")
                return safe_moves
        
        # No safe permutation found
        self.logger.log_warn("No safe movement permutation found")
        return None

    def _is_movement_sequence_safe_camera(self, sequence, current_positions_camera, target_positions_camera):
        """
        Check if a movement sequence avoids collisions by testing each step in camera coordinates.
        
        Args:
            sequence: List of manipulator indices in movement order
            current_positions_camera: Dict of {manipulator_idx: (current_x, current_y)}
            target_positions_camera: Dict of {manipulator_idx: (target_x, target_y)}
            
        Returns:
            bool: True if sequence is safe
        """
        # Simulate the movement sequence in camera coordinates
        simulated_positions = current_positions_camera.copy()
        
        # Test each move in the sequence
        for moving_idx in sequence:
            if moving_idx not in target_positions_camera:
                continue
                
            # Check trajectory of this manipulator against all other manipulators at their current positions
            for other_idx in sequence:
                if other_idx == moving_idx or other_idx not in simulated_positions:
                    continue
                
                # Check if moving manipulator's trajectory intersects with other manipulator's bounding box
                if self._trajectory_intersects_bounding_box(
                    moving_idx,
                    simulated_positions[moving_idx],
                    target_positions_camera[moving_idx],
                    other_idx,
                    simulated_positions[other_idx]
                ):
                    # Collision detected in this sequence
                    return False
            
            # Move this manipulator to its target position
            simulated_positions[moving_idx] = target_positions_camera[moving_idx]
        
        return True

    def _bounding_boxes_intersect(self, bbox1, bbox2):
        """
        Check if two bounding boxes intersect using polygon intersection.
        
        Args:
            bbox1: List of 4 corner points [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
            bbox2: List of 4 corner points [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
            
        Returns:
            bool: True if bounding boxes intersect
        """
        if len(bbox1) != 4 or len(bbox2) != 4:
            return False
        
        # Simple bounding rectangle intersection test first (faster)
        bbox1_min_x = min(p[0] for p in bbox1)
        bbox1_max_x = max(p[0] for p in bbox1)
        bbox1_min_y = min(p[1] for p in bbox1)
        bbox1_max_y = max(p[1] for p in bbox1)
        
        bbox2_min_x = min(p[0] for p in bbox2)
        bbox2_max_x = max(p[0] for p in bbox2)
        bbox2_min_y = min(p[1] for p in bbox2)
        bbox2_max_y = max(p[1] for p in bbox2)
        
        # Check if bounding rectangles don't overlap
        if (bbox1_max_x < bbox2_min_x or bbox2_max_x < bbox1_min_x or
            bbox1_max_y < bbox2_min_y or bbox2_max_y < bbox1_min_y):
            return False
        
        # If bounding rectangles overlap, do more precise polygon intersection test
        return self._polygons_intersect(bbox1, bbox2)

    def _polygons_intersect(self, poly1, poly2):
        """
        Check if two polygons intersect using the Separating Axis Theorem.
        
        Args:
            poly1: List of points [(x1, y1), ...]
            poly2: List of points [(x1, y1), ...]
            
        Returns:
            bool: True if polygons intersect
        """
        # Check if any point of poly1 is inside poly2
        for point in poly1:
            if self._point_in_polygon(point, poly2):
                return True
        
        # Check if any point of poly2 is inside poly1
        for point in poly2:
            if self._point_in_polygon(point, poly1):
                return True
        
        # Check if any edges intersect
        for i in range(len(poly1)):
            edge1 = (poly1[i], poly1[(i + 1) % len(poly1)])
            for j in range(len(poly2)):
                edge2 = (poly2[j], poly2[(j + 1) % len(poly2)])
                if self._line_segments_intersect(edge1[0], edge1[1], edge2[0], edge2[1]):
                    return True
        
        return False

    def _point_in_polygon(self, point, polygon):
        """
        Check if a point is inside a polygon using ray casting algorithm.
        
        Args:
            point: (x, y) coordinates
            polygon: List of (x, y) coordinates
            
        Returns:
            bool: True if point is inside polygon
        """
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside

    def _line_segments_intersect(self, p1, q1, p2, q2):
        """
        Check if two line segments intersect.
        
        Args:
            p1, q1: First line segment endpoints
            p2, q2: Second line segment endpoints
            
        Returns:
            bool: True if line segments intersect
        """
        def orientation(p, q, r):
            val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
            if val == 0:
                return 0  # collinear
            return 1 if val > 0 else 2  # clockwise or counterclockwise
        
        def on_segment(p, q, r):
            return (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
                    q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))
        
        o1 = orientation(p1, q1, p2)
        o2 = orientation(p1, q1, q2)
        o3 = orientation(p2, q2, p1)
        o4 = orientation(p2, q2, q1)
        
        # General case
        if o1 != o2 and o3 != o4:
            return True
        
        # Special cases
        if (o1 == 0 and on_segment(p1, p2, q1) or
            o2 == 0 and on_segment(p1, q2, q1) or
            o3 == 0 and on_segment(p2, p1, q2) or
            o4 == 0 and on_segment(p2, q1, q2)):
            return True
        
        return False

    def _find_safe_movement_sequence(self, target_positions_mm, collision_pairs):
        """
        Find a safe movement sequence using permutations to avoid bounding box collisions.
        Legacy method - maintained for backward compatibility but not used.
        
        Args:
            target_positions_mm: Dict of {manipulator_idx: (target_x, target_y)}
            collision_pairs: List of colliding manipulator pairs
            
        Returns:
            list: Safe movement sequence, or None if no safe sequence found
        """
        # This method is kept for compatibility but not used in the new collision detection system
        return None

    def _is_movement_sequence_safe(self, sequence, target_positions_mm):
        """
        Check if a movement sequence avoids collisions by testing each step.
        Legacy method - maintained for backward compatibility but not used.
        
        Args:
            sequence: List of manipulator indices in movement order
            target_positions_mm: Dict of {manipulator_idx: (target_x, target_y)}
            
        Returns:
            bool: True if sequence is safe (always returns False to force use of new system)
        """
        # This method is kept for compatibility but not used in the new collision detection system
        return False

    def _check_movement_collision(self, mm, points):
        """
        LEGACY FUNCTION - now redirects to bounding box collision detection.
        Check for potential collisions before executing movements and generate safe move sequences.

        Args:
            mm: Micromanipulator plugin instance
            points: List of target points for each manipulator

        Returns:
            tuple: (is_safe, collision_info, safe_moves) where safe_moves is a list of movement sequences
        """
        # Use the new bounding box collision detection
        return self._check_bounding_box_collision(mm, points)

    def _generate_safe_movement_sequence(self, current_positions, target_positions, safe_distance):
        """
        Generate a safe movement sequence that avoids collisions.

        Args:
            current_positions: Dict of {manipulator_idx: (x, y)}
            target_positions: Dict of {manipulator_idx: (x, y)}
            safe_distance: Minimum safe distance in microns

        Returns:
            tuple: (collision_info, safe_moves) where safe_moves is a list of movement steps
        """
        collision_info = []
        safe_moves = []

        # Create list of manipulators that need to move
        moving_manipulators = []
        for mm_idx in current_positions.keys():
            if mm_idx in target_positions and target_positions[mm_idx] is not None and current_positions[mm_idx] is not None:
                moving_manipulators.append(mm_idx)

        if len(moving_manipulators) <= 1:
            # Only one or no manipulators moving, no collision possible
            return collision_info, [{"type": "direct", "moves": target_positions}]

        # Check all pairs for potential collisions
        colliding_pairs = []
        for i, mm1_idx in enumerate(moving_manipulators):
            for mm2_idx in moving_manipulators[i + 1 :]:
                current1 = current_positions[mm1_idx]
                current2 = current_positions[mm2_idx]
                target1 = target_positions[mm1_idx]

                if current1 is None or current2 is None or target1 is None:
                    continue

                # Calculate minimum distance during movement
                distance = self._min_distance_collision_check(current1[0], current2[0], current1[1], current2[1], target1[0], target1[1])

                if distance < safe_distance:
                    collision_info.append({"manipulator1": mm1_idx, "manipulator2": mm2_idx, "distance": distance, "safe_distance": safe_distance})
                    colliding_pairs.append((mm1_idx, mm2_idx))

        if not colliding_pairs:
            # No collisions detected, move all simultaneously
            return collision_info, [{"type": "direct", "moves": target_positions}]

        # Generate collision avoidance strategy
        safe_moves = self._plan_collision_avoidance(current_positions, target_positions, colliding_pairs, safe_distance)

        # Log the strategy being used
        self._log_collision_avoidance_strategy(safe_moves, colliding_pairs)

        return collision_info, safe_moves

    def _log_collision_avoidance_strategy(self, safe_moves, colliding_pairs):
        """Log information about the collision avoidance strategy being used."""
        if not safe_moves:
            return

        strategy_type = safe_moves[0].get("type", "unknown")

        if strategy_type == "direct":
            self.logger.log_info("No collisions detected - executing direct simultaneous movement")
        elif strategy_type == "sequential":
            sequential_order = [move.get("manipulator") for move in safe_moves if move.get("type") == "sequential"]
            self.logger.log_info(f"Using sequential movement strategy - order: {sequential_order}")
        elif any(move.get("type") == "intermediate" for move in safe_moves):
            colliding_manipulators = [pair for pair in colliding_pairs]
            self.logger.log_info(f"Using safe intermediate positions strategy for colliding pairs: {colliding_manipulators}")
        else:
            self.logger.log_info(f"Using collision avoidance strategy with {len(safe_moves)} movement steps")

    def _plan_collision_avoidance(self, current_positions, target_positions, colliding_pairs, safe_distance):
        """
        Plan a sequence of moves to avoid collisions.

        Strategy:
        1. Try reordering moves (move one manipulator first)
        2. If that fails, move colliding manipulators to safe intermediate positions

        Returns:
            list: List of movement steps, each step is a dict with move instructions
        """
        # Extract all manipulators involved in collisions
        colliding_manipulators = set()
        for mm1, mm2 in colliding_pairs:
            colliding_manipulators.add(mm1)
            colliding_manipulators.add(mm2)

        # Strategy 1: Try sequential moves (reordering)
        sequential_moves = self._try_sequential_moves(current_positions, target_positions, colliding_pairs, safe_distance)

        if sequential_moves:
            return sequential_moves

        # Strategy 2: Move manipulators to safe intermediate positions
        return self._move_via_safe_positions(current_positions, target_positions, colliding_manipulators, safe_distance)

    def _try_sequential_moves(self, current_positions, target_positions, colliding_pairs, safe_distance):
        """
        Try to resolve collisions by moving manipulators sequentially in different orders.
        """
        # Get all manipulators that need to move
        moving_manipulators = [mm for mm in current_positions.keys() if mm in target_positions and target_positions[mm] is not None]

        # Try different orderings
        import itertools

        for order in itertools.permutations(moving_manipulators):
            if self._is_sequential_order_safe(order, current_positions, target_positions, safe_distance):
                # Create sequential move list
                moves = []
                temp_positions = current_positions.copy()

                for mm_idx in order:
                    moves.append({"type": "sequential", "manipulator": mm_idx, "target": target_positions[mm_idx]})
                    temp_positions[mm_idx] = target_positions[mm_idx]

                return moves

        return None

    def _is_sequential_order_safe(self, order, current_positions, target_positions, safe_distance):
        """
        Check if a sequential movement order avoids all collisions.
        """
        temp_positions = current_positions.copy()

        for mm_idx in order:
            # Check if this move would collide with any stationary manipulator
            for other_mm in temp_positions.keys():
                if other_mm == mm_idx:
                    continue

                current_pos = temp_positions[mm_idx]
                other_pos = temp_positions[other_mm]
                target_pos = target_positions[mm_idx]

                if current_pos is None or other_pos is None or target_pos is None:
                    continue

                distance = self._min_distance_collision_check(current_pos[0], other_pos[0], current_pos[1], other_pos[1], target_pos[0], target_pos[1])

                if distance < safe_distance:
                    return False

            # Update position after this move
            temp_positions[mm_idx] = target_positions[mm_idx]

        return True

    def _move_via_safe_positions(self, current_positions, target_positions, colliding_manipulators, safe_distance):
        """
        Create a movement sequence via safe intermediate positions.
        """
        moves = []

        # First, move colliding manipulators to safe positions (higher Z + offset in XY)
        safe_offset = safe_distance * 2  # Move twice the safe distance away

        for mm_idx in colliding_manipulators:
            if mm_idx in current_positions and current_positions[mm_idx] is not None:
                current_x, current_y = current_positions[mm_idx]

                # Calculate safe intermediate position (move away from collision area)
                safe_x = current_x + safe_offset
                safe_y = current_y + safe_offset

                moves.append({"type": "intermediate", "manipulator": mm_idx, "target": (safe_x, safe_y), "description": f"Moving manipulator {mm_idx} to safe position"})

        # Then move non-colliding manipulators to their targets
        for mm_idx in current_positions.keys():
            if mm_idx not in colliding_manipulators and mm_idx in target_positions and target_positions[mm_idx] is not None:
                moves.append({"type": "direct", "manipulator": mm_idx, "target": target_positions[mm_idx], "description": f"Moving non-colliding manipulator {mm_idx} to target"})

        # Finally, move colliding manipulators to their final targets
        for mm_idx in colliding_manipulators:
            if mm_idx in target_positions and target_positions[mm_idx] is not None:
                moves.append({"type": "final", "manipulator": mm_idx, "target": target_positions[mm_idx], "description": f"Moving manipulator {mm_idx} to final target"})

        return moves

    def _execute_safe_movement_sequence(self, mm, pos, safe_moves):
        """
        Execute a sequence of safe movements.

        Args:
            mm: Micromanipulator plugin instance
            pos: Positioning plugin instance
            safe_moves: List of movement steps generated by collision avoidance

        Returns:
            tuple: (status, message) where status 0 = success
        """
        try:
            for i, move_step in enumerate(safe_moves):
                move_type = move_step.get("type")

                if move_type == "direct":
                    # Direct simultaneous movement (no collisions)
                    moves = move_step.get("moves", {})
                    for mm_idx, target in moves.items():
                        if target is not None:
                            status = self._execute_single_move(mm, mm_idx, target)
                            if status != 0:
                                return status, f"Failed to execute direct move for manipulator {mm_idx}"

                elif move_type in ["sequential", "intermediate", "final"]:
                    # Single manipulator movement
                    mm_idx = move_step.get("manipulator")
                    target = move_step.get("target")
                    description = move_step.get("description", f"Moving manipulator {mm_idx}")

                    if mm_idx is not None and target is not None:
                        self.logger.log_debug(description)
                        status = self._execute_single_move(mm, mm_idx, target)
                        if status != 0:
                            return status, f"Failed to execute {move_type} move for manipulator {mm_idx}"

                else:
                    self.logger.log_warn(f"Unknown move type: {move_type}")

            return 0, "All movements completed successfully"

        except Exception as e:
            self.logger.log_warn(f"Error executing safe movement sequence: {e}")
            return 2, f"Movement execution failed: {e}"

    def _execute_single_move(self, mm, mm_idx, target):
        """
        Execute a single manipulator move using safe 80%/20% move and update cached position.

        Args:
            mm: Micromanipulator plugin instance
            mm_idx: Manipulator index
            target: Target coordinates - can be (x, y) in MM coordinates or dict with 'target_camera' key

        Returns:
            int: Status code (0 = success)
        """
        try:
            # Handle new camera coordinate format from safe movement sequences
            if isinstance(target, dict) and 'target_camera' in target:
                # Convert camera coordinates to MM coordinates
                camera_x, camera_y = target['target_camera']
                mm_coords = self.convert_to_mm_coords((camera_x, camera_y), mm_idx)
                if mm_coords is None:
                    self.logger.log_warn(f"Could not convert camera coordinates to MM for manipulator {mm_idx}")
                    return 2
                x, y = mm_coords
                self.logger.log_debug(f"Converting camera coords ({camera_x}, {camera_y}) to MM coords ({x}, {y}) for manipulator {mm_idx}")
            else:
                # Handle legacy MM coordinate format
                x, y = target
            
            # Use the new safe move function (80% quick + 20% slow)
            if hasattr(mm, 'mm_safe_move_to_position'):
                status, state = mm.mm_safe_move_to_position(mm_idx, x, y)
                if status != 0:
                    self.logger.log_info(f"Error in safe move for manipulator {mm_idx}: {state.get('Error message', str(state))}")
                    return 2
                
                # Extract final position from the response
                final_position = state.get('final_position')
                if final_position and len(final_position) >= 3:
                    self.update_manipulator_position(mm_idx, final_position)
                    self.logger.log_debug(f"Updated cached position for manipulator {mm_idx} after safe move: {final_position}")
                
            else:
                # Fallback to original method if safe move not available
                mm.mm_change_active_device(mm_idx)
                mm.mm_up_max()  # Move up to avoid collisions during XY movement

                status, state = mm.mm_move(x, y)
                if status:
                    self.logger.log_info(f"Error moving manipulator {mm_idx}: {state.get('Error message', str(state))}")
                    return 2

                # Update cached position after successful move
                try:
                    current_pos = mm.mm_current_position(mm_idx)
                    if current_pos and len(current_pos) >= 3:
                        self.update_manipulator_position(mm_idx, current_pos)
                        self.logger.log_debug(f"Updated cached position for manipulator {mm_idx} after move")
                except Exception as e:
                    self.logger.log_debug(f"Could not update cached position for manipulator {mm_idx}: {e}")

            return 0

        except Exception as e:
            self.logger.log_warn(f"Error executing single move for manipulator {mm_idx}: {e}")
            return 2

    def _execute_safe_movement_sequence_with_positioning(self, mm, pos, safe_moves, points):
        """
        Execute safe movement sequence using positioning coordinates.
        Updated to handle both camera coordinate and MM coordinate formats.

        Args:
            mm: Micromanipulator plugin instance
            pos: Positioning plugin instance
            safe_moves: List of movement steps (may contain camera coordinates)
            points: Original positioning points

        Returns:
            tuple: (status, message)
        """
        try:
            # Convert positioning points to MM coordinates for each manipulator (legacy support)
            mm_targets = {}
            for i, point in enumerate(points):
                if point is not None:
                    x, y = pos.positioning_coords(point)
                    mm_coords = self.convert_to_mm_coords((x, y), i + 1)
                    if mm_coords is None:
                        return 2, f"No calibration data for manipulator {i + 1}"
                    mm_targets[i + 1] = mm_coords

            # Execute the safe movement sequence
            for move_step in safe_moves:
                move_type = move_step.get("type")

                if move_type == "direct":
                    # Move all manipulators to their final targets
                    moves = move_step.get("moves", {})
                    if isinstance(moves, dict):
                        # New camera coordinate format
                        for mm_idx, target_camera_pos in moves.items():
                            target_dict = {"target_camera": target_camera_pos}
                            status = self._execute_single_move(mm, mm_idx, target_dict)
                            if status != 0:
                                return status, f"Failed to execute direct move for manipulator {mm_idx}"
                    else:
                        # Legacy MM coordinate format
                        for mm_idx, target in mm_targets.items():
                            status = self._execute_single_move(mm, mm_idx, target)
                            if status != 0:
                                return status, f"Failed to execute direct move for manipulator {mm_idx}"

                elif move_type == "sequential":
                    # Move one manipulator at a time in the specified order
                    mm_idx = move_step.get("manipulator")
                    target_camera = move_step.get("target_camera")
                    
                    if target_camera is not None:
                        # New camera coordinate format
                        target_dict = {"target_camera": target_camera}
                        self.logger.log_debug(f"Sequential move: manipulator {mm_idx} to camera coords {target_camera}")
                        status = self._execute_single_move(mm, mm_idx, target_dict)
                        if status != 0:
                            return status, f"Failed sequential move for manipulator {mm_idx}"
                    elif mm_idx in mm_targets:
                        # Legacy MM coordinate format
                        self.logger.log_debug(f"Sequential move: manipulator {mm_idx}")
                        status = self._execute_single_move(mm, mm_idx, mm_targets[mm_idx])
                        if status != 0:
                            return status, f"Failed sequential move for manipulator {mm_idx}"

                elif move_type == "intermediate":
                    # Move to safe intermediate position
                    mm_idx = move_step.get("manipulator")
                    target = move_step.get("target")
                    target_camera = move_step.get("target_camera")
                    
                    if target_camera is not None:
                        # New camera coordinate format
                        target_dict = {"target_camera": target_camera}
                        self.logger.log_debug(f"Intermediate move: manipulator {mm_idx} to safe camera position {target_camera}")
                        status = self._execute_single_move(mm, mm_idx, target_dict)
                        if status != 0:
                            return status, f"Failed intermediate move for manipulator {mm_idx}"
                    elif target is not None:
                        # Legacy MM coordinate format
                        self.logger.log_debug(f"Intermediate move: manipulator {mm_idx} to safe position")
                        status = self._execute_single_move(mm, mm_idx, target)
                        if status != 0:
                            return status, f"Failed intermediate move for manipulator {mm_idx}"

                elif move_type == "final":
                    # Move to final target position
                    mm_idx = move_step.get("manipulator")
                    target_camera = move_step.get("target_camera")
                    
                    if target_camera is not None:
                        # New camera coordinate format
                        target_dict = {"target_camera": target_camera}
                        self.logger.log_debug(f"Final move: manipulator {mm_idx} to target camera coords {target_camera}")
                        status = self._execute_single_move(mm, mm_idx, target_dict)
                        if status != 0:
                            return status, f"Failed final move for manipulator {mm_idx}"
                    elif mm_idx in mm_targets:
                        # Legacy MM coordinate format
                        self.logger.log_debug(f"Final move: manipulator {mm_idx} to target")
                        status = self._execute_single_move(mm, mm_idx, mm_targets[mm_idx])
                        if status != 0:
                            return status, f"Failed final move for manipulator {mm_idx}"

            return 0, "Safe movement sequence completed successfully"

        except Exception as e:
            self.logger.log_warn(f"Error executing safe movement sequence with positioning: {e}")
            return 2, f"Safe movement execution failed: {e}"

    def _draw_collision_warning(self, current_pos, target_pos, distance):
        """Draw a warning indicator for potential collision."""
        if current_pos is None or target_pos is None:
            return

        # Draw warning circle around the trajectory midpoint
        x1, y1 = current_pos
        x2, y2 = target_pos
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2

        warning_size = 20
        pen = QPen(QColor(255, 165, 0), 3)  # Orange warning
        brush = QBrush(QColor(255, 165, 0, 50))  # Semi-transparent

        warning_circle = QGraphicsEllipseItem(mid_x - warning_size / 2, mid_y - warning_size / 2, warning_size, warning_size)
        warning_circle.setPen(pen)
        warning_circle.setBrush(brush)
        self.camera_graphic_scene.addItem(warning_circle)

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

    ########Functions to be used externally
   
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
