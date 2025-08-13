import itertools
from typing import List, Tuple, Dict, Optional


class AABB:
    """Axis-aligned bounding box (AABB) for collision detection. Works in 2D space"""

    def __init__(self, tip_x: float, tip_y: float, relative_corners: List[Tuple[float, float]]):
        """Initialize the AABB with tip position and relative corner coordinates"""
        self.tip_x = tip_x
        self.tip_y = tip_y
        self.relative_corners = relative_corners

    def move_bbox(self, new_tip_x: float, new_tip_y: float):
        """Update the tip position of the bounding box"""
        self.tip_x = new_tip_x
        self.tip_y = new_tip_y

    def get_absolute_corners(self) -> List[Tuple[float, float]]:
        """Get the absolute corners of the AABB based on current tip position"""
        absolute_corners = []
        for rel_x, rel_y in self.relative_corners:
            abs_x = self.tip_x + rel_x
            abs_y = self.tip_y + rel_y
            absolute_corners.append((abs_x, abs_y))
        return absolute_corners

    def colliding_with(self, other: "AABB") -> bool:
        """Check if this AABB intersects with another AABB using absolute coordinates"""
        # Get absolute corners for both bounding boxes
        self_abs = self.get_absolute_corners()
        other_abs = other.get_absolute_corners()
        
        # Extract min/max coordinates from all corners
        self_x_coords = [corner[0] for corner in self_abs]
        self_y_coords = [corner[1] for corner in self_abs]
        other_x_coords = [corner[0] for corner in other_abs]
        other_y_coords = [corner[1] for corner in other_abs]
        
        self_min_x, self_max_x = min(self_x_coords), max(self_x_coords)
        self_min_y, self_max_y = min(self_y_coords), max(self_y_coords)
        other_min_x, other_max_x = min(other_x_coords), max(other_x_coords)
        other_min_y, other_max_y = min(other_y_coords), max(other_y_coords)
        
        # Check for overlap using the standard AABB collision detection algorithm
        return not (self_max_x < other_min_x or self_min_x > other_max_x or 
                   self_max_y < other_min_y or self_min_y > other_max_y)

    def __str__(self) -> str:
        return f"AABB({self.tip_x:.1f}, {self.tip_y:.1f})"


