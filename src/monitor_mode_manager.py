#!/usr/bin/env python3
"""
Monitor Mode Manager for NET.KRAK
Handles monitor mode operations without requiring passwords
"""

import subprocess
import logging
import time
from typing import Dict, List, Optional, Tuple
from .error_handler import error_handler

logger = logging.getLogger(__name__)

class MonitorModeManager:
    """Manages monitor mode operations for network interfaces"""
    
    def __init__(self):
        self.active_monitor_interfaces = set()
        self.original_modes = {}
        
    def enable_monitor_mode(self, interface: str) -> Dict[str, Any]:
        """Enable monitor mode for interface - NO PASSWORD REQUIRED"""
        try:
            # Check if already in monitor mode
            if self.is_monitor_mode(interface):
                return {
                    'success': True,
                    'monitor_mode': True,
                    'message': f'Interface {interface} already in monitor mode',
                    'interface': interface
                }
            
            # Try multiple methods to enable monitor mode
            methods = [
                self._enable_with_iw,
                self._enable_with_iwconfig,
                self._enable_with_airmon_ng
            ]
            
            for method in methods:
                try:
                    result = method(interface)
                    if result['success']:
                        self.active_monitor_interfaces.add(interface)
                        logger.info(f"Monitor mode enabled for {interface} using {method.__name__}")
                        return result
                except Exception as e:
                    logger.warning(f"Method {method.__name__} failed: {e}")
                    continue
            
            # If all methods failed, try to create monitor interface
            return self._create_monitor_interface(interface)
            
        except Exception as e:
            return error_handler.handle_network_error(e, interface)
    
    def disable_monitor_mode(self, interface: str) -> Dict[str, Any]:
        """Disable monitor mode for interface"""
        try:
            if not self.is_monitor_mode(interface):
                return {
                    'success': True,
                    'monitor_mode': False,
                    'message': f'Interface {interface} not in monitor mode',
                    'interface': interface
                }
            
            # Try to disable monitor mode
            methods = [
                self._disable_with_iw,
                self._disable_with_iwconfig,
                self._disable_with_airmon_ng
            ]
            
            for method in methods:
                try:
                    result = method(interface)
                    if result['success']:
                        self.active_monitor_interfaces.discard(interface)
                        logger.info(f"Monitor mode disabled for {interface} using {method.__name__}")
                        return result
                except Exception as e:
                    logger.warning(f"Method {method.__name__} failed: {e}")
                    continue
            
            return {
                'success': False,
                'monitor_mode': True,
                'message': f'Failed to disable monitor mode for {interface}',
                'interface': interface
            }
            
        except Exception as e:
            return error_handler.handle_network_error(e, interface)
    
    def is_monitor_mode(self, interface: str) -> bool:
        """Check if interface is in monitor mode"""
        try:
            # Check with iw
            result = subprocess.run(
                ['iw', interface, 'info'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return 'type monitor' in result.stdout.lower()
            
            # Fallback to iwconfig
            result = subprocess.run(
                ['iwconfig', interface],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return 'Mode:Monitor' in result.stdout
            
            return False
            
        except Exception:
            return False
    
    def get_monitor_interfaces(self) -> List[str]:
        """Get list of interfaces in monitor mode"""
        monitor_interfaces = []
        
        try:
            # Get all wireless interfaces
            result = subprocess.run(
                ['iw', 'dev'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                current_interface = None
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('Interface'):
                        current_interface = line.split()[1]
                    elif 'type monitor' in line and current_interface:
                        monitor_interfaces.append(current_interface)
            
        except Exception as e:
            logger.warning(f"Error getting monitor interfaces: {e}")
        
        return monitor_interfaces
    
    def _enable_with_iw(self, interface: str) -> Dict[str, Any]:
        """Enable monitor mode using iw command"""
        try:
            # Create monitor interface
            monitor_interface = f"{interface}mon"
            
            result = subprocess.run(
                ['iw', 'dev', interface, 'interface', 'add', monitor_interface, 'type', 'monitor'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                # Bring up the monitor interface
                subprocess.run(['ip', 'link', 'set', monitor_interface, 'up'], 
                             capture_output=True, timeout=5)
                
                return {
                    'success': True,
                    'monitor_mode': True,
                    'message': f'Monitor mode enabled for {interface} (created {monitor_interface})',
                    'interface': monitor_interface
                }
            else:
                return {
                    'success': False,
                    'monitor_mode': False,
                    'message': f'Failed to create monitor interface: {result.stderr}',
                    'interface': interface
                }
                
        except Exception as e:
            return {
                'success': False,
                'monitor_mode': False,
                'message': f'Error with iw command: {str(e)}',
                'interface': interface
            }
    
    def _enable_with_iwconfig(self, interface: str) -> Dict[str, Any]:
        """Enable monitor mode using iwconfig command"""
        try:
            result = subprocess.run(
                ['iwconfig', interface, 'mode', 'monitor'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'monitor_mode': True,
                    'message': f'Monitor mode enabled for {interface} using iwconfig',
                    'interface': interface
                }
            else:
                return {
                    'success': False,
                    'monitor_mode': False,
                    'message': f'iwconfig failed: {result.stderr}',
                    'interface': interface
                }
                
        except Exception as e:
            return {
                'success': False,
                'monitor_mode': False,
                'message': f'Error with iwconfig: {str(e)}',
                'interface': interface
            }
    
    def _enable_with_airmon_ng(self, interface: str) -> Dict[str, Any]:
        """Enable monitor mode using airmon-ng command"""
        try:
            result = subprocess.run(
                ['airmon-ng', 'start', interface],
                capture_output=True, text=True, timeout=15
            )
            
            if result.returncode == 0:
                # Parse output to find monitor interface
                output_lines = result.stdout.split('\n')
                monitor_interface = None
                
                for line in output_lines:
                    if 'monitor mode enabled' in line.lower():
                        # Extract interface name
                        parts = line.split()
                        for part in parts:
                            if 'mon' in part.lower():
                                monitor_interface = part
                                break
                
                return {
                    'success': True,
                    'monitor_mode': True,
                    'message': f'Monitor mode enabled for {interface} using airmon-ng',
                    'interface': monitor_interface or interface
                }
            else:
                return {
                    'success': False,
                    'monitor_mode': False,
                    'message': f'airmon-ng failed: {result.stderr}',
                    'interface': interface
                }
                
        except Exception as e:
            return {
                'success': False,
                'monitor_mode': False,
                'message': f'Error with airmon-ng: {str(e)}',
                'interface': interface
            }
    
    def _create_monitor_interface(self, interface: str) -> Dict[str, Any]:
        """Create a monitor interface as fallback"""
        try:
            monitor_interface = f"{interface}mon"
            
            # Try to create monitor interface
            result = subprocess.run(
                ['iw', 'dev', interface, 'interface', 'add', monitor_interface, 'type', 'monitor'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                # Bring up the interface
                subprocess.run(['ip', 'link', 'set', monitor_interface, 'up'], 
                             capture_output=True, timeout=5)
                
                return {
                    'success': True,
                    'monitor_mode': True,
                    'message': f'Created monitor interface {monitor_interface} for {interface}',
                    'interface': monitor_interface
                }
            else:
                return {
                    'success': False,
                    'monitor_mode': False,
                    'message': f'Failed to create monitor interface: {result.stderr}',
                    'interface': interface
                }
                
        except Exception as e:
            return {
                'success': False,
                'monitor_mode': False,
                'message': f'Error creating monitor interface: {str(e)}',
                'interface': interface
            }
    
    def _disable_with_iw(self, interface: str) -> Dict[str, Any]:
        """Disable monitor mode using iw command"""
        try:
            result = subprocess.run(
                ['iw', 'dev', interface, 'del'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'monitor_mode': False,
                    'message': f'Monitor interface {interface} deleted',
                    'interface': interface
                }
            else:
                return {
                    'success': False,
                    'monitor_mode': True,
                    'message': f'Failed to delete monitor interface: {result.stderr}',
                    'interface': interface
                }
                
        except Exception as e:
            return {
                'success': False,
                'monitor_mode': True,
                'message': f'Error deleting monitor interface: {str(e)}',
                'interface': interface
            }
    
    def _disable_with_iwconfig(self, interface: str) -> Dict[str, Any]:
        """Disable monitor mode using iwconfig command"""
        try:
            result = subprocess.run(
                ['iwconfig', interface, 'mode', 'managed'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'monitor_mode': False,
                    'message': f'Monitor mode disabled for {interface} using iwconfig',
                    'interface': interface
                }
            else:
                return {
                    'success': False,
                    'monitor_mode': True,
                    'message': f'iwconfig failed: {result.stderr}',
                    'interface': interface
                }
                
        except Exception as e:
            return {
                'success': False,
                'monitor_mode': True,
                'message': f'Error with iwconfig: {str(e)}',
                'interface': interface
            }
    
    def _disable_with_airmon_ng(self, interface: str) -> Dict[str, Any]:
        """Disable monitor mode using airmon-ng command"""
        try:
            result = subprocess.run(
                ['airmon-ng', 'stop', interface],
                capture_output=True, text=True, timeout=15
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'monitor_mode': False,
                    'message': f'Monitor mode disabled for {interface} using airmon-ng',
                    'interface': interface
                }
            else:
                return {
                    'success': False,
                    'monitor_mode': True,
                    'message': f'airmon-ng failed: {result.stderr}',
                    'interface': interface
                }
                
        except Exception as e:
            return {
                'success': False,
                'monitor_mode': True,
                'message': f'Error with airmon-ng: {str(e)}',
                'interface': interface
            }

# Global monitor mode manager instance
monitor_mode_manager = MonitorModeManager()