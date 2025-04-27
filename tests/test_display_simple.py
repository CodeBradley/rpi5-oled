#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified unit tests for the OLED display functionality.
This focuses on layout and grid features without hardware dependencies.
"""

import unittest
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock required external modules
sys.modules['luma.core.interface.serial'] = type('mock_serial', (), {'i2c': lambda **kwargs: None})
sys.modules['luma.oled.device'] = type('mock_device', (), {'ssd1306': lambda **kwargs: None})

# Mock Image and ImageDraw
class MockImage:
    def __init__(self, mode, size):
        self.mode = mode
        self.size = size
        
    def new(self, mode, size):
        return MockImage(mode, size)

class MockDraw:
    def __init__(self, image):
        self.image = image
        
    def rectangle(self, *args, **kwargs):
        pass
        
    def text(self, *args, **kwargs):
        pass

sys.modules['PIL.Image'] = type('MockPIL', (), {
    'Image': MockImage,
    'new': lambda *args: MockImage(*args),
})
sys.modules['PIL.ImageDraw'] = type('MockPIL', (), {
    'ImageDraw': MockDraw,
    'Draw': lambda image: MockDraw(image),
})

# Import after mocking
from layout.grid import GridLayout, GridArea


class TestDisplaySimple(unittest.TestCase):
    """Test the display layout functionality without hardware dependencies."""
    
    def setUp(self):
        """Set up test fixtures."""
        # We'll test the important methods without initializing hardware
        from display import OLEDDisplay
        
        # Create display instance without calling __init__
        self.display = OLEDDisplay.__new__(OLEDDisplay)
        
        # Set required attributes manually
        self.display.width = 128
        self.display.height = 32
        self.display.grid = GridLayout(128, 32)
        self.display.areas = {}
        
        # Add grid's root area to the areas dictionary
        self.display.areas['root'] = self.display.grid.areas['root']
    
    def test_create_standard_layout(self):
        """Test that the standard layout is created correctly."""
        from display import OLEDDisplay
        
        # Call the method we're testing
        areas = self.display.create_standard_layout()
        
        # Verify that all expected areas were created
        expected_areas = [
            'root', 'header', 'hostname', 'uptime', 'body', 
            'metrics', 'status', 'cpu', 'memory', 'temperature'
        ]
        for area_name in expected_areas:
            self.assertIn(area_name, areas)
            self.assertIsInstance(areas[area_name], GridArea)
        
        # Check key dimensions to ensure splits worked correctly
        header_height = areas['header'].height
        expected_header_height = int(self.display.height * 0.2)
        self.assertEqual(header_height, expected_header_height)
        
        body_height = areas['body'].height
        expected_body_height = int(self.display.height * 0.8)
        self.assertEqual(body_height, expected_body_height)
        
        # Check that the rows add up to the total height
        self.assertEqual(header_height + body_height, self.display.height)
        
        # Check column split in metrics area
        metrics_width = areas['metrics'].width
        cpu_width = areas['cpu'].width
        memory_width = areas['memory'].width
        temp_width = areas['temperature'].width
        
        # Check the sum of metrics columns equals metrics width
        self.assertEqual(cpu_width + memory_width + temp_width, metrics_width)
    
    def test_grid_attribute_usage(self):
        """
        Test that the grid attribute is correctly used.
        This validates that self.grid is used to access areas and not self.layout.
        """
        # Create areas first
        self.display.create_standard_layout()
        
        # Directly check the implementation in display.py
        from display import OLEDDisplay
        
        # Get the actual method source code as a string
        import inspect
        method_source = inspect.getsource(OLEDDisplay.add_container)
        
        # Verify it uses self.grid and not self.layout
        self.assertIn('self.grid', method_source)
        self.assertNotIn('self.layout', method_source)
        
        # Check that all areas can be accessed through self.grid
        for area_name in self.display.areas:
            if area_name != 'root':
                # Try accessing the area - should not raise an exception
                area = self.display.grid.get_area(area_name)
                self.assertIsInstance(area, GridArea)
    
    def test_split_area_parameters(self):
        """
        Test that the split_area method is called with correct parameters.
        This catches the error where we forgot to specify count=3.
        """
        # Save original method for validation
        original_split_area = self.display.grid.split_area
        
        # Create a validation wrapper around split_area
        def validate_split_area(area_name, direction='horizontal', count=2, sizes=None):
            # Validate that if we pass 3 sizes, we also pass count=3
            if sizes and len(sizes) == 3:
                self.assertEqual(count, 3, "When passing 3 sizes, count should also be 3")
            
            # Call original method
            return original_split_area(area_name, direction, count, sizes)
        
        # Patch the grid's split_area method with our validation wrapper
        self.display.grid.split_area = validate_split_area
        
        # Now call create_standard_layout, which uses split_area
        self.display.create_standard_layout()
        
        # If we get here without assertions failing, the test passes


if __name__ == '__main__':
    unittest.main()
