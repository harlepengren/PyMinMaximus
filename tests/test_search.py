import unittest
from board import Board
from search import SearchEngine
import time

class TestSearch(unittest.TestCase):
    def test_tactics(self):
        """Test the engine on tactical puzzles."""
        print("TESTING SEARCH")
        
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
                    if str(best_move) == puzzle['solution']:
                        print("✓ CORRECT!")
                    else:
                        print(f"✗ Expected: {puzzle['solution']}")
            else:
                print("No legal moves (checkmate or stalemate)")

    def test_benchmark(self):
        """Compare search algorithms."""
        
        board = Board()
        
        # Test position: complex middlegame
        board.from_fen("r1bq1rk1/ppp2ppp/2np1n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 0 8")
        
        depths = [3, 4, 5]
        
        for depth in depths:
            print(f"\n{'='*60}")
            print(f"Depth {depth}")
            print('='*60)
            
            # Basic minimax (without alpha-beta)
            engine1 = SearchEngine(board)
            engine1.tt.table.clear()  # Disable TT
            start = time.time()
            move1, score1 = engine1.find_best_move(depth)
            time1 = time.time() - start
            nodes1 = engine1.nodes_searched
            
            print(f"Basic Minimax: {nodes1:,} nodes in {time1:.2f}s "
                f"({nodes1/time1:,.0f} nps)")
            
            # With alpha-beta
            engine2 = SearchEngine(board)
            engine2.tt.table.clear()  # Disable TT
            start = time.time()
            move2, score2 = engine2.find_best_move_alphabeta(depth)
            time2 = time.time() - start
            nodes2 = engine2.nodes_searched
            
            print(f"Alpha-Beta:    {nodes2:,} nodes in {time2:.2f}s "
                f"({nodes2/time2:,.0f} nps)")
            print(f"Improvement:   {nodes1/nodes2:.1f}x fewer nodes, "
                f"{time1/time2:.1f}x faster")
            
            # With TT
            engine3 = SearchEngine(board)
            start = time.time()
            move3, score3 = engine3.find_best_move_alphabeta(depth)
            time3 = time.time() - start
            nodes3 = engine3.nodes_searched
            
            print(f"Alpha-Beta+TT: {nodes3:,} nodes in {time3:.2f}s "
                f"({nodes3/time3:,.0f} nps)")
            print(f"Improvement:   {nodes1/nodes3:.1f}x fewer nodes, "
                f"{time1/time3:.1f}x faster vs basic")


if __name__ == '__main__':
    unittest.main()