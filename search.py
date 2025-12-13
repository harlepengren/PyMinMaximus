from evaluation import Evaluator
from constants import *

class TranspositionTable:
    def __init__(self, size_mb=64):
        # Approximate number of entries based on memory
        self.size = (size_mb * 1024 * 1024) // 100  # rough estimate
        self.table = {}
    
    def get_hash(self, board):
        """
        Simple hash of the board position.
        In a real engine, we'd use Zobrist hashing.
        """
        return board.to_fen()
    
    def store(self, board, depth, score, flag):
        """
        Store a position evaluation.
        flag: 'exact', 'lowerbound', or 'upperbound'
        """
        if len(self.table) >= self.size:
            # Simple replacement: clear oldest entries
            self.table.clear()
        
        hash_key = self.get_hash(board)
        self.table[hash_key] = {
            'depth': depth,
            'score': score,
            'flag': flag
        }
    
    def probe(self, board, depth, alpha, beta):
        """
        Check if we've seen this position before.
        Returns (found, score) tuple.
        """
        hash_key = self.get_hash(board)
        
        if hash_key not in self.table:
            return False, 0
        
        entry = self.table[hash_key]
        
        # Only use if searched to equal or greater depth
        if entry['depth'] < depth:
            return False, 0
        
        score = entry['score']
        flag = entry['flag']
        
        if flag == 'exact':
            return True, score
        elif flag == 'lowerbound':
            if score >= beta:
                return True, score
        elif flag == 'upperbound':
            if score <= alpha:
                return True, score
        
        return False, 0

class SearchEngine:
    def __init__(self, board, evaluator=None):
        self.board = board
        self.evaluator = evaluator if evaluator else Evaluator()
        self.nodes_searched = 0
        self.tt = TranspositionTable()
    
    def minimax(self, depth, maximizing_player):
        """
        Basic minimax search algorithm.
        Returns the evaluation score for the current position.
        """
        self.nodes_searched += 1
        
        # Base case: reached maximum depth or game over
        if depth == 0:
            return self.evaluator.evaluate_relative(self.board)
        
        moves = self.board.generate_legal_moves()
        
        # Checkmate or stalemate
        if len(moves) == 0:
            if self.board.is_in_check(self.board.to_move):
                # Checkmate - return a score that's worse the sooner it happens
                return -20000 + (10 - depth)  # Prefer longer defense
            else:
                # Stalemate
                return 0
        
        if maximizing_player:
            max_eval = float('-inf')
            for move in moves:
                undo_info = self.board.make_move(move)
                eval_score = self.minimax(depth - 1, False)
                self.board.unmake_move(move, undo_info)
                max_eval = max(max_eval, eval_score)
            return max_eval
        else:
            min_eval = float('inf')
            for move in moves:
                undo_info = self.board.make_move(move)
                eval_score = self.minimax(depth - 1, True)
                self.board.unmake_move(move, undo_info)
                min_eval = min(min_eval, eval_score)
            return min_eval
    
    def find_best_move(self, depth):
        """
        Find the best move at the root of the search tree.
        """
        self.nodes_searched = 0
        best_move = None
        best_eval = float('-inf')
        
        moves = self.board.generate_legal_moves()
        
        if len(moves) == 0:
            return None
        
        for move in moves:
            undo_info = self.board.make_move(move)
            # We're always maximizing at root (from our perspective)
            eval_score = self.minimax(depth - 1, False)
            self.board.unmake_move(move, undo_info)
            
            if eval_score > best_eval:
                best_eval = eval_score
                best_move = move
        
        return best_move, best_eval
    
    def order_moves(self, moves):
        """
        Order moves to improve alpha-beta pruning.
        Better moves first = more pruning.
        """
        def move_score(move):
            score = 0
            
            # Get the captured piece (if any)
            captured = self.board.board[move.to_row][move.to_col]
            
            if captured != EMPTY:
                # MVV-LVA: Most Valuable Victim - Least Valuable Attacker
                captured_value = self.evaluator.piece_values[captured & 7]
                attacker = self.board.board[move.from_row][move.from_col]
                attacker_value = self.evaluator.piece_values[attacker & 7]
                
                # Prioritize capturing valuable pieces with cheap pieces
                score += captured_value * 10 - attacker_value
            
            # Prioritize promotions
            if move.promotion:
                score += 800
            
            # Prioritize checks (we'll need to make the move to check this)
            # For now, we'll skip this to keep it simple
            
            return score
        
        return sorted(moves, key=move_score, reverse=True)
    
    def alphabeta(self, depth, alpha, beta, maximizing_player):
        """
        Alpha-beta with transposition table.
        """
        alpha_orig = alpha
        
        # Check transposition table
        tt_hit, tt_score = self.tt.probe(self.board, depth, alpha, beta)
        if tt_hit:
            return tt_score
        
        self.nodes_searched += 1
        
        if depth == 0:
            score = self.evaluator.evaluate_relative(self.board)
            return score
        
        moves = self.board.generate_legal_moves()
        
        if len(moves) == 0:
            if self.board.is_in_check(self.board.to_move):
                return -20000 + (10 - depth)
            else:
                return 0
        
        moves = self.order_moves(moves)
        
        if maximizing_player:
            max_eval = float('-inf')
            for move in moves:
                undo_info = self.board.make_move(move)
                eval_score = self.alphabeta(depth - 1, alpha, beta, False)
                self.board.unmake_move(move, undo_info)
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break
            
            # Store in transposition table
            if max_eval <= alpha_orig:
                flag = 'upperbound'
            elif max_eval >= beta:
                flag = 'lowerbound'
            else:
                flag = 'exact'
            self.tt.store(self.board, depth, max_eval, flag)
            
            return max_eval
        else:
            min_eval = float('inf')
            for move in moves:
                undo_info = self.board.make_move(move)
                eval_score = self.alphabeta(depth - 1, alpha, beta, True)
                self.board.unmake_move(move, undo_info)
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break
            
            # Store in transposition table
            if min_eval <= alpha_orig:
                flag = 'upperbound'
            elif min_eval >= beta:
                flag = 'lowerbound'
            else:
                flag = 'exact'
            self.tt.store(self.board, depth, min_eval, flag)
            
            return min_eval
    
    def find_best_move_alphabeta(self, depth):
        """
        Find the best move using alpha-beta pruning.
        """
        self.nodes_searched = 0
        best_move = None
        best_eval = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        moves = self.board.generate_legal_moves()
        
        if len(moves) == 0:
            return None, 0
        
        for move in moves:
            undo_info = self.board.make_move(move)
            eval_score = self.alphabeta(depth - 1, alpha, beta, False)
            self.board.unmake_move(move, undo_info)
            
            if eval_score > best_eval:
                best_eval = eval_score
                best_move = move
            
            alpha = max(alpha, eval_score)
        
        return best_move, best_eval