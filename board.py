
from move import Move
from constants import *

class Board:
    def __init__(self):
        # 8x8 board, index [0][0] is a1, [7][7] is h8
        self.board = [[EMPTY for _ in range(8)] for _ in range(8)]
        
        # Game state
        self.to_move = WHITE
        self.castling_rights = {
            'K': True,  # White kingside
            'Q': True,  # White queenside
            'k': True,  # Black kingside
            'q': True   # Black queenside
        }
        self.en_passant_square = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        
        self.setup_initial_position()
    
    def setup_initial_position(self):
        """Set up the standard starting position."""
        # Black pieces (rank 8 and 7)
        back_rank = [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK]
        for i in range(8):
            self.board[7][i] = BLACK | back_rank[i]
            self.board[6][i] = BLACK | PAWN
        
        # White pieces (rank 2 and 1)
        for i in range(8):
            self.board[1][i] = WHITE | PAWN
            self.board[0][i] = WHITE | back_rank[i]
    
    def piece_at(self, row, col):
        """Get the piece at a given square."""
        return self.board[row][col]
    
    def is_square_attacked(self, row, col, by_color):
        """Check if a square is attacked by a given color."""
        # We'll implement this after move generation
        pass

    def generate_pawn_moves(self, row, col, moves):
        """Generate all pawn moves from a given square."""
        piece = self.board[row][col]
        color = piece & 24
        
        if color == WHITE:
            direction = 1
            start_row = 1
            promotion_row = 7
        else:
            direction = -1
            start_row = 6
            promotion_row = 0
        
        # Single push
        if self.board[row + direction][col] == EMPTY:
            if row + direction == promotion_row:
                # Promotions
                for promo_piece in [QUEEN, ROOK, BISHOP, KNIGHT]:
                    moves.append(Move(row, col, row + direction, col, 
                                    promotion=promo_piece))
            else:
                moves.append(Move(row, col, row + direction, col))
            
            # Double push from starting position
            if row == start_row and self.board[row + 2 * direction][col] == EMPTY:
                moves.append(Move(row, col, row + 2 * direction, col))
        
        # Captures
        for dcol in [-1, 1]:
            new_col = col + dcol
            if 0 <= new_col < 8:
                new_row = row + direction
                target = self.board[new_row][new_col]
                
                # Regular capture
                if target != EMPTY and (target & 24) != color:
                    if new_row == promotion_row:
                        for promo_piece in [QUEEN, ROOK, BISHOP, KNIGHT]:
                            moves.append(Move(row, col, new_row, new_col, 
                                            promotion=promo_piece))
                    else:
                        moves.append(Move(row, col, new_row, new_col))
                
                # En passant
                if self.en_passant_square == (new_row, new_col):
                    moves.append(Move(row, col, new_row, new_col, 
                                    is_en_passant=True))
    
    def generate_knight_moves(self, row, col, moves):
        """Generate all knight moves from a given square."""
        piece = self.board[row][col]
        color = piece & 24
        
        knight_offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for drow, dcol in knight_offsets:
            new_row, new_col = row + drow, col + dcol
            
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.board[new_row][new_col]
                if target == EMPTY or (target & 24) != color:
                    moves.append(Move(row, col, new_row, new_col))
    
    def generate_sliding_moves(self, row, col, moves, directions):
        """Generate moves for sliding pieces (bishop, rook, queen)."""
        piece = self.board[row][col]
        color = piece & 24
        
        for drow, dcol in directions:
            new_row, new_col = row + drow, col + dcol
            
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.board[new_row][new_col]
                
                if target == EMPTY:
                    moves.append(Move(row, col, new_row, new_col))
                elif (target & 24) != color:
                    moves.append(Move(row, col, new_row, new_col))
                    break  # Can't move past a capture
                else:
                    break  # Blocked by own piece
                
                new_row += drow
                new_col += dcol
    
    def generate_bishop_moves(self, row, col, moves):
        """Generate all bishop moves."""
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        self.generate_sliding_moves(row, col, moves, directions)
    
    def generate_rook_moves(self, row, col, moves):
        """Generate all rook moves."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.generate_sliding_moves(row, col, moves, directions)
    
    def generate_queen_moves(self, row, col, moves):
        """Generate all queen moves."""
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        self.generate_sliding_moves(row, col, moves, directions)
    
    def generate_king_moves(self, row, col, moves):
        """Generate all king moves including castling."""
        piece = self.board[row][col]
        color = piece & 24
        
        # Regular king moves
        for drow in [-1, 0, 1]:
            for dcol in [-1, 0, 1]:
                if drow == 0 and dcol == 0:
                    continue
                
                new_row, new_col = row + drow, col + dcol
                
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = self.board[new_row][new_col]
                    if target == EMPTY or (target & 24) != color:
                        moves.append(Move(row, col, new_row, new_col))
        
        # Castling
        if color == WHITE and row == 0:
            # Kingside
            if (self.castling_rights['K'] and 
                self.board[0][5] == EMPTY and 
                self.board[0][6] == EMPTY):
                moves.append(Move(0, 4, 0, 6, is_castling=True))
            
            # Queenside
            if (self.castling_rights['Q'] and 
                self.board[0][1] == EMPTY and 
                self.board[0][2] == EMPTY and 
                self.board[0][3] == EMPTY):
                moves.append(Move(0, 4, 0, 2, is_castling=True))
        
        elif color == BLACK and row == 7:
            # Kingside
            if (self.castling_rights['k'] and 
                self.board[7][5] == EMPTY and 
                self.board[7][6] == EMPTY):
                moves.append(Move(7, 4, 7, 6, is_castling=True))
            
            # Queenside
            if (self.castling_rights['q'] and 
                self.board[7][1] == EMPTY and 
                self.board[7][2] == EMPTY and 
                self.board[7][3] == EMPTY):
                moves.append(Move(7, 4, 7, 2, is_castling=True))
    
    def generate_pseudo_legal_moves(self):
        """Generate all pseudo-legal moves for the current position."""
        moves = []
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                
                if piece == EMPTY or (piece & 24) != self.to_move:
                    continue
                
                piece_type = piece & 7
                
                if piece_type == PAWN:
                    self.generate_pawn_moves(row, col, moves)
                elif piece_type == KNIGHT:
                    self.generate_knight_moves(row, col, moves)
                elif piece_type == BISHOP:
                    self.generate_bishop_moves(row, col, moves)
                elif piece_type == ROOK:
                    self.generate_rook_moves(row, col, moves)
                elif piece_type == QUEEN:
                    self.generate_queen_moves(row, col, moves)
                elif piece_type == KING:
                    self.generate_king_moves(row, col, moves)
        
        return moves
    
    def make_move(self, move):
        """Make a move on the board and return information needed to unmake it."""
        # Store state for unmaking
        undo_info = {
            'captured_piece': self.board[move.to_row][move.to_col],
            'castling_rights': self.castling_rights.copy(),
            'en_passant_square': self.en_passant_square,
            'halfmove_clock': self.halfmove_clock
        }
        
        piece = self.board[move.from_row][move.from_col]
        piece_type = piece & 7
        
        # Move the piece
        self.board[move.to_row][move.to_col] = piece
        self.board[move.from_row][move.from_col] = EMPTY
        
        # Handle promotion
        if move.promotion:
            self.board[move.to_row][move.to_col] = (piece & 24) | move.promotion
        
        # Handle en passant capture
        if move.is_en_passant:
            capture_row = move.from_row
            self.board[capture_row][move.to_col] = EMPTY
        
        # Handle castling
        if move.is_castling:
            # Move the rook
            if move.to_col == 6:  # Kingside
                self.board[move.to_row][5] = self.board[move.to_row][7]
                self.board[move.to_row][7] = EMPTY
            else:  # Queenside
                self.board[move.to_row][3] = self.board[move.to_row][0]
                self.board[move.to_row][0] = EMPTY
        
        # Update en passant square
        self.en_passant_square = None
        if piece_type == PAWN and abs(move.to_row - move.from_row) == 2:
            self.en_passant_square = ((move.from_row + move.to_row) // 2, move.from_col)
        
        # Update castling rights
        if piece_type == KING:
            if self.to_move == WHITE:
                self.castling_rights['K'] = False
                self.castling_rights['Q'] = False
            else:
                self.castling_rights['k'] = False
                self.castling_rights['q'] = False
        
        if piece_type == ROOK:
            if self.to_move == WHITE:
                if move.from_row == 0 and move.from_col == 0:
                    self.castling_rights['Q'] = False
                elif move.from_row == 0 and move.from_col == 7:
                    self.castling_rights['K'] = False
            else:
                if move.from_row == 7 and move.from_col == 0:
                    self.castling_rights['q'] = False
                elif move.from_row == 7 and move.from_col == 7:
                    self.castling_rights['k'] = False
        
        # Update halfmove clock
        if piece_type == PAWN or undo_info['captured_piece'] != EMPTY:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        
        # Update move counters
        if self.to_move == BLACK:
            self.fullmove_number += 1
        
        self.to_move = BLACK if self.to_move == WHITE else WHITE
        
        return undo_info
    
    def unmake_move(self, move, undo_info):
        """Unmake a move and restore the previous position."""
        # Switch back to the side that made the move
        self.to_move = BLACK if self.to_move == WHITE else WHITE
        
        # Restore move counters
        if self.to_move == BLACK:
            self.fullmove_number -= 1
        
        piece = self.board[move.to_row][move.to_col]
        
        # Handle promotion (restore pawn)
        if move.promotion:
            piece = (piece & 24) | PAWN
        
        # Move piece back
        self.board[move.from_row][move.from_col] = piece
        self.board[move.to_row][move.to_col] = undo_info['captured_piece']
        
        # Handle en passant
        if move.is_en_passant:
            capture_row = move.from_row
            opponent_color = BLACK if self.to_move == WHITE else WHITE
            self.board[capture_row][move.to_col] = opponent_color | PAWN
        
        # Handle castling
        if move.is_castling:
            if move.to_col == 6:  # Kingside
                self.board[move.to_row][7] = self.board[move.to_row][5]
                self.board[move.to_row][5] = EMPTY
            else:  # Queenside
                self.board[move.to_row][0] = self.board[move.to_row][3]
                self.board[move.to_row][3] = EMPTY
        
        # Restore game state
        self.castling_rights = undo_info['castling_rights']
        self.en_passant_square = undo_info['en_passant_square']
        self.halfmove_clock = undo_info['halfmove_clock']

    def is_square_attacked(self, row, col, by_color):
        """Check if a square is attacked by pieces of a given color."""
        # Check for pawn attacks
        if by_color == WHITE:
            pawn_direction = 1
        else:
            pawn_direction = -1
        
        for dcol in [-1, 1]:
            pawn_row = row - pawn_direction
            pawn_col = col + dcol
            if 0 <= pawn_row < 8 and 0 <= pawn_col < 8:
                piece = self.board[pawn_row][pawn_col]
                if piece == (by_color | PAWN):
                    return True
        
        # Check for knight attacks
        knight_offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for drow, dcol in knight_offsets:
            new_row, new_col = row + drow, col + dcol
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                piece = self.board[new_row][new_col]
                if piece == (by_color | KNIGHT):
                    return True
        
        # Check for sliding piece attacks
        # Diagonal (bishop and queen)
        for drow, dcol in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            new_row, new_col = row + drow, col + dcol
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                piece = self.board[new_row][new_col]
                if piece != EMPTY:
                    if (piece & 24) == by_color:
                        piece_type = piece & 7
                        if piece_type in [BISHOP, QUEEN]:
                            return True
                    break
                new_row += drow
                new_col += dcol
        
        # Straight (rook and queen)
        for drow, dcol in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = row + drow, col + dcol
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                piece = self.board[new_row][new_col]
                if piece != EMPTY:
                    if (piece & 24) == by_color:
                        piece_type = piece & 7
                        if piece_type in [ROOK, QUEEN]:
                            return True
                    break
                new_row += drow
                new_col += dcol
        
        # Check for king attacks
        for drow in [-1, 0, 1]:
            for dcol in [-1, 0, 1]:
                if drow == 0 and dcol == 0:
                    continue
                new_row, new_col = row + drow, col + dcol
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    piece = self.board[new_row][new_col]
                    if piece == (by_color | KING):
                        return True
        
        return False
    
    def find_king(self, color):
        """Find the king's position for a given color."""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece == (color | KING):
                    return (row, col)
        return None
    
    def is_in_check(self, color):
        """Check if the given color's king is in check."""
        king_pos = self.find_king(color)
        if king_pos is None:
            return False
        
        opponent_color = BLACK if color == WHITE else WHITE
        return self.is_square_attacked(king_pos[0], king_pos[1], opponent_color)
    
    def is_legal_move(self, move):
        """Check if a move is legal (doesn't leave king in check)."""
        undo_info = self.make_move(move)
        
        # The king of the side that just moved
        moving_color = BLACK if self.to_move == WHITE else WHITE
        
        # Special check for castling - squares must not be under attack
        if move.is_castling:
            king_row = move.from_row
            opponent_color = BLACK if moving_color == WHITE else WHITE
            
            # Check that king doesn't move through check
            if move.to_col == 6:  # Kingside
                for col in [4, 5, 6]:
                    if self.is_square_attacked(king_row, col, opponent_color):
                        self.unmake_move(move, undo_info)
                        return False
            else:  # Queenside
                for col in [2, 3, 4]:
                    if self.is_square_attacked(king_row, col, opponent_color):
                        self.unmake_move(move, undo_info)
                        return False
        
        legal = not self.is_in_check(moving_color)
        self.unmake_move(move, undo_info)
        return legal
    
    def generate_legal_moves(self):
        """Generate all legal moves for the current position."""
        pseudo_legal = self.generate_pseudo_legal_moves()
        return [move for move in pseudo_legal if self.is_legal_move(move)]
    
    def from_fen(self, fen):
        """Load a position from FEN notation."""
        parts = fen.split()
        
        # Parse board position
        rows = parts[0].split('/')
        for row_idx, row in enumerate(rows):
            col_idx = 0
            for char in row:
                if char.isdigit():
                    col_idx += int(char)
                else:
                    piece_map = {
                        'P': WHITE | PAWN, 'N': WHITE | KNIGHT, 
                        'B': WHITE | BISHOP, 'R': WHITE | ROOK,
                        'Q': WHITE | QUEEN, 'K': WHITE | KING,
                        'p': BLACK | PAWN, 'n': BLACK | KNIGHT,
                        'b': BLACK | BISHOP, 'r': BLACK | ROOK,
                        'q': BLACK | QUEEN, 'k': BLACK | KING
                    }
                    self.board[7 - row_idx][col_idx] = piece_map[char]
                    col_idx += 1
        
        # Parse side to move
        self.to_move = WHITE if parts[1] == 'w' else BLACK
        
        # Parse castling rights
        castling = parts[2]
        self.castling_rights = {
            'K': 'K' in castling,
            'Q': 'Q' in castling,
            'k': 'k' in castling,
            'q': 'q' in castling
        }
        
        # Parse en passant
        if parts[3] != '-':
            file = ord(parts[3][0]) - ord('a')
            rank = int(parts[3][1]) - 1
            self.en_passant_square = (rank, file)
        else:
            self.en_passant_square = None
        
        # Parse move counters
        self.halfmove_clock = int(parts[4])
        self.fullmove_number = int(parts[5])
    
    def to_fen(self):
        """Convert the current position to FEN notation."""
        fen_parts = []
        
        # Board position
        for row in range(7, -1, -1):
            empty_count = 0
            row_str = ""
            
            for col in range(8):
                piece = self.board[row][col]
                
                if piece == EMPTY:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0
                    
                    piece_type = piece & 7
                    color = piece & 24
                    
                    piece_chars = {
                        PAWN: 'p', KNIGHT: 'n', BISHOP: 'b',
                        ROOK: 'r', QUEEN: 'q', KING: 'k'
                    }
                    char = piece_chars[piece_type]
                    if color == WHITE:
                        char = char.upper()
                    row_str += char
            
            if empty_count > 0:
                row_str += str(empty_count)
            
            fen_parts.append(row_str)
        
        fen = '/'.join(fen_parts)
        
        # Side to move
        fen += ' w' if self.to_move == WHITE else ' b'
        
        # Castling rights
        castling = ''
        if self.castling_rights['K']:
            castling += 'K'
        if self.castling_rights['Q']:
            castling += 'Q'
        if self.castling_rights['k']:
            castling += 'k'
        if self.castling_rights['q']:
            castling += 'q'
        fen += ' ' + (castling if castling else '-')
        
        # En passant
        if self.en_passant_square:
            files = 'abcdefgh'
            fen += f" {files[self.en_passant_square[1]]}{self.en_passant_square[0] + 1}"
        else:
            fen += ' -'
        
        # Move counters
        fen += f" {self.halfmove_clock} {self.fullmove_number}"
        
        return fen
    
    def __str__(self):
        """Display the board in a human-readable format."""
        piece_symbols = {
            EMPTY: '.',
            WHITE | PAWN: 'P', WHITE | KNIGHT: 'N', WHITE | BISHOP: 'B',
            WHITE | ROOK: 'R', WHITE | QUEEN: 'Q', WHITE | KING: 'K',
            BLACK | PAWN: 'p', BLACK | KNIGHT: 'n', BLACK | BISHOP: 'b',
            BLACK | ROOK: 'r', BLACK | QUEEN: 'q', BLACK | KING: 'k'
        }
        
        board_string = "\n  a b c d e f g h\n"
        board_string += "  ---------------\n"
        for row in range(7, -1, -1):
            board_string += f"{row + 1}|"
            for col in range(8):
                piece = self.board[row][col]
                board_string += piece_symbols.get(piece, '?') + " "
            board_string += f"|{row + 1}\n"
        board_string += "  ---------------\n"
        board_string += "  a b c d e f g h\n"

        return board_string
    
