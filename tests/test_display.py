#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the OLED display functionality.
"""

import unittest
from unittest.mock import MagicMock, patch
import logging
import sys
import os
from PIL import Image, ImageDraw

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules to test
from display import OLEDDisplay
from layout.grid import GridLayout, GridArea
from layout.containers import Container, TextContainer, MetricContainer


class MockDevice:
    """Mock OLED display device for testing."""
    
    def __init__(self, *args, **kwargs):
        self.display_calls = 0
        self.contrast_value = 255
        self.inverted = False
    
    def display(self, image):
        """Mock display method."""
        self.display_calls += 1
        self.last_image = image
    
    def contrast(self, value):
        """Mock contrast method."""
        self.contrast_value = value
    
    def invert(self, value):
        """Mock invert method."""
        self.inverted = value


class TestOLEDDisplay(unittest.TestCase):
    """Test cases for the OLEDDisplay class."""
    
    @patch('display.i2c')
    @patch('display.ssd1306')
    def setUp(self, mock_ssd1306, mock_i2c):
        """Set up test fixtures."""
        # Create mocks
        self.mock_serial = MagicMock()
        self.mock_device = MockDevice()
        
        # Configure mocks
        mock_i2c.return_value = self.mock_serial
        mock_ssd1306.return_value = self.mock_device
        
        # Create display under test
        self.display = OLEDDisplay(
            width=128,
            height=32,
            i2c_port=1,
            i2c_address=0x3C,
            rotation=0,
            contrast=255,
            inverted=False
        )
    
    def test_initialization(self):
        """Test OLEDDisplay initialization."""
        # Verify display properties
        self.assertEqual(self.display.width, 128)
        self.assertEqual(self.display.height, 32)
        self.assertEqual(self.display.i2c_port, 1)
        self.assertEqual(self.display.i2c_address, 0x3C)
        
        # Verify internal objects
        self.assertIsInstance(self.display.image, Image.Image)
        self.assertIsInstance(self.display.draw, ImageDraw.ImageDraw)
        self.assertIsInstance(self.display.grid, GridLayout)
        self.assertEqual(len(self.display.containers), 0)
        
        # Verify default state
        self.assertTrue(self.display.is_on)
    
    def test_create_standard_layout(self):
        """Test creating the standard layout."""
        # Reset the display to test create_standard_layout specifically
        self.display.grid = GridLayout(self.display.width, self.display.height)
        self.display.areas = {}
        
        # Call the method
        areas = self.display.create_standard_layout()
        
        # Verify expected areas are created
        expected_areas = ['root', 'header', 'hostname', 'uptime', 'body', 
                         'metrics', 'status', 'cpu', 'memory', 'temperature']
        for area_name in expected_areas:
            self.assertIn(area_name, areas)
            self.assertIsInstance(areas[area_name], GridArea)
        
        # Verify the split_area method was used with correct parameters
        # Check specific area dimensions to ensure layout is correct
        self.assertEqual(areas['header'].height, int(self.display.height * 0.2))
        self.assertEqual(areas['body'].height, int(self.display.height * 0.8))
        
        # Check the metrics columns
        total_width = areas['metrics'].width
        cpu_width = areas['cpu'].width
        memory_width = areas['memory'].width
        temp_width = areas['temperature'].width
        
        # Should be approximately in 33/33/34 ratio
        self.assertAlmostEqual(cpu_width / total_width, 0.33, delta=0.01)
        self.assertAlmostEqual(memory_width / total_width, 0.33, delta=0.01)
        self.assertAlmostEqual(temp_width / total_width, 0.34, delta=0.01)
    
    def test_add_container(self):
        """Test adding a container to the display."""
        # Create a test container
        container = TextContainer(name="test_text", text="Hello")
        
        # Add it to the display (should use the create_standard_layout areas)
        self.display.add_container(container, "header")
        
        # Verify the container was added
        self.assertIn("test_text", self.display.containers)
        self.assertEqual(self.display.containers["test_text"], container)
        
        # Verify container received correct position
        header_area = self.display.grid.get_area("header")
        self.assertEqual(container.x, header_area.x)
        self.assertEqual(container.y, header_area.y)
        self.assertEqual(container.width, header_area.width)
        self.assertEqual(container.height, header_area.height)
    
    def test_remove_container(self):
        """Test removing a container from the display."""
        # First add a container
        container = TextContainer(name="test_text", text="Hello")
        self.display.add_container(container, "header")
        
        # Then remove it
        self.display.remove_container("test_text")
        
        # Verify it was removed
        self.assertNotIn("test_text", self.display.containers)
    
    def test_update_containers(self):
        """Test updating all containers."""
        # Create a container with a mock update method
        container = TextContainer(name="test_text", text="Hello")
        container.update = MagicMock()
        
        # Add to display
        self.display.add_container(container, "header")
        
        # Call update_containers
        self.display.update_containers()
        
        # Verify container's update method was called
        container.update.assert_called_once()
    
    def test_render_containers(self):
        """Test rendering all containers."""
        # Create a container with a mock render method
        container = TextContainer(name="test_text", text="Hello")
        container.render = MagicMock()
        
        # Add to display
        self.display.add_container(container, "header")
        
        # Call render_containers
        self.display.render_containers()
        
        # Verify container's render method was called with correct args
        container.render.assert_called_once()
        # First arg should be ImageDraw
        self.assertEqual(container.render.call_args[0][0], self.display.draw)
        # Second arg should be fonts dictionary
        self.assertEqual(container.render.call_args[0][1], self.display.fonts)
    
    def test_update_display(self):
        """Test full display update cycle."""
        # Create a container
        container = TextContainer(name="test_text", text="Hello")
        container.update = MagicMock()
        container.render = MagicMock()
        
        # Add to display
        self.display.add_container(container, "header")
        
        # Spy on methods we want to verify
        original_clear = self.display.clear
        original_update_containers = self.display.update_containers
        original_render_containers = self.display.render_containers
        original_show = self.display.show
        
        self.display.clear = MagicMock(wraps=original_clear)
        self.display.update_containers = MagicMock(wraps=original_update_containers)
        self.display.render_containers = MagicMock(wraps=original_render_containers)
        self.display.show = MagicMock(wraps=original_show)
        
        # Call update_display
        result = self.display.update_display()
        
        # Verify result and method calls
        self.assertTrue(result)
        self.display.clear.assert_called_once()
        self.display.update_containers.assert_called_once()
        self.display.render_containers.assert_called_once()
        self.display.show.assert_called_once()
    
    def test_turn_off_display(self):
        """Test turning off the display."""
        self.display.turn_off()
        self.assertFalse(self.display.is_on)
    
    def test_turn_on_display(self):
        """Test turning on the display."""
        self.display.is_on = False
        self.display.turn_on()
        self.assertTrue(self.display.is_on)


if __name__ == '__main__':
    unittest.main()
