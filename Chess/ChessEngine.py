"""
This class is responsible for storing all the info about the current state of a chess game. it will also be
responsible for determining the valid moves at the current state. it will also keep a move log
"""
from __future__ import annotations
from collections.abc import Callable
from typing import Literal

import pygame as pg
from dataclasses import dataclass

@dataclass
class CastlingManager:
    color:Literal["w", "b"]
    castling_kingside_possible: bool = True
    castling_queen_possible: bool = True
    preventing_move_num_kingside: int = -1
    preventing_move_num_queenside: int = -1

    def manage_castling_rights(self, move:Move, move_num):
        if move.moved_piece == self.color+"K" and self.castling_kingside_possible:
            self.castling_queen_possible = False
            self.castling_kingside_possible = False
            self.preventing_move_num_kingside = move_num
            self.preventing_move_num_queenside = move_num
        elif move.moved_piece == self.color+"R" and self.castling_kingside_possible and move.start_sq_col == GameConfig.DIMENSION-1: #kingside
            self.castling_kingside_possible = False
            self.preventing_move_num_kingside = move_num
        elif move.moved_piece == self.color+"R" and self.castling_queen_possible and move.start_sq_col == 0: #queenside
            self.castling_queen_possible = False
            self.preventing_move_num_queenside = move_num
        elif move.captured_piece == self.color+"R" and self.castling_kingside_possible and move.end_sq_col == GameConfig.DIMENSION-1: #kingside
            self.castling_kingside_possible = False
            self.preventing_move_num_kingside = move_num
        elif move.captured_piece == self.color+"R" and self.castling_queen_possible and move.end_sq_col == 0: #queenside
            self.castling_queen_possible = False
            self.preventing_move_num_queenside = move_num

class GameConfig:
    DIMENSION = 8
    PAWN_PROMOTION_EVENT = pg.USEREVENT + 1
