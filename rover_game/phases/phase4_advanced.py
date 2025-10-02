"""
Phase 4: Advanced Features Archaeological Rover Game
Enhanced gameplay with dig tool, hub system, and advanced mechanics
"""

import pygame
import math
import sys
import random
import time
import numpy as np
from .phase3_gpr import Phase3Game, Artifact, GPRSystem, ArtifactCatalog
from .phase2_graphics import EnhancedRover, Hazard, EnhancedDigSite

class AdvancedDigSite(EnhancedDigSite):
    """Enhanced dig site with excavation capabilities"""

    def __init__(self, x, y, site_id):
        super().__init__(x, y, site_id)
        self.excavated = False
        self.excavation_progress = 0.0  # 0.0 to 1.0
        self.found_artifacts = []  # List of artifacts found at this site
        self.artifact_site = False  # True if this site has nearby artifacts

    def start_excavation(self):
        """Start the excavation process"""
        if not self.excavated:
            self.excavation_progress = 0.1
            return True
        return False

    def update_excavation(self, dt):
        """Update excavation progress"""
        if 0 < self.excavation_progress < 1.0:
            self.excavation_progress += dt * 0.5  # Takes ~2 seconds to excavate
            if self.excavation_progress >= 1.0:
                self.excavation_progress = 1.0
                self.excavated = True
                return True  # Excavation complete
        return False

