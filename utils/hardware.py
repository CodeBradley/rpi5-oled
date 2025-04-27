#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hardware utility functions for the OLED display framework.

This module provides functions to check hardware requirements,
verify I2C setup, and test display connectivity.
"""

import os
import re
import logging
import subprocess
from typing import List, Tuple, Optional, Dict, Any, Union

# Default I2C bus number for Raspberry Pi
DEFAULT_I2C_BUS = 1
# Default I2C address for SSD1306 OLED displays
DEFAULT_I2C_ADDRESS = 0x3C


def is_raspberry_pi() -> bool:
    """
    Check if the current system is a Raspberry Pi.
    
    Returns:
        True if the system is a Raspberry Pi, False otherwise
    """
    try:
        # Check for Raspberry Pi model in /proc/cpuinfo
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
        
        return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo or 'Broadcom' in cpuinfo
    
    except Exception:
        # If we can't read /proc/cpuinfo, check if Linux + ARM
        try:
            # Check if running on Linux
            is_linux = os.name == 'posix' and os.uname().sysname == 'Linux'
            
            # Check if running on ARM processor
            is_arm = 'arm' in os.uname().machine.lower()
            
            return is_linux and is_arm
        
        except Exception:
            return False


def is_i2c_enabled() -> bool:
    """
    Check if I2C is enabled on the Raspberry Pi.
    
    Returns:
        True if I2C is enabled, False otherwise
    """
    if not is_raspberry_pi():
        logging.warning("Not running on a Raspberry Pi, assuming I2C is enabled")
        return True
    
    try:
        # Check if I2C kernel modules are loaded
        lsmod_output = subprocess.check_output(['lsmod'], text=True)
        if 'i2c_bcm' not in lsmod_output and 'i2c_dev' not in lsmod_output:
            return False
        
        # Check if I2C device nodes exist
        i2c_devs = [f for f in os.listdir('/dev') if f.startswith('i2c-')]
        if not i2c_devs:
            return False
        
        return True
    
    except Exception as e:
        logging.warning(f"Error checking if I2C is enabled: {e}")
        return False


def enable_i2c() -> bool:
    """
    Try to enable I2C on the Raspberry Pi.
    
    Returns:
        True if I2C was successfully enabled, False otherwise
    """
    if not is_raspberry_pi():
        logging.warning("Not running on a Raspberry Pi, can't enable I2C")
        return False
    
    if is_i2c_enabled():
        # I2C is already enabled
        return True
    
    try:
        # Try to enable I2C automatically
        logging.info("Attempting to enable I2C automatically...")
        
        # Try using raspi-config non-interactively
        try:
            subprocess.check_call([
                'sudo', 'raspi-config', 'nonint', 'do_i2c', '0'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            logging.info("Enabled I2C using raspi-config")
            return is_i2c_enabled()  # Verify it's now enabled
        
        except Exception as e:
            logging.warning(f"Failed to enable I2C using raspi-config: {e}")
        
        # Alternative approach: modify config.txt
        config_paths = [
            '/boot/config.txt',
            '/boot/firmware/config.txt'  # For newer Raspberry Pi OS
        ]
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                try:
                    # Read current config
                    with open(config_path, 'r') as f:
                        config_lines = f.readlines()
                    
                    # Check if dtparam=i2c_arm=on is already in config
                    i2c_enabled = any('dtparam=i2c_arm=on' in line for line in config_lines)
                    
                    if not i2c_enabled:
                        # Add I2C configuration
                        with open(config_path, 'a') as f:
                            f.write('\n# Enable I2C\ndtparam=i2c_arm=on\n')
                        
                        logging.info(f"Added I2C configuration to {config_path}")
                        logging.warning("You need to reboot for I2C changes to take effect")
                    
                    return i2c_enabled
                
                except Exception as e:
                    logging.error(f"Failed to modify {config_path}: {e}")
        
        # If we couldn't enable I2C automatically, guide the user
        logging.error("Could not enable I2C automatically")
        logging.error("Please run 'sudo raspi-config' and enable I2C in:")
        logging.error("Interface Options -> I2C -> Yes")
        
        return False
    
    except Exception as e:
        logging.error(f"Error enabling I2C: {e}")
        return False


def get_i2c_addresses(bus: int = DEFAULT_I2C_BUS) -> List[int]:
    """
    Scan I2C bus and return list of available device addresses.
    
    Args:
        bus: I2C bus number (default is 1 for most Raspberry Pi models)
        
    Returns:
        List of I2C device addresses found (as integers)
    """
    if not is_raspberry_pi() or not is_i2c_enabled():
        logging.warning("I2C is not available, cannot scan for devices")
        return []
    
    try:
        # Scan for I2C devices using i2cdetect
        output = subprocess.check_output(
            ['i2cdetect', '-y', str(bus)],
            text=True
        )
        
        # Parse the output to extract addresses
        addresses = []
        for line in output.strip().split('\n')[1:]:  # Skip the header row
            parts = line.split(':')
            if len(parts) != 2:
                continue
            
            # Extract values from the line
            row_values = parts[1].strip().split()
            row_base = int(parts[0].strip(), 16) * 16
            
            for i, val in enumerate(row_values):
                if val != '--':
                    # Convert address to integer
                    addr = int(val, 16) if val != 'UU' else row_base + i
                    addresses.append(addr)
        
        return addresses
    
    except Exception as e:
        logging.error(f"Error scanning I2C bus: {e}")
        return []


def check_oled_display(
    address: int = DEFAULT_I2C_ADDRESS,
    bus: int = DEFAULT_I2C_BUS
) -> Dict[str, Any]:
    """
    Check if OLED display is connected and return status information.
    
    Args:
        address: I2C address of the display (default is 0x3C)
        bus: I2C bus number (default is 1)
        
    Returns:
        Dictionary with status information:
        - is_pi: Whether running on a Raspberry Pi
        - i2c_enabled: Whether I2C is enabled
        - devices_found: List of I2C devices found
        - display_connected: Whether the OLED display is detected
        - status: Overall status message
        - error: Error message (if any)
    """
    result = {
        'is_pi': False,
        'i2c_enabled': False,
        'devices_found': [],
        'display_connected': False,
        'status': 'Unknown',
        'error': None
    }
    
    try:
        # Check if running on a Raspberry Pi
        result['is_pi'] = is_raspberry_pi()
        
        if not result['is_pi']:
            result['status'] = 'Not running on a Raspberry Pi'
            return result
        
        # Check if I2C is enabled
        result['i2c_enabled'] = is_i2c_enabled()
        
        if not result['i2c_enabled']:
            result['status'] = 'I2C is not enabled'
            result['error'] = 'Run "sudo raspi-config" to enable I2C'
            return result
        
        # Scan for I2C devices
        addresses = get_i2c_addresses(bus)
        result['devices_found'] = [f"0x{addr:02X}" for addr in addresses]
        
        # Check if the OLED display is connected
        if address in addresses:
            result['display_connected'] = True
            result['status'] = 'OLED display detected'
        else:
            result['status'] = 'OLED display not found'
            result['error'] = (
                f"Display at address 0x{address:02X} not found on I2C bus {bus}. "
                f"Available devices: {', '.join(result['devices_found']) or 'None'}"
            )
        
        return result
    
    except Exception as e:
        logging.error(f"Error checking OLED display: {e}")
        result['status'] = 'Error checking OLED display'
        result['error'] = str(e)
        return result


def verify_hardware_requirements(
    address: int = DEFAULT_I2C_ADDRESS,
    bus: int = DEFAULT_I2C_BUS,
    auto_enable: bool = True,
    require_display: bool = True
) -> Tuple[bool, Dict[str, Any]]:
    """
    Verify hardware requirements for the OLED display.
    
    This function checks if I2C is enabled and the OLED display
    is connected. It can optionally try to enable I2C if it's not
    already enabled.
    
    Args:
        address: I2C address of the display (default is 0x3C)
        bus: I2C bus number (default is 1)
        auto_enable: Whether to try enabling I2C if it's disabled
        require_display: Whether to require the display to be connected
        
    Returns:
        Tuple (success, details) where:
        - success: True if all requirements are met
        - details: Dictionary with details of the checks
    """
    # Check if running on a Raspberry Pi
    is_pi = is_raspberry_pi()
    
    if not is_pi:
        logging.warning("Not running on a Raspberry Pi, hardware checks skipped")
        return not require_display, {
            'is_pi': False,
            'status': 'Not running on a Raspberry Pi, hardware checks skipped'
        }
    
    # Check if I2C is enabled
    i2c_enabled = is_i2c_enabled()
    
    # Try to enable I2C if not already enabled
    if not i2c_enabled and auto_enable:
        i2c_enabled = enable_i2c()
        
        if i2c_enabled:
            logging.info("Successfully enabled I2C")
        else:
            logging.warning("Failed to enable I2C, please enable it manually")
    
    # If I2C is still not enabled, fail the check
    if not i2c_enabled:
        return False, {
            'is_pi': True,
            'i2c_enabled': False,
            'status': 'I2C is not enabled',
            'error': 'Please run "sudo raspi-config" to enable I2C'
        }
    
    # Check for OLED display
    display_check = check_oled_display(address, bus)
    
    # Determine success based on display check
    success = True if not require_display else display_check['display_connected']
    
    if success:
        level = logging.INFO
        if not display_check['display_connected'] and not require_display:
            level = logging.WARNING
            display_check['status'] += " (continuing anyway as display is not required)"
        
        logging.log(level, display_check['status'])
    else:
        logging.error(display_check['status'])
        if display_check['error']:
            logging.error(display_check['error'])
    
    return success, display_check
