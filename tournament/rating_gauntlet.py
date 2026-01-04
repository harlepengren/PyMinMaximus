import subprocess

def run_rating_gauntlet():
    """
    Run PyMinMaximus against a series of opponents with known ratings.
    This helps establish an accurate ELO.
    """
    
    opponents = [
        #("../random_engine.py", "RandomMover", "", "~400 ELO"),
        ("stockfish", "Stockfish-0", "option.Skill Level=0", "~800 ELO"),
        ("fairy-stockfish", "Fairy-Weak", "option.Skill Level=5", "~1200 ELO"),
        # Add more opponents as available:
        # ("stockfish", "Stockfish-0", "option.Skill Level=0", "~800 ELO"),
        # ("fairy-stockfish", "Fairy-Weak", "option.Skill Level=5", "~1200 ELO"),
    ]
    
    results = []
    
    for opp_cmd, opp_name, opp_options, opp_rating in opponents:
        print(f"\n{'='*60}")
        print(f"Testing vs {opp_name} ({opp_rating})")
        print(f"{'='*60}\n")
        
        cmd = [
            'cutechess-cli',
            '-engine', 'cmd=../pyminmaximus.py', 'name=PyMinMaximus',
            '-engine', f'cmd={opp_cmd}', f'name={opp_name}', opp_options,
            '-each', 'proto=uci', 'tc=40/60',
            '-rounds', '20',
            '-repeat',
            '-pgnout', f'results/vs_{opp_name}.pgn'
        ]
        
        subprocess.run(cmd)
        
        # Analyze results
        from analyze_results import analyze_tournament
        analyze_tournament(f'results/vs_{opp_name}.pgn')
        
        results.append((opp_name, opp_rating))
    
    print("\n" + "="*60)
    print("Rating Gauntlet Complete")
    print("="*60)
    print("\nOpponents tested:")
    for name, rating in results:
        print(f"  - {name} ({rating})")
    
    print("\nAnalyze individual PGN files for detailed results.")


if __name__ == "__main__":
    run_rating_gauntlet()
