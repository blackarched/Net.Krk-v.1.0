"""
logger_config.py - Enhanced logging configuration for net.krak
"""
import logging
import os
import getpass
import time
import json
from pathlib import Path

def setup_logging():
    """
    Sets up a JSON logger that writes to a configurable file path.
    The path is determined by the NETKRAK_LOG_FILE environment variable.
    Defaults to 'logs/netkrak.jsonlog' in the project root.
    """
    log_file_path = os.environ.get("NETKRAK_LOG_FILE")
    if not log_file_path:
        # Default to a 'logs' directory in the project root
        project_root = Path(__file__).parent
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file_path = log_dir / "netkrak.jsonlog"

    logger = logging.getLogger("netkrak")
    logger.setLevel(logging.INFO)

    # Prevent adding multiple handlers if called more than once
    if not logger.handlers:
        handler = logging.FileHandler(log_file_path)
        # Use a formatter that just passes the message through, as we format it to JSON ourselves
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(handler)

    return logger

def log_event(logger, event, **kwargs):
    """
    Logs an event as a JSON string.
    """
    entry = {"event": event, "user": getpass.getuser(), "time": time.time()}
    entry.update(kwargs)
    logger.info(json.dumps(entry))