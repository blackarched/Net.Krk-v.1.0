import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.attacks import deauth_attack, capture_handshake, perform_evil_twin, run_external_tool

class TestAttacks(unittest.TestCase):

    def setUp(self):
        # Create a mock logger to prevent log file creation during tests
        self.mock_logger = MagicMock()

    @patch('src.attacks.sendp')
    def test_deauth_attack_sends_packets(self, mock_sendp):
        """Test that deauth_attack calls scapy's sendp correctly."""
        deauth_attack("lo", "00:11:22:33:44:55", packet_count=5, logger=self.mock_logger)
        self.assertTrue(mock_sendp.called)
        self.assertEqual(mock_sendp.call_args.kwargs['count'], 5)
        self.assertEqual(mock_sendp.call_args.kwargs['iface'], "lo")

    @patch('src.attacks.shutil.which', return_value="/usr/bin/tool")
    @patch('src.attacks.subprocess.Popen')
    def test_run_external_tool_success(self, mock_popen, mock_which):
        """Test that run_external_tool successfully calls Popen."""
        cmd = ["tool", "--arg"]
        run_external_tool(cmd, logger=self.mock_logger)
        mock_popen.assert_called_once_with(
            cmd,
            stdout=unittest.mock.ANY,
            stderr=unittest.mock.ANY
        )

    @patch('src.attacks.shutil.which', return_value=None)
    def test_run_external_tool_tool_not_found(self, mock_which):
        """Test that run_external_tool returns None if the tool is not found."""
        result = run_external_tool(["nonexistent_tool"], logger=self.mock_logger)
        self.assertIsNone(result)
        self.mock_logger.error.assert_called_with("Required tool 'nonexistent_tool' not found in system PATH.")

    @patch('src.attacks.run_external_tool')
    def test_capture_handshake_constructs_correct_command(self, mock_run_tool):
        """Test handshake capture forms the correct airodump-ng command."""
        capture_handshake("wlan0mon", "AA:BB:CC:DD:EE:FF", 11, logger=self.mock_logger)
        expected_cmd = ["airodump-ng", "--bssid", "AA:BB:CC:DD:EE:FF", "-c", "11", "-w", "handshake_capture", "wlan0mon"]
        mock_run_tool.assert_called_once_with(expected_cmd, dry_run=False, logger=self.mock_logger)

    @patch('src.attacks.run_external_tool')
    def test_perform_evil_twin_constructs_correct_command(self, mock_run_tool):
        """Test evil twin forms the correct airbase-ng command."""
        perform_evil_twin("wlan0mon", "AA:BB:CC:DD:EE:FF", "MyFakeAP", logger=self.mock_logger)
        expected_cmd = ["airbase-ng", "--essid", "MyFakeAP", "-a", "AA:BB:CC:DD:EE:FF", "wlan0mon"]
        mock_run_tool.assert_called_once_with(expected_cmd, dry_run=False, logger=self.mock_logger)

if __name__ == '__main__':
    unittest.main()