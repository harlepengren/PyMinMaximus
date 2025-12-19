# zobrist.py

import random
from constants import *

class ZobristHash:
    """
    Zobrist hashing for chess positions.
    Creates unique 64-bit fingerprints for positions.
    """
    
    def __init__(self, seed=42):
        """
        Initialize random number tables for Zobrist hashing.
        
        We need random numbers for:
        - Each piece type on each square
        - Castling rights
        - En passant files
        - Side to move
        """
        random.seed(seed)
        
        # Random numbers for each piece on each square
        # [piece_type][color][square]
        self.piece_keys = [
            [[self._rand64() for _ in range(64)] for _ in range(2)] 
            for _ in range(7)  # EMPTY, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING
        ]
        
        # Random numbers for castling rights
        self.castle_keys = [self._rand64() for _ in range(4)]  # K, Q, k, q
        
        # Random numbers for en passant files (8 files)
        self.ep_keys = [self._rand64() for _ in range(8)]
        
        # Random number for side to move (black)
        self.side_key = self._rand64()
    
    def _rand64(self):
        """Generate a random 64-bit number."""
        return random.randint(0, (1 << 64) - 1)
    
    def hash_position(self, board):
        """
        Compute Zobrist hash for a position.
        
        Returns:
            64-bit integer representing the position
        """
        hash_value = 0
        
        # Hash all pieces on the board
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                
                if piece != EMPTY:
                    piece_type = piece & 7
                    color = 1 if (piece & 24) == BLACK else 0
                    square = row * 8 + col
                    
                    hash_value ^= self.piece_keys[piece_type][color][square]
        
        # Hash castling rights
        if board.castling_rights['K']:
            hash_value ^= self.castle_keys[0]
        if board.castling_rights['Q']:
            hash_value ^= self.castle_keys[1]
        if board.castling_rights['k']:
            hash_value ^= self.castle_keys[2]
        if board.castling_rights['q']:
            hash_value ^= self.castle_keys[3]
        
        # Hash en passant square (only the file matters)
        if board.en_passant_square:
            file = board.en_passant_square[1]
            hash_value ^= self.ep_keys[file]
        
        # Hash side to move (only if Black to move)
        if board.to_move == BLACK:
            hash_value ^= self.side_key
        
        return hash_value
