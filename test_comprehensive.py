#!/usr/bin/env python3
"""
test_comprehensive.py - Comprehensive test suite for net.krak
Tests all major functionality and components
"""
import unittest
import sys
import os
import time
import json
from unittest.mock import patch, MagicMock, mock_open

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from attacks import AttackManager, deauth_attack, run_external_tool, capture_handshake, perform_evil_twin
from scanner import NetworkScanner, scan_networks, list_wifi_interfaces
from logger_config import setup_logging, log_event
from monitor import NetKrakMonitor

class TestAttackManager(unittest.TestCase):
    """Test the AttackManager class"""
    
    def setUp(self):
        self.manager = AttackManager()
        self.mock_logger = MagicMock()
        self.manager.logger = self.mock_logger
    
    def test_validate_mac_address(self):
        """Test MAC address validation"""
        # Valid MAC addresses
        valid_macs = [
            "00:11:22:33:44:55",
            "aa:bb:cc:dd:ee:ff",
            "00-11-22-33-44-55",
            "AA:BB:CC:DD:EE:FF"
        ]
        for mac in valid_macs:
            self.assertTrue(self.manager._validate_mac_address(mac))
        
        # Invalid MAC addresses
        invalid_macs = [
            "00:11:22:33:44",  # Too short
            "00:11:22:33:44:55:66",  # Too long
            "gg:11:22:33:44:55",  # Invalid characters
            "00:11:22:33:44:5g",  # Invalid characters
            "00:11:22:33:44",  # Wrong format
        ]
        for mac in invalid_macs:
            with self.assertRaises(ValueError):
                self.manager._validate_mac_address(mac)
    
    def test_validate_channel(self):
        """Test channel validation"""
        # Valid channels
        for channel in [1, 6, 11, 36, 149, 165]:
            self.assertTrue(self.manager._validate_channel(channel))
        
        # Invalid channels
        for channel in [0, 166, -1, "invalid"]:
            with self.assertRaises(ValueError):
                self.manager._validate_channel(channel)
    
    def test_log_attack_event(self):
        """Test attack event logging"""
        self.manager._log_attack_event("test_event", test_param="test_value")
        self.mock_logger.info.assert_called_once()
        logged_data = json.loads(self.mock_logger.info.call_args[0][0])
        self.assertEqual(logged_data["event_type"], "test_event")
        self.assertEqual(logged_data["test_param"], "test_value")

class TestAttacks(unittest.TestCase):
    """Test attack functions"""
    
    def setUp(self):
        self.mock_logger = MagicMock()
    
    @patch('attacks.sendp')
    def test_deauth_attack_dry_run(self, mock_sendp):
        """Test deauth attack in dry run mode"""
        result = deauth_attack("lo", "00:11:22:33:44:55", dry_run=True, logger=self.mock_logger)
        self.assertTrue(result)
        mock_sendp.assert_not_called()
    
    @patch('attacks.shutil.which', return_value="/usr/bin/airodump-ng")
    @patch('attacks.subprocess.Popen')
    def test_run_external_tool_success(self, mock_popen, mock_which):
        """Test successful external tool execution"""
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        result = run_external_tool(["airodump-ng", "--test"], logger=self.mock_logger)
        self.assertEqual(result, mock_process)
        mock_popen.assert_called_once()
    
    @patch('attacks.shutil.which', return_value=None)
    def test_run_external_tool_not_found(self, mock_which):
        """Test external tool not found"""
        result = run_external_tool(["nonexistent_tool"], logger=self.mock_logger)
        self.assertIsNone(result)

class TestScanner(unittest.TestCase):
    """Test scanner functions"""
    
    def setUp(self):
        self.scanner = NetworkScanner()
        self.mock_logger = MagicMock()
        self.scanner.logger = self.mock_logger
    
    def test_validate_interface(self):
        """Test interface validation"""
        with patch('scanner.scapy.get_if_list', return_value=['lo', 'eth0', 'wlan0']):
            self.assertTrue(self.scanner._validate_interface('lo'))
            with self.assertRaises(ValueError):
                self.scanner._validate_interface('nonexistent')
    
    def test_parse_beacon_frame(self):
        """Test beacon frame parsing"""
        # This would require creating a mock scapy packet
        # For now, just test that the method exists and handles None
        result = self.scanner._parse_beacon_frame(None)
        self.assertIsNone(result)

class TestMonitor(unittest.TestCase):
    """Test monitoring system"""
    
    def setUp(self):
        self.monitor = NetKrakMonitor()
        self.mock_logger = MagicMock()
        self.monitor.logger = self.mock_logger
    
    def test_stats_initialization(self):
        """Test that stats are properly initialized"""
        stats = self.monitor.get_stats()
        self.assertIn("start_time", stats)
        self.assertIn("scans_performed", stats)
        self.assertIn("attacks_executed", stats)
        self.assertEqual(stats["scans_performed"], 0)
    
    def test_callback_system(self):
        """Test callback registration and notification"""
        callback_called = []
        
        def test_callback(data):
            callback_called.append(data)
        
        self.monitor.add_callback(test_callback)
        self.monitor._notify_callbacks({"test": "data"})
        
        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_called[0]["test"], "data")
        
        self.monitor.remove_callback(test_callback)
        self.monitor._notify_callbacks({"test": "data2"})
        
        # Should still be 1 since callback was removed
        self.assertEqual(len(callback_called), 1)

class TestLoggerConfig(unittest.TestCase):
    """Test logger configuration"""
    
    def test_setup_logging(self):
        """Test logging setup"""
        logger = setup_logging()
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "netkrak")
    
    def test_log_event(self):
        """Test event logging"""
        logger = setup_logging()
        with patch.object(logger, 'info') as mock_info:
            log_event(logger, "test_event", param1="value1")
            mock_info.assert_called_once()
            logged_data = json.loads(mock_info.call_args[0][0])
            self.assertEqual(logged_data["event"], "test_event")
            self.assertEqual(logged_data["param1"], "value1")

class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_import_all_modules(self):
        """Test that all modules can be imported without errors"""
        try:
            import attacks
            import scanner
            import dashboard_api
            import orchestrator
            import monitor
            import logger_config
        except ImportError as e:
            self.fail(f"Failed to import module: {e}")
    
    def test_logger_consistency(self):
        """Test that logger configuration is consistent"""
        from logger_config import setup_logging
        logger1 = setup_logging()
        logger2 = setup_logging()
        self.assertEqual(logger1, logger2)  # Should be the same instance

def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestAttackManager,
        TestAttacks,
        TestScanner,
        TestMonitor,
        TestLoggerConfig,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("Running comprehensive net.krak test suite...")
    print("=" * 50)
    
    success = run_tests()
    
    print("=" * 50)
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)