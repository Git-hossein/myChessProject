"""
This is the main Python file. responsible for handling user input and displaying the current GameState object.
"""

from Chess import ChessEngine
import pygame as pg
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
        image = pg.image.load(os.path.join(img_dir, f"{piece}.png")).convert_alpha()
        IMAGES[piece] = pg.transform.scale(image, (SQ_SIZE, SQ_SIZE))



def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    screen.fill("white")
    gs = ChessEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False
    load_images()
    sq_selected = () # the square selected by the player (row, col)
    player_clicks = [] # keeps tracks of player clicks (first click and second click). two tuples at most
    running = True

    waiting_for_promotion = False
    while running:

        for e in pg.event.get() :

            if waiting_for_promotion:
                if e.type == pg.KEYDOWN:
                    choice = None
                    turn = "w" if gs.white_to_play else "b"
                    if e.key == pg.K_q: choice = f"{turn}Q"
                    if e.key == pg.K_r: choice = f"{turn}R"
                    if e.key == pg.K_b: choice = f"{turn}B"
                    if e.key == pg.K_n: choice = f"{turn}N"

                    if choice:
                        print(f"Promoted to {choice}!")
                        waiting_for_promotion = False
                        promotion_move = None
                        gs.board[pending_promotion_move.end_sq_row][pending_promotion_move.end_sq_col] = choice
                        move_made = True  # Trigger valid move recalculation
                        gs.white_to_play = not gs.white_to_play

                continue

            match e.type:

                case pg.QUIT:
                    running = False

                case e_type if e_type == ChessEngine.GameConfig.PAWN_PROMOTION_EVENT:
                    print("we're going into lock mode")
                    waiting_for_promotion = True
                    pending_promotion_move = e.move

                case pg.KEYDOWN if e.key == pg.K_LEFT:
                    gs.undo_last_move()
                    move_made = True

                case pg.MOUSEBUTTONDOWN:
                    x, y = pg.mouse.get_pos()
                    col = x // SQ_SIZE
                    row = y // SQ_SIZE
                    if sq_selected == (row, col): # selecting the same square twice -> reset (deselect)
                        sq_selected = ()
                        player_clicks = []

                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)
                        if len(player_clicks) == 2:
                            move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                            print(move.get_chess_notation())
                            if move in valid_moves:
                                gs.make_move(move, is_real_move = True)
                                move_made = True
                                sq_selected = ()
                                player_clicks = []
                            else:
                                player_clicks = [sq_selected]

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False
        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        pg.display.flip()

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
            square = pg.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            pg.draw.rect(screen, color, square)


def draw_pieces(screen, board: list[list[int]]):
    """draw the pieces on the board"""
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            piece = board[i][j]
            if piece == "--": continue
            screen.blit(IMAGES[piece], (j * SQ_SIZE, i * SQ_SIZE))



if __name__ == '__main__':
    main()