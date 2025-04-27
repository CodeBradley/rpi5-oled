#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Container components for OLED display layouts.

This module provides various container types that can be placed
in grid areas to display different kinds of content.
"""

from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from abc import ABC, abstractmethod
import logging


class Container(ABC):
    """
    Abstract base class for all display containers.
    
    A container is responsible for formatting and rendering
    specific types of content within a grid area.
    """
    
    def __init__(self, name: str):
        """
        Initialize a container.
        
        Args:
            name: Unique identifier for this container
        """
        self.name = name
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.visible = True  # Make containers visible by default
        self.debug = False
    
    def set_position(self, x: int, y: int, width: int, height: int) -> None:
        """
        Set the position and dimensions of this container.
        
        Args:
            x: X-coordinate (left)
            y: Y-coordinate (top)
            width: Width in pixels
            height: Height in pixels
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def show(self) -> None:
        """Show this container."""
        self.visible = True
    
    def hide(self) -> None:
        """Hide this container."""
        self.visible = False
    
    @abstractmethod
    def render(self, draw, fonts: Dict) -> None:
        """
        Render this container's content.
        
        Args:
            draw: PIL ImageDraw instance
            fonts: Dictionary of available fonts
        """
        # Draw debug rectangle if debug is enabled
        if self.debug and self.visible:
            draw.rectangle(
                [(self.x, self.y), (self.x + self.width, self.y + self.height)],
                outline=1,
                width=1
            )
    
    def __repr__(self) -> str:
        """String representation of the container."""
        return f"{self.__class__.__name__}('{self.name}', pos=({self.x}, {self.y}), size=({self.width}, {self.height}))"


class MetricContainer(Container):
    """
    Container for displaying a system metric with an icon and value.
    
    This container is designed to show system metrics like CPU usage,
    RAM usage, temperature, etc. with an associated icon.
    """
    
    def __init__(self, name: str, icon_code: str, provider: Callable, unit: str = "%"):
        """
        Initialize a metric container.
        
        Args:
            name: Unique identifier for this container
            icon_code: Unicode character code for the icon
            provider: Function that returns the current value
            unit: Unit to display after the value
        """
        super().__init__(name)
        self.icon_code = icon_code
        self.provider = provider
        self.unit = unit
        self.value = 0
        self.text_color = 1  # White in monochrome display
        self.icon_size = 12
        self.value_size = 10
    
    def update(self) -> None:
        """Update the metric value from the provider."""
        try:
            self.value = self.provider()
        except Exception as e:
            logging.error(f"Error updating metric {self.name}: {e}")
            self.value = None
    
    def render(self, draw, fonts: Dict) -> None:
        """
        Render the metric with its icon and value.
        
        Args:
            draw: PIL ImageDraw instance
            fonts: Dictionary of available fonts
        """
        if not self.visible:
            return
            
        super().render(draw, fonts)
            
        if 'icon' not in fonts or 'text' not in fonts:
            logging.error("Required fonts are missing")
            return
        
        icon_font = fonts['icon']
        text_font = fonts['text']
        
        # Draw the icon
        draw.text(
            (self.x, self.y), 
            self.icon_code, 
            font=icon_font, 
            fill=self.text_color
        )
        
        # Draw the value
        value_text = f"{self.value}{self.unit}" if self.value is not None else "N/A"
        draw.text(
            (self.x + self.icon_size + 2, self.y),  # Position after icon with padding
            value_text,
            font=text_font,
            fill=self.text_color
        )


