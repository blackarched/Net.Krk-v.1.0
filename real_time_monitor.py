#!/usr/bin/env python3
"""
Real-Time Attack Monitoring and Progress System
==============================================

This module provides real-time monitoring, progress tracking, and analytics
for all network security testing activities.
"""

import time
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich import box

@dataclass
class AttackSession:
    """Represents an active attack session."""
    session_id: str
    attack_type: str
    target_ip: str
    start_time: datetime
    status: str  # "running", "paused", "stopped", "completed"
    packets_captured: int = 0
    data_transferred: int = 0
    errors: int = 0
    warnings: int = 0

@dataclass
class NetworkStats:
    """Network statistics for monitoring."""
    total_devices: int
    active_connections: int
    packets_per_second: float
    bandwidth_usage: float
    suspicious_activity: int

class RealTimeMonitor:
    """Real-time monitoring system for network attacks."""
    
    def __init__(self):
        self.console = Console()
        self.active_sessions: Dict[str, AttackSession] = {}
        self.network_stats = NetworkStats(0, 0, 0.0, 0.0, 0)
        self.monitoring = False
        self.monitor_thread = None
        self.attack_history = []
        
    def start_monitoring(self):
        """Start the real-time monitoring system."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop the real-time monitoring system."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
    
    def create_attack_session(self, attack_type: str, target_ip: str) -> str:
        """Create a new attack session."""
        session_id = f"{attack_type}_{target_ip}_{int(time.time())}"
        session = AttackSession(
            session_id=session_id,
            attack_type=attack_type,
            target_ip=target_ip,
            start_time=datetime.now(),
            status="running"
        )
        self.active_sessions[session_id] = session
        return session_id
    
    def update_session_stats(self, session_id: str, **kwargs):
        """Update statistics for a specific session."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
    
    def stop_session(self, session_id: str):
        """Stop a specific attack session."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.status = "stopped"
            session.end_time = datetime.now()
            self.attack_history.append(session)
            del self.active_sessions[session_id]
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                self._update_network_stats()
                time.sleep(1)
            except Exception as e:
                self.console.print(f"[red]Monitoring error: {e}[/red]")
    
    def _update_network_stats(self):
        """Update network statistics."""
        # Simulate network stats update
        # In a real implementation, this would gather actual network data
        self.network_stats.total_devices = len(self.active_sessions) + 5
        self.network_stats.active_connections = len(self.active_sessions)
        self.network_stats.packets_per_second = sum(
            session.packets_captured for session in self.active_sessions.values()
        ) / 60.0  # Approximate PPS
        self.network_stats.bandwidth_usage = sum(
            session.data_transferred for session in self.active_sessions.values()
        ) / 1024.0  # KB/s
    
    def show_real_time_dashboard(self):
        """Display real-time monitoring dashboard."""
        layout = Layout()
        layout.split_column(
            Layout(self._create_header(), size=3),
            Layout(self._create_sessions_table(), size=8),
            Layout(self._create_network_stats(), size=6),
            Layout(self._create_activity_log(), size=8)
        )
        
        with Live(layout, refresh_per_second=2, console=self.console) as live:
            try:
                while True:
                    time.sleep(0.5)
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Stopping real-time monitoring...[/yellow]")
    
    def _create_header(self) -> Panel:
        """Create the dashboard header."""
        header_text = Text("🔍 REAL-TIME ATTACK MONITOR", style="bold blue")
        return Panel(Align.center(header_text), border_style="blue")
    
    def _create_sessions_table(self) -> Table:
        """Create the active sessions table."""
        table = Table(title="Active Attack Sessions", show_header=True, header_style="bold magenta")
        table.add_column("Session ID", style="cyan", width=20)
        table.add_column("Attack Type", style="green", width=15)
        table.add_column("Target", style="yellow", width=15)
        table.add_column("Status", style="red", width=10)
        table.add_column("Duration", style="blue", width=12)
        table.add_column("Packets", style="magenta", width=10)
        table.add_column("Data (KB)", style="green", width=10)
        
        for session in self.active_sessions.values():
            duration = datetime.now() - session.start_time
            status_color = "green" if session.status == "running" else "yellow" if session.status == "paused" else "red"
            
            table.add_row(
                session.session_id[:20],
                session.attack_type,
                session.target_ip,
                f"[{status_color}]{session.status}[/{status_color}]",
                str(duration).split('.')[0],
                str(session.packets_captured),
                f"{session.data_transferred/1024:.1f}"
            )
        
        if not self.active_sessions:
            table.add_row("No active sessions", "", "", "", "", "", "")
        
        return table
    
    def _create_network_stats(self) -> Panel:
        """Create network statistics panel."""
        stats_text = f"""
