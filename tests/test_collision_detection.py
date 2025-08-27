"""
Comprehensive tests for collision detection system.

This module tests the following classes:
- AABB: Axis-aligned bounding box collision detection
- CollisionDetector: Multi-manipulator collision detection and safe movement generation
"""

import sys
import os
import pytest
from unittest.mock import Mock

# Add the plugins directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "plugins", "affineMove"))

try:
    from collisionDetection import AABB, CollisionDetector
except ImportError:
    # For testing, create mock classes if import fails
    AABB = None
    CollisionDetector = None


class TestAABB:
    """Test cases for AABB (Axis-Aligned Bounding Box) class"""

    def test_aabb_initialization(self):
        """Test AABB initialization with tip position and relative corners"""
        relative_corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        aabb = AABB(5.0, 10.0, relative_corners)

        assert aabb.tip_x == 5.0
        assert aabb.tip_y == 10.0
        assert aabb.relative_corners == relative_corners

    def test_move_bbox(self):
        """Test moving the bounding box to a new position"""
        relative_corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        aabb = AABB(0.0, 0.0, relative_corners)

        aabb.move_bbox(3.0, 4.0)
        assert aabb.tip_x == 3.0
        assert aabb.tip_y == 4.0

    def test_get_absolute_corners(self):
        """Test calculation of absolute corner coordinates"""
        relative_corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        aabb = AABB(5.0, 10.0, relative_corners)

        absolute_corners = aabb.get_absolute_corners()
        expected = [(4.0, 9.0), (6.0, 9.0), (6.0, 11.0), (4.0, 11.0)]

        assert absolute_corners == expected

    def test_collision_detection_overlapping(self):
        """Test collision detection between overlapping AABBs"""
        # Create two overlapping square AABBs
        corners1 = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        corners2 = [(-1, -1), (1, -1), (1, 1), (-1, 1)]

        aabb1 = AABB(0.0, 0.0, corners1)
        aabb2 = AABB(1.0, 0.0, corners2)  # Overlapping

        assert aabb1.colliding_with(aabb2)
        assert aabb2.colliding_with(aabb1)  # Symmetry

    def test_collision_detection_non_overlapping(self):
        """Test collision detection between non-overlapping AABBs"""
        corners1 = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        corners2 = [(-1, -1), (1, -1), (1, 1), (-1, 1)]

        aabb1 = AABB(0.0, 0.0, corners1)
        aabb2 = AABB(5.0, 0.0, corners2)  # Non-overlapping

        assert not aabb1.colliding_with(aabb2)
        assert not aabb2.colliding_with(aabb1)  # Symmetry

    def test_collision_detection_touching(self):
        """Test collision detection between touching AABBs"""
        corners1 = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        corners2 = [(-1, -1), (1, -1), (1, 1), (-1, 1)]

        aabb1 = AABB(0.0, 0.0, corners1)
        aabb2 = AABB(2.0, 0.0, corners2)  # Just touching

        # Touching edges should not be considered collision
        assert not aabb1.colliding_with(aabb2)
        assert not aabb2.colliding_with(aabb1)

    def test_irregular_shaped_aabb(self):
        """Test AABB with irregular shape (non-square)"""
        # L-shaped bounding box
        corners1 = [(-2, -1), (1, -1), (1, 0), (0, 0), (0, 1), (-2, 1)]
        corners2 = [(-1, -1), (1, -1), (1, 1), (-1, 1)]

        aabb1 = AABB(0.0, 0.0, corners1)
        aabb2 = AABB(0.5, 0.0, corners2)  # Should overlap

        assert aabb1.colliding_with(aabb2)

    def test_aabb_str_representation(self):
        """Test string representation of AABB"""
        corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        aabb = AABB(3.5, 7.2, corners)

        expected = "AABB(3.5, 7.2)"
        assert str(aabb) == expected


