import subprocess
import sys

def run_tournament(engine1_cmd, engine1_name, engine2_cmd, engine2_name, 
                   rounds=10, time_control="40/60"):
    """
    Run a tournament between two engines.
    
    Args:
        engine1_cmd: Command to start engine 1 (e.g., "python pyminmaximus.py")
        engine1_name: Name for engine 1
        engine2_cmd: Command to start engine 2
        engine2_name: Name for engine 2
        rounds: Number of rounds (each round = 2 games with colors swapped)
        time_control: Time control string (e.g., "40/60" = 60 seconds for 40 moves)
    """
    
    cmd = [
        'cutechess-cli',
        '-engine', f'cmd={engine1_cmd}', f'name={engine1_name}',
        '-engine', f'cmd={engine2_cmd}', f'name={engine2_name}',
        '-each', 'proto=uci', f'tc={time_control}',
        '-rounds', str(rounds),
        '-repeat',
        '-pgnout', f'results/{engine1_name}_vs_{engine2_name}.pgn'
    ]
    
    print("="*60)
    print(f"Tournament: {engine1_name} vs {engine2_name}")
    print(f"Rounds: {rounds} ({rounds * 2} games)")
    print(f"Time control: {time_control}")
    print("="*60)
    
    subprocess.run(cmd)


if __name__ == "__main__":
    # Test against random mover
    run_tournament(
        "../pyminmaximus.py", "PyMinMaximus",
        "../random_engine.py", "RandomMover",
        rounds=20,
        time_control="40/60"
        # alternative
        # time_control="10:00"
    )
