from evaluation import Evaluator

class SearchEngine:
    def __init__(self, board, evaluator=None):
        self.board = board
        self.evaluator = evaluator if evaluator else Evaluator()
        self.nodes_searched = 0
    
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
    
    def alphabeta(self, depth, alpha, beta, maximizing_player):
        """
        Minimax with alpha-beta pruning.
        Alpha: best value for maximizer found so far
        Beta: best value for minimizer found so far
        """
        self.nodes_searched += 1
        
        if depth == 0:
            return self.evaluator.evaluate_relative(self.board)
        
        moves = self.board.generate_legal_moves()
        
        if len(moves) == 0:
            if self.board.is_in_check(self.board.to_move):
                return -20000 + (10 - depth)
            else:
                return 0
        
        if maximizing_player:
            max_eval = float('-inf')
            for move in moves:
                undo_info = self.board.make_move(move)
                eval_score = self.alphabeta(depth - 1, alpha, beta, False)
                self.board.unmake_move(move, undo_info)
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                # Beta cutoff
                if beta <= alpha:
                    break  # Prune remaining moves
            
            return max_eval
        else:
            min_eval = float('inf')
            for move in moves:
                undo_info = self.board.make_move(move)
                eval_score = self.alphabeta(depth - 1, alpha, beta, True)
                self.board.unmake_move(move, undo_info)
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                # Alpha cutoff
                if beta <= alpha:
                    break  # Prune remaining moves
            
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