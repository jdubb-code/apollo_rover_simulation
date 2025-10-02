#!/usr/bin/env python3
"""
Direct launcher for Phase 2 of Archaeological Rover Game
"""

import sys
import os

# Add rover_game to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rover_game'))

from phases.phase2_graphics import Phase2Game

def main():
    """Launch Phase 2 directly"""
    print("Archaeological Rover - Phase 2: Realistic Graphics")
    print("==================================================")
    print("Starting enhanced game...")
    print("Features:")
    print("• Detailed 6-wheel rover based on concept sketches")
    print("• Realistic terrain with hazard detection")
    print("• Dust particle effects and enhanced animations")
    print("• Professional UI with warning system")
    print("• Collision detection with environmental hazards")
    print("")
    print("Controls: WASD to move, left-click to mark dig sites, ESC to exit")
    print("Red outlines indicate detected hazards!")

    try:
        game = Phase2Game()
        game.run()
        print("Game closed.")
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()