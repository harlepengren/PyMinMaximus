import subprocess
import time

def test_uci_protocol():
    """Test basic UCI communication."""
    print("="*60)
    print("Testing UCI Protocol")
    print("="*60)
    
    # Start engine process
    engine = subprocess.Popen(
        ['python', 'pyminmaximus.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    def send_command(cmd):
        """Send command and read response."""
        print(f"\n→ {cmd}")
        engine.stdin.write(cmd + '\n')
        engine.stdin.flush()
        time.sleep(0.1)
        
        # Read available output
        output = []
        while True:
            try:
                line = engine.stdout.readline().strip()
                if not line:
                    break
                print(f"← {line}")
                output.append(line)
            except:
                break
        
        return output
    
    # Test UCI initialization
    print("\n1. Testing UCI initialization")
    output = send_command('uci')
    assert any('id name' in line for line in output), "Missing engine name"
    assert any('uciok' in line for line in output), "Missing uciok"
    print("✓ UCI initialization OK")
    
    # Test ready check
    print("\n2. Testing ready check")
    output = send_command('isready')
    assert any('readyok' in line for line in output), "Missing readyok"
    print("✓ Ready check OK")
    
    # Test position setup
    print("\n3. Testing position setup")
    send_command('position startpos moves e2e4')
    send_command('isready')
    print("✓ Position setup OK")
    
    # Test search
    print("\n4. Testing search")
    output = send_command('go movetime 1000')
    assert any('bestmove' in line for line in output), "Missing bestmove"
    print("✓ Search OK")
    
    # Cleanup
    send_command('quit')
    engine.wait(timeout=2)
    
    print("\n" + "="*60)
    print("All UCI tests passed! ✓")
    print("="*60)


if __name__ == "__main__":
    test_uci_protocol()
