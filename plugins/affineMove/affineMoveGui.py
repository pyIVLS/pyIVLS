import os
import numpy as np
import cv2

from PyQt6.QtCore import pyqtSignal, QObject, QEventLoop, QEvent
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QComboBox, QGraphicsScene, QGraphicsView
from PyQt6.QtGui import QImage, QPixmap, QPen, QBrush, QColor
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

        self.settingsWidget = uic.loadUi(self.path + "affinemove_Settings.ui")  # type: ignore
        self.MDIWidget = uic.loadUi(self.path + "affinemove_MDI.ui")  # type: ignore
        assert self.settingsWidget is not None, "AffineMove: settingsWidget is None"
        assert self.MDIWidget is not None, "AffineMove: MDIWidget is None"

        # connect buttons to functions
        self.settingsWidget.findSutter.clicked.connect(self._find_sutter_functionality)
        self.settingsWidget.fetchMaskButton.clicked.connect(self._fetch_mask_functionality)
        self.settingsWidget.debugButton.clicked.connect(self.affine_move)
        self.settingsWidget.previewButton.clicked.connect(self._initialize_camera_preview)
        self.settingsWidget.saveCalibrationButton.clicked.connect(self._save_calibration)
        self.settingsWidget.loadCalibrationButton.clicked.connect(self._load_calibration)

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
        self.calibrations = {}  # manipulator 1, manipulator 2, ... calibration points
        self.settings = {}  # settings dictionary for sequence builder

        # find status labels and indicators
        self.mm_status = self.settingsWidget.mmStatus
        self.sample_status = self.settingsWidget.sampleStatus
        self.points_status = self.settingsWidget.pointsStatus
        self.mm_indicator = self.settingsWidget.mmIndicator
        self.sample_indicator = self.settingsWidget.sampleIndicator
        self.points_indicator = self.settingsWidget.pointsIndicator

        self.logger = LoggingHelper(self)
        self.closelock = CloseLockSignalProvider()

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

    def _check_collisions(self, mm, points):
        """
        Checks for collisions between the manipulators and the sample.
        This function is a placeholder and should be implemented based on the specific requirements of the system.
        """

        def get_positions(mm, points):
            # open mm, get positions for all manipulators
            micromanipulator_positions = {}
            status, state = mm.mm_open()
            assert status == 0, f"Error opening micromanipulator: {state.get('Error message', 'Unknown error')}"
            status, positions = mm.mm_get_positions()  # mm_get_positions returns a dictionary with device numbers as keys and (x, y, z) tuples as values
            assert status == 0, f"Error getting micromanipulator positions: {state.get('Error message', 'Unknown error')}"

            # combine the points with the current positions of the manipulators for further processing
            for i, point in enumerate(points):
                device_idx = i
                manipulator_number = device_idx + 1  # manipulators are indexed from 1
                mm_target = self.convert_to_mm_coords(point, device_idx)  # in order: first point is assumed to be for manipulator 1, second for manipulator 2, etc.
                if mm_target is None:
                    self.logger.log_info(f"No calibration data for manipulator {manipulator_number}")
                    return None
                micromanipulator_positions[manipulator_number] = {
                    "mm_target": mm_target,
                    "current_position": positions[manipulator_number],  # throws an key error if not available
                }
            return micromanipulator_positions

        def min_distance(mm1x, mm2x, mm1y, mm2y, mm1targetx, mm1targety):
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

        micromanipulator_trajectories = get_positions(mm, points)

        SAFE_DISTANCE = 1000  # microns, distance to consider as safe from collision
        if micromanipulator_trajectories is None:
            self.logger.log_info("No micromanipulator positions available for collision check.")
            return points
        safe_moves = []
        for i, (mm1, mm2) in enumerate(zip(micromanipulator_trajectories.values(), list(micromanipulator_trajectories.values())[1:])):
            mm1x, mm1y = mm1["current_position"][:2]
            mm2x, mm2y = mm2["current_position"][:2]
            mm1targetx, mm1targety = mm1["mm_target"]
            distance = min_distance(mm1x, mm2x, mm1y, mm2y, mm1targetx, mm1targety)
            if distance < SAFE_DISTANCE:
                self.logger.log_info(f"Collision detected between manipulator {i + 1} and {i + 2}. Distance: {distance} microns.")
                # Generate a safe move for the manipulators
                safe_move = self._generate_safe_moves(mm, points)
                safe_moves.append(safe_move)
            else:
                safe_moves.append(points[i])

    def _generate_safe_moves(self, mm, points):
        """
        Generates safe moves for the manipulators to avoid collisions.
        This function is a placeholder and should be implemented based on the specific requirements of the system.
        """
        # This could involve checking the current positions, the target points, and generating a path that avoids collisions
        # For now, we will just return the points as is
        return points

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

        except Exception as e:
            self.logger.log_warn(f"Error adding visual overlays: {e}")

    def _get_manipulator_positions_in_camera(self, mm):
        """
        Get current positions of all manipulators in camera coordinates.

        Args:
            mm: Micromanipulator plugin instance

        Returns:
            dict: Dictionary mapping manipulator index to camera coordinates (x, y) or None
        """
        positions = {}
        try:
            # Get number of manipulators
            num_manipulators = mm.mm_get_num_manipulators()

            for i in range(1, num_manipulators + 1):  # Manipulator indices start from 1
                try:
                    # Get current position in manipulator coordinates
                    mm_pos = mm.mm_current_position(i)
                    if mm_pos and len(mm_pos) >= 2:
                        # Convert to camera coordinates
                        cam_pos = self.convert_mm_to_camera_coords((mm_pos[0], mm_pos[1]), i)
                        positions[i] = cam_pos
                    else:
                        positions[i] = None
                except Exception as e:
                    self.logger.log_debug(f"Could not get position for manipulator {i}: {e}")
                    positions[i] = None

        except Exception as e:
            self.logger.log_warn(f"Error getting manipulator positions: {e}")

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
            for point_idx, point_set in enumerate(self.measurement_points):
                target_coords[point_idx] = {}

                for device_idx, point in enumerate(point_set, 1):  # device_idx starts from 1
                    if point and len(point) >= 2:
                        # Points are already in camera coordinates
                        target_coords[point_idx][device_idx] = (float(point[0]), float(point[1]))
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
        colors = [QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255), QColor(255, 255, 0), QColor(255, 0, 255), QColor(0, 255, 255)]
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
        colors = [QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255), QColor(255, 255, 0), QColor(255, 0, 255), QColor(0, 255, 255)]
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
        colors = [QColor(255, 0, 0, 80), QColor(0, 255, 0, 80), QColor(0, 0, 255, 80), QColor(255, 255, 0, 80), QColor(255, 0, 255, 80), QColor(0, 255, 255, 80)]
        color = colors[(mm_idx - 1) % len(colors)]

        pen = QPen(color, 1, Qt.PenStyle.DashLine)

        line = QGraphicsLineItem(x1, y1, x2, y2)
        line.setPen(pen)
        self.camera_graphic_scene.addItem(line)

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

    def _check_movement_collision(self, mm, points):
        """
        Check for potential collisions before executing movements and generate safe move sequences.

        Args:
            mm: Micromanipulator plugin instance
            points: List of target points for each manipulator

        Returns:
            tuple: (is_safe, collision_info, safe_moves) where safe_moves is a list of movement sequences
        """
        try:
            SAFE_DISTANCE = 1000  # microns

            # Get current positions of all manipulators
            num_manipulators = mm.mm_get_num_manipulators()
            current_positions = {}
            target_positions = {}

            # Collect current and target positions
            for i in range(1, num_manipulators + 1):
                try:
                    # Get current position
                    current_pos = mm.mm_current_position(i)
                    if current_pos and len(current_pos) >= 2:
                        current_positions[i] = (current_pos[0], current_pos[1])
                    else:
                        current_positions[i] = None

                    # Get target position if available
                    if i - 1 < len(points) and points[i - 1] is not None:
                        point = points[i - 1]
                        # Convert positioning coordinates to camera coordinates, then to MM coordinates
                        mm, cam, pos = self._fetch_dep_plugins()
                        x, y = pos.positioning_coords(point)
                        mm_coords = self.convert_to_mm_coords((x, y), i)
                        target_positions[i] = mm_coords
                    else:
                        target_positions[i] = None

                except Exception as e:
                    self.logger.log_debug(f"Error getting positions for manipulator {i}: {e}")
                    current_positions[i] = None
                    target_positions[i] = None

            # Check for collisions and generate safe movement sequences
            collision_info, safe_moves = self._generate_safe_movement_sequence(current_positions, target_positions, SAFE_DISTANCE)

            is_safe = len(collision_info) == 0
            return is_safe, collision_info, safe_moves

        except Exception as e:
            self.logger.log_warn(f"Error checking movement collision: {e}")
            return False, [{"error": str(e)}], []

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
        Execute a single manipulator move.

        Args:
            mm: Micromanipulator plugin instance
            mm_idx: Manipulator index
            target: Target coordinates (x, y)

        Returns:
            int: Status code (0 = success)
        """
        try:
            mm.mm_change_active_device(mm_idx)
            mm.mm_up_max()  # Move up to avoid collisions during XY movement

            x, y = target
            status, state = mm.mm_move(x, y)
            if status:
                self.logger.log_info(f"Error moving manipulator {mm_idx}: {state.get('Error message', str(state))}")
                return 2

            return 0

        except Exception as e:
            self.logger.log_warn(f"Error executing single move for manipulator {mm_idx}: {e}")
            return 2

    def _execute_safe_movement_sequence_with_positioning(self, mm, pos, safe_moves, points):
        """
        Execute safe movement sequence using positioning coordinates.

        Args:
            mm: Micromanipulator plugin instance
            pos: Positioning plugin instance
            safe_moves: List of movement steps
            points: Original positioning points

        Returns:
            tuple: (status, message)
        """
        try:
            # Convert positioning points to MM coordinates for each manipulator
            mm_targets = {}
            for i, point in enumerate(points):
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
                    for mm_idx, target in mm_targets.items():
                        status = self._execute_single_move(mm, mm_idx, target)
                        if status != 0:
                            return status, f"Failed to execute direct move for manipulator {mm_idx}"

                elif move_type == "sequential":
                    # Move one manipulator at a time in the specified order
                    mm_idx = move_step.get("manipulator")
                    if mm_idx in mm_targets:
                        self.logger.log_debug(f"Sequential move: manipulator {mm_idx}")
                        status = self._execute_single_move(mm, mm_idx, mm_targets[mm_idx])
                        if status != 0:
                            return status, f"Failed sequential move for manipulator {mm_idx}"

                elif move_type == "intermediate":
                    # Move to safe intermediate position
                    mm_idx = move_step.get("manipulator")
                    target = move_step.get("target")
                    if mm_idx is not None and target is not None:
                        self.logger.log_debug(f"Intermediate move: manipulator {mm_idx} to safe position")
                        status = self._execute_single_move(mm, mm_idx, target)
                        if status != 0:
                            return status, f"Failed intermediate move for manipulator {mm_idx}"

                elif move_type == "final":
                    # Move to final target position
                    mm_idx = move_step.get("manipulator")
                    if mm_idx in mm_targets:
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
    def affine_move(self):
        """
        This function is the main entry point for standalone testing. It moves to the next measurement point.
        For sequence builder operation, use loopingIteration() instead.
        """
        try:
            mm, _, pos = self._fetch_dep_plugins()

            # check if plugins are available
            if mm is None or pos is None:
                return [3, "AffineMove: micromanipulator or positioning plugin is None"]

            # open mm and check for errors
            status, state = mm.mm_open()
            if status:
                return [1, state.get("Error message", str(state))]

            # check if there are measurement points available
            if len(self.measurement_points) == 0:
                return [3, "No measurement points available"]

            # reset the iteration if it exceeds the number of measurement points
            if self.iter >= len(self.measurement_points):
                self.iter = 0

            points = self.measurement_points[self.iter]
            point_name = self.measurement_point_names[self.iter]

            # Check for collision before movement and get safe movement sequence
            is_safe, collision_info, safe_moves = self._check_movement_collision(mm, points)

            if not is_safe:
                if safe_moves:
                    # Execute collision avoidance sequence
                    self.logger.log_info(f"Collision detected, executing safe movement sequence with {len(safe_moves)} steps")

                    # Convert points for safe execution
                    converted_points = []
                    for i, point in enumerate(points):
                        x, y = pos.positioning_coords(point)
                        mm_coords = self.convert_to_mm_coords((x, y), i + 1)
                        if mm_coords is None:
                            return [2, f"No calibration data for manipulator {i + 1}"]
                        converted_points.append((i + 1, mm_coords))  # (manipulator_idx, target_coords)

                    # Execute safe movement sequence
                    status, message = self._execute_safe_movement_sequence_with_positioning(mm, pos, safe_moves, points)
                    if status != 0:
                        return [status, message]
                else:
                    # No safe sequence could be generated
                    collision_details = []
                    for collision in collision_info:
                        if "error" in collision:
                            collision_details.append(f"Error: {collision['error']}")
                        else:
                            collision_details.append(f"Manipulator {collision['manipulator1']} <-> {collision['manipulator2']}: {collision['distance']:.1f} μm (safe: {collision['safe_distance']} μm)")

                    collision_msg = "Collision detected and no safe sequence found! " + "; ".join(collision_details)
                    self.logger.log_warn(collision_msg)
                    return [2, f"Movement blocked: {collision_msg}"]
            else:
                # No collisions, execute normal movement
                for i, point in enumerate(points):
                    mm.mm_change_active_device(i + 1)  # manipulators indexed from 0
                    mm.mm_up_max()
                    # convert the point to camera coordinates
                    x, y = pos.positioning_coords(point)
                    # convert camera point to micromanipulator coordinates
                    mm_coords = self.convert_to_mm_coords((x, y), i + 1)
                    if mm_coords is None:
                        return [2, f"No calibration data for manipulator {i + 1}"]

                    x, y = mm_coords
                    status, state = mm.mm_move(x, y)
                    if status:
                        self.logger.log_info(state.get("Error message", str(state)))
                        return [2, state.get("Error message", str(state))]

            self.iter += 1
            return [0, f"Moved to point {point_name} ({self.iter}/{len(self.measurement_points)})"]

        except Exception as e:
            self.logger.log_info(f"Error in affine_move: {str(e)}")
            return [2, f"Affine_move: {str(e)}"]

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

            # Check for collision before movement and get safe movement sequence
            is_safe, collision_info, safe_moves = self._check_movement_collision(mm, points)

            if not is_safe:
                if safe_moves:
                    # Execute collision avoidance sequence
                    self.logger.log_info(f"Collision detected in iteration {currentIteration}, executing safe movement sequence with {len(safe_moves)} steps")

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
                        else:
                            collision_details.append(f"Manipulator {collision['manipulator1']} <-> {collision['manipulator2']}: {collision['distance']:.1f} μm (safe: {collision['safe_distance']} μm)")

                    collision_msg = "Collision detected and no safe sequence found! " + "; ".join(collision_details)
                    self.logger.log_warn(collision_msg)
                    return [2, f"_collision_iter{currentIteration}"]
            else:
                # No collisions, execute normal movement
                for i, point in enumerate(points):
                    mm.mm_change_active_device(i + 1)  # manipulators indexed from 0
                    mm.mm_up_max()
                    # convert the point to camera coordinates
                    x, y = pos.positioning_coords(point)
                    # convert camera point to micromanipulator coordinates
                    mm_coords = self.convert_to_mm_coords((x, y), i + 1)
                    if mm_coords is None:
                        self.logger.log_info(f"No calibration data for manipulator {i + 1}")
                        return [2, f"_error_iter{currentIteration}"]

                    x, y = mm_coords
                    status, state = mm.mm_move(x, y)
                    if status:
                        self.logger.log_info(f"Error moving manipulator {i + 1}: {state.get('Error message', str(state))}")
                        return [2, f"_error_iter{currentIteration}"]

            self.logger.log_info(f"Moved to measurement point {point_name} (iteration {currentIteration})")
            return [0, f"_{point_name}"]

        except Exception as e:
            self.logger.log_info(f"Error in loopingIteration: {str(e)}")
            return [2, f"_error_iter{currentIteration}"]
