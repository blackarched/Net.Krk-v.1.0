"""
monitor.py - Real-time monitoring and status tracking for net.krak
"""
import time
import json
import threading
import logging
from datetime import datetime
from pathlib import Path
from attacks import get_attack_status
from scanner import get_scan_status

class NetKrakMonitor:
    """Real-time monitoring system for net.krak"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("netkrak.monitor")
        self.monitoring = False
        self.monitor_thread = None
        self.callbacks = []
        self.stats = {
            "start_time": time.time(),
            "scans_performed": 0,
            "attacks_executed": 0,
            "networks_discovered": 0,
            "errors_encountered": 0
        }
    
    def add_callback(self, callback):
        """Add a callback function to be called on status updates"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback):
        """Remove a callback function"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _notify_callbacks(self, data):
        """Notify all registered callbacks with status data"""
        for callback in self.callbacks:
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"Error in monitor callback: {e}")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Gather current status
                scan_status = get_scan_status()
                attack_status = get_attack_status()
                
                # Update stats
                self.stats["networks_discovered"] = scan_status.get("networks_found", 0)
                
                # Create status data
                status_data = {
                    "timestamp": time.time(),
                    "datetime": datetime.now().isoformat(),
                    "scan_status": scan_status,
                    "attack_status": attack_status,
                    "stats": self.stats,
                    "uptime": time.time() - self.stats["start_time"]
                }
                
                # Notify callbacks
                self._notify_callbacks(status_data)
                
                # Log status
                self.logger.debug(f"Monitor status: {json.dumps(status_data)}")
                
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
                self.stats["errors_encountered"] += 1
            
            time.sleep(1)  # Update every second
    
    def start_monitoring(self):
        """Start the monitoring system"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            self.logger.info("Monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        if self.monitoring:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=2)
            self.logger.info("Monitoring stopped")
    
    def get_stats(self):
        """Get current statistics"""
        return dict(self.stats)
    
    def update_stat(self, stat_name, increment=1):
        """Update a specific statistic"""
        if stat_name in self.stats:
            self.stats[stat_name] += increment

# Global monitor instance
monitor = NetKrakMonitor()

def start_monitoring():
    """Start the global monitoring system"""
    monitor.start_monitoring()

def stop_monitoring():
    """Stop the global monitoring system"""
    monitor.stop_monitoring()

def add_monitor_callback(callback):
    """Add a callback to the global monitor"""
    monitor.add_callback(callback)

def get_monitor_stats():
    """Get statistics from the global monitor"""
    return monitor.get_stats()