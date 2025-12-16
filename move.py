from constants import *

class Move:
    def __init__(self, from_row, from_col, to_row, to_col, 
                 promotion=None, is_castling=False, is_en_passant=False):
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col
        self.promotion = promotion  # QUEEN, ROOK, BISHOP, or KNIGHT
        self.is_castling = is_castling
        self.is_en_passant = is_en_passant
    
    def __str__(self):
        """Convert move to algebraic notation."""
        files = 'abcdefgh'
        from_square = f"{files[self.from_col]}{self.from_row + 1}"
        to_square = f"{files[self.to_col]}{self.to_row + 1}"
        
        if self.promotion:
            piece_symbols = {QUEEN: 'q', ROOK: 'r', BISHOP: 'b', KNIGHT: 'n'}
            return f"{from_square}{to_square}{piece_symbols[self.promotion]}"
        
        return f"{from_square}{to_square}"
    
    def __repr__(self):
        return self.__str__()
    
def convert_move(move_str:str)->Move:
    """Convert move from alebraic notation to Move."""
    if len(move_str) < 4:
        print("Invalid format. Use: e2e4")
        return
    try:
        from_col = ord(move_str[0]) - ord('a')
        from_row = int(move_str[1]) - 1
        to_col = ord(move_str[2]) - ord('a')
        to_row = int(move_str[3]) - 1
        
        # Check for promotion
        promotion = None
        if len(move_str) == 5:
            promo_map = {'q': QUEEN, 'r': ROOK, 'b': BISHOP, 'n': KNIGHT}
            promotion = promo_map.get(move_str[4])
        
        return Move(from_row,from_col,to_row,to_col,promotion)
    except:
        print("Invalid move format. Use: e2e4")