# Archaeological Rover Simulation

A multi-phase video game demonstrating an archaeological rover's capabilities for exploration, hazard detection, and scientific data collection.

## Quick Start

1. **Install dependencies:**
   ```bash
   python3 -m venv rover_env
   source rover_env/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the game:**
   ```bash
   python main.py
   ```

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

### Phase 4: Advanced Features (🚧 In Development)
- Dig tool: Click on marked dig sites to excavate and view artifact images
- Enhanced hazard system requiring specialized attachments for cleanup
- Robot hub for depositing artifacts, soil samples, and swapping attachments
- Variable confidence levels based on artifact depth/size and scan proximity
- Scrollable artifact catalog for better organization
- Full-map clicking capability (no restricted UI areas)
- Reset functionality for map and artifact state

### Phase 5: Advanced Physics (🚧 Coming Soon)
- PyBullet physics engine integration
- Realistic 6-wheel rover suspension
- Authentic terrain interaction
- Advanced environmental challenges

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
4. Implement advanced features for Phase 4
5. Integrate PyBullet physics for Phase 5

## Development
Built with Python, Pygame, and designed for future integration with PyBullet, matplotlib, and numpy for advanced scientific visualization.