import numpy as np
import math
from typing import Tuple, List, Optional
from ..detection.game_detector import Bubble, GameState


class AimingSystem:
    """Calculates optimal shooting angles for bubble shooter game."""
    
    def __init__(self):
        self.gravity = 9.81  # Gravity acceleration
        self.bullet_speed = 500  # Initial bullet speed (pixels/second)
        self.bounce_damping = 0.8  # Energy loss on wall bounces
        self.max_bounces = 3  # Maximum number of wall bounces to consider
        
    def calculate_best_shot(self, game_state: GameState) -> Optional[Tuple[float, Bubble]]:
        """
        Calculate the best shooting angle to hit bubbles efficiently.
        
        Args:
            game_state: Current game state
            
        Returns:
            Tuple of (angle_in_radians, target_bubble) or None if no good shot
        """
        if not game_state.bubbles:
            return None
            
        best_shot = None
        best_score = -1
        
        # Sort bubbles by priority (lowest hit count and highest position first)
        sorted_bubbles = sorted(
            game_state.bubbles,
            key=lambda b: (b.hit_count, -b.y)  # Prioritize low hit count and high position
        )
        
        for bubble in sorted_bubbles:
            # Try direct shots first
            angle = self._calculate_direct_shot(game_state.shooter_position, bubble)
            if angle is not None:
                score = self._evaluate_shot(bubble, game_state.bubbles, direct=True)
                if score > best_score:
                    best_score = score
                    best_shot = (angle, bubble)
            
            # Try bounced shots if direct shot isn't available or isn't optimal
            bounced_shots = self._calculate_bounced_shots(game_state, bubble)
            for angle, _ in bounced_shots:
                score = self._evaluate_shot(bubble, game_state.bubbles, direct=False)
                if score > best_score:
                    best_score = score
                    best_shot = (angle, bubble)
        
        return best_shot
    
    def _calculate_direct_shot(self, shooter_pos: Tuple[int, int], target: Bubble) -> Optional[float]:
        """Calculate angle for a direct shot to target bubble."""
        sx, sy = shooter_pos
        tx, ty = target.x, target.y
        
        # Calculate vector from shooter to target
        dx = tx - sx
        dy = ty - sy
        
        # Check if target is above shooter (we can only shoot upward)
        if dy >= 0:
            return None
            
        # Calculate angle (0 = straight up, positive = right, negative = left)
        angle = math.atan2(dx, -dy)
        
        # Ensure angle is within reasonable shooting range (-π/2 to π/2)
        if abs(angle) > math.pi / 2:
            return None
            
        return angle
    
    def _calculate_bounced_shots(self, game_state: GameState, target: Bubble) -> List[Tuple[float, int]]:
        """Calculate possible bounced shots to reach target."""
        bounced_shots = []
        game_area = game_state.game_area
        x_min, y_min, width, height = game_area
        x_max = x_min + width
        y_max = y_min + height
        
        # Try different angles and simulate trajectory
        for angle_deg in range(-80, 81, 5):  # -80 to 80 degrees in 5-degree steps
            angle = math.radians(angle_deg)
            trajectory = self._simulate_trajectory(
                game_state.shooter_position, angle, game_area, target
            )
            
            if trajectory and self._trajectory_hits_target(trajectory, target):
                bounced_shots.append((angle, len(trajectory)))
        
        return bounced_shots
    
    def _simulate_trajectory(self, start_pos: Tuple[int, int], angle: float, 
                           game_area: Tuple[int, int, int, int], target: Bubble) -> Optional[List[Tuple[int, int]]]:
        """Simulate bullet trajectory with physics and bounces."""
        x, y = start_pos
        x_min, y_min, width, height = game_area
        x_max = x_min + width
        y_max = y_min + height
        
        # Initial velocity components
        vx = self.bullet_speed * math.sin(angle)
        vy = -self.bullet_speed * math.cos(angle)  # Negative because y increases downward
        
        trajectory = [(int(x), int(y))]
        dt = 0.016  # 60 FPS simulation
        bounces = 0
        
        while bounces <= self.max_bounces and y > y_min:
            # Update position
            x += vx * dt
            y += vy * dt
            vy += self.gravity * dt  # Apply gravity
            
            # Check for wall bounces
            if x <= x_min or x >= x_max:
                vx = -vx * self.bounce_damping
                x = max(x_min, min(x_max, x))
                bounces += 1
            
            # Check if bullet has fallen below game area
            if y >= y_max:
                break
                
            trajectory.append((int(x), int(y)))
            
            # Stop if we're close to target
            if abs(x - target.x) < target.radius and abs(y - target.y) < target.radius:
                break
                
            # Prevent infinite loops
            if len(trajectory) > 1000:
                break
        
        return trajectory if len(trajectory) > 1 else None
    
    def _trajectory_hits_target(self, trajectory: List[Tuple[int, int]], target: Bubble) -> bool:
        """Check if trajectory passes close enough to hit target bubble."""
        for x, y in trajectory:
            distance = math.sqrt((x - target.x)**2 + (y - target.y)**2)
            if distance <= target.radius:
                return True
        return False
    
    def _evaluate_shot(self, target: Bubble, all_bubbles: List[Bubble], direct: bool = True) -> float:
        """
        Evaluate the quality of a shot based on various factors.
        
        Args:
            target: The bubble being targeted
            all_bubbles: All bubbles in the game
            direct: Whether this is a direct shot (vs bounced)
            
        Returns:
            Score (higher is better)
        """
        score = 0
        
        # Prioritize bubbles with low hit counts (easier to eliminate)
        score += (10 - target.hit_count) * 10
        
        # Prioritize bubbles that are higher up (more threatening)
        max_y = max(bubble.y for bubble in all_bubbles) if all_bubbles else target.y
        height_factor = (max_y - target.y) / max_y if max_y > 0 else 0
        score += height_factor * 20
        
        # Bonus for direct shots (more reliable)
        if direct:
            score += 15
        
        # Check for potential chain reactions (bubbles that might fall)
        chain_bonus = self._calculate_chain_potential(target, all_bubbles)
        score += chain_bonus * 5
        
        return score
    
    def _calculate_chain_potential(self, target: Bubble, all_bubbles: List[Bubble]) -> int:
        """Calculate potential for chain reactions when hitting target bubble."""
        # Simplified chain calculation - in practice, this would be more complex
        chain_count = 0
        
        # Look for bubbles near the target that might be affected
        for bubble in all_bubbles:
            if bubble != target:
                distance = math.sqrt((bubble.x - target.x)**2 + (bubble.y - target.y)**2)
                # If bubbles are close, they might form a chain
                if distance < (target.radius + bubble.radius) * 1.5:
                    chain_count += 1
        
        return chain_count
    
    def get_mouse_position_for_angle(self, shooter_pos: Tuple[int, int], 
                                   angle: float, distance: int = 100) -> Tuple[int, int]:
        """
        Convert shooting angle to mouse position for aiming.
        
        Args:
            shooter_pos: Position of the shooter
            angle: Shooting angle in radians
            distance: Distance from shooter to place mouse cursor
            
        Returns:
            Mouse position (x, y)
        """
        sx, sy = shooter_pos
        
        # Calculate target position based on angle
        target_x = sx + distance * math.sin(angle)
        target_y = sy - distance * math.cos(angle)  # Negative because y increases downward
        
        return (int(target_x), int(target_y))