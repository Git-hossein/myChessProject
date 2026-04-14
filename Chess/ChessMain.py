"""
This is the main Python file. responsible for handling user input and displaying the current GameState object.
"""
import numpy as np
from Chess import ChessEngine
import pygame as p
import os

WIDTH = HEIGHT = 512
DIMENSION = 8 # 8X8 board
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def load_images():
    global IMAGES
    pieces = ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]
    img_dir: str = os.path.join(os.path.dirname(__file__), "chess_figures") # type: ignore
    for piece in pieces:
        image = p.image.load(os.path.join(img_dir, f"{piece}.png")).convert_alpha()
        IMAGES[piece] = p.transform.scale(image, (SQ_SIZE, SQ_SIZE))



def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill("white")
    gs = ChessEngine.GameState()
    load_images()
    running = True
    while running:
        for e in p.event.get() :
            if e.type == p.QUIT:
                running = False

        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()

def draw_game_state(screen, gs):
    """
    responsible for all graphics within a current GameState.
    """
    draw_board(screen)
    draw_pieces(screen, gs.board)


def draw_board(screen):
    # 1. Define colors in a list for easy toggling
    light_color = "antiquewhite2"
    dark_color = "darkolivegreen4"
    colors = [light_color, dark_color]

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            square = p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            p.draw.rect(screen, color, square)


def draw_pieces(screen, board: np.ndarray):
    """draw the pieces on the board"""
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            piece = board[i,j]
            if piece == "--": continue
            screen.blit(IMAGES[piece], (j * SQ_SIZE, i * SQ_SIZE))



if __name__ == '__main__':
    main()