class GameState:
    def __init__(self):
        # the board is a 8x8 2d list. each element is a piece. empty fields are represented via "--" otherwise each
        # piece has two characters, first one determines the color and the second the type.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP","bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.white_to_play = True
        self.movelog = []
        self.white_king_pos = (7,4)
        self.black_king_pos = (0, 7)
        self.checkmate = False
        self.stalemate = False
        self.white_castling_manager = CastlingManager(color="w")
        self.black_castling_manager = CastlingManager(color="b")
        self.move_functions: dict[str, Callable] = {
            "P": self.get_pawn_moves, "R": self.get_rook_moves, "N": self.get_knight_moves,
            "B": self.get_bishop_moves, "Q": self.get_queen_moves, "K": self.get_king_moves}

    def make_move(self, move: Move, is_real_move = False):
        self.board[move.start_sq_row][move.start_sq_col] = "--"
        self.board[move.end_sq_row][move.end_sq_col] = move.moved_piece
        self.movelog.append(move)

        if move.moved_piece == "bK":
            self.black_king_pos = (move.end_sq_row, move.end_sq_col)
        elif move.moved_piece == "wK":
            self.white_king_pos = (move.end_sq_row, move.end_sq_col)

        if move.is_En_Passant:
            self.board[move.start_sq_row][move.end_sq_col] = "--"
            print(move)

        if move.castling:
            castling_manager = self.white_castling_manager if self.white_to_play else self.black_castling_manager
            print(f"its castling and castling kingside is:{castling_manager.castling_kingside_possible} and queenside:{castling_manager.castling_queen_possible}")
            er, ec = move.end_sq_row, move.end_sq_col
            if move.end_sq_col == 6 and castling_manager.castling_kingside_possible:
                assert self.board[er][7] == "wR" if self.white_to_play else "bR"
                self.board[er][5] = self.board[er][7] #kingside castling
                self.board[er][7] = "--"
            elif move.end_sq_col == 2 and castling_manager.castling_queen_possible:
                assert self.board[er][0] == "wR" if self.white_to_play else "bR"
                self.board[er][3] = self.board[er][0] #queenside castling
                self.board[er][0] = "--"

        self.white_castling_manager.manage_castling_rights(move, len(self.movelog))
        self.black_castling_manager.manage_castling_rights(move, len(self.movelog))
        if move.is_pawn_promotion and is_real_move:
            print("promoting!!!!")
            promotion_event = pg.event.Event(GameConfig.PAWN_PROMOTION_EVENT, {"move": move})
            pg.event.post(promotion_event)
        else:
            self.white_to_play = not self.white_to_play


    def undo_last_move(self):
        if len(self.movelog) != 0:
            last_move: Move = self.movelog.pop()
            self.board[last_move.end_sq_row][last_move.end_sq_col] = last_move.captured_piece
            self.board[last_move.start_sq_row][last_move.start_sq_col] = last_move.moved_piece
            self.white_to_play = not self.white_to_play

            if last_move.is_En_Passant:
                self.board[last_move.end_sq_row][last_move.end_sq_col] = "--"  # The landing square is actually empty
                self.board[last_move.start_sq_row][last_move.end_sq_col] = last_move.captured_piece  # Put pawn back side-by-side
            for manager in [self.white_castling_manager, self.black_castling_manager]:
                if manager.preventing_move_num_kingside == len(self.movelog) + 1:
                    manager.castling_kingside_possible = True
                    manager.preventing_move_num_kingside = -1
                if manager.preventing_move_num_queenside == len(self.movelog) + 1:
                    manager.castling_queen_possible = True
                    manager.preventing_move_num_queenside = -1
            if last_move.castling:

                startsq = (last_move.start_sq_row, last_move.start_sq_col)
                endsq = (last_move.end_sq_row, last_move.end_sq_col)
                match (startsq, endsq):
                    case ((r1, 4), (r2, 6)) if r1 == r2:
                        color = "b" if r1 == 0 else "w"
                        self.board[r1][4] = color+"K"
                        self.board[r1][7] = color+"R"
                        self.board[r1][5] = "--"

                    case ((r1, 4), (r2, 2)) if r1 == r2:
                        color = "b" if r1 == 0 else "w"
                        self.board[r1][4] = color+"K"
                        self.board[r1][0] = color+"R"
                        self.board[r1][3] = "--"


            if last_move.moved_piece == "bK":
                self.black_king_pos = (last_move.start_sq_row, last_move.start_sq_col)
            elif last_move.moved_piece == "wK":
                self.white_king_pos = (last_move.start_sq_row, last_move.start_sq_col)

    def get_valid_moves(self):
        moves = self.get_all_possible_moves()
        for i in range(len(moves)-1, -1, -1):
            move = moves[i]
            self.make_move(move)
            self.white_to_play = not self.white_to_play
            if self.in_check_efficient():
                moves.remove(move)
            self.undo_last_move()
            self.white_to_play = not self.white_to_play

        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.stalemate, self.checkmate = False, False

        return moves

    def in_check(self):
        king_pos = self.white_king_pos if self.white_to_play else self.black_king_pos
        return self.square_under_attack(king_pos[0], king_pos[1])

    def in_check_efficient(self):
        # 1. Determine who we are looking for
        if self.white_to_play:
            king_r, king_c = self.white_king_pos
            friendly_color = "w"
            enemy_color = "b"
            # From White King's view, Black pawns attack from "above" (-1)
            pawn_directions = [(-1, 1), (-1, -1)]
        else:
            king_r, king_c = self.black_king_pos
            friendly_color = "b"
            enemy_color = "w"
            # From Black King's view, White pawns attack from "below" (+1)
            pawn_directions = [(1, 1), (1, -1)]

        # 2. Check for Knight attacks (Fixed boundary and color)
        knight_directions = [(-1, 2), (1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, 1), (2, -1)]
        for dr, dc in knight_directions:
            r, c = king_r + dr, king_c + dc
            if 0 <= r < GameConfig.DIMENSION and 0 <= c < GameConfig.DIMENSION:
                piece = self.board[r][c]
                if piece[0] == enemy_color and piece[1] == "N":
                    return True

        # 3. Check for Sliding pieces, Pawns, and King (Fixed color checks)
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            for i in range(1, GameConfig.DIMENSION):  # Using range(1,8) instead of while is often cleaner
                r, c = king_r + dr * i, king_c + dc * i
                if 0 <= r < 8 and 0 <= c < 8:
                    piece = self.board[r][c]
                    if piece == "--":
                        continue
                    elif piece[0] == friendly_color:
                        break  # Blocked by our own piece
                    else:  # Enemy piece
                        type = piece[1]
                        # Orthogonal threats
                        if (dr == 0 or dc == 0) and type in ("R", "Q"):
                            return True
                        # Diagonal threats
                        elif (dr != 0 and dc != 0) and type in ("B", "Q"):
                            return True
                        # Pawn threats (only 1 square away)
                        elif i == 1 and type == "P" and (dr, dc) in pawn_directions:
                            return True
                        # Enemy King (prevents kings from standing next to each other)
                        elif i == 1 and type == "K":
                            return True

                        break  # Hit an enemy piece that doesn't check us, it blocks the line
                else:
                    break  # Off board

        return False





    def square_under_attack(self, r, c):
        self.white_to_play = not self.white_to_play
        opponent_moves = self.get_all_possible_moves()
        self.white_to_play = not self.white_to_play
        for move in opponent_moves:
            if r == move.end_sq_row and c == move.end_sq_col:
                return True
        return False

    def get_all_possible_moves(self):
        possible_moves = []
        turn = "w" if self.white_to_play else "b"
        for r in range(GameConfig.DIMENSION):
            for c in range(GameConfig.DIMENSION):
                if self.board[r][c][0] != turn:
                    continue
                else:
                    piece = self.board[r][c][1]
                    possible_moves.extend(self.move_functions[piece](r, c))

        return possible_moves

    def get_pawn_moves(self, r, c):
        """
        get all the possible moves for a pawn located at row r and column c as a list of `Moves`.
        """
        moves = []
        forward = -1 if self.white_to_play else +1
        starting_row = 6 if self.white_to_play else 1
        opposing_color = "b" if self.white_to_play else "w"
        opponent_pawn = f"{opposing_color}P"
        dest_row = r + forward
        if 0 <= dest_row < GameConfig.DIMENSION:
            if self.board[dest_row][c] == "--":                                               #move one square
                moves.append(Move((r, c), (dest_row, c), self.board))
                if r == starting_row and self.board[r + 2 * forward][c] == "--":                 #move two squares
                    moves.append(Move((r, c), (r + 2 * forward, c), self.board))

            if c-1>=0 and self.board[dest_row][c - 1][0] == opposing_color:                     #capture to the left
                moves.append(Move((r,c), (dest_row, c - 1), self.board))

            if c+1 <= GameConfig.DIMENSION-1 and self.board[dest_row][c + 1][0] == opposing_color:         #capture to the right
                moves.append(Move((r, c), (dest_row, c + 1), self.board))

            if c-1>=0 and self.board[r][c-1] == opponent_pawn:
                last_move = self.movelog[-1]
                start_sq = last_move.start_sq_row, last_move.start_sq_col
                end_sq = last_move.end_sq_row, last_move.end_sq_col
                if start_sq == (r + 2*forward, c-1) and end_sq == (r, c-1) and last_move.moved_piece == opponent_pawn:
                    print("en passant with ")
                    moves.append(Move((r, c), (dest_row, c-1), self.board, en_passant=True))

            if c+1 <= GameConfig.DIMENSION-1  and self.board[r][c+1] == opponent_pawn:
                last_move = self.movelog[-1]
                start_sq = last_move.start_sq_row, last_move.start_sq_col
                end_sq = last_move.end_sq_row, last_move.end_sq_col
                if start_sq == (r + 2 * forward, c + 1) and  end_sq == (r, c + 1) and last_move.moved_piece == opponent_pawn:
                    moves.append(Move((r, c), (dest_row, c + 1), self.board, en_passant=True))

        return moves

    def get_rook_moves(self, r, c):
        """
        get all the possible moves for a rook located at row r and column c as a list of `Moves`.
        """
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        return self.get_sliding_moves(r, c, directions)


    def get_knight_moves(self, r, c):
        """
        get all the possible moves for a knight located at row r and column c as a list of `Moves`.
        """
        directions = [
            (-1, 2),
            (1, 2),
            (-2, 1),
            (-2, -1),
            (-1, -2),
            (1, -2),
            (2, 1),
            (2, -1)]
             
        return self.get_stepping_moves(r, c, directions)
        
    
    def get_bishop_moves(self, r, c):
        """
        get all the possible moves for a bishop located at row r and column c as a list of `Moves`.
        """
        directions = [(1,1), (1, -1), (-1,1), (-1, -1)]
        return self.get_sliding_moves(r,c, directions)

    def get_queen_moves(self, r, c):
        """
        get all the possible moves for a queen located at row r and column c as a list of `Moves`.
        """
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1,1), (1, -1), (-1,1), (-1, -1)]
        return self.get_sliding_moves(r, c, directions)
    
    def get_king_moves(self, r, c):
        """
        get all the possible moves for a king located at row r and column c as a list of `Moves`.
        """
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1,1), (1, -1), (-1,1), (-1, -1)]
        king_moves = self.get_stepping_moves(r, c, directions)
        #castling:
        castling_manager = self.white_castling_manager if self.white_to_play else self.black_castling_manager

        """
        1. king and rook not moved
        2. no pieces in between
        3.1. currently in check
        3.2. in the way in check
        3.3. into check at end of castling
        """
        king = "wK" if self.white_to_play else "bK"
        rook = "wR" if self.white_to_play else "bR"
        def update_kings_pos(row, col):
            if self.white_to_play:
                self.white_king_pos = (row, col)
            else:
                self.ball_king_pos = (row, col)
        print(f"{castling_manager.castling_kingside_possible}, {castling_manager.castling_queen_possible}")
        if (castling_manager.castling_kingside_possible
                and self.board[r][5] == "--"
                and self.board[r][6] == "--"
                and self.board[r][7] == rook
                and not self.in_check_efficient()):
            print("get king moves: castling kingside")

            is_safe = True
            for col in [5, 6]:
                self.board[r][c] = "--"
                self.board[r][col] = king
                update_kings_pos(r, col)
                if self.in_check_efficient():
                    is_safe = False
                self.board[r][c] = king
                self.board[r][col] = "--"
                update_kings_pos(r, c)
                if not is_safe: break
            if is_safe:
                king_moves.append(Move((r, c), (r, 6), self.board, castling=True))


        if (castling_manager.castling_queen_possible
                and self.board[r][3] == "--"
                and self.board[r][2] == "--"
                and self.board[r][1] == "--"
                and self.board[r][0] == rook
                and not self.in_check_efficient()):
            print("get queen moves: castling queenside")

            is_safe = True
            for col in [3, 2]:
                self.board[r][c] = "--"
                self.board[r][col] = king
                update_kings_pos(r, col)
                if self.in_check_efficient():
                    is_safe = False
                self.board[r][c] = king
                self.board[r][col] = "--"
                update_kings_pos(r, c)
                if not is_safe: break
            if is_safe:
                king_moves.append(Move((r, c), (r, 2), self.board, castling=True))

        return king_moves

    def get_stepping_moves(self, r, c, directions):
            """
            Generates all possible moves for a stepping piece (King, Knight).

            The piece steps in each directions once, checks it hits an enemy piece or lands on
            an empty square all the while making sure not step out of the edges.

            Args:
                r (int): Starting row index.
                c (int): Starting column index.
                directions (list[tuple]): List of (dr, dc) vectors (e.g., [(2, -1), ...]).

            Returns:
                list[Move]: A list of valid Move objects for the piece.
            """
            moves = []
            opposing_color = "b" if self.white_to_play else "w"
            for dr, dc in directions:
                row, col = r + dr, c + dc
                if (0<= row <GameConfig.DIMENSION and 0<= col <GameConfig.DIMENSION):
                    piece = self.board[row][col]
                    if piece == "--" or piece[0] == opposing_color: 
                        moves.append(Move((r, c), (row, col), self.board))
            return moves

    def get_sliding_moves(self, r, c, directions):
        """
            Generates all possible moves for a sliding piece (Rook, Bishop, or Queen).

            The piece continues to move in each direction until it hits the edge of
            the board, a friendly piece (blocked), or an enemy piece (captured).

            Args:
                r (int): Starting row index.
                c (int): Starting column index.
                directions (list[tuple]): List of (dr, dc) unit vectors (e.g., [(1, 0), ...]).

            Returns:
                list[Move]: A list of valid Move objects for the piece.
            """
        moves = []
        opposing_color = "b" if self.white_to_play else "w"

        for dr, dc in directions:
            row, col = r + dr, c + dc

            while 0 <= row < GameConfig.DIMENSION and 0 <= col < GameConfig.DIMENSION:
                square = self.board[row][col]

                if square == "--":
                    moves.append(Move((r, c), (row, col), self.board))
                elif square[0] == opposing_color:
                    moves.append(Move((r, c), (row, col), self.board))
                    break
                else:
                    break

                row += dr
                col += dc

        return moves

