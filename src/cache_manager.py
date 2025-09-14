#!/usr/bin/env python3
"""
Cache Manager for NET.KRAK
Provides intelligent caching for API responses and network data
"""

import time
import json
import threading
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Intelligent caching system for network data and API responses"""
    
    def __init__(self, default_ttl=300):  # 5 minutes default TTL
        self.cache = {}
        self.ttl = {}
        self.default_ttl = default_ttl
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_requests': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self.lock:
            self.stats['total_requests'] += 1
            
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            # Check if expired
            if time.time() > self.ttl.get(key, 0):
                del self.cache[key]
                del self.ttl[key]
                self.stats['evictions'] += 1
                self.stats['misses'] += 1
                return None
            
            self.stats['hits'] += 1
            return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        with self.lock:
            self.cache[key] = value
            self.ttl[key] = time.time() + (ttl or self.default_ttl)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                del self.ttl[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache"""
        with self.lock:
            self.cache.clear()
            self.ttl.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        with self.lock:
            current_time = time.time()
            expired_keys = [k for k, v in self.ttl.items() if current_time > v]
            
            for key in expired_keys:
                del self.cache[key]
                del self.ttl[key]
                self.stats['evictions'] += 1
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            hit_rate = (self.stats['hits'] / max(self.stats['total_requests'], 1)) * 100
            return {
                **self.stats,
                'hit_rate': round(hit_rate, 2),
                'current_size': len(self.cache),
                'memory_usage': sum(len(str(v)) for v in self.cache.values())
            }
    
    def get_network_cache_key(self, interface: str, scan_type: str = 'full') -> str:
        """Generate cache key for network data"""
        return f"network_scan:{interface}:{scan_type}"
    
    def get_interface_cache_key(self) -> str:
        """Generate cache key for interface data"""
        return "interfaces:all"
    
    def get_attack_cache_key(self, attack_type: str, target: str) -> str:
        """Generate cache key for attack data"""
        return f"attack:{attack_type}:{target}"

# Global cache instance
cache_manager = CacheManager()