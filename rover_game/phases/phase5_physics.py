"""
Phase 5: Advanced Physics with Hazard Keep-Out Regions
Enhanced collision system preventing rover from entering hazard zones
"""

import pygame
import math
import sys
import random
import time
import numpy as np
from .phase4_advanced import Phase4Game, AdvancedDigSite, ArtifactImage
from .phase3_gpr import Artifact, GPRSystem, ArtifactCatalog
from .phase2_graphics import Hazard, EnhancedDigSite


class PhysicsRover:
    """Enhanced rover with physics-based collision detection for hazard keep-out zones"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0  # Facing direction in degrees
        self.speed = 0
        self.max_speed = 5  # Increased from 3 for faster navigation
        self.rotation_speed = 2.5
        self.width = 40
        self.height = 25
        self.trail = []  # Store rover path
        self.dust_particles = []
        self.last_move_time = time.time()

        # Physics properties
        self.velocity_x = 0
        self.velocity_y = 0
        self.collision_radius = 25  # Collision detection radius

        # Collision feedback
        self.collision_warning = False
        self.warning_timer = 0

        # Rover components for detailed rendering
        self.wheel_positions = [
            (-15, -10), (-15, 10),  # Front wheels
            (0, -12), (0, 12),      # Middle wheels
            (15, -10), (15, 10)     # Rear wheels
        ]

    def update(self, keys, hazards):
        """Update rover position with physics-based hazard collision detection"""
        old_x, old_y = self.x, self.y
        old_speed = self.speed

        # Rotation
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle -= self.rotation_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle += self.rotation_speed

        # Movement with terrain resistance
        acceleration = 0.15
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + acceleration, self.max_speed)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - acceleration, -self.max_speed/2)
        else:
            self.speed *= 0.92  # Natural deceleration with terrain friction

        # Apply movement
        if abs(self.speed) > 0.1:
            rad = math.radians(self.angle)
            new_x = self.x + self.speed * math.cos(rad)
            new_y = self.y + self.speed * math.sin(rad)

            # Check hazard collisions with keep-out zone
            collision_result = self.check_hazard_keepout(new_x, new_y, hazards)

            if not collision_result['collision']:
                # No collision - move freely
                self.x = new_x
                self.y = new_y
                self.collision_warning = False

                # Add to trail
                if len(self.trail) == 0 or \
                   (self.x - self.trail[-1][0])**2 + (self.y - self.trail[-1][1])**2 > 80:
                    self.trail.append((int(self.x), int(self.y)))
                    if len(self.trail) > 100:
                        self.trail.pop(0)

                # Generate dust particles
                if abs(self.speed) > 1 and time.time() - self.last_move_time > 0.1:
                    self.generate_dust_particles()
                    self.last_move_time = time.time()
            else:
                # Collision detected - slide along boundary
                self.handle_collision_slide(collision_result, hazards)
                self.collision_warning = True
                self.warning_timer = time.time()
                self.speed *= 0.3  # Reduce speed significantly

        # Update dust particles
        self.update_dust_particles()

        # Reset collision warning after 0.5 seconds
        if self.collision_warning and time.time() - self.warning_timer > 0.5:
            self.collision_warning = False

    def check_hazard_keepout(self, x, y, hazards):
        """
        Check if rover position would enter hazard keep-out zone
        Returns dict with collision info
        """
        for hazard in hazards:
            # Calculate distance from rover center to hazard center
            dx = x - hazard.x
            dy = y - hazard.y
            distance = math.sqrt(dx * dx + dy * dy)

            # Keep-out radius = hazard radius + rover collision radius
            keepout_radius = hazard.radius + self.collision_radius

            if distance < keepout_radius:
                # Collision detected
                return {
                    'collision': True,
                    'hazard': hazard,
                    'distance': distance,
                    'keepout_radius': keepout_radius,
                    'normal_x': dx / distance if distance > 0 else 0,
                    'normal_y': dy / distance if distance > 0 else 0
                }

        return {'collision': False}

    def handle_collision_slide(self, collision_result, hazards):
        """
        Handle collision by sliding rover along keep-out boundary
        This creates a smooth pushing effect instead of hard stop
        """
        hazard = collision_result['hazard']
        keepout_radius = collision_result['keepout_radius']

        # Calculate vector from hazard to rover
        dx = self.x - hazard.x
        dy = self.y - hazard.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            # Normalize direction vector
            nx = dx / distance
            ny = dy / distance

            # Push rover to exact boundary of keep-out zone
            self.x = hazard.x + nx * keepout_radius
            self.y = hazard.y + ny * keepout_radius

            # Allow sliding tangent to the boundary
            # Calculate tangent direction
            rad = math.radians(self.angle)
            move_x = self.speed * math.cos(rad)
            move_y = self.speed * math.sin(rad)

            # Project movement onto tangent (perpendicular to normal)
            dot = move_x * nx + move_y * ny
            tangent_x = move_x - dot * nx
            tangent_y = move_y - dot * ny

            # Try to move along tangent
            test_x = self.x + tangent_x * 0.5
            test_y = self.y + tangent_y * 0.5

            # Only apply tangent movement if it doesn't cause another collision
            if not self.check_hazard_keepout(test_x, test_y, hazards)['collision']:
                self.x = test_x
                self.y = test_y

    def generate_dust_particles(self):
        """Generate dust particles behind rover"""
        rad = math.radians(self.angle + 180)  # Behind rover
        for _ in range(3):
            particle_x = self.x + random.uniform(-10, 10) + 20 * math.cos(rad)
            particle_y = self.y + random.uniform(-10, 10) + 20 * math.sin(rad)

            particle = {
                'x': particle_x,
                'y': particle_y,
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1),
                'life': 1.0,
                'decay': random.uniform(0.02, 0.05)
            }
            self.dust_particles.append(particle)

    def update_dust_particles(self):
        """Update dust particle physics"""
        for particle in self.dust_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= particle['decay']
            particle['vx'] *= 0.95
            particle['vy'] *= 0.95

            if particle['life'] <= 0:
                self.dust_particles.remove(particle)

    def draw(self, screen):
        """Draw enhanced rover with detailed graphics and collision warning"""
        # Draw trail with fading effect
        if len(self.trail) > 1:
            for i, pos in enumerate(self.trail):
                alpha = int(255 * (i / len(self.trail)) * 0.3)
                color = (120, 100, 80, alpha)
                pygame.draw.circle(screen, (120, 100, 80), pos, 3)

        # Draw dust particles
        for particle in self.dust_particles:
            alpha = int(255 * particle['life'])
            size = int(3 * particle['life'])
            if size > 0:
                color = (139, 119, 99)  # Dust color
                pygame.draw.circle(screen, color,
                                 (int(particle['x']), int(particle['y'])), size)

        # Draw collision warning indicator
        if self.collision_warning:
            # Pulsing red circle
            pulse = int(5 * (1 + math.sin(time.time() * 10)))
            pygame.draw.circle(screen, (255, 0, 0),
                             (int(self.x), int(self.y)),
                             self.collision_radius + pulse, 3)

        # Draw rover body with detailed design
        rad = math.radians(self.angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        # Main body (larger, more detailed)
        body_width, body_height = 35, 20
        body_corners = []
        for dx, dy in [(-body_width//2, -body_height//2),
                       (body_width//2, -body_height//2),
                       (body_width//2, body_height//2),
                       (-body_width//2, body_height//2)]:
            x = self.x + dx * cos_a - dy * sin_a
            y = self.y + dx * sin_a + dy * cos_a
            body_corners.append((x, y))

        # Body color changes if collision warning
        body_color = (255, 100, 100) if self.collision_warning else (80, 90, 110)
        pygame.draw.polygon(screen, body_color, body_corners)
        pygame.draw.polygon(screen, (200, 210, 220), body_corners, 2)

        # Draw 6 wheels
        for wx, wy in self.wheel_positions:
            wheel_x = self.x + wx * cos_a - wy * sin_a
            wheel_y = self.y + wx * sin_a + wy * cos_a
            pygame.draw.circle(screen, (40, 40, 40), (int(wheel_x), int(wheel_y)), 4)
            pygame.draw.circle(screen, (120, 120, 120), (int(wheel_x), int(wheel_y)), 4, 1)

        # Solar panels
        panel_width, panel_height = 25, 12
        panel_corners = []
        for dx, dy in [(-panel_width//2, -panel_height//2 - 5),
                       (panel_width//2, -panel_height//2 - 5),
                       (panel_width//2, panel_height//2 - 5),
                       (-panel_width//2, panel_height//2 - 5)]:
            x = self.x + dx * cos_a - dy * sin_a
            y = self.y + dx * sin_a + dy * cos_a
            panel_corners.append((x, y))

        pygame.draw.polygon(screen, (20, 40, 80), panel_corners)
        pygame.draw.polygon(screen, (100, 150, 200), panel_corners, 2)

        # Camera/sensor on front
        sensor_offset = 18
        sensor_x = self.x + sensor_offset * cos_a
        sensor_y = self.y + sensor_offset * sin_a
        pygame.draw.circle(screen, (200, 100, 50), (int(sensor_x), int(sensor_y)), 5)
        pygame.draw.circle(screen, (255, 200, 100), (int(sensor_x), int(sensor_y)), 3)

        # Communication antenna
        antenna_x = self.x - 10 * cos_a
        antenna_y = self.y - 10 * sin_a
        antenna_top_x = antenna_x - 8 * sin_a
        antenna_top_y = antenna_y + 8 * cos_a
        pygame.draw.line(screen, (150, 150, 150),
                        (int(antenna_x), int(antenna_y)),
                        (int(antenna_top_x), int(antenna_top_y)), 2)
        pygame.draw.circle(screen, (200, 50, 50), (int(antenna_top_x), int(antenna_top_y)), 3)


class Phase5Game(Phase4Game):
    """Phase 5 game with advanced physics and hazard keep-out zones"""

    def __init__(self):
        # Initialize Phase4Game first
        super().__init__()

        # Replace rover with physics-enabled version
        rover_x, rover_y = self.rover.x, self.rover.y
        self.rover = PhysicsRover(rover_x, rover_y)

        pygame.display.set_caption("Archaeological Rover - Phase 5: Keep-Out Zones")

        # Add visual feedback for keep-out zones
        self.show_keepout_zones = True

    def draw_keepout_zones(self):
        """Draw visual representation of hazard keep-out zones"""
        if self.show_keepout_zones:
            for hazard in self.hazards:
                keepout_radius = hazard.radius + self.rover.collision_radius

                # Draw semi-transparent keep-out zone
                s = pygame.Surface((keepout_radius * 2, keepout_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 0, 0, 30),
                                 (keepout_radius, keepout_radius), keepout_radius)
                screen_x = int(hazard.x - keepout_radius)
                screen_y = int(hazard.y - keepout_radius)
                self.screen.blit(s, (screen_x, screen_y))

                # Draw keep-out boundary circle
                pygame.draw.circle(self.screen, (255, 100, 100),
                                 (int(hazard.x), int(hazard.y)),
                                 keepout_radius, 2)

    def handle_events(self):
        """Enhanced event handling with keep-out zone toggle"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    # Check if artifact display is open
                    if self.artifact_display:
                        self.artifact_display = None
                        continue

                    # Check if reset button was clicked
                    if hasattr(self, 'reset_button_rect') and self.reset_button_rect.collidepoint(mouse_x, mouse_y):
                        self.reset_game()
                        continue

                    # Check for excavation clicks first
                    if self.handle_excavation_click(mouse_x, mouse_y):
                        continue

                    # Create dig sites anywhere on the map (but not in hazards)
                    can_place = True
                    for hazard in self.hazards:
                        if math.sqrt((hazard.x - mouse_x)**2 + (hazard.y - mouse_y)**2) < 60:
                            can_place = False
                            break

                    if can_place:
                        new_site = self.create_dig_site(mouse_x, mouse_y)
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

        return True

    def draw(self):
        """Enhanced drawing with keep-out zone visualization"""
        # First draw terrain background
        self.screen.fill((101, 86, 71))  # Base terrain color

        # Draw terrain patterns/textures
        random.seed(42)  # Consistent terrain
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(1, 3)
            color = (random.randint(80, 120), random.randint(70, 100), random.randint(60, 90))
            pygame.draw.circle(self.screen, color, (x, y), size)
        random.seed()  # Reset seed

        # Draw keep-out zones BEFORE other elements
        self.draw_keepout_zones()

        # Draw discovered artifacts as gold circles
        for artifact in self.artifacts:
            if artifact.discovered:
                pygame.draw.circle(self.screen, (255, 215, 0),
                                 (int(artifact.x), int(artifact.y)), 15, 3)

        # Draw dig sites
        for site in self.dig_sites:
            site.draw(self.screen)

        # Draw hazards
        for hazard in self.hazards:
            hazard.draw(self.screen)

        # Draw rover
        self.rover.draw(self.screen)

        # Draw GPR system
        self.gpr_system.draw(self.screen)

        # Draw artifact catalog
        self.artifact_catalog.draw_catalog_panel(self.screen, 20, 300, 300, 200)

        # Draw Phase 4 specific elements
        # Draw dig proximity indicators
        self.draw_dig_proximity_indicators()

        # Draw excavation progress
        self.draw_excavation_progress()

        # Draw artifact display (on top of everything)
        self.draw_artifact_display()

        # Draw Phase 5 UI
        self.draw_phase5_ui()

        # Update display
        pygame.display.flip()

    def draw_phase5_ui(self):
        """Draw Phase 5 specific UI with updated controls"""
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
        excavated_sites = sum(1 for s in self.dig_sites if s.excavated)

        collision_status = "⚠️ COLLISION!" if self.rover.collision_warning else "✓ Clear"
        collision_color = (255, 100, 100) if self.rover.collision_warning else (100, 255, 100)

        status_items = [
            f"Position: ({int(self.rover.x)}, {int(self.rover.y)})",
            f"Heading: {int(self.rover.angle) % 360}°",
            f"Speed: {self.rover.speed:.1f} m/s",
            ("Hazard Status: " + collision_status, collision_color),
            f"Dig Sites: {len(self.dig_sites)} (Excavated: {excavated_sites})",
            f"Hazards Detected: {sum(1 for h in self.hazards if h.detected)}",
            f"Artifacts Found: {detected_artifacts}",
            f"Nearby Sites: {len(self.nearby_dig_sites)}"
        ]

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
        help_title = help_font.render("Phase 5: Keep-Out Zones", True, (255, 255, 255))
        self.screen.blit(help_title, (30, self.height - 150))

        controls = [
            "WASD/Arrows: Move Rover  |  Left Click: Mark Dig Site  |  G: Toggle GPR  |  P: Excavate Near Site",
            "C: Clear Sites  |  Q/E: Scroll Catalog  |  K: Toggle Keep-Out Zones  |  ESC: Exit",
            "Green circles: Excavatable sites  |  Gold circles: Artifacts  |  Red zones: Hazard keep-out areas",
            "⚠️ Rover CANNOT enter red keep-out zones around hazards!"
        ]

        controls_font = pygame.font.Font(None, 20)
        y_pos = self.height - 125
        for control in controls:
            text = controls_font.render(control, True, (200, 220, 255))
            self.screen.blit(text, (30, y_pos))
            y_pos += 23


if __name__ == "__main__":
    game = Phase5Game()
    game.run()
