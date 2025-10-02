#!/usr/bin/env python3
"""
Simple pygame test to check if display works
"""

import pygame
import sys

def test_pygame():
    print("Testing pygame display...")

    try:
        pygame.init()
        print("Pygame initialized")

        # Try to create a small test window
        screen = pygame.display.set_mode((400, 300))
        pygame.display.set_caption("Pygame Test Window")
        print("Display created successfully")

        # Fill with a color so you can see it
        screen.fill((0, 128, 255))  # Blue background
        pygame.display.flip()
        print("Window should now be visible - a blue 400x300 window")

        # Keep window open for 5 seconds
        clock = pygame.time.Clock()
        for i in range(300):  # 5 seconds at 60fps
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Window closed by user")
                    pygame.quit()
                    return
            clock.tick(60)

        print("Test completed - closing window")
        pygame.quit()

    except Exception as e:
        print(f"Error: {e}")
        print("Display might not be available")

if __name__ == "__main__":
    test_pygame()