class ServiceIconContainer(Container):
    """
    Container for displaying service status icons.
    
    This container shows the status of services like Docker, CephFS, etc.
    using icons that indicate whether the service is running or not.
    """
    
    def __init__(self, name: str, services: Dict[str, Tuple[str, Callable]]):
        """
        Initialize a service icon container.
        
        Args:
            name: Unique identifier for this container
            services: Dictionary mapping service names to (icon_code, status_provider) tuples
        """
        super().__init__(name)
        self.services = services
        self.statuses = {}
        self.icon_size = 16
        self.active_color = 1  # White in monochrome display
        self.inactive_color = 0  # Black in monochrome display
        self.icon_spacing = 2
    
    def update(self) -> None:
        """Update all service statuses from their providers."""
        for service_name, (_, provider) in self.services.items():
            try:
                self.statuses[service_name] = provider()
            except Exception as e:
                logging.error(f"Error updating service {service_name}: {e}")
                self.statuses[service_name] = False
    
    def render(self, draw, fonts: Dict) -> None:
        """
        Render the service icons.
        
        Args:
            draw: PIL ImageDraw instance
            fonts: Dictionary of available fonts
        """
        if not self.visible:
            return
            
        super().render(draw, fonts)
            
        if 'icon' not in fonts:
            logging.error("Icon font is missing")
            return
        
        icon_font = fonts['icon']
        
        # Calculate grid layout based on number of services
        service_count = len(self.services)
        columns = min(2, service_count)
        rows = (service_count + columns - 1) // columns  # Ceiling division
        
        # Calculate icon spacing
        total_width = columns * self.icon_size + (columns - 1) * self.icon_spacing
        total_height = rows * self.icon_size + (rows - 1) * self.icon_spacing
        
        # Start position to center the icons
        start_x = self.x + (self.width - total_width) // 2
        start_y = self.y + (self.height - total_height) // 2
        
        # Draw each service icon
        i = 0
        for service_name, (icon_code, _) in self.services.items():
            status = self.statuses.get(service_name, False)
            
            # Calculate position in the grid
            col = i % columns
            row = i // columns
            
            x = start_x + col * (self.icon_size + self.icon_spacing)
            y = start_y + row * (self.icon_size + self.icon_spacing)
            
            # Draw the icon with color based on status
            fill_color = self.active_color if status else self.inactive_color
            
            # For monochrome display, we may need to use different icons for active/inactive
            # or use a background rectangle to indicate status
            if not status:
                # Draw a diagonal strike-through for inactive services
                padding = 2
                draw.line(
                    [(x + padding, y + padding), (x + self.icon_size - padding, y + self.icon_size - padding)],
                    fill=self.active_color,
                    width=1
                )
                draw.line(
                    [(x + padding, y + self.icon_size - padding), (x + self.icon_size - padding, y + padding)],
                    fill=self.active_color,
                    width=1
                )
            
            draw.text((x, y), icon_code, font=icon_font, fill=self.active_color)
            i += 1


class TextContainer(Container):
    """
    Container for displaying text information.
    
    This container is designed for displaying textual information
    like hostname, IP address, etc.
    """
    
    def __init__(self, name: str, provider: Callable, prefix: str = ""):
        """
        Initialize a text container.
        
        Args:
            name: Unique identifier for this container
            provider: Function that returns the text to display
            prefix: Optional prefix to display before the text
        """
        super().__init__(name)
        self.provider = provider
        self.prefix = prefix
        self.text = ""
        self.text_color = 1  # White in monochrome display
        self.alignment = "left"  # left, center, right
    
    def update(self) -> None:
        """Update the text from the provider."""
        try:
            self.text = self.provider()
        except Exception as e:
            logging.error(f"Error updating text {self.name}: {e}")
            self.text = "N/A"
    
    def render(self, draw, fonts: Dict) -> None:
        """
        Render the text.
        
        Args:
            draw: PIL ImageDraw instance
            fonts: Dictionary of available fonts
        """
        if not self.visible:
            return
            
        super().render(draw, fonts)
            
        if 'text' not in fonts:
            logging.error("Text font is missing")
            return
        
        text_font = fonts['text']
        display_text = f"{self.prefix}{self.text}" if self.text else f"{self.prefix}N/A"
        
        # Calculate text position based on alignment
        text_width = text_font.getsize(display_text)[0] if hasattr(text_font, 'getsize') else 0
        
        if self.alignment == "left":
            x = self.x
        elif self.alignment == "center":
            x = self.x + (self.width - text_width) // 2
        else:  # right
            x = self.x + self.width - text_width
        
        draw.text((x, self.y), display_text, font=text_font, fill=self.text_color)


class DividerContainer(Container):
    """
    Container for displaying a divider line.
    
    This container renders a horizontal or vertical divider line
    to separate different sections of the display.
    """
    
    def __init__(self, name: str, orientation: str = "horizontal"):
        """
        Initialize a divider container.
        
        Args:
            name: Unique identifier for this container
            orientation: "horizontal" or "vertical"
        """
        super().__init__(name)
        self.orientation = orientation
        self.line_color = 1  # White in monochrome display
        self.line_width = 1
    
    def update(self) -> None:
        """Update the divider (no-op)."""
        pass
    
    def render(self, draw, fonts: Dict) -> None:
        """
        Render the divider line.
        
        Args:
            draw: PIL ImageDraw instance
            fonts: Dictionary of available fonts (not used)
        """
        if not self.visible:
            return
            
        super().render(draw, fonts)
            
        if self.orientation == "horizontal":
            # Center the line vertically
            y = self.y + self.height // 2
            draw.line([(self.x, y), (self.x + self.width, y)], fill=self.line_color, width=self.line_width)
        else:  # vertical
            # Center the line horizontally
            x = self.x + self.width // 2
            draw.line([(x, self.y), (x, self.y + self.height)], fill=self.line_color, width=self.line_width)