class CollisionDetector:
    """collision detector for single manipulator movements using bounding boxes"""

    def __init__(self):
        self.bounding_boxes: Dict[int, AABB] = {}

    def set_manipulator_bounding_box(self, manipulator_idx: int, relative_coords: List[Tuple[float, float]]) -> bool:
        """Set the bounding box for a manipulator using relative coordinates"""
        try:
            bounding_box = AABB(0.0, 0.0, relative_coords)
            self.bounding_boxes[manipulator_idx] = bounding_box
            return True
        except Exception:
            return False

    def get_bounding_box(self, manipulator_idx: int) -> Optional[AABB]:
        """Get the bounding box for a manipulator"""
        return self.bounding_boxes.get(manipulator_idx)

    def clear_manipulator_bounding_box(self, manipulator_idx: int) -> bool:
        """Clear the bounding box for a manipulator. Returns True if box existed and was removed."""
        if manipulator_idx in self.bounding_boxes:
            del self.bounding_boxes[manipulator_idx]
            return True
        return False

    def get_manipulator_indices(self) -> List[int]:
        """Get all manipulator indices that have bounding boxes"""
        return list(self.bounding_boxes.keys())

    def update_manipulator_tip_position(self, manipulator_idx: int, tip_x: float, tip_y: float) -> bool:
        """Update the tip position for a manipulator's bounding box"""
        if manipulator_idx in self.bounding_boxes:
            self.bounding_boxes[manipulator_idx].move_bbox(tip_x, tip_y)
            return True
        return False

    def get_all_bounding_boxes(self) -> Dict[int, AABB]:
        """Get all bounding boxes"""
        return self.bounding_boxes.copy()

    def check_move_collision(self, moves: Dict[int, Tuple[Tuple[float, float], Tuple[float, float]]], 
                           trajectory_steps: int = 20) -> bool:
        """
        Check if a single manipulator movement would cause collisions.
        
        Args:
            moves: Dict mapping manipulator_idx to ((current_x, current_y), (target_x, target_y))
            trajectory_steps: Number of steps to check along the trajectory
            
        Returns:
            bool: True if collision detected, False if safe to move
        """
        if len(moves) != 1:
            raise ValueError("Only single manipulator movements are supported")
        
        moving_idx, ((current_x, current_y), (target_x, target_y)) = next(iter(moves.items()))
        
        # Check if we have a bounding box for the moving manipulator
        if moving_idx not in self.bounding_boxes:
            return False  # No bounding box means no collision possible
        
        moving_bbox = self.bounding_boxes[moving_idx]
        
        # Generate trajectory for the moving manipulator
        trajectory = self._generate_linear_trajectory(
            (current_x, current_y), (target_x, target_y), trajectory_steps
        )
        
        # Check collision with all other manipulators at each step
        for step_pos in trajectory:
            # Move the moving manipulator's bounding box to this trajectory step
            orig_x, orig_y = moving_bbox.tip_x, moving_bbox.tip_y
            moving_bbox.move_bbox(step_pos[0], step_pos[1])
            
            # Check collision with all other manipulators at their current positions
            for other_idx, other_bbox in self.bounding_boxes.items():
                if other_idx == moving_idx:
                    continue
                    
                if moving_bbox.colliding_with(other_bbox):
                    # Restore original position and return collision detected
                    moving_bbox.move_bbox(orig_x, orig_y)
                    return True
            
            # Restore original position for next iteration
            moving_bbox.move_bbox(orig_x, orig_y)
        
        return False  # No collision detected

    def generate_safe_movement_sequence(self, moves: Dict[int, Tuple[Tuple[float, float], Tuple[float, float]]]) -> List[Tuple[int, Tuple[float, float]]]:
        """
        Generate a safe movement sequence to avoid collisions.
        
        Args:
            moves: Dict mapping manipulator_idx to ((current_x, current_y), (target_x, target_y))
            
        Returns:
            List of tuples (manipulator_idx, target_position) where target_position is (x, y).
            This format works for both full moves and segmented moves.
            Empty list if no safe sequence exists.
        """
        if not moves:
            return []
        
        # Update all manipulator positions to their current positions
        for manip_idx, ((current_x, current_y), _) in moves.items():
            if manip_idx in self.bounding_boxes:
                self.bounding_boxes[manip_idx].move_bbox(current_x, current_y)
        
        # First try full moves in all permutations
        manipulator_indices = list(moves.keys())
        
        for permutation in itertools.permutations(manipulator_indices):
            if self._test_movement_sequence(moves, list(permutation)):
                # Return full moves as sequence
                return [(idx, moves[idx][1]) for idx in permutation]
        
        # If no safe sequence found with full moves, try breaking moves into X and Y components
        print("No safe sequence found with full moves, trying segmented moves...")
        return self._generate_segmented_movement_sequence(moves)

    def _test_movement_sequence(self, moves: Dict[int, Tuple[Tuple[float, float], Tuple[float, float]]], 
                              sequence: List[int]) -> bool:
        """Test if a movement sequence is collision-free"""
        # Store original positions
        original_positions = {}
        for manip_idx in self.bounding_boxes:
            bbox = self.bounding_boxes[manip_idx]
            original_positions[manip_idx] = (bbox.tip_x, bbox.tip_y)
        
        try:
            # Test each move in sequence
            for manip_idx in sequence:
                if manip_idx not in moves:
                    continue
                    
                (current_x, current_y), (target_x, target_y) = moves[manip_idx]
                
                # Test if this single move causes collision
                single_move = {manip_idx: ((current_x, current_y), (target_x, target_y))}
                if self.check_move_collision(single_move):
                    return False
                
                # Update position for next iteration
                if manip_idx in self.bounding_boxes:
                    self.bounding_boxes[manip_idx].move_bbox(target_x, target_y)
            
            return True
            
        finally:
            # Restore original positions
            for manip_idx, (orig_x, orig_y) in original_positions.items():
                if manip_idx in self.bounding_boxes:
                    self.bounding_boxes[manip_idx].move_bbox(orig_x, orig_y)

    def _generate_linear_trajectory(self, start: Tuple[float, float], end: Tuple[float, float], 
                                  steps: int) -> List[Tuple[float, float]]:
        """Generate linear trajectory between two points"""
        start_x, start_y = start
        end_x, end_y = end
        
        # Check if there's actual movement
        distance = ((end_x - start_x)**2 + (end_y - start_y)**2)**0.5
        if distance < 0.01:  # Essentially no movement
            return [start]
        
        # Generate linear interpolation points
        trajectory = []
        for i in range(steps + 1):
            t = i / steps  # Parameter from 0 to 1
            x = start_x + t * (end_x - start_x)
            y = start_y + t * (end_y - start_y)
            trajectory.append((x, y))
            
        return trajectory

    def _generate_segmented_movement_sequence(self, moves: Dict[int, Tuple[Tuple[float, float], Tuple[float, float]]]) -> List[Tuple[int, Tuple[float, float]]]:
        """
        Generate a safe movement sequence by breaking moves into X and Y components.
        
        Args:
            moves: Dict mapping manipulator_idx to ((current_x, current_y), (target_x, target_y))
            
        Returns:
            List of tuples (manipulator_idx, target_position) representing the sequence of moves.
            Empty list if no safe sequence exists even with segmentation.
        """
        # Create segmented moves (X and Y components)
        segmented_moves = self._create_segmented_moves(moves)
        print(f"Created {len(segmented_moves)} segmented moves:")
        print("Segmented moves:", segmented_moves)
        # Try all permutations of segmented moves
        move_keys = list(segmented_moves.keys())
        
        for permutation in itertools.permutations(move_keys):
            if self._test_segmented_movement_sequence(segmented_moves, list(permutation)):
                # Convert segmented moves to (manipulator_idx, target_position) format
                sequence = []
                for move_key in permutation:
                    manip_idx, move_type = move_key
                    (_, _), (target_x, target_y) = segmented_moves[move_key]
                    sequence.append((manip_idx, (target_x, target_y)))
                return sequence
        
        return []  # No safe sequence found even with segmentation

    def _create_segmented_moves(self, moves: Dict[int, Tuple[Tuple[float, float], Tuple[float, float]]]) -> Dict[Tuple[int, str], Tuple[Tuple[float, float], Tuple[float, float]]]:
        """
        Break down moves into X and Y components.
        
        Args:
            moves: Original moves dict
            
        Returns:
            Dict mapping (manipulator_idx, move_type) to move coordinates
        """
        segmented_moves = {}
        
        for manip_idx, ((current_x, current_y), (target_x, target_y)) in moves.items():
            # Only create segments if there's actual movement in that dimension
            if abs(target_x - current_x) > 0.01:  # X movement
                segmented_moves[(manip_idx, 'x')] = ((current_x, current_y), (target_x, current_y))
            
            if abs(target_y - current_y) > 0.01:  # Y movement
                # For Y movement, start from the X-moved position if X movement exists
                start_x = target_x if abs(target_x - current_x) > 0.01 else current_x
                segmented_moves[(manip_idx, 'y')] = ((start_x, current_y), (target_x, target_y))
        
        return segmented_moves

    def _test_segmented_movement_sequence(self, segmented_moves: Dict[Tuple[int, str], Tuple[Tuple[float, float], Tuple[float, float]]], 
                                        sequence: List[Tuple[int, str]]) -> bool:
        """
        Test if a segmented movement sequence is collision-free.
        
        Args:
            segmented_moves: Dict mapping (manipulator_idx, move_type) to move coordinates
            sequence: List of (manipulator_idx, move_type) tuples in execution order
            
        Returns:
            bool: True if sequence is safe, False if collision detected
        """
        # Store original positions
        original_positions = {}
        for manip_idx in self.bounding_boxes:
            bbox = self.bounding_boxes[manip_idx]
            original_positions[manip_idx] = (bbox.tip_x, bbox.tip_y)
        
        try:
            # Test each segmented move in sequence
            for move_key in sequence:
                if move_key not in segmented_moves:
                    continue
                    
                manip_idx, move_type = move_key
                (current_x, current_y), (target_x, target_y) = segmented_moves[move_key]
                
                # Test if this single segmented move causes collision
                single_move = {manip_idx: ((current_x, current_y), (target_x, target_y))}
                if self.check_move_collision(single_move):
                    return False
                
                # Update position for next iteration
                if manip_idx in self.bounding_boxes:
                    self.bounding_boxes[manip_idx].move_bbox(target_x, target_y)
            
            return True
            
        finally:
            # Restore original positions
            for manip_idx, (orig_x, orig_y) in original_positions.items():
                if manip_idx in self.bounding_boxes:
                    self.bounding_boxes[manip_idx].move_bbox(orig_x, orig_y)

    def execute_movement_sequence(self, sequence: List[Tuple[int, Tuple[float, float]]]) -> bool:
        """
        Execute a movement sequence generated by generate_safe_movement_sequence.
        
        Args:
            sequence: Sequence returned by generate_safe_movement_sequence in format
                     [(manipulator_idx, target_position), ...]
            
        Returns:
            bool: True if all moves executed successfully, False otherwise
        """
        if not sequence:
            return False
            
        # Execute each move in the sequence
        for manip_idx, (target_x, target_y) in sequence:
            if manip_idx in self.bounding_boxes:
                self.bounding_boxes[manip_idx].move_bbox(target_x, target_y)
        
        return True

