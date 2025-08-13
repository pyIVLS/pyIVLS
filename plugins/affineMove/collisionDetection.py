import itertools
import time
from typing import List, Tuple, Dict, Optional, Any


class AABB:
    """Axis-aligned bounding box (AABB) for collision detection. Works in 2D space"""

    def __init__(self, tip_x: float, tip_y: float, relative_corners: List[Tuple[float, float]]):
        """Initialize the AABB with tip position and absolute corner coordinates in camera coordinates"""
        self.tip_x = tip_x
        self.tip_y = tip_y
        self.relative_corners = relative_corners

    def move_bbox(self, new_tip_x: float, new_tip_y: float):
        """Update the tip position of the bounding box"""
        self.tip_x = new_tip_x
        self.tip_y = new_tip_y

    def get_absolute_corners(self) -> List[Tuple[float, float]]:
        """Get the absolute corners of the AABB based on current tip position"""
        # Convert relative corners to absolute coordinates
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

    def set_bounding_box(self, manipulator_idx: int, tip_x: float, tip_y: float, relative_corners: List[Tuple[float, float]]):
        """Set the bounding box for a manipulator"""
        bounding_box = AABB(tip_x, tip_y, relative_corners)
        self.bounding_boxes[manipulator_idx] = bounding_box

    def set_manipulator_bounding_box(self, manipulator_idx: int, relative_coords: List[Tuple[float, float]]) -> bool:
        """Set the bounding box for a manipulator using relative coordinates"""
        try:
            # Use tip position as (0, 0) for now, since we're working with relative coordinates
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

    def check_trajectory_collisions(self, current_positions: Dict[int, Tuple[float, float]], 
                                  target_positions: Dict[int, Tuple[float, float]], 
                                  trajectory_steps: int = 20, debug: bool = False) -> Dict[str, Any]:
        """
        Check for collisions along movement trajectories.
        
        Args:
            current_positions: Dictionary mapping manipulator_idx to current (x, y) tip positions
            target_positions: Dictionary mapping manipulator_idx to target (x, y) tip positions  
            trajectory_steps: Number of steps to check along each trajectory
            debug: Print debug information
            
        Returns:
            Dictionary with collision analysis results:
            {
                'has_collisions': bool,
                'collision_details': List[Dict],
                'safe_order': List[int] or None,
                'trajectory_data': Dict
            }
        """
        if debug:
            print(f"Checking trajectories for {len(current_positions)} manipulators")
            print(f"Current: {current_positions}")
            print(f"Target: {target_positions}")
            
        result = {
            'has_collisions': False,
            'collision_details': [],
            'safe_order': None,
            'trajectory_data': {}
        }
        
        try:
            # Update all bounding box positions to current positions
            for manipulator_idx, (x, y) in current_positions.items():
                if manipulator_idx in self.bounding_boxes:
                    self.update_manipulator_tip_position(manipulator_idx, x, y)
            
            # Generate trajectories for each manipulator
            trajectories = self._generate_trajectories(current_positions, target_positions, trajectory_steps)
            result['trajectory_data'] = trajectories
            
            if debug:
                for manip, traj in trajectories.items():
                    print(f"Manipulator {manip}: {len(traj)} trajectory points")
            
            # Check for collisions assuming one manipulator moves at a time
            collision_matrix = self._check_sequential_movement_collisions(trajectories)
            
            # Analyze collision results
            result['has_collisions'] = any(
                any(collision_steps for collision_steps in stationary_collisions.values()) 
                for stationary_collisions in collision_matrix.values()
            )
            
            if debug and result['has_collisions']:
                print("Collisions found in matrix:")
                for moving, stationary_dict in collision_matrix.items():
                    for stationary, steps in stationary_dict.items():
                        if steps:
                            print(f"  Manipulator {moving} collides with {stationary} at steps: {steps}")
            
            result['collision_details'] = self._analyze_collision_matrix(collision_matrix, trajectories)
            
            # Try to find a safe movement order
            if result['has_collisions']:
                result['safe_order'] = self._find_safe_movement_order(collision_matrix, list(current_positions.keys()))
            else:
                # No collisions, any order is safe
                result['safe_order'] = list(current_positions.keys())
                
        except Exception as e:
            result['error'] = str(e)
            if debug:
                print(f"Error in trajectory collision check: {e}")
            
        return result

    def _generate_trajectories(self, current_positions: Dict[int, Tuple[float, float]], 
                             target_positions: Dict[int, Tuple[float, float]], 
                             steps: int) -> Dict[int, List[Tuple[float, float]]]:
        """Generate linear trajectories for each manipulator"""
        trajectories = {}
        
        for manipulator_idx in current_positions:
            if manipulator_idx not in target_positions:
                continue
                
            current_x, current_y = current_positions[manipulator_idx]
            target_x, target_y = target_positions[manipulator_idx]
            
            # Check if manipulator actually moves
            distance = ((target_x - current_x)**2 + (target_y - current_y)**2)**0.5
            if distance < 0.01:  # Essentially no movement
                # Create a single-point trajectory (stays in place)
                trajectories[manipulator_idx] = [(current_x, current_y)]
                continue
            
            # Generate linear interpolation points
            trajectory = []
            for i in range(steps + 1):
                t = i / steps  # Parameter from 0 to 1
                x = current_x + t * (target_x - current_x)
                y = current_y + t * (target_y - current_y)
                trajectory.append((x, y))
                
            trajectories[manipulator_idx] = trajectory
            
        return trajectories

    def _check_sequential_movement_collisions(self, trajectories: Dict[int, List[Tuple[float, float]]]) -> Dict[int, Dict[int, List[int]]]:
        """
        Check collisions assuming manipulators move one at a time.
        
        Returns:
            collision_matrix[moving_manipulator][stationary_manipulator] = [collision_step_indices]
        """
        collision_matrix = {}
        manipulator_indices = list(trajectories.keys())
        
        for moving_idx in manipulator_indices:
            collision_matrix[moving_idx] = {}
            
            for stationary_idx in manipulator_indices:
                if moving_idx == stationary_idx:
                    collision_matrix[moving_idx][stationary_idx] = []
                    continue
                    
                # Check collision at each step of the moving manipulator's trajectory
                collision_steps = []
                
                try:
                    if (moving_idx in self.bounding_boxes and 
                        stationary_idx in self.bounding_boxes and
                        moving_idx in trajectories and
                        stationary_idx in trajectories):
                        
                        # Stationary manipulator stays at its current position (first point of trajectory)
                        stationary_pos = trajectories[stationary_idx][0]
                        
                        # Get bounding boxes
                        moving_bbox = self.bounding_boxes[moving_idx]
                        stationary_bbox = self.bounding_boxes[stationary_idx]
                        
                        # Set stationary bbox to its current position
                        stationary_bbox.move_bbox(stationary_pos[0], stationary_pos[1])
                        
                        # Check collision at each step of the trajectory
                        for step_idx, (x, y) in enumerate(trajectories[moving_idx]):
                            # Temporarily move the moving bbox to this trajectory point
                            original_tip_x, original_tip_y = moving_bbox.tip_x, moving_bbox.tip_y
                            moving_bbox.move_bbox(x, y)
                            
                            # Check for collision
                            if moving_bbox.colliding_with(stationary_bbox):
                                collision_steps.append(step_idx)
                                
                            # Restore original position
                            moving_bbox.move_bbox(original_tip_x, original_tip_y)
                except Exception as e:
                    print(f"Error in collision check between {moving_idx} and {stationary_idx}: {e}")
                    import traceback
                    traceback.print_exc()
                
                collision_matrix[moving_idx][stationary_idx] = collision_steps
                
        return collision_matrix

    def _analyze_collision_matrix(self, collision_matrix: Dict[int, Dict[int, List[int]]], 
                                trajectories: Dict[int, List[Tuple[float, float]]]) -> List[Dict]:
        """Analyze collision matrix and generate detailed collision information"""
        collision_details = []
        
        for moving_idx, stationary_collisions in collision_matrix.items():
            for stationary_idx, collision_steps in stationary_collisions.items():
                if collision_steps:
                    detail = {
                        'moving_manipulator': moving_idx,
                        'stationary_manipulator': stationary_idx,
                        'collision_steps': collision_steps,
                        'collision_positions': []
                    }
                    
                    # Add position information for collision points
                    if moving_idx in trajectories:
                        for step in collision_steps:
                            if step < len(trajectories[moving_idx]):
                                detail['collision_positions'].append(trajectories[moving_idx][step])
                    
                    collision_details.append(detail)
                    
        return collision_details

    def _find_safe_movement_order(self, collision_matrix: Dict[int, Dict[int, List[int]]], 
                                manipulator_indices: List[int]) -> Optional[List[int]]:
        """
        Try to find a safe order to move manipulators to avoid collisions.
        This is a simplified approach - more sophisticated algorithms could be implemented.
        """
        # Create a dependency graph: if A collides with B when A moves, then A depends on B moving first
        dependencies = {}
        
        try:
            for moving_idx in manipulator_indices:
                dependencies[moving_idx] = set()
                
                for stationary_idx in manipulator_indices:
                    if (moving_idx in collision_matrix and 
                        stationary_idx in collision_matrix[moving_idx] and
                        collision_matrix[moving_idx][stationary_idx]):
                        # moving_idx collides with stationary_idx when moving_idx moves
                        # So stationary_idx should move first
                        dependencies[moving_idx].add(stationary_idx)
        except Exception as e:
            print(f"Error building dependencies: {e}")
            print(f"collision_matrix type: {type(collision_matrix)}")
            print(f"collision_matrix keys: {list(collision_matrix.keys()) if hasattr(collision_matrix, 'keys') else 'No keys method'}")
            raise e
        
        # Try to perform topological sort to find a valid order
        try:
            safe_order = self._topological_sort(dependencies)
            return safe_order
        except Exception:
            # If topological sort fails (circular dependencies), return None
            return None

    def _topological_sort(self, dependencies: Dict[int, set]) -> List[int]:
        """Perform topological sort on dependency graph"""
        # Kahn's algorithm for topological sorting
        in_degree = {node: 0 for node in dependencies}
        
        # Calculate in-degrees
        for node in dependencies:
            for dep in dependencies[node]:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        # Find nodes with no incoming edges
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # Remove this node and update in-degrees
            try:
                for dependent in dependencies[node]:
                    if dependent in in_degree:
                        in_degree[dependent] -= 1
                        if in_degree[dependent] == 0:
                            queue.append(dependent)
            except TypeError as e:
                print(f"Error iterating dependencies[{node}]: {dependencies[node]}, type: {type(dependencies[node])}")
                raise e
        
        # Check if all nodes were processed (no cycles)
        if len(result) != len(dependencies):
            raise ValueError("Circular dependency detected")
            
        return result
