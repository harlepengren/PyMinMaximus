import unittest
from board import Board
from search import SearchEngine
import time

class PerformanceTest(unittest.TestCase):
    def test_alphabeta_speed(self):
        """Tests the nodes per second of minmaxalphabeta."""
        fen = "rnbqkbnr/pp2ppp1/2p4p/6B1/3Pp3/2N5/PPP2PPP/R2QKBNR w KQkq - 0 5"

        board = Board()
        board.from_fen(fen)
        engine = SearchEngine(board)

        print("="*60)
        print("Testing MiniMaxAlpha Speed (depth=6)")
        start = time.perf_counter()
        bestmove, eval = engine.find_best_move_alphabeta(6)
        end = time.perf_counter()
        print(f"Best Move Identified: {bestmove} with score of {eval}")
        print(f"Nodes Searched: {engine.nodes_searched}")
        print(f"Total time: {end-start}")
        print(f"Nodes/Second (nps): {engine.nodes_searched/(end-start)}")

    def test_generate_moves(self):
        """Tests how many times we call board.generate_legal_moves()."""

        print("="*60)
        print("Testing how many times board.generate_legal_moves is called")
        fen = "rnbqkbnr/pp2ppp1/2p4p/6B1/3Pp3/2N5/PPP2PPP/R2QKBNR w KQkq - 0 5"
        board = Board()
        board.from_fen(fen)
        engine = SearchEngine(board)
        depth = 5

        bestmove, eval = engine.find_best_move_alphabeta(depth)
        print(f"Generate Legal Moves Calls: {board.num_moves_generated}")
        print(f"Average calls per depth {board.num_moves_generated/depth}")
        print(f"Average calls per node: {board.num_moves_generated/engine.nodes_searched}")

    def test_move_generation_speed(self):
        """Tests the speed of move generation."""
        fen = "rnbqkbnr/pp2ppp1/2p4p/6B1/3Pp3/2N5/PPP2PPP/R2QKBNR w KQkq - 0 5"
        board = Board()
        board.from_fen(fen)

        print("="*60)
        print("Testing Move Generation Speed")
        iterations = 100000
        start = time.perf_counter()
        for _ in range(iterations):
            moves = board.generate_legal_moves()
        end = time.perf_counter()
        print(f"Generated moves {iterations} times in {end-start} seconds")
        print(f"Average time per generation: {(end-start)/iterations} seconds")

    def test_board_evaluation_speed(self):
        """Tests the speed of board evaluation."""
        fen = "rnbqkbnr/pp2ppp1/2p4p/6B1/3Pp3/2N5/PPP2PPP/R2QKBNR w KQkq - 0 5"
        board = Board()
        board.from_fen(fen)

        print("="*60)
        print("Testing Board Evaluation Speed")
        iterations = 100000
        start = time.perf_counter()
        for _ in range(iterations):
            score = board.evaluate_board()
        end = time.perf_counter()
        print(f"Evaluated board {iterations} times in {end-start} seconds")
        print(f"Average time per evaluation: {(end-start)/iterations} seconds")
