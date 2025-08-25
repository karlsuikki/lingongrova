# Lingongrova Bot

An intelligent bot for playing the lingongrova bubble shooter web game. This bot uses computer vision to analyze the game state and physics-based calculations to determine optimal shooting strategies.

## Link to Competition
https://pagen.se/sortiment/lingongrova/vinn-skolstartskit/?utm_source=pagen&utm_medium=kampanjsidan&utm_campaign=2025_w34_vinn_skolstartkit&utm_content=vinn_skolstartkit_2025

## Features

- **Computer Vision**: Uses OpenCV to detect bubbles, hit counts, and game state
- **Physics Simulation**: Calculates bullet trajectories with gravity and wall bounces
- **Smart Targeting**: Prioritizes bubbles based on hit count and strategic value
- **Web Automation**: Controls the browser using Playwright for reliable interaction
- **Debug Mode**: Saves annotated screenshots for analysis and debugging

## Game Mechanics

The bot is designed for bubble shooter games with these characteristics:
- Shoot bullets at red bubbles rising from the bottom
- Bubbles have numbers indicating how many hits are needed to destroy them
- Bullets follow realistic physics with gravity and wall bounces
- After shooting, bubbles rise and new ones spawn

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/karlsuikki/lingongrova.git
   cd lingongrova
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

## Configuration

Copy the example environment file and customize settings:
```bash
cp .env.example .env
```

Available configuration options:
- `GAME_URL`: URL of the game (default: competition link)
- `HEADLESS`: Run browser in headless mode (true/false)
- `DEBUG`: Enable debug mode with screenshots (true/false)
- `SCREENSHOT_DIR`: Directory for debug screenshots
- `MAX_ROUNDS`: Maximum number of rounds to play
- `SHOT_COOLDOWN`: Seconds to wait between shots

## Usage

### Basic Usage
```bash
python main.py
```

### Command Line Options
```bash
python main.py --headless              # Run in headless mode
python main.py --no-debug              # Disable debug screenshots
python main.py --max-rounds 100        # Play up to 100 rounds
python main.py --url "https://..."     # Use custom game URL
```

### Testing the Bot
Run the test suite to verify everything is working:
```bash
python test_bot.py
```

## Architecture

The bot is organized into several modules:

### Detection (`bot/detection/`)
- `GameDetector`: Analyzes screenshots to detect game elements
- Uses OpenCV for computer vision and image processing
- Identifies bubbles, hit counts, shooter position, and bullets

### Aiming (`bot/aiming/`)
- `AimingSystem`: Calculates optimal shooting angles
- Simulates bullet physics with gravity and bounces
- Evaluates shot quality based on multiple factors

### Control (`bot/control/`)
- `GameController`: Manages browser automation and game loop
- Uses Playwright for reliable web interactions
- Coordinates detection and aiming systems

### Utils (`bot/utils/`)
- Configuration management
- Logging setup
- Dependency validation

## How It Works

1. **Game Detection**: Takes screenshots and uses computer vision to identify:
   - Bubble positions and hit counts
   - Shooter location
   - Game boundaries

2. **Strategy Calculation**: Analyzes detected bubbles to determine:
   - Priority targets (low hit count, high position)
   - Optimal shooting angles
   - Potential chain reactions

3. **Execution**: Controls the browser to:
   - Aim at calculated position
   - Click to shoot
   - Wait for appropriate timing

4. **Loop**: Repeats the process until game completion or max rounds reached

## Debug Features

When debug mode is enabled, the bot will:
- Save annotated screenshots showing detected elements
- Log detailed information about decisions
- Display real-time analysis of game state

Screenshots are saved in the `screenshots/` directory with annotations showing:
- Detected bubbles (green circles)
- Hit counts (white numbers)
- Shooter position (red circle)
- Game area boundaries (yellow rectangle)

## Troubleshooting

### Common Issues

1. **Game not detected**: 
   - Check if the game URL is correct
   - Ensure the game has loaded completely
   - Try adjusting detection parameters

2. **Poor shooting accuracy**:
   - Verify game area detection is correct
   - Check if bubble detection is accurate
   - Adjust physics parameters if needed

3. **Browser automation fails**:
   - Ensure Playwright browsers are installed
   - Check for popup blockers or security restrictions
   - Try running in non-headless mode for debugging

### Performance Tips

- Use headless mode for better performance
- Reduce debug output for faster execution
- Adjust shot cooldown based on game timing
- Monitor system resources during long sessions

## Contributing

Feel free to contribute improvements:
- Better computer vision algorithms
- More sophisticated aiming strategies
- Additional game mechanic support
- Performance optimizations

## License

This project is for educational and competition purposes.

