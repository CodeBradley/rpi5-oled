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
from layout.grid import GridLayout, GridArea
from layout.containers import Container
from fonts.icons import load_fonts


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
        
        # Initialize grid layout and areas
        self.grid = GridLayout(width, height)
        self.areas = {}
        
        # Load fonts
        self.fonts = load_fonts(icon_size=16, text_size=10)
        
        # Dictionary of containers to render
        self.containers: Dict[str, Container] = {}
        
        # Flag to track display state
        self.is_on = True
        
        # Track last update time
        self.last_update = 0
        
        # Create standard layout
        self.create_standard_layout()
    
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
    
    def create_standard_layout(self) -> Dict[str, GridArea]:
        """
        Create a standard layout grid with predefined areas.
        
        Returns:
            Dictionary of named grid areas for component placement
        """
        logging.debug("Creating standard layout with dimensions: %dx%d", self.width, self.height)
        
        # Create main grid layout
        self.grid = GridLayout(self.width, self.height)
        logging.debug("Created grid layout with root area: %s", self.grid.root)
        
        # For a 128x32 display, optimize the layout with these specific proportions
        
        # Split into top section for metrics and a small section at bottom for hostname/icons
        # The 128x32 display needs more space for metrics, less for bottom info
        areas = self.grid.split_area('root', direction='horizontal', sizes=[0.8, 0.2])
        top, bottom = areas[0], areas[1]
        logging.debug("Split root into top (%s) and bottom (%s)", top, bottom)
        
        # Split top into metrics section (wider) and services section (narrower)
        areas = self.grid.split_area(top.name, direction='vertical', sizes=[0.8, 0.2])
        metrics_area, services_area = areas[0], areas[1]
        logging.debug("Split top into metrics (%s) and services (%s)", metrics_area, services_area)
        
        # Split metrics area into even thirds for CPU, memory, temperature
        areas = self.grid.split_area(metrics_area.name, direction='vertical', count=3, sizes=[0.33, 0.33, 0.34])
        cpu_col, memory_col, temp_col = areas[0], areas[1], areas[2]
        logging.debug("Split metrics into cpu (%s), memory (%s), and temperature (%s)", 
                     cpu_col, memory_col, temp_col)
        
        # Use the bottom area as a single area for hostname/IP
        # For a tiny display, we'll put hostname and IP in the same area
        hostname_area = bottom
        ip_area = bottom  # Same as hostname for now, to be displayed on same line or alternating
        
        # Create areas dictionary
        self.areas = {
            'root': self.grid.root,
            'top': top,
            'bottom': bottom,
            'metrics': metrics_area,
            'services': services_area,
            'cpu': cpu_col,
            'memory': memory_col,
            'temperature': temp_col,
            'hostname': hostname_area,
            'ip_address': ip_area
        }
        logging.debug("Created areas dictionary with %d entries: %s", 
                     len(self.areas), list(self.areas.keys()))
        
        # Check if grid areas match dictionary
        for name, area in self.areas.items():
            if name != 'root' and not self.grid.has_area(area.name):
                logging.error("Area '%s' exists in areas dict but not in grid!", name)
        
        return self.areas
    
    def clear(self) -> None:
        """Clear the display buffer."""
        self.draw.rectangle((0, 0, self.width, self.height), fill=0)
    
    def show(self) -> None:
        """Update the physical display with the current buffer."""
        try:
            logging.debug("Displaying image to physical device")
            pixels = list(self.image.getdata())
            white_pixels = sum(1 for p in pixels if p > 0)
            logging.debug(f"Image has {white_pixels} lit pixels out of {len(pixels)}")
            self.device.display(self.image)
            self.last_update = time.time()
            logging.debug(f"Display updated at {self.last_update}")
        except Exception as e:
            logging.error(f"Error updating display: {e}")
    
    def add_container(self, container: Container, area_name: str) -> None:
        """
        Add a container to a grid area for rendering.
        
        Args:
            container: Container to add
            area_name: Name of the grid area to place the container in
        
        Raises:
            KeyError: If the area does not exist
        """
        # First check if area exists in our areas dictionary
        if area_name not in self.areas:
            raise KeyError(f"Grid area '{area_name}' does not exist in areas dictionary")
            
        # Use the area from our dictionary, not directly from the grid
        area = self.areas[area_name]
        
        logging.debug("Adding container '%s' to area '%s' (grid name: '%s')", 
                     container.name, area_name, area.name)
        
        # Set position based on grid area
        container.set_position(area.x, area.y, area.width, area.height)
        
        # Enable debug mode to visualize grid boundaries
        container.debug = True
        
        self.containers[container.name] = container
    
    def remove_container(self, container_name: str) -> None:
        """
        Remove a container from the display.
        
        Args:
            container_name: Name of the container to remove
        """
        if container_name in self.containers:
            del self.containers[container_name]
    
    def update_containers(self) -> None:
        """Update all containers with fresh data."""
        for container in self.containers.values():
            container.update()
    
    def render_containers(self) -> None:
        """Render all containers to the display buffer."""       
        logging.debug(f"Rendering {len(self.containers)} containers to buffer")
        for i, container in enumerate(self.containers.values()):
            logging.debug(f"  Rendering container {i+1}/{len(self.containers)}: {container.name}")
            container.render(self.draw, self.fonts)
        logging.debug("Finished rendering all containers")
    
    def update(self, force: bool = False) -> bool:
        """
        Update the display with the current container data.
        
        Args:
            force: Whether to force an update even if no data has changed
        
        Returns:
            True if the display was updated, False otherwise
        """
        try:
            # Update container data
            self.update_containers()
            
            # Clear the display buffer
            self.clear()
            
            # Render containers to buffer
            self.render_containers()
            
            # Update physical display
            self.show()
            
            return True
        
        except Exception as e:
            logging.error(f"Error in update: {e}")
            return False
    
    def draw_text(self, position: Tuple[int, int], text: str, 
                  font_name: str = 'text', fill: int = 1) -> None:
        """
        Draw text at the specified position.
        
        Args:
            position: (x, y) coordinates
            text: Text to draw
            font_name: Name of font to use
            fill: Fill color (1 for white, 0 for black)
        """
        if font_name not in self.fonts:
            logging.warning(f"Font '{font_name}' not found, using default text font")
            font_name = 'text'
        
        self.draw.text(position, text, font=self.fonts[font_name], fill=fill)
    
    def draw_icon(self, position: Tuple[int, int], icon_code: str, 
                 font_name: str = 'icon', fill: int = 1) -> None:
        """
        Draw an icon at the specified position.
        
        Args:
            position: (x, y) coordinates
            icon_code: Unicode character code for the icon
            font_name: Name of font to use
            fill: Fill color (1 for white, 0 for black)
        """
        if font_name not in self.fonts:
            logging.warning(f"Font '{font_name}' not found, using default icon font")
            font_name = 'icon'
        
        self.draw.text(position, icon_code, font=self.fonts[font_name], fill=fill)
    
    def turn_off(self) -> None:
        """Turn off the display (power saving)."""
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
    
    def cleanup(self) -> None:
        """Clean up resources before shutdown."""
        try:
            # Clear display before shutdown
            self.clear()
            self.show()
            logging.info("Display cleaned up for shutdown")
        except Exception as e:
            logging.error(f"Error during display cleanup: {e}")
