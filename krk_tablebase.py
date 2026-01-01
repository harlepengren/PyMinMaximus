"""
KRK Endgame Tablebase Generator
================================
Generates a complete tablebase for King + Rook vs King endgame.

This uses retrograde analysis:
1. Start with terminal positions (checkmate, stalemate)
2. Work backwards to find positions that lead to these outcomes
3. Iterate until all positions are classified

Position encoding:
- White King: 64 squares
- White Rook: 64 squares  
- Black King: 64 squares
- Side to move: 2 possibilities
Total: 64 * 64 * 64 * 2 = 524,288 theoretical positions

With symmetry reduction (horizontal mirroring), we can halve this.
Illegal positions (overlapping pieces) are filtered out.
"""

from constants import *

class KRKTablebase:
    # Outcome constants
    UNKNOWN = 0
    DRAW = 1
    WHITE_WIN = 2
    BLACK_WIN = 3  # Shouldn't occur in KRK, but included for completeness
    
    def __init__(self):
        """Initialize the tablebase."""
        # Dictionary mapping position keys to (outcome, depth)
        # outcome: DRAW or WHITE_WIN
        # depth: moves to mate (DTM - Distance To Mate)
        self.table = {}
        self.positions_solved = 0
        
    def square_to_coords(self, square):
        """Convert square index (0-63) to (row, col)."""
        return (square // 8, square % 8)
    
    def coords_to_square(self, row, col):
        """Convert (row, col) to square index (0-63)."""
        if not (0 <= row < 8 and 0 <= col < 8):
            return None
        return row * 8 + col
    
    def encode_position(self, wk_sq, wr_sq, bk_sq, white_to_move):
        """
        Encode position as a unique key.
        We use horizontal mirroring symmetry to reduce storage.
        """
        # Apply horizontal mirroring if king is on right half
        wk_row, wk_col = self.square_to_coords(wk_sq)
        wr_row, wr_col = self.square_to_coords(wr_sq)
        bk_row, bk_col = self.square_to_coords(bk_sq)
        
        if wk_col > 3:  # Mirror if on right half
            wk_col = 7 - wk_col
            wr_col = 7 - wr_col
            bk_col = 7 - bk_col
            
            wk_sq = self.coords_to_square(wk_row, wk_col)
            wr_sq = self.coords_to_square(wr_row, wr_col)
            bk_sq = self.coords_to_square(bk_row, bk_col)
        
        return (wk_sq, wr_sq, bk_sq, white_to_move)
    
    def is_legal_position(self, wk_sq, wr_sq, bk_sq):
        """Check if position is legal (no overlapping pieces)."""
        if wk_sq == wr_sq or wk_sq == bk_sq or wr_sq == bk_sq:
            return False
        
        # Kings can't be adjacent
        wk_row, wk_col = self.square_to_coords(wk_sq)
        bk_row, bk_col = self.square_to_coords(bk_sq)
        
        row_diff = abs(wk_row - bk_row)
        col_diff = abs(wk_col - bk_col)
        
        if row_diff <= 1 and col_diff <= 1:
            return False
        
        return True
    
    def is_attacked_by_rook(self, rook_sq, target_sq, blocking_sq=None):
        """Check if rook attacks a square (with optional blocking piece)."""
        r_row, r_col = self.square_to_coords(rook_sq)
        t_row, t_col = self.square_to_coords(target_sq)
        
        # Rook must be on same rank or file
        if r_row != t_row and r_col != t_col:
            return False
        
        # Check for blocking piece
        if blocking_sq is not None:
            b_row, b_col = self.square_to_coords(blocking_sq)
            
            # If moving horizontally
            if r_row == t_row:
                min_col = min(r_col, t_col)
                max_col = max(r_col, t_col)
                # Blocker must be on same row and between rook and target
                if b_row == r_row and min_col < b_col < max_col:
                    return False
            # If moving vertically
            else:
                min_row = min(r_row, t_row)
                max_row = max(r_row, t_row)
                if b_col == r_col and min_row < b_row < max_row:
                    return False
        
        return True
    
    def is_attacked_by_king(self, king_sq, target_sq):
        """Check if king attacks a square."""
        k_row, k_col = self.square_to_coords(king_sq)
        t_row, t_col = self.square_to_coords(target_sq)
        
        return abs(k_row - t_row) <= 1 and abs(k_col - t_col) <= 1
    
    def generate_king_moves(self, king_sq, occupied_squares):
        """Generate all legal king moves from a square."""
        moves = []
        k_row, k_col = self.square_to_coords(king_sq)
        
        for drow in [-1, 0, 1]:
            for dcol in [-1, 0, 1]:
                if drow == 0 and dcol == 0:
                    continue
                
                new_row = k_row + drow
                new_col = k_col + dcol
                new_sq = self.coords_to_square(new_row, new_col)
                
                if new_sq is not None and new_sq not in occupied_squares:
                    moves.append(new_sq)
        
        return moves
    
    def generate_rook_moves(self, rook_sq, occupied_squares):
        """Generate all legal rook moves from a square."""
        moves = []
        r_row, r_col = self.square_to_coords(rook_sq)
        
        # Horizontal moves
        for dcol in [-1, 1]:
            col = r_col + dcol
            while 0 <= col < 8:
                sq = self.coords_to_square(r_row, col)
                if sq in occupied_squares:
                    break
                moves.append(sq)
                col += dcol
        
        # Vertical moves
        for drow in [-1, 1]:
            row = r_row + drow
            while 0 <= row < 8:
                sq = self.coords_to_square(row, r_col)
                if sq in occupied_squares:
                    break
                moves.append(sq)
                row += drow
        
        return moves
    
    def is_checkmate(self, wk_sq, wr_sq, bk_sq):
        """
        Check if black king is checkmated.
        Black is in check and has no legal moves.
        """
        # Black king must be in check from rook
        if not self.is_attacked_by_rook(wr_sq, bk_sq, wk_sq):
            return False
        
        # Check if black king has any legal moves
        occupied = {wk_sq, wr_sq}
        black_king_moves = self.generate_king_moves(bk_sq, occupied)
        
        for bk_new_sq in black_king_moves:
            # Can't move into check from white king
            if self.is_attacked_by_king(wk_sq, bk_new_sq):
                continue
            
            # Can't move into check from rook
            if self.is_attacked_by_rook(wr_sq, bk_new_sq, wk_sq):
                continue
            
            # Found a legal move - not checkmate
            return False
        
        # No legal moves - checkmate!
        return True
    
    def is_stalemate(self, wk_sq, wr_sq, bk_sq):
        """
        Check if black king is stalemated.
        Black is NOT in check but has no legal moves.
        """
        # Black king must NOT be in check from rook
        if self.is_attacked_by_rook(wr_sq, bk_sq, wk_sq):
            return False
        
        # Black king must NOT be in check from white king (shouldn't happen but check anyway)
        if self.is_attacked_by_king(wk_sq, bk_sq):
            return False
        
        # Check if black king has any legal moves
        occupied = {wk_sq, wr_sq}
        black_king_moves = self.generate_king_moves(bk_sq, occupied)
        
        # If no squares to move to at all, it's stalemate
        if len(black_king_moves) == 0:
            return True
        
        for bk_new_sq in black_king_moves:
            # Can't move into check from white king
            if self.is_attacked_by_king(wk_sq, bk_new_sq):
                continue
            
            # Can't move into check from rook
            if self.is_attacked_by_rook(wr_sq, bk_new_sq, wk_sq):
                continue
            
            # Found a legal move - not stalemate
            return False
        
        # No legal moves but not in check - stalemate!
        return True
    
    def generate_all_positions(self):
        """Generate all legal KRK positions."""
        positions = []
        
        for wk_sq in range(64):
            for wr_sq in range(64):
                for bk_sq in range(64):
                    if not self.is_legal_position(wk_sq, wr_sq, bk_sq):
                        continue
                    
                    # Both sides to move
                    positions.append((wk_sq, wr_sq, bk_sq, True))   # White to move
                    positions.append((wk_sq, wr_sq, bk_sq, False))  # Black to move
        
        return positions
    
    def classify_terminal_positions(self, positions):
        """
        Phase 1: Classify all terminal positions (checkmate, stalemate).
        Returns number of positions classified.
        """
        count = 0
        
        for wk_sq, wr_sq, bk_sq, white_to_move in positions:
            key = self.encode_position(wk_sq, wr_sq, bk_sq, white_to_move)
            
            if key in self.table:
                continue
            
            # Check for checkmate (black is mated)
            if self.is_checkmate(wk_sq, wr_sq, bk_sq):
                self.table[key] = (self.WHITE_WIN, 0)
                count += 1
                continue
            
            # Check for stalemate (only when black to move)
            if not white_to_move and self.is_stalemate(wk_sq, wr_sq, bk_sq):
                self.table[key] = (self.DRAW, 0)
                count += 1
                continue
        
        return count
    
    def retrograde_iteration(self, positions, current_depth):
        """
        Single iteration of retrograde analysis.
        
        For each unsolved position:
        - Generate all legal moves
        - Check outcomes of resulting positions
        - If we can force a mate, mark this position with current_depth
        
        Returns number of new positions solved.
        """
        newly_solved = 0
        
        for wk_sq, wr_sq, bk_sq, white_to_move in positions:
            key = self.encode_position(wk_sq, wr_sq, bk_sq, white_to_move)
            
            # Skip if already solved
            if key in self.table:
                continue
            
            if white_to_move:
                # White to move - looking for winning moves
                can_win = False
                all_moves_solved = True
                
                occupied = {bk_sq}
                
                # Try white king moves
                wk_moves = self.generate_king_moves(wk_sq, occupied)
                for wk_new_sq in wk_moves:
                    # Can't move into check from rook's original position
                    if self.is_attacked_by_rook(wr_sq, wk_new_sq, bk_sq):
                        continue
                    
                    if not self.is_legal_position(wk_new_sq, wr_sq, bk_sq):
                        continue
                    
                    next_key = self.encode_position(wk_new_sq, wr_sq, bk_sq, False)
                    
                    if next_key not in self.table:
                        all_moves_solved = False
                    elif self.table[next_key][0] == self.WHITE_WIN:
                        can_win = True
                        break
                
                if can_win:
                    self.table[key] = (self.WHITE_WIN, current_depth)
                    newly_solved += 1
                    continue
                
                # Try white rook moves
                if not can_win:
                    occupied_with_king = {wk_sq, bk_sq}
                    wr_moves = self.generate_rook_moves(wr_sq, occupied_with_king)
                    
                    for wr_new_sq in wr_moves:
                        if not self.is_legal_position(wk_sq, wr_new_sq, bk_sq):
                            continue
                        
                        # Check if this move gives check
                        gives_check = self.is_attacked_by_rook(wr_new_sq, bk_sq, wk_sq)
                        
                        # If black is in check, verify it's legal (white king not in check)
                        if gives_check:
                            if self.is_attacked_by_king(bk_sq, wk_sq):
                                continue  # Illegal - white king in check
                        
                        next_key = self.encode_position(wk_sq, wr_new_sq, bk_sq, False)
                        
                        if next_key not in self.table:
                            all_moves_solved = False
                        elif self.table[next_key][0] == self.WHITE_WIN:
                            can_win = True
                            break
                
                if can_win:
                    self.table[key] = (self.WHITE_WIN, current_depth)
                    newly_solved += 1
                elif all_moves_solved:
                    # All moves explored, none win - this is a draw
                    self.table[key] = (self.DRAW, 0)
                    newly_solved += 1
                    
            else:
                # Black to move - can black force a draw or does white win?
                can_draw = False
                all_moves_lose = True
                
                occupied = {wk_sq, wr_sq}
                bk_moves = self.generate_king_moves(bk_sq, occupied)
                
                for bk_new_sq in bk_moves:
                    # Can't move into check from white king
                    if self.is_attacked_by_king(wk_sq, bk_new_sq):
                        continue
                    
                    # Can't move into check from rook
                    if self.is_attacked_by_rook(wr_sq, bk_new_sq, wk_sq):
                        continue
                    
                    next_key = self.encode_position(wk_sq, wr_sq, bk_new_sq, True)
                    
                    if next_key not in self.table:
                        all_moves_lose = False
                    elif self.table[next_key][0] == self.DRAW:
                        can_draw = True
                        break
                
                if can_draw:
                    self.table[key] = (self.DRAW, 0)
                    newly_solved += 1
                elif all_moves_lose:
                    # All moves lead to white win - this is a white win
                    self.table[key] = (self.WHITE_WIN, current_depth)
                    newly_solved += 1
        
        return newly_solved
    
    def generate(self):
        """
        Generate the complete KRK tablebase using retrograde analysis.
        """
        print("Generating KRK Tablebase...")
        print("=" * 60)
        
        # Generate all legal positions
        print("Generating all legal positions...")
        positions = self.generate_all_positions()
        print(f"Total legal positions: {len(positions):,}")
        
        # Phase 1: Classify terminal positions
        print("\nPhase 1: Classifying terminal positions...")
        terminal_count = self.classify_terminal_positions(positions)
        print(f"Terminal positions found: {terminal_count:,}")
        print(f"  - Checkmates and stalemates")
        
        # Phase 2: Retrograde analysis
        print("\nPhase 2: Retrograde analysis...")
        depth = 1
        max_depth = 100  # Safety limit
        
        while depth <= max_depth:
            newly_solved = self.retrograde_iteration(positions, depth)
            
            if newly_solved == 0:
                print(f"\nConverged at depth {depth}")
                break
            
            total_solved = len(self.table)
            percentage = (total_solved / len(positions)) * 100
            print(f"Depth {depth:2d}: +{newly_solved:5,} new positions "
                  f"(Total: {total_solved:6,} / {len(positions):,} = {percentage:5.1f}%)")
            
            depth += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("Tablebase Generation Complete!")
        print("=" * 60)
        print(f"Total positions: {len(positions):,}")
        print(f"Positions solved: {len(self.table):,}")
        print(f"Maximum depth: {depth - 1}")
        
        # Statistics
        wins = sum(1 for outcome, _ in self.table.values() if outcome == self.WHITE_WIN)
        draws = sum(1 for outcome, _ in self.table.values() if outcome == self.DRAW)
        
        print(f"\nOutcome distribution:")
        print(f"  White wins: {wins:,} ({wins/len(self.table)*100:.1f}%)")
        print(f"  Draws:      {draws:,} ({draws/len(self.table)*100:.1f}%)")
        
        # Find longest mate
        max_dtm = max((depth for outcome, depth in self.table.values() 
                       if outcome == self.WHITE_WIN), default=0)
        print(f"\nLongest forced mate: {max_dtm} moves")
    
    def probe(self, wk_sq, wr_sq, bk_sq, white_to_move):
        """
        Look up a position in the tablebase.
        
        Returns: (outcome, depth) or None if position is illegal/not in tablebase
        """
        if not self.is_legal_position(wk_sq, wr_sq, bk_sq):
            return None
        
        key = self.encode_position(wk_sq, wr_sq, bk_sq, white_to_move)
        return self.table.get(key)
    
    def probe_from_board(self, board):
        """
        Probe the tablebase from a Board object.
        Only works if the position is a KRK endgame.
        """
        # Count pieces
        white_king = None
        white_rook = None
        black_king = None
        piece_count = 0
        
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece == EMPTY:
                    continue
                
                piece_count += 1
                piece_type = piece & 7
                color = piece & 24
                
                if piece == (WHITE | KING):
                    white_king = self.coords_to_square(row, col)
                elif piece == (WHITE | ROOK):
                    white_rook = self.coords_to_square(row, col)
                elif piece == (BLACK | KING):
                    black_king = self.coords_to_square(row, col)
        
        # Must be exactly 3 pieces: WK, WR, BK
        if piece_count != 3 or white_king is None or white_rook is None or black_king is None:
            return None
        
        white_to_move = (board.to_move == WHITE)
        return self.probe(white_king, white_rook, black_king, white_to_move)
    
    def save(self, filename):
        """Save tablebase to file."""
        import pickle
        with open(filename, 'wb') as f:
            pickle.dump(self.table, f)
        print(f"\nTablebase saved to {filename}")
        print(f"File size: {len(pickle.dumps(self.table)) / 1024 / 1024:.2f} MB")
    
    def load(self, filename):
        """Load tablebase from file."""
        import pickle
        with open(filename, 'rb') as f:
            self.table = pickle.load(f)
        #print(f"Tablebase loaded from {filename}")
        #print(f"Positions in tablebase: {len(self.table):,}")


def square_name(square):
    """Convert square index to algebraic notation."""
    if square is None:
        return "??"
    row, col = square // 8, square % 8
    return f"{'abcdefgh'[col]}{row + 1}"


def demo():
    """Demonstrate the KRK tablebase."""
    print("\nKRK Endgame Tablebase Demo")
    print("=" * 60)
    
    # Generate the tablebase
    tb = KRKTablebase()
    tb.generate()
    
    # Example lookups
    print("\n\nExample Position Lookups:")
    print("=" * 60)
    
    # Example 1: Basic checkmate
    wk, wr, bk = 8, 0, 16  # a2, a1, a3 (files aligned for checkmate)
    result = tb.probe(wk, wr, bk, True)
    if result:
        outcome_str = "White wins" if result[0] == tb.WHITE_WIN else "Draw"
        print(f"\nPosition: WK={square_name(wk)}, WR={square_name(wr)}, BK={square_name(bk)}")
        print(f"Result: {outcome_str} in {result[1]} moves")
    
    # Example 2: Longer mate
    wk, wr, bk = 0, 63, 7  # a1, h8, h1
    result = tb.probe(wk, wr, bk, True)
    if result:
        outcome_str = "White wins" if result[0] == tb.WHITE_WIN else "Draw"
        print(f"\nPosition: WK={square_name(wk)}, WR={square_name(wr)}, BK={square_name(bk)}")
        print(f"Result: {outcome_str} in {result[1]} moves")
    
    # Example 3: Stalemate position
    wk, wr, bk = 10, 8, 0  # c2, a2, a1 (stalemate)
    result = tb.probe(wk, wr, bk, False)  # Black to move
    if result:
        outcome_str = "White wins" if result[0] == tb.WHITE_WIN else "Draw"
        print(f"\nPosition: WK={square_name(wk)}, WR={square_name(wr)}, BK={square_name(bk)} (Black to move)")
        print(f"Result: {outcome_str}")
    
    # Save to file
    tb.save("krk_tablebase.pkl")
    
    return tb


if __name__ == "__main__":
    tb = demo()
