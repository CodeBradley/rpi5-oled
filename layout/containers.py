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
        self.icon_size = 6
        self.value_size = 6
    
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
            
        if 'metric_icon' not in fonts or 'metric_text' not in fonts:
            # Fall back to other fonts if needed
            icon_font = fonts.get('small_icon', fonts.get('icon', None))
            text_font = fonts.get('small', fonts.get('text', None))
            if icon_font is None or text_font is None:
                logging.error("Required fonts are missing")
                return
        else:
            # Use the right font sizes from the mockup
            icon_font = fonts['metric_icon']  # 6px for icons
            text_font = fonts['metric_text']  # 12px for metrics text
            
        # For simple layout, center everything in the column
        
        # Format the value - integers for percentage
        value = self.value if self.value is not None else 0
        if self.unit == "%":
            value_text = f"{int(value)}{self.unit}"
        else:
            value_text = f"{value}{self.unit}"
        
        # Center value in container
        text_width = text_font.getsize(value_text)[0] if hasattr(text_font, 'getsize') else 0
        text_x = self.x + (self.width - text_width) // 2
        text_y = self.y + (self.height // 2) - 2  # Position in center
        
        # For icon placement, position it slightly higher
        icon_width = icon_font.getsize(self.icon_code)[0] if hasattr(icon_font, 'getsize') else 0
        icon_x = self.x + (self.width - icon_width) // 2
        # Position icon in top third of the container
        icon_y = self.y + (self.height // 3) - 6
        
        # Draw the icon centered in upper part
        draw.text(
            (icon_x, icon_y),
            self.icon_code,
            font=icon_font,
            fill=self.text_color
        )
        
        # Position value text in bottom half of container
        # This creates more space between icon and value
        draw.text(
            (text_x, text_y + 2),  # Move text down slightly
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
        self.icon_size = 6
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
            
        if 'small_icon' not in fonts:
            logging.error("Small icon font is missing")
            return
        
        icon_font = fonts['small_icon']
        
        # For tiny displays, show icons in a vertical stack
        service_count = len(self.services)
        
        # Calculate spacing between icons
        total_height = service_count * self.icon_size
        padding = 0
        if total_height < self.height:
            padding = (self.height - total_height) // (service_count + 1)
        
        # Set base position (centered horizontally)
        base_x = self.x + (self.width - self.icon_size) // 2
        current_y = self.y + padding
        
        # Draw each service icon vertically stacked
        for service_name, (icon_code, _) in self.services.items():
            is_active = self.statuses.get(service_name, False)
            
            # Draw the icon
            draw.text(
                (base_x, current_y),
                icon_code,
                font=icon_font,
                fill=self.active_color if is_active else self.inactive_color
            )
            
            # For inactive services, use a different visual indicator (dimming)
            # instead of a strike-through to save space
            
            # Move to the next icon position
            current_y += self.icon_size + padding


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
        
        # Use smaller font for small displays
        text_font = fonts['small'] if 'small' in fonts else fonts['text']
        
        # Truncate text if too long for small display
        max_chars = 15  # Adjust based on display width and font size
        text = self.text if self.text else "N/A"
        if len(text) > max_chars:
            text = text[:max_chars-2] + ".."  # Truncate with ellipsis
            
        display_text = f"{self.prefix}{text}"
        
        # Center vertically
        font_height = 8  # Estimated font height
        y = self.y + (self.height - font_height) // 2
        
        # Calculate text position based on alignment
        text_width = text_font.getsize(display_text)[0] if hasattr(text_font, 'getsize') else 0
        
        if self.alignment == "left":
            x = self.x + 2  # Small padding
        elif self.alignment == "center":
            x = self.x + (self.width - text_width) // 2
        else:  # right
            x = self.x + self.width - text_width - 2  # Small padding
        
        draw.text((x, y), display_text, font=text_font, fill=self.text_color)


class IconContainer(Container):
    """
    Container for displaying an icon from the icon font.
    
    This container displays only an icon, useful for metric icons
    without values.
    """
    
    def __init__(self, name: str, icon_code: str):
        """
        Initialize an icon container.
        
        Args:
            name: Unique identifier for this container
            icon_code: Unicode character code for the icon
        """
        super().__init__(name)
        self.icon_code = icon_code
        self.icon_size = 6  # Use the size from mockup
        self.icon_color = 1  # White in monochrome display
    
    def update(self) -> None:
        """Update method, no-op for icons."""
        pass
    
    def render(self, draw, fonts: Dict) -> None:
        """
        Render the icon.
        
        Args:
            draw: PIL ImageDraw instance
            fonts: Dictionary of available fonts
        """
        if not self.visible:
            return
            
        super().render(draw, fonts)
            
        if 'metric_icon' not in fonts:
            if 'small_icon' not in fonts:
                logging.error("Icon font is missing")
                return
            icon_font = fonts['small_icon']
        else:
            icon_font = fonts['metric_icon']
        
        # Center the icon in the container
        x = self.x + (self.width - self.icon_size) // 2
        y = self.y + (self.height - self.icon_size) // 2
        
        # Draw the icon
        draw.text(
            (x, y),
            self.icon_code,
            font=icon_font,
            fill=self.icon_color
        )


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
