#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Network information providers for OLED display.

This module provides information about network interfaces,
hostname, IP addresses, etc. for display on the OLED screen.
"""

import os
import socket
import subprocess
import logging
from typing import Dict, List, Optional, Callable, Any, Union
import psutil

# Type alias for network info providers
InfoProvider = Callable[[], str]


def get_hostname() -> str:
    """
    Get the system hostname.
    
    Returns:
        System hostname
    """
    try:
        return socket.gethostname()
    except Exception as e:
        logging.error(f"Error getting hostname: {e}")
        return "unknown"


def get_ip_address(interface: Optional[str] = None) -> str:
    """
    Get the IP address for the specified interface.
    
    If no interface is specified, the primary interface will be used.
    
    Args:
        interface: Network interface name (e.g., 'eth0', 'wlan0')
        
    Returns:
        IP address as a string, or empty string if not available
    """
    try:
        # If interface is not specified, find primary interface
        if not interface:
            # Find the interface with a default route
            stats = psutil.net_if_stats()
            interfaces = []
            
            # Check all network interfaces
            for iface, addrs in psutil.net_if_addrs().items():
                if iface in stats and stats[iface].isup:
                    for addr in addrs:
                        if addr.family == socket.AF_INET:  # IPv4
                            interfaces.append(iface)
                            break
            
            # Prefer ethernet over wireless
            if 'eth0' in interfaces:
                interface = 'eth0'
            elif 'enp0s3' in interfaces:  # Common for VMs
                interface = 'enp0s3'
            elif 'wlan0' in interfaces:
                interface = 'wlan0'
            elif interfaces:
                interface = interfaces[0]
            else:
                return ""
        
        # Get IP for the specified interface
        addrs = psutil.net_if_addrs().get(interface, [])
        for addr in addrs:
            if addr.family == socket.AF_INET:  # IPv4
                return addr.address
        
        return ""
    
    except Exception as e:
        logging.error(f"Error getting IP address for {interface}: {e}")
        return ""


def get_external_ip() -> str:
    """
    Get the external (public) IP address.
    
    Returns:
        External IP address as a string, or empty string if not available
    """
    try:
        # Try several services to get external IP
        services = [
            'http://ifconfig.me/ip',
            'http://api.ipify.org',
            'http://ipinfo.io/ip'
        ]
        
        for service in services:
            try:
                result = subprocess.run(
                    ['curl', '-s', service],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=2
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except subprocess.TimeoutExpired:
                continue
        
        return ""
    
    except Exception as e:
        logging.error(f"Error getting external IP: {e}")
        return ""


def get_network_interfaces() -> List[Dict[str, Any]]:
    """
    Get information about all network interfaces.
    
    Returns:
        List of dictionaries with interface information
    """
    interfaces = []
    
    try:
        stats = psutil.net_if_stats()
        
        for iface, addrs in psutil.net_if_addrs().items():
            if iface in stats and stats[iface].isup:
                interface_info = {
                    'name': iface,
                    'ipv4': '',
                    'ipv6': '',
                    'mac': ''
                }
                
                for addr in addrs:
                    if addr.family == socket.AF_INET:  # IPv4
                        interface_info['ipv4'] = addr.address
                    elif addr.family == socket.AF_INET6:  # IPv6
                        interface_info['ipv6'] = addr.address
                    elif addr.family == psutil.AF_LINK:  # MAC
                        interface_info['mac'] = addr.address
                
                interfaces.append(interface_info)
    
    except Exception as e:
        logging.error(f"Error getting network interfaces: {e}")
    
    return interfaces


def get_primary_interface() -> Optional[str]:
    """
    Get the name of the primary network interface.
    
    Returns:
        Name of the primary interface, or None if not available
    """
    try:
        # Try to find interface with default route
        interfaces = get_network_interfaces()
        
        # Prefer ethernet over wireless
        for iface in interfaces:
            if iface['name'].startswith('eth'):
                return iface['name']
        
        # Then try wireless
        for iface in interfaces:
            if iface['name'].startswith('wlan'):
                return iface['name']
        
        # Otherwise, take first available
        if interfaces:
            return interfaces[0]['name']
        
        return None
    
    except Exception as e:
        logging.error(f"Error getting primary interface: {e}")
        return None


def get_network_info_provider(info_type: str, **kwargs) -> InfoProvider:
    """
    Get a provider function for the specified network information.
    
    Args:
        info_type: Type of network information
        **kwargs: Additional arguments for the provider
        
    Returns:
        Function that returns the network information
        
    Raises:
        ValueError: If the info type is not recognized
    """
    info_types = {
        'hostname': get_hostname,
        'ip_address': lambda: get_ip_address(kwargs.get('interface')),
        'external_ip': get_external_ip,
    }
    
    if info_type not in info_types:
        raise ValueError(f"Unknown network info type: {info_type}")
    
    return info_types[info_type]
