import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class Bubble:
    """Represents a bubble in the game."""
    x: int
    y: int
    radius: int
    hit_count: int
    color: Tuple[int, int, int]


@dataclass
class GameState:
    """Represents the current state of the game."""
    bubbles: List[Bubble]
    shooter_position: Tuple[int, int]
    bullets: List[Tuple[int, int]]
    game_area: Tuple[int, int, int, int]  # x, y, width, height


class GameDetector:
    """Detects game elements using computer vision."""
    
    def __init__(self):
        self.bubble_color_range = {
            'red_lower': np.array([0, 50, 50]),
            'red_upper': np.array([10, 255, 255])
        }
        self.min_bubble_radius = 15
        self.max_bubble_radius = 40
        
    def detect_game_state(self, screenshot: np.ndarray) -> Optional[GameState]:
        """
        Analyze screenshot and return current game state.
        
        Args:
            screenshot: Screenshot as numpy array
            
        Returns:
            GameState object or None if game not detected
        """
        try:
            # Find game area first
            game_area = self._find_game_area(screenshot)
            if not game_area:
                return None
                
            # Extract game region
            x, y, w, h = game_area
            game_region = screenshot[y:y+h, x:x+w]
            
            # Detect bubbles
            bubbles = self._detect_bubbles(game_region, x, y)
            
            # Detect shooter position
            shooter_pos = self._detect_shooter(game_region, x, y)
            
            # Detect bullets (if any)
            bullets = self._detect_bullets(game_region, x, y)
            
            return GameState(
                bubbles=bubbles,
                shooter_position=shooter_pos,
                bullets=bullets,
                game_area=game_area
            )
            
        except Exception as e:
            print(f"Error detecting game state: {e}")
            return None
    
    def _find_game_area(self, screenshot: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Find the game playing area in the screenshot."""
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Use edge detection to find game boundaries
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            # Fallback: use center portion of screen
            h, w = screenshot.shape[:2]
            return (w//4, h//4, w//2, h//2)
        
        # Find the largest rectangular contour (likely the game area)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Ensure minimum size
        if w < 200 or h < 300:
            h, w = screenshot.shape[:2]
            return (w//4, h//4, w//2, h//2)
            
        return (x, y, w, h)
    
    def _detect_bubbles(self, game_region: np.ndarray, offset_x: int, offset_y: int) -> List[Bubble]:
        """Detect red bubbles in the game region."""
        bubbles = []
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(game_region, cv2.COLOR_BGR2HSV)
        
        # Create mask for red color
        mask = cv2.inRange(hsv, self.bubble_color_range['red_lower'], 
                          self.bubble_color_range['red_upper'])
        
        # Find contours of red objects
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Calculate contour properties
            area = cv2.contourArea(contour)
            if area < 100:  # Too small to be a bubble
                continue
                
            # Get bounding circle
            (x, y), radius = cv2.minEnclosingCircle(contour)
            
            if self.min_bubble_radius <= radius <= self.max_bubble_radius:
                # Try to detect hit count (this would need OCR or template matching)
                hit_count = self._detect_hit_count(game_region, int(x), int(y), int(radius))
                
                # Get average color
                mask_bubble = np.zeros(game_region.shape[:2], dtype=np.uint8)
                cv2.circle(mask_bubble, (int(x), int(y)), int(radius), 255, -1)
                color = cv2.mean(game_region, mask_bubble)[:3]
                
                bubble = Bubble(
                    x=int(x) + offset_x,
                    y=int(y) + offset_y,
                    radius=int(radius),
                    hit_count=hit_count,
                    color=tuple(map(int, color))
                )
                bubbles.append(bubble)
                
        return bubbles
    
    def _detect_hit_count(self, game_region: np.ndarray, x: int, y: int, radius: int) -> int:
        """
        Detect the hit count number on a bubble.
        This is a simplified version - in practice, you'd use OCR or template matching.
        """
        # Extract the center area of the bubble
        center_size = radius // 2
        x1, y1 = max(0, x - center_size), max(0, y - center_size)
        x2, y2 = min(game_region.shape[1], x + center_size), min(game_region.shape[0], y + center_size)
        
        bubble_center = game_region[y1:y2, x1:x2]
        
        if bubble_center.size == 0:
            return 1
            
        # Convert to grayscale and apply threshold
        gray = cv2.cvtColor(bubble_center, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Count white pixels as a rough estimate of number complexity
        white_pixels = np.sum(thresh == 255)
        total_pixels = thresh.size
        
        if total_pixels == 0:
            return 1
            
        white_ratio = white_pixels / total_pixels
        
        # Simple heuristic based on white pixel ratio
        if white_ratio < 0.1:
            return 1
        elif white_ratio < 0.2:
            return 2
        elif white_ratio < 0.3:
            return 3
        else:
            return max(1, min(9, int(white_ratio * 10)))
    
    def _detect_shooter(self, game_region: np.ndarray, offset_x: int, offset_y: int) -> Tuple[int, int]:
        """Detect the shooter position (usually at the bottom center)."""
        h, w = game_region.shape[:2]
        
        # Look for the shooter in the bottom portion
        bottom_region = game_region[int(h * 0.8):, :]
        
        # For now, assume shooter is at bottom center
        shooter_x = w // 2 + offset_x
        shooter_y = h - 50 + offset_y
        
        return (shooter_x, shooter_y)
    
    def _detect_bullets(self, game_region: np.ndarray, offset_x: int, offset_y: int) -> List[Tuple[int, int]]:
        """Detect bullets in flight."""
        bullets = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(game_region, cv2.COLOR_BGR2GRAY)
        
        # Look for small bright circles (bullets)
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, 1, 20,
            param1=50, param2=30, minRadius=3, maxRadius=10
        )
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                bullets.append((x + offset_x, y + offset_y))
                
        return bullets

    def save_debug_image(self, screenshot: np.ndarray, game_state: GameState, filename: str):
        """Save screenshot with detected elements marked for debugging."""
        debug_img = screenshot.copy()
        
        if game_state:
            # Draw game area
            x, y, w, h = game_state.game_area
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (255, 255, 0), 2)
            
            # Draw bubbles
            for bubble in game_state.bubbles:
                cv2.circle(debug_img, (bubble.x, bubble.y), bubble.radius, (0, 255, 0), 2)
                cv2.putText(debug_img, str(bubble.hit_count), 
                           (bubble.x - 10, bubble.y + 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Draw shooter
            cv2.circle(debug_img, game_state.shooter_position, 10, (0, 0, 255), -1)
            
            # Draw bullets
            for bullet_pos in game_state.bullets:
                cv2.circle(debug_img, bullet_pos, 5, (255, 0, 255), -1)
        
        cv2.imwrite(filename, debug_img)