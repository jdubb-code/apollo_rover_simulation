# Archaeological Rover Simulation

A multi-phase video game demonstrating an archaeological rover's capabilities for exploration, hazard detection, and scientific data collection.

## Quick Start

### Automated Setup (Recommended)

**macOS/Linux:**
```bash
./setup.sh
```

**Windows:**
```cmd
setup.bat
```

The installer will:
- Check for Python 3.8+
- Create a virtual environment
- Install all dependencies
- Provide instructions to run the game

### Manual Setup

If the automated installer doesn't work:

1. **Install Python 3.8 or later:**
   - macOS: `brew install python3` or download from [python.org](https://www.python.org/downloads/)
   - Windows: Download from [python.org](https://www.python.org/downloads/) (check "Add Python to PATH")
   - Linux: `sudo apt install python3 python3-venv python3-pip`

2. **Create virtual environment:**
   ```bash
   # macOS/Linux
   python3 -m venv rover_env
   source rover_env/bin/activate

   # Windows
   python -m venv rover_env
   rover_env\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the game:**
   ```bash
   python main.py
   ```

### Troubleshooting

**"python3: command not found" (macOS/Linux)**
- Install Python 3: `brew install python3` or from [python.org](https://www.python.org/downloads/)

**"python is not recognized" (Windows)**
- Reinstall Python and check "Add Python to PATH" during installation

**"No module named 'pygame'"**
- Make sure virtual environment is activated: `source rover_env/bin/activate` (macOS/Linux) or `rover_env\Scripts\activate` (Windows)
- Reinstall dependencies: `pip install -r requirements.txt`

**Permission denied: ./setup.sh**
- Make script executable: `chmod +x setup.sh`

## Game Phases

### Phase 1: Simple Graphics (✅ Complete)
- Basic geometric rover representation
- Overhead camera view
- Simple movement and dig site marking
- **Controls:**
  - WASD or Arrow Keys: Move rover
  - Left Click: Mark potential dig site
  - C: Clear all dig sites
  - ESC: Exit

### Phase 2: Realistic Graphics (✅ Complete)
- Detailed 6-wheel rover sprite based on concept sketches
- Enhanced terrain textures with visual depth
- Professional UI design with gradient panels
- Hazard detection system with collision avoidance
- Dust particle effects and realistic animations
- Warning system for detected environmental hazards

### Phase 3: GPR Integration (✅ Complete)
- Ground Penetrating Radar interface in top-right corner
- Real-time subsurface data visualization with color-coded signals
- 20 hidden artifacts with depth-based detection system
- Artifact cataloging system with automatic ID assignment
- Scientific signal strength indicators and confidence tracking
- Enhanced 1400x900 display for GPR visualization

### Phase 4: Advanced Features (✅ Complete)
- Dig tool: Click on marked dig sites to excavate and view artifact images
- Proximity-based excavation system with notification log
- Variable confidence levels based on artifact depth/size and scan proximity
- Scrollable artifact catalog for better organization
- Full-map clicking capability (no restricted UI areas)
- Reset functionality for map and artifact state

### Phase 5: Keep-Out Zones (✅ Complete)
- Physics-based collision detection system
- Hazard keep-out zones preventing rover entry
- Visual indicators for restricted areas (red zones)
- Collision warning system with feedback
- Boundary sliding mechanics for smooth navigation
- Toggle visualization of keep-out zones (K key)

### Phase 6: Realistic Hazards & Camera System (✅ Complete)
- **Camera System**: Rover stays centered on screen while exploring a larger 3000x2400 world
- **Realistic hazard graphics** with 5 types: rocks, boulders, trees, water, and ponds
- Type-specific visual representations:
  - Rocks and boulders: Irregular shapes with texture and lighting effects
  - Trees: Brown trunks with green foliage layers
  - Bodies of water: Animated ripples and reflections
- Enhanced environmental diversity with 25-35 hazards and 30-40 artifacts
- Smooth camera following that keeps rover centered during exploration
- **Battery system**: 60-second capacity that drains during movement
- **Auto-recharge at base**: Battery recharges over 5 seconds when at base
- **Return-to-base autopilot**: Press R to automatically navigate back to base
- Pathfinding that avoids keep-out zones
- **Debugging controls** for artifact discovery:
  - Press N to show/hide artifact count in status panel
  - Press H to show all artifact locations (gray X marks)
  - Gold circles indicate discovered artifacts
  - Use GPR (G key) to scan and discover artifacts, then excavate nearby
- All Phase 5 features (keep-out zones, collision detection) with improved graphics

### Phase 7: Exploration Mode (✅ Complete)
- **Hidden hazards**: Hazards are invisible until discovered
- **Discovery system**: Rover must get within 150 pixels to reveal hazards
- **Exploration statistics**: Track discovery progress (X/Y hazards found)
- Keep-out zones only apply to discovered hazards
- Collision detection works with both discovered and undiscovered hazards
- Press E to toggle exploration stats panel
- All Phase 6 features inherited (battery, autopilot, camera system)

### Phase 8: Grid Navigation (✅ Complete)
- **Visual grid overlay**: 100x100 pixel grid dividing the map into sections
- **World boundaries**: Map is now bounded - rover cannot drive infinitely
- Rover constrained within dig site boundaries (50 pixel buffer from edges)
- **Autonomous grid navigation**: Lawn-mower pattern surveying
  - Press V for horizontal sweeping pattern
  - Press B for vertical sweeping pattern
  - Press X to stop autonomous navigation
- **Intelligent obstacle avoidance**: When obstacle blocks grid path:
  - Rover automatically finds detour around obstacle
  - Returns to grid path after clearing obstacle
  - Shows detour waypoints in orange
- **Visual feedback**:
  - Current target waypoint in green
  - Completed waypoints in gray
  - Upcoming waypoints in cyan
  - Red boundary lines marking world edges
- Press M to toggle grid display
- Grid navigation status panel showing progress
- All Phase 7 features inherited

## Project Structure

```
apollo_2026_ip_v2/
├── main.py                    # Game launcher
├── run_game.py               # Helper script with venv
├── requirements.txt          # Python dependencies
├── rover_game/
│   ├── phases/
│   │   └── phase1_simple.py  # Phase 1 implementation
│   ├── rover/                # Rover mechanics (future)
│   ├── systems/              # Game systems (future)
│   └── assets/               # Graphics and data (future)
└── rover_env/                # Virtual environment
```

## Concept Art
- `apollo_rover1_low_res.jpg` - Original rover design sketch
- `apollo_rover2_lowres.jpg` - Additional rover concepts

## Features Implemented (Phase 1)
- ✅ Basic rover movement with WASD/Arrow keys
- ✅ Rover rotation and momentum physics
- ✅ Trail/track visualization
- ✅ Click-to-mark dig site system
- ✅ Real-time rover status display
- ✅ Coordinate system and grid overlay
- ✅ Simple terrain visualization

## Next Steps
1. Enhance graphics for Phase 2 ✅
2. Add hazard detection system ✅
3. Implement GPR interface for Phase 3 ✅
4. Implement advanced features for Phase 4 ✅
5. Implement keep-out zones for Phase 5 ✅
6. Add realistic hazard graphics for Phase 6 ✅
7. Add exploration mode for Phase 7 ✅
8. Add grid navigation for Phase 8 ✅
9. Future enhancements (TBD)

## Development
Built with Python, Pygame, and designed for future integration with PyBullet, matplotlib, and numpy for advanced scientific visualization.