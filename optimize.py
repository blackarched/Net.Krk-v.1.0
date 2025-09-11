#!/usr/bin/env python3
"""
optimize.py - Performance optimization and system tuning for net.krak
"""
import os
import sys
import time
try:
    import psutil
except ImportError:
    psutil = None
import subprocess
import logging
from pathlib import Path

class NetKrakOptimizer:
    """Performance optimizer for net.krak"""
    
    def __init__(self):
        self.logger = logging.getLogger("netkrak.optimizer")
        self.optimizations_applied = []
    
    def check_system_requirements(self):
        """Check if system meets requirements"""
        if psutil:
            requirements = {
                "python_version": sys.version_info >= (3, 7),
                "memory_gb": psutil.virtual_memory().total >= 2 * 1024**3,  # 2GB
                "disk_space_gb": psutil.disk_usage('/').free >= 1 * 1024**3,  # 1GB
                "cpu_cores": psutil.cpu_count() >= 2
            }
        else:
            requirements = {
                "python_version": sys.version_info >= (3, 7),
                "memory_gb": True,  # Skip check if psutil not available
                "disk_space_gb": True,  # Skip check if psutil not available
                "cpu_cores": True  # Skip check if psutil not available
            }
        
        self.logger.info(f"System requirements check: {requirements}")
        return all(requirements.values())
    
    def optimize_network_interfaces(self):
        """Optimize network interface settings"""
        try:
            # Check for wireless interfaces
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            if result.returncode == 0:
                interfaces = []
                for line in result.stdout.split('\n'):
                    if 'IEEE 802.11' in line:
                        iface = line.split()[0]
                        interfaces.append(iface)
                
                self.logger.info(f"Found wireless interfaces: {interfaces}")
                
                # Optimize each interface
                for iface in interfaces:
                    self._optimize_interface(iface)
                
                self.optimizations_applied.append("network_interfaces")
                return True
        except Exception as e:
            self.logger.error(f"Error optimizing network interfaces: {e}")
            return False
    
    def _optimize_interface(self, interface):
        """Optimize a specific network interface"""
        try:
            # Set power management off
            subprocess.run(['iwconfig', interface, 'power', 'off'], 
                         capture_output=True, check=False)
            
            # Set RTS threshold
            subprocess.run(['iwconfig', interface, 'rts', 'off'], 
                         capture_output=True, check=False)
            
            # Set fragmentation threshold
            subprocess.run(['iwconfig', interface, 'frag', 'off'], 
                         capture_output=True, check=False)
            
            self.logger.info(f"Optimized interface {interface}")
        except Exception as e:
            self.logger.warning(f"Could not optimize interface {interface}: {e}")
    
    def optimize_system_limits(self):
        """Optimize system limits for better performance"""
        try:
            # Increase file descriptor limits
            import resource
            soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
            if soft < 65536:
                resource.setrlimit(resource.RLIMIT_NOFILE, (65536, hard))
                self.logger.info("Increased file descriptor limit")
            
            # Set process priority
            os.nice(-5)  # Higher priority
            self.logger.info("Set higher process priority")
            
            self.optimizations_applied.append("system_limits")
            return True
        except Exception as e:
            self.logger.error(f"Error optimizing system limits: {e}")
            return False
    
    def optimize_memory_usage(self):
        """Optimize memory usage"""
        try:
            # Set garbage collection thresholds
            import gc
            gc.set_threshold(700, 10, 10)
            
            # Force garbage collection
            gc.collect()
            
            self.logger.info("Optimized memory usage")
            self.optimizations_applied.append("memory_usage")
            return True
        except Exception as e:
            self.logger.error(f"Error optimizing memory usage: {e}")
            return False
    
    def create_optimized_config(self):
        """Create optimized configuration file"""
        config = {
            "performance": {
                "max_scan_time": 30,
                "max_attack_duration": 600,
                "packet_buffer_size": 65536,
                "thread_pool_size": 4,
                "memory_limit_mb": 512
            },
            "network": {
                "interface_timeout": 5,
                "packet_timeout": 1,
                "retry_attempts": 3
            },
            "logging": {
                "level": "INFO",
                "max_file_size_mb": 10,
                "backup_count": 5
            }
        }
        
        config_path = Path(".netkrak_optimized.json")
        try:
            import json
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info(f"Created optimized config: {config_path}")
            self.optimizations_applied.append("config_file")
            return True
        except Exception as e:
            self.logger.error(f"Error creating config file: {e}")
            return False
    
    def benchmark_performance(self):
        """Benchmark system performance"""
        benchmarks = {}
        
        # CPU benchmark
        start_time = time.time()
        sum(range(1000000))
        benchmarks["cpu_time"] = time.time() - start_time
        
        # Memory benchmark
        if psutil:
            memory_before = psutil.virtual_memory().used
            test_data = [0] * 100000
            memory_after = psutil.virtual_memory().used
            benchmarks["memory_usage_mb"] = (memory_after - memory_before) / 1024 / 1024
        else:
            test_data = [0] * 100000
            benchmarks["memory_usage_mb"] = "psutil not available"
        
        # Disk benchmark
        test_file = Path("test_benchmark.tmp")
        start_time = time.time()
        with open(test_file, 'w') as f:
            f.write("x" * 1024 * 1024)  # 1MB
        benchmarks["disk_write_time"] = time.time() - start_time
        test_file.unlink()
        
        self.logger.info(f"Performance benchmarks: {benchmarks}")
        return benchmarks
    
    def run_full_optimization(self):
        """Run all optimizations"""
        self.logger.info("Starting net.krak optimization...")
        
        # Check system requirements
        if not self.check_system_requirements():
            self.logger.warning("System does not meet minimum requirements")
        
        # Run optimizations
        optimizations = [
            self.optimize_network_interfaces,
            self.optimize_system_limits,
            self.optimize_memory_usage,
            self.create_optimized_config
        ]
        
        for optimization in optimizations:
            try:
                optimization()
            except Exception as e:
                self.logger.error(f"Optimization failed: {e}")
        
        # Run benchmarks
        benchmarks = self.benchmark_performance()
        
        # Summary
        self.logger.info(f"Optimization complete. Applied: {self.optimizations_applied}")
        return {
            "optimizations_applied": self.optimizations_applied,
            "benchmarks": benchmarks
        }

def main():
    """Main optimization function"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    optimizer = NetKrakOptimizer()
    result = optimizer.run_full_optimization()
    
    print("NetKrak Optimization Complete!")
    print(f"Applied optimizations: {', '.join(result['optimizations_applied'])}")
    print(f"Performance benchmarks: {result['benchmarks']}")

if __name__ == "__main__":
    main()