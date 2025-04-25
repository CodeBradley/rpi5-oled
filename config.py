"""
Configuration settings for the Raspberry Pi 5 OLED display application.
Optimized for performance and reliability.
"""
import logging

# Logging configuration
LOG_LEVEL = logging.INFO  # Use logging.DEBUG for more verbose output during development
LOG_FILE = "/var/log/rpi5-oled.log"  # Log file location

# I2C settings
I2C_PORT = 1  # Default I2C port on Raspberry Pi 5
I2C_ADDRESS = 0x3C  # Common address for SSD1306 OLED displays (check your specific display)

# Display settings
DISPLAY_WIDTH = 128  # 0.91" OLED is typically 128x32 pixels
DISPLAY_HEIGHT = 32
ROTATION = 0  # 0 = normal, 1 = 90°, 2 = 180°, 3 = 270°

# Performance settings
UPDATE_INTERVAL = 5.0  # Update display every 5 seconds
MIN_REFRESH_INTERVAL = 0.1  # Minimum time between display refreshes (prevents flicker)
DISPLAY_TIMEOUT = 300  # Turn off display after this many seconds of inactivity (0 to disable)
POWER_SAVE_MODE = False  # If True, uses inverted display (black background) to save power

# Icons and visuals
ICON_SIZE = (8, 8)  # Size of status icons in pixels
FONT_SIZE = 11  # Default font size
ICON_CACHE_ENABLED = True  # Cache icons in memory to improve performance
USE_ANTIALIASING = False  # Set to True for smoother text/icons, False for better performance

# Layout and spacing
LINE_PADDING = 2  # Pixels between lines of text (increased for better readability)
TOP_MARGIN = 0    # Pixels from top of display to first line
LEFT_MARGIN = 0   # Pixels from left edge of display
CENTER_CONTENT_VERTICALLY = True  # Center all content vertically on the display

# Font settings
# Uncomment to use a custom font (must be installed on the system)
# CUSTOM_FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

# Enabled modules (comment out to disable)
ENABLED_MODULES = [
    'ip_address',
    'hostname',
    'uptime',
    #'ssh_status',
    #'docker_status',
    #'cpu_temp',       # Uncomment to show CPU temperature
    # 'memory_usage',   # Uncomment to show RAM usage
    #'disk_usage',     # Uncomment to show disk usage
    # 'network_traffic', # Uncomment to show network traffic
]

# Module-specific settings
MODULE_SETTINGS = {
    'ip_address': {
        'interface': 'wlan0',  # Primary network interface (wlan0 for WiFi, eth0 for Ethernet)
        'show_ipv6': False,    # Set to True to display IPv6 address
        'refresh_interval': 60, # Check IP address every 60 seconds (IP rarely changes)
    },
    'hostname': {
        'refresh_interval': 3600, # Hostname rarely changes, check once per hour
    },
    'uptime': {
        'refresh_interval': 60,  # Update uptime display every minute
        'format': 'short',      # 'short' for compact display, 'long' for detailed
    },
    'ssh_status': {
        'service_name': 'sshd',  # SSH service name
        'refresh_interval': 30,  # Check SSH status every 30 seconds
    },
    'docker_status': {
        'socket_path': '/var/run/docker.sock',  # Docker socket path
        'refresh_interval': 30,  # Check Docker status every 30 seconds
        'show_container_count': True, # Show number of running containers
    },
    'cpu_temp': {
        'refresh_interval': 5,   # Update temperature every 5 seconds
        'warning_temp': 70,      # Temperature in °C to show warning
        'critical_temp': 80,     # Temperature in °C to show critical warning
    },
    'memory_usage': {
        'refresh_interval': 10,   # Update memory usage every 10 seconds
        'warning_percent': 80,   # Percentage to show warning
    },
    'disk_usage': {
        'mount_point': '/',      # Filesystem to monitor
        'refresh_interval': 300, # Check disk space every 5 minutes
        'warning_percent': 80,   # Percentage to show warning
    },
    'network_traffic': {
        'interface': 'wlan0',    # Network interface to monitor
        'refresh_interval': 5,   # Update every 5 seconds
        'show_units': True,      # Show KB/s, MB/s units
    }
}

# Error handling
MAX_RETRIES = 3         # Maximum number of retries for failed operations
RETRY_DELAY = 1.0       # Seconds to wait between retries
