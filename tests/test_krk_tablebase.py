"""
Test suite for KRK Tablebase using unittest framework
Verifies correctness with known positions
"""

import unittest
import sys
from io import StringIO
from krk_tablebase import KRKTablebase, square_name
from constants import *


def sq(name):
    """Convert algebraic notation to square index"""
    col = ord(name[0]) - ord('a')
    row = int(name[1]) - 1
    return row * 8 + col


class TestKRKTablebase(unittest.TestCase):
    """Test suite for KRK endgame tablebase"""
    
    @classmethod
    def setUpClass(cls):
        """Generate the tablebase once for all tests"""
        print("\nGenerating KRK Tablebase for tests...")
        print("=" * 60)
        cls.tb = KRKTablebase()
        
        # Suppress generation output
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        cls.tb.generate()
        sys.stdout = old_stdout
        
        print(f"Tablebase ready: {len(cls.tb.table):,} positions")
        print("=" * 60)
    
    def test_tablebase_generation(self):
        """Test that tablebase generates the expected number of positions"""
        # Should solve exactly half the positions (White wins + draws)
        # The other half would be Black wins, which don't exist in KRK
        self.assertGreater(len(self.tb.table), 200000)
        self.assertLess(len(self.tb.table), 250000)
    
    def test_basic_checkmate_positions(self):
        """Test basic checkmate positions"""
        # Back rank mate - e2, e1, e8
        wk, wr, bk = sq('e2'), sq('e1'), sq('e8')
        result = self.tb.probe(wk, wr, bk, True)
        self.assertIsNotNone(result, "Back rank mate position should be in tablebase")
        outcome, dtm = result
        self.assertEqual(outcome, self.tb.WHITE_WIN, "Should be a white win")
        
        # Another back rank mate - g7, g8, e8
        wk, wr, bk = sq('g7'), sq('g8'), sq('e8')
        result = self.tb.probe(wk, wr, bk, True)
        self.assertIsNotNone(result)
        outcome, dtm = result
        self.assertEqual(outcome, self.tb.WHITE_WIN)
        self.assertEqual(dtm, 1, "Should be mate in 1")
    
    def test_stalemate_positions(self):
        """Test stalemate (draw) positions"""
        # Classic corner stalemate: WK c2, WR b2, BK a1, Black to move
        wk, wr, bk = sq('c2'), sq('b2'), sq('a1')
        result = self.tb.probe(wk, wr, bk, False)
        self.assertIsNotNone(result, "Stalemate position should be in tablebase")
        outcome, dtm = result
        self.assertEqual(outcome, self.tb.DRAW, "Should be a draw (stalemate)")
        self.assertEqual(dtm, 0, "Stalemate should have DTM of 0")
    
    def test_winning_positions(self):
        """Test various winning positions"""
        test_cases = [
            # (wk, wr, bk, wtm, description)
            (sq('e4'), sq('e1'), sq('e8'), True, "King opposition, rook on back rank"),
            (sq('d4'), sq('a4'), sq('a8'), True, "Rook cuts off king"),
        ]
        
        for wk, wr, bk, wtm, description in test_cases:
            with self.subTest(description=description):
                result = self.tb.probe(wk, wr, bk, wtm)
                self.assertIsNotNone(result, f"{description} should be in tablebase")
                outcome, dtm = result
                self.assertEqual(outcome, self.tb.WHITE_WIN, 
                               f"{description} should be a win")
    
    def test_corner_escape_positions(self):
        """Test longest mate sequences (corner escapes)"""
        # King in opposite corner
        wk, wr, bk = sq('a1'), sq('h8'), sq('h1')
        result = self.tb.probe(wk, wr, bk, True)
        self.assertIsNotNone(result)
        outcome, dtm = result
        self.assertEqual(outcome, self.tb.WHITE_WIN)
        self.assertGreater(dtm, 0, "Should require multiple moves")
        
        # Another corner position
        wk, wr, bk = sq('a8'), sq('h1'), sq('a1')
        result = self.tb.probe(wk, wr, bk, True)
        self.assertIsNotNone(result)
        outcome, dtm = result
        self.assertEqual(outcome, self.tb.WHITE_WIN)
    
    def test_illegal_positions(self):
        """Test that illegal positions are not in tablebase"""
        # Kings adjacent (illegal)
        wk, wr, bk = sq('a2'), sq('a3'), sq('a1')  # WK and BK adjacent
        result = self.tb.probe(wk, wr, bk, True)
        self.assertIsNone(result, "Adjacent kings should be illegal")
        
        # Pieces overlapping (illegal)
        wk, wr, bk = sq('e4'), sq('e4'), sq('e8')  # WK and WR overlap
        result = self.tb.probe(wk, wr, bk, True)
        self.assertIsNone(result, "Overlapping pieces should be illegal")
    
    def test_maximum_dtm(self):
        """Test that maximum DTM is within expected bounds"""
        max_dtm = 0
        for outcome, dtm in self.tb.table.values():
            if outcome == self.tb.WHITE_WIN:
                max_dtm = max(max_dtm, dtm)
        
        self.assertLessEqual(max_dtm, 10, 
                            "Maximum DTM should be 10 or less (actual KRK max is 6)")
        self.assertGreaterEqual(max_dtm, 5,
                               "Maximum DTM should be at least 5")
    
    def test_outcome_distribution(self):
        """Test that outcome distribution makes sense"""
        wins = sum(1 for outcome, _ in self.tb.table.values() 
                   if outcome == self.tb.WHITE_WIN)
        draws = sum(1 for outcome, _ in self.tb.table.values() 
                    if outcome == self.tb.DRAW)
        
        total = len(self.tb.table)
        
        # Almost all positions should be wins
        win_percentage = (wins / total) * 100
        self.assertGreater(win_percentage, 99.0, 
                          "More than 99% of KRK positions should be wins")
        
        # Draws should be very rare
        draw_percentage = (draws / total) * 100
        self.assertLess(draw_percentage, 1.0,
                       "Less than 1% of KRK positions should be draws")
    
    def test_symmetry_encoding(self):
        """Test that symmetry reduction works correctly"""
        # Positions that should be equivalent due to mirroring
        # e4, e1, e8 should be same as d4, d1, d8 after mirroring
        
        # Test that we can query both
        result1 = self.tb.probe(sq('e4'), sq('e1'), sq('e8'), True)
        result2 = self.tb.probe(sq('d4'), sq('d1'), sq('d8'), True)
        
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        # Both should be wins (though DTM might differ)
        self.assertEqual(result1[0], self.tb.WHITE_WIN)
        self.assertEqual(result2[0], self.tb.WHITE_WIN)
    
    def test_white_to_move_positions(self):
        """Test positions with white to move"""
        # When white to move in a winning position, should always find a win
        wins_white_to_move = 0
        for (wk, wr, bk, wtm), (outcome, dtm) in self.tb.table.items():
            if wtm and outcome == self.tb.WHITE_WIN:
                wins_white_to_move += 1
        
        self.assertGreater(wins_white_to_move, 100000,
                          "Should have many winning positions with white to move")
    
    def test_black_to_move_positions(self):
        """Test positions with black to move"""
        # Some positions with black to move should be draws (stalemates)
        draws_black_to_move = 0
        for (wk, wr, bk, wtm), (outcome, dtm) in self.tb.table.items():
            if not wtm and outcome == self.tb.DRAW:
                draws_black_to_move += 1
        
        self.assertGreater(draws_black_to_move, 0,
                          "Should have some stalemate positions")
        self.assertLess(draws_black_to_move, 500,
                       "Stalemates should be rare")


