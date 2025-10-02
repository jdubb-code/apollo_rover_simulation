"""
Phase 3: GPR Integration Archaeological Rover Game
Ground Penetrating Radar interface and artifact detection system
"""

import pygame
import math
import sys
import random
import time
import numpy as np
from .phase2_graphics import EnhancedRover, Hazard, EnhancedDigSite

class Artifact:
    """Hidden archaeological artifact detected by GPR"""

    def __init__(self, x, y, depth, artifact_type="pottery"):
        self.x = x
        self.y = y
        self.depth = depth  # Depth in meters (0.5 to 3.0)
        self.type = artifact_type
        self.discovered = False
        self.confidence = 0.0  # GPR detection confidence (0.0 to 1.0)
        self.scan_count = 0

        # Artifact properties
        self.size = random.uniform(0.1, 0.8)  # Size in meters
        self.signal_strength = self.calculate_signal_strength()

        # Variable confidence limits based on depth and size
        self.max_confidence = self.calculate_max_confidence()

        # Visual properties
        self.id = None
        self.discovery_time = None

    def calculate_signal_strength(self):
        """Calculate GPR signal strength based on depth and size"""
        # Deeper artifacts have weaker signals
        depth_factor = max(0.1, 1.0 - (self.depth / 3.0))
        # Larger artifacts have stronger signals
        size_factor = min(1.0, self.size / 0.5)
        return depth_factor * size_factor * random.uniform(0.7, 1.0)

    def calculate_max_confidence(self):
        """Calculate maximum achievable confidence based on artifact properties"""
        # Base confidence potential based on depth
        if self.depth < 0.8:  # Shallow artifacts
            depth_confidence = 0.95
        elif self.depth < 1.5:  # Medium depth
            depth_confidence = 0.75
        elif self.depth < 2.2:  # Deep artifacts
            depth_confidence = 0.60
        else:  # Very deep artifacts
            depth_confidence = 0.45

        # Size factor - larger artifacts have higher max confidence
        size_confidence = min(1.0, 0.5 + (self.size / 0.8) * 0.5)

        # Combined maximum confidence
        max_conf = depth_confidence * size_confidence

        # Add some randomness for realism (±10%)
        variation = random.uniform(-0.1, 0.1)
        return max(0.25, min(0.95, max_conf + variation))  # Clamp between 25% and 95%

    def get_display_type(self):
        """Get the artifact type to display based on confidence level"""
        confidence_threshold = 0.5  # 50% confidence required to identify type
        if self.confidence >= confidence_threshold:
            return self.type
        else:
            return "unknown"

    def get_gpr_signature(self, rover_x, rover_y, scan_range=50):
        """Get GPR signature if artifact is in range"""
        distance = math.sqrt((self.x - rover_x)**2 + (self.y - rover_y)**2)

        if distance <= scan_range:
            # Signal strength decreases with distance
            distance_factor = max(0.0, 1.0 - (distance / scan_range))
            signal = self.signal_strength * distance_factor

            # Add some noise
            noise = random.uniform(-0.1, 0.1)
            return max(0.0, signal + noise)
        return 0.0

    def update_confidence(self, signal_strength, rover_x, rover_y):
        """Update detection confidence based on repeated scans and detection quality"""
        if signal_strength > 0:
            self.scan_count += 1

            # Calculate distance factor for detection position quality
            distance = math.sqrt((self.x - rover_x)**2 + (self.y - rover_y)**2)
            scan_range = 50  # From get_gpr_signature default

            # More precise detection zones
            if distance <= 10:  # Very close - direct detection
                detection_quality = 1.0
                position_bonus = 1.5  # 50% bonus for direct detection
            elif distance <= 20:  # Close - good detection
                detection_quality = 0.8
                position_bonus = 1.2  # 20% bonus for close detection
            elif distance <= 35:  # Medium - moderate detection
                detection_quality = 0.4
                position_bonus = 1.0  # No bonus
            else:  # Far - edge detection
                detection_quality = 0.1
                position_bonus = 0.5  # Penalty for edge detection

            # Much smaller base increase for more gradual buildup
            base_increase = signal_strength * 0.03 * detection_quality * position_bonus

            # First few scans give less confidence (realistic early detection)
            if self.scan_count <= 2:
                early_scan_penalty = 0.3  # 70% reduction for first scans
            elif self.scan_count <= 5:
                early_scan_penalty = 0.6  # 40% reduction for early scans
            else:
                early_scan_penalty = 1.0  # Full confidence increase for repeated scans

            # Diminishing returns - but less severe to allow confidence building
            current_ratio = self.confidence / self.max_confidence
            diminishing_factor = max(0.4, 1.0 - (current_ratio * 0.5))

            # Apply all factors
            confidence_increase = base_increase * early_scan_penalty * diminishing_factor

            # Apply confidence increase, capped by max_confidence
            new_confidence = self.confidence + confidence_increase
            self.confidence = min(self.max_confidence, new_confidence)

            # Lower discovery threshold - artifacts can be "discovered" with lower confidence
            discovery_threshold = max(0.25, self.max_confidence * 0.4)
            if self.confidence > discovery_threshold and not self.discovered:
                self.discovered = True
                self.discovery_time = time.time()

