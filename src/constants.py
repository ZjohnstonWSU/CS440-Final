import pygame

# Screen constants
WIDTH, HEIGHT = 900, 720
BOARD_SIZE = HEIGHT
SQUARE_SIZE = BOARD_SIZE // 8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
GREEN = (0, 196, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

# Indicator to track if the game has started
game_started = False

# Global variable to track the current selected difficulty
selected_difficulty = 'Easy'

# Initialize screen (move from main.py)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")
