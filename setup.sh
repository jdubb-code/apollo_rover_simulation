#!/bin/bash

echo "============================================"
echo "Archaeological Rover Simulation - Setup"
echo "============================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo ""
    echo "Please install Python 3.8 or later:"
    echo "  macOS: brew install python3"
    echo "  or download from: https://www.python.org/downloads/"
    echo ""
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "✓ Found Python $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "❌ Python 3.8 or later is required."
    echo "Please upgrade Python: https://www.python.org/downloads/"
    exit 1
fi

echo ""
echo "Creating virtual environment..."
python3 -m venv rover_env

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment."
    echo "You may need to install python3-venv:"
    echo "  Ubuntu/Debian: sudo apt install python3-venv"
    exit 1
fi

echo "✓ Virtual environment created"
echo ""
echo "Activating virtual environment..."

# Activate virtual environment
source rover_env/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment."
    exit 1
fi

echo "✓ Virtual environment activated"
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies."
    exit 1
fi

echo ""
echo "============================================"
echo "✓ Setup complete!"
echo "============================================"
echo ""
echo "To run the game:"
echo "  1. Activate the virtual environment:"
echo "     source rover_env/bin/activate"
echo ""
echo "  2. Run the game:"
echo "     python main.py"
echo ""
echo "To deactivate the virtual environment later:"
echo "     deactivate"
echo ""
