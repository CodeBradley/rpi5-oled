"""
Display handling for the Raspberry Pi 5 OLED display application.
Optimized for performance and reliability.
"""
import os
import logging
import time
from PIL import Image, ImageDraw, ImageFont
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
import config


class OLEDDisplay:
    """Class to manage the OLED display."""
    
    def __init__(self):
        try:
            # Initialize I2C and SSD1306
            self.serial = i2c(port=1, address=config.I2C_ADDRESS)
            self.display = ssd1306(self.serial, 
                                  width=config.DISPLAY_WIDTH, 
                                  height=config.DISPLAY_HEIGHT)
            
            # Create blank image for drawing
            self.image = Image.new("1", (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT))
            self.draw = ImageDraw.Draw(self.image)
            
            # Load default font
            self.font = ImageFont.load_default()
            
            # Calculate font height for proper line spacing
            # Use getbbox() for newer Pillow versions or fall back to getsize() for older versions
            try:
                # For newer Pillow versions
                bbox = self.font.getbbox("A")
                self.font_height = bbox[3] - bbox[1]
                logging.info(f"Using font height {self.font_height} (getbbox method)")
            except AttributeError:
                # For older Pillow versions
                self.font_height = self.font.getsize("A")[1]
                logging.info(f"Using font height {self.font_height} (getsize method)")
            
            # Store last content for change detection
            self.last_content = None
            
            # Track last update time for rate limiting
            self.last_update_time = 0
            self.min_update_interval = 0.1  # seconds
            
            # Load icons
            self.icons = self._load_icons()
            
            # Clear the display on startup
            self.clear()
            logging.info("OLED display initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing display: {e}")
            raise
    
    def _load_icons(self):
        """Load icon images with error handling and optimization."""
        icons = {}
        icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
        
        # Create icons directory if it doesn't exist
        if not os.path.exists(icons_dir):
            try:
                os.makedirs(icons_dir)
                self._create_default_icons(icons_dir)
                logging.info(f"Created icons directory and default icons at {icons_dir}")
            except Exception as e:
                logging.error(f"Failed to create icons directory: {e}")
                # Continue without icons rather than crashing
                return {}
        
        # Load all icons from the icons directory
        try:
            icon_files = [f for f in os.listdir(icons_dir) if f.endswith('.png')]
            logging.info(f"Found {len(icon_files)} icon files")
            
            for filename in icon_files:
                try:
                    icon_name = os.path.splitext(filename)[0]
                    icon_path = os.path.join(icons_dir, filename)
                    icon = Image.open(icon_path).convert("1")
                    # Use NEAREST for small icons - faster and sufficient quality
                    icons[icon_name] = icon.resize(config.ICON_SIZE, Image.NEAREST)
                except Exception as e:
                    logging.warning(f"Failed to load icon {filename}: {e}")
                    # Skip this icon but continue loading others
                    continue
        except Exception as e:
            logging.error(f"Error listing icon directory: {e}")
            # Return empty dict rather than crashing
            return {}
        
        logging.info(f"Successfully loaded {len(icons)} icons")
        return icons
    
    def _create_default_icons(self, icons_dir):
        """Create default icons if they don't exist."""
        # Create simple icons as a fallback
        # SSH icon (active)
        ssh_active = Image.new("1", config.ICON_SIZE, 0)
        draw = ImageDraw.Draw(ssh_active)
        draw.rectangle([(0, 0), (7, 7)], outline=1)
        draw.text((1, 0), "S", fill=1, font=ImageFont.load_default())
        ssh_active.save(os.path.join(icons_dir, "ssh_active.png"))
        
        # SSH icon (inactive)
        ssh_inactive = Image.new("1", config.ICON_SIZE, 0)
        draw = ImageDraw.Draw(ssh_inactive)
        draw.rectangle([(0, 0), (7, 7)], outline=1)
        draw.line([(0, 0), (7, 7)], fill=1)
        draw.line([(0, 7), (7, 0)], fill=1)
        ssh_inactive.save(os.path.join(icons_dir, "ssh_inactive.png"))
        
        # Docker icon (active)
        docker_active = Image.new("1", config.ICON_SIZE, 0)
        draw = ImageDraw.Draw(docker_active)
        draw.rectangle([(0, 0), (7, 7)], outline=1)
        draw.text((1, 0), "D", fill=1, font=ImageFont.load_default())
        docker_active.save(os.path.join(icons_dir, "docker_active.png"))
        
        # Docker icon (inactive)
        docker_inactive = Image.new("1", config.ICON_SIZE, 0)
        draw = ImageDraw.Draw(docker_inactive)
        draw.rectangle([(0, 0), (7, 7)], outline=1)
        draw.line([(0, 0), (7, 7)], fill=1)
        draw.line([(0, 7), (7, 0)], fill=1)
        docker_inactive.save(os.path.join(icons_dir, "docker_inactive.png"))
    
    def clear(self):
        """Clear the display."""
        self.draw.rectangle([(0, 0), (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)], fill=0)
        self.display.clear()
    
    def show(self):
        """Update the display with the current image.
        Added error handling for display communication issues.
        """
        try:
            self.display.display(self.image)
            return True
        except Exception as e:
            logging.error(f"Error displaying image on OLED: {e}")
            # Try to recover the display if possible
            try:
                self.display.cleanup()
                time.sleep(0.1)
                self.serial = i2c(port=1, address=config.I2C_ADDRESS)
                self.display = ssd1306(self.serial, 
                                      width=config.DISPLAY_WIDTH, 
                                      height=config.DISPLAY_HEIGHT)
                self.display.display(self.image)
                logging.info("Successfully recovered display after error")
                return True
            except Exception as recovery_error:
                logging.error(f"Failed to recover display: {recovery_error}")
                return False
    
    def draw_text(self, position, text, fill=1, align="left"):
        """Draw text at the specified position with alignment options."""
        try:
            if align == "left":
                self.draw.text(position, text, font=self.font, fill=fill)
            elif align == "center":
                # Calculate width of text for centering
                try:
                    # For newer Pillow versions
                    bbox = self.font.getbbox(text)
                    text_width = bbox[2] - bbox[0]
                except AttributeError:
                    # For older Pillow versions
                    text_width = self.font.getsize(text)[0]
                centered_position = (position[0] + (config.DISPLAY_WIDTH - text_width) // 2, position[1])
                self.draw.text(centered_position, text, font=self.font, fill=fill)
            elif align == "right":
                # Calculate width of text for right alignment
                try:
                    # For newer Pillow versions
                    bbox = self.font.getbbox(text)
                    text_width = bbox[2] - bbox[0]
                except AttributeError:
                    # For older Pillow versions
                    text_width = self.font.getsize(text)[0]
                right_position = (config.DISPLAY_WIDTH - text_width - position[0], position[1])
                self.draw.text(right_position, text, font=self.font, fill=fill)
            return True
        except Exception as e:
            logging.error(f"Error drawing text '{text}': {e}")
            return False
    
    def draw_icon(self, position, icon_name):
        """Draw an icon at the specified position with error handling."""
        try:
            if icon_name in self.icons:
                self.image.paste(self.icons[icon_name], position)
                return True
            else:
                # Log missing icon but draw placeholder
                logging.warning(f"Icon '{icon_name}' not found, using placeholder")
                self.draw.rectangle(
                    [position, (position[0] + config.ICON_SIZE[0], position[1] + config.ICON_SIZE[1])],
                    outline=1
                )
                # Draw an X in the placeholder to indicate missing icon
                self.draw.line([(position[0], position[1]), 
                               (position[0] + config.ICON_SIZE[0], position[1] + config.ICON_SIZE[1])], 
                               fill=1)
                self.draw.line([(position[0], position[1] + config.ICON_SIZE[1]), 
                               (position[0] + config.ICON_SIZE[0], position[1])], 
                               fill=1)
                return False
        except Exception as e:
            logging.error(f"Error drawing icon '{icon_name}': {e}")
            return False
    
    def update_display(self, content_providers):
        """Update the display with information from content providers.
        Optimized to only update when content changes and rate-limited to prevent flicker.
        """
        # Rate limiting to prevent excessive updates
        current_time = time.time()
        if current_time - self.last_update_time < self.min_update_interval:
            return False
        
        # Get new content from providers
        new_content = []
        try:
            for provider in content_providers:
                try:
                    new_content.append(provider.get_content())
                except Exception as e:
                    logging.error(f"Error getting content from provider {provider.__class__.__name__}: {e}")
                    # Add placeholder for failed provider
                    new_content.append({'text': 'Error', 'error': str(e)})
        except Exception as e:
            logging.error(f"Error processing content providers: {e}")
            return False
        
        # Only update if content has changed
        if new_content != self.last_content:
            try:
                # Clear the display
                self.clear()
                
                # Draw all content
                y_position = 0
                for content in new_content:
                    if 'text' in content:
                        # Get alignment if specified, default to left
                        align = content.get('align', 'left')
                        self.draw_text((0, y_position), content['text'], align=align)
                        # Use calculated font height instead of fixed 8 pixels
                        y_position += self.font_height + 1  # +1 for spacing
                    
                    if 'icon' in content and 'position' in content:
                        self.draw_icon(content['position'], content['icon'])
                
                # Show the updated display
                self.show()
                self.last_content = new_content
                self.last_update_time = current_time
                return True
            except Exception as e:
                logging.error(f"Error updating display: {e}")
                return False
        return False
