import unittest
from board import Board
from search import SearchEngine

class PerformanceTest(unittest.TestCase):
    def test_minmaxalphabeta_speed(self):
        """Tests the nodes per second of minmaxalphabeta."""

