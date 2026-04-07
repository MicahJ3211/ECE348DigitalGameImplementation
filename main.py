#!/usr/bin/env python3
"""
Card Game Core - Main Entry Point
A strategic two-player card game built with Python and pygame.
"""

import pygame
import sys
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from src.game import Game


def main():
    """Initialize and run the game."""
    # Initialize pygame
    pygame.init()
    
    # Create window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Card Game")
    
    # Create and run game
    game = Game(screen)
    game.run()
    
    # Cleanup
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
