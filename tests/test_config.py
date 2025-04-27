#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the configuration module.
"""

import os
import unittest
import tempfile
import json
import yaml
from config import Config, DEFAULT_CONFIG


class TestConfig(unittest.TestCase):
    """Test cases for the Config class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
    
    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
    
    def test_default_config(self):
        """Test default configuration values."""
        self.assertEqual(self.config.get('display.width'), 128)
        self.assertEqual(self.config.get('display.height'), 32)
        self.assertEqual(self.config.get('display.i2c_port'), 1)
        self.assertEqual(self.config.get('display.i2c_address'), 0x3C)
        
        metrics = self.config.get_metrics()
        self.assertEqual(len(metrics), 3)
        self.assertEqual(metrics[0]['name'], 'memory')
        
        services = self.config.get_services()
        self.assertEqual(len(services), 2)
        self.assertEqual(services[0]['name'], 'Docker')
    
    def test_get_with_default(self):
        """Test getting a configuration value with a default."""
        # Existing key
        self.assertEqual(self.config.get('display.width'), 128)
        
        # Non-existent key with default
        self.assertEqual(self.config.get('non.existent.key', 'default'), 'default')
        
        # Non-existent key without default
        self.assertIsNone(self.config.get('non.existent.key'))
    
    def test_set_value(self):
        """Test setting a configuration value."""
        # Set an existing key
        self.config.set('display.width', 256)
        self.assertEqual(self.config.get('display.width'), 256)
        
        # Set a new key
        self.config.set('new.key', 'value')
        self.assertEqual(self.config.get('new.key'), 'value')
        
        # Set a nested key
        self.config.set('new.nested.key', 'nested_value')
        self.assertEqual(self.config.get('new.nested.key'), 'nested_value')
    
    def test_load_json_config(self):
        """Test loading configuration from a JSON file."""
        # Create a temporary JSON config file
        config_path = os.path.join(self.temp_dir.name, 'config.json')
        test_config = {
            'display': {
                'width': 64,
                'height': 48,
                'update_interval': 10.0,
            },
            'system_info': {
                'show_hostname': False,
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(test_config, f)
        
        # Load the configuration
        config = Config(config_path)
        
        # Check that values were loaded correctly
        self.assertEqual(config.get('display.width'), 64)
        self.assertEqual(config.get('display.height'), 48)
        self.assertEqual(config.get('display.update_interval'), 10.0)
        self.assertEqual(config.get('system_info.show_hostname'), False)
        
        # Check that default values are preserved for unspecified keys
        self.assertEqual(config.get('display.i2c_port'), 1)
        self.assertEqual(config.get('display.i2c_address'), 0x3C)
    
    def test_load_yaml_config(self):
        """Test loading configuration from a YAML file."""
        # Create a temporary YAML config file
        config_path = os.path.join(self.temp_dir.name, 'config.yaml')
        test_config = """
        display:
          width: 64
          height: 48
          update_interval: 10.0
        system_info:
          show_hostname: false
        """
        
        with open(config_path, 'w') as f:
            f.write(test_config)
        
        # Load the configuration
        config = Config(config_path)
        
        # Check that values were loaded correctly
        self.assertEqual(config.get('display.width'), 64)
        self.assertEqual(config.get('display.height'), 48)
        self.assertEqual(config.get('display.update_interval'), 10.0)
        self.assertEqual(config.get('system_info.show_hostname'), False)
        
        # Check that default values are preserved for unspecified keys
        self.assertEqual(config.get('display.i2c_port'), 1)
        self.assertEqual(config.get('display.i2c_address'), 0x3C)
    
    def test_save_config(self):
        """Test saving configuration to a file."""
        # Set some custom values
        self.config.set('display.width', 64)
        self.config.set('display.height', 48)
        self.config.set('system_info.show_hostname', False)
        
        # Save to JSON
        json_path = os.path.join(self.temp_dir.name, 'config.json')
        self.config.save(json_path)
        
        # Load the saved config
        json_config = Config(json_path)
        self.assertEqual(json_config.get('display.width'), 64)
        self.assertEqual(json_config.get('display.height'), 48)
        self.assertEqual(json_config.get('system_info.show_hostname'), False)
        
        # Save to YAML
        yaml_path = os.path.join(self.temp_dir.name, 'config.yaml')
        self.config.save(yaml_path)
        
        # Load the saved config
        yaml_config = Config(yaml_path)
        self.assertEqual(yaml_config.get('display.width'), 64)
        self.assertEqual(yaml_config.get('display.height'), 48)
        self.assertEqual(yaml_config.get('system_info.show_hostname'), False)


if __name__ == '__main__':
    unittest.main()