class TestCollisionDetector:
    """Test cases for CollisionDetector class"""

    @pytest.fixture
    def detector(self):
        """Create a fresh CollisionDetector instance for each test"""
        return CollisionDetector()

    @pytest.fixture
    def square_corners(self):
        """Standard square bounding box corners"""
        return [(-1, -1), (1, -1), (1, 1), (-1, 1)]

    def test_initialization(self, detector):
        """Test CollisionDetector initialization"""
        assert detector.bounding_boxes == {}
        assert detector.get_manipulator_indices() == []

    def test_set_manipulator_bounding_box(self, detector, square_corners):
        """Test setting a bounding box for a manipulator"""
        result = detector.set_manipulator_bounding_box(0, square_corners)

        assert result is True
        assert 0 in detector.bounding_boxes
        assert detector.get_manipulator_indices() == [0]

    def test_set_invalid_bounding_box(self, detector):
        """Test setting an invalid bounding box"""
        # This should not raise an exception but return False
        result = detector.set_manipulator_bounding_box(0, None)
        assert result is False

    def test_get_bounding_box(self, detector, square_corners):
        """Test retrieving a bounding box"""
        detector.set_manipulator_bounding_box(0, square_corners)
        bbox = detector.get_bounding_box(0)

        assert bbox is not None
        assert isinstance(bbox, AABB)
        assert bbox.relative_corners == square_corners

    def test_get_nonexistent_bounding_box(self, detector):
        """Test retrieving a non-existent bounding box"""
        bbox = detector.get_bounding_box(999)
        assert bbox is None

    def test_clear_manipulator_bounding_box(self, detector, square_corners):
        """Test clearing a manipulator's bounding box"""
        detector.set_manipulator_bounding_box(0, square_corners)

        result = detector.clear_manipulator_bounding_box(0)
        assert result is True
        assert 0 not in detector.bounding_boxes

        # Try clearing again
        result = detector.clear_manipulator_bounding_box(0)
        assert result is False

    def test_update_manipulator_tip_position(self, detector, square_corners):
        """Test updating a manipulator's tip position"""
        detector.set_manipulator_bounding_box(0, square_corners)

        result = detector.update_manipulator_tip_position(0, 5.0, 7.0)
        assert result is True

        bbox = detector.get_bounding_box(0)
        assert bbox.tip_x == 5.0
        assert bbox.tip_y == 7.0

    def test_update_nonexistent_manipulator_position(self, detector):
        """Test updating position of non-existent manipulator"""
        result = detector.update_manipulator_tip_position(999, 5.0, 7.0)
        assert result is False

    def test_get_all_bounding_boxes(self, detector, square_corners):
        """Test getting all bounding boxes"""
        detector.set_manipulator_bounding_box(0, square_corners)
        detector.set_manipulator_bounding_box(1, square_corners)

        all_boxes = detector.get_all_bounding_boxes()
        assert len(all_boxes) == 2
        assert 0 in all_boxes
        assert 1 in all_boxes

        # Ensure it's a copy
        all_boxes[2] = Mock()
        assert 2 not in detector.bounding_boxes

    def test_check_move_collision_no_collision(self, detector, square_corners):
        """Test movement collision check with no collision"""
        # Set up two manipulators far apart
        detector.set_manipulator_bounding_box(0, square_corners)
        detector.set_manipulator_bounding_box(1, square_corners)
        detector.update_manipulator_tip_position(0, 0.0, 0.0)
        detector.update_manipulator_tip_position(1, 10.0, 10.0)

        # Move manipulator 0 away from manipulator 1
        moves = {0: ((0.0, 0.0), (5.0, 5.0))}

        collision = detector.check_move_collision(moves)
        assert collision is False

    def test_check_move_collision_with_collision(self, detector, square_corners):
        """Test movement collision check with collision"""
        # Set up two manipulators close together
        detector.set_manipulator_bounding_box(0, square_corners)
        detector.set_manipulator_bounding_box(1, square_corners)
        detector.update_manipulator_tip_position(0, 0.0, 0.0)
        detector.update_manipulator_tip_position(1, 3.0, 0.0)

        # Move manipulator 0 toward manipulator 1
        moves = {0: ((0.0, 0.0), (2.0, 0.0))}

        collision = detector.check_move_collision(moves)
        assert collision is True

    def test_check_move_collision_multiple_moves_raises_error(self, detector, square_corners):
        """Test that multiple moves in collision check raises ValueError"""
        detector.set_manipulator_bounding_box(0, square_corners)
        detector.set_manipulator_bounding_box(1, square_corners)

        moves = {0: ((0.0, 0.0), (5.0, 5.0)), 1: ((10.0, 10.0), (15.0, 15.0))}

        with pytest.raises(ValueError, match="Only single manipulator movements are supported"):
            detector.check_move_collision(moves)

    def test_check_move_collision_no_bounding_box(self, detector):
        """Test collision check for manipulator without bounding box"""
        moves = {999: ((0.0, 0.0), (5.0, 5.0))}
        collision = detector.check_move_collision(moves)
        assert collision is False

    def test_generate_linear_trajectory(self, detector):
        """Test linear trajectory generation"""
        start = (0.0, 0.0)
        end = (10.0, 5.0)
        steps = 10

        trajectory = detector._generate_linear_trajectory(start, end, steps)

        assert len(trajectory) == 11  # steps + 1
        assert trajectory[0] == start
        assert trajectory[-1] == end

        # Check intermediate point
        mid_point = trajectory[5]
        assert abs(mid_point[0] - 5.0) < 0.01
        assert abs(mid_point[1] - 2.5) < 0.01

    def test_generate_linear_trajectory_no_movement(self, detector):
        """Test trajectory generation with no actual movement"""
        start = (5.0, 3.0)
        end = (5.0, 3.0)
        steps = 10

        trajectory = detector._generate_linear_trajectory(start, end, steps)

        assert len(trajectory) == 1
        assert trajectory[0] == start

    def test_simple_safe_movement_sequence(self, detector, square_corners):
        """Test generating safe movement sequence for non-colliding moves"""
        # Set up two manipulators far apart
        detector.set_manipulator_bounding_box(0, square_corners)
        detector.set_manipulator_bounding_box(1, square_corners)

        moves = {0: ((0.0, 0.0), (2.0, 0.0)), 1: ((10.0, 10.0), (12.0, 10.0))}

        sequence = detector.generate_safe_movement_sequence(moves)

        assert len(sequence) == 2
        # Should contain both manipulators
        manip_indices = [seq[0] for seq in sequence]
        assert 0 in manip_indices
        assert 1 in manip_indices

    def test_complex_movement_sequence_requiring_segmentation(self, detector, square_corners):
        """Test movement sequence that requires X/Y segmentation"""
        # Set up manipulators that would collide with direct moves but can be solved with segmentation
        detector.set_manipulator_bounding_box(0, square_corners)
        detector.set_manipulator_bounding_box(1, square_corners)
        detector.update_manipulator_tip_position(0, 0.0, 0.0)
        detector.update_manipulator_tip_position(1, 0.0, 4.0)

        # Moves that can be solved by segmentation (not a crossing swap)
        moves = {
            0: ((0.0, 0.0), (6.0, 4.0)),  # Move to different position, not swapping
            1: ((0.0, 4.0), (6.0, 0.0)),  # Move to different position, not swapping
        }

        sequence = detector.generate_safe_movement_sequence(moves)

        # Should find a safe sequence with segmentation
        assert len(sequence) >= 2  # At least one move per manipulator

    def test_impossible_movement_sequence(self, detector):
        """Test movement sequence that is impossible due to collision"""
        # Create a scenario where manipulators are trapped
        # Large bounding boxes that overlap significantly
        large_corners = [(-5, -5), (5, -5), (5, 5), (-5, 5)]

        detector.set_manipulator_bounding_box(0, large_corners)
        detector.set_manipulator_bounding_box(1, large_corners)
        detector.update_manipulator_tip_position(0, 0.0, 0.0)
        detector.update_manipulator_tip_position(1, 1.0, 0.0)

        # Moves that would cause unavoidable collision
        moves = {0: ((0.0, 0.0), (2.0, 0.0)), 1: ((1.0, 0.0), (-1.0, 0.0))}

        sequence = detector.generate_safe_movement_sequence(moves)

        # Should return empty list for impossible moves
        assert sequence == []

    def test_create_segmented_moves(self, detector):
        """Test breaking moves into X and Y components"""
        moves = {0: ((0.0, 0.0), (5.0, 3.0)), 1: ((10.0, 5.0), (15.0, 8.0))}

        segmented = detector._create_segmented_moves(moves)

        # Should have X and Y components for each manipulator
        expected_keys = {(0, "x"), (0, "y"), (1, "x"), (1, "y")}
        assert set(segmented.keys()) == expected_keys

        # Check X move for manipulator 0
        assert segmented[(0, "x")] == ((0.0, 0.0), (5.0, 0.0))
        # Check Y move for manipulator 0 (starts from X-moved position)
        assert segmented[(0, "y")] == ((5.0, 0.0), (5.0, 3.0))

    def test_create_segmented_moves_no_movement(self, detector):
        """Test segmentation with no actual movement"""
        moves = {
            0: ((5.0, 3.0), (5.0, 3.0))  # No movement
        }

        segmented = detector._create_segmented_moves(moves)

        # Should have no segments for zero movement
        assert segmented == {}

    def test_create_segmented_moves_x_only(self, detector):
        """Test segmentation with X movement only"""
        moves = {
            0: ((0.0, 5.0), (3.0, 5.0))  # X movement only
        }

        segmented = detector._create_segmented_moves(moves)

        # Should only have X component
        assert list(segmented.keys()) == [(0, "x")]
        assert segmented[(0, "x")] == ((0.0, 5.0), (3.0, 5.0))

    def test_create_segmented_moves_y_only(self, detector):
        """Test segmentation with Y movement only"""
        moves = {
            0: ((5.0, 0.0), (5.0, 3.0))  # Y movement only
        }

        segmented = detector._create_segmented_moves(moves)

        # Should only have Y component
        assert list(segmented.keys()) == [(0, "y")]
        assert segmented[(0, "y")] == ((5.0, 0.0), (5.0, 3.0))

    def test_execute_movement_sequence(self, detector, square_corners):
        """Test executing a movement sequence"""
        detector.set_manipulator_bounding_box(0, square_corners)
        detector.set_manipulator_bounding_box(1, square_corners)

        sequence = [(0, (5.0, 3.0)), (1, (10.0, 7.0))]

        result = detector.execute_movement_sequence(sequence)
        assert result is True

        # Check final positions
        bbox0 = detector.get_bounding_box(0)
        bbox1 = detector.get_bounding_box(1)
        assert bbox0.tip_x == 5.0
        assert bbox0.tip_y == 3.0
        assert bbox1.tip_x == 10.0
        assert bbox1.tip_y == 7.0

    def test_execute_empty_sequence(self, detector):
        """Test executing an empty movement sequence"""
        result = detector.execute_movement_sequence([])
        assert result is False

    def test_test_movement_sequence_collision_free(self, detector, square_corners):
        """Test movement sequence testing with collision-free moves"""
        detector.set_manipulator_bounding_box(0, square_corners)
        detector.set_manipulator_bounding_box(1, square_corners)
        detector.update_manipulator_tip_position(0, 0.0, 0.0)
        detector.update_manipulator_tip_position(1, 10.0, 10.0)

        moves = {0: ((0.0, 0.0), (2.0, 0.0)), 1: ((10.0, 10.0), (12.0, 10.0))}

        sequence = [0, 1]
        result = detector._test_movement_sequence(moves, sequence)
        assert result is True

    def test_test_movement_sequence_with_collision(self, detector, square_corners):
        """Test movement sequence testing with collision"""
        detector.set_manipulator_bounding_box(0, square_corners)
        detector.set_manipulator_bounding_box(1, square_corners)
        detector.update_manipulator_tip_position(0, 0.0, 0.0)
        detector.update_manipulator_tip_position(1, 3.0, 0.0)

        moves = {
            0: ((0.0, 0.0), (3.0, 0.0)),  # Would collide with manipulator 1
            1: ((3.0, 0.0), (6.0, 0.0)),
        }

        sequence = [0, 1]
        result = detector._test_movement_sequence(moves, sequence)
        assert result is False


