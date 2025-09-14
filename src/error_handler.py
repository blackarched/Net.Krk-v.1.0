#!/usr/bin/env python3
"""
Centralized Error Handler for NET.KRAK
Provides comprehensive error handling, logging, and user feedback
"""

import logging
import traceback
import sys
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import json

class ErrorHandler:
    """Centralized error handling and logging system"""
    
    def __init__(self, logger_name: str = "net_krak"):
        self.logger = logging.getLogger(logger_name)
        self.error_counts = {}
        self.error_history = []
        self.max_history = 1000
        
    def handle_error(self, error: Exception, context: str = "", 
                    user_message: str = "", log_level: int = logging.ERROR) -> Dict[str, Any]:
        """Handle and log errors with context"""
        
        error_type = type(error).__name__
        error_msg = str(error)
        
        # Update error counts
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Create error record
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': error_msg,
            'context': context,
            'user_message': user_message,
            'traceback': traceback.format_exc()
        }
        
        # Add to history
        self.error_history.append(error_record)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
        
        # Log the error
        self.logger.log(log_level, f"[{context}] {error_type}: {error_msg}")
        if log_level >= logging.ERROR:
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
        
        # Return user-friendly response
        return {
            'success': False,
            'error': error_type,
            'message': user_message or f"An error occurred: {error_msg}",
            'context': context,
            'timestamp': error_record['timestamp']
        }
    
    def handle_network_error(self, error: Exception, interface: str = "") -> Dict[str, Any]:
        """Handle network-specific errors"""
        context = f"Network operation on {interface}" if interface else "Network operation"
        
        if "Permission denied" in str(error):
            return self.handle_error(
                error, context, 
                "Permission denied. Please run with appropriate privileges or check interface permissions.",
                logging.WARNING
            )
        elif "No such file or directory" in str(error):
            return self.handle_error(
                error, context,
                "Required tool not found. Please install the necessary network tools.",
                logging.WARNING
            )
        elif "Operation not permitted" in str(error):
            return self.handle_error(
                error, context,
                "Operation not permitted. This may require root privileges or specific capabilities.",
                logging.WARNING
            )
        else:
            return self.handle_error(
                error, context,
                f"Network operation failed: {str(error)}",
                logging.ERROR
            )
    
    def handle_attack_error(self, error: Exception, attack_type: str = "") -> Dict[str, Any]:
        """Handle attack-specific errors"""
        context = f"Attack operation: {attack_type}" if attack_type else "Attack operation"
        
        if "Interface" in str(error) and "not found" in str(error):
            return self.handle_error(
                error, context,
                "Network interface not found. Please check the interface name and ensure it exists.",
                logging.WARNING
            )
        elif "monitor mode" in str(error).lower():
            return self.handle_error(
                error, context,
                "Interface not in monitor mode. Please enable monitor mode for the selected interface.",
                logging.WARNING
            )
        elif "Permission denied" in str(error):
            return self.handle_error(
                error, context,
                "Permission denied for attack operation. This requires root privileges.",
                logging.WARNING
            )
        else:
            return self.handle_error(
                error, context,
                f"Attack operation failed: {str(error)}",
                logging.ERROR
            )
    
    def handle_api_error(self, error: Exception, endpoint: str = "") -> Dict[str, Any]:
        """Handle API-specific errors"""
        context = f"API endpoint: {endpoint}" if endpoint else "API operation"
        
        if "JSON" in str(error):
            return self.handle_error(
                error, context,
                "Invalid JSON data received. Please check the request format.",
                logging.WARNING
            )
        elif "KeyError" in str(error):
            return self.handle_error(
                error, context,
                "Missing required parameter. Please check the request data.",
                logging.WARNING
            )
        else:
            return self.handle_error(
                error, context,
                f"API operation failed: {str(error)}",
                logging.ERROR
            )
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            'total_errors': sum(self.error_counts.values()),
            'error_types': self.error_counts,
            'recent_errors': self.error_history[-10:] if self.error_history else [],
            'most_common_error': max(self.error_counts.items(), key=lambda x: x[1])[0] if self.error_counts else None
        }
    
    def clear_history(self) -> None:
        """Clear error history"""
        self.error_history.clear()
        self.error_counts.clear()

# Global error handler instance
error_handler = ErrorHandler()

# Decorator for automatic error handling
def handle_errors(context: str = "", user_message: str = ""):
    """Decorator for automatic error handling"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return error_handler.handle_error(e, context, user_message)
        return wrapper
    return decorator