"""
Phase 7: Exploration Mode
Building upon Phase 6 with hidden hazards that must be discovered through exploration
"""

import pygame
import math
import random
from .phase6_extended import Phase6Game, RealisticHazard, Camera


class ExplorationHazard(RealisticHazard):
    """Hazard that is initially hidden and must be discovered"""

    def __init__(self, x, y, hazard_type=None):
        super().__init__(x, y, hazard_type)
        self.discovered = False
        self.discovery_range = 150  # Rover must be within this range to discover

    def update_discovery(self, rover_x, rover_y):
        """Check if rover is close enough to discover this hazard"""
        if not self.discovered:
            distance = math.sqrt((self.x - rover_x)**2 + (self.y - rover_y)**2)
            if distance <= self.discovery_range:
                self.discovered = True
                return True  # Return True if newly discovered
        return False

    def draw(self, screen):
        """Draw hazard only if discovered"""
        if self.discovered:
            super().draw(screen)

    def get_keep_out_zone(self):
        """Get keep-out zone - only active if discovered"""
        if self.discovered:
            return (self.x, self.y, self.radius)
        return None


class Phase7Game(Phase6Game):
    """Phase 7 game with exploration and hidden hazards"""

    def __init__(self):
        # Initialize Phase6Game first
        super().__init__()

        pygame.display.set_caption("Archaeological Rover - Phase 7: Exploration Mode")

        # Replace hazards with exploration hazards
        self.generate_exploration_hazards()

        # Track discovery statistics
        self.total_hazards = len(self.hazards)
        self.discovered_hazards = 0
        self.show_discovery_stats = True

    def generate_exploration_hazards(self):
        """Generate hazards that are initially hidden"""
        hazard_types = ["rock", "boulder", "tree", "water", "pond"]
        num_hazards = random.randint(25, 35)

        self.hazards = []

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

            # Create exploration hazard
            hazard_type = random.choice(hazard_types)
            hazard = ExplorationHazard(x, y, hazard_type)
            self.hazards.append(hazard)

    def update(self):
        """Update game state with exploration mechanics"""
        # Check for hazard discoveries before parent update
        for hazard in self.hazards:
            if hazard.update_discovery(self.rover.x, self.rover.y):
                self.discovered_hazards += 1
                print(f"Discovered {hazard.type}! ({self.discovered_hazards}/{self.total_hazards} hazards found)")

        # Call parent update
        super().update()

    def check_collision(self, new_x, new_y):
        """Check collision only with discovered hazards"""
        for hazard in self.hazards:
            # Only check collision if hazard is discovered
            if hazard.discovered:
                keepout_radius = hazard.radius + self.rover.collision_radius
                distance = math.sqrt((new_x - hazard.x)**2 + (new_y - hazard.y)**2)
                if distance < keepout_radius:
                    return True
        return False

    def is_path_clear(self, x1, y1, x2, y2):
        """Check if a straight line path is clear of discovered keep-out zones"""
        # Sample points along the line
        num_samples = 20
        for i in range(num_samples + 1):
            t = i / num_samples
            check_x = x1 + (x2 - x1) * t
            check_y = y1 + (y2 - y1) * t

            # Check against discovered hazard keep-out zones
            for hazard in self.hazards:
                if hazard.discovered:  # Only check discovered hazards
                    keepout_radius = hazard.radius + self.rover.collision_radius + 10  # Add buffer
                    dist = math.sqrt((check_x - hazard.x)**2 + (check_y - hazard.y)**2)
                    if dist < keepout_radius:
                        return False

        return True

    def draw_keepout_zones_camera(self):
        """Draw keep-out zones only for discovered hazards"""
        if self.show_keepout_zones:
            for hazard in self.hazards:
                if hazard.discovered:  # Only draw if discovered
                    keepout_radius = hazard.radius + self.rover.collision_radius
                    screen_pos = self.camera.apply(hazard.x, hazard.y)
                    pygame.draw.circle(self.screen, (255, 0, 0), screen_pos, keepout_radius, 2)

    def draw_status_panel(self):
        """Enhanced status panel with discovery statistics"""
        # Draw parent status panel first
        super().draw_status_panel()

        # Add discovery stats if enabled
        if self.show_discovery_stats:
            panel_x = 20
            panel_y = 240  # Below main status panel

            # Discovery stats background
            stats_rect = pygame.Rect(panel_x, panel_y, 260, 60)
            pygame.draw.rect(self.screen, (30, 30, 40), stats_rect, border_radius=8)
            pygame.draw.rect(self.screen, (150, 150, 180), stats_rect, 3, border_radius=8)

            # Title
            font = pygame.font.Font(None, 22)
            title = font.render("EXPLORATION", True, (100, 200, 255))
            self.screen.blit(title, (panel_x + 10, panel_y + 8))

            # Discovery progress
            small_font = pygame.font.Font(None, 20)
            discovery_percent = (self.discovered_hazards / self.total_hazards) * 100 if self.total_hazards > 0 else 0
            stats_text = small_font.render(f"Hazards: {self.discovered_hazards}/{self.total_hazards} ({int(discovery_percent)}%)",
                                          True, (200, 200, 200))
            self.screen.blit(stats_text, (panel_x + 10, panel_y + 35))

    def draw_controls(self):
        """Enhanced controls showing exploration features"""
        # Draw parent controls first
        super().draw_controls()

        # Update controls text to mention exploration
        panel_x = 20
        panel_y = self.height - 180

        # Add note about exploration
        small_font = pygame.font.Font(None, 18)
        note = small_font.render("Explore to discover hidden hazards!", True, (255, 200, 100))
        self.screen.blit(note, (panel_x + 10, panel_y + 155))

    def reset_game(self):
        """Reset game and regenerate hidden hazards"""
        super().reset_game()
        # Regenerate exploration hazards on reset
        self.generate_exploration_hazards()
        self.total_hazards = len(self.hazards)
        self.discovered_hazards = 0

    def handle_keydown(self, event):
        """Handle keyboard input with Phase 7 specific controls"""
        # Call parent keydown handler
        super().handle_keydown(event)

        # Toggle discovery stats with 'E' key
        if event.key == pygame.K_e:
            self.show_discovery_stats = not self.show_discovery_stats
