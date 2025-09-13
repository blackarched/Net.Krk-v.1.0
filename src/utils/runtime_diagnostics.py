"""
runtime_diagnostics.py - Comprehensive runtime diagnostics for net.krak
Provides detailed diagnostics for missing tools, insufficient privileges, and system requirements
"""
import os
import sys
import shutil
import subprocess
import json
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class RuntimeDiagnostics:
    """Comprehensive runtime diagnostics for net.krak"""
    
    def __init__(self):
        self.required_tools = {
            'aircrack-ng': {
                'commands': ['airodump-ng', 'aireplay-ng', 'aircrack-ng', 'airmon-ng'],
                'package': 'aircrack-ng',
                'description': 'WiFi security testing suite'
            },
            'iw': {
                'commands': ['iw', 'iwconfig'],
                'package': 'wireless-tools',
                'description': 'Wireless interface management'
            },
            'net-tools': {
                'commands': ['ifconfig', 'netstat'],
                'package': 'net-tools',
                'description': 'Network configuration tools'
            },
            'reaver': {
                'commands': ['reaver'],
                'package': 'reaver',
                'description': 'WPS PIN attack tool'
            },
            'bully': {
                'commands': ['bully'],
                'package': 'bully',
                'description': 'Alternative WPS attack tool'
            }
        }
        
        self.required_capabilities = [
            'CAP_NET_RAW',
            'CAP_NET_ADMIN',
            'CAP_SYS_ADMIN'
        ]
    
    def run_comprehensive_diagnostics(self) -> Dict:
        """Run comprehensive system diagnostics"""
        diagnostics = {
            'system_info': self.get_system_info(),
            'tool_availability': self.check_tool_availability(),
            'privilege_checks': self.check_privileges(),
            'interface_checks': self.check_wireless_interfaces(),
            'docker_checks': self.check_docker_environment(),
            'recommendations': []
        }
        
        # Generate recommendations based on findings
        diagnostics['recommendations'] = self.generate_recommendations(diagnostics)
        
        return diagnostics
    
    def get_system_info(self) -> Dict:
        """Get basic system information"""
        return {
            'platform': platform.platform(),
            'python_version': sys.version,
            'architecture': platform.architecture()[0],
            'is_root': os.geteuid() == 0,
            'user': os.getenv('USER', 'unknown'),
            'home_dir': os.path.expanduser('~'),
            'working_dir': os.getcwd()
        }
    
    def check_tool_availability(self) -> Dict:
        """Check availability of required tools"""
        results = {}
        
        for tool_group, config in self.required_tools.items():
            tool_results = {}
            all_found = True
            
            for command in config['commands']:
                path = shutil.which(command)
                tool_results[command] = {
                    'available': path is not None,
                    'path': path,
                    'package': config['package'],
                    'description': config['description']
                }
                if path is None:
                    all_found = False
            
            results[tool_group] = {
                'available': all_found,
                'tools': tool_results,
                'package': config['package'],
                'description': config['description']
            }
        
        return results
    
    def check_privileges(self) -> Dict:
        """Check system privileges and capabilities"""
        results = {
            'is_root': os.geteuid() == 0,
            'capabilities': {},
            'docker_capabilities': self.check_docker_capabilities(),
            'network_interface_access': self.check_network_interface_access()
        }
        
        # Check individual capabilities if possible
        for cap in self.required_capabilities:
            results['capabilities'][cap] = self.check_capability(cap)
        
        return results
    
    def check_capability(self, capability: str) -> Dict:
        """Check if a specific capability is available"""
        try:
            # Try to check capabilities using getcap if available
            if shutil.which('getcap'):
                result = subprocess.run(
                    ['getcap', '/proc/self/exe'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                has_cap = capability.lower() in result.stdout.lower()
            else:
                # Fallback: assume we have capabilities if running as root
                has_cap = os.geteuid() == 0
            
            return {
                'available': has_cap,
                'method': 'getcap' if shutil.which('getcap') else 'root_check'
            }
        except Exception as e:
            return {
                'available': False,
                'error': str(e),
                'method': 'error'
            }
    
    def check_docker_capabilities(self) -> Dict:
        """Check if running in Docker with proper capabilities"""
        docker_info = {
            'is_docker': False,
            'has_required_caps': False,
            'network_mode': 'unknown',
            'capabilities': []
        }
        
        try:
            # Check if running in Docker
            if os.path.exists('/.dockerenv'):
                docker_info['is_docker'] = True
                
                # Check for required capabilities by testing network operations
                try:
                    # Try to create a raw socket (requires CAP_NET_RAW)
                    import socket
                    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
                    sock.close()
                    docker_info['has_required_caps'] = True
                except PermissionError:
                    docker_info['has_required_caps'] = False
                
                # Check network mode
                try:
                    result = subprocess.run(
                        ['ip', 'route', 'show', 'default'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if '172.' in result.stdout or '192.168.' in result.stdout:
                        docker_info['network_mode'] = 'bridge'
                    else:
                        docker_info['network_mode'] = 'host'
                except:
                    docker_info['network_mode'] = 'unknown'
        
        except Exception as e:
            docker_info['error'] = str(e)
        
        return docker_info
    
    def check_network_interface_access(self) -> Dict:
        """Check access to network interfaces"""
        results = {
            'can_list_interfaces': False,
            'can_access_wireless': False,
            'interfaces': [],
            'wireless_interfaces': []
        }
        
        try:
            # Try to list network interfaces
            if shutil.which('ip'):
                result = subprocess.run(
                    ['ip', 'link', 'show'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    results['can_list_interfaces'] = True
                    # Parse interfaces
                    for line in result.stdout.split('\n'):
                        if ':' in line and 'state' in line:
                            iface = line.split(':')[1].strip().split('@')[0]
                            results['interfaces'].append(iface)
            
            # Try to access wireless interfaces
            if shutil.which('iw'):
                result = subprocess.run(
                    ['iw', 'dev'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    results['can_access_wireless'] = True
                    # Parse wireless interfaces
                    for line in result.stdout.split('\n'):
                        if 'Interface' in line:
                            iface = line.split('Interface')[1].strip()
                            results['wireless_interfaces'].append(iface)
        
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def check_wireless_interfaces(self) -> Dict:
        """Check for available wireless interfaces"""
        results = {
            'available_interfaces': [],
            'monitor_mode_interfaces': [],
            'can_enter_monitor_mode': False
        }
        
        try:
            # List wireless interfaces
            if shutil.which('iw'):
                result = subprocess.run(
                    ['iw', 'dev'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'Interface' in line:
                            iface = line.split('Interface')[1].strip()
                            results['available_interfaces'].append(iface)
                            
                            # Check if already in monitor mode
                            mode_result = subprocess.run(
                                ['iw', iface, 'info'],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            if 'type monitor' in mode_result.stdout:
                                results['monitor_mode_interfaces'].append(iface)
            
            # Test if we can enter monitor mode
            if results['available_interfaces']:
                test_interface = results['available_interfaces'][0]
                try:
                    # Try to set monitor mode (this will fail if no permissions)
                    result = subprocess.run(
                        ['iw', 'dev', test_interface, 'set', 'type', 'monitor'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    results['can_enter_monitor_mode'] = result.returncode == 0
                except:
                    results['can_enter_monitor_mode'] = False
        
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def check_docker_environment(self) -> Dict:
        """Check Docker environment and configuration"""
        return {
            'is_docker': os.path.exists('/.dockerenv'),
            'has_tun_device': os.path.exists('/dev/net/tun'),
            'has_dbus_access': os.path.exists('/var/run/dbus'),
            'network_mode': self._detect_network_mode()
        }
    
    def _detect_network_mode(self) -> str:
        """Detect Docker network mode"""
        try:
            result = subprocess.run(
                ['ip', 'route', 'show', 'default'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if '172.' in result.stdout or '192.168.' in result.stdout:
                return 'bridge'
            else:
                return 'host'
        except:
            return 'unknown'
    
    def generate_recommendations(self, diagnostics: Dict) -> List[str]:
        """Generate actionable recommendations based on diagnostics"""
        recommendations = []
        
        # Tool availability recommendations
        tool_checks = diagnostics['tool_availability']
        for tool_group, status in tool_checks.items():
            if not status['available']:
                recommendations.append(
                    f"Install {status['package']}: sudo apt-get install {status['package']} "
                    f"({status['description']})"
                )
        
        # Privilege recommendations
        if not diagnostics['privilege_checks']['is_root']:
            recommendations.append(
                "Run as root: sudo python3 orchestrator.py [command]"
            )
        
        # Docker recommendations
        docker_checks = diagnostics['docker_checks']
        if docker_checks['is_docker']:
            if not diagnostics['privilege_checks']['docker_capabilities']['has_required_caps']:
                recommendations.append(
                    "Add required capabilities: --cap-add=NET_ADMIN --cap-add=NET_RAW"
                )
            
            if docker_checks['network_mode'] != 'host':
                recommendations.append(
                    "Use host networking: --network host (required for wireless operations)"
                )
            
            if not docker_checks['has_tun_device']:
                recommendations.append(
                    "Add TUN device: --device /dev/net/tun"
                )
        
        # Interface recommendations
        interface_checks = diagnostics['interface_checks']
        if not interface_checks['available_interfaces']:
            recommendations.append(
                "No wireless interfaces found. Check if WiFi adapter is connected and drivers are installed."
            )
        elif not interface_checks['can_enter_monitor_mode']:
            recommendations.append(
                "Cannot enter monitor mode. Ensure running as root with proper capabilities."
            )
        
        return recommendations
    
    def print_diagnostics(self, diagnostics: Dict = None):
        """Print formatted diagnostics to console"""
        if diagnostics is None:
            diagnostics = self.run_comprehensive_diagnostics()
        
        print("\n" + "="*80)
        print("                    NET.KRAK RUNTIME DIAGNOSTICS")
        print("="*80)
        
        # System Information
        print("\n📊 SYSTEM INFORMATION:")
        sys_info = diagnostics['system_info']
        print(f"  Platform: {sys_info['platform']}")
        print(f"  Python: {sys_info['python_version']}")
        print(f"  Running as root: {'✅' if sys_info['is_root'] else '❌'}")
        print(f"  User: {sys_info['user']}")
        
        # Tool Availability
        print("\n🔧 TOOL AVAILABILITY:")
        tool_checks = diagnostics['tool_availability']
        for tool_group, status in tool_checks.items():
            status_icon = "✅" if status['available'] else "❌"
            print(f"  {status_icon} {tool_group}: {status['description']}")
            if not status['available']:
                for tool, tool_status in status['tools'].items():
                    if not tool_status['available']:
                        print(f"    ❌ Missing: {tool} (install {tool_status['package']})")
        
        # Privilege Checks
        print("\n🔐 PRIVILEGE CHECKS:")
        priv_checks = diagnostics['privilege_checks']
        print(f"  Root privileges: {'✅' if priv_checks['is_root'] else '❌'}")
        
        if priv_checks['docker_capabilities']['is_docker']:
            print(f"  Docker capabilities: {'✅' if priv_checks['docker_capabilities']['has_required_caps'] else '❌'}")
            print(f"  Network mode: {priv_checks['docker_capabilities']['network_mode']}")
        
        # Interface Checks
        print("\n📡 WIRELESS INTERFACES:")
        iface_checks = diagnostics['interface_checks']
        print(f"  Available interfaces: {len(iface_checks['available_interfaces'])}")
        for iface in iface_checks['available_interfaces']:
            print(f"    - {iface}")
        
        print(f"  Monitor mode capable: {'✅' if iface_checks['can_enter_monitor_mode'] else '❌'}")
        
        # Recommendations
        if diagnostics['recommendations']:
            print("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(diagnostics['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "="*80)
    
    def get_docker_run_command(self, diagnostics: Dict = None) -> str:
        """Generate the optimal Docker run command based on diagnostics"""
        if diagnostics is None:
            diagnostics = self.run_comprehensive_diagnostics()
        
        cmd_parts = ["docker run -it --rm"]
        
        # Add capabilities
        cmd_parts.append("--cap-add=NET_ADMIN --cap-add=NET_RAW")
        
        # Add devices
        cmd_parts.append("--device /dev/net/tun")
        
        # Add network mode
        cmd_parts.append("--network host")
        
        # Add volumes
        cmd_parts.append("-v /path/to/captures:/app/captures")
        cmd_parts.append("-v /var/run/dbus:/var/run/dbus")
        
        # Add container name
        cmd_parts.append("--name netkrak netkrak:latest")
        
        return " \\\n  ".join(cmd_parts)

def main():
    """Main function for standalone diagnostics"""
    diagnostics_engine = RuntimeDiagnostics()
    diagnostics = diagnostics_engine.run_comprehensive_diagnostics()
    diagnostics_engine.print_diagnostics(diagnostics)
    
    # Print Docker command if in Docker
    if diagnostics['docker_checks']['is_docker']:
        print("\n🐳 DOCKER RUN COMMAND:")
        print(diagnostics_engine.get_docker_run_command(diagnostics))

if __name__ == "__main__":
    main()