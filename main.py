#!/usr/bin/env python3
"""
Lingongrova Bot - Automated bubble shooter game player
"""

import asyncio
import sys
import argparse
from bot.control.game_controller import GameController
from bot.utils.config import load_config, setup_logging, print_banner, validate_dependencies


async def main():
    """Main entry point for the bot."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Lingongrova Bubble Shooter Bot')
    parser.add_argument('--headless', action='store_true', 
                       help='Run browser in headless mode')
    parser.add_argument('--no-debug', action='store_true',
                       help='Disable debug mode and screenshots')
    parser.add_argument('--max-rounds', type=int, default=50,
                       help='Maximum number of rounds to play')
    parser.add_argument('--url', type=str,
                       help='Game URL (overrides config)')
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Validate dependencies
    if not validate_dependencies():
        sys.exit(1)
    
    # Load configuration
    config = load_config()
    
    # Override config with command line arguments
    if args.headless:
        config['headless'] = True
    if args.no_debug:
        config['debug'] = False
    if args.max_rounds:
        config['max_rounds'] = args.max_rounds
    if args.url:
        config['game_url'] = args.url
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Lingongrova Bot")
    
    # Print configuration
    print("\nConfiguration:")
    print(f"  Game URL: {config['game_url']}")
    print(f"  Headless: {config['headless']}")
    print(f"  Debug: {config['debug']}")
    print(f"  Max Rounds: {config['max_rounds']}")
    print()
    
    # Initialize game controller
    controller = GameController(
        headless=config['headless'],
        debug=config['debug']
    )
    
    try:
        # Start browser
        print("Starting browser...")
        await controller.start_browser()
        
        # Navigate to game
        print("Navigating to game...")
        await controller.navigate_to_game(config['game_url'])
        
        # Look for game start button
        print("Looking for game start button...")
        game_started = await controller.find_and_start_game()
        
        if not game_started:
            print("Could not start game automatically. Please start manually and press Enter...")
            input()
        
        # Start playing
        print("Starting game loop...")
        await controller.play_game_loop(max_rounds=config['max_rounds'])
        
        print("Game completed successfully!")
        
    except KeyboardInterrupt:
        print("\nBot interrupted by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        print(f"Error: {e}")
    finally:
        # Clean up
        print("Cleaning up...")
        await controller.close()
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())