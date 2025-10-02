"""
Phase 2: Realistic Graphics Archaeological Rover Game
Enhanced visuals, detailed rover design, and hazard detection system
"""

import pygame
import math
import sys
import random
import time

class EnhancedRover:
    """Realistic rover with detailed graphics and enhanced physics"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0  # Facing direction in degrees
        self.speed = 0
        self.max_speed = 3
        self.rotation_speed = 2.5
        self.width = 40
        self.height = 25
        self.trail = []  # Store rover path
        self.dust_particles = []
        self.last_move_time = time.time()

        # Rover components for detailed rendering
        self.wheel_positions = [
            (-15, -10), (-15, 10),  # Front wheels
            (0, -12), (0, 12),      # Middle wheels
            (15, -10), (15, 10)     # Rear wheels
        ]

    def update(self, keys, hazards):
        """Update rover position and check for hazards"""
        old_x, old_y = self.x, self.y

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

            # Check hazard collisions
            collision = self.check_hazard_collision(new_x, new_y, hazards)
            if not collision:
                self.x = new_x
                self.y = new_y

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
                # Stop if hitting hazard
                self.speed *= 0.5

        # Update dust particles
        self.update_dust_particles()

    def check_hazard_collision(self, x, y, hazards):
        """Check if rover position collides with any hazards"""
        rover_rect = pygame.Rect(x - self.width//2, y - self.height//2,
                                self.width, self.height)

        for hazard in hazards:
            if hazard.get_rect().colliderect(rover_rect):
                return True
        return False

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
        """Draw enhanced rover with detailed graphics"""
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

        pygame.draw.polygon(screen, (70, 90, 120), body_corners)  # Main body
        pygame.draw.polygon(screen, (50, 70, 100), body_corners, 3)  # Body outline

        # Draw wheels
        for wheel_dx, wheel_dy in self.wheel_positions:
            wheel_x = self.x + wheel_dx * cos_a - wheel_dy * sin_a
            wheel_y = self.y + wheel_dx * sin_a + wheel_dy * cos_a

            pygame.draw.circle(screen, (40, 40, 40), (int(wheel_x), int(wheel_y)), 6)
            pygame.draw.circle(screen, (60, 60, 60), (int(wheel_x), int(wheel_y)), 6, 2)

        # Draw solar panels
        panel_width, panel_height = 20, 8
        panel_corners = []
        for dx, dy in [(-panel_width//2, -panel_height//2),
                       (panel_width//2, -panel_height//2),
                       (panel_width//2, panel_height//2),
                       (-panel_width//2, panel_height//2)]:
            x = self.x + dx * cos_a - dy * sin_a
            y = self.y + dx * sin_a + dy * cos_a
            panel_corners.append((x, y))

        pygame.draw.polygon(screen, (30, 50, 80), panel_corners)
        pygame.draw.polygon(screen, (100, 150, 200), panel_corners, 2)

        # Draw antenna/communication equipment
        antenna_x = self.x + 15 * cos_a
        antenna_y = self.y + 15 * sin_a
        pygame.draw.circle(screen, (200, 200, 200), (int(antenna_x), int(antenna_y)), 3)

        # Direction indicator (enhanced)
        front_x = self.x + (body_width//2 + 15) * cos_a
        front_y = self.y + (body_width//2 + 15) * sin_a
        pygame.draw.line(screen, (255, 255, 100),
                        (self.x, self.y), (front_x, front_y), 4)

class Hazard:
    """Environmental hazard that blocks rover movement"""

    def __init__(self, x, y, hazard_type="rock"):
        self.x = x
        self.y = y
        self.type = hazard_type
        self.detected = False

        if hazard_type == "rock":
            self.width = random.randint(20, 40)
            self.height = random.randint(15, 35)
            self.color = (80, 70, 60)
        elif hazard_type == "crevasse":
            self.width = random.randint(60, 100)
            self.height = random.randint(10, 20)
            self.color = (20, 20, 30)
        elif hazard_type == "slope":
            self.width = random.randint(40, 80)
            self.height = random.randint(30, 60)
            self.color = (100, 85, 70)

        # Calculate radius for circular collision detection (used in Phase 5)
        self.radius = max(self.width, self.height) // 2

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
        """Draw hazard with detection highlighting"""
        rect = self.get_rect()

        if self.type == "rock":
            # Draw irregular rock shape
            pygame.draw.ellipse(screen, self.color, rect)
            pygame.draw.ellipse(screen, (60, 50, 40), rect, 3)
        elif self.type == "crevasse":
            # Draw dark crevasse
            pygame.draw.rect(screen, self.color, rect)
            pygame.draw.rect(screen, (10, 10, 15), rect, 2)
        elif self.type == "slope":
            # Draw sloped terrain
            pygame.draw.ellipse(screen, self.color, rect)
            pygame.draw.ellipse(screen, (80, 65, 50), rect, 2)

        # Highlight if detected
        if self.detected:
            pygame.draw.rect(screen, (255, 0, 0), rect, 3)

class EnhancedDigSite:
    """Enhanced dig site with professional graphics"""

    def __init__(self, x, y, site_id):
        self.x = x
        self.y = y
        self.id = site_id
        self.radius = 20
        self.pulse_timer = 0

    def update(self):
        """Update visual effects"""
        self.pulse_timer += 0.1

    def draw(self, screen):
        """Draw enhanced dig site marker"""
        # Pulsing effect
        pulse_size = int(3 + 2 * math.sin(self.pulse_timer))

        # Outer ring
        pygame.draw.circle(screen, (255, 200, 0),
                          (int(self.x), int(self.y)), self.radius + pulse_size, 4)

        # Inner ring
        pygame.draw.circle(screen, (255, 255, 100),
                          (int(self.x), int(self.y)), 12, 3)

        # Center marker
        pygame.draw.circle(screen, (255, 255, 0),
                          (int(self.x), int(self.y)), 6)

        # Site ID with background
        font = pygame.font.Font(None, 28)
        text = font.render(str(self.id), True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x, self.y - 35))

        # Text background
        bg_rect = text_rect.inflate(10, 4)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2, border_radius=5)

        screen.blit(text, text_rect)

class Phase2Game:
    """Enhanced Phase 2 game with realistic graphics"""

    def __init__(self):
        pygame.init()
        self.width = 1200
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Archaeological Rover - Phase 2: Realistic Graphics")
        self.clock = pygame.time.Clock()

        # Game objects
        self.rover = EnhancedRover(self.width // 2, self.height // 2)
        self.dig_sites = []
        self.hazards = self.generate_hazards()
        self.next_site_id = 1

        # UI fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        self.large_font = pygame.font.Font(None, 48)

    def generate_hazards(self):
        """Generate random hazards across the terrain, avoiding rover spawn"""
        hazards = []
        rover_spawn_x = self.width // 2
        rover_spawn_y = self.height // 2
        min_distance_from_spawn = 150  # Keep hazards at least 150 pixels from spawn

        attempts = 0
        max_attempts = 100  # Prevent infinite loop

        while len(hazards) < 15 and attempts < max_attempts:
            x = random.randint(100, self.width - 100)
            y = random.randint(100, self.height - 100)

            # Check distance from rover spawn point
            distance_from_spawn = math.sqrt((x - rover_spawn_x)**2 + (y - rover_spawn_y)**2)

            if distance_from_spawn >= min_distance_from_spawn:
                hazard_type = random.choice(["rock", "crevasse", "slope"])
                hazards.append(Hazard(x, y, hazard_type))

            attempts += 1

        return hazards

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    # Don't place sites too close to hazards
                    can_place = True
                    for hazard in self.hazards:
                        if math.sqrt((hazard.x - mouse_x)**2 + (hazard.y - mouse_y)**2) < 60:
                            can_place = False
                            break

                    if can_place:
                        new_site = EnhancedDigSite(mouse_x, mouse_y, self.next_site_id)
                        self.dig_sites.append(new_site)
                        self.next_site_id += 1
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_c:
                    self.dig_sites.clear()
                    self.next_site_id = 1
        return True

    def update(self):
        """Update game state"""
        keys = pygame.key.get_pressed()
        self.rover.update(keys, self.hazards)

        # Update dig sites
        for site in self.dig_sites:
            site.update()

        # Update hazard detection
        for hazard in self.hazards:
            hazard.is_near_rover(self.rover.x, self.rover.y)

    def draw_terrain(self):
        """Draw enhanced terrain background"""
        # Base terrain color with subtle texture
        self.screen.fill((101, 86, 71))

        # Add terrain texture with random dots
        for _ in range(500):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            color_variation = random.randint(-20, 20)
            color = (101 + color_variation, 86 + color_variation, 71 + color_variation)
            pygame.draw.circle(self.screen, color, (x, y), 1)

        # Enhanced coordinate grid
        grid_color = (90, 75, 60)
        for x in range(0, self.width, 100):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.height), 1)
        for y in range(0, self.height, 100):
            pygame.draw.line(self.screen, grid_color, (0, y), (self.width, y), 1)

    def draw(self):
        """Render the enhanced game"""
        self.draw_terrain()

        # Draw hazards
        for hazard in self.hazards:
            hazard.draw(self.screen)

        # Draw dig sites
        for site in self.dig_sites:
            site.draw(self.screen)

        # Draw rover
        self.rover.draw(self.screen)

        # Draw enhanced UI
        self.draw_enhanced_ui()

        pygame.display.flip()

    def draw_enhanced_ui(self):
        """Draw enhanced user interface"""
        # Enhanced status panel
        panel_width, panel_height = 350, 160
        panel_rect = pygame.Rect(20, 20, panel_width, panel_height)

        # Panel background with gradient effect
        pygame.draw.rect(self.screen, (20, 30, 40), panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 150, 200), panel_rect, 3, border_radius=10)

        # Title
        title = self.font.render("ROVER STATUS", True, (255, 255, 255))
        self.screen.blit(title, (30, 30))

        # Status information
        y_offset = 65
        status_items = [
            f"Position: ({int(self.rover.x)}, {int(self.rover.y)})",
            f"Heading: {int(self.rover.angle) % 360}°",
            f"Speed: {self.rover.speed:.1f} m/s",
            f"Dig Sites: {len(self.dig_sites)}",
            f"Hazards Detected: {sum(1 for h in self.hazards if h.detected)}"
        ]

        for item in status_items:
            text = self.small_font.render(item, True, (220, 220, 220))
            self.screen.blit(text, (30, y_offset))
            y_offset += 22

        # Warning system
        detected_hazards = [h for h in self.hazards if h.detected]
        if detected_hazards:
            warning_rect = pygame.Rect(20, 200, panel_width, 50)
            pygame.draw.rect(self.screen, (200, 50, 50), warning_rect, border_radius=5)
            pygame.draw.rect(self.screen, (255, 100, 100), warning_rect, 2, border_radius=5)

            warning_text = self.small_font.render("⚠ HAZARDS DETECTED", True, (255, 255, 255))
            text_rect = warning_text.get_rect(center=warning_rect.center)
            self.screen.blit(warning_text, text_rect)

        # Enhanced controls help
        help_panel = pygame.Rect(20, self.height - 120, 500, 100)
        pygame.draw.rect(self.screen, (40, 40, 40), help_panel, border_radius=8)
        pygame.draw.rect(self.screen, (200, 200, 200), help_panel, 2, border_radius=8)

        help_title = self.small_font.render("CONTROLS", True, (255, 255, 255))
        self.screen.blit(help_title, (30, self.height - 110))

        controls = [
            "WASD/Arrows: Move Rover  |  Left Click: Mark Dig Site",
            "C: Clear Sites  |  ESC: Exit  |  Red Outline: Detected Hazard"
        ]

        y_pos = self.height - 85
        for control in controls:
            text = pygame.font.Font(None, 22).render(control, True, (200, 200, 200))
            self.screen.blit(text, (30, y_pos))
            y_pos += 20

    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Phase2Game()
    game.run()