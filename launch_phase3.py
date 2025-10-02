#!/usr/bin/env python3
"""
Direct launcher for Phase 3 of Archaeological Rover Game
"""

import sys
import os

# Add rover_game to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rover_game'))

from phases.phase3_gpr import Phase3Game

def main():
    """Launch Phase 3 directly"""
    print("Archaeological Rover - Phase 3: GPR Integration")
    print("===============================================")
    print("Starting GPR-enabled archaeological exploration...")
    print("")
    print("🚀 NEW FEATURES:")
    print("• Ground Penetrating Radar in top-right corner")
    print("• Real-time subsurface data visualization")
    print("• 20 hidden artifacts to discover underground")
    print("• Artifact catalog system with detailed tracking")
    print("• Scientific signal strength indicators")
    print("• Enhanced 1400x900 display for better visibility")
    print("")
    print("🎮 CONTROLS:")
    print("• WASD: Move rover")
    print("• Left Click: Mark dig sites (near gold artifacts for excavation)")
    print("• G: Toggle GPR on/off")
    print("• C: Clear dig sites")
    print("• ESC: Exit")
    print("")
    print("🔬 GPR GUIDE:")
    print("• Red signals: Strong artifact signatures (deep/large)")
    print("• Yellow signals: Medium artifact signatures")
    print("• Green signals: Weak artifact signatures (shallow/small)")
    print("• Watch the scanning line move across subsurface data")
    print("• Artifacts appear as gold circles when confidence reaches 80%+")
    print("")
    print("Look for the pygame window - archaeological discovery awaits!")

    try:
        game = Phase3Game()
        game.run()
        print("Archaeological mission completed.")
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()