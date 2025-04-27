#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grid layout system for OLED display.

This module provides a flexible grid layout system for organizing content
on the OLED display, similar to CSS grid layouts.
"""

from typing import Dict, List, Tuple, Optional, Union, Any
import logging

# Type aliases
Position = Tuple[int, int]
Size = Tuple[int, int]
Rect = Tuple[int, int, int, int]  # x, y, width, height


class GridArea:
    """
    Represents a rectangular area in the grid layout.
    
    Attributes:
        name: Unique identifier for this grid area
        rect: (x, y, width, height) in pixels
        content: Content to be displayed in this area
    """
    
    def __init__(self, name: str, rect: Rect, content: Any = None):
        """
        Initialize a grid area.
        
        Args:
            name: Unique identifier for this area
            rect: (x, y, width, height) in pixels
            content: Content to be displayed in this area
        """
        self.name = name
        self.rect = rect
        self.content = content
        self.children: List[GridArea] = []
    
    @property
    def x(self) -> int:
        """Get the x-coordinate of the area."""
        return self.rect[0]
    
    @property
    def y(self) -> int:
        """Get the y-coordinate of the area."""
        return self.rect[1]
    
    @property
    def width(self) -> int:
        """Get the width of the area."""
        return self.rect[2]
    
    @property
    def height(self) -> int:
        """Get the height of the area."""
        return self.rect[3]
    
    def contains_point(self, x: int, y: int) -> bool:
        """
        Check if this area contains the given point.
        
        Args:
            x: X-coordinate to check
            y: Y-coordinate to check
            
        Returns:
            True if the point is inside this area, False otherwise
        """
        return (self.x <= x < self.x + self.width and
                self.y <= y < self.y + self.height)
    
    def add_child(self, child: 'GridArea') -> None:
        """
        Add a child area to this area.
        
        Args:
            child: Child grid area to add
        """
        self.children.append(child)
    
    def __repr__(self) -> str:
        """String representation of the grid area."""
        return f"GridArea('{self.name}', {self.rect})"


class GridLayout:
    """
    Grid layout manager for organizing content on the OLED display.
    
    This class provides a flexible grid system for positioning elements
    on the OLED display, similar to CSS grid layouts.
    
    Attributes:
        width: Total width of the display in pixels
        height: Total height of the display in pixels
        areas: Dictionary of named grid areas
    """
    
    def __init__(self, width: int, height: int):
        """
        Initialize a grid layout.
        
        Args:
            width: Width of the display in pixels
            height: Height of the display in pixels
        """
        self.width = width
        self.height = height
        self.areas: Dict[str, GridArea] = {}
        
        # Create the root area covering the entire display
        self.root = GridArea("root", (0, 0, width, height))
    
    def add_area(self, name: str, rect: Rect, parent: Optional[str] = None) -> GridArea:
        """
        Add a new grid area to the layout.
        
        Args:
            name: Unique identifier for this area
            rect: (x, y, width, height) in pixels
            parent: Optional parent area name
            
        Returns:
            The created GridArea
            
        Raises:
            ValueError: If the area extends beyond the display or overlaps with an existing area
        """
        # Validate area dimensions
        x, y, w, h = rect
        if x < 0 or y < 0 or x + w > self.width or y + h > self.height:
            raise ValueError(f"Area '{name}' extends beyond display dimensions")
        
        # Create the new area
        area = GridArea(name, rect)
        self.areas[name] = area
        
        # Add as child to parent if specified, otherwise to root
        if parent:
            if parent not in self.areas:
                raise ValueError(f"Parent area '{parent}' does not exist")
            self.areas[parent].add_child(area)
        else:
            self.root.add_child(area)
            
        return area
    
    def get_area(self, name: str) -> GridArea:
        """
        Get a grid area by name.
        
        Args:
            name: Name of the grid area to retrieve
            
        Returns:
            The requested GridArea
            
        Raises:
            KeyError: If the area does not exist
        """
        if name not in self.areas:
            raise KeyError(f"Grid area '{name}' does not exist")
        return self.areas[name]
    
    def split_area(self, 
                   area_name: str, 
                   direction: str = "horizontal", 
                   count: int = 2, 
                   sizes: Optional[List[float]] = None) -> List[GridArea]:
        """
        Split an existing area into multiple areas.
        
        Args:
            area_name: Name of the area to split
            direction: "horizontal" or "vertical"
            count: Number of areas to create
            sizes: Optional list of relative sizes (must sum to 1.0)
            
        Returns:
            List of created GridAreas
            
        Raises:
            ValueError: If the parameters are invalid
            KeyError: If the area does not exist
        """
        area = self.get_area(area_name)
        x, y, width, height = area.rect
        
        # Validate sizes if provided
        if sizes:
            if len(sizes) != count:
                raise ValueError(f"Expected {count} sizes, got {len(sizes)}")
            if abs(sum(sizes) - 1.0) > 0.001:
                raise ValueError(f"Sizes must sum to 1.0, got {sum(sizes)}")
        else:
            # Equal sizes
            sizes = [1.0 / count] * count
        
        new_areas = []
        current_pos = 0
        
        for i in range(count):
            if direction == "horizontal":
                # Split horizontally (side by side)
                segment_width = int(width * sizes[i])
                if i == count - 1:  # Last segment gets remaining pixels
                    segment_width = width - current_pos
                rect = (x + current_pos, y, segment_width, height)
                current_pos += segment_width
            elif direction == "vertical":
                # Split vertically (top to bottom)
                segment_height = int(height * sizes[i])
                if i == count - 1:  # Last segment gets remaining pixels
                    segment_height = height - current_pos
                rect = (x, y + current_pos, width, segment_height)
                current_pos += segment_height
            else:
                raise ValueError(f"Direction must be 'horizontal' or 'vertical', got '{direction}'")
            
            new_name = f"{area_name}_{i}"
            new_area = self.add_area(new_name, rect, parent=area_name)
            new_areas.append(new_area)
        
        return new_areas
    
    def create_grid(self, area_name: str, rows: int, cols: int) -> List[List[GridArea]]:
        """
        Create a grid of areas within an existing area.
        
        Args:
            area_name: Name of the area to divide into a grid
            rows: Number of rows
            cols: Number of columns
            
        Returns:
            2D list of created GridAreas
            
        Raises:
            KeyError: If the area does not exist
            ValueError: If rows or cols are invalid
        """
        if rows < 1 or cols < 1:
            raise ValueError("Rows and columns must be positive integers")
        
        area = self.get_area(area_name)
        x, y, width, height = area.rect
        
        # Calculate cell dimensions
        cell_width = width // cols
        cell_height = height // rows
        
        # Create grid
        grid = []
        for row in range(rows):
            grid_row = []
            for col in range(cols):
                cell_x = x + col * cell_width
                cell_y = y + row * cell_height
                
                # Last row/column gets remaining pixels
                cell_w = width - col * cell_width if col == cols - 1 else cell_width
                cell_h = height - row * cell_height if row == rows - 1 else cell_height
                
                cell_name = f"{area_name}_r{row}c{col}"
                cell = self.add_area(cell_name, (cell_x, cell_y, cell_w, cell_h), parent=area_name)
                grid_row.append(cell)
            grid.append(grid_row)
        
        return grid


class FlexLayout:
    """
    Flexible layout manager that adapts based on content requirements.
    
    This class provides layouts that can adjust to different content needs,
    like showing a 2x2 grid for 4 service icons or a 1x2 grid for 2 icons.
    """
    
    def __init__(self, grid: GridLayout):
        """
        Initialize a flexible layout.
        
        Args:
            grid: GridLayout instance to build upon
        """
        self.grid = grid
    
    def create_service_grid(self, area_name: str, service_count: int) -> List[GridArea]:
        """
        Create a grid for service icons that adapts based on count.
        
        Args:
            area_name: Name of the parent area
            service_count: Number of service icons to display
            
        Returns:
            List of areas for placing service icons
            
        Raises:
            ValueError: If service_count is invalid
        """
        if service_count < 1:
            raise ValueError("Service count must be at least 1")
        
        area = self.grid.get_area(area_name)
        
        # Different layouts based on service count
        if service_count == 1:
            # Single centered icon
            icon_size = min(area.width, area.height)
            x_offset = (area.width - icon_size) // 2
            y_offset = (area.height - icon_size) // 2
            icon_area = self.grid.add_area(
                f"{area_name}_service_0",
                (area.x + x_offset, area.y + y_offset, icon_size, icon_size),
                parent=area_name
            )
            return [icon_area]
        
        elif service_count == 2:
            # Two icons side by side
            rows, cols = 1, 2
        elif service_count <= 4:
            # 2x2 grid
            rows, cols = 2, 2
        else:
            # For more than 4, use a grid with more columns
            rows = 2
            cols = (service_count + 1) // 2
        
        # Create the grid
        grid = self.grid.create_grid(area_name, rows, cols)
        
        # Flatten the grid and return only needed areas
        flat_grid = [cell for row in grid for cell in row]
        return flat_grid[:service_count]
