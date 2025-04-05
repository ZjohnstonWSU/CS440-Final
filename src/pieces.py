import pygame
from constants import SQUARE_SIZE

# Chess piece class
class ChessPiece:
    def __init__(self, color, type, image):
        self.color = color
        self.type = type
        self.image = None

        if image:
            self.image = pygame.image.load(image)
            self.image = pygame.transform.scale(self.image, (SQUARE_SIZE, SQUARE_SIZE))