class GPRSystem:
    """Ground Penetrating Radar system for artifact detection"""

    def __init__(self, screen_width, screen_height):
        self.width = 300
        self.height = 250
        self.x = screen_width - self.width - 20
        self.y = 20

        # GPR display properties
        self.scan_data = np.zeros((50, 30))  # 2D array for subsurface data
        self.depth_layers = 10
        self.scan_range = 80
        self.active = True

        # Visual properties
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # Scan animation
        self.scan_line_pos = 0
        self.scan_direction = 1

    def update_scan(self, rover_x, rover_y, artifacts):
        """Update GPR scan based on rover position and artifacts"""
        if not self.active:
            return

        # Clear previous scan data with some persistence
        self.scan_data *= 0.95

        # Generate subsurface data
        for i in range(50):
            for j in range(30):
                # Convert grid position to world coordinates
                world_x = rover_x + (i - 25) * 3
                world_y = rover_y + (j - 15) * 3

                # Check for artifacts at this position
                for artifact in artifacts:
                    distance = math.sqrt((artifact.x - world_x)**2 + (artifact.y - world_y)**2)
                    if distance < 15:  # Artifact detection radius
                        # Calculate depth representation
                        depth_layer = int(artifact.depth * 5)  # Scale depth to display
                        if depth_layer < 30:
                            signal = artifact.get_gpr_signature(rover_x, rover_y, self.scan_range)
                            if signal > 0:
                                self.scan_data[i][min(j + depth_layer, 29)] = signal
                                artifact.update_confidence(signal, rover_x, rover_y)

        # Add some background noise
        noise_level = 0.05
        self.scan_data += np.random.random((50, 30)) * noise_level

        # Update scan line animation
        self.scan_line_pos += self.scan_direction * 2
        if self.scan_line_pos >= 48 or self.scan_line_pos <= 2:
            self.scan_direction *= -1

    def draw(self, screen):
        """Draw GPR interface"""
        if not self.active:
            return

        # Main GPR panel background
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (10, 20, 30), panel_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 150, 200), panel_rect, 3, border_radius=8)

        # Title
        title = self.font.render("GROUND PENETRATING RADAR", True, (255, 255, 255))
        screen.blit(title, (self.x + 10, self.y + 10))

        # GPR display area
        display_rect = pygame.Rect(self.x + 10, self.y + 40, 280, 150)
        pygame.draw.rect(screen, (0, 10, 20), display_rect)
        pygame.draw.rect(screen, (50, 100, 150), display_rect, 2)

        # Draw subsurface data
        cell_width = 280 / 50
        cell_height = 150 / 30

        for i in range(50):
            for j in range(30):
                intensity = self.scan_data[i][j]
                if intensity > 0:
                    # Color based on signal strength
                    if intensity > 0.7:
                        color = (255, 100, 100)  # Strong signal - red
                    elif intensity > 0.4:
                        color = (255, 200, 100)  # Medium signal - yellow
                    else:
                        color = (100, 255, 100)  # Weak signal - green

                    alpha = min(255, int(intensity * 255))

                    cell_rect = pygame.Rect(
                        self.x + 10 + i * cell_width,
                        self.y + 40 + j * cell_height,
                        cell_width + 1,
                        cell_height + 1
                    )

                    # Create surface for alpha blending
                    cell_surface = pygame.Surface((cell_width + 1, cell_height + 1))
                    cell_surface.set_alpha(alpha)
                    cell_surface.fill(color)
                    screen.blit(cell_surface, cell_rect)

        # Draw scanning line
        scan_x = self.x + 10 + self.scan_line_pos * cell_width
        pygame.draw.line(screen, (255, 255, 255),
                        (scan_x, self.y + 40), (scan_x, self.y + 190), 2)

        # Depth scale
        for i in range(6):
            depth = i * 0.5  # Every 0.5 meters
            y_pos = self.y + 40 + i * 25
            depth_text = self.small_font.render(f"{depth}m", True, (200, 200, 200))
            screen.blit(depth_text, (self.x + 285, y_pos))

        # Status information
        status_y = self.y + 200
        status_items = [
            "SCAN: ACTIVE",
            f"RANGE: {self.scan_range}m",
        ]

        for i, item in enumerate(status_items):
            text = self.small_font.render(item, True, (150, 255, 150))
            screen.blit(text, (self.x + 10 + i * 90, status_y))

        # Signal strength indicator
        pygame.draw.rect(screen, (50, 50, 50), (self.x + 10, self.y + 220, 100, 15))
        current_signal = np.max(self.scan_data)
        if current_signal > 0:
            bar_width = int(100 * min(1.0, current_signal))
            color = (255, 100, 100) if current_signal > 0.7 else (255, 200, 100)
            pygame.draw.rect(screen, color, (self.x + 10, self.y + 220, bar_width, 15))

        signal_text = self.small_font.render("SIGNAL", True, (200, 200, 200))
        screen.blit(signal_text, (self.x + 120, self.y + 222))

