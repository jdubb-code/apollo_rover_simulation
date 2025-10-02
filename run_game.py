#!/usr/bin/env python3
"""
Run Archaeological Rover Game with virtual environment activation
"""
import subprocess
import sys
import os

def run_with_venv():
    """Run the game using the virtual environment"""
    # Get the path to the virtual environment Python
    venv_python = os.path.join(os.path.dirname(__file__), "rover_env", "bin", "python")

    if not os.path.exists(venv_python):
        print("Virtual environment not found. Please run:")
        print("python3 -m venv rover_env")
        print("source rover_env/bin/activate")
        print("pip install -r requirements.txt")
        return

    # Run the main game
    main_script = os.path.join(os.path.dirname(__file__), "main.py")
    subprocess.run([venv_python, main_script])

if __name__ == "__main__":
    run_with_venv()