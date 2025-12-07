import unittest
import chess

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
    def test_depth(self):
        board = chess.Board()
        self.assertEqual(perft(board,1),20)
        self.assertEqual(perft(board,2),400)
        self.assertEqual(perft(board,3),8902)
        self.assertEqual(perft(board,4),197281)

if __name__ == '__main__':
    unittest.main()