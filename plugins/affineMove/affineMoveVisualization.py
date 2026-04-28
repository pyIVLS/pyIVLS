"""
Visualization and drawing functionality for affineMove plugin.
Separated from main GUI class to improve modularity and maintainability.
"""

import numpy as np
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem, QGraphicsRectItem
from PyQt6.QtGui import QImage, QPixmap, QPen, QBrush, QColor, QFont
from PyQt6.QtCore import Qt
from plugins.affineMove.collisionDetection import AABB
from plugin_components import MANIPULATOR_COLORS


class AffineMoveVisualization:
    """Handles all visualization and drawing operations for the affineMove plugin."""

    def __init__(self, graphics_view: QGraphicsView, graphics_scene: QGraphicsScene):
        self.graphics_view = graphics_view
        self.graphics_scene = graphics_scene

        self.manipulator_colors = MANIPULATOR_COLORS

        # Camera image bounds for preventing view expansion
        self.camera_image_bounds = (0, 0, 800, 600)  # Default bounds
        self.calibration_points = []

    def set_calibration_points(self, points):
        """Set the current calibration points for visualization."""
        self.calibration_points = points

    def update_graphics_view(self, img):
        """Updates the graphics view with a new camera image."""
        if img is None:
            return

        # Convert to QImage
        if isinstance(img, np.ndarray):
            height, width, channel = img.shape
            bytes_per_line = 3 * width
            q_image = QImage(img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

        # Update image bounds based on actual image size
        self.camera_image_bounds = (0, 0, q_image.width(), q_image.height())

        # Create pixmap and add to scene
        pixmap = QPixmap.fromImage(q_image)
        self.graphics_scene.clear()
        self.graphics_scene.addPixmap(pixmap)

        # Set scene rectangle to match image bounds
        self.graphics_scene.setSceneRect(0, 0, q_image.width(), q_image.height())

    def add_visual_overlays(
        self,
        manipulator_positions=None,
        target_positions=None,
        planned_moves=None,
        bounding_boxes=None,
    ):
        """
        Adds visual overlays to the graphics scene.

        Args:
            manipulator_positions: Dict of {manipulator_idx: (x, y)} current positions
            target_positions: Dict of {manipulator_idx: (x, y)} target positions
            planned_moves: List of (manipulator_idx, current_pos, target_pos) for planned moves
            bounding_boxes: Dict of {manipulator_idx: AABB} bounding boxes
        """
        # Draw current manipulator positions
        if manipulator_positions:
            for mm_idx, pos in manipulator_positions.items():
                if pos:
                    self._draw_manipulator_dot(pos, mm_idx)

        if target_positions:
            for point_name, location_dict in target_positions.items():
                for mm_idx, pos in location_dict.items():
                    if pos:
                        self._draw_target_reference_dot(pos, mm_idx)

        # Draw planned moves
        if planned_moves:
            self._draw_planned_moves(planned_moves)

        # draw bounding boxes
        if bounding_boxes:
            self._draw_manipulator_bounding_boxes(bounding_boxes)

        if len(self.calibration_points) > 0:
            count = len(self.calibration_points)
            for i, camera_point in enumerate(self.calibration_points):
                # point_pair is (mm_point, camera_point), we want to draw camera_point
                self._draw_calibration_point(camera_point, i + 1, count)

    def _draw_manipulator_dot(self, cam_pos, mm_idx):
        """Draw a dot representing the current manipulator position."""
        x, y = cam_pos
        color = self._get_manipulator_color(mm_idx)

        # Create filled circle
        ellipse = QGraphicsEllipseItem(x - 5, y - 5, 10, 10)
        ellipse.setBrush(QBrush(color))
        ellipse.setPen(QPen(Qt.GlobalColor.black, 2))
        self.graphics_scene.addItem(ellipse)

    def _draw_target_reference_dot(self, cam_pos, mm_idx):
        """Draw a target reference dot with enhanced visibility."""
        x, y = cam_pos
        color = self._get_manipulator_color(mm_idx)

        # Create larger circle for better visibility
        ellipse = QGraphicsEllipseItem(x - 6, y - 6, 12, 12)
        ellipse.setBrush(QBrush(color))
        ellipse.setPen(QPen(Qt.GlobalColor.white, 3))  # White border for contrast
        self.graphics_scene.addItem(ellipse)

        # Add inner dot for target appearance
        inner_ellipse = QGraphicsEllipseItem(x - 2, y - 2, 4, 4)
        inner_ellipse.setBrush(QBrush(Qt.GlobalColor.white))
        inner_ellipse.setPen(QPen(Qt.GlobalColor.white, 1))
        self.graphics_scene.addItem(inner_ellipse)

    def _draw_planned_moves(self, planned_moves):
        """Draw planned movement trajectories and targets."""
        for manipulator_idx, current_pos, target_pos in planned_moves:
            if current_pos and target_pos:
                self._draw_planned_trajectory_line(current_pos, target_pos, manipulator_idx)
                self._draw_planned_move_labels(current_pos, target_pos, manipulator_idx)

    def _draw_planned_trajectory_line(self, current_pos, target_pos, mm_idx):
        """Draw a line showing the planned trajectory."""
        x1, y1 = current_pos
        x2, y2 = target_pos
        color = self._get_manipulator_color(mm_idx)

        # Create dashed line for planned moves
        pen = QPen(color, 2)
        pen.setStyle(Qt.PenStyle.DashLine)

        line = QGraphicsLineItem(x1, y1, x2, y2)
        line.setPen(pen)
        self.graphics_scene.addItem(line)

    def _draw_planned_move_labels(self, current_pos, target_pos, mm_idx):
        """Draw labels for planned moves."""
        x2, y2 = target_pos
        color = self._get_manipulator_color(mm_idx)

        # Calculate distance
        x1, y1 = current_pos
        distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        # Add distance label near target
        text = QGraphicsTextItem(f"→{distance:.0f}px")
        text.setPos(x2 + 10, y2 + 10)
        text.setDefaultTextColor(color)
        font = QFont()
        font.setPointSize(8)
        text.setFont(font)
        self.graphics_scene.addItem(text)

    def _draw_manipulator_bounding_boxes(self, bounding_boxes):
        """Draw bounding boxes for all manipulators."""
        for manipulator_idx, bbox in bounding_boxes.items():
            if bbox:
                try:
                    self._draw_bounding_box(bbox, manipulator_idx)
                except Exception as e:
                    print(f"Error drawing bounding box for manipulator {manipulator_idx}: {e}")

    def _draw_bounding_box(self, aabb: AABB, mm_idx):
        """Draw bounding box for a manipulator."""
        color = self._get_manipulator_color(mm_idx)

        try:
            corners = aabb.get_absolute_corners()

            # Two points defining a rectangle (top-left and bottom-right)
            x1, y1 = corners[0]
            x2, y2 = corners[1]

            # Create rectangle
            rect = QGraphicsRectItem(x1, y1, x2 - x1, y2 - y1)
            rect.setPen(QPen(color, 3))  # Thicker lines for better visibility
            rect.setBrush(QBrush())  # Transparent fill
            self.graphics_scene.addItem(rect)

        except Exception as e:
            print(f"Error drawing bounding box for manipulator {mm_idx}: {e}")

    def _get_manipulator_color(self, mm_idx):
        """Get the color for a specific manipulator index."""
        if mm_idx < 1 or mm_idx > len(self.manipulator_colors):
            raise ValueError(f"Manipulator index {mm_idx} is out of range. Must be between 1 and {len(self.manipulator_colors)}.")
        return self.manipulator_colors[mm_idx - 1]

    def clear_overlays(self):
        """Clear all overlays while keeping the background image."""
        # Store the background pixmap
        pixmap_items = [item for item in self.graphics_scene.items() if hasattr(item, "pixmap")]

        # Clear scene
        self.graphics_scene.clear()

        # Restore background pixmap
        for item in pixmap_items:
            self.graphics_scene.addItem(item)

    def update_camera_bounds(self, width, height):
        """Update the camera image bounds."""
        self.camera_image_bounds = (0, 0, width, height)
        self.graphics_scene.setSceneRect(0, 0, width, height)

    def _draw_calibration_point(self, point, point_number, total_points):
        """Draw a calibration point with a large indicator and progress text.

        Args:
            point: (x, y) tuple of the clicked point
            point_number: Current point number (1-indexed)
            total_points: Total number of points needed
            manipulator_idx: Index of the manipulator being calibrated
        """
        if point is None:
            return
        x, y = point

        # Draw a large crosshair at the clicked point
        crosshair_size = 20

        # Horizontal line
        h_line = QGraphicsLineItem(x - crosshair_size, y, x + crosshair_size, y)
        h_line.setPen(QPen(Qt.GlobalColor.red, 3))
        self.graphics_scene.addItem(h_line)

        # Vertical line
        v_line = QGraphicsLineItem(x, y - crosshair_size, x, y + crosshair_size)
        v_line.setPen(QPen(Qt.GlobalColor.red, 3))
        self.graphics_scene.addItem(v_line)

        # Add text label with point number
        text = QGraphicsTextItem(f"Point {point_number}/{total_points}")
        text.setPos(x + 25, y - 10)
        text.setDefaultTextColor(Qt.GlobalColor.red)
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        text.setFont(font)
        self.graphics_scene.addItem(text)
