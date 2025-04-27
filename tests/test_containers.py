#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the container system.
"""

import unittest
from unittest.mock import MagicMock, patch
from typing import Dict
from PIL import Image, ImageDraw
from layout.containers import (
    Container, MetricContainer, ServiceIconContainer, TextContainer, DividerContainer
)

# Create a concrete container class for testing
class TestableContainer(Container):
    """Concrete implementation of Container for testing."""
    
    def render(self, draw, fonts: Dict) -> None:
        """Implement the abstract render method."""
        super().render(draw, fonts)
        
    def update(self) -> None:
        """Implement the update method."""
        pass


class TestContainer(unittest.TestCase):
    """Test cases for the base Container class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.container = TestableContainer("test_container")
        self.container.set_position(10, 20, 100, 50)
        
        # Create mock draw and fonts objects
        self.draw = MagicMock(spec=ImageDraw.ImageDraw)
        self.fonts = {
            'icon': MagicMock(),
            'text': MagicMock()
        }
    
    def test_initialization(self):
        """Test Container initialization."""
        self.assertEqual(self.container.name, "test_container")
        self.assertFalse(self.container.visible)
        
    def test_set_position(self):
        """Test setting container position."""
        self.assertEqual(self.container.x, 10)
        self.assertEqual(self.container.y, 20)
        self.assertEqual(self.container.width, 100)
        self.assertEqual(self.container.height, 50)
        
    def test_show_hide(self):
        """Test showing and hiding the container."""
        self.container.show()
        self.assertTrue(self.container.visible)
        
        self.container.hide()
        self.assertFalse(self.container.visible)
        
    def test_update(self):
        """Test the update method."""
        # Base container update does nothing, but shouldn't fail
        self.container.update()
        
    def test_render(self):
        """Test the render method."""
        # Base container render only draws a rectangle if debug is enabled
        self.container.debug = True
        self.container.show()
        self.container.render(self.draw, self.fonts)
        
        # Verify rectangle was drawn
        self.draw.rectangle.assert_called_once()


class TestMetricContainer(unittest.TestCase):
    """Test cases for the MetricContainer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock provider function that returns a value
        self.provider = MagicMock(return_value=75.5)
        
        # Create the container
        self.container = MetricContainer(
            "cpu", 
            icon_code="\uf3d8", 
            provider=self.provider,
            unit="%"
        )
        self.container.set_position(10, 20, 100, 50)
        self.container.show()
        
        # Create mock draw and fonts objects
        self.draw = MagicMock(spec=ImageDraw.ImageDraw)
        self.fonts = {
            'icon': MagicMock(),
            'text': MagicMock()
        }
    
    def test_initialization(self):
        """Test MetricContainer initialization."""
        self.assertEqual(self.container.name, "cpu")
        self.assertEqual(self.container.icon_code, "\uf3d8")
        self.assertEqual(self.container.provider, self.provider)
        self.assertEqual(self.container.unit, "%")
        # Value is initialized to 0 in the current implementation
        self.assertEqual(self.container.value, 0)
        
    def test_update(self):
        """Test updating the metric value."""
        self.container.update()
        self.assertEqual(self.container.value, 75.5)
        
        # Ensure the provider was called
        self.provider.assert_called_once()
        
    def test_render(self):
        """Test rendering the metric."""
        # Update the container first
        self.container.update()
        
        # Render the container
        self.container.render(self.draw, self.fonts)
        
        # Verify text was drawn for both the icon and value
        self.draw.text.assert_called()
        self.assertEqual(self.draw.text.call_count, 2)


class TestServiceIconContainer(unittest.TestCase):
    """Test cases for the ServiceIconContainer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock service providers
        self.docker_provider = MagicMock(return_value=True)
        self.ceph_provider = MagicMock(return_value=False)
        
        # Create services dictionary
        self.services = {
            "Docker": ("\uf424", self.docker_provider),
            "Ceph": ("\uef5b", self.ceph_provider)
        }
        
        # Create the container
        self.container = ServiceIconContainer("services", self.services)
        self.container.set_position(10, 20, 100, 50)
        self.container.show()
        
        # Create mock draw and fonts objects
        self.draw = MagicMock(spec=ImageDraw.ImageDraw)
        self.fonts = {
            'icon': MagicMock(),
            'text': MagicMock()
        }
    
    def test_initialization(self):
        """Test ServiceIconContainer initialization."""
        self.assertEqual(self.container.name, "services")
        self.assertEqual(len(self.container.services), 2)
        self.assertEqual(len(self.container.statuses), 0)
        
    def test_update(self):
        """Test updating service statuses."""
        self.container.update()
        
        # Check service statuses were updated
        self.assertEqual(len(self.container.statuses), 2)
        self.assertTrue(self.container.statuses["Docker"])
        self.assertFalse(self.container.statuses["Ceph"])
        
        # Ensure the providers were called
        self.docker_provider.assert_called_once()
        self.ceph_provider.assert_called_once()
        
    def test_render(self):
        """Test rendering the service icons."""
        # Update the container first
        self.container.update()
        
        # Render the container
        self.container.render(self.draw, self.fonts)
        
        # Verify text was drawn for each service icon
        self.assertEqual(self.draw.text.call_count, 2)


class TestTextContainer(unittest.TestCase):
    """Test cases for the TextContainer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock provider function that returns text
        self.provider = MagicMock(return_value="hostname")
        
        # Create the container
        self.container = TextContainer(
            "hostname", 
            provider=self.provider,
            prefix="Host: "
        )
        self.container.set_position(10, 20, 100, 50)
        self.container.show()
        
        # Create mock draw and fonts objects
        self.draw = MagicMock(spec=ImageDraw.ImageDraw)
        self.fonts = {
            'icon': MagicMock(),
            'text': MagicMock()
        }
    
    def test_initialization(self):
        """Test TextContainer initialization."""
        self.assertEqual(self.container.name, "hostname")
        self.assertEqual(self.container.provider, self.provider)
        self.assertEqual(self.container.prefix, "Host: ")
        # Text is initialized to empty string in the current implementation
        self.assertEqual(self.container.text, "")
        
    def test_update(self):
        """Test updating the text value."""
        self.container.update()
        # In the current implementation, the prefix is not automatically added
        self.assertEqual(self.container.text, "hostname")
        
        # Ensure the provider was called
        self.provider.assert_called_once()
        
    def test_render(self):
        """Test rendering the text."""
        # Update the container first
        self.container.update()
        
        # Render the container
        self.container.render(self.draw, self.fonts)
        
        # Verify text was drawn
        self.draw.text.assert_called_once()


class TestDividerContainer(unittest.TestCase):
    """Test cases for the DividerContainer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create the container
        self.container = DividerContainer("divider", orientation="horizontal")
        self.container.set_position(10, 20, 100, 5)
        self.container.show()
        
        # Create mock draw object
        self.draw = MagicMock(spec=ImageDraw.ImageDraw)
        self.fonts = {}
    
    def test_initialization(self):
        """Test DividerContainer initialization."""
        self.assertEqual(self.container.name, "divider")
        self.assertEqual(self.container.orientation, "horizontal")
        
    def test_render(self):
        """Test rendering the divider."""
        # Render the container
        self.container.render(self.draw, self.fonts)
        
        # Verify line was drawn
        self.draw.line.assert_called_once()


if __name__ == '__main__':
    unittest.main()
