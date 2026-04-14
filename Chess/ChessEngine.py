"""
This class is responsible for storing all the info about the current state of a chess game. it will also be
responsible for determining the valid moves at the current state. it will also keep a move log
"""
from __future__ import annotations
import numpy as np


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
    def get_chess_notation(self):
        return Move.get_rank_file(self.start_sq_row, self.start_sq_col) + Move.get_rank_file(self.end_sq_row, self.end_sq_col)


