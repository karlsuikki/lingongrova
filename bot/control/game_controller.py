import asyncio
import time
import os
from typing import Optional, Tuple
from playwright.async_api import async_playwright, Page, Browser
import cv2
import numpy as np

from ..detection.game_detector import GameDetector, GameState
from ..aiming.aiming_system import AimingSystem


class GameController:
    """Controls the web browser and coordinates bot actions."""
    
    def __init__(self, headless: bool = False, debug: bool = True):
        self.headless = headless
        self.debug = debug
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.game_detector = GameDetector()
        self.aiming_system = AimingSystem()
        self.screenshot_dir = "screenshots"
        
        # Create screenshot directory
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Game timing
        self.shot_cooldown = 2.0  # Seconds between shots
        self.last_shot_time = 0
        
    async def start_browser(self):
        """Start the browser and navigate to the game."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        self.page = await self.browser.new_page()
        
        # Set viewport size
        await self.page.set_viewport_size({"width": 1280, "height": 720})
        
    async def navigate_to_game(self, url: str):
        """Navigate to the game URL."""
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
            
        print(f"Navigating to game: {url}")
        await self.page.goto(url, wait_until="networkidle")
        
        # Wait a bit for the game to load
        await asyncio.sleep(3)
        
    async def take_screenshot(self) -> np.ndarray:
        """Take a screenshot and return as numpy array."""
        if not self.page:
            raise RuntimeError("Browser not started.")
            
        screenshot_bytes = await self.page.screenshot()
        
        # Convert to numpy array
        nparr = np.frombuffer(screenshot_bytes, np.uint8)
        screenshot = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        return screenshot
    
    async def click_at_position(self, x: int, y: int):
        """Click at the specified position."""
        if not self.page:
            raise RuntimeError("Browser not started.")
            
        await self.page.mouse.click(x, y)
        print(f"Clicked at position ({x}, {y})")
        
    async def aim_and_shoot(self, target_pos: Tuple[int, int], shooter_pos: Tuple[int, int]):
        """Aim at target position and shoot."""
        if not self.page:
            raise RuntimeError("Browser not started.")
            
        # Move mouse to aiming position
        await self.page.mouse.move(target_pos[0], target_pos[1])
        await asyncio.sleep(0.1)  # Brief pause for aiming
        
        # Click to shoot
        await self.page.mouse.click(target_pos[0], target_pos[1])
        print(f"Shot from {shooter_pos} towards {target_pos}")
        
        self.last_shot_time = time.time()
        
    async def wait_for_shot_cooldown(self):
        """Wait for the shot cooldown period."""
        time_since_shot = time.time() - self.last_shot_time
        if time_since_shot < self.shot_cooldown:
            wait_time = self.shot_cooldown - time_since_shot
            print(f"Waiting {wait_time:.1f}s for shot cooldown...")
            await asyncio.sleep(wait_time)
    
    async def play_game_loop(self, max_rounds: int = 50):
        """Main game loop."""
        print("Starting game loop...")
        
        round_count = 0
        consecutive_no_shots = 0
        
        while round_count < max_rounds:
            try:
                round_count += 1
                print(f"\n=== Round {round_count} ===")
                
                # Take screenshot and analyze game state
                screenshot = await self.take_screenshot()
                game_state = self.game_detector.detect_game_state(screenshot)
                
                if not game_state:
                    print("Could not detect game state, waiting...")
                    await asyncio.sleep(1)
                    consecutive_no_shots += 1
                    if consecutive_no_shots > 10:
                        print("Too many failed detections, stopping...")
                        break
                    continue
                
                print(f"Detected {len(game_state.bubbles)} bubbles")
                
                # Save debug screenshot if enabled
                if self.debug:
                    debug_filename = os.path.join(
                        self.screenshot_dir, f"round_{round_count:03d}_debug.jpg"
                    )
                    self.game_detector.save_debug_image(screenshot, game_state, debug_filename)
                
                # Check if game is over (no bubbles left)
                if not game_state.bubbles:
                    print("No bubbles detected - game might be complete!")
                    break
                
                # Calculate best shot
                best_shot = self.aiming_system.calculate_best_shot(game_state)
                
                if not best_shot:
                    print("No good shot found, waiting for bubbles to settle...")
                    await asyncio.sleep(2)
                    consecutive_no_shots += 1
                    if consecutive_no_shots > 5:
                        print("Too many rounds without shots, stopping...")
                        break
                    continue
                
                consecutive_no_shots = 0
                angle, target_bubble = best_shot
                
                print(f"Targeting bubble at ({target_bubble.x}, {target_bubble.y}) "
                      f"with hit count {target_bubble.hit_count}")
                
                # Convert angle to mouse position
                mouse_pos = self.aiming_system.get_mouse_position_for_angle(
                    game_state.shooter_position, angle, distance=200
                )
                
                # Wait for cooldown
                await self.wait_for_shot_cooldown()
                
                # Aim and shoot
                await self.aim_and_shoot(mouse_pos, game_state.shooter_position)
                
                # Wait for bullet to travel and bubbles to settle
                await asyncio.sleep(3)
                
                # Check for any dialogs or popups that might need to be closed
                await self._handle_popups()
                
            except Exception as e:
                print(f"Error in game loop: {e}")
                await asyncio.sleep(2)
                
        print(f"Game loop completed after {round_count} rounds")
    
    async def _handle_popups(self):
        """Handle any popups or dialogs that might appear."""
        try:
            # Look for common popup elements and close them
            close_buttons = await self.page.query_selector_all(
                'button:has-text("Close"), button:has-text("OK"), button:has-text("Continue"), .close-button'
            )
            
            for button in close_buttons:
                if await button.is_visible():
                    await button.click()
                    print("Closed popup")
                    await asyncio.sleep(0.5)
                    
        except Exception as e:
            print(f"Error handling popups: {e}")
    
    async def find_and_start_game(self):
        """Look for game start button and click it."""
        if not self.page:
            raise RuntimeError("Browser not started.")
            
        try:
            # Common game start button selectors
            start_selectors = [
                'button:has-text("Start")',
                'button:has-text("Play")', 
                'button:has-text("Begin")',
                '.start-button',
                '.play-button',
                '#start-game',
                '#play-game'
            ]
            
            for selector in start_selectors:
                try:
                    button = await self.page.wait_for_selector(selector, timeout=2000)
                    if button and await button.is_visible():
                        await button.click()
                        print(f"Clicked start button: {selector}")
                        await asyncio.sleep(2)
                        return True
                except:
                    continue
                    
            print("No start button found, assuming game is already active")
            return True
            
        except Exception as e:
            print(f"Error finding start button: {e}")
            return False
    
    async def close(self):
        """Clean up browser resources."""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        print("Browser closed")