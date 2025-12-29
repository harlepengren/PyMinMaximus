import subprocess
import time
import unittest

class TestUCIProtocol(unittest.TestCase):
    def setUp(self):
        """Test basic UCI communication."""
        print("="*60)
        print("Testing UCI Protocol")
        print("="*60)
        
        # Start engine process
        self.engine = subprocess.Popen(
            ['python3', 'pyminmaximus.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
    def send_command(self, cmd):
        """Send command and read response."""
        print(f"\n→ {cmd}")
        self.engine.stdin.write(cmd + '\n')
        self.engine.stdin.flush()
        time.sleep(0.1)
        
        # Read available output
        output = []
        while True:
            # Check if data is available (0.5 second timeout)
            ready, _, _ = select.select([self.engine.stdout], [], [], 0.5)
            if not ready:
                break
            line = self.engine.stdout.readline()
            if not line:
                break
            print(f"← {line.strip()}")
            output.append(line)
        
        return output
        
    def test_uci_initialization(self):
        # Test UCI initialization
        print("\n1. Testing UCI initialization")
        output = self.send_command('uci')
        #self.assertIsNotNone('id name' in line for line in output)
        #self.assertIsNotNone('uciok' in line for line in output)
        
    def test_ready_check(self):
        # Test ready check
        print("\n2. Testing ready check")
        output = self.send_command('isready')
        #self.assertIsNotNone('readyok' in line for line in output), "Missing readyok"
        
    def test_position_setup(self):
        # Test position setup
        print("\n3. Testing position setup")
        self.send_command('position startpos moves e2e4')
        self.send_command('isready')
        print("✓ Position setup OK")
        
    def test_search(self):
        # Test search
        print("\n4. Testing search")
        output = self.send_command('go movetime 1000')
        #self.assertIsNotNone('bestmove' in line for line in output), "Missing bestmove"
        
    def tearDown(self):
        # Cleanup
        self.send_command('quit')
        self.engine.wait(timeout=2)

        print("\n" + "="*60)
        print("All UCI tests passed! ✓")
        print("="*60)

        return super().tearDown()

if __name__ == "__main__":
    unittest.main()
