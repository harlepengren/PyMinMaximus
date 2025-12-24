import unittest
from board import Board
from search import SearchEngine
import time

class PerformanceTest(unittest.TestCase):
    def test_alphabeta_speed(self):
        """Tests the nodes per second of minmaxalphabeta."""

        board = Board()
        engine = SearchEngine(board)
        total_time = 0

        print("="*60)
        print("Testing MiniMaxAlpha Speed (depth=6)")
        start = time.perf_counter()
        bestmove, eval = engine.find_best_move_alphabeta(6)
        end = time.perf_counter()
        print(f"Best Move Identified: {bestmove} with score of {eval}")
        print(f"Total time: {end-start}")
        print(f"Nodes/Second (nps): {engine.nodes_searched/(end-start)}")