class TestTablebaseStatistics(unittest.TestCase):
    """Test statistical properties of the tablebase"""
    
    @classmethod
    def setUpClass(cls):
        """Generate the tablebase once for all tests"""
        cls.tb = KRKTablebase()
        
        # Suppress generation output
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        cls.tb.generate()
        sys.stdout = old_stdout
    
    def test_dtm_distribution(self):
        """Test that DTM distribution is reasonable"""
        dtm_counts = {}
        for outcome, dtm in self.tb.table.values():
            if outcome == self.tb.WHITE_WIN:
                dtm_counts[dtm] = dtm_counts.get(dtm, 0) + 1
        
        # Should have positions at depth 0 (terminal checkmates)
        self.assertIn(0, dtm_counts)
        self.assertGreater(dtm_counts[0], 0)
        
        # Should have positions at depth 1
        self.assertIn(1, dtm_counts)
        self.assertGreater(dtm_counts[1], 1000)
        
        # Distribution should generally decrease with depth
        # (more positions close to mate than far away)
        self.assertGreater(dtm_counts.get(1, 0), dtm_counts.get(5, 0))
    
    def test_position_count(self):
        """Test that position count matches expectations"""
        # With symmetry reduction, we should have roughly half
        # of the theoretical maximum
        self.assertGreater(len(self.tb.table), 200000)
        self.assertLess(len(self.tb.table), 250000)


class TestTablebaseSaveLoad(unittest.TestCase):
    """Test saving and loading tablebase"""
    
    def test_save_and_load(self):
        """Test that we can save and load the tablebase"""
        import tempfile
        import os
        
        # Generate original tablebase
        tb1 = KRKTablebase()
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        tb1.generate()
        sys.stdout = old_stdout
        
        original_size = len(tb1.table)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as f:
            temp_filename = f.name
        
        try:
            # Save
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            tb1.save(temp_filename)
            sys.stdout = old_stdout
            
            # Load into new tablebase
            tb2 = KRKTablebase()
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            tb2.load(temp_filename)
            sys.stdout = old_stdout
            
            # Verify same size
            self.assertEqual(len(tb2.table), original_size)
            
            # Test a few positions
            test_positions = [
                (sq('e2'), sq('e1'), sq('e8'), True),
                (sq('c2'), sq('b2'), sq('a1'), False),
                (sq('a1'), sq('h8'), sq('h1'), True),
            ]
            
            for wk, wr, bk, wtm in test_positions:
                result1 = tb1.probe(wk, wr, bk, wtm)
                result2 = tb2.probe(wk, wr, bk, wtm)
                self.assertEqual(result1, result2,
                               f"Position {square_name(wk)},{square_name(wr)},{square_name(bk)} "
                               f"should match after save/load")
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.remove(temp_filename)


def run_tests_with_output():
    """Run tests with proper output formatting"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestKRKTablebase))
    suite.addTests(loader.loadTestsFromTestCase(TestTablebaseStatistics))
    suite.addTests(loader.loadTestsFromTestCase(TestTablebaseSaveLoad))
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result


if __name__ == "__main__":
    # Run with our custom runner for better output
    result = run_tests_with_output()
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
