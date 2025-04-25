#!/usr/bin/env python3
"""
Main application for the Raspberry Pi 5 OLED display system monitor.
Displays IP address, hostname, uptime, SSH and Docker status on a 0.91" I2C OLED display.
Optimized for performance and reliability.
"""
import os
import time
import signal
import sys
import logging
import traceback
from logging.handlers import RotatingFileHandler
from display import OLEDDisplay
from content_providers import get_enabled_providers
import config

# Set up logging
def setup_logging():
    """Configure the logging system."""
    log_dir = os.path.dirname(os.path.abspath(config.LOG_FILE))
    
    # Create log directory if it doesn't exist
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception:
            # Fall back to local log if we can't write to system location
            config.LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rpi5-oled.log')
    
    # Configure logging
    logger = logging.getLogger()
    logger.setLevel(config.LOG_LEVEL)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.LOG_LEVEL)
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    
    # File handler (with rotation to prevent huge log files)
    file_handler = RotatingFileHandler(
        config.LOG_FILE, 
        maxBytes=1024*1024,  # 1MB
        backupCount=5
    )
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


class Application:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.running = True
        self.display = None
        self.providers = []
        self.last_provider_init_time = 0
        self.provider_init_interval = 300  # Reinitialize providers every 5 minutes
        self.error_count = 0
        self.max_consecutive_errors = 5
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logging.info("Application initialized")
    
    def signal_handler(self, sig, frame):
        """Handle signals for graceful shutdown."""
        logging.info("Received shutdown signal, cleaning up...")
        self.running = False
        if self.display:
            try:
                self.display.clear()
                logging.info("Display cleared")
            except Exception as e:
                logging.error(f"Error clearing display during shutdown: {e}")
        logging.info("Shutdown complete")
        sys.exit(0)
    
    def initialize(self):
        """Initialize the display and content providers."""
        retry_count = 0
        max_retries = config.MAX_RETRIES
        
        while retry_count < max_retries:
            try:
                # Initialize the display
                if not self.display:
                    logging.info("Initializing display...")
                    self.display = OLEDDisplay()
                
                # Initialize content providers
                logging.info("Initializing content providers...")
                self.providers = get_enabled_providers()
                self.last_provider_init_time = time.time()
                
                logging.info("Initialization complete")
                self.error_count = 0  # Reset error counter on successful init
                return True
            except Exception as e:
                retry_count += 1
                logging.error(f"Initialization attempt {retry_count} failed: {e}")
                if retry_count < max_retries:
                    logging.info(f"Retrying in {config.RETRY_DELAY} seconds...")
                    time.sleep(config.RETRY_DELAY)
                else:
                    logging.critical(f"Failed to initialize after {max_retries} attempts")
                    return False
    
    def update_display(self):
        """Update the display with current information."""
        if not self.display or not self.providers:
            logging.warning("Cannot update display: display or providers not initialized")
            return False
        
        # Check if we need to reinitialize providers (for long-running instances)
        current_time = time.time()
        if current_time - self.last_provider_init_time > self.provider_init_interval:
            logging.info("Reinitializing content providers...")
            try:
                self.providers = get_enabled_providers()
                self.last_provider_init_time = current_time
            except Exception as e:
                logging.error(f"Failed to reinitialize providers: {e}")
        
        # Update the display
        try:
            update_success = self.display.update_display(self.providers)
            if update_success:
                self.error_count = 0  # Reset error counter on successful update
            return update_success
        except Exception as e:
            self.error_count += 1
            logging.error(f"Error updating display: {e}")
            if self.error_count >= self.max_consecutive_errors:
                logging.critical(f"Too many consecutive errors ({self.error_count}), reinitializing...")
                return self.initialize()
            return False
    
    def run(self):
        """Run the main application loop."""
        if not self.initialize():
            logging.critical("Failed to initialize. Exiting.")
            return
        
        logging.info("Starting main loop")
        last_update_time = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # Only update at the configured interval
                if current_time - last_update_time >= config.UPDATE_INTERVAL:
                    # Update the display
                    self.update_display()
                    last_update_time = current_time
                
                # Sleep for a short time to prevent CPU hogging
                # This allows for more responsive signal handling
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                self.signal_handler(signal.SIGINT, None)
                break
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                logging.debug(traceback.format_exc())
                
                # Prevent tight loop in case of persistent errors
                # but still allow signal handling
                time.sleep(1)


if __name__ == "__main__":
    # Set up logging first thing
    logger = setup_logging()
    
    try:
        logging.info("Starting Raspberry Pi 5 OLED Display Application")
        logging.info(f"Log level: {logging.getLevelName(config.LOG_LEVEL)}")
        logging.info(f"Display dimensions: {config.DISPLAY_WIDTH}x{config.DISPLAY_HEIGHT}")
        logging.info(f"Update interval: {config.UPDATE_INTERVAL} seconds")
        logging.info(f"Enabled modules: {', '.join(config.ENABLED_MODULES)}")
        
        app = Application()
        app.run()
    except Exception as e:
        logging.critical(f"Fatal error: {e}")
        logging.debug(traceback.format_exc())
        sys.exit(1)
