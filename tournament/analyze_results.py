import chess.pgn

def analyze_tournament(pgn_file):
    """Analyze tournament results from PGN file."""
    print("="*60)
    print("Tournament Results Analysis")
    print("="*60)
    
    results = {'PyMinMaximus': {'wins': 0, 'losses': 0, 'draws': 0},
               'opponent': {'wins': 0, 'losses': 0, 'draws': 0}}
    
    total_games = 0
    pymm_white_games = 0
    pymm_white_wins = 0
    
    with open(pgn_file) as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break
            
            total_games += 1
            
            white = game.headers.get("White", "")
            black = game.headers.get("Black", "")
            result = game.headers.get("Result", "*")
            
            is_pymm_white = "PyMinMaximus" in white
            
            if is_pymm_white:
                pymm_white_games += 1
            
            # Count results
            if result == "1-0":
                if is_pymm_white:
                    results['PyMinMaximus']['wins'] += 1
                    results['opponent']['losses'] += 1
                    pymm_white_wins += 1
                else:
                    results['PyMinMaximus']['losses'] += 1
                    results['opponent']['wins'] += 1
            
            elif result == "0-1":
                if is_pymm_white:
                    results['PyMinMaximus']['losses'] += 1
                    results['opponent']['wins'] += 1
                else:
                    results['PyMinMaximus']['wins'] += 1
                    results['opponent']['losses'] += 1
                    pymm_white_wins += 1
            
            elif result == "1/2-1/2":
                results['PyMinMaximus']['draws'] += 1
                results['opponent']['draws'] += 1
    
    # Calculate statistics
    pymm_total = sum(results['PyMinMaximus'].values())
    pymm_score = results['PyMinMaximus']['wins'] + results['PyMinMaximus']['draws'] * 0.5
    pymm_percentage = (pymm_score / pymm_total * 100) if pymm_total > 0 else 0
    
    print(f"\nTotal games: {total_games}")
    print(f"\nPyMinMaximus:")
    print(f"  Wins: {results['PyMinMaximus']['wins']}")
    print(f"  Losses: {results['PyMinMaximus']['losses']}")
    print(f"  Draws: {results['PyMinMaximus']['draws']}")
    print(f"  Score: {pymm_score}/{pymm_total} ({pymm_percentage:.1f}%)")
    
    if pymm_white_games > 0:
        white_percentage = (pymm_white_wins / pymm_white_games * 100)
        print(f"\nAs White: {pymm_white_wins}/{pymm_white_games} ({white_percentage:.1f}%)")
    
    # Estimate ELO difference
    if pymm_percentage > 0 and pymm_percentage < 100:
        # Simple ELO estimation
        expected_score = pymm_percentage / 100
        elo_diff = 400 * (expected_score - 0.5) / 0.1
        print(f"\nEstimated ELO difference: {elo_diff:+.0f}")
    
    print("="*60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        analyze_tournament(sys.argv[1])
    else:
        print("Usage: python analyze_results.py <pgn_file>")
