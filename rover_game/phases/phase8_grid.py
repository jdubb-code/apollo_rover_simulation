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

        # In Phase 8, all hazards are visible from the start (no exploration mechanic)
        for hazard in self.hazards:
            if hasattr(hazard, 'discovered'):
                hazard.discovered = True  # Make all exploration hazards visible

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

        # World boundaries (make world finite)
        self.enable_boundaries = True
        self.boundary_buffer = 50  # Keep rover this far from edge

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
                    waypoints.append((x, y))
            else:
                # Sweep left
                for x in range(self.world_width - self.boundary_buffer, self.boundary_buffer, -self.grid_size):
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
                    waypoints.append((x, y))
            else:
                # Sweep up
                for y in range(self.world_height - self.boundary_buffer, self.boundary_buffer, -self.grid_size):
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

    def update_grid_following(self):
        """Update grid following navigation with obstacle avoidance"""
        if not self.grid_waypoints or self.grid_waypoint_index >= len(self.grid_waypoints):
            print("Grid navigation complete!")
            self.stop_grid_following()
            return

        # Get current target waypoint
        target_x, target_y = self.grid_waypoints[self.grid_waypoint_index]

        # Calculate direction to waypoint
        dx = target_x - self.rover.x
        dy = target_y - self.rover.y
        distance = math.sqrt(dx*dx + dy*dy)

        # Check if reached waypoint
        if distance < 30:
            self.grid_waypoint_index += 1
            if self.grid_waypoint_index >= len(self.grid_waypoints):
                print("Grid navigation complete!")
                self.stop_grid_following()
            return

        # Check if path to waypoint is clear
        if not self.is_path_clear(self.rover.x, self.rover.y, target_x, target_y):
            # Obstacle detected, need to go around
            if not self.avoiding_obstacle:
                print("Obstacle detected on grid path, finding detour...")
                self.avoiding_obstacle = True
                detour = self.find_detour_to_waypoint(target_x, target_y)
                if detour:
                    self.avoidance_waypoints = detour
                else:
                    # Can't find detour, skip to next waypoint
                    print("No detour found, skipping waypoint")
                    self.grid_waypoint_index += 1
                    self.avoiding_obstacle = False
                    return

        # If avoiding obstacle, follow detour waypoints
        if self.avoiding_obstacle and self.avoidance_waypoints:
            detour_x, detour_y = self.avoidance_waypoints[0]
            dx = detour_x - self.rover.x
            dy = detour_y - self.rover.y
            detour_distance = math.sqrt(dx*dx + dy*dy)

            if detour_distance < 30:
                # Reached detour waypoint
                self.avoidance_waypoints.pop(0)
                if not self.avoidance_waypoints:
                    # Detour complete, back to grid path
                    self.avoiding_obstacle = False
                    print("Returned to grid path")
                return

        # Steer toward target (or detour point)
        if self.avoiding_obstacle and self.avoidance_waypoints:
            target_x, target_y = self.avoidance_waypoints[0]
            dx = target_x - self.rover.x
            dy = target_y - self.rover.y

        target_angle = math.degrees(math.atan2(dy, dx))
        current_angle = self.rover.angle % 360
        target_angle = target_angle % 360

        # Calculate angle difference
        angle_diff = target_angle - current_angle
        if angle_diff > 180:
            angle_diff -= 360
        elif angle_diff < -180:
            angle_diff += 360

        # Adjust heading
        turn_speed = 2.5
        if abs(angle_diff) > turn_speed:
            if angle_diff > 0:
                self.rover.angle += turn_speed
            else:
                self.rover.angle -= turn_speed
        else:
            self.rover.angle = target_angle

        # Move forward
        self.rover.speed = min(self.rover.speed + 0.15, self.rover.max_speed)

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
        # Handle grid following before parent update
        if self.grid_following:
            self.update_grid_following()

        # Call parent update
        super().update()

        # Enforce world boundaries after movement
        self.enforce_world_boundaries()

    def draw(self):
        """Enhanced drawing with Phase 8 features"""
        # Call parent (Phase 7) draw to get everything rendered
        # We'll just draw over the bottom UI portion
        from .phase6_extended import Phase6Game

        # Clear screen
        self.screen.fill((101, 86, 71))  # Base terrain color

        # Draw terrain patterns/textures across visible area
        import random
        random.seed(42)  # Consistent terrain
        camera_left = int(self.camera.x)
        camera_top = int(self.camera.y)
        camera_right = int(self.camera.x + self.width)
        camera_bottom = int(self.camera.y + self.height)

        # Draw terrain rocks/patterns only in visible area
        for world_x in range(camera_left - 100, camera_right + 100, 50):
            for world_y in range(camera_top - 100, camera_bottom + 100, 50):
                random.seed(world_x * 1000 + world_y)
                for _ in range(3):
                    offset_x = random.randint(0, 50)
                    offset_y = random.randint(0, 50)
                    size = random.randint(1, 3)
                    color = (random.randint(80, 120), random.randint(70, 100), random.randint(60, 90))
                    screen_pos = self.camera.apply(world_x + offset_x, world_y + offset_y)
                    if 0 <= screen_pos[0] < self.width and 0 <= screen_pos[1] < self.height:
                        pygame.draw.circle(self.screen, color, screen_pos, size)
        random.seed()

        # Draw keep-out zones
        self.draw_keepout_zones_camera()

        # Draw base
        if hasattr(self, 'draw_base_camera'):
            self.draw_base_camera()

        # Draw artifacts
        if hasattr(self, 'draw_artifacts_camera'):
            self.draw_artifacts_camera()

        # Draw dig sites
        for site in self.dig_sites:
            if hasattr(self, 'draw_dig_site_camera'):
                self.draw_dig_site_camera(site)

        # Draw hazards
        for hazard in self.hazards:
            if hasattr(self, 'draw_hazard_camera'):
                self.draw_hazard_camera(hazard)

        # Draw rover trail
        if hasattr(self, 'draw_rover_trail_camera'):
            self.draw_rover_trail_camera()

        # Draw autopilot path
        if self.autopilot_active and hasattr(self, 'autopilot_path'):
            for i, (wx, wy) in enumerate(self.autopilot_path):
                screen_pos = self.camera.apply(wx, wy)
                if 0 <= screen_pos[0] <= self.width and 0 <= screen_pos[1] <= self.height:
                    pygame.draw.circle(self.screen, (0, 255, 255), screen_pos, 4)

        # Draw rover
        if hasattr(self, 'draw_rover_camera'):
            self.draw_rover_camera()

        # Draw grid overlay
        self.draw_grid()

        # Draw grid waypoints if active
        if self.grid_following and self.grid_waypoints:
            for i, (wx, wy) in enumerate(self.grid_waypoints):
                screen_pos = self.camera.apply(wx, wy)
                if 0 <= screen_pos[0] <= self.width and 0 <= screen_pos[1] <= self.height:
                    if i == self.grid_waypoint_index:
                        pygame.draw.circle(self.screen, (0, 255, 0), screen_pos, 6)
                    elif i < self.grid_waypoint_index:
                        pygame.draw.circle(self.screen, (100, 100, 100), screen_pos, 3)
                    else:
                        pygame.draw.circle(self.screen, (0, 200, 200), screen_pos, 4)

        # Draw detour waypoints
        if self.avoiding_obstacle and self.avoidance_waypoints:
            for (wx, wy) in self.avoidance_waypoints:
                screen_pos = self.camera.apply(wx, wy)
                if 0 <= screen_pos[0] <= self.width and 0 <= screen_pos[1] <= self.height:
                    pygame.draw.circle(self.screen, (255, 165, 0), screen_pos, 8, 2)

        # Draw fixed UI elements
        if hasattr(self, 'draw_status_panel'):
            self.draw_status_panel()

        if hasattr(self, 'draw_gpr_display'):
            self.draw_gpr_display()

        if hasattr(self, 'draw_artifact_catalog'):
            self.draw_artifact_catalog()

        if hasattr(self, 'draw_selected_artifact_coords'):
            self.draw_selected_artifact_coords()

        if hasattr(self, 'draw_excavation_progress'):
            self.draw_excavation_progress()

        if hasattr(self, 'draw_artifact_display'):
            self.draw_artifact_display()

        if hasattr(self, 'draw_battery_indicator'):
            self.draw_battery_indicator()

        # Draw Phase 8 custom bottom UI (instead of Phase 6's)
        self.draw_phase8_ui()

    def draw_keepout_zones_camera(self):
        """Draw keep-out zones for ALL hazards in Phase 8 (override Phase 7's discovery-based version)"""
        if self.show_keepout_zones:
            for hazard in self.hazards:
                # In Phase 8, show all keep-out zones regardless of discovery
                keepout_radius = hazard.radius + self.rover.collision_radius
                screen_pos = self.camera.apply(hazard.x, hazard.y)
                pygame.draw.circle(self.screen, (255, 0, 0), screen_pos, keepout_radius, 2)

    def draw_phase8_ui(self):
        """Draw Phase 8 bottom UI panel with title and controls"""
        # Enhanced controls panel at bottom
        ui_panel = pygame.Rect(20, self.height - 160, self.width - 40, 140)
        pygame.draw.rect(self.screen, (20, 30, 40), ui_panel, border_radius=15)
        pygame.draw.rect(self.screen, (100, 120, 150), ui_panel, 3, border_radius=15)

        # Title
        help_font = pygame.font.Font(None, 28)
        help_title = help_font.render("Phase 8: Grid Navigation", True, (255, 255, 255))
        self.screen.blit(help_title, (30, self.height - 150))

        # Controls organized in columns
        controls_font = pygame.font.Font(None, 19)
        y_pos = self.height - 125

        # Line 1: Movement + Grid Nav
        controls_line1 = [
            ("Movement: ", (150, 200, 255)),
            ("WASD: Move", (200, 220, 255)),
            (" | R: Return to Base", (200, 220, 255)),
            ("  |  ", (200, 220, 255)),
            ("Grid: ", (0, 255, 200)),
            ("V: H-Sweep", (200, 220, 255)),
            (" | B: V-Sweep", (200, 220, 255)),
            (" | X: Stop", (200, 220, 255)),
            (" | M: Toggle Grid", (200, 220, 255))
        ]

        x_pos = 30
        for text, color in controls_line1:
            rendered = controls_font.render(text, True, color)
            self.screen.blit(rendered, (x_pos, y_pos))
            x_pos += rendered.get_width()

        y_pos += 22

        # Line 2: Exploration controls
        controls_line2 = [
            ("Exploration: ", (255, 200, 100)),
            ("G: GPR", (200, 220, 255)),
            (" | P: Excavate", (200, 220, 255)),
            (" | K: Keep-Out Zones", (200, 220, 255)),
            (" | E: Exploration Stats", (200, 220, 255)),
            (" | C: Clear Sites", (200, 220, 255)),
            (" | ESC: Exit", (200, 220, 255))
        ]

        x_pos = 30
        for text, color in controls_line2:
            rendered = controls_font.render(text, True, color)
            self.screen.blit(rendered, (x_pos, y_pos))
            x_pos += rendered.get_width()

        y_pos += 22

        # Line 3: Info
        info_font = pygame.font.Font(None, 18)
        if self.grid_following:
            info_text = f"Grid Navigation Active: {self.grid_waypoint_index}/{len(self.grid_waypoints)} waypoints ({int((self.grid_waypoint_index/len(self.grid_waypoints))*100) if self.grid_waypoints else 0}% complete)"
            color = (100, 255, 100)
        else:
            info_text = "Bounded world with grid overlay. Press V or B to start autonomous grid navigation!"
            color = (200, 220, 255)

        text = info_font.render(info_text, True, color)
        self.screen.blit(text, (30, y_pos))

    def draw_status_panel(self):
        """Enhanced status panel with grid navigation status"""
        # Draw parent status panel first
        super().draw_status_panel()

        # Add grid navigation status if active
        if self.grid_following:
            panel_x = 20
            panel_y = 310  # Below exploration stats

            # Grid status background
            stats_rect = pygame.Rect(panel_x, panel_y, 260, 60)
            pygame.draw.rect(self.screen, (30, 30, 40), stats_rect, border_radius=8)
            pygame.draw.rect(self.screen, (150, 150, 180), stats_rect, 3, border_radius=8)

            # Title
            font = pygame.font.Font(None, 22)
            title = font.render("GRID NAVIGATION", True, (0, 255, 255))
            self.screen.blit(title, (panel_x + 10, panel_y + 8))

            # Progress
            small_font = pygame.font.Font(None, 20)
            progress_percent = (self.grid_waypoint_index / len(self.grid_waypoints)) * 100 if self.grid_waypoints else 0
            status_text = f"Progress: {self.grid_waypoint_index}/{len(self.grid_waypoints)} ({int(progress_percent)}%)"
            text = small_font.render(status_text, True, (200, 200, 200))
            self.screen.blit(text, (panel_x + 10, panel_y + 35))

    def handle_keydown(self, event):
        """Handle keyboard input with Phase 8 specific controls"""
        # Call parent keydown handler
        super().handle_keydown(event)

        # Grid navigation controls
        if event.key == pygame.K_v:
            # Start horizontal grid navigation
            if not self.grid_following:
                self.start_grid_following("horizontal")
            else:
                print("Grid navigation already active")

        elif event.key == pygame.K_b:
            # Start vertical grid navigation
            if not self.grid_following:
                self.start_grid_following("vertical")
            else:
                print("Grid navigation already active")

        elif event.key == pygame.K_x:
            # Stop grid navigation
            if self.grid_following:
                self.stop_grid_following()

        elif event.key == pygame.K_m:
            # Toggle grid display
            self.show_grid = not self.show_grid

    def reset_game(self):
        """Reset game including grid navigation"""
        super().reset_game()
        self.stop_grid_following()
