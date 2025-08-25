#!/usr/bin/env python3
"""
Test script for the Lingongrova Bot
"""

import asyncio
import os
import sys
import numpy as np
import cv2
from bot.detection.game_detector import GameDetector, Bubble, GameState
from bot.aiming.aiming_system import AimingSystem
from bot.control.game_controller import GameController


def test_detection():
    """Test game detection functionality."""
    print("Testing game detection...")
    
    # Create a simple test image
    test_image = np.zeros((600, 800, 3), dtype=np.uint8)
    
    # Draw some red circles (mock bubbles)
    cv2.circle(test_image, (200, 150), 25, (0, 0, 255), -1)  # Red bubble
    cv2.circle(test_image, (300, 200), 20, (0, 0, 255), -1)  # Red bubble
    cv2.circle(test_image, (400, 100), 30, (0, 0, 255), -1)  # Red bubble
    
    # Add some text numbers (mock hit counts)
    cv2.putText(test_image, "2", (195, 155), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(test_image, "1", (295, 205), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(test_image, "3", (395, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    detector = GameDetector()
    game_state = detector.detect_game_state(test_image)
    
    if game_state:
        print(f"✓ Detected {len(game_state.bubbles)} bubbles")
        for i, bubble in enumerate(game_state.bubbles):
            print(f"  Bubble {i+1}: pos=({bubble.x}, {bubble.y}), hits={bubble.hit_count}")
        
        # Save debug image
        os.makedirs("test_output", exist_ok=True)
        detector.save_debug_image(test_image, game_state, "test_output/detection_test.jpg")
        print("✓ Debug image saved to test_output/detection_test.jpg")
    else:
        print("✗ Game detection failed")
        return False
    
    return True


def test_aiming():
    """Test aiming system functionality."""
    print("\nTesting aiming system...")
    
    # Create mock game state
    bubbles = [
        Bubble(x=200, y=150, radius=25, hit_count=2, color=(255, 0, 0)),
        Bubble(x=300, y=200, radius=20, hit_count=1, color=(255, 0, 0)),
        Bubble(x=400, y=100, radius=30, hit_count=3, color=(255, 0, 0)),
    ]
    
    game_state = GameState(
        bubbles=bubbles,
        shooter_position=(400, 500),
        bullets=[],
        game_area=(0, 0, 800, 600)
    )
    
    aiming_system = AimingSystem()
    best_shot = aiming_system.calculate_best_shot(game_state)
    
    if best_shot:
        angle, target = best_shot
        mouse_pos = aiming_system.get_mouse_position_for_angle(
            game_state.shooter_position, angle, distance=100
        )
        
        print(f"✓ Best shot calculated:")
        print(f"  Target: ({target.x}, {target.y}) with {target.hit_count} hits")
        print(f"  Angle: {angle:.2f} radians ({angle * 180 / 3.14159:.1f} degrees)")
        print(f"  Mouse position: ({mouse_pos[0]}, {mouse_pos[1]})")
    else:
        print("✗ Aiming calculation failed")
        return False
    
    return True


async def test_browser():
    """Test browser automation."""
    print("\nTesting browser automation...")
    
    try:
        controller = GameController(headless=True, debug=False)
        await controller.start_browser()
        
        # Navigate to a simple test page
        await controller.page.goto("data:text/html,<h1>Test Page</h1>")
        
        # Take a screenshot
        screenshot = await controller.take_screenshot()
        
        if screenshot is not None and screenshot.size > 0:
            print("✓ Browser automation working")
            print(f"  Screenshot size: {screenshot.shape}")
        else:
            print("✗ Screenshot failed")
            return False
            
        await controller.close()
        
    except Exception as e:
        print(f"✗ Browser test failed: {e}")
        return False
    
    return True


async def main():
    """Run all tests."""
    print("Running Lingongrova Bot Tests\n" + "="*40)
    
    tests_passed = 0
    total_tests = 3
    
    # Test detection
    if test_detection():
        tests_passed += 1
    
    # Test aiming
    if test_aiming():
        tests_passed += 1
    
    # Test browser
    if await test_browser():
        tests_passed += 1
    
    print(f"\n" + "="*40)
    print(f"Tests completed: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("✓ All tests passed! Bot is ready to use.")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)