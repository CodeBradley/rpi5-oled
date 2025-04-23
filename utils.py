"""
Utility functions for the Raspberry Pi 5 OLED display application.
"""
import socket
import subprocess
import time
from datetime import timedelta


def get_ip_address(interface='wlan0'):
    """Get the IP address for a specific network interface."""
    try:
        cmd = f"ip addr show {interface} | grep 'inet ' | awk '{{print $2}}' | cut -d/ -f1"
        ip = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        return ip if ip else "No IP"
    except Exception:
        return "No IP"


def get_hostname():
    """Get the system hostname."""
    try:
        return socket.gethostname()
    except Exception:
        return "Unknown"


def get_uptime():
    """Get the system uptime in a human-readable format."""
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
        
        # Convert to timedelta for easier formatting
        uptime = timedelta(seconds=uptime_seconds)
        
        # Format based on duration
        if uptime.days > 0:
            return f"{uptime.days}d {uptime.seconds // 3600}h"
        elif uptime.seconds // 3600 > 0:
            return f"{uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m"
        else:
            return f"{uptime.seconds // 60}m"
    except Exception:
        return "Unknown"


def check_service_status(service_name):
    """Check if a systemd service is active."""
    try:
        cmd = f"systemctl is-active {service_name}"
        status = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        return status == "active"
    except Exception:
        return False


def check_docker_status():
    """Check if Docker is running."""
    try:
        cmd = "systemctl is-active docker"
        status = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        return status == "active"
    except Exception:
        return False
