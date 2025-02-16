import pygame
import sys
from constants import *
from gameHelpers import init_board, handle_click, draw_board, draw_piece

pygame.init()

#Main game loop
def main():
    init_board()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(pygame.mouse.get_pos())
        draw_board()
        draw_piece()
        pygame.display.flip()
        
if __name__ == "__main__":
    main()