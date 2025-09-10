import unittest
from unittest.mock import patch, MagicMock
from scanner import scan_networks, set_monitor_mode

class TestScanner(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()

    @patch('scanner.shutil.which', return_value="/sbin/iwconfig")
    @patch('scanner.subprocess.run')
    def test_set_monitor_mode_success(self, mock_run, mock_which):
        """Test that monitor mode is set with correct subprocess calls."""
        result = set_monitor_mode("wlan0", self.mock_logger)
        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 3)
        mock_run.assert_any_call(["ifconfig", "wlan0", "down"], check=True, capture_output=True, text=True)
        mock_run.assert_any_call(["iwconfig", "wlan0", "mode", "monitor"], check=True, capture_output=True, text=True)
        mock_run.assert_any_call(["ifconfig", "wlan0", "up"], check=True, capture_output=True, text=True)

    @patch('scanner.set_monitor_mode', return_value=True)
    @patch('scanner.scapy.sniff')
    def test_scan_networks_calls_sniff(self, mock_sniff, mock_set_monitor):
        """Test that scan_networks calls scapy.sniff when monitor mode is successful."""
        scan_networks("lo", scan_count=10, logger=self.mock_logger)
        mock_set_monitor.assert_called_once_with("lo", self.mock_logger)
        self.assertTrue(mock_sniff.called)
        self.assertEqual(mock_sniff.call_args.kwargs['count'], 100) # 10 * 10

    @patch('scanner.set_monitor_mode', return_value=False)
    @patch('scanner.scapy.sniff')
    def test_scan_networks_does_not_sniff_on_failure(self, mock_sniff, mock_set_monitor):
        """Test that scan_networks does not proceed if monitor mode fails."""
        result = scan_networks("lo", logger=self.mock_logger)
        mock_set_monitor.assert_called_once_with("lo", self.mock_logger)
        self.assertFalse(mock_sniff.called)
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()