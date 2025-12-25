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
                    piece = board.board[row][col]
                
                    if piece == EMPTY or (piece & 24) != board.to_move:
                        continue
                
                    piece_type = piece & 7
                    if piece_type == PAWN:
                        board.generate_pawn_moves(row,col,moves)
                        pawn_counter += 1
        end = time.perf_counter()
        print("="*60)
        print("Pawn Move Generation Test")
        print(f"{pawn_counter} pawns tested")
        print(f"{len(moves)} moves generated in {end-start} seconds")

    def test_bishops(self):
        bishop_counter = 0
        moves = []

        board = Board()
        board.to_fen('8/2b1k3/6b1/8/2B5/8/3K1B2/8 w - - 0 1')
        start = time.perf_counter()
        for _ in range(10000):
            for row in range(8):
                for col in range(8):
                    piece = board.board[row][col]
                
                    if piece == EMPTY or (piece & 24) != board.to_move:
                        continue
                
                    piece_type = piece & 7
                    if piece_type == BISHOP:
                        board.generate_bishop_moves(row,col,moves)
                        bishop_counter += 1
        end = time.perf_counter()
        print("="*60)
        print("Bishop Move Generation Test")
        print(f"{bishop_counter} bishops tested")
        print(f"{len(moves)} moves generated in {end-start} seconds")