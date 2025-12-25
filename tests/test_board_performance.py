import unittest
from board import Board
import time
from constants import *

def get_piece_name(piece):
    piece_type = piece & 7

    if piece_type == PAWN:
        return "pawn"
    elif piece_type == KNIGHT:
        return "knight"
    elif piece_type == BISHOP:
        return "bishop"
    elif piece_type == ROOK:
        return "rook"
    elif piece_type == QUEEN:
        return "queen"
    elif piece_type == KING:
        return "king"

def get_piece_moves(board, target_piece):
    num_pieces = 0
    moves = []

    start = time.perf_counter()
    for _ in range(10000):
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
    end = time.perf_counter()
    print("="*60)
    print(f"{get_piece_name(target_piece)} Move Generation Test")
    print(f"{num_pieces} {get_piece_name(target_piece)} tested")
    print(f"{len(moves)} moves generated in {end-start} seconds")

    return

class TestBoardPerformance(unittest.TestCase):
    def test_pawns(self):
        board = Board()
        get_piece_moves(board,PAWN)        

    def test_bishops(self):
        board = Board()
        board.from_fen('8/2b1k3/6b1/8/2B5/8/3K1B2/8 w - - 0 1')
        get_piece_moves(board,BISHOP)

    def test_knights(self):
        board = Board()
        board.from_fen('8/2bnk3/4n1b1/8/2B2N2/2N5/3K1B2/8 w - - 0 1')
        get_piece_moves(board,KNIGHT)

    def test_rooks(self):
        board = Board()
        board.from_fen('8/1rbnk3/4nrb1/8/2B2N2/2N1R3/3K1B2/R7 w - - 0 1')
        get_piece_moves(board,ROOK)

    def test_queen(self):
        board = Board()
        board.from_fen('4q3/1rbnk3/4nrb1/8/2B2N2/2N1R3/3K1B2/R1Q5 w - - 0 1')
        get_piece_moves(board,QUEEN)
    
    def test_king(self):
        board = Board()
        board.from_fen('4q3/1rbnk3/4nrb1/8/2B2N2/2N1R3/3K1B2/R1Q5 w - - 0 1')
        get_piece_moves(board,KING)

    def test_move_legal(self):
        board = Board()
        board.from_fen('4q3/1rbnk3/4nrb1/8/2B2N2/2N1R3/3K1B2/R1Q5 w - - 0 1')
        pseudo_legal = board.generate_pseudo_legal_moves()
        start = time.perf_counter()
        for _ in range(10000):
            moves = [move for move in pseudo_legal if self.is_legal_move(move)]
        end = time.perf_counter()
        print("="*60)
        print("Move Legality Check")
        print(f"Completed in {end-start} seconds")
