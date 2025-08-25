import os
import time
from typing import Dict, Any
from dotenv import load_dotenv


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    load_dotenv()
    
    return {
        'game_url': os.getenv('GAME_URL', 'https://pagen.se/sortiment/lingongrova/vinn-skolstartskit/'),
        'headless': os.getenv('HEADLESS', 'false').lower() == 'true',
        'debug': os.getenv('DEBUG', 'true').lower() == 'true',
        'screenshot_dir': os.getenv('SCREENSHOT_DIR', 'screenshots'),
        'max_rounds': int(os.getenv('MAX_ROUNDS', '50')),
        'shot_cooldown': float(os.getenv('SHOT_COOLDOWN', '2.0')),
    }


def setup_logging():
    """Set up logging configuration."""
    import logging
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/bot_{int(time.time())}.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('lingongrova_bot')


def print_banner():
    """Print bot banner."""
    banner = """
    ╔═══════════════════════════════════════╗
    ║          LINGONGROVA BOT              ║
    ║     Bubble Shooter Game AI            ║
    ╚═══════════════════════════════════════╝
    """
    print(banner)


def validate_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import cv2
        import numpy as np
        import playwright
        from PIL import Image
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False