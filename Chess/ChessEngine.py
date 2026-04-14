"""
This class is responsible for storing all the info about the current state of a chess game. it will also be
responsible for determining the valid moves at the current state. it will also keep a move log
"""
import numpy as np

class GameState():
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
        self.movelog = np.array([])

