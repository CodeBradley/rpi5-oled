#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Icon font utilities and mappings.

This module provides utilities for working with icon fonts,
particularly the custom BoxIcons font, including Unicode mappings.
"""

import os
from typing import Dict
import logging
from PIL import ImageFont

# Base directory for fonts
FONTS_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the custom BoxIcons font
BOXICONS_FONT_PATH = os.path.join(FONTS_DIR, 'lakenet-boxicons.ttf')

# BoxIcons Unicode mappings
ICONS = {
    # System metrics
    'memory': '\uf538',      # RAM/memory (microchip icon in BoxIcons)
    'cpu': '\uf2e1',         # CPU (chip icon in BoxIcons)
    'temperature': '\uf2ca', # Temperature (thermometer icon in BoxIcons)
    'disk': '\uf38f',        # Disk (hard drive icon in BoxIcons)
    'network': '\uf2c8',     # Network (network icon in BoxIcons)
    
    # Services
    'docker': '\uf308',      # Docker (container icon in BoxIcons)
    'ceph': '\uef5b',        # CephFS (custom glyph at uniEF5B)
    'kubernetes': '\uf30b',  # Kubernetes
    'nginx': '\uf2da',       # Nginx (server icon in BoxIcons)
    'apache': '\uf2da',      # Apache (server icon in BoxIcons)
    'mysql': '\uf300',       # MySQL (database icon in BoxIcons)
    'postgresql': '\uf300',  # PostgreSQL (database icon in BoxIcons)
    'redis': '\uf300',       # Redis (database icon in BoxIcons)
    
    # Status indicators
    'check': '\uf26a',       # Check mark (success)
    'error': '\uf26b',       # X mark (error)
    'warning': '\uf333',     # Warning triangle
    'info': '\uf59e',        # Information
}


def load_icon_font(size: int = 16) -> ImageFont.FreeTypeFont:
    """
    Load the BoxIcons font at the specified size.
    
    Args:
        size: Font size in points
        
    Returns:
        Loaded font object
        
    Raises:
        FileNotFoundError: If the font file doesn't exist
        IOError: If the font file can't be loaded
    """
    if not os.path.exists(BOXICONS_FONT_PATH):
        logging.error(f"BoxIcons font not found at: {BOXICONS_FONT_PATH}")
        raise FileNotFoundError(f"BoxIcons font not found: {BOXICONS_FONT_PATH}")
    
    try:
        return ImageFont.truetype(BOXICONS_FONT_PATH, size)
    except IOError as e:
        logging.error(f"Failed to load BoxIcons font: {e}")
        raise IOError(f"Failed to load BoxIcons font: {e}")


def get_icon_code(name: str) -> str:
    """
    Get the Unicode character code for the named icon.
    
    Args:
        name: Name of the icon
        
    Returns:
        Unicode character code for the icon
        
    Raises:
        KeyError: If the icon name is not recognized
    """
    if name not in ICONS:
        logging.warning(f"Unknown icon name: {name}, using default")
        return ICONS.get('info', '?')  # Default fallback
    
    return ICONS[name]


def load_fonts(icon_size: int = 16, text_size: int = 10) -> Dict[str, ImageFont.FreeTypeFont]:
    """
    Load all fonts needed for the display.
    
    Args:
        icon_size: Size for icon font
        text_size: Size for text font
        
    Returns:
        Dictionary of loaded fonts
    """
    fonts = {}
    
    try:
        # Load fonts with exact sizes from mockup
        
        # Metrics and service icons: 6px height
        fonts['metric_icon'] = load_icon_font(6)  
        fonts['service_icon'] = load_icon_font(6)
        
        # Metrics text: 12px (main value)
        fonts['metric_text'] = ImageFont.load_default()
        
        # Hostname/IP: 10px
        fonts['hostname_text'] = ImageFont.load_default()
        
        # Try to find better fonts (Helvetica or alternatives)
        system_fonts = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux alternative
            '/usr/share/fonts/TTF/DejaVuSans.ttf',               # Another Linux location
            '/System/Library/Fonts/Helvetica.ttc'                 # macOS
        ]
        
        for font_path in system_fonts:
            if os.path.exists(font_path):
                try:
                    # Set exact font sizes from the mockup
                    fonts['metric_text'] = ImageFont.truetype(font_path, 12)  # 12px for metrics
                    fonts['hostname_text'] = ImageFont.truetype(font_path, 10)  # 10px for hostname/IP
                    break
                except IOError:
                    continue
    
    except Exception as e:
        logging.error(f"Error loading fonts: {e}")
    
    return fonts
