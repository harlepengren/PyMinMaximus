from evaluation import Evaluator
from constants import *
import time
from krk_tablebase import KRKTablebase
from opening_book import OpeningBook
import os

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
    def __init__(self, board, evaluator=None, book=None):
        self.board = board
        self.stop = False
        self.evaluator = evaluator if evaluator else Evaluator()
        self.nodes_searched = 0
        self.tt = TranspositionTable()

        # Opening book
        self.book = book if book else OpeningBook('books/kasparov.bin')

        # Add tablebase
        self.krk_tablebase = None
        self.load_tablebases()

    def load_tablebases(self):
        """Load endgame tablebases"""
        try:
            self.krk_tablebase = KRKTablebase()
            table_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tablebase/krk_tablebase.pkl')
            self.krk_tablebase.load(table_path)
            print("KRK tablebase loaded successfully")
        except:
            # Generate if not found
            print("Generating KRK tablebase...")
            self.krk_tablebase = KRKTablebase()
            self.krk_tablebase.generate()
            self.krk_tablebase.save(table_path)

    def is_tablebase_position(self, board):
        """Check if position is in a tablebase"""
        # Count pieces and material
        piece_count = 0
        white_pieces = []
        black_pieces = []
        
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece != EMPTY:
                    piece_count += 1
                    if (piece & 24) == WHITE:
                        white_pieces.append(piece & 7)
                    else:
                        black_pieces.append(piece & 7)
        
        # Check for KRK
        if piece_count == 3:
            white_pieces.sort()
            black_pieces.sort()
            
            # White has K+R, Black has K
            if white_pieces == [KING, ROOK] and black_pieces == [KING]:
                return 'KRK_white'
            
            # Black has K+R, White has K (flip the board mentally)
            if white_pieces == [KING] and black_pieces == [KING, ROOK]:
                return 'KRK_black'
        
        return None
    
    def probe_tablebase(self, board):
        """
        Probe endgame tablebases.
        Returns (score, best_move) or None if not in tablebase.
        """
        tb_type = self.is_tablebase_position(board)
        
        if tb_type is None:
            return None
        
        if tb_type == 'KRK_white':
            # Query KRK tablebase
            result = self.krk_tablebase.probe_from_board(board)
            if result is None:
                return None
            
            outcome, dtm = result
            
            if outcome == self.krk_tablebase.WHITE_WIN:
                # Convert DTM to score
                # Use high score that decreases with distance
                score = 19000 - dtm
            else:  # DRAW
                score = 0
            
            # Find the best move that maintains this outcome
            best_move = self.find_tablebase_best_move(board, outcome, dtm)
            return (score, best_move)
        
        elif tb_type == 'KRK_black':
            # Flip perspective for black
            result = self.krk_tablebase.probe_from_board(board)
            if result is None:
                return None
            
            outcome, dtm = result
            
            if outcome == self.krk_tablebase.WHITE_WIN:
                # Black is losing
                score = -(19000 - dtm)
            else:
                score = 0
            
            best_move = self.find_tablebase_best_move(board, outcome, dtm)
            return (score, best_move)
        
        return None

    def find_tablebase_best_move(self, board, target_outcome, current_dtm):
        """
        Find the best move according to the tablebase.
        Looks for moves that maintain winning path or quickest mate.
        """
        moves = board.generate_legal_moves()
        best_move = None
        best_dtm = float('inf')
        
        for move in moves:
            undo_info = board.make_move(move)
            
            # Query position after move
            result = self.krk_tablebase.probe_from_board(board)
            
            board.unmake_move(move, undo_info)
            
            if result is None:
                continue
            
            outcome, dtm = result
            
            # If we're winning, look for quickest mate
            if outcome == target_outcome:
                if outcome == self.krk_tablebase.WHITE_WIN:
                    # Want smallest DTM (quickest mate)
                    if dtm < best_dtm:
                        best_dtm = dtm
                        best_move = move
                else:  # DRAW
                    best_move = move
                    break  # Any drawing move is fine
        
        return best_move
    
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
        # Check for time cutoff
        if self.stop:
            return 0

        # Check tablebase FIRST (before any search)
        piece_count = sum(1 for row in self.board.board for p in row if p != EMPTY)
        if piece_count <= 5:
            tb_result = self.probe_tablebase(self.board)
            if tb_result is not None:
                score, _ = tb_result
                # Return from current player's perspective
                if not maximizing_player:
                    score = -score
                return score

        alpha_orig = alpha
        
        # Check transposition table
        tt_hit, tt_score = self.tt.probe(self.board, depth, alpha, beta)
        if tt_hit:
            return tt_score
        
        self.nodes_searched += 1
        
        moves = self.board.generate_legal_moves()

        if depth == 0 or len(moves) == 0:
            score = self.evaluator.evaluate(self.board)
            return score
        
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
        time_remaining: time left in milliseconds (optional)
        """
        # Check opening book
        if self.book.is_in_book(self.board):
            moves = self.board.generate_legal_moves()
            book_move = self.book.get_book_move(self.board,len(self.board.move_stack))
            for move in moves:
                if str(move) == book_move:
                    return move, 1000

        # Check tablebase
        piece_count = sum(1 for row in self.board.board for p in row if p != EMPTY)
        if piece_count <= 5:
            tb_result = self.probe_tablebase(self.board)
            if tb_result is not None:
                score, best_move = tb_result
                if best_move is not None:
                    print(f"Tablebase: {best_move} (score: {score})")
                    return best_move, score

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
    
    def iterative_deepening(self, max_depth, time_limit=None):
        """
        Iteratively search to increasing depths.
        """
        
        start_time = time.time()
        best_move = None
        best_score = float('-inf')
        
        for depth in range(1, max_depth + 1):
            # Check time
            if time_limit and (time.time() - start_time) > time_limit:
                break
            
            self.nodes_searched = 0
            move, score = self.find_best_move_alphabeta(depth)
            
            elapsed = time.time() - start_time
            nps = self.nodes_searched / elapsed if elapsed > 0 else 0
            
            print(f"Depth {depth}: {move} (score: {score}) "
                  f"[{self.nodes_searched:,} nodes in {elapsed:.2f}s, "
                  f"{nps:,.0f} nps]")
            
            if move:
                best_move = move
                best_score = score
            
            # Stop if we found a mate
            if abs(score) > 19000:
                break
        print(f"Total Time: {time.time() - start_time}")
        return best_move, best_score