#!/usr/bin/env python3
"""
Archaeological Rover Game
Main launcher for all phases of the rover simulation
"""

import sys
import os

# Add rover_game to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rover_game'))

from phases.phase1_simple import Phase1Game
from phases.phase2_graphics import Phase2Game
from phases.phase3_gpr import Phase3Game
from phases.phase4_advanced import Phase4Game
from phases.phase5_physics import Phase5Game
from phases.phase6_extended import Phase6Game
from phases.phase7_exploration import Phase7Game
from phases.phase8_grid import Phase8Game

def main():
    """Main entry point for the rover game"""
    print("Archaeological Rover Simulation")
    print("================================")
    print("1. Phase 1: Simple Graphics")
    print("2. Phase 2: Realistic Graphics")
    print("3. Phase 3: GPR Integration")
    print("4. Phase 4: Advanced Features")
    print("5. Phase 5: Keep-Out Zones")
    print("6. Phase 6: Extended Features")
    print("7. Phase 7: Exploration Mode")
    print("8. Phase 8: Grid Navigation")

    choice = input("\nSelect phase (1-8) or press Enter for Phase 3: ").strip()

    if choice == "1":
        print("Starting Phase 1...")
        print("A pygame window should open. If you don't see it, check your dock/taskbar.")
        print("Controls: WASD to move, left-click to mark dig sites, ESC to exit")

        try:
            game = Phase1Game()
            game.run()
        except Exception as e:
            print(f"Error running game: {e}")
            print("Make sure you have pygame installed: pip install pygame")

    elif choice == "2":
        print("Starting Phase 2...")
        print("Enhanced graphics with hazard detection system!")
        print("Controls: WASD to move, left-click to mark dig sites, ESC to exit")
        print("Red outlines indicate detected hazards - avoid collisions!")

        try:
            game = Phase2Game()
            game.run()
        except Exception as e:
            print(f"Error running game: {e}")
            print("Make sure you have pygame installed: pip install pygame")

    elif choice == "3" or choice == "":
        print("Starting Phase 3...")
        print("GPR Integration with artifact detection!")
        print("Controls: WASD to move, left-click to mark dig sites, G to toggle GPR")
        print("Watch the GPR display for subsurface artifacts (red/yellow signals)")
        print("Gold circles appear when artifacts are discovered!")

        try:
            game = Phase3Game()
            game.run()
        except Exception as e:
            print(f"Error running game: {e}")
            print("Make sure you have pygame and numpy installed")

    elif choice == "4":
        print("Starting Phase 4...")
        print("Advanced Features with proximity-based dig tool and notification system!")
        print("Controls: WASD to move, left-click to mark dig sites, G to toggle GPR")
        print("Approach marked sites near artifacts and press P to excavate!")
        print("Green circles indicate excavatable sites. Notifications appear in artifact log.")

        try:
            game = Phase4Game()
            game.run()
        except Exception as e:
            print(f"Error running game: {e}")
            print("Make sure you have pygame and numpy installed")

    elif choice == "5":
        print("Starting Phase 5...")
        print("Keep-Out Zones: Rover cannot enter hazard areas!")
        print("Controls: WASD to move, left-click to mark dig sites, P to excavate, K to toggle zones")
        print("Red zones show where rover cannot go. Watch for collision warnings!")

        try:
            game = Phase5Game()
            game.run()
        except Exception as e:
            print(f"Error running game: {e}")
            print("Make sure you have pygame and numpy installed")

    elif choice == "6":
        print("Starting Phase 6...")
        print("Realistic Hazards with Camera System & Autopilot!")
        print("Explore a 3000x2400 world - camera follows the rover keeping it centered!")
        print("Navigate around rocks, boulders, trees, and bodies of water with animated effects!")
        print("Controls: WASD to move, R to return to base (autopilot), G to use GPR, P to excavate")
        print("Autopilot calculates path avoiding keep-out zones!")
        print("Battery drains during movement and recharges at base (5 seconds)")
        print("Debugging: Press N to show artifact count, H to see all artifact locations")

        try:
            game = Phase6Game()
            game.run()
        except Exception as e:
            print(f"Error running game: {e}")
            print("Make sure you have pygame and numpy installed")

    elif choice == "7":
        print("Starting Phase 7...")
        print("Exploration Mode: Discover Hidden Hazards!")
        print("Hazards are invisible until you explore and discover them!")
        print("Navigate carefully - undiscovered hazards can still block your path!")
        print("Controls: WASD to move, R to return to base, G to use GPR, P to excavate")
        print("Press E to toggle exploration stats showing discovery progress")
        print("Battery system with auto-recharge at base included!")

        try:
            game = Phase7Game()
            game.run()
        except Exception as e:
            print(f"Error running game: {e}")
            print("Make sure you have pygame and numpy installed")

    elif choice == "8":
        print("Starting Phase 8...")
        print("Grid Navigation: Autonomous Survey Mode!")
        print("Visual grid overlay divides the map into sections")
        print("World is now bounded - rover cannot drive infinitely!")
        print("Autonomous grid-following with obstacle avoidance")
        print("")
        print("Controls:")
        print("  V: Start horizontal grid navigation")
        print("  B: Start vertical grid navigation")
        print("  X: Stop grid navigation")
        print("  M: Toggle grid display")
        print("  All Phase 7 controls (WASD, R, G, P, E, etc.)")
        print("")
        print("The rover will autonomously follow a lawn-mower pattern,")
        print("automatically avoiding obstacles and resuming the grid path!")

        try:
            game = Phase8Game()
            game.run()
        except Exception as e:
            print(f"Error running game: {e}")
            print("Make sure you have pygame and numpy installed")

    else:
        print("Invalid selection. Please choose 1-8.")

if __name__ == "__main__":
    main()