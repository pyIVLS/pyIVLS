import itertools
import time
from typing import List, Tuple, Dict, Optional


class AABB:
    """Axis-aligned bounding box (AABB) for collision detection. Works in 2D space"""

    def __init__(self, tip_x: float, tip_y: float, relative_corners: List[Tuple[float, float]]):
        """Initialize the AABB with tip position and absolute corner coordinates in camera coordinates"""
        self.tip_x = tip_x
        self.tip_y = tip_y
        self.relative_corners = relative_corners

    def move_bbox(self, new_ti):

    def colliding_with(self, other: "AABB") -> bool:
        """Check if this AABB intersects with another AABB"""
        return not (self.relative_corners[0][0] < other.relative_corners[0][0] or self.relative_corners[1][0] > other.relative_corners[1][0] or self.relative_corners[0][1] < other.relative_corners[0][1] or self.relative_corners[1][1] > other.relative_corners[1][1])

    def get_corners(self) -> List[Tuple[float, float]]:
        """Get the four corners of the AABB"""
        return self.relative_corners

    def __str__(self) -> str:
        return f"AABB({self.tip_x:.1f}, {self.tip_y:.1f}, {self.relative_corners[1][0]:.1f}, {self.relative_corners[1][1]:.1f})"


class MovementPlanner:
    """Handles finding safe movement sequences to avoid collisions"""


class CollisionDetector:
    """Handles collision detection between micromanipulators using bounding boxes"""

    def __init__(self):
        self.bounding_boxes: Dict[int, AABB] = {}

    def set_bounding_box(self, manipulator_idx: int, tip_x: float, tip_y: float, absolute_corners: List[Tuple[float, float]]):
        """Set the bounding box for a manipulator"""
        self.bounding_boxes[manipulator_idx] = bounding_box