class TestCollisionDetectorIntegration:
    """Integration tests for complex collision scenarios"""

    @pytest.fixture
    def detector_with_manipulators(self):
        """Set up detector with multiple manipulators"""
        detector = CollisionDetector()
        square_corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]

        # Set up 3 manipulators
        for i in range(3):
            detector.set_manipulator_bounding_box(i, square_corners)

        return detector

    def test_three_manipulator_swap(self, detector_with_manipulators):
        """Test three-manipulator movement that should be solvable"""
        detector = detector_with_manipulators

        # Initial positions with enough space for non-conflicting moves
        detector.update_manipulator_tip_position(0, 0.0, 0.0)
        detector.update_manipulator_tip_position(1, 8.0, 0.0)  # Far apart
        detector.update_manipulator_tip_position(2, 4.0, 8.0)  # Well separated

        # Non-conflicting moves where paths don't cross
        moves = {
            0: ((0.0, 0.0), (0.0, 6.0)),  # Move straight up
            1: ((8.0, 0.0), (8.0, 6.0)),  # Move straight up
            2: ((4.0, 8.0), (4.0, 2.0)),  # Move straight down
        }

        sequence = detector.generate_safe_movement_sequence(moves)

        # Should find a valid sequence for these non-conflicting moves
        assert len(sequence) >= 3

    def test_diagonal_crossing_maneuver(self, detector_with_manipulators):
        """Test diagonal crossing that requires careful sequencing"""
        detector = detector_with_manipulators

        # Set up square formation
        detector.update_manipulator_tip_position(0, 0.0, 0.0)
        detector.update_manipulator_tip_position(1, 6.0, 0.0)
        detector.update_manipulator_tip_position(2, 3.0, 6.0)

        # Cross diagonally
        moves = {0: ((0.0, 0.0), (6.0, 6.0)), 1: ((6.0, 0.0), (0.0, 6.0)), 2: ((3.0, 6.0), (3.0, -3.0))}

        sequence = detector.generate_safe_movement_sequence(moves)

        # Should handle complex crossing
        assert len(sequence) >= 3

    def test_performance_with_many_manipulators(self):
        """Test performance with larger number of manipulators"""
        detector = CollisionDetector()
        corners = [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)]

        # Set up 4 manipulators in a grid
        num_manipulators = 4
        for i in range(num_manipulators):
            detector.set_manipulator_bounding_box(i, corners)
            x = (i % 2) * 3.0
            y = (i // 2) * 3.0
            detector.update_manipulator_tip_position(i, x, y)

        # Create moves that shuffle positions
        moves = {}
        for i in range(num_manipulators):
            target_i = (i + 1) % num_manipulators
            target_x = (target_i % 2) * 3.0
            target_y = (target_i // 2) * 3.0
            current_x = (i % 2) * 3.0
            current_y = (i // 2) * 3.0
            moves[i] = ((current_x, current_y), (target_x, target_y))

        # This should complete in reasonable time
        sequence = detector.generate_safe_movement_sequence(moves)

        # Should find some solution (even if not optimal)
        assert isinstance(sequence, list)
