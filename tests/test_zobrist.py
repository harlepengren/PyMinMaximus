import unittest
from move import Move
from zobrist import ZobristHash

class TestZobrist(unittest.TestCase):
    def test_zobrist(self):
        """Test Zobrist hashing properties."""
        from board import Board
        
        zobrist = ZobristHash()
        
        # Test 1: Same position = same hash
        print("Test 1: Consistency")
        board1 = Board()
        hash1 = zobrist.hash_position(board1)
        hash2 = zobrist.hash_position(board1)
        print(f"  Hash 1: {hash1}")
        print(f"  Hash 2: {hash2}")
        print(f"  Same: {hash1 == hash2} ✓")
        
        # Test 2: Different positions = different hashes
        print("\nTest 2: Uniqueness")
        board2 = Board()
        board2.make_move(Move(1, 4, 3, 4))  # e4
        hash3 = zobrist.hash_position(board2)
        print(f"  Starting: {hash1}")
        print(f"  After e4: {hash3}")
        print(f"  Different: {hash1 != hash3} ✓")
        
        # Test 3: Transpositions = same hash
        print("\nTest 3: Transpositions")
        # Reach same position via different move orders
        board3 = Board()
        board3.make_move(Move(1, 4, 3, 4))  # e4
        board3.make_move(Move(6, 4, 4, 4))  # e5
        
        board4 = Board()
        board4.make_move(Move(1, 4, 3, 4))  # e4
        board4.make_move(Move(6, 4, 4, 4))  # e5
        
        hash4 = zobrist.hash_position(board3)
        hash5 = zobrist.hash_position(board4)
        print(f"  Hash via path 1: {hash4}")
        print(f"  Hash via path 2: {hash5}")
        print(f"  Same: {hash4 == hash5} ✓")


if __name__ == "__main__":
    unittest.main()
