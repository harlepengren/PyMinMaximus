#!/usr/bin/env python3

import sys
import random
from board import Board
from constants import *

class RandomEngine:
    """Simple engine that plays random legal moves."""
    
    def __init__(self):
        self.board = Board()
        self.name = "RandomMover"
        self.author = "Harlepengren"
    
    def uci(self):
        print(f"id name {self.name}")
        print(f"id author {self.author}")
        print("uciok")
        sys.stdout.flush()
    
    def isready(self):
        print("readyok")
        sys.stdout.flush()
    
    def ucinewgame(self):
        self.board = Board()
    
    def position(self, args):
        if args[0] == 'startpos':
            self.board = Board()
            move_start = 1
        elif args[0] == 'fen':
            try:
                moves_idx = args.index('moves')
                fen = ' '.join(args[1:moves_idx])
                move_start = moves_idx
            except ValueError:
                fen = ' '.join(args[1:])
                move_start = len(args)
            
            self.board = Board()
            self.board.from_fen(fen)
        
        if move_start < len(args) and args[move_start] == 'moves':
            for move_str in args[move_start + 1:]:
                move = self._parse_move(move_str)
                if move:
                    self.board.make_move(move)
    
    def go(self, args):
        # Just pick a random legal move
        legal_moves = self.board.generate_legal_moves()
        
        if legal_moves:
            move = random.choice(legal_moves)
            print(f"bestmove {move}")
        else:
            print("bestmove 0000")
        
        sys.stdout.flush()
    
    def _parse_move(self, move_str):
        from move import Move
        
        from_col = ord(move_str[0]) - ord('a')
        from_row = int(move_str[1]) - 1
        to_col = ord(move_str[2]) - ord('a')
        to_row = int(move_str[3]) - 1
        
        promotion = None
        if len(move_str) == 5:
            promo_map = {'q': QUEEN, 'r': ROOK, 'b': BISHOP, 'n': KNIGHT}
            promotion = promo_map.get(move_str[4].lower())
        
        legal_moves = self.board.generate_legal_moves()
        for move in legal_moves:
            if (move.from_row == from_row and move.from_col == from_col and
                move.to_row == to_row and move.to_col == to_col):
                if promotion is None or move.promotion == promotion:
                    return move
        
        return None
    
    def run(self):
        while True:
            try:
                line = input().strip()
                if not line:
                    continue
                
                parts = line.split()
                command = parts[0]
                args = parts[1:]
                
                if command == 'uci':
                    self.uci()
                elif command == 'isready':
                    self.isready()
                elif command == 'ucinewgame':
                    self.ucinewgame()
                elif command == 'position':
                    self.position(args)
                elif command == 'go':
                    self.go(args)
                elif command == 'quit':
                    break
                
            except EOFError:
                break


if __name__ == "__main__":
    engine = RandomEngine()
    engine.run()
