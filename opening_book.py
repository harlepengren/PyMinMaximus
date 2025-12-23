import struct
import random
from typing import Optional, List, Tuple
from zobrist import ZobristHash
from constants import *

class OpeningBook:
    """
    Reader for Polyglot opening book format (.bin files).
    """
    
    def __init__(self, book_path: Optional[str] = None):
        """
        Initialize opening book.
        
        Args:
            book_path: Path to Polyglot .bin file (None = no book)
        """
        self.book_path = book_path
        self.book_enabled = book_path is not None
        self.max_book_ply = 20  # Stay in book for first 20 plies
        self.zobrist = ZobristHash()
        
        if self.book_enabled:
            try:
                # Test that we can open the book
                with open(book_path, 'rb') as f:
                    # Try reading one entry
                    entry = f.read(16)
                    if len(entry) == 16:
                        print(f"✓ Opening book loaded: {book_path}")
                    else:
                        raise ValueError("Invalid book format")
            except Exception as e:
                print(f"✗ Could not load opening book: {e}")
                self.book_enabled = False
    
    def _decode_move(self, move_int):
        """
        Decode Polyglot move format.
        
        Move format (16 bits):
        - Bits 0-5: to_square (0-63)
        - Bits 6-11: from_square (0-63)
        - Bits 12-14: promotion piece (0=none, 1=knight, 2=bishop, 3=rook, 4=queen)
        
        Returns:
            Tuple of (from_row, from_col, to_row, to_col, promotion)
        """
        to_square = move_int & 0x3F
        from_square = (move_int >> 6) & 0x3F
        promo = (move_int >> 12) & 0x7
        
        # Convert square numbers to row/col
        to_row = to_square // 8
        to_col = to_square % 8
        from_row = from_square // 8
        from_col = from_square % 8
        
        # Convert promotion code to piece type
        promotion = None
        if promo == 1:
            promotion = KNIGHT
        elif promo == 2:
            promotion = BISHOP
        elif promo == 3:
            promotion = ROOK
        elif promo == 4:
            promotion = QUEEN
        
        return (from_row, from_col, to_row, to_col, promotion)
    
    def _find_entries(self, position_hash):
        """
        Find all book entries for a position using binary search.
        
        The book file is sorted by hash, so we use binary search
        to find the first matching entry, then read all consecutive matches.
        
        Returns:
            List of (move_tuple, weight) entries
        """
        if not self.book_enabled:
            return []
        
        entries = []
        
        try:
            with open(self.book_path, 'rb') as f:
                # Get file size and entry count
                f.seek(0, 2)  # Seek to end
                file_size = f.tell()
                entry_count = file_size // 16
                
                if entry_count == 0:
                    return []
                
                # Binary search for first occurrence of this hash
                left, right = 0, entry_count - 1
                first_match = -1
                
                while left <= right:
                    mid = (left + right) // 2
                    f.seek(mid * 16)
                    
                    # Read hash from entry
                    entry_hash = struct.unpack('>Q', f.read(8))[0]
                    
                    if entry_hash < position_hash:
                        left = mid + 1
                    elif entry_hash > position_hash:
                        right = mid - 1
                    else:
                        # Found a match, but keep searching left for first occurrence
                        first_match = mid
                        right = mid - 1
                
                # If no match found, return empty
                if first_match == -1:
                    return []
                
                # Read all consecutive entries with matching hash
                f.seek(first_match * 16)
                
                while f.tell() < file_size:
                    entry_data = f.read(16)
                    if len(entry_data) < 16:
                        break
                    
                    # Unpack entry: Q=8 bytes hash, H=2 bytes move, H=2 bytes weight, I=4 bytes learn
                    entry_hash, move_int, weight, learn = struct.unpack('>QHHI', entry_data)
                    
                    # Stop when we hit a different position
                    if entry_hash != position_hash:
                        break
                    
                    # Decode move and add to list
                    move_tuple = self._decode_move(move_int)
                    entries.append((move_tuple, weight))
        
        except Exception as e:
            print(f"Book lookup error: {e}")
            return []
        
        return entries
    
    def get_book_move(self, board, move_number: int, 
                      selection_mode: str = "weighted") -> Optional[str]:
        """
        Get a move from the opening book.
        
        Args:
            board: Current board position
            move_number: Current move number (for max_book_ply check)
            selection_mode: How to select from multiple book moves
                - "best": Choose highest weighted move
                - "weighted": Probabilistic selection based on weights
                - "random": Random selection (ignores weights)
        
        Returns:
            Move in UCI format (e.g., "e2e4") or None if not in book
        """
        if not self.book_enabled:
            return None
        
        # Check if we're still in book range
        ply = (move_number - 1) * 2 + (0 if board.to_move == WHITE else 1)
        if ply >= self.max_book_ply:
            return None
        
        # Get position hash
        position_hash = self.zobrist.hash_position(board)
        
        # Find all book entries for this position
        entries = self._find_entries(position_hash)
        
        if not entries:
            return None
        
        # Select move based on mode
        if selection_mode == "best":
            # Choose highest weighted move
            move_tuple, weight = max(entries, key=lambda e: e[1])
        
        elif selection_mode == "weighted":
            # Probabilistic selection based on weights
            total_weight = sum(w for _, w in entries)
            if total_weight == 0:
                # All weights are zero, choose randomly
                move_tuple, weight = random.choice(entries)
            else:
                # Weighted random selection
                r = random.uniform(0, total_weight)
                cumulative = 0
                move_tuple = entries[0][0]
                for m, w in entries:
                    cumulative += w
                    if r <= cumulative:
                        move_tuple = m
                        break
        
        else:  # random
            move_tuple, weight = random.choice(entries)
        
        # Convert move tuple to UCI format
        from_row, from_col, to_row, to_col, promotion = move_tuple
        
        files = 'abcdefgh'
        uci = f"{files[from_col]}{from_row + 1}{files[to_col]}{to_row + 1}"
        
        # Add promotion piece if present
        if promotion:
            promo_chars = {KNIGHT: 'n', BISHOP: 'b', ROOK: 'r', QUEEN: 'q'}
            uci += promo_chars.get(promotion, '')
        
        return uci
    
    def is_in_book(self, board) -> bool:
        """Check if current position is in the book."""
        if not self.book_enabled:
            return False
        
        position_hash = self.zobrist.hash_position(board)
        entries = self._find_entries(position_hash)
        return len(entries) > 0
    
    def get_book_moves_info(self, board) -> List[Tuple[str, int]]:
        """
        Get all book moves with their weights for the current position.
        
        Returns:
            List of (move_uci, weight) tuples, sorted by weight descending
        """
        if not self.book_enabled:
            return []
        
        position_hash = self.zobrist.hash_position(board)
        entries = self._find_entries(position_hash)
        
        result = []
        files = 'abcdefgh'
        
        for move_tuple, weight in entries:
            from_row, from_col, to_row, to_col, promotion = move_tuple
            uci = f"{files[from_col]}{from_row + 1}{files[to_col]}{to_row + 1}"
            
            if promotion:
                promo_chars = {KNIGHT: 'n', BISHOP: 'b', ROOK: 'r', QUEEN: 'q'}
                uci += promo_chars.get(promotion, '')
            
            result.append((uci, weight))
        
        # Sort by weight, highest first
        result.sort(key=lambda x: -x[1])
        
        return result
