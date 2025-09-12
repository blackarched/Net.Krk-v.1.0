import unittest
from unittest.mock import patch
import sys
import os

# This is the correct way to modify the path to find the `src` directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.scanner import list_wifi_interfaces

class TestNewStructure(unittest.TestCase):

    @patch('src.scanner.scapy.get_if_list', return_value=['lo', 'eth0', 'wlan0'])
    @patch('src.scanner.subprocess.run')
    def test_list_wifi_interfaces_success(self, mock_run, mock_get_if_list):
        """
        Test that list_wifi_interfaces correctly identifies wireless interfaces.
        """
        # Mock the subprocess call to iwconfig
        def mock_subprocess_run(*args, **kwargs):
            cmd = args[0]
            iface = cmd[1]
            mock_result = unittest.mock.MagicMock()
            if iface == 'wlan0':
                mock_result.stdout = "wlan0     IEEE 802.11"
            else:
                mock_result.stdout = ""
            return mock_result

        mock_run.side_effect = mock_subprocess_run

        interfaces = list_wifi_interfaces()
        self.assertEqual(interfaces, ['wlan0'])

if __name__ == '__main__':
    unittest.main()