class Move:
    ranks_to_rows ={
        "1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0
    }
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {
        "a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7
    }
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    @classmethod
    def get_rank_file(cls, row, col):
        return cls.cols_to_files[col] + cls.rows_to_ranks[row]

    def __init__(self, start_sq, end_sq, board, en_passant = False, castling = False):
        self.start_sq_row = start_sq[0]
        self.start_sq_col = start_sq[1]
        self.end_sq_row = end_sq[0]
        self.end_sq_col = end_sq[1]
        self.moved_piece = board[self.start_sq_row][self.start_sq_col]
        self.captured_piece =board[self.end_sq_row][self.end_sq_col] if not en_passant else board[self.start_sq_row][self.end_sq_col]
        assert not en_passant or board[self.start_sq_row][self.end_sq_col][1] == "P", f"{board[self.end_sq_row-1][self.end_sq_col]}"
        self.is_En_Passant = en_passant
        self.castling = castling
        self.is_pawn_promotion = False
        self.promotion_piece = None
        if (self.moved_piece == "wP" and self.end_sq_row == 0) or (self.moved_piece == "bP" and self.end_sq_row == 7):
            self.is_pawn_promotion = True
        self.move_id = 1000 * self.start_sq_row + 100 * self.start_sq_col + 10 * self.end_sq_row + self.end_sq_col

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        if self.move_id == other.move_id:
            return True
        else:
            return False

    def __str__(self):
        return f"Move({self.start_sq_row}, {self.start_sq_col} -> {self.end_sq_row}, {self.end_sq_col}, {self.moved_piece} captures {self.captured_piece})"

    def get_chess_notation(self):
        return Move.get_rank_file(self.start_sq_row, self.start_sq_col) + Move.get_rank_file(self.end_sq_row, self.end_sq_col)


