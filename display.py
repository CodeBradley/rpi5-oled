"""
Display handling for the Raspberry Pi 5 OLED display application.
"""
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import os
import config


class OLEDDisplay:
    """Class to manage the OLED display."""
    
    def __init__(self):
        # Initialize I2C
        self.i2c = busio.I2C(board.SCL, board.SDA)
        
        # Initialize display
        self.display = adafruit_ssd1306.SSD1306_I2C(
            config.DISPLAY_WIDTH, 
            config.DISPLAY_HEIGHT, 
            self.i2c, 
            addr=config.I2C_ADDRESS
        )
        
        # Create blank image for drawing
        self.image = Image.new("1", (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT))
        self.draw = ImageDraw.Draw(self.image)
        
        # Load default font
        self.font = ImageFont.load_default()
        
        # Load icons
        self.icons = self._load_icons()
        
        # Clear the display on startup
        self.clear()
    
    def _load_icons(self):
        """Load icon images."""
        icons = {}
        icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
        
        # Create icons directory if it doesn't exist
        if not os.path.exists(icons_dir):
            os.makedirs(icons_dir)
            self._create_default_icons(icons_dir)
        
        # Load all icons from the icons directory
        for filename in os.listdir(icons_dir):
            if filename.endswith('.png'):
                icon_name = os.path.splitext(filename)[0]
                icon_path = os.path.join(icons_dir, filename)
                icon = Image.open(icon_path).convert("1")
                icons[icon_name] = icon.resize(config.ICON_SIZE, Image.LANCZOS)
        
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
        self.display.fill(0)
        self.display.show()
    
    def show(self):
        """Update the display with the current image."""
        self.display.image(self.image)
        self.display.show()
    
    def draw_text(self, position, text, fill=1):
        """Draw text at the specified position."""
        self.draw.text(position, text, font=self.font, fill=fill)
    
    def draw_icon(self, position, icon_name):
        """Draw an icon at the specified position."""
        if icon_name in self.icons:
            self.image.paste(self.icons[icon_name], position)
        else:
            # Draw a placeholder if icon not found
            self.draw.rectangle(
                [position, (position[0] + config.ICON_SIZE[0], position[1] + config.ICON_SIZE[1])],
                outline=1
            )
    
    def update_display(self, content_providers):
        """Update the display with information from content providers."""
        # Clear the display
        self.clear()
        
        # Get content from each provider and draw it
        y_position = 0
        for provider in content_providers:
            content = provider.get_content()
            if 'text' in content:
                self.draw_text((0, y_position), content['text'])
                y_position += 8  # Advance by font height
            
            if 'icon' in content and 'position' in content:
                self.draw_icon(content['position'], content['icon'])
        
        # Show the updated display
        self.show()
