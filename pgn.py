import re
from board import Board
from move import Move
from constants import *

class PGNGame:
    """Represents a single chess game from a PGN file."""
    
    def __init__(self):
        self.headers = {}
        self.moves = []  # List of move strings in SAN format
        self.uci_moves = []  # List of moves in UCI format
        self.result = "*"
    
    def __str__(self):
        """String representation of the game."""
        header_str = "\n".join([f"[{key} \"{value}\"]" for key, value in self.headers.items()])
        moves_str = " ".join(self.moves)
        return f"{header_str}\n\n{moves_str} {self.result}"


class PGNParser:
    """Parser for PGN files."""
    
    def __init__(self):
        self.games = []
    
    def parse_file(self, filename):
        """Parse a PGN file and extract all games."""
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_string(content)
    
    def parse_string(self, pgn_string):
        """Parse PGN content from a string."""
        self.games = []
        
        # Split into individual games
        # Games are separated by blank lines after the movetext
        game_texts = self._split_games(pgn_string)
        
        for game_text in game_texts:
            if game_text.strip():
                game = self._parse_game(game_text)
                if game:
                    self.games.append(game)
        
        return self.games
    
    def _split_games(self, content):
        """Split PGN content into individual games."""
        games = []
        current_game = []
        in_headers = False
        
        lines = content.split('\n')
        
        for line in lines:
            stripped = line.strip()
            
            # Check if this is a header line
            if stripped.startswith('['):
                if current_game and not in_headers:
                    # We've hit a new game
                    games.append('\n'.join(current_game))
                    current_game = []
                in_headers = True
                current_game.append(line)
            elif stripped:
                in_headers = False
                current_game.append(line)
            elif current_game:
                # Blank line - could be end of game or just spacing
                current_game.append(line)
        
        # Don't forget the last game
        if current_game:
            games.append('\n'.join(current_game))
        
        return games
    
    def _parse_game(self, game_text):
        """Parse a single game from text."""
        game = PGNGame()
        
        lines = game_text.split('\n')
        movetext_lines = []
        
        # Parse headers
        for line in lines:
            line = line.strip()
            if line.startswith('['):
                # Parse header
                match = re.match(r'\[(\w+)\s+"(.*)"\]', line)
                if match:
                    key, value = match.groups()
                    game.headers[key] = value
            elif line:
                # This is part of the movetext
                movetext_lines.append(line)
        
        # Parse movetext
        movetext = ' '.join(movetext_lines)
        game.moves, game.result = self._parse_movetext(movetext)
        
        # Convert to UCI
        game.uci_moves = self._convert_to_uci(game)
        
        return game
    
    def _parse_movetext(self, movetext):
        """Parse the movetext section and extract moves."""
        moves = []
        
        # Remove comments in braces
        movetext = re.sub(r'\{[^}]*\}', '', movetext)
        
        # Remove comments in semicolons
        movetext = re.sub(r';[^\n]*', '', movetext)
        
        # Remove variations (recursive parentheses is complex, so we'll do simple)
        while '(' in movetext:
            movetext = re.sub(r'\([^()]*\)', '', movetext)
        
        # Extract result
        result_match = re.search(r'(1-0|0-1|1/2-1/2|\*)\s*$', movetext)
        result = result_match.group(1) if result_match else "*"
        
        # Remove result from movetext
        movetext = re.sub(r'(1-0|0-1|1/2-1/2|\*)\s*$', '', movetext)
        
        # Remove move numbers (e.g., "1.", "23...")
        movetext = re.sub(r'\d+\.+', '', movetext)
        
        # Remove NAGs (Numeric Annotation Glyphs like $1, $2, etc.)
        movetext = re.sub(r'\$\d+', '', movetext)
        
        # Remove annotation symbols (!, ?, !!, ??, !?, ?!)
        movetext = re.sub(r'[!?]+', '', movetext)
        
        # Split into individual moves
        tokens = movetext.split()
        
        for token in tokens:
            token = token.strip()
            if token and not token.startswith('(') and not token.endswith(')'):
                moves.append(token)
        
        return moves, result
    
    def _convert_to_uci(self, game):
        """Convert SAN moves to UCI format."""
        board = Board()
        
        # Set up initial position if FEN is provided
        if 'FEN' in game.headers:
            board.from_fen(game.headers['FEN'])
        
        uci_moves = []
        
        for san_move in game.moves:
            try:
                uci_move = self._san_to_uci(board, san_move)
                if uci_move:
                    uci_moves.append(uci_move)
                    
                    # Make the move on the board
                    move = self._uci_to_move(board, uci_move)
                    if move:
                        board.make_move(move)
                else:
                    print(f"Warning: Could not convert move '{san_move}'")
                    break
            except Exception as e:
                print(f"Error converting move '{san_move}': {e}")
                break
        
        return uci_moves
    
    def _san_to_uci(self, board, san):
        """Convert a single SAN move to UCI format."""
        # Generate all legal moves
        legal_moves = board.generate_legal_moves()
        
        # Store original for debugging
        original_san = san
        
        # Clean up the SAN notation
        san = san.replace('+', '').replace('#', '')
        
        # Handle castling
        if san in ['O-O', 'O-O-O']:
            for move in legal_moves:
                if move.is_castling:
                    if san == 'O-O' and move.to_col == 6:
                        return self._move_to_uci(move)
                    elif san == 'O-O-O' and move.to_col == 2:
                        return self._move_to_uci(move)
        
        # Parse the SAN move
        piece_type = None
        from_file = None
        from_rank = None
        to_square = None
        promotion = None
        is_capture = 'x' in san
        
        # Remove capture indicator for parsing
        san = san.replace('x', '')
        
        # Check for promotion
        if '=' in san:
            san, promo_char = san.split('=')
            promotion_map = {'Q': QUEEN, 'R': ROOK, 'B': BISHOP, 'N': KNIGHT}
            promotion = promotion_map.get(promo_char.upper())
        
        # Determine piece type
        if san[0].isupper():
            piece_map = {'K': KING, 'Q': QUEEN, 'R': ROOK, 'B': BISHOP, 'N': KNIGHT}
            piece_type = piece_map.get(san[0])
            san = san[1:]  # Remove piece character
        else:
            piece_type = PAWN
        
        # Extract destination square (last 2 characters)
        if len(san) >= 2:
            to_square = san[-2:]
            san = san[:-2]
        else:
            return None
        
        # Extract disambiguation info (file and/or rank)
        if san:
            for char in san:
                if char.isalpha():
                    from_file = ord(char) - ord('a')
                elif char.isdigit():
                    from_rank = int(char) - 1
        
        # Convert destination square to row/col
        if len(to_square) != 2 or not to_square[0].isalpha() or not to_square[1].isdigit():
            return None
            
        to_col = ord(to_square[0]) - ord('a')
        to_row = int(to_square[1]) - 1
        
        # Validate coordinates
        if not (0 <= to_col < 8 and 0 <= to_row < 8):
            return None
        
        # Find matching legal move
        candidates = []
        for move in legal_moves:
            # Check if destination matches
            if move.to_row != to_row or move.to_col != to_col:
                continue
            
            # Check piece type
            piece = board.board[move.from_row][move.from_col]
            if (piece & 7) != piece_type:
                continue
            
            # Check disambiguation
            if from_file is not None and move.from_col != from_file:
                continue
            if from_rank is not None and move.from_row != from_rank:
                continue
            
            # Check promotion
            if promotion is not None:
                if move.promotion != promotion:
                    continue
            elif move.promotion is not None:
                # SAN doesn't have promotion but move does
                continue
            
            candidates.append(move)
        
        # If we have exactly one candidate, use it
        if len(candidates) == 1:
            return self._move_to_uci(candidates[0])
        elif len(candidates) > 1:
            # Multiple candidates - shouldn't happen with proper disambiguation
            # Try to pick the most likely one (capture if it's a capture move)
            if is_capture:
                for move in candidates:
                    target = board.board[move.to_row][move.to_col]
                    if target != EMPTY:
                        return self._move_to_uci(move)
            return self._move_to_uci(candidates[0])
        
        return None
    
    def _move_to_uci(self, move):
        """Convert a Move object to UCI notation."""
        files = 'abcdefgh'
        
        from_square = files[move.from_col] + str(move.from_row + 1)
        to_square = files[move.to_col] + str(move.to_row + 1)
        
        uci = from_square + to_square
        
        if move.promotion:
            promo_chars = {QUEEN: 'q', ROOK: 'r', BISHOP: 'b', KNIGHT: 'n'}
            uci += promo_chars.get(move.promotion, 'q')
        
        return uci
    
    def _uci_to_move(self, board, uci):
        """Convert UCI notation to a Move object."""
        files = 'abcdefgh'
        
        from_col = files.index(uci[0])
        from_row = int(uci[1]) - 1
        to_col = files.index(uci[2])
        to_row = int(uci[3]) - 1
        
        promotion = None
        if len(uci) > 4:
            promo_map = {'q': QUEEN, 'r': ROOK, 'b': BISHOP, 'n': KNIGHT}
            promotion = promo_map.get(uci[4].lower())
        
        # Check if it's castling
        piece = board.board[from_row][from_col]
        is_castling = ((piece & 7) == KING) and abs(to_col - from_col) == 2
        
        # Check if it's en passant
        is_en_passant = False
        if (piece & 7) == PAWN:
            if board.en_passant_square and (to_row, to_col) == board.en_passant_square:
                is_en_passant = True
        
        return Move(from_row, from_col, to_row, to_col, 
                   promotion=promotion, 
                   is_castling=is_castling,
                   is_en_passant=is_en_passant)


def pgn_to_uci(pgn_filename, output_filename=None):
    """
    Convert a PGN file to UCI format.
    
    Args:
        pgn_filename: Path to the input PGN file
        output_filename: Path to the output file (optional)
    
    Returns:
        List of games with UCI moves
    """
    parser = PGNParser()
    games = parser.parse_file(pgn_filename)
    
    if output_filename:
        with open(output_filename, 'w', encoding='utf-8') as f:
            for i, game in enumerate(games):
                # Write game headers as comments
                f.write(f"# Game {i + 1}\n")
                for key, value in game.headers.items():
                    f.write(f"# {key}: {value}\n")
                
                # Write UCI moves
                f.write(' '.join(game.uci_moves))
                f.write(f" # Result: {game.result}\n\n")
    
    return games