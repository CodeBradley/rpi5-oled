#!/usr/bin/env python3
"""
Main application for the Raspberry Pi 5 OLED display system monitor.
Displays IP address, hostname, uptime, SSH and Docker status on a 0.91" I2C OLED display.
"""
import time
import signal
import sys
from display import OLEDDisplay
from content_providers import get_enabled_providers
import config


class Application:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.running = True
        self.display = None
        self.providers = []
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Handle signals for graceful shutdown."""
        print("Shutting down...")
        self.running = False
        if self.display:
            self.display.clear()
        sys.exit(0)
    
    def initialize(self):
        """Initialize the display and content providers."""
        try:
            # Initialize the display
            self.display = OLEDDisplay()
            
            # Initialize content providers
            self.providers = get_enabled_providers()
            
            print("Initialization complete")
            return True
        except Exception as e:
            print(f"Initialization failed: {e}")
            return False
    
    def update_display(self):
        """Update the display with current information."""
        if self.display and self.providers:
            self.display.update_display(self.providers)
    
    def run(self):
        """Run the main application loop."""
        if not self.initialize():
            print("Failed to initialize. Exiting.")
            return
        
        print("Starting main loop")
        while self.running:
            try:
                # Update the display
                self.update_display()
                
                # Wait for the next update interval
                time.sleep(config.UPDATE_INTERVAL)
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(1)  # Prevent tight loop in case of persistent errors


if __name__ == "__main__":
    app = Application()
    app.run()
