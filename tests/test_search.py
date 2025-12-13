import unittest
from board import Board
from search import SearchEngine

class TestSearch(unittest.TestCase):
    def test_tactics(self):
        """Test the engine on tactical puzzles."""
        
        puzzles = [
            {
                'name': 'Mate in 1',
                'fen': 'r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4',
                'solution': None  # Black is already mated
            },
            {
                'name': 'Back Rank Mate',
                'fen': '6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1',
                'solution': 'd1d8'  # Rd8#
            },
            {
                'name': 'Queen Fork',
                'fen': 'r1bqkb1r/pppp1ppp/2n5/4p3/2B1n3/5N2/PPPPQPPP/RNB1K2R w KQkq - 0 1',
                'solution': 'e2e5'  # Qxe5+ wins the knight
            },
            {
                'name': 'Smothered Mate',
                'fen': '6rk/6pp/7N/8/8/8/8/R3K3 w - - 0 1',
                'solution': 'h6f7'  # Nf7#
            }
        ]
        
        for puzzle in puzzles:
            print(f"\n{'='*60}")
            print(f"Puzzle: {puzzle['name']}")
            print(f"FEN: {puzzle['fen']}")
            print('='*60)
            
            board = Board()
            board.from_fen(puzzle['fen'])
            
            print(board)
            
            engine = SearchEngine(board)
            best_move, score = engine.iterative_deepening(6, time_limit=5.0)
            
            if best_move:
                print(f"\nEngine's choice: {best_move}")
                if puzzle['solution']:
                    self.assertEqual(str(best_move),puzzle['solution'])
            else:
                print("No legal moves (checkmate or stalemate)")

if __name__ == '__main__':
    unittest.main()