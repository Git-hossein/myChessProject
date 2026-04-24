"""
This is the main Python file. responsible for handling user input and displaying the current GameState object.
"""
from typing import Literal

from Chess import ChessEngine
import pygame as pg
import os
import math

WIDTH = HEIGHT = 512
DIMENSION = 8 # 8X8 board
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
SURFACES = {"light": {}, "dark": {}}

def load_images():
    global IMAGES
    pieces = ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]
    img_dir: str = os.path.join(os.path.dirname(__file__), "chess_figures") # type: ignore
    for piece in pieces:
        image = pg.image.load(os.path.join(img_dir, f"{piece}.png")).convert_alpha()
        IMAGES[piece] = pg.transform.scale(image, (SQ_SIZE, SQ_SIZE))

def load_highlight_squares():
    def get_tinted_surface(color, alpha=100):
        s = pg.Surface((SQ_SIZE, SQ_SIZE)).convert()
        s.set_alpha(alpha)
        s.fill(color)
        return s

    global SURFACES
    SURFACES["light"]["select_surface"] = get_tinted_surface("blue")
    SURFACES["light"]["highlight_surface"] = get_tinted_surface("yellow")
    SURFACES["dark"]["select_surface"] = get_tinted_surface("lightskyblue1")
    SURFACES["dark"]["highlight_surface"] = get_tinted_surface("gold")


def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    screen.fill("white")
    gs = ChessEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False
    load_images()
    load_highlight_squares()
    sq_selected = () # the square selected by the player (row, col)
    player_clicks = [] # keeps tracks of player clicks (first click and second click). two tuples at most
    running = True
    animate = False
    game_over = False
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
                    animate = False
                    game_over = False

                case pg.KEYDOWN if e.key == pg.K_r:
                    gs = ChessEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    move_made = False
                    sq_selected = ()
                    player_clicks = []

                case pg.MOUSEBUTTONDOWN:
                    if not game_over:
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
                                print(move)
                                for i in range(len(valid_moves)):
                                    if valid_moves[i] == move:
                                        gs.make_move(valid_moves[i], is_real_move = True)
                                        move_made = True
                                        sq_selected = ()
                                        player_clicks = []
                                        animate = True
                                        break

                                else:
                                    print("invaliedmove")
                                    player_clicks = [sq_selected]

        if move_made:
            if animate:
                animate_piece(move, screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False

        draw_game_state(screen, gs, valid_moves, sq_selected)
        if gs.checkmate or gs.stalemate:
            game_over = True
            winner = "b" if gs.white_to_play and gs.checkmate else "stalemate" if gs.stalemate else "w"
            draw_game_over(screen, (gs.white_king_pos, gs.black_king_pos), winner) # type: ignore

        clock.tick(MAX_FPS)
        pg.display.flip()



def highlight_squares(screen, gs, valid_moves, sq_selected):
    """highlight squares"""
    if sq_selected != ():
        r, c = sq_selected
        color = "light" if (r + c) % 2 == 0 else "dark"
        if gs.board[r][c][0] == ("w" if gs.white_to_play else "b"):
            screen.blit(SURFACES[color]["select_surface"], (c*SQ_SIZE, r*SQ_SIZE))
        for move in valid_moves:
            if move.start_sq_row == r and move.start_sq_col == c:
                screen.blit(SURFACES[color]["highlight_surface"], (move.end_sq_col * SQ_SIZE, move.end_sq_row  * SQ_SIZE))


#
# def animate_piece(move, screen, board, clock, animation_style = None):
#     dR = move.end_sq_row - move.start_sq_row
#     dC = move.end_sq_col - move.start_sq_col
#     frames_per_square = 10
#     frame_count = max(abs(dR), abs(dC)) * frames_per_square
#     for frame in range(frame_count + 1):
#         r, c = move.start_sq_row + dR * frame/frame_count, move.start_sq_col + dC * frame/frame_count
#         draw_board(screen)
#         draw_pieces_except(screen, board, move.end_sq_row, move.end_sq_col) #IMPORTANT: the movement has logically already happened (so the piece is at endsq, endcol)
#         piece = board[move.end_sq_row][move.end_sq_col]
#         screen.blit(IMAGES[piece], (c * SQ_SIZE, r * SQ_SIZE))
#         pg.display.flip()
#         clock.tick(60)


def animate_piece(move, screen, board, clock, frame_count = 10):
    dR = move.end_sq_row - move.start_sq_row
    dC = move.end_sq_col - move.start_sq_col
    frame_count = frame_count
    for frame in range(frame_count + 1):
        t = frame / frame_count
        p = (1 - math.cos(t * math.pi)) / 2
        r, c = move.start_sq_row + dR * p, move.start_sq_col + dC * p
        draw_board(screen)
        draw_pieces_except(screen, board, move.end_sq_row, move.end_sq_col)
        piece = board[move.end_sq_row][move.end_sq_col]
        screen.blit(IMAGES[piece], (c * SQ_SIZE, r * SQ_SIZE))
        pg.display.flip()
        clock.tick(60)

def draw_pieces_except(screen, board, target_row, target_col):
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            piece = board[i][j]
            if (i, j) == (target_row, target_col): continue
            if piece != "--":
                screen.blit(IMAGES[piece], (j * SQ_SIZE, i * SQ_SIZE))



def draw_game_over(screen, king_positions, winner: Literal["w", "b", "stalemate"]):
    wk, bk = king_positions
    wk_r, wk_c = wk
    bk_r, bk_c = bk
    text = "White Won!" if winner == "w" else "Black Won!" if winner == "b" else "stalemate!"
    font = pg.font.SysFont("Arial", 20, True)
    text_obj = font.render(text, True, "black")
    screen.blit(text_obj, (WIDTH/2 - text_obj.get_width()/2, HEIGHT/2 - text_obj.get_height()/2))
    get_square = lambda r, c: pg.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
    if winner == "w":
        winner_c, winner_r = wk_c, wk_r
        losser_c, losser_r = bk_c, bk_r
    elif winner == "b":
        winner_c, winner_r = bk_c, bk_r
        losser_c, losser_r = wk_c, wk_r

    if not winner == "stalemate":
        winner_square = get_square(winner_r, winner_c)
        losser_square = get_square(losser_r, losser_c)
        pg.draw.rect(screen, "gold", winner_square, 5)
        pg.draw.rect(screen, "red", losser_square, 5)
    else:
        pg.draw.rect(screen, "chocolate1", get_square(wk_r, wk_c), 5)
        pg.draw.rect(screen, "chocolate1", get_square(bk_r, bk_c), 5)

def draw_game_state(screen, gs, valid_moves, sq_selected):
    """
    responsible for all graphics within a current GameState.
    """
    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, sq_selected)
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