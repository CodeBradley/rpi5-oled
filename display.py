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
            area_name: Name of the grid area to place the container in
        
        Raises:
            KeyError: If the area does not exist
        """
        area = self.layout.get_area(area_name)
        container.set_position(area.x, area.y, area.width, area.height)
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
        for container in self.containers.values():
            container.render(self.draw, self.fonts)
    
    def update_display(self, force: bool = False) -> bool:
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
            logging.error(f"Error in update_display: {e}")
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
