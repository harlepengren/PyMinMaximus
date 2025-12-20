import struct
from collections import defaultdict
from zobrist import ZobristHash
from board import Board
from constants import *
import pgn

class BookCreator:
    """
    Create Polyglot opening books from manual position entry.
    Build your own opening repertoire!
    """
    
    def __init__(self):
        self.positions = defaultdict(lambda: defaultdict(int))
        self.zobrist = ZobristHash()
    
    def add_position(self, fen, move_uci, weight=1):
        """
        Manually add a position and move to the book.
        
        Args:
            fen: FEN string of position
            move_uci: Move in UCI format (e.g., "e2e4")
            weight: Weight/frequency of this move (higher = more likely)
        """
        # Load position from FEN
        board = Board()
        board.from_fen(fen)
        
        # Get position hash
        position_hash = self.zobrist.hash_position(board)
        
        # Add move with weight
        self.positions[position_hash][move_uci] += weight
    
    def _encode_move(self, move_uci):
        """
        Encode UCI move to Polyglot format.
        
        Args:
            move_uci: Move string like "e2e4" or "e7e8q"
        
        Returns:
            16-bit encoded move
        """
        # Parse UCI move
        from_col = ord(move_uci[0]) - ord('a')
        from_row = int(move_uci[1]) - 1
        to_col = ord(move_uci[2]) - ord('a')
        to_row = int(move_uci[3]) - 1
        
        # Calculate square numbers
        from_square = from_row * 8 + from_col
        to_square = to_row * 8 + to_col
        
        # Check for promotion
        promo = 0
        if len(move_uci) == 5:
            promo_map = {'n': 1, 'b': 2, 'r': 3, 'q': 4}
            promo = promo_map.get(move_uci[4].lower(), 0)
        
        # Encode: to | (from << 6) | (promo << 12)
        return to_square | (from_square << 6) | (promo << 12)
    
    def save_book(self, output_path: str):
        """
        Save the book in Polyglot binary format.
        
        Args:
            output_path: Path for output .bin file
        """
        entries = []
        
        # Convert all positions and moves to binary entries
        for position_hash, moves in self.positions.items():
            for move_uci, weight in moves.items():
                move_int = self._encode_move(move_uci)
                entries.append((position_hash, move_int, weight, 0))
        
        # Sort entries by position hash (required for binary search)
        entries.sort(key=lambda e: e[0])
        
        # Write to binary file
        with open(output_path, 'wb') as f:
            for position_hash, move_int, weight, learn in entries:
                # Pack as big-endian: Q (8 bytes), H (2 bytes), H (2 bytes), I (4 bytes)
                packed = struct.pack('>QHHI', position_hash, move_int, weight, learn)
                f.write(packed)
        
        print(f"\n{'='*60}")
        print(f"Book saved to: {output_path}")
        print(f"Unique positions: {len(self.positions)}")
        print(f"Total entries: {len(entries)}")
        print(f"{'='*60}")

    def encode_games(self,pgn_file):
        parser = pgn.PGNParser()
        games = parser.parse_file(pgn_file)

        for current_game in games:
            board = Board()

            for index, move in enumerate(current_game.uci_moves):
                if index > 20:
                    break

                self.add_position(board.to_fen(),move)
                board.push_uci(move)
