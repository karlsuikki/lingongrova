#!/usr/bin/env python3
"""
Setup script for the Lingongrova Bot
This script helps set up the bot environment and dependencies.
"""

import subprocess
import sys
import os
import shutil


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        if e.stdout:
            print(f"   Output: {e.stdout}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info >= (3, 8):
        print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
        return True
    else:
        print(f"✗ Python {sys.version_info.major}.{sys.version_info.minor} is not compatible")
        print("  Please install Python 3.8 or newer")
        return False


def setup_virtual_environment():
    """Set up a virtual environment."""
    if not shutil.which('python'):
        print("✗ Python not found in PATH")
        return False
    
    venv_path = "venv"
    if os.path.exists(venv_path):
        print("✓ Virtual environment already exists")
        return True
    
    return run_command(f"{sys.executable} -m venv {venv_path}", 
                      "Creating virtual environment")


def install_dependencies():
    """Install Python dependencies."""
    # Try simple requirements first
    if os.path.exists("requirements-simple.txt"):
        success = run_command("pip install -r requirements-simple.txt", 
                            "Installing Python packages")
    else:
        success = run_command("pip install -r requirements.txt", 
                            "Installing Python packages")
    
    if not success:
        print("❌ Failed to install Python dependencies")
        print("💡 Try installing manually:")
        print("   pip install playwright opencv-python numpy pillow python-dotenv")
        return False
    
    return True


def install_playwright_browsers():
    """Install Playwright browsers."""
    return run_command("playwright install chromium", 
                      "Installing Playwright browsers")


def create_config_file():
    """Create configuration file."""
    if os.path.exists(".env"):
        print("✓ Configuration file already exists")
        return True
    
    if os.path.exists(".env.example"):
        try:
            shutil.copy(".env.example", ".env")
            print("✓ Created configuration file from example")
            return True
        except Exception as e:
            print(f"✗ Failed to create config file: {e}")
            return False
    
    # Create a basic config file
    config_content = """# Lingongrova Bot Configuration
GAME_URL=https://pagen.se/sortiment/lingongrova/vinn-skolstartskit/
HEADLESS=false
DEBUG=true
SCREENSHOT_DIR=screenshots
"""
    try:
        with open(".env", "w") as f:
            f.write(config_content)
        print("✓ Created basic configuration file")
        return True
    except Exception as e:
        print(f"✗ Failed to create config file: {e}")
        return False


def test_installation():
    """Test if the installation works."""
    print("\n🧪 Testing installation...")
    
    try:
        # Test basic imports
        import cv2
        import numpy as np
        import playwright
        print("✓ All required packages can be imported")
        
        # Test bot modules
        from bot.detection.game_detector import GameDetector
        from bot.aiming.aiming_system import AimingSystem
        print("✓ Bot modules can be imported")
        
        print("✅ Installation test passed!")
        return True
        
    except ImportError as e:
        print(f"✗ Import test failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def main():
    """Main setup function."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                  LINGONGROVA BOT SETUP                       ║
║               Automated Installation Script                  ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    steps_completed = 0
    total_steps = 5
    
    # Step 1: Check Python version
    if check_python_version():
        steps_completed += 1
    else:
        print("❌ Setup failed at Python version check")
        return False
    
    # Step 2: Install dependencies
    print(f"\n📋 Step 2/{total_steps}: Installing Dependencies")
    if install_dependencies():
        steps_completed += 1
    else:
        print("⚠️  Dependency installation failed, but continuing...")
    
    # Step 3: Install Playwright browsers
    print(f"\n📋 Step 3/{total_steps}: Installing Browser")
    if install_playwright_browsers():
        steps_completed += 1
    else:
        print("⚠️  Browser installation failed, but continuing...")
    
    # Step 4: Create config file
    print(f"\n📋 Step 4/{total_steps}: Creating Configuration")
    if create_config_file():
        steps_completed += 1
    
    # Step 5: Test installation
    print(f"\n📋 Step 5/{total_steps}: Testing Installation")
    if test_installation():
        steps_completed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Setup completed: {steps_completed}/{total_steps} steps successful")
    
    if steps_completed >= 4:  # Allow some flexibility
        print("""
🎉 SETUP SUCCESSFUL!

You can now run the bot with:
  python main.py

For a demonstration:
  python demo.py

For testing:
  python test_bot.py

For help:
  python main.py --help
""")
        return True
    else:
        print("""
❌ SETUP INCOMPLETE

Please check the errors above and try:
1. Installing dependencies manually: pip install playwright opencv-python numpy pillow python-dotenv
2. Installing browsers: playwright install chromium
3. Running the test: python demo.py --check
""")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)