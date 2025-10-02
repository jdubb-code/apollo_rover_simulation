#!/usr/bin/env python3
"""
Direct launcher for Phase 1 of Archaeological Rover Game
"""

import sys
import os

# Add rover_game to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rover_game'))

from phases.phase1_simple import Phase1Game

def main():
    """Launch Phase 1 directly"""
    print("Archaeological Rover - Phase 1: Simple Graphics")
    print("===============================================")
    print("Starting game...")
    print("Controls: WASD to move, left-click to mark dig sites, ESC to exit")
    print("Look for the pygame window - it should appear shortly!")

    try:
        game = Phase1Game()
        game.run()
        print("Game closed.")
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()