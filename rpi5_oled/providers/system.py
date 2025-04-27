#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System metrics providers for OLED display.

This module collects system metrics like CPU usage, memory usage,
temperature, etc. for display on the OLED screen.
"""

import os
import re
import time
import logging
from typing import Optional, Dict, Any, Callable, Union
import psutil

# Type alias for metric providers
MetricProvider = Callable[[], Union[int, float, str]]


def get_cpu_usage() -> int:
    """
    Get the current CPU usage as a percentage.
    
    Returns:
        Integer percentage of CPU usage (0-100)
    """
    try:
        return int(psutil.cpu_percent(interval=0.1))
    except Exception as e:
        logging.error(f"Error getting CPU usage: {e}")
        return 0


def get_memory_usage() -> int:
    """
    Get the current memory usage as a percentage.
    
    Returns:
        Integer percentage of memory usage (0-100)
    """
    try:
        return int(psutil.virtual_memory().percent)
    except Exception as e:
        logging.error(f"Error getting memory usage: {e}")
        return 0


def get_cpu_temperature() -> int:
    """
    Get the current CPU temperature in Celsius.
    
    Returns:
        Integer temperature in Celsius, or 0 if unavailable
    """
    try:
        # Try to get temperature from psutil if available
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if temps:
                # Different systems report temperatures differently
                for name, entries in temps.items():
                    if name in ['cpu_thermal', 'cpu-thermal', 'coretemp']:
                        if entries and len(entries) > 0:
                            return int(entries[0].current)
        
        # Fallback for Raspberry Pi
        if os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                return int(int(f.read().strip()) / 1000)
        
        # No temperature available
        return 0
    
    except Exception as e:
        logging.error(f"Error getting CPU temperature: {e}")
        return 0


def get_disk_usage(mount_point: str = '/') -> int:
    """
    Get the disk usage for the specified mount point as a percentage.
    
    Args:
        mount_point: Mount point to check
        
    Returns:
        Integer percentage of disk usage (0-100)
    """
    try:
        return int(psutil.disk_usage(mount_point).percent)
    except Exception as e:
        logging.error(f"Error getting disk usage for {mount_point}: {e}")
        return 0


def get_load_average() -> float:
    """
    Get the 1-minute load average.
    
    Returns:
        1-minute load average as a float
    """
    try:
        return os.getloadavg()[0]
    except Exception as e:
        logging.error(f"Error getting load average: {e}")
        return 0.0


def get_network_traffic(interface: str = 'eth0') -> Dict[str, float]:
    """
    Get current network traffic for the specified interface.
    
    Args:
        interface: Network interface name
        
    Returns:
        Dictionary with 'tx_kbps' and 'rx_kbps' keys
    """
    try:
        # Get initial counters
        counters = psutil.net_io_counters(pernic=True).get(interface)
        if not counters:
            return {'tx_kbps': 0.0, 'rx_kbps': 0.0}
        
        bytes_sent = counters.bytes_sent
        bytes_recv = counters.bytes_recv
        
        # Wait for a short time
        time.sleep(0.1)
        
        # Get counters again
        counters = psutil.net_io_counters(pernic=True).get(interface)
        if not counters:
            return {'tx_kbps': 0.0, 'rx_kbps': 0.0}
        
        # Calculate KB/s
        tx_kbps = (counters.bytes_sent - bytes_sent) * 8 / 1024 / 0.1
        rx_kbps = (counters.bytes_recv - bytes_recv) * 8 / 1024 / 0.1
        
        return {
            'tx_kbps': round(tx_kbps, 1),
            'rx_kbps': round(rx_kbps, 1)
        }
    
    except Exception as e:
        logging.error(f"Error getting network traffic for {interface}: {e}")
        return {'tx_kbps': 0.0, 'rx_kbps': 0.0}


def get_uptime() -> str:
    """
    Get the system uptime as a formatted string.
    
    Returns:
        Uptime as a string in the format "Xd Xh Xm"
    """
    try:
        uptime_seconds = time.time() - psutil.boot_time()
        days = int(uptime_seconds // (24 * 3600))
        hours = int((uptime_seconds % (24 * 3600)) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}d {hours}h"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    except Exception as e:
        logging.error(f"Error getting uptime: {e}")
        return "?"


def get_metric_provider(metric_name: str, **kwargs) -> MetricProvider:
    """
    Get a provider function for the specified metric.
    
    Args:
        metric_name: Name of the metric
        **kwargs: Additional arguments for the provider
        
    Returns:
        Function that returns the metric value
        
    Raises:
        ValueError: If the metric name is not recognized
    """
    metrics = {
        'cpu_usage': get_cpu_usage,
        'memory_usage': get_memory_usage,
        'cpu_temperature': get_cpu_temperature,
        'disk_usage': lambda: get_disk_usage(kwargs.get('mount_point', '/')),
        'load_average': get_load_average,
        'uptime': get_uptime,
    }
    
    if metric_name not in metrics:
        raise ValueError(f"Unknown metric: {metric_name}")
    
    return metrics[metric_name]