class ArtifactCatalog:
    """System for cataloging discovered artifacts"""

    def __init__(self):
        self.discovered_artifacts = []
        self.next_id = 1
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)

        # Scrolling functionality
        self.scroll_offset = 0  # How many items to scroll down
        self.max_visible_items = 4  # Maximum artifacts visible at once

        # Notification system
        self.notifications = []  # List of notification messages
        self.notification_timer = 0

    def add_artifact(self, artifact):
        """Add a newly discovered artifact to catalog"""
        if artifact not in self.discovered_artifacts:
            artifact.id = f"ART-{self.next_id:03d}"
            self.next_id += 1
            self.discovered_artifacts.append(artifact)
            return True
        return False

    def scroll_up(self):
        """Scroll up in the artifact list"""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1

    def scroll_down(self):
        """Scroll down in the artifact list"""
        max_scroll = max(0, len(self.discovered_artifacts) - self.max_visible_items)
        if self.scroll_offset < max_scroll:
            self.scroll_offset += 1

    def can_scroll_up(self):
        """Check if can scroll up"""
        return self.scroll_offset > 0

    def can_scroll_down(self):
        """Check if can scroll down"""
        max_scroll = max(0, len(self.discovered_artifacts) - self.max_visible_items)
        return self.scroll_offset < max_scroll

    def draw_catalog_panel(self, screen, x, y, width, height):
        """Draw scrollable artifact catalog panel"""
        panel_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, (20, 30, 20), panel_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 200, 100), panel_rect, 3, border_radius=8)

        # Title
        title = self.font.render("ARTIFACT CATALOG", True, (255, 255, 255))
        screen.blit(title, (x + 10, y + 10))

        # Create clipping area for artifact list (leave space for title and total count)
        list_area = pygame.Rect(x + 5, y + 35, width - 10, height - 65)

        # Set clipping to keep content inside panel
        screen.set_clip(list_area)

        # Calculate visible artifacts based on scroll offset (newest first)
        total_artifacts = len(self.discovered_artifacts)

        # Reverse the list so newest artifacts appear first
        reversed_artifacts = list(reversed(self.discovered_artifacts))

        start_index = self.scroll_offset
        end_index = min(start_index + self.max_visible_items, total_artifacts)

        visible_artifacts = reversed_artifacts[start_index:end_index]

        # Draw artifact list
        y_offset = y + 40
        for i, artifact in enumerate(visible_artifacts):
            display_type = artifact.get_display_type().replace('_', ' ').title()
            artifact_info = f"{artifact.id}: {display_type}"
            depth_info = f"Depth: {artifact.depth:.1f}m"
            conf_info = f"Conf: {artifact.confidence:.0%} (Max: {artifact.max_confidence:.0%})"

            text = self.small_font.render(artifact_info, True, (200, 255, 200))
            screen.blit(text, (x + 10, y_offset))

            # Color-code confidence based on level
            conf_ratio = artifact.confidence / artifact.max_confidence if artifact.max_confidence > 0 else 0
            if conf_ratio > 0.8:
                conf_color = (100, 255, 100)  # Green - high confidence
            elif conf_ratio > 0.5:
                conf_color = (255, 255, 100)  # Yellow - medium confidence
            else:
                conf_color = (255, 150, 150)  # Red - low confidence

            detail_text = self.small_font.render(f"{depth_info} | {conf_info}", True, conf_color)
            screen.blit(detail_text, (x + 10, y_offset + 20))

            y_offset += 45

        # Remove clipping
        screen.set_clip(None)

        # Scroll indicators
        if self.can_scroll_up():
            up_arrow = self.small_font.render("▲", True, (255, 255, 255))
            screen.blit(up_arrow, (x + width - 25, y + 35))

        if self.can_scroll_down():
            down_arrow = self.small_font.render("▼", True, (255, 255, 255))
            screen.blit(down_arrow, (x + width - 25, y + height - 45))

        # Total count and scroll info
        if total_artifacts > 0:
            showing_text = f"Showing {start_index + 1}-{end_index} of {total_artifacts}"
            info_text = self.small_font.render(showing_text, True, (150, 150, 150))
            screen.blit(info_text, (x + 10, y + height - 25))

        # Draw notifications
        self.draw_notifications(screen, x, y, width, height)

    def add_notification(self, message, duration=3.0):
        """Add a notification message to display"""
        import time
        self.notifications.append({
            'message': message,
            'start_time': time.time(),
            'duration': duration
        })

    def update_notifications(self):
        """Update and remove expired notifications"""
        import time
        current_time = time.time()
        self.notifications = [n for n in self.notifications
                            if current_time - n['start_time'] < n['duration']]

    def draw_notifications(self, screen, x, y, width, height):
        """Draw notification messages"""
        import time
        current_time = time.time()

        # Draw active notifications below the catalog
        notification_y = y + height + 10
        for notification in self.notifications:
            time_elapsed = current_time - notification['start_time']
            if time_elapsed < notification['duration']:
                # Fade out effect
                alpha = max(0, 1 - (time_elapsed / notification['duration']))
                color_value = int(255 * alpha)

                # Notification background
                notif_rect = pygame.Rect(x, notification_y, width, 25)
                pygame.draw.rect(screen, (20, 60, 20), notif_rect, border_radius=5)
                pygame.draw.rect(screen, (0, 200, 0), notif_rect, 2, border_radius=5)

                # Notification text
                text = self.small_font.render(notification['message'], True,
                                            (color_value, 255, color_value))
                screen.blit(text, (x + 10, notification_y + 5))

                notification_y += 30

