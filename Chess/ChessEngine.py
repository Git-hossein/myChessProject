"""
This class is responsible for storing all the info about the current state of a chess game. it will also be
responsible for determining the valid moves at the current state. it will also keep a move log
"""
from __future__ import annotations
import numpy as np
from collections.abc import Callable
from Chess.ChessMain import DIMENSION


class GameState:
    def __init__(self):
        # the board is an 8x8 2d list. each element is a piece. empty fields are represented via "--" otherwise each
        # piece has two characters, first one determines the color and the second the type.
        self.board = np.array([
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP","bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]])

        self.white_to_play = True
        self.movelog = []
        self.move_functions: dict[str, Callable] = {
            "P": self.get_pawn_moves, "R": self.get_rook_moves, "N": self.get_knight_moves,
            "B": self.get_bishop_moves, "Q": self.get_queen_moves, "K": self.get_king_moves}

    def make_move(self, move: Move):
        self.board[move.start_sq_row, move.start_sq_col] = "--"
        self.board[move.end_sq_row, move.end_sq_col] = move.moved_piece
        self.movelog.append(move)
        self.white_to_play = not self.white_to_play

    def undo_last_move(self):
        if len(self.movelog) != 0:
            last_move: Move = self.movelog.pop()
            self.board[last_move.end_sq_row, last_move.end_sq_col] = last_move.captured_piece
            self.board[last_move.start_sq_row, last_move.start_sq_col] = last_move.moved_piece
            self.white_to_play = not self.white_to_play

    def get_valid_moves(self):
        return self.get_all_possible_moves()

    def get_all_possible_moves(self):
        possible_moves = []
        turn = "w" if self.white_to_play else "b"
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                if self.board[r, c][0] != turn:
                    continue
                else:
                    piece = self.board[r,c][1]
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

        if self.board[r + forward, c] == "--":                                               #move one square
            moves.append(Move((r, c), (r + forward, c), self.board))
            if r == starting_row and self.board[r + 2 * forward, c] == "--":                 #move two squares
                moves.append(Move((r, c), (r + 2 * forward, c), self.board))

        if c-1>=0 and self.board[r + forward, c-1][0] == opposing_color:                     #capture to the left
            moves.append(Move((r,c), (r + forward, c-1), self.board))

        if c+1 <= DIMENSION-1 and self.board[r + forward, c+1][0] == opposing_color:         #capture to the right
            moves.append(Move((r, c), (r + forward, c + 1), self.board))

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
        return self.get_stepping_moves(r, c, directions)

    def get_stepping_moves(self, r, c, directions):
            """
            Generates all possible moves for a steping piece (King, Knight).

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
                if (0<= row <DIMENSION and 0<= col <DIMENSION):
                    piece = self.board[row, col]
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

            while 0 <= row < DIMENSION and 0 <= col < DIMENSION:
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

    def __init__(self, start_sq, end_sq, board):
        self.start_sq_row = start_sq[0]
        self.start_sq_col = start_sq[1]
        self.end_sq_row = end_sq[0]
        self.end_sq_col = end_sq[1]
        self.moved_piece = board[self.start_sq_row, self.start_sq_col]
        self.captured_piece =board[self.end_sq_row, self.end_sq_col]
        self.move_id = 1000 * self.start_sq_row + 100 * self.start_sq_col + 10 * self.end_sq_row + self.end_sq_col

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        if self.move_id == other.move_id:
            return True
        else:
            return False

    def get_chess_notation(self):
        return Move.get_rank_file(self.start_sq_row, self.start_sq_col) + Move.get_rank_file(self.end_sq_row, self.end_sq_col)


