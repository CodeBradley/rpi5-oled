"""
Configuration settings for the Raspberry Pi 5 OLED display application.
"""

# I2C settings
I2C_PORT = 1  # Default I2C port on Raspberry Pi
I2C_ADDRESS = 0x3C  # Common address for SSD1306 OLED displays (check your specific display)

# Display settings
DISPLAY_WIDTH = 128  # 0.91" OLED is typically 128x32 pixels
DISPLAY_HEIGHT = 32
ROTATION = 0  # 0 = normal, 1 = 90°, 2 = 180°, 3 = 270°

# Update frequency
UPDATE_INTERVAL = 5  # Update display every 5 seconds

# Icons and visuals
ICON_SIZE = (8, 8)  # Size of status icons in pixels
FONT_SIZE = 8  # Default font size

# Enabled modules (comment out to disable)
ENABLED_MODULES = [
    'ip_address',
    'hostname',
    'uptime',
    'ssh_status',
    'docker_status',
]

# Module-specific settings
MODULE_SETTINGS = {
    'ip_address': {
        'interface': 'wlan0',  # Primary network interface (wlan0 for WiFi, eth0 for Ethernet)
    },
    'ssh_status': {
        'service_name': 'sshd',  # SSH service name
    },
    'docker_status': {
        'socket_path': '/var/run/docker.sock',  # Docker socket path
    }
}
