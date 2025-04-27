#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code integrity tests for the OLED framework.
These tests don't run functionality but validate that code structure 
is correct to catch the issues we've been fixing.
"""

import unittest
import re
import inspect
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestCodeIntegrity(unittest.TestCase):
    """
    Test code structure and patterns to identify common issues
    without requiring hardware dependencies.
    """
    
    def test_display_grid_not_layout(self):
        """
        Test that display.py uses 'self.grid' and not 'self.layout'.
        This catches one of our major issues - the rename from layout to grid.
        """
        # Get the display module
        import display
        
        # Read the source code
        with open(display.__file__, 'r') as f:
            source_code = f.read()
        
        # Find all instances of self.layout - should be none after our fix
        layout_matches = re.findall(r'self\.layout\b', source_code)
        
        # Error with detail if we find any instances
        if layout_matches:
            # Find the line numbers for context
            lines = source_code.split('\n')
            line_numbers = []
            for i, line in enumerate(lines, 1):
                if 'self.layout' in line:
                    line_numbers.append(f"Line {i}: {line.strip()}")
            
            # Fail with details
            self.fail(f"Found {len(layout_matches)} instances of 'self.layout' which should be 'self.grid':\n" + 
                     "\n".join(line_numbers))
    
    def test_split_area_usage(self):
        """
        Test that create_standard_layout calls split_area with correct parameters.
        """
        # Get the display module
        import display
        
        # Get the implementation of create_standard_layout method
        method_source = inspect.getsource(display.OLEDDisplay.create_standard_layout)
        
        # Check for proper count parameter in metrics split
        metrics_split_pattern = re.search(r'split_area\([^)]*metrics[^)]*count=3', method_source)
        self.assertIsNotNone(metrics_split_pattern, 
                          "Missing count=3 parameter in metrics split_area call")
        
        # Check that float values are used, not percentage strings
        percentage_pattern = re.search(r"sizes=\[['\"]?\d+%['\"]?", method_source)
        self.assertIsNone(percentage_pattern, 
                       "Using percentage strings in split_area calls - should use floats")
        
        # Check that float values are actually used
        float_pattern = re.search(r'sizes=\[\s*0\.\d+\s*,\s*0\.\d+', method_source)
        self.assertIsNotNone(float_pattern, 
                          "Not using proper float values in split_area calls")
    
    def test_add_container_method(self):
        """
        Test that add_container method properly uses grid attribute.
        """
        # Get the display module
        import display
        
        # Get the implementation of add_container method
        method_source = inspect.getsource(display.OLEDDisplay.add_container)
        
        # Check that it uses self.grid.get_area
        get_area_pattern = re.search(r'self\.grid\.get_area', method_source)
        self.assertIsNotNone(get_area_pattern, 
                          "add_container should use self.grid.get_area")


if __name__ == '__main__':
    unittest.main()
