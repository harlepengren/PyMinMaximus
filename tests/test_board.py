import unittest
from board import *
import chess
import time
import random

def perft(board, depth):
        """Count leaf nodes at a given depth."""
        if depth == 0:
            return 1
        
        moves = board.generate_legal_moves()
        if depth == 1:
            return len(moves)
        
        count = 0
        for move in moves:
            undo_info = board.make_move(move)
            count += perft(board, depth - 1)
            board.unmake_move(move, undo_info)
        
        return count

class TestBoard(unittest.TestCase):         
    def test_starting_position(self):
        print("Test 1: Starting Position")
        board = Board()
        print(board)
    
        moves = board.generate_legal_moves()
        assert(len(moves) > 0)
        print(f"Legal moves available: {len(moves)}")
        print(f"First 5 moves: {moves[:5]}\n")

    def test_make_moves(self):
         # Test 2: Make some moves
        print("Test 2: Playing 1.e4 e5 2.Nf3")
        board = Board()
        board.make_move(Move(1, 4, 3, 4))  # e4
        board.make_move(Move(6, 4, 4, 4))  # e5
        board.make_move(Move(0, 6, 2, 5))  # Nf3
        print(board)
    
    def test_fen(self):
        # Test 3: FEN notation
        print("Test 3: Loading position from FEN")
        board2 = Board()
        # Famous position: "The Immortal Game" after 10.e5
        fen = "r1bqkb1r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5"
        board2.from_fen(fen)
        print(board2)
        print(f"FEN: {board2.to_fen()}")
        print(f"Legal moves: {len(board2.generate_legal_moves())}\n")
    
    def test_check(self):
        # Test 4: Check detection
        print("Test 4: Check Detection")
        board3 = Board()
        # Scholar's mate position
        board3.from_fen("r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4")
        print(board3)
        print(f"Black in check: {board3.is_in_check(BLACK)}")
        assert(board3.is_in_check(BLACK))
        print(f"Legal moves for black: {len(board3.generate_legal_moves())}\n")

    def test_depth(self):
        print("Test 5: Perft Verification")
        print("Running perft tests from starting position...")
        board = Board()
        self.assertEqual(perft(board,1),20)
        self.assertEqual(perft(board,2),400)
        self.assertEqual(perft(board,3),8902)
        self.assertEqual(perft(board,4),197281)
    
    def test_special_moves(self):
        # Test 6: Special moves
        print("\nTest 6: Special Moves")
        
        # En passant
        print("En Passant:")
        board5 = Board()
        board5.from_fen("rnbqkbnr/ppp1p1pp/8/3pPp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 3")
        print(board5)
        moves = board5.generate_legal_moves()
        en_passant_moves = [m for m in moves if m.is_en_passant]
        print(f"En passant captures available: {en_passant_moves}\n")
        
        # Castling
        print("Castling:")
        board6 = Board()
        board6.from_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        print(board6)
        moves = board6.generate_legal_moves()
        castling_moves = [m for m in moves if m.is_castling]
        print(f"Castling moves available: {len(castling_moves)}")
        for move in castling_moves:
            side = "Kingside" if move.to_col == 6 else "Queenside"
            color = "White" if move.from_row == 0 else "Black"
            print(f"  - {color} {side}: {move}")
        
        # Promotion
        print("\nPromotion:")
        board7 = Board()
        board7.from_fen("8/P7/8/8/8/8/8/4K2k w - - 0 1")
        print(board7)
        moves = board7.generate_legal_moves()
        promotion_moves = [m for m in moves if m.promotion]
        print(f"Promotion moves available: {len(promotion_moves)}")

    def test_time(self):
        # Test 7: Test speed vs Python-Chess
        start_time = time.perf_counter()
        for _ in range(1000):
            board = Board()
            moves = board.generate_legal_moves()
            next_move = random.choice(moves)
            undo_info = board.make_move(next_move)
            board.unmake_move(next_move,undo_info)
        first_time = time.perf_counter() - start_time

        start_time = time.perf_counter()
        for _ in range(1000):
            board = chess.Board()
            moves = list(board.generate_legal_moves())
            next_move = random.choice(moves)
            board.push(next_move)
            board.pop()
        second_time = time.perf_counter() - start_time
        print(f"PyMinMaximus: {first_time} PyChess: {second_time}")
        assert(first_time < second_time)
        

if __name__ == '__main__':
    unittest.main()