import unittest
import subprocess
import sys
import os

class TestOrchestrator(unittest.TestCase):
    def test_root_check(self):
        # This test should only run when not root, to verify the root check guard.
        if os.geteuid() == 0:
            self.skipTest("Running as root, cannot test non-root exit condition.")
        
        # Execute the script as a subprocess with a valid command structure
        result = subprocess.run(
            [sys.executable, "src/orchestrator.py", "scan", "lo"],
            capture_output=True, 
            text=True
        )
        
        # Check that the script printed the correct error message to stderr and exited
        self.assertIn("must be run as root", result.stderr)

if __name__ == "__main__":
    unittest.main()