class ArtifactImage:
    """Represents an artifact image display"""

    def __init__(self, artifact):
        self.artifact = artifact
        self.display_type = artifact.get_display_type()
        self.image_type = self.get_artifact_image_type(self.display_type)
        self.display_time = 0
        self.fade_in = True

    def get_artifact_image_type(self, artifact_type):
        """Get appropriate image representation for artifact type"""
        image_map = {
            "pottery": "🏺",
            "tool": "🔧",
            "ornament": "💍",
            "bone": "🦴",
            "metal": "⚱️",
            "stone_carving": "🗿",
            "unknown": "❓"  # Question mark for unknown artifacts
        }
        return image_map.get(artifact_type, "📦")

    def draw(self, screen, x, y, width, height):
        """Draw the artifact image display"""
        # Background panel
        panel_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, (40, 20, 10), panel_rect, border_radius=10)
        pygame.draw.rect(screen, (200, 150, 100), panel_rect, 3, border_radius=10)

        # Title
        font = pygame.font.Font(None, 32)
        title = font.render(f"ARTIFACT DISCOVERED", True, (255, 255, 255))
        screen.blit(title, (x + 20, y + 20))

        # Artifact details
        details_font = pygame.font.Font(None, 24)
        details = [
            f"Type: {self.display_type.replace('_', ' ').title()}",
            f"Depth: {self.artifact.depth:.1f}m",
            f"Size: {self.artifact.size:.2f}m",
            f"ID: {self.artifact.id or 'Unassigned'}"
        ]

        y_offset = 60
        for detail in details:
            text = details_font.render(detail, True, (220, 220, 220))
            screen.blit(text, (x + 20, y + y_offset))
            y_offset += 25

        # Large artifact icon
        icon_font = pygame.font.Font(None, 120)
        icon = icon_font.render(self.image_type, True, (255, 200, 100))
        icon_rect = icon.get_rect(center=(x + width - 100, y + height // 2))
        screen.blit(icon, icon_rect)

        # Close instruction
        close_text = details_font.render("Click anywhere to close", True, (150, 150, 150))
        screen.blit(close_text, (x + 20, y + height - 30))

class Phase4Game(Phase3Game):
    """Phase 4 game with advanced features"""

    def __init__(self):
        super().__init__()
        pygame.display.set_caption("Archaeological Rover - Phase 4: Advanced Features")

        # Enhanced dig sites
        self.dig_sites = []  # Will contain AdvancedDigSite objects

        # Excavation system
        self.active_excavation = None
        self.excavation_timer = 0

        # Proximity-based digging
        self.nearby_dig_sites = []
        self.dig_proximity_radius = 40  # Pixels - how close rover needs to be

        # Artifact image display
        self.artifact_display = None
        self.display_timer = 0

        # Enhanced UI
        self.ui_font = pygame.font.Font(None, 24)

    def create_dig_site(self, x, y):
        """Create an advanced dig site"""
        site = AdvancedDigSite(x, y, self.next_site_id)

        # Check for nearby discovered artifacts
        nearby_artifacts = [a for a in self.artifacts
                          if a.discovered and
                          math.sqrt((a.x - x)**2 + (a.y - y)**2) < 50]

        if nearby_artifacts:
            site.artifact_site = True
            site.found_artifacts = nearby_artifacts

        return site

    def handle_excavation_click(self, mouse_x, mouse_y):
        """Handle clicks on excavated dig sites to view artifacts"""
        for site in self.dig_sites:
            distance = math.sqrt((site.x - mouse_x)**2 + (site.y - mouse_y)**2)
            if distance < 30:  # Click radius
                if site.excavated and site.found_artifacts:
                    # Show artifact image
                    artifact = site.found_artifacts[0]  # Show first artifact
                    self.artifact_display = ArtifactImage(artifact)
                    self.display_timer = time.time()
                    return True
        return False

    def update_nearby_dig_sites(self):
        """Update list of dig sites within proximity range"""
        self.nearby_dig_sites = []
        for site in self.dig_sites:
            if not site.excavated and site.artifact_site:
                distance = math.sqrt((site.x - self.rover.x)**2 + (site.y - self.rover.y)**2)
                if distance <= self.dig_proximity_radius:
                    self.nearby_dig_sites.append(site)

    def excavate_nearby_site(self):
        """Excavate the nearest dig site when P is pressed"""
        if self.nearby_dig_sites and not self.active_excavation:
            # Find closest site
            closest_site = min(self.nearby_dig_sites,
                             key=lambda site: math.sqrt((site.x - self.rover.x)**2 + (site.y - self.rover.y)**2))

            # Start excavation
            if closest_site.start_excavation():
                self.active_excavation = closest_site
                print(f"Excavating dig site at ({closest_site.x}, {closest_site.y})")
                return True
        return False


    def handle_events(self):
        """Enhanced event handling with dig functionality"""
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

                    # Don't place sites in UI areas (removed restriction for full-map clicking)
                    # if mouse_x > self.width - 350:  # GPR area - REMOVED
                    #     continue

                    # Create dig sites anywhere on the map
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

        return True

    def update(self):
        """Enhanced update with excavation progress"""
        # Update proximity detection for dig sites
        self.update_nearby_dig_sites()

        # Normal game update (manual rover control always enabled)
        super().update()

        # Update excavation progress
        if self.active_excavation:
            dt = 1/60  # Assuming 60 FPS
            if self.active_excavation.update_excavation(dt):
                # Excavation complete
                if self.active_excavation.found_artifacts:
                    # Show artifact discovery
                    artifact = self.active_excavation.found_artifacts[0]
                    self.artifact_display = ArtifactImage(artifact)
                    self.display_timer = time.time()

                    # Add notification to artifact log
                    artifact_type = artifact.get_display_type().replace('_', ' ').title()
                    message = f"Retrieved: {artifact.id} - {artifact_type}"
                    self.artifact_catalog.add_notification(message)

                self.active_excavation = None

    def draw_excavation_progress(self):
        """Draw excavation progress indicator"""
        if self.active_excavation:
            site = self.active_excavation

            # Progress bar above the dig site
            bar_width = 60
            bar_height = 8
            bar_x = site.x - bar_width // 2
            bar_y = site.y - 40

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
            progress_text = self.ui_font.render("Excavating...", True, (255, 255, 255))
            text_rect = progress_text.get_rect(center=(site.x, bar_y - 15))
            self.screen.blit(progress_text, text_rect)

    def draw_dig_proximity_indicators(self):
        """Draw indicators for dig sites within proximity range"""
        # Draw nearby dig sites with special highlighting
        for site in self.nearby_dig_sites:
            # Pulsing green circle for excavatable sites
            pulse = int(10 * (1 + math.sin(time.time() * 4)))
            pygame.draw.circle(self.screen, (0, 255, 0), (int(site.x), int(site.y)), 35 + pulse, 3)

            # "PRESS P" label
            press_p_text = self.ui_font.render("PRESS P", True, (0, 255, 0))
            text_rect = press_p_text.get_rect(center=(site.x, site.y - 50))
            self.screen.blit(press_p_text, text_rect)

        # Draw proximity radius around rover (faint circle for reference)
        if self.nearby_dig_sites:
            pygame.draw.circle(self.screen, (100, 100, 100),
                             (int(self.rover.x), int(self.rover.y)),
                             self.dig_proximity_radius, 1)

    def draw_artifact_display(self):
        """Draw artifact image display"""
        if self.artifact_display:
            # Center the display
            display_width = 400
            display_height = 300
            x = (self.width - display_width) // 2
            y = (self.height - display_height) // 2

            self.artifact_display.draw(self.screen, x, y, display_width, display_height)

    def draw(self):
        """Enhanced drawing with new UI elements"""
        # First draw terrain background
        self.screen.fill((101, 86, 71))  # Base terrain color

        # Draw terrain patterns/textures
        import random
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(1, 3)
            color = (random.randint(80, 120), random.randint(70, 100), random.randint(60, 90))
            pygame.draw.circle(self.screen, color, (x, y), size)

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

        # Draw Phase 4 UI instead of Phase 3 enhanced UI
        self.draw_phase4_ui()

        # Update display
        pygame.display.flip()

    def draw_phase4_ui(self):
        """Draw Phase 4 specific UI with updated controls"""
        # Draw ROVER STATUS panel in top left (same as Phase 3)
        panel_width, panel_height = 350, 220
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

        status_items = [
            f"Position: ({int(self.rover.x)}, {int(self.rover.y)})",
            f"Heading: {int(self.rover.angle) % 360}°",
            f"Speed: {self.rover.speed:.1f} m/s",
            f"Dig Sites: {len(self.dig_sites)} (Excavated: {excavated_sites})",
            f"Hazards Detected: {sum(1 for h in self.hazards if h.detected)}",
            f"Artifacts Found: {detected_artifacts}",
            f"Nearby Sites: {len(self.nearby_dig_sites)}"
        ]

        for item in status_items:
            text = small_font.render(item, True, (220, 220, 220))
            self.screen.blit(text, (30, y_offset))
            y_offset += 18

        # Reset button (from Phase 3)
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

        # Enhanced controls panel at bottom (same as before but updated)
        ui_panel = pygame.Rect(20, self.height - 140, self.width - 40, 120)
        pygame.draw.rect(self.screen, (20, 30, 40), ui_panel, border_radius=15)
        pygame.draw.rect(self.screen, (100, 120, 150), ui_panel, 3, border_radius=15)

        # Help section
        help_font = pygame.font.Font(None, 28)
        help_title = help_font.render("Controls & Status:", True, (255, 255, 255))
        self.screen.blit(help_title, (30, self.height - 130))

        controls = [
            "WASD/Arrows: Move Rover  |  Left Click: Mark Dig Site  |  G: Toggle GPR  |  P: Excavate Near Site",
            "C: Clear Sites  |  Q/E: Scroll Catalog  |  ESC: Exit",
            "Green circles: Excavatable sites nearby  |  Gold circles: Discovered artifacts"
        ]

        controls_font = pygame.font.Font(None, 22)
        y_pos = self.height - 105
        for control in controls:
            text = controls_font.render(control, True, (200, 220, 255))
            self.screen.blit(text, (30, y_pos))
            y_pos += 25

    def reset_game(self):
        """Enhanced reset including new Phase 4 features"""
        super().reset_game()

        # Reset Phase 4 specific elements
        self.active_excavation = None
        self.excavation_timer = 0
        self.artifact_display = None
        self.display_timer = 0

        # Reset proximity-based dig tool state
        self.nearby_dig_sites = []

        # Convert all dig sites to AdvancedDigSite
        self.dig_sites = []

if __name__ == "__main__":
    game = Phase4Game()
    game.run()