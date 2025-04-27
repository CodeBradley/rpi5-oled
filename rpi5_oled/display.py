#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OLED Display controller for Raspberry Pi.

This module manages the OLED display hardware and rendering,
using the luma.oled library to communicate with the display.
"""

import os
import time
import logging
from typing import Dict, List, Tuple, Optional, Any
from PIL import Image, ImageDraw
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from rpi5_oled.layout.grid import GridLayout, GridArea
from rpi5_oled.layout.containers import Container
from rpi5_oled.fonts.icons import load_fonts


class OLEDDisplay:
    """
    Controller for OLED display hardware and rendering.
    
    This class manages the OLED display hardware, rendering content
    to the display using the grid layout and container system.
    
    Attributes:
        width: Display width in pixels
        height: Display height in pixels
        layout: GridLayout instance for organizing content
        containers: Dictionary of containers to render
        i2c_port: I2C port number
        i2c_address: I2C device address
    """
    
    def __init__(self, 
                width: int = 128, 
                height: int = 32, 
                i2c_port: int = 1, 
                i2c_address: int = 0x3C,
                rotation: int = 0,
                contrast: int = 255,
                inverted: bool = False):
        """
        Initialize the OLED display controller.
        
        Args:
            width: Display width in pixels
            height: Display height in pixels
            i2c_port: I2C port number
            i2c_address: I2C device address
            rotation: Display rotation (0, 1, 2, or 3 for 0, 90, 180, or 270 degrees)
            contrast: Display contrast (0-255)
            inverted: Whether to invert display colors
        """
        self.width = width
        self.height = height
        self.i2c_port = i2c_port
        self.i2c_address = i2c_address
        self.rotation = rotation
        self.contrast = contrast
        self.inverted = inverted
        
        # Initialize I2C and display
        self._initialize_display()
        
        # Create PIL image and drawing context
        self.image = Image.new("1", (width, height))
        self.draw = ImageDraw.Draw(self.image)
        
        # Load fonts
        self.fonts = load_fonts(icon_size=16, text_size=10)
        
        # Create grid layout
        self.layout = GridLayout(width, height)
        
        # Dictionary of containers to render
        self.containers: Dict[str, Container] = {}
        
        # Flag to track display state
        self.is_on = True
        
        # Track last update time
        self.last_update = 0
    
    def _initialize_display(self) -> None:
        """
        Initialize the OLED display hardware.
        
        Raises:
            RuntimeError: If the display initialization fails
        """
        try:
            # Initialize I2C interface
            self.serial = i2c(port=self.i2c_port, address=self.i2c_address)
            
            # Initialize OLED device
            self.device = ssd1306(
                self.serial,
                width=self.width,
                height=self.height,
                rotate=self.rotation
            )
            
            # Set contrast and mode
            self.device.contrast(self.contrast)
            
            # Set display mode (inverted or normal)
            if self.inverted:
                self.device.invert(True)
            
            logging.info(
                f"Initialized SSD1306 OLED display: "
                f"{self.width}x{self.height}, I2C address: 0x{self.i2c_address:X}"
            )
        
        except Exception as e:
            logging.error(f"Failed to initialize OLED display: {e}")
            raise RuntimeError(f"Failed to initialize OLED display: {e}")
    
    def clear(self) -> None:
        """Clear the display buffer."""
        self.draw.rectangle((0, 0, self.width, self.height), fill=0)
    
    def show(self) -> None:
        """Update the physical display with the current buffer."""
        try:
            self.device.display(self.image)
            self.last_update = time.time()
        except Exception as e:
            logging.error(f"Error updating display: {e}")
    
    def add_container(self, container: Container, area_name: str) -> None:
        """
        Add a container to a grid area for rendering.
        
        Args:
            container: Container to add
            area_name: Name of the grid area to place the container
            
        Raises:
            KeyError: If the grid area does not exist
        """
        area = self.layout.get_area(area_name)
        container.set_position(area.x, area.y, area.width, area.height)
        self.containers[container.name] = container
    
    def remove_container(self, container_name: str) -> None:
        """
        Remove a container.
        
        Args:
            container_name: Name of the container to remove
            
        Raises:
            KeyError: If the container does not exist
        """
        if container_name in self.containers:
            del self.containers[container_name]
    
    def update_containers(self) -> None:
        """Update all containers' content."""
        for container in self.containers.values():
            container.update()
    
    def render(self) -> None:
        """Render all containers to the display buffer."""
        self.clear()
        
        for container in self.containers.values():
            container.render(self.draw, self.fonts)
        
        self.show()
    
    def update(self) -> None:
        """Update container content and render the display."""
        self.update_containers()
        self.render()
    
    def turn_off(self) -> None:
        """Turn off the display."""
        if self.is_on:
            try:
                self.device.hide()
                self.is_on = False
                logging.info("Display turned off")
            except Exception as e:
                logging.error(f"Error turning off display: {e}")
    
    def turn_on(self) -> None:
        """Turn on the display."""
        if not self.is_on:
            try:
                self.device.show()
                self.is_on = True
                logging.info("Display turned on")
            except Exception as e:
                logging.error(f"Error turning on display: {e}")
    
    def set_contrast(self, contrast: int) -> None:
        """
        Set display contrast.
        
        Args:
            contrast: Contrast value (0-255)
        """
        if 0 <= contrast <= 255:
            try:
                self.device.contrast(contrast)
                self.contrast = contrast
            except Exception as e:
                logging.error(f"Error setting contrast: {e}")
    
    def set_inverted(self, inverted: bool) -> None:
        """
        Set display inversion mode.
        
        Args:
            inverted: Whether to invert display colors
        """
        try:
            self.device.invert(inverted)
            self.inverted = inverted
        except Exception as e:
            logging.error(f"Error setting inversion mode: {e}")
    
    def cleanup(self) -> None:
        """Clean up resources and turn off the display."""
        try:
            self.clear()
            self.show()
            self.device.cleanup()
            logging.info("Display cleaned up")
        except Exception as e:
            logging.error(f"Error cleaning up display: {e}")
    
    def reset(self) -> None:
        """Reset the display by reinitializing it."""
        try:
            self.cleanup()
            self._initialize_display()
            logging.info("Display reset")
        except Exception as e:
            logging.error(f"Error resetting display: {e}")
            raise RuntimeError(f"Failed to reset display: {e}")
    
    def create_standard_layout(self) -> Dict[str, GridArea]:
        """
        Create a standard layout for the OLED display.
        
        This creates a layout with areas for:
        - Top row with 3 metrics
        - Service icons
        - Divider
        - Hostname
        - IP address
        
        Returns:
            Dictionary of created grid areas
        """
        # Split the display into 3 main vertical sections
        main_areas = self.layout.split_area(
            "root", 
            direction="vertical", 
            count=3, 
            sizes=[0.4, 0.1, 0.5]  # 40% top, 10% divider, 50% bottom
        )
        
        # Name the main areas
        metrics_area = main_areas[0]
        metrics_area.name = "metrics"
        
        divider_area = main_areas[1]
        divider_area.name = "divider"
        
        info_area = main_areas[2]
        info_area.name = "info"
        
        # Add areas to the layout
        self.layout.areas["metrics"] = metrics_area
        self.layout.areas["divider"] = divider_area
        self.layout.areas["info"] = info_area
        
        # Split metrics area into metrics and services
        metrics_split = self.layout.split_area(
            "metrics", 
            direction="horizontal", 
            count=2, 
            sizes=[0.6, 0.4]  # 60% metrics, 40% services
        )
        
        resource_metrics = metrics_split[0]
        resource_metrics.name = "resource_metrics"
        
        services = metrics_split[1]
        services.name = "services"
        
        self.layout.areas["resource_metrics"] = resource_metrics
        self.layout.areas["services"] = services
        
        # Create 3 equal metric sections in the resource_metrics area
        metrics_grid = self.layout.split_area(
            "resource_metrics", 
            direction="horizontal", 
            count=3
        )
        
        for i, metric in enumerate(metrics_grid):
            metric.name = f"metric_{i}"
            self.layout.areas[metric.name] = metric
        
        # Split info area into hostname and IP address
        info_split = self.layout.split_area(
            "info", 
            direction="vertical", 
            count=2
        )
        
        hostname = info_split[0]
        hostname.name = "hostname"
        
        ip_address = info_split[1]
        ip_address.name = "ip_address"
        
        self.layout.areas["hostname"] = hostname
        self.layout.areas["ip_address"] = ip_address
        
        return self.layout.areas
