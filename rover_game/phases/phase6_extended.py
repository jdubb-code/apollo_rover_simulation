"""
Phase 6: Extended Features
Building upon Phase 5 with realistic hazard graphics (rocks, trees, water)
"""

import pygame
import math
import sys
import random
import time
import numpy as np
from .phase5_physics import Phase5Game, PhysicsRover
from .phase4_advanced import AdvancedDigSite, ArtifactImage
from .phase3_gpr import Artifact, GPRSystem, ArtifactCatalog
from .phase2_graphics import Hazard, EnhancedDigSite


class RealisticHazard:
    """Enhanced hazard with realistic graphics for rocks, trees, and bodies of water"""

    def __init__(self, x, y, hazard_type=None):
        self.x = x
        self.y = y
        self.detected = False

        # Randomly assign hazard type if not specified
        if hazard_type is None:
            hazard_type = random.choice(["rock", "boulder", "tree", "water", "pond"])

        self.type = hazard_type

        # Set properties based on hazard type
        if self.type == "rock":
            self.radius = random.randint(15, 25)
            self.color = (120, 110, 100)
            self.detail_color = (90, 80, 70)
            self.width = self.radius * 2
            self.height = self.radius * 2
        elif self.type == "boulder":
            self.radius = random.randint(30, 45)
            self.color = (100, 90, 85)
            self.detail_color = (70, 60, 55)
            self.width = self.radius * 2
            self.height = self.radius * 2
        elif self.type == "tree":
            self.radius = random.randint(20, 30)
            self.trunk_color = (101, 67, 33)
            self.foliage_color = (34, 139, 34)
            self.foliage_dark = (25, 100, 25)
            self.width = self.radius * 2
            self.height = self.radius * 2
        elif self.type == "water":
            self.radius = random.randint(40, 60)
            self.color = (30, 144, 255)
            self.ripple_color = (100, 180, 255)
            self.dark_color = (20, 100, 180)
            self.width = self.radius * 2
            self.height = self.radius * 2
            self.ripple_offset = random.random() * 6.28  # Random phase for ripples
        elif self.type == "pond":
            self.radius = random.randint(25, 40)
            self.color = (65, 105, 225)
            self.ripple_color = (100, 149, 237)
            self.dark_color = (30, 60, 150)
            self.width = self.radius * 2
            self.height = self.radius * 2
            self.ripple_offset = random.random() * 6.28

    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2,
                          self.width, self.height)

    def is_near_rover(self, rover_x, rover_y, detection_range=80):
        """Check if hazard is within rover's detection range"""
        distance = math.sqrt((self.x - rover_x)**2 + (self.y - rover_y)**2)
        if distance <= detection_range:
            self.detected = True
        return self.detected

    def draw(self, screen):
        """Draw realistic hazard with type-specific graphics"""

        if self.type in ["rock", "boulder"]:
            self.draw_rock(screen)
        elif self.type == "tree":
            self.draw_tree(screen)
        elif self.type in ["water", "pond"]:
            self.draw_water(screen)

        # Highlight if detected
        if self.detected:
            pygame.draw.circle(screen, (255, 0, 0),
                             (int(self.x), int(self.y)), self.radius + 5, 3)

    def draw_rock(self, screen):
        """Draw realistic rock/boulder"""
        # Main rock body with irregular shape
        main_color = self.color

        # Draw multiple overlapping circles for irregular shape
        num_circles = 3 if self.type == "rock" else 5
        for i in range(num_circles):
            angle = (i / num_circles) * 2 * math.pi
            offset_x = math.cos(angle) * (self.radius * 0.3)
            offset_y = math.sin(angle) * (self.radius * 0.3)
            sub_radius = int(self.radius * random.uniform(0.6, 0.9))

            pygame.draw.circle(screen, main_color,
                             (int(self.x + offset_x), int(self.y + offset_y)),
                             sub_radius)

        # Main body
        pygame.draw.circle(screen, main_color,
                         (int(self.x), int(self.y)), self.radius)

        # Add texture with darker spots
        random.seed(int(self.x + self.y))  # Consistent pattern
        for _ in range(5 if self.type == "boulder" else 3):
            spot_x = self.x + random.randint(-self.radius//2, self.radius//2)
            spot_y = self.y + random.randint(-self.radius//2, self.radius//2)
            spot_size = random.randint(3, 8)
            pygame.draw.circle(screen, self.detail_color,
                             (int(spot_x), int(spot_y)), spot_size)
        random.seed()  # Reset seed

        # Highlight edge for 3D effect
        pygame.draw.circle(screen, self.detail_color,
                         (int(self.x), int(self.y)), self.radius, 2)

        # Light reflection spot
        light_x = self.x - self.radius * 0.3
        light_y = self.y - self.radius * 0.3
        pygame.draw.circle(screen, (160, 150, 140),
                         (int(light_x), int(light_y)), max(3, self.radius // 5))

    def draw_tree(self, screen):
        """Draw realistic tree with trunk and foliage"""
        # Trunk
        trunk_width = max(8, self.radius // 3)
        trunk_height = self.radius
        trunk_rect = pygame.Rect(
            int(self.x - trunk_width//2),
            int(self.y - trunk_height//4),
            trunk_width,
            trunk_height
        )
        pygame.draw.rect(screen, self.trunk_color, trunk_rect)
        pygame.draw.rect(screen, (80, 50, 20), trunk_rect, 2)  # Bark outline

        # Add bark texture
        for i in range(3):
            line_y = int(self.y - trunk_height//4 + (i+1) * trunk_height // 4)
            pygame.draw.line(screen, (80, 50, 20),
                           (int(self.x - trunk_width//2), line_y),
                           (int(self.x + trunk_width//2), line_y), 1)

        # Foliage - multiple overlapping circles for bushy appearance
        foliage_positions = [
            (0, -self.radius * 0.8),
            (-self.radius * 0.4, -self.radius * 0.5),
            (self.radius * 0.4, -self.radius * 0.5),
            (-self.radius * 0.3, -self.radius * 1.0),
            (self.radius * 0.3, -self.radius * 1.0),
        ]

        # Draw darker foliage first (back layer)
        for offset_x, offset_y in foliage_positions:
            pygame.draw.circle(screen, self.foliage_dark,
                             (int(self.x + offset_x), int(self.y + offset_y)),
                             int(self.radius * 0.5))

        # Draw lighter foliage on top
        for offset_x, offset_y in foliage_positions:
            pygame.draw.circle(screen, self.foliage_color,
                             (int(self.x + offset_x * 0.8), int(self.y + offset_y * 0.8)),
                             int(self.radius * 0.45))

    def draw_water(self, screen):
        """Draw realistic body of water with ripples"""
        # Main water body
        pygame.draw.circle(screen, self.dark_color,
                         (int(self.x), int(self.y)), self.radius)

        # Mid-tone layer
        pygame.draw.circle(screen, self.color,
                         (int(self.x), int(self.y)), int(self.radius * 0.9))

        # Animated ripples
        current_time = time.time()
        for i in range(3):
            ripple_radius = int(self.radius * (0.3 + i * 0.2))
            ripple_phase = (current_time + self.ripple_offset + i * 2) % 3
            if ripple_phase < 1.5:  # Only show ripple for half the cycle
                alpha_factor = 1 - (ripple_phase / 1.5)
                ripple_color = (
                    int(self.ripple_color[0] * alpha_factor + self.color[0] * (1 - alpha_factor)),
                    int(self.ripple_color[1] * alpha_factor + self.color[1] * (1 - alpha_factor)),
                    int(self.ripple_color[2] * alpha_factor + self.color[2] * (1 - alpha_factor))
                )
                pygame.draw.circle(screen, ripple_color,
                                 (int(self.x), int(self.y)), ripple_radius, 2)

        # Light reflection
        reflect_x = self.x - self.radius * 0.3
        reflect_y = self.y - self.radius * 0.3
        reflect_radius = int(self.radius * 0.2)
        pygame.draw.circle(screen, (200, 230, 255),
                         (int(reflect_x), int(reflect_y)), reflect_radius)

        # Shore/edge
        pygame.draw.circle(screen, (139, 119, 99),
                         (int(self.x), int(self.y)), self.radius, 3)


class Camera:
    """Camera system that follows the rover and keeps it centered"""

    def __init__(self, screen_width, screen_height, world_width, world_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = world_width
        self.world_height = world_height

        # Camera position in world coordinates (top-left corner of view)
        self.x = 0
        self.y = 0

    def update(self, target_x, target_y):
        """Update camera to center on target (usually the rover)"""
        # Center camera on target
        self.x = target_x - self.screen_width // 2
        self.y = target_y - self.screen_height // 2

        # Clamp camera to world bounds
        self.x = max(0, min(self.x, self.world_width - self.screen_width))
        self.y = max(0, min(self.y, self.world_height - self.screen_height))

    def apply(self, x, y):
        """Convert world coordinates to screen coordinates"""
        return (int(x - self.x), int(y - self.y))

    def apply_rect(self, rect):
        """Convert world rect to screen rect"""
        return pygame.Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)

    def reverse(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        return (screen_x + self.x, screen_y + self.y)


class Phase6Game(Phase5Game):
    """Phase 6 game with realistic hazards and camera system"""

    def __init__(self):
        # Initialize Phase5Game first
        super().__init__()

        pygame.display.set_caption("Archaeological Rover - Phase 6: Realistic Hazards")

        # Create larger world with camera system
        self.world_width = 3000
        self.world_height = 2400
        self.camera = Camera(self.width, self.height, self.world_width, self.world_height)

        # Move rover to center of world
        self.rover.x = self.world_width // 2
        self.rover.y = self.world_height // 2

        # Store base location (rover spawn point)
        self.base_x = self.world_width // 2
        self.base_y = self.world_height // 2

        # Replace hazards with realistic versions across larger world
        self.generate_realistic_hazards()

        # Regenerate artifacts across larger world
        self.artifacts = self.generate_artifacts_world()

        # Debug mode to show all artifacts
        self.show_all_artifacts = False

        # Show artifact count
        self.show_artifact_count = False

        # Selected artifact for showing coordinates
        self.selected_artifact = None

        # Autopilot/return to base
        self.autopilot_active = False
        self.autopilot_path = []
        self.autopilot_waypoint_index = 0

        # Battery system
        self.battery_capacity = 60.0  # 60 seconds = 1 minute
        self.battery_level = 60.0  # Start full
        self.battery_depleted = False
        self.is_recharging = False
        self.recharge_timer = 0.0
        self.recharge_duration = 5.0  # 5 seconds to fully recharge

    def generate_realistic_hazards(self):
        """Generate realistic hazards with diverse types across the world"""
        self.hazards = []

        # Generate a mix of hazard types
        hazard_types = ["rock", "boulder", "tree", "water", "pond"]

        # Create more hazards for larger world (25-35 hazards)
        num_hazards = random.randint(25, 35)

        for _ in range(num_hazards):
            # Ensure hazards are not too close to starting position or edges
            while True:
                x = random.randint(150, self.world_width - 150)
                y = random.randint(150, self.world_height - 150)

                # Check distance from rover starting position (center of world)
                rover_start_x = self.world_width // 2
                rover_start_y = self.world_height // 2
                if math.sqrt((x - rover_start_x)**2 + (y - rover_start_y)**2) > 200:
                    # Check distance from other hazards
                    too_close = False
                    for existing_hazard in self.hazards:
                        dist = math.sqrt((x - existing_hazard.x)**2 + (y - existing_hazard.y)**2)
                        if dist < 120:
                            too_close = True
                            break

                    if not too_close:
                        break

            # Pick a random hazard type
            hazard_type = random.choice(hazard_types)
            hazard = RealisticHazard(x, y, hazard_type)
            self.hazards.append(hazard)

    def generate_artifacts_world(self):
        """Generate artifacts across the larger world"""
        artifacts = []
        artifact_types = ["pottery", "tool", "jewelry", "statue", "tablet"]

        # Generate 30-40 artifacts across the world
        for i in range(random.randint(30, 40)):
            # Spread artifacts across the world
            x = random.randint(200, self.world_width - 200)
            y = random.randint(200, self.world_height - 200)
            depth = random.uniform(0.5, 3.0)
            artifact_type = random.choice(artifact_types)

            artifact = Artifact(x, y, depth, artifact_type)
            artifacts.append(artifact)

        return artifacts

    def handle_events(self):
        """Enhanced event handling for Phase 6 with camera support"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()

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
                    # Scroll down in artifact catalog
                    self.artifact_catalog.scroll_down()
                elif event.key == pygame.K_p:
                    # Excavate nearby dig site
                    if self.excavate_nearby_site():
                        print("Excavation started!")
                elif event.key == pygame.K_k:
                    # Toggle keep-out zone visualization
                    self.show_keepout_zones = not self.show_keepout_zones
                elif event.key == pygame.K_h:
                    # Toggle showing all artifacts (debug/help mode)
                    self.show_all_artifacts = not self.show_all_artifacts
                    status = "ON" if self.show_all_artifacts else "OFF"
                    print(f"Show all artifacts: {status}")
                elif event.key == pygame.K_n:
                    # Toggle showing artifact count
                    self.show_artifact_count = not self.show_artifact_count
                    status = "ON" if self.show_artifact_count else "OFF"
                    print(f"Artifact count display: {status}")
                elif event.key == pygame.K_r:
                    # Return to base
                    if not self.autopilot_active:
                        self.start_return_to_base()
                    else:
                        self.cancel_autopilot()

        return True

    def handle_catalog_click(self, mouse_x, mouse_y):
        """Handle clicks on artifact catalog to show coordinates"""
        # Catalog panel position (matching draw_catalog_panel call)
        catalog_x, catalog_y = 20, 300
        catalog_width, catalog_height = 300, 200

        # Check if click is within catalog bounds
        if (catalog_x <= mouse_x <= catalog_x + catalog_width and
            catalog_y <= mouse_y <= catalog_y + catalog_height):

            # Calculate which artifact was clicked
            # List area starts at y + 35 (after title)
            list_y = catalog_y + 40
            relative_y = mouse_y - list_y

            if relative_y >= 0:
                # Each artifact entry is 45 pixels tall
                entry_height = 45
                clicked_index = int(relative_y // entry_height)

                # Get reversed list (newest first) and apply scroll offset
                reversed_artifacts = list(reversed(self.artifact_catalog.discovered_artifacts))
                start_index = self.artifact_catalog.scroll_offset
                end_index = min(start_index + self.artifact_catalog.max_visible_items,
                              len(reversed_artifacts))
                visible_artifacts = reversed_artifacts[start_index:end_index]

                # Check if clicked index is valid
                if 0 <= clicked_index < len(visible_artifacts):
                    self.selected_artifact = visible_artifacts[clicked_index]
                    print(f"Selected artifact at ({int(self.selected_artifact.x)}, {int(self.selected_artifact.y)})")
                    return True

        return False

    def handle_excavation_click_world(self, world_x, world_y):
        """Handle excavation click using world coordinates"""
        # Check if click is on artifact display area
        if hasattr(self, 'artifact_display') and self.artifact_display:
            return False

        # Find dig sites near click in world coordinates
        for site in self.dig_sites:
            if not site.excavated:
                dist = math.sqrt((site.x - world_x)**2 + (site.y - world_y)**2)
                if dist < 30:  # Click tolerance
                    # Check if site is near artifacts
                    for artifact in self.artifacts:
                        if not artifact.discovered:
                            artifact_dist = math.sqrt((artifact.x - site.x)**2 + (artifact.y - site.y)**2)
                            if artifact_dist < 50:
                                # Start excavation
                                self.active_excavation = site
                                self.excavation_timer = 0
                                site.start_excavation()
                                return True
        return False

    def start_return_to_base(self):
        """Start autopilot to return to base"""
        print("Calculating path to base...")
        self.autopilot_path = self.calculate_path_to_base()
        if self.autopilot_path:
            self.autopilot_active = True
            self.autopilot_waypoint_index = 0
            print(f"Autopilot engaged! Following {len(self.autopilot_path)} waypoints to base.")
        else:
            print("Could not find path to base!")

    def cancel_autopilot(self):
        """Cancel autopilot mode"""
        self.autopilot_active = False
        self.autopilot_path = []
        self.autopilot_waypoint_index = 0

        # If battery was depleted during return to base, now stop the rover
        if self.battery_level <= 0:
            self.battery_depleted = True

        print("Autopilot cancelled.")

    def calculate_path_to_base(self):
        """Calculate a path from rover to base avoiding keep-out zones"""
        # Simple waypoint-based pathfinding
        # Check if direct path is clear
        if self.is_path_clear(self.rover.x, self.rover.y, self.base_x, self.base_y):
            return [(self.base_x, self.base_y)]

        # If not, use waypoint pathfinding
        waypoints = []
        current_x, current_y = self.rover.x, self.rover.y
        target_x, target_y = self.base_x, self.base_y

        max_attempts = 50
        attempts = 0

        while attempts < max_attempts:
            # Calculate direction to target
            dx = target_x - current_x
            dy = target_y - current_y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance < 50:  # Close enough to base
                waypoints.append((target_x, target_y))
                break

            # Try direct path
            step_distance = min(200, distance)
            next_x = current_x + (dx / distance) * step_distance
            next_y = current_y + (dy / distance) * step_distance

            if self.is_path_clear(current_x, current_y, next_x, next_y):
                waypoints.append((next_x, next_y))
                current_x, current_y = next_x, next_y
            else:
                # Find alternate route around obstacles
                best_waypoint = None
                best_score = float('inf')

                # Try multiple angles around the obstacle
                for angle_offset in [-45, 45, -90, 90, -135, 135]:
                    angle = math.atan2(dy, dx) + math.radians(angle_offset)
                    test_x = current_x + math.cos(angle) * step_distance
                    test_y = current_y + math.sin(angle) * step_distance

                    # Check if this waypoint is clear
                    if self.is_path_clear(current_x, current_y, test_x, test_y):
                        # Score based on distance to target
                        score = math.sqrt((test_x - target_x)**2 + (test_y - target_y)**2)
                        if score < best_score:
                            best_score = score
                            best_waypoint = (test_x, test_y)

                if best_waypoint:
                    waypoints.append(best_waypoint)
                    current_x, current_y = best_waypoint
                else:
                    # Stuck, try backing up
                    back_x = current_x - (dx / distance) * 100
                    back_y = current_y - (dy / distance) * 100
                    waypoints.append((back_x, back_y))
                    current_x, current_y = back_x, back_y

            attempts += 1

        return waypoints if waypoints else None

    def is_path_clear(self, x1, y1, x2, y2):
        """Check if a straight line path is clear of keep-out zones"""
        # Sample points along the line
        num_samples = 20
        for i in range(num_samples + 1):
            t = i / num_samples
            check_x = x1 + (x2 - x1) * t
            check_y = y1 + (y2 - y1) * t

            # Check against all hazard keep-out zones
            for hazard in self.hazards:
                keepout_radius = hazard.radius + self.rover.collision_radius + 10  # Add buffer
                dist = math.sqrt((check_x - hazard.x)**2 + (check_y - hazard.y)**2)
                if dist < keepout_radius:
                    return False

        return True

    def reset_game(self):
        """Reset game and regenerate realistic hazards"""
        super().reset_game()
        # Reset rover to center of world
        self.rover.x = self.world_width // 2
        self.rover.y = self.world_height // 2
        # Regenerate realistic hazards on reset
        self.generate_realistic_hazards()
        # Cancel autopilot
        self.cancel_autopilot()
        # Reset battery
        self.battery_level = self.battery_capacity
        self.battery_depleted = False

    def update(self):
        """Update game state with Phase 6 features and camera"""
        # Update battery
        self.update_battery()

        # Handle autopilot before normal update
        if self.autopilot_active:
            self.update_autopilot()

        # Only allow movement if battery isn't depleted or returning to base
        if not self.battery_depleted or self.autopilot_active:
            super().update()
        else:
            # Battery depleted, stop rover
            self.rover.speed *= 0.9  # Gradually slow down

        # Update camera to follow rover
        self.camera.update(self.rover.x, self.rover.y)

    def update_battery(self):
        """Update battery level based on rover movement and recharging at base"""
        # Check if rover is at base (within 50 pixels)
        distance_to_base = math.sqrt((self.rover.x - self.base_x)**2 + (self.rover.y - self.base_y)**2)
        at_base = distance_to_base < 50

        # Handle recharging at base
        if at_base and self.battery_level < self.battery_capacity:
            self.is_recharging = True
            # Recharge over 5 seconds at 60 FPS = capacity/300 per frame
            recharge_rate = self.battery_capacity / (self.recharge_duration * 60.0)
            self.battery_level += recharge_rate
            self.recharge_timer += 1.0 / 60.0  # Track recharge time

            if self.battery_level >= self.battery_capacity:
                self.battery_level = self.battery_capacity
                self.battery_depleted = False
                self.is_recharging = False
                self.recharge_timer = 0.0
                print("Battery fully recharged!")
            return
        else:
            # Reset recharge state when not at base
            if self.is_recharging:
                self.is_recharging = False
                self.recharge_timer = 0.0

        # Handle depleted battery
        if self.battery_level <= 0:
            self.battery_level = 0
            # Only stop if not returning to base
            if not self.autopilot_active:
                self.battery_depleted = True
            return

        # Drain battery when rover is moving
        if abs(self.rover.speed) > 0.1:
            # Drain rate: 1 second per frame at 60 FPS = 1/60 per frame
            drain_rate = 1.0 / 60.0
            self.battery_level -= drain_rate

            if self.battery_level <= 0:
                self.battery_level = 0
                if not self.autopilot_active:
                    self.battery_depleted = True
                    print("Battery depleted! Rover stopped.")

    def update_autopilot(self):
        """Update autopilot movement toward waypoints"""
        if not self.autopilot_path or self.autopilot_waypoint_index >= len(self.autopilot_path):
            self.cancel_autopilot()
            return

        # Get current waypoint
        target_x, target_y = self.autopilot_path[self.autopilot_waypoint_index]

        # Calculate direction to waypoint
        dx = target_x - self.rover.x
        dy = target_y - self.rover.y
        distance = math.sqrt(dx*dx + dy*dy)

        # Check if reached waypoint
        if distance < 30:
            self.autopilot_waypoint_index += 1
            if self.autopilot_waypoint_index >= len(self.autopilot_path):
                print("Arrived at base!")
                self.cancel_autopilot()
                return
            return

        # Steer toward waypoint
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

    def draw(self):
        """Enhanced drawing with Phase 6 features and camera system"""
        # Clear screen
        self.screen.fill((101, 86, 71))  # Base terrain color

        # Draw terrain patterns/textures across visible area
        random.seed(42)  # Consistent terrain
        # Draw terrain for entire world (visible portion)
        camera_left = int(self.camera.x)
        camera_top = int(self.camera.y)
        camera_right = int(self.camera.x + self.width)
        camera_bottom = int(self.camera.y + self.height)

        # Draw terrain rocks/patterns only in visible area
        for world_x in range(camera_left - 100, camera_right + 100, 50):
            for world_y in range(camera_top - 100, camera_bottom + 100, 50):
                random.seed(world_x * 1000 + world_y)  # Consistent per location
                for _ in range(3):
                    offset_x = random.randint(0, 50)
                    offset_y = random.randint(0, 50)
                    size = random.randint(1, 3)
                    color = (random.randint(80, 120), random.randint(70, 100), random.randint(60, 90))
                    screen_pos = self.camera.apply(world_x + offset_x, world_y + offset_y)
                    if 0 <= screen_pos[0] < self.width and 0 <= screen_pos[1] < self.height:
                        pygame.draw.circle(self.screen, color, screen_pos, size)
        random.seed()  # Reset seed

        # Draw keep-out zones with camera offset
        self.draw_keepout_zones_camera()

        # Draw base location
        self.draw_base_camera()

        # Draw artifacts with camera offset
        self.draw_artifacts_camera()

        # Draw dig sites with camera offset
        for site in self.dig_sites:
            self.draw_dig_site_camera(site)

        # Draw hazards with camera offset
        for hazard in self.hazards:
            self.draw_hazard_camera(hazard)

        # Draw rover trail with camera offset
        self.draw_rover_trail_camera()

        # Draw autopilot path if active
        if self.autopilot_active:
            self.draw_autopilot_path_camera()

        # Draw rover with camera offset
        self.draw_rover_camera()

        # Draw Phase 4 proximity indicators with camera
        self.draw_dig_proximity_indicators_camera()

        # === UI ELEMENTS (no camera offset) ===
        # Draw GPR system (fixed UI)
        self.gpr_system.draw(self.screen)

        # Draw artifact catalog (fixed UI)
        self.artifact_catalog.draw_catalog_panel(self.screen, 20, 300, 300, 200)

        # Draw selected artifact coordinates
        self.draw_selected_artifact_coords()

        # Draw excavation progress (fixed UI)
        self.draw_excavation_progress()

        # Draw artifact display (fixed UI, on top of everything)
        self.draw_artifact_display()

        # Draw Phase 6 UI (fixed)
        self.draw_phase6_ui()

        # Draw battery indicator
        self.draw_battery_indicator()

        # Update display
        pygame.display.flip()

    def draw_keepout_zones_camera(self):
        """Draw keep-out zones with camera offset"""
        if self.show_keepout_zones:
            for hazard in self.hazards:
                screen_pos = self.camera.apply(hazard.x, hazard.y)
                keepout_radius = hazard.radius + self.rover.collision_radius

                # Draw semi-transparent keep-out zone
                s = pygame.Surface((keepout_radius * 2, keepout_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 0, 0, 30),
                                 (keepout_radius, keepout_radius), keepout_radius)
                screen_x = screen_pos[0] - keepout_radius
                screen_y = screen_pos[1] - keepout_radius
                self.screen.blit(s, (screen_x, screen_y))

                # Draw keep-out boundary circle
                pygame.draw.circle(self.screen, (255, 100, 100),
                                 screen_pos, keepout_radius, 2)

    def draw_base_camera(self):
        """Draw base location with camera offset"""
        screen_pos = self.camera.apply(self.base_x, self.base_y)

        # Draw base structure
        base_size = 40

        # Outer square (landing pad)
        outer_rect = pygame.Rect(
            screen_pos[0] - base_size,
            screen_pos[1] - base_size,
            base_size * 2,
            base_size * 2
        )
        pygame.draw.rect(self.screen, (80, 80, 100), outer_rect)
        pygame.draw.rect(self.screen, (150, 150, 180), outer_rect, 3)

        # Inner building/hub
        inner_size = 25
        inner_rect = pygame.Rect(
            screen_pos[0] - inner_size,
            screen_pos[1] - inner_size,
            inner_size * 2,
            inner_size * 2
        )
        pygame.draw.rect(self.screen, (100, 100, 120), inner_rect)
        pygame.draw.rect(self.screen, (180, 180, 200), inner_rect, 2)

        # Communication antenna on top
        antenna_tip_y = screen_pos[1] - inner_size - 15
        pygame.draw.line(self.screen, (200, 200, 220),
                        screen_pos, (screen_pos[0], antenna_tip_y), 3)
        pygame.draw.circle(self.screen, (255, 100, 100),
                         (screen_pos[0], antenna_tip_y), 5)

        # Corner markers
        for dx, dy in [(-base_size, -base_size), (base_size, -base_size),
                       (-base_size, base_size), (base_size, base_size)]:
            marker_pos = (screen_pos[0] + dx, screen_pos[1] + dy)
            pygame.draw.circle(self.screen, (255, 200, 0), marker_pos, 5)

        # Label "BASE" below the structure
        font = pygame.font.Font(None, 24)
        label = font.render("BASE", True, (200, 200, 220))
        label_rect = label.get_rect(center=(screen_pos[0], screen_pos[1] + base_size + 15))
        self.screen.blit(label, label_rect)

    def draw_artifacts_camera(self):
        """Draw artifacts with camera offset"""
        for artifact in self.artifacts:
            screen_pos = self.camera.apply(artifact.x, artifact.y)

            if artifact.discovered:
                # Discovered artifacts show as bright gold circles
                pygame.draw.circle(self.screen, (255, 215, 0),
                                 screen_pos, 15, 3)
                # Add pulsing effect
                pulse = int(2 + 1 * math.sin(time.time() * 2))
                pygame.draw.circle(self.screen, (255, 215, 0),
                                 screen_pos, 10 + pulse, 2)
            elif self.show_all_artifacts:
                # Undiscovered artifacts show as faint underground markers (when H is pressed)
                # Color based on depth - deeper = darker
                depth_alpha = int(100 + (155 * (1 - artifact.depth / 3.0)))
                color = (150, 150, 150)

                # Draw X marker to show undiscovered location
                pygame.draw.line(self.screen, color,
                               (screen_pos[0] - 8, screen_pos[1] - 8),
                               (screen_pos[0] + 8, screen_pos[1] + 8), 2)
                pygame.draw.line(self.screen, color,
                               (screen_pos[0] + 8, screen_pos[1] - 8),
                               (screen_pos[0] - 8, screen_pos[1] + 8), 2)

                # Small circle to indicate artifact
                pygame.draw.circle(self.screen, color, screen_pos, 5, 1)

    def draw_dig_site_camera(self, site):
        """Draw dig site with camera offset"""
        screen_pos = self.camera.apply(site.x, site.y)

        # Pulsing effect
        pulse_size = int(3 + 2 * math.sin(site.pulse_timer))

        # Outer ring
        pygame.draw.circle(self.screen, (255, 200, 0),
                          screen_pos, site.radius + pulse_size, 4)

        # Inner ring
        pygame.draw.circle(self.screen, (255, 255, 100),
                          screen_pos, 12, 3)

        # Center marker
        pygame.draw.circle(self.screen, (255, 255, 0),
                          screen_pos, 6)

        # If excavated, draw X
        if site.excavated:
            pygame.draw.line(self.screen, (100, 100, 100),
                           (screen_pos[0] - 10, screen_pos[1] - 10),
                           (screen_pos[0] + 10, screen_pos[1] + 10), 3)
            pygame.draw.line(self.screen, (100, 100, 100),
                           (screen_pos[0] + 10, screen_pos[1] - 10),
                           (screen_pos[0] - 10, screen_pos[1] + 10), 3)

    def draw_hazard_camera(self, hazard):
        """Draw hazard with camera offset"""
        # Create a temporary surface for the hazard if needed
        # For RealisticHazard, we need to modify its draw method to accept screen position
        screen_pos = self.camera.apply(hazard.x, hazard.y)

        # Temporarily modify hazard position for drawing
        old_x, old_y = hazard.x, hazard.y
        hazard.x, hazard.y = screen_pos[0], screen_pos[1]
        hazard.draw(self.screen)
        hazard.x, hazard.y = old_x, old_y

    def draw_rover_trail_camera(self):
        """Draw rover trail with camera offset"""
        if len(self.rover.trail) > 1:
            for i, pos in enumerate(self.rover.trail):
                screen_pos = self.camera.apply(pos[0], pos[1])
                pygame.draw.circle(self.screen, (120, 100, 80), screen_pos, 3)

    def draw_autopilot_path_camera(self):
        """Draw the autopilot path with camera offset"""
        if not self.autopilot_path:
            return

        # Draw line from rover to first waypoint
        rover_screen = self.camera.apply(self.rover.x, self.rover.y)

        if len(self.autopilot_path) > self.autopilot_waypoint_index:
            first_waypoint = self.autopilot_path[self.autopilot_waypoint_index]
            first_screen = self.camera.apply(first_waypoint[0], first_waypoint[1])
            pygame.draw.line(self.screen, (0, 255, 255), rover_screen, first_screen, 3)

        # Draw lines between waypoints
        for i in range(self.autopilot_waypoint_index, len(self.autopilot_path) - 1):
            wp1 = self.autopilot_path[i]
            wp2 = self.autopilot_path[i + 1]
            screen1 = self.camera.apply(wp1[0], wp1[1])
            screen2 = self.camera.apply(wp2[0], wp2[1])
            pygame.draw.line(self.screen, (0, 255, 255), screen1, screen2, 3)

        # Draw waypoint markers
        for i in range(self.autopilot_waypoint_index, len(self.autopilot_path)):
            wp = self.autopilot_path[i]
            screen_pos = self.camera.apply(wp[0], wp[1])

            # Current waypoint is larger and different color
            if i == self.autopilot_waypoint_index:
                pygame.draw.circle(self.screen, (255, 255, 0), screen_pos, 10, 3)
            else:
                pygame.draw.circle(self.screen, (0, 255, 255), screen_pos, 6, 2)

    def draw_rover_camera(self):
        """Draw rover with camera offset"""
        # Draw dust particles
        for particle in self.rover.dust_particles:
            screen_pos = self.camera.apply(particle['x'], particle['y'])
            alpha = int(255 * particle['life'])
            size = int(3 * particle['life'])
            if size > 0:
                color = (139, 119, 99)
                pygame.draw.circle(self.screen, color, screen_pos, size)

        # Get rover screen position
        rover_screen_pos = self.camera.apply(self.rover.x, self.rover.y)

        # Draw collision warning indicator
        if self.rover.collision_warning:
            pulse = int(5 * (1 + math.sin(time.time() * 10)))
            pygame.draw.circle(self.screen, (255, 0, 0),
                             rover_screen_pos,
                             self.rover.collision_radius + pulse, 3)

        # Draw rover body with detailed design
        rad = math.radians(self.rover.angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        # Main body
        body_width, body_height = 35, 20
        body_corners = []
        for dx, dy in [(-body_width//2, -body_height//2),
                       (body_width//2, -body_height//2),
                       (body_width//2, body_height//2),
                       (-body_width//2, body_height//2)]:
            world_x = self.rover.x + dx * cos_a - dy * sin_a
            world_y = self.rover.y + dx * sin_a + dy * cos_a
            screen_pos = self.camera.apply(world_x, world_y)
            body_corners.append(screen_pos)

        body_color = (255, 100, 100) if self.rover.collision_warning else (80, 90, 110)
        pygame.draw.polygon(self.screen, body_color, body_corners)
        pygame.draw.polygon(self.screen, (200, 210, 220), body_corners, 2)

        # Draw 6 wheels
        for wx, wy in self.rover.wheel_positions:
            world_x = self.rover.x + wx * cos_a - wy * sin_a
            world_y = self.rover.y + wx * sin_a + wy * cos_a
            screen_pos = self.camera.apply(world_x, world_y)
            pygame.draw.circle(self.screen, (40, 40, 40), screen_pos, 4)
            pygame.draw.circle(self.screen, (120, 120, 120), screen_pos, 4, 1)

        # Solar panels
        panel_width, panel_height = 25, 12
        panel_corners = []
        for dx, dy in [(-panel_width//2, -panel_height//2 - 5),
                       (panel_width//2, -panel_height//2 - 5),
                       (panel_width//2, panel_height//2 - 5),
                       (-panel_width//2, panel_height//2 - 5)]:
            world_x = self.rover.x + dx * cos_a - dy * sin_a
            world_y = self.rover.y + dx * sin_a + dy * cos_a
            screen_pos = self.camera.apply(world_x, world_y)
            panel_corners.append(screen_pos)

        pygame.draw.polygon(self.screen, (20, 40, 80), panel_corners)
        pygame.draw.polygon(self.screen, (100, 150, 200), panel_corners, 2)

        # Camera/sensor on front
        sensor_offset = 18
        world_sensor_x = self.rover.x + sensor_offset * cos_a
        world_sensor_y = self.rover.y + sensor_offset * sin_a
        sensor_screen_pos = self.camera.apply(world_sensor_x, world_sensor_y)
        pygame.draw.circle(self.screen, (200, 100, 50), sensor_screen_pos, 5)
        pygame.draw.circle(self.screen, (255, 200, 100), sensor_screen_pos, 3)

        # Communication antenna
        world_antenna_x = self.rover.x - 10 * cos_a
        world_antenna_y = self.rover.y - 10 * sin_a
        world_antenna_top_x = world_antenna_x - 8 * sin_a
        world_antenna_top_y = world_antenna_y + 8 * cos_a
        antenna_screen_pos = self.camera.apply(world_antenna_x, world_antenna_y)
        antenna_top_screen_pos = self.camera.apply(world_antenna_top_x, world_antenna_top_y)
        pygame.draw.line(self.screen, (150, 150, 150),
                        antenna_screen_pos, antenna_top_screen_pos, 2)
        pygame.draw.circle(self.screen, (200, 50, 50), antenna_top_screen_pos, 3)

    def draw_dig_proximity_indicators_camera(self):
        """Draw proximity indicators for nearby dig sites with camera offset"""
        self.nearby_dig_sites = []

        for site in self.dig_sites:
            if not site.excavated:
                dist = math.sqrt((self.rover.x - site.x)**2 + (self.rover.y - site.y)**2)
                if dist < 80:  # Within excavation range
                    self.nearby_dig_sites.append(site)
                    screen_pos = self.camera.apply(site.x, site.y)

                    # Draw green circle around excavatable sites
                    pulse = int(3 + 2 * math.sin(time.time() * 3))
                    pygame.draw.circle(self.screen, (0, 255, 0),
                                     screen_pos, 35 + pulse, 3)

    def draw_battery_indicator(self):
        """Draw battery level indicator with timer"""
        # Position in top right, below GPR
        panel_x = self.width - 220
        panel_y = 280
        panel_width = 200
        panel_height = 100

        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (30, 30, 40), panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, (150, 150, 180), panel_rect, 3, border_radius=8)

        # Title
        font = pygame.font.Font(None, 24)
        title = font.render("BATTERY", True, (255, 255, 255))
        self.screen.blit(title, (panel_x + 10, panel_y + 10))

        # Battery box
        battery_box_x = panel_x + 20
        battery_box_y = panel_y + 40
        battery_box_width = 160
        battery_box_height = 30

        # Battery outline
        battery_rect = pygame.Rect(battery_box_x, battery_box_y, battery_box_width, battery_box_height)
        pygame.draw.rect(self.screen, (200, 200, 200), battery_rect, 2, border_radius=3)

        # Battery terminal (small bump on right)
        terminal_rect = pygame.Rect(battery_box_x + battery_box_width, battery_box_y + 8, 5, 14)
        pygame.draw.rect(self.screen, (200, 200, 200), terminal_rect)

        # Battery fill level
        battery_percent = self.battery_level / self.battery_capacity
        fill_width = int((battery_box_width - 4) * battery_percent)

        if fill_width > 0:
            fill_rect = pygame.Rect(battery_box_x + 2, battery_box_y + 2, fill_width, battery_box_height - 4)

            # Color based on battery level
            if battery_percent > 0.5:
                fill_color = (100, 255, 100)  # Green
            elif battery_percent > 0.25:
                fill_color = (255, 255, 100)  # Yellow
            else:
                fill_color = (255, 100, 100)  # Red

            pygame.draw.rect(self.screen, fill_color, fill_rect, border_radius=2)

        # Timer text or recharge status
        small_font = pygame.font.Font(None, 20)

        if self.is_recharging:
            # Show recharging status with progress
            recharge_percent = (self.recharge_timer / self.recharge_duration) * 100
            timer_text = small_font.render(f"CHARGING: {int(recharge_percent)}%", True, (100, 255, 100))
            self.screen.blit(timer_text, (panel_x + 10, panel_y + 75))
        else:
            # Show remaining time
            remaining_time = max(0, int(self.battery_level))
            timer_text = small_font.render(f"Time: {remaining_time}s", True, (255, 255, 255))
            self.screen.blit(timer_text, (panel_x + 10, panel_y + 75))

            # Warning if depleted
            if self.battery_depleted and not self.autopilot_active:
                warning_font = pygame.font.Font(None, 18)
                warning = warning_font.render("DEPLETED!", True, (255, 50, 50))
                self.screen.blit(warning, (panel_x + 110, panel_y + 75))

    def draw_excavation_progress(self):
        """Draw excavation progress indicator with camera offset"""
        if self.active_excavation:
            site = self.active_excavation

            # Convert world coordinates to screen coordinates
            screen_x, screen_y = self.camera.apply(site.x, site.y)

            # Progress bar above the dig site
            bar_width = 60
            bar_height = 8
            bar_x = screen_x - bar_width // 2
            bar_y = screen_y - 40

            # Background
            pygame.draw.rect(self.screen, (50, 50, 50),
                           (bar_x, bar_y, bar_width, bar_height))

            # Progress
            progress_width = int(bar_width * site.excavation_progress)
            pygame.draw.rect(self.screen, (100, 200, 100),
                           (bar_x, bar_y, progress_width, bar_height))

            # Border
            pygame.draw.rect(self.screen, (200, 200, 200),
                           (bar_x, bar_y, bar_width, bar_height), 2)

            # Text
            ui_font = pygame.font.Font(None, 24)
            progress_text = ui_font.render("Excavating...", True, (255, 255, 255))
            text_rect = progress_text.get_rect(center=(screen_x, bar_y - 15))
            self.screen.blit(progress_text, text_rect)

    def draw_selected_artifact_coords(self):
        """Draw coordinates for selected artifact from catalog"""
        if self.selected_artifact:
            # Draw small panel below artifact catalog
            panel_x = 20
            panel_y = 510  # Below catalog (300 + 200 + 10)
            panel_width = 300
            panel_height = 80

            # Panel background
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(self.screen, (30, 40, 30), panel_rect, border_radius=8)
            pygame.draw.rect(self.screen, (150, 200, 150), panel_rect, 3, border_radius=8)

            # Title
            font = pygame.font.Font(None, 24)
            title = font.render("SELECTED ARTIFACT", True, (200, 255, 200))
            self.screen.blit(title, (panel_x + 10, panel_y + 10))

            # Artifact ID
            small_font = pygame.font.Font(None, 20)
            display_type = self.selected_artifact.get_display_type().replace('_', ' ').title()
            id_text = small_font.render(f"{self.selected_artifact.id}: {display_type}", True, (255, 255, 255))
            self.screen.blit(id_text, (panel_x + 10, panel_y + 35))

            # Coordinates
            coords_text = small_font.render(
                f"Location: ({int(self.selected_artifact.x)}, {int(self.selected_artifact.y)})",
                True, (100, 255, 100))
            self.screen.blit(coords_text, (panel_x + 10, panel_y + 55))

    def draw_phase6_ui(self):
        """Draw Phase 6 specific UI elements"""
        # Draw ROVER STATUS panel in top left
        panel_width, panel_height = 350, 240
        panel_rect = pygame.Rect(20, 20, panel_width, panel_height)

        # Panel background with gradient effect
        pygame.draw.rect(self.screen, (20, 30, 40), panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 150, 200), panel_rect, 3, border_radius=10)

        # Title
        font = pygame.font.Font(None, 32)
        small_font = pygame.font.Font(None, 24)
        title = font.render("ROVER STATUS", True, (255, 255, 255))
        self.screen.blit(title, (30, 30))

        # Status information
        y_offset = 65
        detected_artifacts = sum(1 for a in self.artifacts if a.discovered)
        total_artifacts = len(self.artifacts)
        excavated_sites = sum(1 for s in self.dig_sites if s.excavated)

        collision_status = "⚠️ COLLISION!" if self.rover.collision_warning else "✓ Clear"
        collision_color = (255, 100, 100) if self.rover.collision_warning else (100, 255, 100)

        # Calculate distance from base
        distance_from_base = math.sqrt((self.rover.x - self.base_x)**2 + (self.rover.y - self.base_y)**2)

        # Autopilot status
        autopilot_status = "🚀 AUTOPILOT ACTIVE" if self.autopilot_active else "Manual Control"
        autopilot_color = (100, 255, 255) if self.autopilot_active else (200, 200, 200)

        status_items = [
            f"Position: ({int(self.rover.x)}, {int(self.rover.y)})",
            f"Distance from Base: {int(distance_from_base)}m",
            f"Heading: {int(self.rover.angle) % 360}°",
            f"Speed: {self.rover.speed:.1f} m/s",
            ("Hazard Status: " + collision_status, collision_color),
            ("Mode: " + autopilot_status, autopilot_color),
            f"Dig Sites: {len(self.dig_sites)} (Excavated: {excavated_sites})",
            f"Hazards Detected: {sum(1 for h in self.hazards if h.detected)}",
        ]

        # Only show artifact count when N is pressed
        if self.show_artifact_count:
            status_items.append(f"Artifacts: {detected_artifacts}/{total_artifacts} discovered")

        status_items.append(f"Nearby Sites: {len(self.nearby_dig_sites)}")

        for item in status_items:
            if isinstance(item, tuple):
                text = small_font.render(item[0], True, item[1])
            else:
                text = small_font.render(item, True, (220, 220, 220))
            self.screen.blit(text, (30, y_offset))
            y_offset += 18

        # Reset button
        button_y = y_offset + 10
        button_rect = pygame.Rect(30, button_y, 120, 30)
        self.reset_button_rect = button_rect  # Store for click detection

        # Button styling
        button_color = (60, 80, 100)
        border_color = (150, 180, 200)
        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=5)
        pygame.draw.rect(self.screen, border_color, button_rect, 2, border_radius=5)

        # Button text
        button_text = small_font.render("RESET GAME", True, (255, 255, 255))
        text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, text_rect)

        # Enhanced controls panel at bottom
        ui_panel = pygame.Rect(20, self.height - 160, self.width - 40, 140)
        pygame.draw.rect(self.screen, (20, 30, 40), ui_panel, border_radius=15)
        pygame.draw.rect(self.screen, (100, 120, 150), ui_panel, 3, border_radius=15)

        # Help section
        help_font = pygame.font.Font(None, 28)
        help_title = help_font.render("Phase 6: Realistic Hazards", True, (255, 255, 255))
        self.screen.blit(help_title, (30, self.height - 150))

        controls = [
            "WASD/Arrows: Move Rover (Camera Follows)  |  R: Return to Base (Auto)  |  G: Toggle GPR  |  P: Excavate",
            "C: Clear Sites  |  Q/E: Scroll Catalog  |  K: Keep-Out Zones  |  ESC: Exit",
            "Explore from BASE! Cyan line = Auto-path. Gold circles = Discovered artifacts."
        ]

        controls_font = pygame.font.Font(None, 20)
        y_pos = self.height - 125
        for control in controls:
            text = controls_font.render(control, True, (200, 220, 255))
            self.screen.blit(text, (30, y_pos))
            y_pos += 23

        # Debugging section
        debug_header_font = pygame.font.Font(None, 22)
        debug_header = debug_header_font.render("Debugging:", True, (255, 200, 100))
        self.screen.blit(debug_header, (30, y_pos))
        y_pos += 20

        debug_controls = [
            "N: Show Artifact Count  |  H: Show All Artifact Locations (gray X marks)"
        ]

        for control in debug_controls:
            text = controls_font.render(control, True, (255, 220, 150))
            self.screen.blit(text, (30, y_pos))
            y_pos += 23


if __name__ == "__main__":
    game = Phase6Game()
    game.run()
