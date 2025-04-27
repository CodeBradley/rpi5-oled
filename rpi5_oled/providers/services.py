#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service status providers for OLED display.

This module checks the status of various services like Docker,
CephFS, etc. for display on the OLED screen.
"""

import os
import re
import socket
import subprocess
import logging
from typing import Callable, Dict, Any, Optional, Union, List
import shutil

# Type alias for service status providers
StatusProvider = Callable[[], bool]


def is_service_running(service_name: str) -> bool:
    """
    Check if a systemd service is running.
    
    Args:
        service_name: Name of the systemd service
        
    Returns:
        True if the service is running, False otherwise
    """
    try:
        # Use systemctl to check service status
        result = subprocess.run(
            ['systemctl', 'is-active', service_name],
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout.strip() == 'active'
    except Exception as e:
        logging.error(f"Error checking service {service_name}: {e}")
        return False


def is_docker_running() -> bool:
    """
    Check if Docker is running.
    
    Returns:
        True if Docker is running, False otherwise
    """
    try:
        # First, check if docker command exists
        if not shutil.which('docker'):
            return False
        
        # Try to run 'docker info' to check if Docker daemon is running
        result = subprocess.run(
            ['docker', 'info'],
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except Exception as e:
        logging.error(f"Error checking Docker: {e}")
        return False


def is_ceph_running() -> bool:
    """
    Check if CephFS is running and mounted.
    
    Returns:
        True if CephFS is running and mounted, False otherwise
    """
    try:
        # Check if ceph command exists
        if shutil.which('ceph'):
            # Try to get Ceph status
            result = subprocess.run(
                ['ceph', 'status'],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                return True
        
        # Alternative: check if any Ceph filesystems are mounted
        with open('/proc/mounts', 'r') as f:
            mounts = f.read()
            return 'ceph' in mounts or 'cephfs' in mounts
    except Exception as e:
        logging.error(f"Error checking CephFS: {e}")
        return False


def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """
    Check if a port is open on the specified host.
    
    Args:
        host: Hostname or IP address
        port: Port number
        timeout: Timeout in seconds
        
    Returns:
        True if the port is open, False otherwise
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        logging.error(f"Error checking port {port} on {host}: {e}")
        return False


def is_process_running(process_name: str) -> bool:
    """
    Check if a process is running.
    
    Args:
        process_name: Name of the process
        
    Returns:
        True if the process is running, False otherwise
    """
    try:
        # Use ps to find processes matching the name
        result = subprocess.run(
            ['pgrep', '-f', process_name],
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except Exception as e:
        logging.error(f"Error checking process {process_name}: {e}")
        return False


def get_service_provider(service_name: str, **kwargs) -> StatusProvider:
    """
    Get a provider function for the specified service.
    
    Args:
        service_name: Name of the service
        **kwargs: Additional arguments for the provider
        
    Returns:
        Function that returns the service status
        
    Raises:
        ValueError: If the service name is not recognized
    """
    services = {
        'docker': is_docker_running,
        'ceph': is_ceph_running,
        'systemd': lambda: is_service_running(kwargs.get('unit_name', service_name)),
        'port': lambda: is_port_open(
            kwargs.get('host', 'localhost'),
            kwargs.get('port', 80),
            kwargs.get('timeout', 1.0)
        ),
        'process': lambda: is_process_running(kwargs.get('process_name', service_name)),
    }
    
    # Handle common services directly
    if service_name.lower() in ['docker', 'ceph', 'cephfs']:
        return services.get(service_name.lower(), services['systemd'])
    
    # For other services, default to checking systemd service
    provider_type = kwargs.get('provider_type', 'systemd')
    if provider_type not in services:
        raise ValueError(f"Unknown service provider type: {provider_type}")
    
    return services[provider_type]