class Phase3Game:
    """Phase 3 game with GPR integration and artifact detection"""

    def __init__(self):
        pygame.init()
        self.width = 1400
        self.height = 900
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Archaeological Rover - Phase 3: GPR Integration")
        self.clock = pygame.time.Clock()

        # Game objects
        self.rover = EnhancedRover(self.width // 2, self.height // 2)
        self.dig_sites = []
        self.hazards = self.generate_hazards()
        self.artifacts = self.generate_artifacts()
        self.next_site_id = 1

        # GPR and catalog systems
        self.gpr_system = GPRSystem(self.width, self.height)
        self.artifact_catalog = ArtifactCatalog()

        # UI fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        self.large_font = pygame.font.Font(None, 48)

    def generate_hazards(self):
        """Generate random hazards across the terrain"""
        hazards = []
        for _ in range(12):
            x = random.randint(100, self.width - 100)
            y = random.randint(100, self.height - 100)
            hazard_type = random.choice(["rock", "crevasse", "slope"])
            hazards.append(Hazard(x, y, hazard_type))
        return hazards

    def generate_artifacts(self):
        """Generate hidden artifacts for GPR detection"""
        artifacts = []
        artifact_types = ["pottery", "tool", "ornament", "bone", "metal", "stone_carving"]

        for _ in range(20):
            x = random.randint(200, self.width - 200)
            y = random.randint(200, self.height - 200)
            depth = random.uniform(0.3, 2.5)  # 0.3 to 2.5 meters deep
            artifact_type = random.choice(artifact_types)

            # Don't place artifacts too close to hazards
            too_close = False
            for hazard in self.hazards:
                if math.sqrt((hazard.x - x)**2 + (hazard.y - y)**2) < 80:
                    too_close = True
                    break

            if not too_close:
                artifacts.append(Artifact(x, y, depth, artifact_type))

        return artifacts

    def reset_game(self):
        """Reset the game state to initial conditions"""
        # Store initial rover position
        initial_x = self.width // 2
        initial_y = self.height // 2

        # Reset rover position and state
        self.rover.x = initial_x
        self.rover.y = initial_y
        self.rover.angle = 0
        self.rover.speed = 0
        self.rover.trail = []

        # Clear dig sites
        self.dig_sites = []
        self.next_site_id = 1

        # Reset all artifacts
        for artifact in self.artifacts:
            artifact.discovered = False
            artifact.confidence = 0.0
            artifact.scan_count = 0
            artifact.id = None
            artifact.discovery_time = None
            # Recalculate max confidence (has randomness component)
            artifact.max_confidence = artifact.calculate_max_confidence()

        # Reset GPR system
        self.gpr_system.scan_data = np.zeros((50, 30))
        self.gpr_system.scan_line_pos = 0
        self.gpr_system.scan_direction = 1

        # Reset hazard detection status
        for hazard in self.hazards:
            hazard.detected = False

        # Reset artifact catalog
        self.artifact_catalog.discovered_artifacts = []

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    # Check if reset button was clicked
                    if hasattr(self, 'reset_button_rect') and self.reset_button_rect.collidepoint(mouse_x, mouse_y):
                        self.reset_game()
                        continue

                    # Don't place sites in UI areas
                    if mouse_x > self.width - 350:  # GPR area
                        continue

                    # Check for nearby discovered artifacts
                    nearby_artifacts = [a for a in self.artifacts
                                      if a.discovered and
                                      math.sqrt((a.x - mouse_x)**2 + (a.y - mouse_y)**2) < 50]

                    if nearby_artifacts:
                        # Mark as excavation site if artifact is nearby
                        new_site = EnhancedDigSite(mouse_x, mouse_y, self.next_site_id)
                        new_site.artifact_site = True  # Special marking
                        self.dig_sites.append(new_site)
                        self.next_site_id += 1
                    else:
                        # Regular dig site
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
                elif event.key == pygame.K_g:
                    # Toggle GPR
                    self.gpr_system.active = not self.gpr_system.active
                elif event.key == pygame.K_q:
                    # Scroll up in artifact catalog
                    self.artifact_catalog.scroll_up()
                elif event.key == pygame.K_e:
                    # Scroll down in artifact catalog
                    self.artifact_catalog.scroll_down()
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

        # Update GPR system
        self.gpr_system.update_scan(self.rover.x, self.rover.y, self.artifacts)

        # Check for newly discovered artifacts
        for artifact in self.artifacts:
            if artifact.discovered and self.artifact_catalog.add_artifact(artifact):
                print(f"New artifact discovered: {artifact.id} - {artifact.type}")

        # Update notifications
        self.artifact_catalog.update_notifications()

    def draw_terrain(self):
        """Draw enhanced terrain background"""
        # Base terrain color with subtle texture
        self.screen.fill((101, 86, 71))

        # Add terrain texture
        for _ in range(800):
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

    def draw_artifacts(self):
        """Draw discovered artifacts on terrain"""
        for artifact in self.artifacts:
            if artifact.discovered:
                # Draw artifact marker
                pygame.draw.circle(self.screen, (255, 215, 0), (int(artifact.x), int(artifact.y)), 8)
                pygame.draw.circle(self.screen, (200, 165, 0), (int(artifact.x), int(artifact.y)), 8, 2)

                # Draw artifact ID if cataloged
                if artifact.id:
                    id_text = self.small_font.render(artifact.id, True, (255, 255, 255))
                    id_rect = id_text.get_rect(center=(artifact.x, artifact.y - 20))

                    # Background for text
                    bg_rect = id_rect.inflate(6, 2)
                    pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect, border_radius=3)
                    self.screen.blit(id_text, id_rect)

    def draw(self):
        """Render the enhanced game"""
        self.draw_terrain()

        # Draw hazards
        for hazard in self.hazards:
            hazard.draw(self.screen)

        # Draw discovered artifacts
        self.draw_artifacts()

        # Draw dig sites
        for site in self.dig_sites:
            site.draw(self.screen)

        # Draw rover
        self.rover.draw(self.screen)

        # Draw GPR system
        self.gpr_system.draw(self.screen)

        # Draw artifact catalog
        self.artifact_catalog.draw_catalog_panel(self.screen, 20, 300, 300, 200)

        # Draw enhanced UI
        self.draw_enhanced_ui()

        pygame.display.flip()

    def draw_enhanced_ui(self):
        """Draw enhanced user interface"""
        # Enhanced status panel
        panel_width, panel_height = 350, 220  # Increased height for reset button
        panel_rect = pygame.Rect(20, 20, panel_width, panel_height)

        # Panel background with gradient effect
        pygame.draw.rect(self.screen, (20, 30, 40), panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 150, 200), panel_rect, 3, border_radius=10)

        # Title
        title = self.font.render("ROVER STATUS", True, (255, 255, 255))
        self.screen.blit(title, (30, 30))

        # Status information
        y_offset = 65
        detected_artifacts = sum(1 for a in self.artifacts if a.discovered)
        status_items = [
            f"Position: ({int(self.rover.x)}, {int(self.rover.y)})",
            f"Heading: {int(self.rover.angle) % 360}°",
            f"Speed: {self.rover.speed:.1f} m/s",
            f"Dig Sites: {len(self.dig_sites)}",
            f"Hazards Detected: {sum(1 for h in self.hazards if h.detected)}",
            f"Artifacts Found: {detected_artifacts}"
        ]

        for item in status_items:
            text = self.small_font.render(item, True, (220, 220, 220))
            self.screen.blit(text, (30, y_offset))
            y_offset += 18

        # Reset button
        self.reset_button_rect = pygame.Rect(30, y_offset + 10, 100, 30)
        pygame.draw.rect(self.screen, (60, 80, 120), self.reset_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, (120, 160, 200), self.reset_button_rect, 2, border_radius=5)

        reset_text = self.small_font.render("RESET", True, (255, 255, 255))
        text_rect = reset_text.get_rect(center=self.reset_button_rect.center)
        self.screen.blit(reset_text, text_rect)

        # Warning system
        detected_hazards = [h for h in self.hazards if h.detected]
        if detected_hazards:
            warning_rect = pygame.Rect(20, 260, panel_width, 40)
            pygame.draw.rect(self.screen, (200, 50, 50), warning_rect, border_radius=5)
            pygame.draw.rect(self.screen, (255, 100, 100), warning_rect, 2, border_radius=5)

            warning_text = self.small_font.render("⚠ HAZARDS DETECTED", True, (255, 255, 255))
            text_rect = warning_text.get_rect(center=warning_rect.center)
            self.screen.blit(warning_text, text_rect)

        # Enhanced controls help
        help_panel = pygame.Rect(20, self.height - 140, 600, 120)
        pygame.draw.rect(self.screen, (40, 40, 40), help_panel, border_radius=8)
        pygame.draw.rect(self.screen, (200, 200, 200), help_panel, 2, border_radius=8)

        help_title = self.small_font.render("CONTROLS", True, (255, 255, 255))
        self.screen.blit(help_title, (30, self.height - 130))

        controls = [
            "WASD/Arrows: Move Rover  |  Left Click: Mark Dig Site  |  G: Toggle GPR",
            "C: Clear Sites  |  Q/E: Scroll Catalog  |  ESC: Exit",
            "Gold circles: Discovered artifacts  |  Red outlines: Detected hazards"
        ]

        y_pos = self.height - 105
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
    game = Phase3Game()
    game.run()