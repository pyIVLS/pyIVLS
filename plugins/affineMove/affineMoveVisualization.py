"""
Visualization and drawing functionality for affineMove plugin.
Separated from main GUI class to improve modularity and maintainability.
"""

import numpy as np
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem
from PyQt6.QtGui import QImage, QPixmap, QPen, QBrush, QColor, QFont
from PyQt6.QtCore import Qt


class AffineMoveVisualization:
    """Handles all visualization and drawing operations for the affineMove plugin."""

    def __init__(self, graphics_view: QGraphicsView, graphics_scene: QGraphicsScene):
        self.graphics_view = graphics_view
        self.graphics_scene = graphics_scene

        # Color schemes for different manipulators
        self.manipulator_colors = [
            QColor(255, 0, 0),  # Red
            QColor(0, 255, 0),  # Green
            QColor(0, 0, 255),  # Blue
            QColor(255, 255, 0),  # Yellow
            QColor(255, 0, 255),  # Magenta
            QColor(0, 255, 255),  # Cyan
        ]

        # Camera image bounds for preventing view expansion
        self.camera_image_bounds = (0, 0, 800, 600)  # Default bounds

    def update_graphics_view(self, img):
        """Updates the graphics view with a new camera image."""
        if img is None:
            return

        # Convert numpy array to QImage if necessary
        if isinstance(img, np.ndarray):
            if len(img.shape) == 3:  # Color image
                height, width, channel = img.shape
                bytes_per_line = 3 * width
                q_image = QImage(img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            else:  # Grayscale image
                height, width = img.shape
                bytes_per_line = width
                q_image = QImage(img.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8)
        else:
            q_image = img

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
        show_bounding_boxes=False,
    ):
        """
        Adds visual overlays to the graphics scene.

        Args:
            manipulator_positions: Dict of {manipulator_idx: (x, y)} current positions
            target_positions: Dict of {manipulator_idx: (x, y)} target positions
            planned_moves: List of (manipulator_idx, current_pos, target_pos) for planned moves
            bounding_boxes: Dict of {manipulator_idx: AABB} bounding boxes
            show_bounding_boxes: Whether to display bounding boxes
        """
        # Draw current manipulator positions
        if manipulator_positions:
            for mm_idx, pos in manipulator_positions.items():
                if pos:
                    self._draw_manipulator_dot(pos, mm_idx)

        # Draw target reference positions
        if target_positions:
            for mm_idx, pos in target_positions.items():
                if pos:
                    self._draw_target_reference_dot(pos, mm_idx)

        # Draw planned moves
        if planned_moves:
            self._draw_planned_moves(planned_moves)

        # Draw bounding boxes if enabled
        if show_bounding_boxes and bounding_boxes:
            self._draw_manipulator_bounding_boxes(bounding_boxes)

    def _draw_manipulator_dot(self, cam_pos, mm_idx):
        """Draw a dot representing the current manipulator position."""
        x, y = cam_pos
        color = self._get_manipulator_color(mm_idx)

        # Create filled circle
        ellipse = QGraphicsEllipseItem(x - 5, y - 5, 10, 10)
        ellipse.setBrush(QBrush(color))
        ellipse.setPen(QPen(Qt.GlobalColor.black, 2))
        self.graphics_scene.addItem(ellipse)

        # Add label
        text = QGraphicsTextItem(f"M{mm_idx}")
        text.setPos(x + 8, y - 8)
        text.setDefaultTextColor(color)
        font = QFont()
        font.setBold(True)
        text.setFont(font)
        self.graphics_scene.addItem(text)

    def _draw_target_reference_dot(self, target_pos, mm_idx):
        """Draw a dot representing the target position."""
        x, y = target_pos
        color = self._get_manipulator_color(mm_idx)

        # Create hollow circle for target
        ellipse = QGraphicsEllipseItem(x - 8, y - 8, 16, 16)
        ellipse.setBrush(QBrush(Qt.GlobalColor.transparent))
        ellipse.setPen(QPen(color, 3))
        self.graphics_scene.addItem(ellipse)

        # Add cross in the center
        line1 = QGraphicsLineItem(x - 4, y, x + 4, y)
        line1.setPen(QPen(color, 2))
        self.graphics_scene.addItem(line1)

        line2 = QGraphicsLineItem(x, y - 4, x, y + 4)
        line2.setPen(QPen(color, 2))
        self.graphics_scene.addItem(line2)

    def _draw_planned_moves(self, planned_moves):
        """Draw planned movement trajectories and targets."""
        for manipulator_idx, current_pos, target_pos in planned_moves:
            if current_pos and target_pos:
                self._draw_planned_trajectory_line(current_pos, target_pos, manipulator_idx)
                self._draw_planned_target_dot(target_pos, manipulator_idx)
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

    def _draw_planned_target_dot(self, target_pos, mm_idx):
        """Draw the planned target position."""
        x, y = target_pos
        color = self._get_manipulator_color(mm_idx)

        # Create diamond shape for planned target
        size = 6
        points = [
            (x, y - size),  # Top
            (x + size, y),  # Right
            (x, y + size),  # Bottom
            (x - size, y),  # Left
        ]

        # Note: QGraphicsPolygonItem would be better but requires QPolygonF
        # For simplicity, draw as lines forming a diamond
        for i in range(4):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % 4]
            line = QGraphicsLineItem(x1, y1, x2, y2)
            line.setPen(QPen(color, 2))
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

    def _draw_trajectory_line(self, current_pos, target_pos, mm_idx):
        """Draw a solid trajectory line for actual movements."""
        x1, y1 = current_pos
        x2, y2 = target_pos
        color = self._get_manipulator_color(mm_idx)

        line = QGraphicsLineItem(x1, y1, x2, y2)
        line.setPen(QPen(color, 3))
        self.graphics_scene.addItem(line)

    def _draw_position_labels(self, current_pos, target_pos, mm_idx):
        """Draw position coordinate labels."""
        if current_pos:
            x, y = current_pos
            text = QGraphicsTextItem(f"({x:.0f},{y:.0f})")
            text.setPos(x + 12, y - 20)
            text.setDefaultTextColor(self._get_manipulator_color(mm_idx))
            font = QFont()
            font.setPointSize(7)
            text.setFont(font)
            self.graphics_scene.addItem(text)

    def _draw_manipulator_bounding_boxes(self, bounding_boxes):
        """Draw bounding boxes for all manipulators."""
        for manipulator_idx, bbox in bounding_boxes.items():
            if bbox:
                coords = bbox.get_absolute_corners()
                self._draw_bounding_box(coords, manipulator_idx, is_absolute=True)

    def _draw_bounding_box(self, coords, manipulator_idx, is_absolute=False):
        """
        Draw a bounding box on the graphics scene.

        Args:
            coords: List of (x, y) coordinate tuples defining the box corners
            manipulator_idx: Index of the manipulator for color coding
            is_absolute: Whether coordinates are absolute (True) or relative (False)
        """
        if len(coords) < 3:
            return

        color = self._get_manipulator_color(manipulator_idx)
        pen = QPen(color, 2)
        pen.setStyle(Qt.PenStyle.DotLine)

        # Draw lines connecting all corners
        for i in range(len(coords)):
            x1, y1 = coords[i]
            x2, y2 = coords[(i + 1) % len(coords)]

            line = QGraphicsLineItem(x1, y1, x2, y2)
            line.setPen(pen)
            self.graphics_scene.addItem(line)

        # Add label
        if coords:
            center_x = sum(x for x, y in coords) / len(coords)
            center_y = sum(y for x, y in coords) / len(coords)

            text = QGraphicsTextItem(f"BB{manipulator_idx}")
            text.setPos(center_x - 15, center_y - 8)
            text.setDefaultTextColor(color)
            font = QFont()
            font.setPointSize(8)
            font.setBold(True)
            text.setFont(font)
            self.graphics_scene.addItem(text)

    def _get_manipulator_color(self, mm_idx):
        """Get the color for a specific manipulator index."""
        return self.manipulator_colors[mm_idx % len(self.manipulator_colors)]

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
