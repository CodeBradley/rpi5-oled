#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration module for the OLED display framework.

This module defines default configuration values and handles loading
user configuration from a file.
"""

import os
import sys
import json
import yaml
import logging
from typing import Dict, Any, Optional, List, Union

# Default configuration values
DEFAULT_CONFIG = {
    # Display settings
    "display": {
        "width": 128,
        "height": 32,
        "i2c_port": 1,
        "i2c_address": 0x3C,
        "rotation": 0,  # 0, 1, 2, or 3 for 0, 90, 180, or 270 degrees
        "contrast": 255,
        "inverted": False,
        "update_interval": 5.0,  # Seconds between updates
        "font_size": 10
    },
    
    # Resource metrics to display (can have up to 3)
    "metrics": [
        {
            "name": "memory",
            "type": "memory_usage",
            "icon": "memory",
            "unit": "%"
        },
        {
            "name": "cpu",
            "type": "cpu_usage",
            "icon": "cpu",
            "unit": "%"
        },
        {
            "name": "temperature",
            "type": "cpu_temperature",
            "icon": "temperature",
            "unit": "°C"
        }
    ],
    
    # Services to monitor
    "services": [
        {
            "name": "Docker",
            "type": "docker",
            "icon": "docker"
        },
        {
            "name": "CephFS",
            "type": "ceph",
            "icon": "ceph"
        }
    ],
    
    # System information
    "system_info": {
        "show_hostname": True,
        "show_ip": True,
        "network_interface": None  # None means auto-detect
    },
    
    # Advanced settings
    "advanced": {
        "log_level": "INFO",
        "log_file": "/var/log/rpi5-oled.log",
        "enable_auto_off": False,
        "auto_off_timeout": 300,  # Seconds of inactivity before turning off display
        "power_save_mode": False
    }
}


class Config:
    """
    Configuration manager for the OLED display framework.
    
    This class handles loading, validating, and accessing configuration values,
    with support for falling back to default values when needed.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file
        """
        self.config = DEFAULT_CONFIG.copy()
        self.config_file = config_file
        
        if config_file:
            self.load_from_file(config_file)
    
    def load_from_file(self, config_file: str) -> None:
        """
        Load configuration from a file.
        
        Args:
            config_file: Path to configuration file
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            ValueError: If the configuration file is invalid
        """
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        try:
            # Determine file format from extension
            _, ext = os.path.splitext(config_file)
            
            if ext.lower() in ['.yml', '.yaml']:
                # YAML format
                with open(config_file, 'r') as f:
                    user_config = yaml.safe_load(f)
            elif ext.lower() == '.json':
                # JSON format
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {ext}")
            
            # Update config with user values, preserving defaults for missing values
            self._update_recursive(self.config, user_config)
            
            logging.info(f"Loaded configuration from {config_file}")
        
        except Exception as e:
            logging.error(f"Error loading configuration from {config_file}: {e}")
            raise ValueError(f"Invalid configuration file: {e}")
    
    def _update_recursive(self, target: Dict, source: Dict) -> None:
        """
        Recursively update a dictionary with values from another dictionary.
        
        Args:
            target: Target dictionary to update
            source: Source dictionary with new values
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursively update nested dictionaries
                self._update_recursive(target[key], value)
            else:
                # Update or add the value
                target[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key path.
        
        Args:
            key: Key path (dot-separated for nested values)
            default: Default value if the key doesn't exist
            
        Returns:
            Configuration value, or default if not found
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value by key path.
        
        Args:
            key: Key path (dot-separated for nested values)
            value: Value to set
        """
        keys = key.split('.')
        target = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in target or not isinstance(target[k], dict):
                target[k] = {}
            target = target[k]
        
        # Set the value
        target[keys[-1]] = value
    
    def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get the configured metrics.
        
        Returns:
            List of metric configurations
        """
        return self.config.get('metrics', [])
    
    def get_services(self) -> List[Dict[str, Any]]:
        """
        Get the configured services.
        
        Returns:
            List of service configurations
        """
        return self.config.get('services', [])
    
    def get_display_config(self) -> Dict[str, Any]:
        """
        Get display configuration.
        
        Returns:
            Display configuration dictionary
        """
        return self.config.get('display', {})
    
    def save(self, config_file: Optional[str] = None) -> None:
        """
        Save the current configuration to a file.
        
        Args:
            config_file: Path to save to, or None to use the original file
            
        Raises:
            ValueError: If no file path is provided and no original file exists
        """
        file_path = config_file or self.config_file
        if not file_path:
            raise ValueError("No configuration file path provided")
        
        try:
            # Determine file format from extension
            _, ext = os.path.splitext(file_path)
            
            if ext.lower() in ['.yml', '.yaml']:
                # YAML format
                with open(file_path, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False)
            elif ext.lower() == '.json':
                # JSON format
                with open(file_path, 'w') as f:
                    json.dump(self.config, f, indent=2)
            else:
                raise ValueError(f"Unsupported configuration file format: {ext}")
            
            logging.info(f"Saved configuration to {file_path}")
        
        except Exception as e:
            logging.error(f"Error saving configuration to {file_path}: {e}")
            raise ValueError(f"Failed to save configuration file: {e}")


# Global configuration instance
config = Config()


def load_config(config_file: Optional[str] = None) -> Config:
    """
    Load configuration from a file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Config instance
    """
    global config
    
    if config_file:
        config = Config(config_file)
    
    return config


def get_config() -> Config:
    """
    Get the global configuration instance.
    
    Returns:
        Config instance
    """
    return config


def configure_logging() -> None:
    """Configure logging based on current configuration."""
    log_level_name = config.get('advanced.log_level', 'INFO')
    log_file = config.get('advanced.log_file')
    
    # Map log level name to value
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # Basic configuration
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add file handler if log file is specified
    if log_file:
        try:
            # Ensure log directory exists
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            
            # Add to root logger
            logging.getLogger().addHandler(file_handler)
            
            logging.info(f"Logging to {log_file} at level {log_level_name}")
        
        except Exception as e:
            logging.error(f"Failed to set up file logging: {e}")
