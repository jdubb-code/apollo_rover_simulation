"""
Phase 1: Simple Graphics Archaeological Rover Game
Basic geometric shapes and fundamental rover mechanics
"""

import pygame
import math
import sys

class Rover:
    """Simple rover represented as a rectangle"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0  # Facing direction in degrees
        self.speed = 0
        self.max_speed = 2
        self.rotation_speed = 3
        self.width = 30
        self.height = 20
        self.trail = []  # Store rover path

    def update(self, keys):
        """Update rover position based on input"""
        # Rotation
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle -= self.rotation_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle += self.rotation_speed

        # Movement
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + 0.2, self.max_speed)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - 0.2, -self.max_speed/2)
        else:
            self.speed *= 0.95  # Natural deceleration

        # Apply movement
        if abs(self.speed) > 0.1:
            rad = math.radians(self.angle)
            self.x += self.speed * math.cos(rad)
            self.y += self.speed * math.sin(rad)

            # Add to trail every few pixels
            if len(self.trail) == 0 or \
               (self.x - self.trail[-1][0])**2 + (self.y - self.trail[-1][1])**2 > 100:
                self.trail.append((int(self.x), int(self.y)))
                # Limit trail length
                if len(self.trail) > 50:
                    self.trail.pop(0)

    def draw(self, screen):
        """Draw rover as a simple rectangle"""
        # Draw trail first
        if len(self.trail) > 1:
            for i in range(len(self.trail) - 1):
                alpha = int(255 * (i / len(self.trail)))
                color = (100, 100, 100, alpha)
                pygame.draw.circle(screen, (100, 100, 100), self.trail[i], 2)

        # Draw rover body
        rad = math.radians(self.angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        # Calculate corners of rotated rectangle
        corners = []
        for dx, dy in [(-self.width//2, -self.height//2),
                       (self.width//2, -self.height//2),
                       (self.width//2, self.height//2),
                       (-self.width//2, self.height//2)]:
            x = self.x + dx * cos_a - dy * sin_a
            y = self.y + dx * sin_a + dy * cos_a
            corners.append((x, y))

        pygame.draw.polygon(screen, (100, 150, 200), corners)

        # Draw direction indicator
        front_x = self.x + (self.width//2 + 10) * cos_a
        front_y = self.y + (self.width//2 + 10) * sin_a
        pygame.draw.line(screen, (255, 255, 255),
                        (self.x, self.y), (front_x, front_y), 3)

class DigSite:
    """Represents a potential archaeological dig site"""

    def __init__(self, x, y, site_id):
        self.x = x
        self.y = y
        self.id = site_id
        self.radius = 15

    def draw(self, screen):
        """Draw dig site marker"""
        pygame.draw.circle(screen, (255, 200, 0), (int(self.x), int(self.y)), self.radius, 3)
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 5)

        # Draw site ID
        font = pygame.font.Font(None, 24)
        text = font.render(str(self.id), True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x, self.y - 25))
        screen.blit(text, text_rect)

class Phase1Game:
    """Main game class for Phase 1"""

    def __init__(self):
        pygame.init()
        self.width = 1000
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Archaeological Rover - Phase 1: Simple Graphics")
        self.clock = pygame.time.Clock()

        # Game objects
        self.rover = Rover(self.width // 2, self.height // 2)
        self.dig_sites = []
        self.next_site_id = 1

        # UI font
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Add dig site at mouse position
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    new_site = DigSite(mouse_x, mouse_y, self.next_site_id)
                    self.dig_sites.append(new_site)
                    self.next_site_id += 1
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_c:
                    # Clear all dig sites
                    self.dig_sites.clear()
                    self.next_site_id = 1
        return True

    def update(self):
        """Update game state"""
        keys = pygame.key.get_pressed()
        self.rover.update(keys)

    def draw(self):
        """Render the game"""
        # Clear screen with terrain color
        self.screen.fill((120, 100, 80))  # Brown terrain

        # Draw coordinate grid (subtle)
        for x in range(0, self.width, 50):
            pygame.draw.line(self.screen, (100, 80, 60), (x, 0), (x, self.height), 1)
        for y in range(0, self.height, 50):
            pygame.draw.line(self.screen, (100, 80, 60), (0, y), (self.width, y), 1)

        # Draw dig sites
        for site in self.dig_sites:
            site.draw(self.screen)

        # Draw rover
        self.rover.draw(self.screen)

        # Draw UI
        self.draw_ui()

        pygame.display.flip()

    def draw_ui(self):
        """Draw user interface elements"""
        # Status panel background
        panel_rect = pygame.Rect(10, 10, 300, 120)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), panel_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), panel_rect, 2)

        # Rover status
        y_offset = 20
        texts = [
            f"Rover Position: ({int(self.rover.x)}, {int(self.rover.y)})",
            f"Heading: {int(self.rover.angle) % 360}°",
            f"Speed: {self.rover.speed:.1f}",
            f"Dig Sites Marked: {len(self.dig_sites)}"
        ]

        for text in texts:
            surface = self.small_font.render(text, True, (255, 255, 255))
            self.screen.blit(surface, (20, y_offset))
            y_offset += 20

        # Controls help
        help_y = self.height - 80
        help_texts = [
            "Controls: WASD or Arrow Keys to move",
            "Left Click: Mark dig site  |  C: Clear sites  |  ESC: Exit"
        ]

        for text in help_texts:
            surface = self.small_font.render(text, True, (255, 255, 255))
            self.screen.blit(surface, (20, help_y))
            help_y += 20

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
    game = Phase1Game()
    game.run()