📊 Network Statistics:
• Total Devices: {self.network_stats.total_devices}
• Active Connections: {self.network_stats.active_connections}
• Packets/Second: {self.network_stats.packets_per_second:.1f}
• Bandwidth Usage: {self.network_stats.bandwidth_usage:.1f} KB/s
• Suspicious Activity: {self.network_stats.suspicious_activity}
        """
        return Panel(stats_text, title="Network Overview", border_style="green")
    
    def _create_activity_log(self) -> Panel:
        """Create activity log panel."""
        log_entries = []
        for session in list(self.active_sessions.values())[-5:]:  # Show last 5 sessions
            log_entries.append(f"[{session.start_time.strftime('%H:%M:%S')}] {session.attack_type} on {session.target_ip}")
        
        if not log_entries:
            log_entries = ["No recent activity"]
        
        log_text = "\n".join(log_entries)
        return Panel(log_text, title="Recent Activity", border_style="yellow")
    
    def show_attack_analytics(self):
        """Display attack analytics and history."""
        if not self.attack_history:
            self.console.print("[yellow]No attack history available.[/yellow]")
            return
        
        # Create analytics table
        table = Table(title="Attack History & Analytics", show_header=True, header_style="bold magenta")
        table.add_column("Date", style="cyan", width=12)
        table.add_column("Attack Type", style="green", width=15)
        table.add_column("Target", style="yellow", width=15)
        table.add_column("Duration", style="blue", width=12)
        table.add_column("Packets", style="magenta", width=10)
        table.add_column("Success", style="green", width=8)
        
        for session in self.attack_history[-10:]:  # Show last 10 sessions
            duration = (session.end_time - session.start_time) if hasattr(session, 'end_time') else timedelta(0)
            success = "✅" if session.errors == 0 else "❌"
            
            table.add_row(
                session.start_time.strftime("%Y-%m-%d"),
                session.attack_type,
                session.target_ip,
                str(duration).split('.')[0],
                str(session.packets_captured),
                success
            )
        
        self.console.print(table)
        
        # Show summary statistics
        total_attacks = len(self.attack_history)
        successful_attacks = len([s for s in self.attack_history if s.errors == 0])
        total_packets = sum(s.packets_captured for s in self.attack_history)
        
        summary_panel = Panel(
            f"""
📈 Summary Statistics:
• Total Attacks: {total_attacks}
• Success Rate: {(successful_attacks/total_attacks*100):.1f}%
• Total Packets Captured: {total_packets:,}
• Average Duration: {sum((s.end_time - s.start_time).total_seconds() for s in self.attack_history if hasattr(s, 'end_time')) / max(total_attacks, 1):.1f}s
            """,
            title="Analytics Summary",
            border_style="blue"
        )
        self.console.print(summary_panel)
    
    def export_session_data(self, session_id: str, filename: str = None):
        """Export session data to JSON file."""
        if session_id not in self.active_sessions:
            self.console.print(f"[red]Session {session_id} not found.[/red]")
            return
        
        session = self.active_sessions[session_id]
        if not filename:
            filename = f"session_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        session_data = asdict(session)
        session_data['start_time'] = session.start_time.isoformat()
        
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        self.console.print(f"[green]Session data exported to {filename}[/green]")
    
    def get_session_recommendations(self, session_id: str) -> List[str]:
        """Get recommendations based on session data."""
        if session_id not in self.active_sessions:
            return []
        
        session = self.active_sessions[session_id]
        recommendations = []
        
        if session.errors > 5:
            recommendations.append("High error rate detected. Check network connectivity and target availability.")
        
        if session.packets_captured == 0:
            recommendations.append("No packets captured. Verify target is active and network interface is correct.")
        
        if session.warnings > 3:
            recommendations.append("Multiple warnings detected. Review attack parameters and network configuration.")
        
        if session.data_transferred > 1000000:  # 1MB
            recommendations.append("Large data transfer detected. Consider bandwidth limitations and target impact.")
        
        return recommendations

def main():
    """Main function for real-time monitor."""
    monitor = RealTimeMonitor()
    
    # Example usage
    monitor.start_monitoring()
    
    # Create some example sessions
    session1 = monitor.create_attack_session("ARP_SPOOF", "192.168.1.100")
    session2 = monitor.create_attack_session("PACKET_SNIFF", "192.168.1.0/24")
    
    # Update some stats
    monitor.update_session_stats(session1, packets_captured=150, data_transferred=50000)
    monitor.update_session_stats(session2, packets_captured=300, data_transferred=75000)
    
    # Show dashboard
    monitor.show_real_time_dashboard()

if __name__ == "__main__":
    main()