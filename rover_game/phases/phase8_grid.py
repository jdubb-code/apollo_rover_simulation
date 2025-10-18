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
        # Draw parent elements first
        super().draw()

        # Draw grid overlay after terrain but before UI
        self.draw_grid()

        # Draw grid waypoints if active
        if self.grid_following and self.grid_waypoints:
            for i, (wx, wy) in enumerate(self.grid_waypoints):
                screen_pos = self.camera.apply(wx, wy)
                if 0 <= screen_pos[0] <= self.width and 0 <= screen_pos[1] <= self.height:
                    # Draw waypoint marker
                    if i == self.grid_waypoint_index:
                        # Current target in green
                        pygame.draw.circle(self.screen, (0, 255, 0), screen_pos, 6)
                    elif i < self.grid_waypoint_index:
                        # Completed in gray
                        pygame.draw.circle(self.screen, (100, 100, 100), screen_pos, 3)
                    else:
                        # Upcoming in cyan
                        pygame.draw.circle(self.screen, (0, 200, 200), screen_pos, 4)

        # Draw detour waypoints if avoiding obstacles
        if self.avoiding_obstacle and self.avoidance_waypoints:
            for (wx, wy) in self.avoidance_waypoints:
                screen_pos = self.camera.apply(wx, wy)
                if 0 <= screen_pos[0] <= self.width and 0 <= screen_pos[1] <= self.height:
                    pygame.draw.circle(self.screen, (255, 165, 0), screen_pos, 8, 2)  # Orange circles

    def draw_controls(self):
        """Enhanced controls showing grid navigation features"""
        panel_x = 20
        panel_y = self.height - 240  # Panel sized for controls

        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, 280, 230)
        pygame.draw.rect(self.screen, (30, 30, 40), panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, (150, 150, 180), panel_rect, 3, border_radius=8)

        # Title
        font = pygame.font.Font(None, 24)
        title = font.render("CONTROLS", True, (255, 255, 255))
        self.screen.blit(title, (panel_x + 10, panel_y + 8))

        # Control list organized by category
        small_font = pygame.font.Font(None, 17)
        header_font = pygame.font.Font(None, 19)

        y_offset = 33

        # Movement section
        header = header_font.render("Movement:", True, (150, 200, 255))
        self.screen.blit(header, (panel_x + 10, panel_y + y_offset))
        y_offset += 18

        movement_controls = [
            "WASD: Move Rover",
            "R: Return to Base (Auto)"
        ]
        for control in movement_controls:
            text = small_font.render(control, True, (200, 200, 200))
            self.screen.blit(text, (panel_x + 15, panel_y + y_offset))
            y_offset += 16

        y_offset += 4

        # Grid Navigation section
        header = header_font.render("Grid Navigation:", True, (0, 255, 200))
        self.screen.blit(header, (panel_x + 10, panel_y + y_offset))
        y_offset += 18

        grid_controls = [
            "V: Start Horizontal Sweep",
            "B: Start Vertical Sweep",
            "X: Stop Grid Navigation",
            "M: Toggle Grid Display"
        ]
        for control in grid_controls:
            text = small_font.render(control, True, (200, 200, 200))
            self.screen.blit(text, (panel_x + 15, panel_y + y_offset))
            y_offset += 16

        y_offset += 4

        # Exploration section
        header = header_font.render("Exploration:", True, (255, 200, 100))
        self.screen.blit(header, (panel_x + 10, panel_y + y_offset))
        y_offset += 18

        explore_controls = [
            "G: Toggle GPR",
            "P: Excavate Artifact",
            "K: Toggle Keep-Out Zones",
            "E: Toggle Exploration Stats"
        ]
        for control in explore_controls:
            text = small_font.render(control, True, (200, 200, 200))
            self.screen.blit(text, (panel_x + 15, panel_y + y_offset))
            y_offset += 16


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
