from board import Board
from search import SearchEngine
from evaluation import Evaluator
from move import convert_move

import pandas as pd

class EvaluationTuner:
    """
    Simple tuner for evaluation parameters.
    In a real engine, you'd use automated tuning methods.
    """
    
    def __init__(self, rating=None):
        puzzles = pd.read_csv('puzzles/chess_puzzles_1.csv')

        if rating:
            puzzles = puzzles[puzzles['Rating'] <= rating]

        puzzle_sample = puzzles.sample(n=100, replace=False)

        self.test_positions = []
        for current_sample in puzzle_sample.itertuples():
            moves = current_sample.Moves.split()
            if len(moves) > 1:
                self.test_positions.append({
                    'fen': current_sample.FEN,
                    'next_move': moves[0],
                    'best_move': moves[1],
                    'weight': 1.0
                })
    
    def test_evaluation_weights(self, evaluator, failure_list=False):
        """
        Test how well the evaluation performs on test positions.
        """
        score = 0
        current_test = 0
        failure_fen = []
        
        for position in self.test_positions:
            print(f'Test {current_test} (score {score})...')
            current_test += 1
            board = Board()
            board.from_fen(position['fen'])
            board.make_move(convert_move(position['next_move']))
            
            engine = SearchEngine(board, evaluator)
            best_move, _ = engine.find_best_move_alphabeta(4)
            
            if str(best_move) == position['best_move']:
                score += position['weight']
            else:
                failure_fen.append(position['fen'])
        
        if failure_list:
            return score, failure_fen
        
        return score
        
    
    def tune_parameters(self):
        """
        Simple grid search for parameter tuning.
        """
        best_score = 0
        best_params = None
        
        # Try different values for key parameters
        for doubled_pawn_penalty in [5, 10, 15, 20]:
            for passed_pawn_bonus in [5, 10, 15, 20]:
                evaluator = Evaluator()
                # Modify evaluator parameters here
                
                score = self.test_evaluation_weights(evaluator)
                
                if score > best_score:
                    best_score = score
                    best_params = {
                        'doubled_pawn': doubled_pawn_penalty,
                        'passed_pawn': passed_pawn_bonus
                    }
        
        return best_params, best_score

def test_search(rating=None,theme=None,depth=3,max_puzzles=100):
    puzzles = pd.read_csv('puzzles/chess_puzzles_1.csv')

    if rating:
        puzzles = puzzles[puzzles['Rating'] <= rating]

    if theme:
        puzzles = puzzles[puzzles['Themes'].str.contains(theme)]

    if max_puzzles:
        puzzles = puzzles.sample(n=max_puzzles)

    score = 0
    for index, current_puzzle in puzzles.iterrows():
        moves = current_puzzle['Moves'].split()
        if len(moves) < 2:
            continue

        board = Board()
        board.from_fen(current_puzzle['FEN'])
        board.push_uci(moves[0])

        engine = SearchEngine(board)
        best_move, eval_score = engine.find_best_move_alphabeta(depth)

        if best_move == moves[1]:
            score += 1

        print(best_move, moves[1], eval_score)

    print(f"Final Score: {score} ({score/len(puzzles)})")




    
    

def run_eval(rating=None, failure_list:bool=False):
    evaluator = Evaluator()
    tuner = EvaluationTuner(rating)
    return tuner.test_evaluation_weights(evaluator,failure_list)

if __name__ == "__main__":
    run_eval()