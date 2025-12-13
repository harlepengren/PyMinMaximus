from constants import *

class Evaluator:
    def __init__(self):
        self.piece_values = {
            PAWN: 100,
            KNIGHT: 320,
            BISHOP: 330,
            ROOK: 500,
            QUEEN: 900,
            KING: 20000
        }
    
    def evaluate(self, board):
        """
        Evaluate the position from White's perspective.
        Positive = good for White, Negative = good for Black
        """
        score = 0
        
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                
                if piece == EMPTY:
                    continue
                
                piece_type = piece & 7
                color = piece & 24
                
                value = self.piece_values[piece_type]
                
                if color == WHITE:
                    score += value
                else:
                    score -= value
        
        return score
    
    def evaluate_relative(self, board):
        """
        Evaluate from the perspective of the side to move.
        Positive = good for side to move
        """
        score = self.evaluate(board)
        return score if board.to_move == WHITE else -score