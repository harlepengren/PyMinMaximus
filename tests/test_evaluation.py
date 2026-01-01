import unittest
from board import Board
from evaluation import Evaluator
from move import Move
from constants import *
import pst

class TestEvaluation(unittest.TestCase):
    def test_evaluation(self):
        """Test evaluation on various positions."""
        
        print("\n" + "="*60)
        print("Testing Evaluation Function on Various Positions")
        print("="*60)
        evaluator = Evaluator()

        print("Case 1: Starting Position")
        board = Board()
        eval_score = evaluator.evaluate(board)
        print(f"Evaluation: {eval_score:+d} centipawns")
        self.assertEqual(eval_score, 0)

        print("\nCase 2: White up a Queen")
        board = Board()
        board.from_fen('rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        eval_score = evaluator.evaluate(board)
        print(f"Evaluation: {eval_score:+d} centipawns")
        self.assertGreater(eval_score, 800)  # Expecting a high positive score for

        print("\nCase 3: Knight on Rim vs Center")
        board = Board()
        board.from_fen('8/8/8/4N3/8/8/n7/8 w - - 0 1')
        eval_score = evaluator.evaluate(board)
        print(f"Evaluation: {eval_score:+d} centipawns")
        self.assertGreater(eval_score, 0)  # Expecting a positive score for center knight

        print("\nCase 4: Passed Pawn vs Doubled Pawns")
        passed_board = Board()
        passed_board.from_fen('8/8/8/8/8/3P4/8/8 w - - 0 1')
        passed_score = evaluator.evaluate(passed_board)
        print(f"Passed Pawn Evaluation: {passed_score:+d} centipawns")
        doubled_board = Board()
        doubled_board.from_fen('8/8/8/8/3P4/3P4/8/8 w - - 0 1')
        doubled_score = evaluator.evaluate(doubled_board)
        print(f"Doubled Pawns Evaluation: {doubled_score:+d} centipawns")
        self.assertGreater(passed_score, doubled_score)

        print("\nCase 5: Castled vs Uncastled King")
        board = Board()
        board.from_fen('rnb2rk1/pppp1ppp/3b1n2/4p3/4P3/3B1N2/PPPP1PPP/RNB1K2R w KQ - 0 1')
        castled_score = evaluator.evaluate(board)
        print(f"Evaluation: {castled_score:+d} centipawns")
        self.assertGreater(0,castled_score)


    def test_positions(self):
        """Compare how evaluation changes after moves."""
        
        print("\n" + "="*60)
        print("Comparing Evaluation Before and After Moves")
        print("="*60)
        
        board = Board()
        evaluator = Evaluator()
        
        # Test opening principles
        print("\n1. Center Control: e4 vs. h4")
        
        board1 = Board()
        score_start = evaluator.evaluate(board1)
        
        # e4 - good center move
        board1.make_move(Move(1, 4, 3, 4))
        score_e4 = evaluator.evaluate(board1)
        
        board2 = Board()
        # h4 - poor edge move
        board2.make_move(Move(1, 7, 3, 7))
        score_h4 = evaluator.evaluate(board2)
        
        print(f"Starting position: {score_start:+d}")
        print(f"After 1.e4: {score_e4:+d} (improvement: {score_e4 - score_start:+d})  PST: {board1.pst:+d}")
        print(f"After 1.h4: {score_h4:+d} (improvement: {score_h4 - score_start:+d}) PST: {board2.pst:+d}")
        print(f"e4 is better by: {score_e4 - score_h4:+d} centipawns")
        self.assertGreater(score_e4, score_h4)
        
        # Test knight development
        print("\n2. Knight Development: Nf3 vs. Na3")
        
        board3 = Board()
        board3.make_move(Move(1, 4, 3, 4))  # e4
        score_before = evaluator.evaluate(board3)
        
        # Nf3 - good square
        board3_nf3 = Board()
        board3_nf3.from_fen(board3.to_fen())
        board3_nf3.make_move(Move(0, 6, 2, 5))  # Nf3
        score_nf3 = evaluator.evaluate(board3_nf3)
        
        # Na3 - rim square
        board3_na3 = Board()
        board3_na3.from_fen(board3.to_fen())
        board3_na3.make_move(Move(0, 1, 2, 0))  # Na3
        score_na3 = evaluator.evaluate(board3_na3)
        
        print(f"After 1.e4 (White to move): {score_before:+d}")
        print(f"After 1.e4 Nf3: {score_nf3:+d}")
        print(f"After 1.e4 Na3: {score_na3:+d}")
        print(f"Nf3 is better by: {score_nf3 - score_na3:+d} centipawns")
        self.assertGreater(score_nf3, score_na3)


if __name__ == "__main__":
    unittest.main()