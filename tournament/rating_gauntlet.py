import subprocess
import sys

def run_rating_gauntlet(tcontrol="40/60", rounds=20):
    """
    Run PyMinMaximus against a series of opponents with known ratings.
    This helps establish an accurate ELO.
    """
    
    opponents = [
        ("../random_engine.py", "RandomMover", "", "~400 ELO"),
        ("stockfish", "Stockfish-0", "option.Skill Level=0", "~800 ELO"),
        ("stockfish", "Fairy-Weak", "option.Skill Level=5", "~1200 ELO"),
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
            '-each', 'proto=uci', f'tc={tcontrol}',
            '-rounds', str(rounds),
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
    if sys.argc > 1:
        argument_dict = dict(sys.argv[1:])

    if "tc" in argument_dict:
        tcontrol = argument_dict["tc"]
    else:
        tcontrol = "40/60"

    if "rounds" in argument_dict:
        rounds = int(argument_dict["rounds"])
    else:
        rounds = 20

    run_rating_gauntlet(tcontrol=tcontrol, rounds=rounds)
