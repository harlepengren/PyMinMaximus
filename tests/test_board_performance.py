import unittest
from board import Board
import time
from constants import *

class TestBoardPerformance(unittest.TestCase):
    def test_pawns(self):
        pawn_counter = 0
        moves = []

        board = Board()
        start = time.perf_counter()
        for _ in range(10000):
            for row in range(8):
                for col in range(8):
                    if self.board[row][col] == PAWN:
                        board.generate_pawn_moves(row,col,moves)
                        pawn_counter += 1
        end = time.perf_counter
        print("="*60)
        print("Pawn Move Generation Test")
        print(f"{len(moves)} moves generated in {end-start} seconds")