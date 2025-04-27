#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct file pattern tests for the OLED framework.
These tests examine file contents directly without importing modules,
avoiding the need for hardware dependencies.
"""

import unittest
import re
import os

class TestFilePatterns(unittest.TestCase):
    """
    Test code structure and patterns by examining file contents directly.
    This avoids the need to import hardware-dependent modules.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.display_path = os.path.join(self.project_root, 'display.py')
        
        # Read the display.py file
        with open(self.display_path, 'r') as f:
            self.display_code = f.read()
    
    def test_display_uses_grid_not_layout(self):
        """
        Test that display.py uses 'self.grid' and not 'self.layout'.
        This catches one of our major issues - the rename from layout to grid.
        """
        # Find all instances of self.layout - should be none after our fix
        layout_matches = re.findall(r'self\.layout\b', self.display_code)
        
        # Error with detail if we find any instances
        if layout_matches:
            # Find the line numbers for context
            lines = self.display_code.split('\n')
            line_numbers = []
            for i, line in enumerate(lines, 1):
                if 'self.layout' in line:
                    line_numbers.append(f"Line {i}: {line.strip()}")
            
            # Fail with details
            self.fail(f"Found {len(layout_matches)} instances of 'self.layout' which should be 'self.grid':\n" + 
                     "\n".join(line_numbers))
    
    def test_create_standard_layout_pattern(self):
        """
        Test that create_standard_layout uses correct patterns for splitting areas.
        """
        # Extract the create_standard_layout method using regex
        method_pattern = re.compile(r'def create_standard_layout.*?return self\.areas', re.DOTALL)
        method_match = method_pattern.search(self.display_code)
        self.assertIsNotNone(method_match, "Could not find create_standard_layout method")
        
        method_code = method_match.group(0)
        
        # 1. Check for proper count parameter in metrics split
        metrics_split_pattern = re.search(r'split_area\([^)]*metrics.*?count=3', method_code)
        self.assertIsNotNone(metrics_split_pattern, 
                          "Missing count=3 parameter in metrics split_area call")
        
        # 2. Check that float values are used, not percentage strings
        percentage_pattern = re.search(r"sizes=\[['\"]?\d+%['\"]?", method_code)
        self.assertIsNone(percentage_pattern, 
                       "Using percentage strings in split_area calls - should use floats")
        
        # 3. Check that float values are actually used
        float_pattern = re.search(r'sizes=\[\s*0\.\d+\s*,\s*0\.\d+', method_code)
        self.assertIsNotNone(float_pattern, 
                          "Not using proper float values in split_area calls")
    
    def test_add_container_uses_grid(self):
        """
        Test that add_container method properly uses grid attribute.
        """
        # Extract the add_container method using regex
        method_pattern = re.compile(r'def add_container.*?self\.containers\[container\.name\] = container', re.DOTALL)
        method_match = method_pattern.search(self.display_code)
        self.assertIsNotNone(method_match, "Could not find add_container method")
        
        method_code = method_match.group(0)
        
        # Check that it uses self.grid.get_area
        get_area_pattern = re.search(r'self\.grid\.get_area', method_code)
        self.assertIsNotNone(get_area_pattern, 
                          "add_container should use self.grid.get_area")
        
        # Make sure it doesn't use self.layout
        layout_pattern = re.search(r'self\.layout', method_code)
        self.assertIsNone(layout_pattern,
                        "add_container should not use self.layout")


if __name__ == '__main__':
    unittest.main()
