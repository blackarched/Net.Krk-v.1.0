"""
orchestrator.py - Main CLI, process management, logging, and legal/safety guards for net.krak
"""
import os
import sys
import argparse
import json
import logging
import getpass
import signal
import time
from pathlib import Path
from scanner import scan_networks, list_wifi_interfaces
from attacks import deauth_attack, capture_handshake, perform_evil_twin, capture_credentials

PID_FILE = ".netkrak.pid"
LOG_FILE = "netkrak_activity.jsonlog"

# --- Safety & Legal Guards ---
def require_root():
    if os.geteuid() != 0:
        print("[FATAL] This script must be run as root to access network interfaces.", file=sys.stderr)
        sys.exit(1)

def load_auth(auth_file):
    try:
        with open(auth_file, "r") as f:
            data = json.load(f)
        # TODO: Implement robust signature verification logic here
        print("[INFO] Authorization file loaded. Signature verification is currently a placeholder.")
        return data
    except Exception as e:
        print(f"[FATAL] Failed to load or parse authorization file: {e}", file=sys.stderr)
        sys.exit(1)

def confirm_target(target_bssid, target_ssid, attack_type):
    print("\n" + "="*50)
    print("                    ! ! ! WARNING ! ! !")
    print("="*50)
    print("You are about to launch a potentially disruptive network attack.")
    print("Ensure you have explicit, written authorization for this action.")
    print("\nTARGET DETAILS:")
    print(f"    SSID:         {target_ssid}")
    print(f"    BSSID:        {target_bssid}")
    print(f"    ATTACK TYPE:  {attack_type.upper()}")
    print("-" * 50)
    confirm = input(f"To proceed, type the target BSSID ({target_bssid}) again: ").strip()
    if confirm != target_bssid:
        print("\n[ABORTED] Confirmation failed. BSSID did not match. Exiting.")
        sys.exit(1)
    print("[CONFIRMED] Target confirmed. Proceeding with attack.")


def write_pid():
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def cleanup_pid():
    if os.path.exists(PID_FILE):
        try:
            os.remove(PID_FILE)
        except OSError:
            pass # Ignore if it's already gone

def setup_logging():
    logger = logging.getLogger("netkrak")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(LOG_FILE)
    # Use a structured formatter for JSON logs
    formatter = logging.Formatter('{"time": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def log_event(logger, event, **kwargs):
    entry = {"event": event, "user": getpass.getuser(), "timestamp": time.time()}
    entry.update(kwargs)
    # The custom formatter expects a JSON string as the message
    logger.info(json.dumps(entry))

def handle_signal(signum, frame):
    print(f"\n[!] Signal {signal.Signals(signum).name} received. Shutting down gracefully...")
    cleanup_pid()
    sys.exit(0)

def main():
    require_root()
    parser = argparse.ArgumentParser(
        description="net.krak WiFi Pentest Suite Orchestrator.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    # Global arguments
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without sending packets or running tools.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- list-interfaces command ---
    list_parser = subparsers.add_parser("list-interfaces", help="List available wireless network interfaces.")

    # --- scan command ---
    scan_parser = subparsers.add_parser("scan", help="Scan for WiFi networks.")
    scan_parser.add_argument("interface", type=str, help="WiFi interface to use for scanning (must be in monitor mode).")
    scan_parser.add_argument("--scanner", choices=["airodump", "scapy"], default="airodump", help="The scanning tool to use (default: airodump).")
    scan_parser.add_argument("--scan-time", type=int, default=15, help="Seconds to scan for networks (default: 15).")

    # --- attack command ---
    attack_parser = subparsers.add_parser("attack", help="Run an attack on a target.")
    attack_parser.add_argument("interface", type=str, help="WiFi interface to use for the attack (must be in monitor mode).")
    attack_parser.add_argument("--bssid", required=True, help="BSSID of the target access point.")
    attack_parser.add_argument("--ssid", required=True, help="SSID of the target access point.")
    attack_parser.add_argument("--channel", type=int, help="Channel of the target access point (required for some attacks).")
    attack_parser.add_argument("--attack-type", choices=["deauth", "handshake", "evil_twin", "credential"], required=True)
    # Authorization arguments
    attack_parser.add_argument("--authorized", action="store_true", help="Flag to acknowledge authorization to test the target.")
    attack_parser.add_argument("--auth-file", type=str, help="Path to a signed authorization JSON file (optional).")
    attack_parser.add_argument("--force", action="store_true", help="Force attack without interactive confirmation (requires --authorized).")

    args = parser.parse_args()

    logger = setup_logging()
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    log_event(logger, "session_start", args=vars(args))
    write_pid()

    if args.command == "list-interfaces":
        interfaces = list_wifi_interfaces(logger=logger)
        if interfaces:
            print("Available wireless interfaces:")
            for iface in interfaces:
                print(f"  - {iface}")
        else:
            print("No wireless interfaces found. Ensure drivers are installed and `iwconfig` is available.")

    elif args.command == "scan":
        print(f"[INFO] Scanning for networks on {args.interface} using {args.scanner} for {args.scan_time} seconds...")
        nets = scan_networks(args.interface, method=args.scanner, scan_time=args.scan_time, logger=logger)
        print(json.dumps(nets, indent=2))
        log_event(logger, "scan_complete", networks_found=len(nets))

    elif args.command == "attack":
        # Authorization check for real attacks
        if not args.dry_run:
            if not args.authorized:
                print("[FATAL] --authorized flag is required for all real attacks.", file=sys.stderr)
                log_event(logger, "attack_aborted", reason="Missing --authorized flag")
                cleanup_pid()
                sys.exit(1)
            if args.auth_file:
                auth_data = load_auth(args.auth_file)
                log_event(logger, "auth_file_loaded", file=args.auth_file, data=auth_data)
            if not args.force:
                confirm_target(args.bssid, args.ssid, args.attack_type)

        print(f"[INFO] Preparing '{args.attack_type}' attack on {args.ssid} ({args.bssid}) via {args.interface}")
        log_event(logger, "attack_start", bssid=args.bssid, ssid=args.ssid, type=args.attack_type)

        if args.attack_type == "deauth":
            deauth_attack(args.interface, args.bssid, dry_run=args.dry_run, logger=logger)
        elif args.attack_type == "handshake":
            if not args.channel:
                print("[FATAL] --channel is required for handshake capture.", file=sys.stderr)
                sys.exit(1)
            capture_handshake(args.interface, args.bssid, args.channel, dry_run=args.dry_run, logger=logger)
        elif args.attack_type == "evil_twin":
            perform_evil_twin(args.interface, args.bssid, args.ssid, dry_run=args.dry_run, logger=logger)
        elif args.attack_type == "credential":
            if not args.channel:
                print("[FATAL] --channel is required for credential capture.", file=sys.stderr)
                sys.exit(1)
            capture_credentials(args.interface, args.bssid, args.channel, dry_run=args.dry_run, logger=logger)

    cleanup_pid()
    log_event(logger, "session_stop")

if __name__ == "__main__":
    main()
