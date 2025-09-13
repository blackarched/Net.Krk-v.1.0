"""
orchestrator.py - Enhanced CLI, process management, logging, and legal/safety guards for net.krak
Improved with better process management, enhanced logging, and additional safety measures
"""
import os
import sys
import argparse
import json
import logging
import getpass
import signal
import time
import threading
import hashlib
import hmac
try:
    import psutil
except ImportError:
    psutil = None
from pathlib import Path
from .scanner import scan_networks, list_wifi_interfaces, get_network_info, get_scan_status
from .attacks import (deauth_attack, capture_handshake, perform_evil_twin, capture_credentials,
                     perform_wps_attack, perform_fragmentation_attack, stop_attack, stop_all_attacks,
                     get_attack_status)

# Configuration
PID_FILE = ".netkrak.pid"
LOG_FILE = "netkrak_activity.jsonlog"
CONFIG_FILE = ".netkrak_config.json"

class NetKrakOrchestrator:
    """Enhanced orchestrator with better process management and safety measures"""
    
    def __init__(self):
        self.logger = None
        self.running = True
        self.active_processes = {}
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration from file"""
        config_path = Path(CONFIG_FILE)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[WARNING] Failed to load config: {e}")
        return {
            "max_scan_time": 300,
            "max_attack_duration": 3600,
            "auto_cleanup": True,
            "log_level": "INFO",
            "safety_checks": True
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"[WARNING] Failed to save config: {e}")
    
    def setup_logging(self):
        """Enhanced logging setup with better formatting"""
        self.logger = logging.getLogger("netkrak")
        self.logger.setLevel(getattr(logging, self.config.get("log_level", "INFO")))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # File handler with JSON formatting
        file_handler = logging.FileHandler(LOG_FILE)
        file_formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler with better formatting
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        return self.logger
    
    def log_event(self, event, **kwargs):
        """Enhanced event logging with structured data"""
        entry = {
            "event": event,
            "user": getpass.getuser(),
            "timestamp": time.time(),
            "pid": os.getpid(),
            **kwargs
        }
        self.logger.info(json.dumps(entry))
    
    def require_root(self):
        """Enhanced root privilege check"""
        if os.geteuid() != 0:
            print("[FATAL] This script must be run as root to access network interfaces.", file=sys.stderr)
            print("[INFO] Please run with: sudo python3 orchestrator.py [command]", file=sys.stderr)
            sys.exit(1)
    
    def load_auth(self, auth_file):
        """Enhanced authorization file loading with validation"""
        try:
            with open(auth_file, "r") as f:
                data = json.load(f)
            
            # Basic validation
            required_fields = ["target", "authorized_by", "date", "signature"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Robust signature verification
            if not self.verify_signature(data, auth_file):
                raise ValueError("Invalid signature in authorization file")
            
            print("[INFO] Authorization file loaded and signature verified successfully.")
            self.log_event("auth_file_loaded", file=auth_file, data=data)
            return data
            
        except FileNotFoundError:
            print(f"[FATAL] Authorization file not found: {auth_file}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"[FATAL] Invalid JSON in authorization file: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[FATAL] Failed to load authorization file: {e}", file=sys.stderr)
            sys.exit(1)
    
    def verify_signature(self, data, auth_file):
        """Robust signature verification using HMAC-SHA256"""
        try:
            # Get the signature from the data
            provided_signature = data.get("signature", "")
            if not provided_signature:
                print("[ERROR] No signature found in authorization file")
                return False
            
            # Create a copy of data without signature for verification
            data_copy = data.copy()
            data_copy.pop("signature", None)
            
            # Create the message to sign (sorted JSON for consistency)
            message = json.dumps(data_copy, sort_keys=True, separators=(',', ':'))
            
            # Get the secret key (in production, this should be from secure storage)
            secret_key = self.get_auth_secret_key()
            
            # Generate expected signature
            expected_signature = hmac.new(
                secret_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures using constant-time comparison
            if hmac.compare_digest(provided_signature, expected_signature):
                print("[INFO] Authorization signature verified successfully")
                return True
            else:
                print("[ERROR] Authorization signature verification failed")
                return False
                
        except Exception as e:
            print(f"[ERROR] Signature verification error: {e}")
            return False
    
    def get_auth_secret_key(self):
        """Get the secret key for signature verification"""
        # In production, this should be loaded from a secure key store
        # For now, we'll use a default key that should be changed
        default_key = "netkrak_auth_secret_key_2024_change_me"
        
        # Try to load from environment variable first
        env_key = os.getenv("NETKRAK_AUTH_SECRET_KEY")
        if env_key:
            return env_key
        
        # Try to load from a secure file
        key_file = os.path.expanduser("~/.netkrak_auth_key")
        try:
            with open(key_file, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"[WARNING] No auth secret key found. Using default key.")
            print(f"[WARNING] For production use, set NETKRAK_AUTH_SECRET_KEY or create {key_file}")
            return default_key
    
    def confirm_target(self, target_bssid, target_ssid, attack_type):
        """Enhanced target confirmation with safety checks"""
        print("\n" + "="*60)
        print("                    ! ! ! WARNING ! ! !")
        print("="*60)
        print("You are about to launch a potentially disruptive network attack.")
        print("Ensure you have explicit, written authorization for this action.")
        print("\nTARGET DETAILS:")
        print(f"    SSID:         {target_ssid}")
        print(f"    BSSID:        {target_bssid}")
        print(f"    ATTACK TYPE:  {attack_type.upper()}")
        print(f"    TIMESTAMP:    {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        # Enhanced confirmation
        confirm = input(f"To proceed, type the target BSSID ({target_bssid}) again: ").strip()
        if confirm != target_bssid:
            print("\n[ABORTED] Confirmation failed. BSSID did not match. Exiting.")
            self.log_event("attack_aborted", reason="BSSID confirmation failed")
            sys.exit(1)
        
        # Additional safety check
        safety_confirm = input("Type 'I UNDERSTAND THE RISKS' to confirm: ").strip()
        if safety_confirm != "I UNDERSTAND THE RISKS":
            print("\n[ABORTED] Safety confirmation failed. Exiting.")
            self.log_event("attack_aborted", reason="Safety confirmation failed")
            sys.exit(1)
        
        print("[CONFIRMED] Target confirmed. Proceeding with attack.")
        self.log_event("target_confirmed", bssid=target_bssid, ssid=target_ssid, attack_type=attack_type)
    
    def write_pid(self):
        """Write process ID to file"""
        try:
            with open(PID_FILE, "w") as f:
                f.write(str(os.getpid()))
        except Exception as e:
            print(f"[WARNING] Failed to write PID file: {e}")
    
    def cleanup_pid(self):
        """Clean up PID file"""
        if os.path.exists(PID_FILE):
            try:
                os.remove(PID_FILE)
            except OSError:
                pass
    
    def cleanup_processes(self):
        """Clean up all active processes"""
        try:
            stop_all_attacks(logger=self.logger)
            self.log_event("processes_cleaned")
        except Exception as e:
            self.logger.error(f"Error cleaning up processes: {e}")
    
    def handle_signal(self, signum, frame):
        """Enhanced signal handling"""
        signal_name = signal.Signals(signum).name
        print(f"\n[!] Signal {signal_name} received. Shutting down gracefully...")
        self.log_event("signal_received", signal=signal_name)
        
        self.running = False
        self.cleanup_processes()
        self.cleanup_pid()
        sys.exit(0)
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGHUP, self.handle_signal)
    
    def validate_attack_params(self, args):
        """Validate attack parameters"""
        errors = []
        
        if not args.bssid:
            errors.append("BSSID is required")
        elif not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', args.bssid):
            errors.append("Invalid BSSID format")
        
        if not args.ssid:
            errors.append("SSID is required")
        elif len(args.ssid) > 32:
            errors.append("SSID too long (max 32 characters)")
        
        if args.channel and not (1 <= args.channel <= 165):
            errors.append("Invalid channel (must be 1-165)")
        
        if args.scan_time and not (1 <= args.scan_time <= self.config["max_scan_time"]):
            errors.append(f"Scan time too long (max {self.config['max_scan_time']} seconds)")
        
        return errors
    
    def run_scan(self, args):
        """Enhanced network scanning"""
        try:
            print(f"[INFO] Scanning for networks on {args.interface} using {args.scanner} for {args.scan_time} seconds...")
            self.log_event("scan_start", interface=args.interface, scanner=args.scanner, scan_time=args.scan_time)
            
            networks = scan_networks(
                args.interface, 
                method=args.scanner, 
                scan_time=args.scan_time, 
                logger=self.logger
            )
            
            if networks:
                print(f"\n[SUCCESS] Found {len(networks)} networks:")
                print(json.dumps(networks, indent=2))
            else:
                print("[WARNING] No networks found. Check interface name and ensure it is in monitor mode.")
            
            self.log_event("scan_complete", networks_found=len(networks))
            return networks
            
        except Exception as e:
            print(f"[ERROR] Scan failed: {e}")
            self.log_event("scan_error", error=str(e))
            return []
    
    def run_attack(self, args):
        """Enhanced attack execution"""
        try:
            # Validate parameters
            errors = self.validate_attack_params(args)
            if errors:
                for error in errors:
                    print(f"[ERROR] {error}")
                sys.exit(1)
            
            # Authorization check for real attacks
            if not args.dry_run:
                if not args.authorized:
                    print("[FATAL] --authorized flag is required for all real attacks.", file=sys.stderr)
                    self.log_event("attack_aborted", reason="Missing --authorized flag")
                    sys.exit(1)
                
                if args.auth_file:
                    auth_data = self.load_auth(args.auth_file)
                
                if not args.force:
                    self.confirm_target(args.bssid, args.ssid, args.attack_type)
            
            print(f"[INFO] Preparing '{args.attack_type}' attack on {args.ssid} ({args.bssid}) via {args.interface}")
            self.log_event("attack_start", bssid=args.bssid, ssid=args.ssid, type=args.attack_type)
            
            # Execute attack
            result = None
            if args.attack_type == "deauth":
                result = deauth_attack(args.interface, args.bssid, dry_run=args.dry_run, logger=self.logger)
            elif args.attack_type == "handshake":
                if not args.channel:
                    print("[FATAL] --channel is required for handshake capture.", file=sys.stderr)
                    sys.exit(1)
                result = capture_handshake(args.interface, args.bssid, args.channel, dry_run=args.dry_run, logger=self.logger)
            elif args.attack_type == "evil_twin":
                result = perform_evil_twin(args.interface, args.bssid, args.ssid, dry_run=args.dry_run, logger=self.logger)
            elif args.attack_type == "credential":
                if not args.channel:
                    print("[FATAL] --channel is required for credential capture.", file=sys.stderr)
                    sys.exit(1)
                result = capture_credentials(args.interface, args.bssid, args.channel, dry_run=args.dry_run, logger=self.logger)
            elif args.attack_type == "wps":
                result = perform_wps_attack(args.interface, args.bssid, dry_run=args.dry_run, logger=self.logger)
            elif args.attack_type == "fragmentation":
                result = perform_fragmentation_attack(args.interface, args.bssid, dry_run=args.dry_run, logger=self.logger)
            
            if result:
                print(f"[SUCCESS] {args.attack_type} attack {'simulated' if args.dry_run else 'started'} successfully")
                self.log_event("attack_success", attack_type=args.attack_type, result=str(result))
            else:
                print(f"[ERROR] {args.attack_type} attack failed")
                self.log_event("attack_failed", attack_type=args.attack_type)
            
        except Exception as e:
            print(f"[ERROR] Attack execution failed: {e}")
            self.log_event("attack_error", error=str(e))
            sys.exit(1)
    
    def run_list_interfaces(self, args):
        """List available WiFi interfaces"""
        try:
            interfaces = list_wifi_interfaces(logger=self.logger)
            if interfaces:
                print("Available wireless interfaces:")
                for iface in interfaces:
                    print(f"  - {iface}")
            else:
                print("No wireless interfaces found. Ensure drivers are installed and `iwconfig` is available.")
            
            self.log_event("interfaces_listed", count=len(interfaces))
            
        except Exception as e:
            print(f"[ERROR] Failed to list interfaces: {e}")
            self.log_event("interface_list_error", error=str(e))
            sys.exit(1)
    
    def run_status(self, args):
        """Show system status"""
        try:
            print("[INFO] NetKrak System Status")
            print("=" * 40)
            
            # Scan status
            scan_status = get_scan_status()
            print(f"Scan Status: {'Active' if scan_status['active'] else 'Idle'}")
            print(f"Networks Found: {scan_status['networks_found']}")
            print(f"Clients Found: {scan_status['clients_found']}")
            
            # Attack status
            attack_status = get_attack_status()
            print(f"Active Attacks: {len(attack_status)}")
            for pid, info in attack_status.items():
                print(f"  - PID {pid}: {info.get('command', 'Unknown')}")
            
            # System info
            print(f"Uptime: {time.time() - self.start_time:.2f} seconds")
            print(f"Log File: {LOG_FILE}")
            
            self.log_event("status_requested")
            
        except Exception as e:
            print(f"[ERROR] Failed to get status: {e}")
            self.log_event("status_error", error=str(e))
    
    def run_cleanup(self, args):
        """Clean up all processes and temporary files"""
        try:
            print("[INFO] Cleaning up all processes...")
            self.cleanup_processes()
            self.cleanup_pid()
            print("[SUCCESS] Cleanup completed")
            self.log_event("cleanup_completed")
            
        except Exception as e:
            print(f"[ERROR] Cleanup failed: {e}")
            self.log_event("cleanup_error", error=str(e))
            sys.exit(1)
    
    def run_diagnostics(self, args):
        """Run comprehensive system diagnostics"""
        try:
            # Import diagnostics module
            from .utils.runtime_diagnostics import RuntimeDiagnostics
            
            diagnostics_engine = RuntimeDiagnostics()
            diagnostics = diagnostics_engine.run_comprehensive_diagnostics()
            
            if args.json:
                # Output in JSON format
                print(json.dumps(diagnostics, indent=2))
            elif args.docker_command:
                # Generate Docker command
                print("🐳 OPTIMAL DOCKER RUN COMMAND:")
                print(diagnostics_engine.get_docker_run_command(diagnostics))
            else:
                # Print formatted diagnostics
                diagnostics_engine.print_diagnostics(diagnostics)
            
            self.log_event("diagnostics_run", format=args.json and "json" or "formatted")
            
        except ImportError as e:
            print(f"[ERROR] Could not import diagnostics module: {e}")
            print("[INFO] Make sure utils/runtime_diagnostics.py exists")
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Diagnostics failed: {e}")
            self.log_event("diagnostics_error", error=str(e))
            sys.exit(1)
    
    def main(self):
        """Main orchestrator function"""
        self.require_root()
        self.setup_logging()
        self.setup_signal_handlers()
        self.start_time = time.time()
        
        self.log_event("session_start", version="2.0.0")
        self.write_pid()
        
        parser = argparse.ArgumentParser(
            description="net.krak WiFi Pentest Suite Orchestrator v2.0",
            formatter_class=argparse.RawTextHelpFormatter
        )
        
        # Global arguments
        parser.add_argument("--dry-run", action="store_true", 
                          help="Simulate actions without sending packets or running tools.")
        parser.add_argument("--config", type=str, 
                          help="Path to configuration file")
        parser.add_argument("--verbose", "-v", action="store_true", 
                          help="Enable verbose logging")
        
        subparsers = parser.add_subparsers(dest="command", required=True)
        
        # List interfaces command
        list_parser = subparsers.add_parser("list-interfaces", 
                                          help="List available wireless network interfaces.")
        
        # Scan command
        scan_parser = subparsers.add_parser("scan", help="Scan for WiFi networks.")
        scan_parser.add_argument("interface", type=str, 
                               help="WiFi interface to use for scanning (must be in monitor mode).")
        scan_parser.add_argument("--scanner", choices=["airodump", "scapy"], default="scapy", 
                               help="The scanning tool to use (default: scapy).")
        scan_parser.add_argument("--scan-time", type=int, default=15, 
                               help="Seconds to scan for networks (default: 15).")
        
        # Attack command
        attack_parser = subparsers.add_parser("attack", help="Run an attack on a target.")
        attack_parser.add_argument("interface", type=str, 
                                 help="WiFi interface to use for the attack (must be in monitor mode).")
        attack_parser.add_argument("--bssid", required=True, 
                                 help="BSSID of the target access point.")
        attack_parser.add_argument("--ssid", required=True, 
                                 help="SSID of the target access point.")
        attack_parser.add_argument("--channel", type=int, 
                                 help="Channel of the target access point (required for some attacks).")
        attack_parser.add_argument("--attack-type", 
                                 choices=["deauth", "handshake", "evil_twin", "credential", "wps", "fragmentation"], 
                                 required=True)
        attack_parser.add_argument("--authorized", action="store_true", 
                                 help="Flag to acknowledge authorization to test the target.")
        attack_parser.add_argument("--auth-file", type=str, 
                                 help="Path to a signed authorization JSON file (optional).")
        attack_parser.add_argument("--force", action="store_true", 
                                 help="Force attack without interactive confirmation (requires --authorized).")
        
        # Status command
        status_parser = subparsers.add_parser("status", help="Show system status.")
        
        # Cleanup command
        cleanup_parser = subparsers.add_parser("cleanup", help="Clean up all processes and temporary files.")
        
        # Diagnostics command
        diag_parser = subparsers.add_parser("diagnostics", help="Run comprehensive system diagnostics.")
        diag_parser.add_argument("--json", action="store_true", 
                               help="Output diagnostics in JSON format.")
        diag_parser.add_argument("--docker-command", action="store_true",
                               help="Generate optimal Docker run command.")
        
        args = parser.parse_args()
        
        # Load config if specified
        if args.config:
            try:
                with open(args.config, 'r') as f:
                    self.config.update(json.load(f))
                self.save_config()
            except Exception as e:
                print(f"[WARNING] Failed to load config file: {e}")
        
        # Set verbose logging
        if args.verbose:
            self.logger.setLevel(logging.DEBUG)
        
        try:
            # Execute command
            if args.command == "list-interfaces":
                self.run_list_interfaces(args)
            elif args.command == "scan":
                self.run_scan(args)
            elif args.command == "attack":
                self.run_attack(args)
            elif args.command == "status":
                self.run_status(args)
            elif args.command == "cleanup":
                self.run_cleanup(args)
            elif args.command == "diagnostics":
                self.run_diagnostics(args)
            
        except KeyboardInterrupt:
            print("\n[!] Interrupted by user")
            self.log_event("interrupted_by_user")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            self.log_event("unexpected_error", error=str(e))
            sys.exit(1)
        finally:
            self.cleanup_pid()
            self.log_event("session_stop")

# Import re for validation
import re

if __name__ == "__main__":
    orchestrator = NetKrakOrchestrator()
    orchestrator.main()