if __name__ == '__main__':
    print("=== PyMinMaximus: Part 1 Demo ===\n")
    
    # Test 1: Initial position
    print("Test 1: Starting Position")
    board = Board()
    print(board)
    
    moves = board.generate_legal_moves()
    print(f"Legal moves available: {len(moves)}")
    print(f"First 5 moves: {moves[:5]}\n")
    
    # Test 2: Make some moves
    print("Test 2: Playing 1.e4 e5 2.Nf3")
    board.make_move(Move(1, 4, 3, 4))  # e4
    board.make_move(Move(6, 4, 4, 4))  # e5
    board.make_move(Move(0, 6, 2, 5))  # Nf3
    print(board)
    
    # Test 3: FEN notation
    print("Test 3: Loading position from FEN")
    board2 = Board()
    # Famous position: "The Immortal Game" after 10.e5
    fen = "r1bqkb1r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5"
    board2.from_fen(fen)
    print(board2)
    print(f"FEN: {board2.to_fen()}")
    print(f"Legal moves: {len(board2.generate_legal_moves())}\n")
    
    # Test 4: Check detection
    print("Test 4: Check Detection")
    board3 = Board()
    # Scholar's mate position
    board3.from_fen("r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4")
    print(board3)
    print(f"Black in check: {board3.is_in_check(BLACK)}")
    print(f"Legal moves for black: {len(board3.generate_legal_moves())}\n")
    
    # Test 5: Perft verification
    print("Test 5: Perft Verification")
    print("Running perft tests from starting position...")
    board4 = Board()
    
    expected_results = {
        1: 20,
        2: 400,
        3: 8902,
        4: 197281
    }
    
    for depth in range(1, 5):
        nodes = perft(board4, depth)
        expected = expected_results[depth]
        status = "✓ PASS" if nodes == expected else "✗ FAIL"
        print(f"Depth {depth}: {nodes:,} nodes (expected {expected:,}) {status}")
    
    # Test 6: Special moves
    print("\nTest 6: Special Moves")
    
    # En passant
    print("En Passant:")
    board5 = Board()
    board5.from_fen("rnbqkbnr/ppp1p1pp/8/3pPp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 3")
    print(board5)
    moves = board5.generate_legal_moves()
    en_passant_moves = [m for m in moves if m.is_en_passant]
    print(f"En passant captures available: {en_passant_moves}\n")
    
    # Castling
    print("Castling:")
    board6 = Board()
    board6.from_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    print(board6)
    moves = board6.generate_legal_moves()
    castling_moves = [m for m in moves if m.is_castling]
    print(f"Castling moves available: {len(castling_moves)}")
    for move in castling_moves:
        side = "Kingside" if move.to_col == 6 else "Queenside"
        color = "White" if move.from_row == 0 else "Black"
        print(f"  - {color} {side}: {move}")
    
    # Promotion
    print("\nPromotion:")
    board7 = Board()
    board7.from_fen("8/P7/8/8/8/8/8/4K2k w - - 0 1")
    print(board7)
    moves = board7.generate_legal_moves()
    promotion_moves = [m for m in moves if m.promotion]
    print(f"Promotion moves available: {len(promotion_moves)}")
    
    print("\n=== All tests complete! ===")
    print("\nYour chess board is working correctly!")
