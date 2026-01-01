from constants import *

# Pawn table - encourage center control and advancement
pawn_table = [
    [  0,   0,   0,   0,   0,   0,   0,   0],  # Rank 1
    [ 50,  50,  50,  50,  50,  50,  50,  50],  # Rank 2
    [ 10,  10,  20,  30,  30,  20,  10,  10],  # Rank 3
    [  5,   5,  10,  25,  25,  10,   5,   5],  # Rank 4
    [  0,   0,   0,  20,  20,   0,   0,   0],  # Rank 5
    [  5,  -5, -10,   0,   0, -10,  -5,   5],  # Rank 6
    [  5,  10,  10, -20, -20,  10,  10,   5],  # Rank 7
    [  0,   0,   0,   0,   0,   0,   0,   0]   # Rank 8
]
        
# Knight table - encourage center control
knight_table = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20,   0,   0,   0,   0, -20, -40],
    [-30,   0,  10,  15,  15,  10,   0, -30],
    [-30,   5,  15,  20,  20,  15,   5, -30],
    [-30,   0,  15,  20,  20,  15,   0, -30],
    [-30,   5,  10,  15,  15,  10,   5, -30],
    [-40, -20,   0,   5,   5,   0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50]
]
        
# Bishop table - encourage long diagonals
bishop_table = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10,   0,   0,   0,   0,   0,   0, -10],
    [-10,   0,   5,  10,  10,   5,   0, -10],
    [-10,   5,   5,  10,  10,   5,   5, -10],
    [-10,   0,  10,  10,  10,  10,   0, -10],
    [-10,  10,  10,  10,  10,  10,  10, -10],
    [-10,   5,   0,   0,   0,   0,   5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20]
]
        
# Rook table - encourage open files and 7th rank
rook_table = [
    [  0,   0,   0,   0,   0,   0,   0,   0],
    [  5,  10,  10,  10,  10,  10,  10,   5],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [  0,   0,   0,   5,   5,   0,   0,   0]
]
        
# Queen table - slight center preference, stay back early
queen_table = [
    [-20, -10, -10,  -5,  -5, -10, -10, -20],
    [-10,   0,   0,   0,   0,   0,   0, -10],
    [-10,   0,   5,   5,   5,   5,   0, -10],
    [ -5,   0,   5,   5,   5,   5,   0,  -5],
    [  0,   0,   5,   5,   5,   5,   0,  -5],
    [-10,   5,   5,   5,   5,   5,   0, -10],
    [-10,   0,   5,   0,   0,   0,   0, -10],
    [-20, -10, -10,  -5,  -5, -10, -10, -20]
]
        
# King middlegame table - encourage castling and safety
king_middlegame_table = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [ 20,  20,   0,   0,   0,   0,  20,  20],
    [ 20,  30,  10,   0,   0,  10,  30,  20]
]
        
# King endgame table - encourage centralization
king_endgame_table = [
    [-50, -40, -30, -20, -20, -30, -40, -50],
    [-30, -20, -10,   0,   0, -10, -20, -30],
    [-30, -10,  20,  30,  30,  20, -10, -30],
    [-30, -10,  30,  40,  40,  30, -10, -30],
    [-30, -10,  30,  40,  40,  30, -10, -30],
    [-30, -10,  20,  30,  30,  20, -10, -30],
    [-30, -30,   0,   0,   0,   0, -30, -30],
    [-50, -30, -30, -30, -30, -30, -30, -50]
]

def get_piece_value(piece_type):
    """Return the base material value of a piece type."""
    if piece_type == PAWN:
        return 100
    elif piece_type == KNIGHT:
        return 320
    elif piece_type == BISHOP:
        return 330
    elif piece_type == ROOK:
        return 500
    elif piece_type == QUEEN:
        return 900
    elif piece_type == KING:
        return 20000
    return 0


def get_piece_square_value(piece_type, row, col, is_white, is_endgame):
    """
    Get the piece-square table value for a piece.
    Black's tables are flipped vertically from White's.
    """
    # Flip row for black pieces
    table_row = row if is_white else 7 - row
    
    if piece_type == PAWN:
        return pawn_table[table_row][col]
    elif piece_type == KNIGHT:
        return knight_table[table_row][col]
    elif piece_type == BISHOP:
        return bishop_table[table_row][col]
    elif piece_type == ROOK:
        return rook_table[table_row][col]
    elif piece_type == QUEEN:
        return queen_table[table_row][col]
    elif piece_type == KING:
        if is_endgame:
            return king_endgame_table[table_row][col]
        else:
            return king_middlegame_table[table_row][col]
    
    return 0

def calculate_pst(board,is_endgame=False):
    # Calculate the piece-square table value for the current board state
    total = 0
    for row in range(8):
        for col in range(8):
            piece = board.board[row][col]
            if piece != EMPTY:
                piece_type = piece & 7
                is_white = (piece & 24) == WHITE
                total += get_piece_square_value(piece_type, row, col, is_white, is_endgame)
    return total