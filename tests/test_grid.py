#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the grid layout system.
"""

import unittest
from layout.grid import GridLayout, GridArea


class TestGridArea(unittest.TestCase):
    """Test cases for the GridArea class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.area = GridArea("test_area", (0, 0, 100, 50))
    
    def test_initialization(self):
        """Test GridArea initialization."""
        self.assertEqual(self.area.x, 0)
        self.assertEqual(self.area.y, 0)
        self.assertEqual(self.area.width, 100)
        self.assertEqual(self.area.height, 50)
        self.assertEqual(self.area.name, "test_area")
        
    def test_position(self):
        """Test area position properties."""
        self.assertEqual(self.area.x, 0)
        self.assertEqual(self.area.y, 0)
        self.assertEqual(self.area.x + self.area.width, 100)
        self.assertEqual(self.area.y + self.area.height, 50)
        
    def test_center(self):
        """Test area center calculation."""
        self.assertEqual(self.area.x + self.area.width // 2, 50)
        self.assertEqual(self.area.y + self.area.height // 2, 25)
        
    def test_size(self):
        """Test area size calculation."""
        self.assertEqual((self.area.width, self.area.height), (100, 50))
        
    def test_position_tuple(self):
        """Test position tuple property."""
        self.assertEqual((self.area.x, self.area.y), (0, 0))
        
    def test_contains_point(self):
        """Test contains_point method."""
        self.assertTrue(self.area.contains_point(50, 25))  # Center
        self.assertTrue(self.area.contains_point(0, 0))    # Top-left
        self.assertTrue(self.area.contains_point(99, 49))  # Bottom-right (inside)
        self.assertFalse(self.area.contains_point(100, 50))  # Bottom-right (outside)
        self.assertFalse(self.area.contains_point(-1, -1))  # Outside
        
    def test_repr(self):
        """Test string representation."""
        expected = "GridArea('test_area', (0, 0, 100, 50))"
        self.assertEqual(repr(self.area), expected)


class TestGridLayout(unittest.TestCase):
    """Test cases for the GridLayout class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.layout = GridLayout(200, 100)
    
    def test_initialization(self):
        """Test GridLayout initialization."""
        self.assertEqual(self.layout.width, 200)
        self.assertEqual(self.layout.height, 100)
        self.assertIn("root", self.layout.areas)
        self.assertEqual(self.layout.areas["root"].width, 200)
        self.assertEqual(self.layout.areas["root"].height, 100)
    
    def test_add_area(self):
        """Test adding an area to the layout."""
        rect = (10, 10, 50, 30)
        self.layout.add_area("test_area", rect)
        self.assertIn("test_area", self.layout.areas)
        self.assertEqual(self.layout.areas["test_area"].rect, rect)
    
    def test_get_area(self):
        """Test getting an area from the layout."""
        area = self.layout.get_area("root")
        self.assertEqual(area.name, "root")
        
        # Test getting non-existent area
        with self.assertRaises(KeyError):
            self.layout.get_area("non_existent")
    
    def test_split_area_horizontal(self):
        """Test splitting an area horizontally."""
        areas = self.layout.split_area("root", "horizontal", 2)
        self.assertEqual(len(areas), 2)
        self.assertEqual(areas[0].width, 100)
        self.assertEqual(areas[0].height, 100)
        self.assertEqual(areas[1].width, 100)
        self.assertEqual(areas[1].height, 100)
        self.assertEqual(areas[0].x, 0)
        self.assertEqual(areas[1].x, 100)
    
    def test_split_area_vertical(self):
        """Test splitting an area vertically."""
        areas = self.layout.split_area("root", "vertical", 2)
        self.assertEqual(len(areas), 2)
        self.assertEqual(areas[0].width, 200)
        self.assertEqual(areas[0].height, 50)
        self.assertEqual(areas[1].width, 200)
        self.assertEqual(areas[1].height, 50)
        self.assertEqual(areas[0].y, 0)
        self.assertEqual(areas[1].y, 50)
    
    def test_split_area_unequal(self):
        """Test splitting an area with unequal sizes."""
        areas = self.layout.split_area("root", "horizontal", 2, [0.25, 0.75])
        self.assertEqual(len(areas), 2)
        self.assertEqual(areas[0].width, 50)  # 25% of 200
        self.assertEqual(areas[1].width, 150)  # 75% of 200
    
    def test_split_area_nested(self):
        """Test nested area splitting."""
        # First split horizontally
        h_areas = self.layout.split_area("root", "horizontal", 2)
        
        # The areas are already named by the split_area method
        left_area = self.layout.get_area("root_0")
        right_area = self.layout.get_area("root_1")
        
        # Split left area vertically
        v_areas = self.layout.split_area("root_0", "vertical", 2)
        self.assertEqual(len(v_areas), 2)
        self.assertEqual(v_areas[0].width, 100)
        self.assertEqual(v_areas[0].height, 50)
        self.assertEqual(v_areas[0].x, 0)
        self.assertEqual(v_areas[0].y, 0)


if __name__ == '__main__':
    unittest.main()
