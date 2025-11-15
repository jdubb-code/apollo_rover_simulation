"""
Phase 8: Grid Navigation
Building upon Phase 7 with grid overlay, world boundaries, and grid-following navigation
"""

import pygame
import math
import random
from .phase7_exploration import Phase7Game, ExplorationHazard


class Phase8Game(Phase7Game):
    """Phase 8 game with grid navigation and world boundaries"""

    def __init__(self):
        # Initialize Phase7Game first
        super().__init__()

        pygame.display.set_caption("Archaeological Rover - Phase 8: Grid Navigation")

        # Grid settings
        self.grid_size = 100  # Grid cell size in pixels
        self.show_grid = True

        # Grid following system
        self.grid_following = False
        self.grid_pattern = "horizontal"  # horizontal, vertical, or spiral
        self.grid_waypoints = []
        self.grid_waypoint_index = 0
        self.grid_start_x = None
        self.grid_start_y = None

        # Obstacle avoidance during grid following
        self.original_grid_path = []
        self.avoiding_obstacle = False
        self.avoidance_waypoints = []
        self.avoidance_waypoint_index = 0

        # Grid-specific stuck detection
        self.grid_stuck_counter = 0
        self.grid_last_position = None
        self.grid_backing_up = False
        self.grid_backup_distance = 0
        self.grid_original_waypoint = None  # Store waypoint before obstacle
        self.grid_collision_pause_frames = 0  # Pause counter for collision recovery
        self.grid_collision_state = None  # States: 'pause_before', 'backing_up', 'pause_after', None
        self.grid_last_speed = 0  # Track speed to detect collisions
        self.grid_collision_cooldown = 0  # Cooldown to prevent rapid retriggering

        # World boundaries (make world finite)
        self.enable_boundaries = True
        self.boundary_buffer = 50  # Keep rover this far from edge

        # Survey system
        self.survey_active = False
        self.survey_button_rect = None
        self.survey_phase = "horizontal"  # "horizontal" or "vertical"
        self.show_stop_confirmation = False
        self.confirmation_yes_rect = None
        self.confirmation_no_rect = None
        self.battery_threshold_for_return = 60.0  # Return when 60 seconds battery left (25% of 240s)

        # Resume position tracking
        self.resume_position = None  # (x, y) where rover should return after recharge
        self.returning_to_resume = False  # Flag to track if navigating to resume position

    def draw_grid(self):
        """Draw grid overlay on the world"""
        if not self.show_grid:
            return

        # Calculate visible grid range based on camera position
        start_x = max(0, int(self.camera.x // self.grid_size) * self.grid_size)
        start_y = max(0, int(self.camera.y // self.grid_size) * self.grid_size)
        end_x = min(self.world_width, int((self.camera.x + self.width) // self.grid_size + 1) * self.grid_size)
        end_y = min(self.world_height, int((self.camera.y + self.height) // self.grid_size + 1) * self.grid_size)

        # Draw vertical lines
        for x in range(start_x, end_x + self.grid_size, self.grid_size):
            if x <= self.world_width:
                screen_start = self.camera.apply(x, 0)
                screen_end = self.camera.apply(x, self.world_height)

                # Only draw if on screen
                if 0 <= screen_start[0] <= self.width:
                    pygame.draw.line(self.screen, (100, 100, 120),
                                   (screen_start[0], 0),
                                   (screen_end[0], self.height), 1)

        # Draw horizontal lines
        for y in range(start_y, end_y + self.grid_size, self.grid_size):
            if y <= self.world_height:
                screen_start = self.camera.apply(0, y)
                screen_end = self.camera.apply(self.world_width, y)

                # Only draw if on screen
                if 0 <= screen_start[1] <= self.height:
                    pygame.draw.line(self.screen, (100, 100, 120),
                                   (0, screen_start[1]),
                                   (self.width, screen_end[1]), 1)

        # Draw world boundary
        if self.enable_boundaries:
            # Draw rectangle around world bounds
            corners = [
                (0, 0),
                (self.world_width, 0),
                (self.world_width, self.world_height),
                (0, self.world_height),
                (0, 0)
            ]

            for i in range(len(corners) - 1):
                screen_start = self.camera.apply(corners[i][0], corners[i][1])
                screen_end = self.camera.apply(corners[i+1][0], corners[i+1][1])
                pygame.draw.line(self.screen, (255, 100, 100), screen_start, screen_end, 3)

    def generate_grid_path_horizontal(self):
        """Generate a lawn-mower pattern (horizontal sweeps)"""
        waypoints = []

        # Start from current position, snap to grid
        start_grid_x = int(self.rover.x // self.grid_size) * self.grid_size
        start_grid_y = int(self.rover.y // self.grid_size) * self.grid_size

        # Create horizontal sweeps across the map
        y = start_grid_y
        going_right = True

        while y < self.world_height - self.boundary_buffer:
            if going_right:
                # Sweep right
                for x in range(self.boundary_buffer, self.world_width - self.boundary_buffer, self.grid_size):
                    if self.is_waypoint_safe(x, y):
                        waypoints.append((x, y))
            else:
                # Sweep left
                for x in range(self.world_width - self.boundary_buffer, self.boundary_buffer, -self.grid_size):
                    if self.is_waypoint_safe(x, y):
                        waypoints.append((x, y))

            going_right = not going_right
            y += self.grid_size

        return waypoints

    def generate_grid_path_vertical(self):
        """Generate a lawn-mower pattern (vertical sweeps)"""
        waypoints = []

        # Start from current position, snap to grid
        start_grid_x = int(self.rover.x // self.grid_size) * self.grid_size
        start_grid_y = int(self.rover.y // self.grid_size) * self.grid_size

        # Create vertical sweeps across the map
        x = start_grid_x
        going_down = True

        while x < self.world_width - self.boundary_buffer:
            if going_down:
                # Sweep down
                for y in range(self.boundary_buffer, self.world_height - self.boundary_buffer, self.grid_size):
                    if self.is_waypoint_safe(x, y):
                        waypoints.append((x, y))
            else:
                # Sweep up
                for y in range(self.world_height - self.boundary_buffer, self.boundary_buffer, -self.grid_size):
                    if self.is_waypoint_safe(x, y):
                        waypoints.append((x, y))

            going_down = not going_down
            x += self.grid_size

        return waypoints

    def start_grid_following(self, pattern="horizontal"):
        """Start autonomous grid following"""
        self.grid_pattern = pattern

        if pattern == "horizontal":
            self.grid_waypoints = self.generate_grid_path_horizontal()
        elif pattern == "vertical":
            self.grid_waypoints = self.generate_grid_path_vertical()

        if self.grid_waypoints:
            self.grid_following = True
            self.grid_waypoint_index = 0
            self.original_grid_path = self.grid_waypoints.copy()
            self.avoiding_obstacle = False
            print(f"Starting grid navigation ({pattern} pattern) with {len(self.grid_waypoints)} waypoints")
        else:
            print("Failed to generate grid path")

    def stop_grid_following(self):
        """Stop grid following"""
        self.grid_following = False
        self.grid_waypoints = []
        self.grid_waypoint_index = 0
        self.avoiding_obstacle = False
        self.avoidance_waypoints = []
        print("Grid navigation stopped")

    def is_waypoint_safe(self, x, y):
        """Check if a waypoint is safe (not inside any hazard keep-out zone)"""
        for hazard in self.hazards:
            # Calculate distance from waypoint to hazard center
            dx = x - hazard.x
            dy = y - hazard.y
            distance = math.sqrt(dx * dx + dy * dy)

            # Keep-out radius = hazard radius + rover collision radius + safety buffer
            # Add extra 10 pixel buffer to ensure waypoint is safely outside
            keepout_radius = hazard.radius + self.rover.collision_radius + 10

            if distance < keepout_radius:
                return False  # Waypoint is inside keep-out zone

        return True  # Waypoint is safe

    def generate_serpentine_scan(self):
        """Generate a complete serpentine scan pattern: horizontal sweeps first, then vertical"""
        waypoints = []
        visited_positions = set()  # Track visited positions to avoid duplicates

        # Calculate offset to center waypoints in grid cells
        grid_center_offset = self.grid_size // 2

        # Phase 1: Horizontal sweeps (left-right, alternating)
        y = self.boundary_buffer + grid_center_offset
        going_right = True

        while y < self.world_height - self.boundary_buffer:
            if going_right:
                # Sweep right
                x = self.boundary_buffer + grid_center_offset
                while x < self.world_width - self.boundary_buffer:
                    pos = (x, y)
                    # Only add waypoint if not visited AND safe from hazards
                    if pos not in visited_positions and self.is_waypoint_safe(x, y):
                        waypoints.append(pos)
                        visited_positions.add(pos)
                    x += self.grid_size
            else:
                # Sweep left
                x = self.world_width - self.boundary_buffer - grid_center_offset
                while x > self.boundary_buffer:
                    pos = (x, y)
                    # Only add waypoint if not visited AND safe from hazards
                    if pos not in visited_positions and self.is_waypoint_safe(x, y):
                        waypoints.append(pos)
                        visited_positions.add(pos)
                    x -= self.grid_size

            going_right = not going_right
            y += self.grid_size

        # Phase 2: Vertical sweeps (up-down, alternating)
        x = self.boundary_buffer + grid_center_offset
        going_down = True

        while x < self.world_width - self.boundary_buffer:
            if going_down:
                # Sweep down
                y = self.boundary_buffer + grid_center_offset
                while y < self.world_height - self.boundary_buffer:
                    pos = (x, y)
                    # Only add waypoint if not visited AND safe from hazards
                    if pos not in visited_positions and self.is_waypoint_safe(x, y):
                        waypoints.append(pos)
                        visited_positions.add(pos)
                    y += self.grid_size
            else:
                # Sweep up
                y = self.world_height - self.boundary_buffer - grid_center_offset
                while y > self.boundary_buffer:
                    pos = (x, y)
                    # Only add waypoint if not visited AND safe from hazards
                    if pos not in visited_positions and self.is_waypoint_safe(x, y):
                        waypoints.append(pos)
                        visited_positions.add(pos)
                    y -= self.grid_size

            going_down = not going_down
            x += self.grid_size

        return waypoints

    def start_survey(self):
        """Start the autonomous survey"""
        if self.survey_active:
            return

        # Generate complete serpentine scan
        scan_waypoints = self.generate_serpentine_scan()

        if scan_waypoints:
            # Start with current rover position
            self.grid_waypoints = []

            # If rover is not already at the first scan waypoint, add intermediate waypoints
            first_scan_x, first_scan_y = scan_waypoints[0]
            distance_to_start = math.sqrt((first_scan_x - self.rover.x)**2 + (first_scan_y - self.rover.y)**2)

            if distance_to_start > 50:  # If far from start, generate Manhattan path (left then up)
                # Calculate horizontal and vertical distances
                delta_x = first_scan_x - self.rover.x
                delta_y = first_scan_y - self.rover.y

                # Phase 1: Move horizontally (left/right) with waypoints every ~200 pixels
                if abs(delta_x) > 50:
                    num_horizontal = max(1, int(abs(delta_x) / 200))
                    for i in range(1, num_horizontal + 1):
                        t = i / num_horizontal
                        waypoint_x = self.rover.x + delta_x * t
                        waypoint_y = self.rover.y  # Keep Y constant during horizontal movement
                        self.grid_waypoints.append((waypoint_x, waypoint_y))

                # Phase 2: Move vertically (up/down) with waypoints every ~200 pixels
                if abs(delta_y) > 50:
                    num_vertical = max(1, int(abs(delta_y) / 200))
                    for i in range(1, num_vertical + 1):
                        t = i / num_vertical
                        waypoint_x = first_scan_x  # Already at target X from Phase 1
                        waypoint_y = self.rover.y + delta_y * t
                        self.grid_waypoints.append((waypoint_x, waypoint_y))

            # Add all the scan waypoints
            self.grid_waypoints.extend(scan_waypoints)

            self.survey_active = True
            self.grid_following = True
            self.grid_waypoint_index = 0
            self.survey_phase = "horizontal"
            self.original_grid_path = self.grid_waypoints.copy()
            self.avoiding_obstacle = False

            # Calculate how many navigation waypoints were added
            num_nav_waypoints = len(self.grid_waypoints) - len(scan_waypoints)
            print(f"Starting survey with {len(self.grid_waypoints)} waypoints (including {num_nav_waypoints} navigation waypoints)")
        else:
            print("Failed to generate survey path")

    def stop_survey(self):
        """Stop the survey and return to base"""
        self.survey_active = False
        self.grid_following = False
        self.grid_waypoints = []
        self.grid_waypoint_index = 0
        self.avoiding_obstacle = False
        self.avoidance_waypoints = []

        # Start autopilot to return to base
        self.start_return_to_base()
        print("Survey stopped - returning to base")

    def check_battery_for_return(self):
        """Check if rover has enough battery to return to base"""
        if not self.survey_active:
            return False

        # Calculate distance to base
        distance_to_base = math.sqrt((self.rover.x - self.base_x)**2 + (self.rover.y - self.base_y)**2)

        # Estimate battery needed (rough calculation)
        # Battery drains at ~1 second per second of movement
        # Estimate time to reach base at average speed (rough: distance / 50 pixels per second)
        estimated_travel_time = distance_to_base / 50.0  # seconds
        battery_needed = estimated_travel_time * 1.2  # Add 20% safety margin

        # If current battery is below threshold or below needed amount, return
        if self.battery_level <= self.battery_threshold_for_return or self.battery_level <= battery_needed:
            return True

        return False

    def start_navigation_to_resume_position(self):
        """Navigate directly back to the saved resume position"""
        if not self.resume_position:
            print("No resume position saved!")
            return

        resume_x, resume_y = self.resume_position
        print(f"Calculating path to resume position ({resume_x:.1f}, {resume_y:.1f})...")

        # Use the pathfinding system to navigate to resume position
        path = self.calculate_path_to_position(resume_x, resume_y)

        if path:
            self.autopilot_path = path
            self.autopilot_active = True
            self.autopilot_waypoint_index = 0
            self.returning_to_resume = True

            # Enable GPR for scanning during navigation
            self.autopilot_gpr_enabled = self.gpr_system.active  # Save current state
            if not self.gpr_system.active:
                self.gpr_system.active = True
                print("GPR enabled for waypoint scanning")

            print(f"Autopilot engaged! Following {len(path)} waypoints to resume position.")
        else:
            print("Could not find path to resume position!")

    def calculate_path_to_position(self, target_x, target_y):
        """Calculate a path from rover to a target position avoiding keep-out zones"""
        # Check if direct path is clear
        if self.is_path_clear(self.rover.x, self.rover.y, target_x, target_y):
            return [(target_x, target_y)]

        # If not clear, use simple waypoint navigation around obstacles
        # Try cardinal directions as intermediate waypoints
        waypoints = []

        # Try going via a point to the side
        mid_x = (self.rover.x + target_x) / 2
        mid_y = (self.rover.y + target_y) / 2

        # Try multiple intermediate points, prioritizing explored areas
        best_path = None
        best_score = float('inf')

        for offset in [(100, 0), (-100, 0), (0, 100), (0, -100), (100, 100), (-100, -100)]:
            test_x = mid_x + offset[0]
            test_y = mid_y + offset[1]

            if (self.is_path_clear(self.rover.x, self.rover.y, test_x, test_y) and
                self.is_path_clear(test_x, test_y, target_x, target_y)):

                # Calculate score (lower is better)
                score = math.sqrt((test_x - target_x)**2 + (test_y - target_y)**2)

                # Prefer explored areas - give 30% better score if near rover's trail
                if self.is_area_explored(test_x, test_y, radius=50):
                    score *= 0.7

                if score < best_score:
                    best_score = score
                    best_path = [(test_x, test_y), (target_x, target_y)]

        if best_path:
            return best_path

        # If no path found, return direct path anyway
        return [(target_x, target_y)]

    def update_grid_following(self):
        """Update grid following navigation with Manhattan-style (horizontal/vertical) movement"""
        if not self.grid_waypoints or self.grid_waypoint_index >= len(self.grid_waypoints):
            print("Grid navigation complete!")
            self.stop_grid_following()
            return

        # Determine current target waypoint based on whether we're avoiding obstacle
        if self.avoiding_obstacle and self.avoidance_waypoints:
            if self.avoidance_waypoint_index >= len(self.avoidance_waypoints):
                # Detour complete, return to grid following
                print("Detour complete, resuming grid path")
                self.avoiding_obstacle = False
                self.avoidance_waypoints = []
                self.avoidance_waypoint_index = 0
                self.grid_waypoint_index += 1  # Move to next grid waypoint
                return
            # Follow detour waypoint
            target_x, target_y = self.avoidance_waypoints[self.avoidance_waypoint_index]
            # Check if reached detour waypoint
            dx = target_x - self.rover.x
            dy = target_y - self.rover.y
            distance = math.sqrt(dx*dx + dy*dy)
            if distance < 50:
                self.avoidance_waypoint_index += 1
                return
        else:
            # Get current target waypoint from grid
            target_x, target_y = self.grid_waypoints[self.grid_waypoint_index]
            # Store this as the current target for collision recovery
            # (moved this assignment outside the if/else for clarity)

        # Calculate direction to waypoint
        dx = target_x - self.rover.x
        dy = target_y - self.rover.y
        distance = math.sqrt(dx*dx + dy*dy)

        # Check if reached waypoint (relaxed threshold for smoother navigation)
        if distance < 50:
            self.grid_waypoint_index += 1
            self.grid_stuck_counter = 0  # Reset stuck counter at waypoints
            if self.grid_waypoint_index >= len(self.grid_waypoints):
                print("Grid navigation complete!")
                self.stop_grid_following()
            return

        # Decrement cooldown timer
        if self.grid_collision_cooldown > 0:
            self.grid_collision_cooldown -= 1

        # PROACTIVE hazard detection: Check if rover is about to hit keep-out zone
        # Look ahead in the direction we're moving to detect hazards early
        if (not self.grid_collision_state and
            not self.avoiding_obstacle and
            self.grid_collision_cooldown == 0 and
            abs(self.rover.speed) > 0.5):

            # Look ahead based on current trajectory
            lookahead_distance = 40  # Look 40 pixels ahead
            rad = math.radians(self.rover.angle)
            lookahead_x = self.rover.x + lookahead_distance * math.cos(rad)
            lookahead_y = self.rover.y + lookahead_distance * math.sin(rad)

            # Check if lookahead position would collide with any hazard keep-out zone
            for hazard in self.hazards:
                # Only check discovered hazards
                if hasattr(hazard, 'discovered') and not hazard.discovered:
                    continue

                dx = lookahead_x - hazard.x
                dy = lookahead_y - hazard.y
                distance = math.sqrt(dx * dx + dy * dy)

                # Keep-out radius = hazard radius + rover collision radius
                keepout_radius = hazard.radius + self.rover.collision_radius

                if distance < keepout_radius:
                    print(f"Hazard approaching! Preemptive backup initiated.")
                    print("Starting immediate backup sequence...")
                    self.grid_collision_state = 'pause_before'
                    self.grid_collision_pause_frames = 0
                    self.grid_backup_distance = 0
                    self.grid_original_waypoint = (target_x, target_y)
                    self.grid_collision_cooldown = 120  # 2 second cooldown (60fps * 2)
                    self.rover.speed = 0  # Stop immediately
                    return

        # FALLBACK: Detect hazard collision via rover's collision warning system (if proactive check missed)
        # When rover hits hazard, Phase 5 sets collision_warning = True
        # Only trigger if not in collision state, not avoiding, and cooldown expired
        if (self.rover.collision_warning and
            not self.grid_collision_state and
            not self.avoiding_obstacle and
            self.grid_collision_cooldown == 0):
            print(f"Hazard collision detected! Speed dropped to {self.rover.speed:.2f}")
            print("Starting immediate backup sequence...")
            self.grid_collision_state = 'pause_before'
            self.grid_collision_pause_frames = 0
            self.grid_backup_distance = 0
            self.grid_original_waypoint = (target_x, target_y)
            self.grid_collision_cooldown = 120  # 2 second cooldown (60fps * 2)
            self.rover.speed = 0  # Stop immediately
            return

        # Detect if stuck (not making progress) - active at ALL distances (removed dead zone)
        if self.grid_last_position and not self.grid_collision_state and not self.avoiding_obstacle:
            last_x, last_y = self.grid_last_position
            movement = math.sqrt((self.rover.x - last_x)**2 + (self.rover.y - last_y)**2)

            # Check if rover is trying to move but not making progress
            # Stuck = speed > 1.0 but movement < 1.5 (trying to move but can't)
            # OR movement < 0.5 regardless of speed (completely stuck)
            is_stuck = (self.rover.speed > 1.0 and movement < 1.5) or (movement < 0.5)

            if is_stuck:
                self.grid_stuck_counter += 1
                if self.grid_stuck_counter % 5 == 0:  # Debug output every 5 frames
                    print(f"Stuck counter: {self.grid_stuck_counter} (movement: {movement:.2f}px, speed: {self.rover.speed:.2f})")
            else:
                self.grid_stuck_counter = 0
        else:
            # Reset stuck counter when in collision state or avoiding obstacle
            self.grid_stuck_counter = 0

        self.grid_last_position = (self.rover.x, self.rover.y)

        # If stuck for 15 frames (~0.25 seconds), start collision recovery sequence (very aggressive)
        if self.grid_stuck_counter > 15 and not self.grid_collision_state and not self.avoiding_obstacle:
            print("Grid navigation stuck! Starting collision recovery...")
            self.grid_collision_state = 'pause_before'
            self.grid_collision_pause_frames = 0
            self.grid_backup_distance = 0
            self.grid_original_waypoint = (target_x, target_y)  # Remember where we were going
            self.rover.speed = 0  # Stop immediately
            return

        # Handle collision recovery sequence: pause -> backup -> pause -> try alternate angles
        if self.grid_collision_state:
            if self.grid_collision_state == 'pause_before':
                # Pause for 0.1 seconds (6 frames at 60fps)
                self.rover.speed = 0
                self.grid_collision_pause_frames += 1
                if self.grid_collision_pause_frames >= 6:
                    print("Backing up 2 meters...")
                    self.grid_collision_state = 'backing_up'
                    self.grid_collision_pause_frames = 0
                return

            elif self.grid_collision_state == 'backing_up':
                # Back up at full speed for 2 meters (much shorter)
                backup_angle = self.rover.angle + 180
                self.rover.angle = backup_angle % 360
                self.rover.speed = min(self.rover.speed + 0.5, self.rover.max_speed)  # Accelerate even faster
                self.grid_backup_distance += abs(self.rover.speed)

                # Backup for 2 meters (200 pixels) - much shorter distance
                if self.grid_backup_distance >= 200:
                    print("Backup complete! Pausing before route calculation...")
                    self.grid_collision_state = 'pause_after'
                    self.grid_collision_pause_frames = 0
                    self.rover.speed = 0
                return

            elif self.grid_collision_state == 'pause_after':
                # Pause for 0.1 seconds (6 frames at 60fps)
                self.rover.speed = 0
                self.grid_collision_pause_frames += 1
                if self.grid_collision_pause_frames >= 6:
                    print("Collision recovery complete, resuming navigation...")
                    self.grid_collision_state = None
                    self.grid_collision_pause_frames = 0
                    self.grid_backup_distance = 0
                    self.grid_stuck_counter = 0

                    # Try ±45° angles to get around obstacle
                    if self.grid_original_waypoint:
                        self.try_alternate_angles_to_waypoint(self.grid_original_waypoint)

                    # CRITICAL: Recalculate target after collision recovery
                    # The old target_x, target_y, dx, dy, distance are stale
                    if self.avoiding_obstacle and self.avoidance_waypoints:
                        target_x, target_y = self.avoidance_waypoints[self.avoidance_waypoint_index]
                    else:
                        target_x, target_y = self.grid_waypoints[self.grid_waypoint_index]

                    dx = target_x - self.rover.x
                    dy = target_y - self.rover.y
                    distance = math.sqrt(dx*dx + dy*dy)

                    # Don't return - let navigation continue in this frame
                    # Fall through to normal navigation code below
                else:
                    # Still pausing, return and wait
                    return
                # If pause is done, continue to navigation code below (don't return)

        # Manhattan-style movement: prioritize horizontal movement first, then vertical
        # This makes the rover move in straight lines along grid axes
        horizontal_threshold = 20  # Pixels tolerance for being "on" a horizontal line

        # When very close to waypoint (within 80 pixels), use direct angle for smoother final approach
        if distance < 80:
            target_angle = math.degrees(math.atan2(dy, dx))
        # Determine target angle based on which axis has larger delta
        elif abs(dx) > horizontal_threshold:
            # Move horizontally (left or right)
            if dx > 0:
                target_angle = 0  # Right (East)
            else:
                target_angle = 180  # Left (West)
        elif abs(dy) > horizontal_threshold:
            # Move vertically (up or down)
            if dy > 0:
                target_angle = 90  # Down (South)
            else:
                target_angle = 270  # Up (North)
        else:
            # Very close, just point directly at target
            target_angle = math.degrees(math.atan2(dy, dx))

        # Normalize angles
        current_angle = self.rover.angle % 360
        target_angle = target_angle % 360

        # Calculate angle difference
        angle_diff = target_angle - current_angle
        if angle_diff > 180:
            angle_diff -= 360
        elif angle_diff < -180:
            angle_diff += 360

        # Adjust heading
        turn_speed = 3.0  # Slightly faster turning for grid movement
        if abs(angle_diff) > turn_speed:
            if angle_diff > 0:
                self.rover.angle += turn_speed
            else:
                self.rover.angle -= turn_speed
        else:
            self.rover.angle = target_angle

        # Move forward only when roughly facing the right direction
        if abs(angle_diff) < 15:  # Within 15 degrees of target
            self.rover.speed = min(self.rover.speed + 0.15, self.rover.max_speed)
        elif abs(angle_diff) < 30:  # Within 30 degrees, still move but slower
            self.rover.speed = min(self.rover.speed + 0.1, self.rover.max_speed * 0.8)
        else:
            # Slow down while turning (0.6x instead of 0.3x for faster cornering)
            self.rover.speed = max(self.rover.speed - 0.1, self.rover.max_speed * 0.6)

    def try_alternate_angles_to_waypoint(self, target_waypoint):
        """Try ±45° angles to get around obstacle, then return to grid line"""
        target_x, target_y = target_waypoint

        # Calculate current direction to target
        dx = target_x - self.rover.x
        dy = target_y - self.rover.y
        direct_angle = math.degrees(math.atan2(dy, dx))

        # Try ±45° from current direction
        for angle_offset in [45, -45]:
            test_angle = direct_angle + angle_offset
            test_distance = 300  # Try to move 300 pixels at angle

            # Calculate test position
            test_x = self.rover.x + test_distance * math.cos(math.radians(test_angle))
            test_y = self.rover.y + test_distance * math.sin(math.radians(test_angle))

            # Check if path is clear
            if self.is_path_clear(self.rover.x, self.rover.y, test_x, test_y):
                # Found clear path at this angle
                print(f"Found clear path at {angle_offset:+d}°")

                # Create detour: go around obstacle, then return to grid line
                detour_waypoints = []

                # Step 1: Move at angle to avoid obstacle
                detour_waypoints.append((test_x, test_y))

                # Step 2: Return to original grid line (align with target X or Y)
                # Determine if we're on a horizontal or vertical sweep
                if abs(dx) > abs(dy):
                    # Horizontal sweep - return to target Y, keep new X
                    detour_waypoints.append((test_x, target_y))
                else:
                    # Vertical sweep - return to target X, keep new Y
                    detour_waypoints.append((target_x, test_y))

                # Step 3: Continue to original target
                detour_waypoints.append((target_x, target_y))

                # Use avoidance waypoints instead of modifying grid_waypoints
                self.avoiding_obstacle = True
                self.avoidance_waypoints = detour_waypoints
                self.avoidance_waypoint_index = 0

                print(f"Taking detour with {len(detour_waypoints)} waypoints")
                return

        # No clear path found, skip this waypoint
        print("No clear path found, skipping to next waypoint")
        self.grid_waypoint_index += 1

    def find_detour_to_waypoint(self, target_x, target_y):
        """Find a detour around obstacles to reach target waypoint"""
        # Try angles around the obstacle
        detour_angles = [45, -45, 90, -90, 135, -135]
        detour_distance = 150  # Distance to move around obstacle

        for angle_offset in detour_angles:
            # Calculate detour point
            angle = math.atan2(target_y - self.rover.y, target_x - self.rover.x) + math.radians(angle_offset)
            detour_x = self.rover.x + math.cos(angle) * detour_distance
            detour_y = self.rover.y + math.sin(angle) * detour_distance

            # Check if detour point is clear and then path to target is clear
            if self.is_path_clear(self.rover.x, self.rover.y, detour_x, detour_y):
                if self.is_path_clear(detour_x, detour_y, target_x, target_y):
                    return [(detour_x, detour_y)]

        return None

    def enforce_world_boundaries(self):
        """Keep rover within world boundaries"""
        if not self.enable_boundaries:
            return

        # Check and constrain X position
        if self.rover.x < self.boundary_buffer:
            self.rover.x = self.boundary_buffer
            self.rover.speed = 0
        elif self.rover.x > self.world_width - self.boundary_buffer:
            self.rover.x = self.world_width - self.boundary_buffer
            self.rover.speed = 0

        # Check and constrain Y position
        if self.rover.y < self.boundary_buffer:
            self.rover.y = self.boundary_buffer
            self.rover.speed = 0
        elif self.rover.y > self.world_height - self.boundary_buffer:
            self.rover.y = self.world_height - self.boundary_buffer
            self.rover.speed = 0

    def update(self):
        """Update game state with Phase 8 features"""
        # Check battery level during survey
        if self.survey_active and not self.autopilot_active and not self.returning_to_resume:
            if self.check_battery_for_return():
                print("Battery low! Returning to base to recharge...")
                # Save current position to resume later
                self.resume_position = (self.rover.x, self.rover.y)
                print(f"Saved resume position: ({self.rover.x:.1f}, {self.rover.y:.1f})")
                self.grid_following = False  # Pause grid following
                self.start_return_to_base()

        # Handle grid following before parent update
        if self.grid_following:
            self.update_grid_following()

        # Call parent update
        super().update()

        # If survey was paused for battery and we're now at base and fully charged, navigate to resume position
        if self.survey_active and not self.grid_following and not self.autopilot_active and not self.returning_to_resume:
            # Check if at base and fully charged
            distance_to_base = math.sqrt((self.rover.x - self.base_x)**2 + (self.rover.y - self.base_y)**2)
            # Battery capacity is 240 seconds, so 95% is 228 seconds
            if distance_to_base < 100 and self.battery_level >= 228.0 and self.resume_position:
                # Navigate directly back to resume position
                print(f"Battery recharged! Navigating to resume position ({self.resume_position[0]:.1f}, {self.resume_position[1]:.1f})...")
                self.start_navigation_to_resume_position()

        # Check if we've reached the resume position
        if self.returning_to_resume and not self.autopilot_active and self.resume_position:
            # Autopilot has completed - check if we're close to resume position
            resume_x, resume_y = self.resume_position
            distance_to_resume = math.sqrt((self.rover.x - resume_x)**2 + (self.rover.y - resume_y)**2)
            if distance_to_resume < 100:  # Within 100 pixels is close enough
                print("Reached resume position! Resuming survey...")
                self.returning_to_resume = False
                self.resume_position = None
                self.grid_following = True

        # Enforce world boundaries after movement
        self.enforce_world_boundaries()

    def draw(self):
        """Enhanced drawing with Phase 8 features - call parent then add Phase 8 overlays"""
        try:
            # Import Phase6Game to use its draw method
            from .phase6_extended import Phase6Game

            # Call Phase 6's draw (which calls our overridden draw_bottom_controls_panel)
            Phase6Game.draw(self)

            # Draw grid overlay on top
            self.draw_grid()

            # Draw grid waypoints if survey is active (show even when paused for battery)
            if self.survey_active and self.grid_waypoints:
                for i, (wx, wy) in enumerate(self.grid_waypoints):
                    screen_pos = self.camera.apply(wx, wy)
                    if 0 <= screen_pos[0] <= self.width and 0 <= screen_pos[1] <= self.height:
                        if i == self.grid_waypoint_index:
                            # Current waypoint: filled bright green
                            pygame.draw.circle(self.screen, (0, 255, 0), screen_pos, 6)
                        elif i < self.grid_waypoint_index:
                            # Visited waypoints: hollow gray circle
                            pygame.draw.circle(self.screen, (150, 150, 150), screen_pos, 4, 2)
                        else:
                            # Future waypoints: filled cyan
                            pygame.draw.circle(self.screen, (0, 200, 200), screen_pos, 4)

            # Draw detour waypoints
            if self.avoiding_obstacle and self.avoidance_waypoints:
                for (wx, wy) in self.avoidance_waypoints:
                    screen_pos = self.camera.apply(wx, wy)
                    if 0 <= screen_pos[0] <= self.width and 0 <= screen_pos[1] <= self.height:
                        pygame.draw.circle(self.screen, (255, 165, 0), screen_pos, 8, 2)

            # Update display after all Phase 8 drawing is complete
            # Call parent's display_update which we didn't override
            from .phase6_extended import Phase6Game
            Phase6Game.display_update(self)

        except Exception as e:
            # If anything fails, print error and show black screen
            print(f"Draw error: {e}")
            import traceback
            traceback.print_exc()

    def display_update(self):
        """Override to prevent Phase 6's draw from flipping display prematurely"""
        # Do nothing - we'll call parent's display_update manually at end of our draw
        pass

    def draw_status_panel_ui(self):
        """Override: Draw status panel with Survey button"""
        # Call parent to draw the main status panel
        super().draw_status_panel_ui()

        # Add Survey button next to Reset button
        # Find where the reset button is (we need to read parent's button position)
        # The reset button is drawn at the bottom of the status panel
        # Let's add our button next to it

        small_font = pygame.font.Font(None, 24)

        # Survey button - place it next to reset button
        # Reset button is at (30, button_y) with width 120
        # We'll place survey button at (160, button_y) with width 140

        # We need to calculate button_y the same way parent does
        # Parent calculates it based on y_offset after status items
        # For simplicity, we'll place it at a fixed position that aligns with reset button
        # The reset button appears around y=240 based on the panel height
        button_y = 240

        survey_button_x = 160
        survey_button_width = 140
        button_height = 30

        self.survey_button_rect = pygame.Rect(survey_button_x, button_y, survey_button_width, button_height)

        # Button color based on state
        if self.survey_active:
            button_color = (120, 40, 40)  # Red when active
            border_color = (200, 100, 100)
            button_text_str = "STOP SURVEY"
        else:
            button_color = (40, 100, 40)  # Green when inactive
            border_color = (100, 200, 100)
            button_text_str = "START SURVEY"

        # Draw button
        pygame.draw.rect(self.screen, button_color, self.survey_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, border_color, self.survey_button_rect, 2, border_radius=5)

        # Button text
        button_text = small_font.render(button_text_str, True, (255, 255, 255))
        text_rect = button_text.get_rect(center=self.survey_button_rect.center)
        self.screen.blit(button_text, text_rect)

        # Draw confirmation dialog if needed
        if self.show_stop_confirmation:
            self.draw_stop_confirmation_dialog()

    def draw_stop_confirmation_dialog(self):
        """Draw a confirmation dialog for stopping the survey"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_width = 400
        dialog_height = 150
        dialog_x = (self.width - dialog_width) // 2
        dialog_y = (self.height - dialog_height) // 2

        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(self.screen, (40, 50, 60), dialog_rect, border_radius=10)
        pygame.draw.rect(self.screen, (150, 180, 200), dialog_rect, 3, border_radius=10)

        # Title
        title_font = pygame.font.Font(None, 32)
        title = title_font.render("Stop Survey?", True, (255, 255, 255))
        title_rect = title.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + 30))
        self.screen.blit(title, title_rect)

        # Message
        msg_font = pygame.font.Font(None, 22)
        msg = msg_font.render("Return to base? Unsaved progress will be lost.", True, (200, 200, 200))
        msg_rect = msg.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + 70))
        self.screen.blit(msg, msg_rect)

        # Yes button
        button_width = 100
        button_height = 35
        yes_x = dialog_x + 80
        button_y = dialog_y + 100

        self.confirmation_yes_rect = pygame.Rect(yes_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (100, 40, 40), self.confirmation_yes_rect, border_radius=5)
        pygame.draw.rect(self.screen, (200, 100, 100), self.confirmation_yes_rect, 2, border_radius=5)

        yes_text = msg_font.render("YES", True, (255, 255, 255))
        yes_rect = yes_text.get_rect(center=self.confirmation_yes_rect.center)
        self.screen.blit(yes_text, yes_rect)

        # No button
        no_x = dialog_x + 220
        self.confirmation_no_rect = pygame.Rect(no_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (40, 100, 40), self.confirmation_no_rect, border_radius=5)
        pygame.draw.rect(self.screen, (100, 200, 100), self.confirmation_no_rect, 2, border_radius=5)

        no_text = msg_font.render("NO", True, (255, 255, 255))
        no_rect = no_text.get_rect(center=self.confirmation_no_rect.center)
        self.screen.blit(no_text, no_rect)

    def draw_bottom_controls_panel(self):
        """Override: Draw Phase 8 bottom control panel with grid navigation controls"""
        # Control panel at bottom
        panel_height = 190
        panel_y = self.height - panel_height
        ui_panel = pygame.Rect(0, panel_y, self.width, panel_height)
        pygame.draw.rect(self.screen, (25, 35, 45), ui_panel)

        # Draw a top border
        pygame.draw.line(self.screen, (80, 120, 160), (0, panel_y), (self.width, panel_y), 3)

        # Title - just say "Controls"
        title_font = pygame.font.Font(None, 32)
        title = title_font.render("Controls", True, (100, 200, 255))
        self.screen.blit(title, (25, panel_y + 12))

        # Subtitle / Status
        subtitle_font = pygame.font.Font(None, 20)
        if self.grid_following:
            # Show current waypoint as index+1 for human-readable count (1-based instead of 0-based)
            current_waypoint = self.grid_waypoint_index + 1
            total_waypoints = len(self.grid_waypoints)
            progress_pct = int((self.grid_waypoint_index/total_waypoints)*100) if total_waypoints > 0 else 0
            subtitle_text = f"ACTIVE - Progress: {current_waypoint}/{total_waypoints} waypoints ({progress_pct}%)"
            subtitle_color = (100, 255, 150)
        elif self.autopilot_active and self.autopilot_path:
            # Show autopilot progress when navigating (return to base or resume)
            current_waypoint = self.autopilot_waypoint_index + 1
            total_waypoints = len(self.autopilot_path)
            progress_pct = int((self.autopilot_waypoint_index/total_waypoints)*100) if total_waypoints > 0 else 0
            nav_mode = "Returning to base" if not self.returning_to_resume else "Navigating to resume position"
            subtitle_text = f"{nav_mode} - Progress: {current_waypoint}/{total_waypoints} waypoints ({progress_pct}%)"
            subtitle_color = (255, 200, 100)
        else:
            subtitle_text = "Autonomous grid surveying with exploration discovery system"
            subtitle_color = (180, 200, 220)

        subtitle = subtitle_font.render(subtitle_text, True, subtitle_color)
        self.screen.blit(subtitle, (25, panel_y + 42))

        # Controls - organized in 3 columns
        controls_y = panel_y + 70
        controls_font = pygame.font.Font(None, 19)

        # Column 1: Movement
        col1_x = 25
        header1 = controls_font.render("Movement:", True, (150, 200, 255))
        self.screen.blit(header1, (col1_x, controls_y))

        move_controls = [
            "WASD - Move",
            "R - Return to Base"
        ]
        for i, ctrl in enumerate(move_controls):
            text = controls_font.render(ctrl, True, (200, 220, 240))
            self.screen.blit(text, (col1_x, controls_y + 20 + i*18))

        # Column 2: Grid Navigation
        col2_x = 280
        header2 = controls_font.render("Grid Navigation:", True, (100, 255, 200))
        self.screen.blit(header2, (col2_x, controls_y))

        grid_controls = [
            "M - Toggle Grid Display"
        ]
        for i, ctrl in enumerate(grid_controls):
            text = controls_font.render(ctrl, True, (200, 220, 240))
            self.screen.blit(text, (col2_x, controls_y + 20 + i*18))

        # Column 3: Exploration
        col3_x = 600
        header3 = controls_font.render("Exploration:", True, (255, 200, 100))
        self.screen.blit(header3, (col3_x, controls_y))

        explore_controls = [
            "G - Toggle GPR",
            "P - Excavate",
            "K - Keep-Out Zones",
            "E - Exploration Stats"
        ]
        for i, ctrl in enumerate(explore_controls):
            text = controls_font.render(ctrl, True, (200, 220, 240))
            self.screen.blit(text, (col3_x, controls_y + 20 + i*18))

        # Column 4: Other
        col4_x = 900
        header4 = controls_font.render("Other:", True, (200, 200, 200))
        self.screen.blit(header4, (col4_x, controls_y))

        other_controls = [
            "C - Clear Sites",
            "Q/E - Scroll Catalog",
            "ESC - Exit"
        ]
        for i, ctrl in enumerate(other_controls):
            text = controls_font.render(ctrl, True, (200, 220, 240))
            self.screen.blit(text, (col4_x, controls_y + 20 + i*18))

    def handle_events(self):
        """Override: Handle events including survey button clicks"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    # Check if confirmation dialog is open (highest priority)
                    if self.show_stop_confirmation:
                        if self.confirmation_yes_rect and self.confirmation_yes_rect.collidepoint(mouse_x, mouse_y):
                            # User confirmed stop
                            self.show_stop_confirmation = False
                            self.stop_survey()
                        elif self.confirmation_no_rect and self.confirmation_no_rect.collidepoint(mouse_x, mouse_y):
                            # User cancelled
                            self.show_stop_confirmation = False
                        else:
                            # Clicked outside dialog, close it
                            self.show_stop_confirmation = False
                        continue

                    # Check if survey button was clicked (UI element) - before parent checks
                    if hasattr(self, 'survey_button_rect') and self.survey_button_rect and self.survey_button_rect.collidepoint(mouse_x, mouse_y):
                        if self.survey_active:
                            # Show confirmation dialog
                            self.show_stop_confirmation = True
                        else:
                            # Start survey
                            self.start_survey()
                        continue

                    # Check if artifact display is open (UI element)
                    if self.artifact_display:
                        self.artifact_display = None
                        continue

                    # Check if reset button was clicked (UI element)
                    if hasattr(self, 'reset_button_rect') and self.reset_button_rect.collidepoint(mouse_x, mouse_y):
                        self.reset_game()
                        continue

                    # Check if clicking on artifact catalog (UI element)
                    if self.handle_catalog_click(mouse_x, mouse_y):
                        continue

                    # Convert screen coordinates to world coordinates for gameplay clicks
                    world_x, world_y = self.camera.reverse(mouse_x, mouse_y)

                    # Check for excavation clicks first
                    if self.handle_excavation_click_world(world_x, world_y):
                        continue

                    # Create dig sites anywhere on the map (but not in hazards)
                    can_place = True
                    for hazard in self.hazards:
                        if math.sqrt((hazard.x - world_x)**2 + (hazard.y - world_y)**2) < 60:
                            can_place = False
                            break

                    if can_place:
                        new_site = self.create_dig_site(world_x, world_y)
                        self.dig_sites.append(new_site)
                        self.next_site_id += 1

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

        return True

    def handle_keydown(self, event):
        """Handle keyboard input with Phase 8 specific controls"""
        # Handle Phase 8 specific keys first
        if event.key == pygame.K_m:
            # Toggle grid display
            self.show_grid = not self.show_grid
            return

        # Block debugging keys (N and H) - disabled in Phase 8
        if event.key == pygame.K_n or event.key == pygame.K_h:
            # Debugging keys disabled in Phase 8
            return

        # Handle all other keys from parent (ESC, C, G, Q, E, P, K, R, etc.)
        if event.key == pygame.K_ESCAPE:
            return False
        elif event.key == pygame.K_c:
            self.dig_sites = []
        elif event.key == pygame.K_g:
            self.gpr_system.active = not self.gpr_system.active
        elif event.key == pygame.K_q:
            # Scroll up in artifact catalog
            self.artifact_catalog.scroll_up()
        elif event.key == pygame.K_e:
            # Scroll down in artifact catalog - but Phase 7 uses E for exploration stats
            # Let's check if we're in Phase 7 mode
            if hasattr(self, 'show_discovery_stats'):
                # Phase 7 - toggle exploration stats
                self.show_discovery_stats = not self.show_discovery_stats
            else:
                # Phase 6 - scroll catalog
                self.artifact_catalog.scroll_down()
        elif event.key == pygame.K_p:
            # Excavate nearby dig site
            if self.excavate_nearby_site():
                print("Excavation started!")
        elif event.key == pygame.K_k:
            # Toggle keep-out zone visualization
            self.show_keepout_zones = not self.show_keepout_zones
        elif event.key == pygame.K_r:
            # Return to base
            if not self.autopilot_active:
                self.start_return_to_base()
            else:
                self.cancel_autopilot()

    def reset_game(self):
        """Reset game including grid navigation and survey"""
        super().reset_game()
        self.stop_grid_following()
        self.survey_active = False
        self.show_stop_confirmation = False
