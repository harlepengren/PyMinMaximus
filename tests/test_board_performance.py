import unittest
from board import Board
import time
from constants import *

def get_piece_moves(board, target_piece):
    num_pieces = 0
    moves = []

    for _ in range(1000):
        for row in range(8):
                for col in range(8):
                    piece = board.board[row][col]
                    
                    if piece == EMPTY or (piece & 24) != board.to_move:
                        continue
                    
                    piece_type = piece & 7
                    if piece_type != target_piece:
                        continue
                    
                    if piece_type == PAWN:
                        board.generate_pawn_moves(row, col, moves)
                    elif piece_type == KNIGHT:
                        board.generate_knight_moves(row, col, moves)
                    elif piece_type == BISHOP:
                        board.generate_bishop_moves(row, col, moves)
                    elif piece_type == ROOK:
                        board.generate_rook_moves(row, col, moves)
                    elif piece_type == QUEEN:
                        board.generate_queen_moves(row, col, moves)
                    elif piece_type == KING:
                        board.generate_king_moves(row, col, moves)
                    num_pieces += 1

    return num_pieces, len(moves)

class TestBoardPerformance(unittest.TestCase):
    def test_pawns(self):
        board = Board()
        start = time.perf_counter()
        pawn_counter, num_moves = get_piece_moves(board,PAWN)
        end = time.perf_counter()
        print("="*60)
        print("Pawn Move Generation Test")
        print(f"{pawn_counter} pawns tested")
        print(f"{num_moves} moves generated in {end-start} seconds")

    def test_bishops(self):
        board = Board()
        board.from_fen('8/2b1k3/6b1/8/2B5/8/3K1B2/8 w - - 0 1')
        start = time.perf_counter()
        bishop_counter, num_moves = get_piece_moves(board,BISHOP)
        end = time.perf_counter()
        print("="*60)
        print("Bishop Move Generation Test")
        print(f"{bishop_counter} bishops tested")
        print(f"{num_moves} moves generated in {end-start} seconds")