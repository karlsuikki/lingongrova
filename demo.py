#!/usr/bin/env python3
"""
Example usage and demonstration of the Lingongrova Bot
This script shows how to use the bot and provides a simple demo.
"""

import sys
import os

def print_bot_demo():
    """Print a demonstration of how the bot works."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                    LINGONGROVA BOT DEMO                       ║
║                  Bubble Shooter Game AI                      ║
╚═══════════════════════════════════════════════════════════════╝

🎯 HOW THE BOT WORKS:

1. GAME DETECTION 🔍
   • Takes screenshots of the game screen
   • Uses OpenCV computer vision to detect:
     - Red bubbles and their positions
     - Hit count numbers on each bubble
     - Shooter position at bottom
     - Game area boundaries

2. STRATEGIC ANALYSIS 🧠
   • Evaluates all detected bubbles
   • Prioritizes targets based on:
     - Low hit counts (easier to destroy)
     - High position (more threatening)
     - Potential chain reactions
   • Calculates optimal shooting angles

3. PHYSICS SIMULATION ⚡
   • Simulates bullet trajectories with:
     - Realistic gravity effects
     - Wall bounces with energy loss
     - Collision detection with bubbles
   • Supports both direct and bounced shots

4. AUTOMATED CONTROL 🎮
   • Controls web browser using Playwright
   • Moves mouse to optimal aiming position
   • Clicks to shoot at calculated angle
   • Waits for appropriate timing between shots

📁 PROJECT STRUCTURE:

lingongrova/
├── bot/
│   ├── detection/
│   │   └── game_detector.py      # Computer vision system
│   ├── aiming/
│   │   └── aiming_system.py      # Physics and strategy
│   ├── control/
│   │   └── game_controller.py    # Browser automation
│   └── utils/
│       └── config.py             # Configuration management
├── main.py                       # Main bot script
├── test_bot.py                   # Test suite
├── requirements.txt              # Python dependencies
└── README.md                     # Documentation

🚀 QUICK START:

1. Install dependencies:
   pip install -r requirements.txt
   playwright install chromium

2. Run the bot:
   python main.py

3. Advanced usage:
   python main.py --headless              # Background mode
   python main.py --max-rounds 100        # Limit rounds
   python main.py --url "custom-game-url" # Different game

🛠️ FEATURES:

✓ Advanced computer vision for game state detection
✓ Physics-based trajectory calculation with bounces
✓ Smart target prioritization and strategy
✓ Robust web browser automation
✓ Debug mode with annotated screenshots
✓ Configurable settings and parameters
✓ Comprehensive error handling and logging
✓ Cross-platform compatibility

🎮 GAME COMPATIBILITY:

The bot is designed for bubble shooter games with:
• Red bubbles that rise from bottom
• Hit count numbers displayed on bubbles
• Physics-based bullet trajectories
• Wall bouncing mechanics

🔧 CUSTOMIZATION:

The bot can be easily adapted for different games by:
• Adjusting color detection ranges
• Modifying physics parameters
• Changing targeting strategies
• Adding new game mechanics

This implementation provides a solid foundation for automated
bubble shooter gameplay with room for enhancement and customization!
""")

def check_environment():
    """Check if the bot environment is properly set up."""
    print("\n🔍 ENVIRONMENT CHECK:")
    
    # Check if we're in the right directory
    if os.path.exists('bot/detection/game_detector.py'):
        print("✓ Bot files found")
    else:
        print("✗ Bot files not found - make sure you're in the project directory")
        return False
    
    # Check Python version
    if sys.version_info >= (3, 8):
        print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} (compatible)")
    else:
        print(f"✗ Python {sys.version_info.major}.{sys.version_info.minor} (requires 3.8+)")
        return False
    
    # Check dependencies
    dependencies = ['cv2', 'numpy', 'playwright', 'PIL', 'dotenv']
    missing = []
    
    for dep in dependencies:
        try:
            if dep == 'cv2':
                import cv2
            elif dep == 'PIL':
                import PIL
            elif dep == 'dotenv':
                import dotenv
            else:
                __import__(dep)
            print(f"✓ {dep}")
        except ImportError:
            print(f"✗ {dep} (missing)")
            missing.append(dep)
    
    if missing:
        print(f"\n📦 To install missing dependencies:")
        print("pip install -r requirements.txt")
        print("playwright install chromium")
        return False
    
    print("\n🎉 Environment is ready! You can run the bot with:")
    print("python main.py")
    return True

def main():
    """Main demo function."""
    print_bot_demo()
    
    # Check if dependencies are available
    if len(sys.argv) > 1 and sys.argv[1] == '--check':
        check_environment()
    else:
        print("\n💡 To check if your environment is ready, run:")
        print("python demo.py --check")

if __name__ == "__main__":
    main()