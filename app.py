#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main application for the Raspberry Pi 5 OLED display framework.

This module provides the main application class and entry point
for running the OLED display.
"""

import os
import sys
import time
import signal
import logging
import argparse
from typing import Dict, List, Optional, Any, Tuple

from config import config, load_config, configure_logging
from display import OLEDDisplay
from layout.containers import (
    MetricContainer, ServiceIconContainer, TextContainer, DividerContainer
)
from providers.system import get_metric_provider
from providers.services import get_service_provider
from providers.network import get_network_info_provider
from fonts.icons import get_icon_code
from utils.hardware import verify_hardware_requirements


class OLEDApplication:
    """
    Main application for the Raspberry Pi 5 OLED display.
    
    This class initializes the display, sets up content providers,
    and runs the main update loop.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the OLED display application.
        
        Args:
            config_file: Path to configuration file
        """
        # Load configuration
        if config_file:
            load_config(config_file)
        
        # Configure logging
        configure_logging()
        
        # Initialize state
        self.running = True
        self.display = None
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Initialize the display
        self._initialize_display()
        
        # Set up containers
        self._setup_containers()
    
    def _initialize_display(self) -> None:
        """
        Initialize the OLED display.
        
        Raises:
            RuntimeError: If display initialization fails
        """
        try:
            display_config = config.get_display_config()
            i2c_port = display_config.get('i2c_port', 1)
            i2c_address = display_config.get('i2c_address', 0x3C)
            
            # Verify hardware requirements before initializing
            success, hw_details = self._verify_hardware(i2c_address, i2c_port)
            
            if not success:
                error_msg = hw_details.get('error', 'Unknown hardware issue')
                raise RuntimeError(f"Hardware check failed: {error_msg}")
            
            self.display = OLEDDisplay(
                width=display_config.get('width', 128),
                height=display_config.get('height', 32),
                i2c_port=i2c_port,
                i2c_address=i2c_address,
                rotation=display_config.get('rotation', 0),
                contrast=display_config.get('contrast', 255),
                inverted=display_config.get('inverted', False)
            )
            
            # Create the standard layout
            self.areas = self.display.create_standard_layout()
            logging.info("Display initialized successfully")
        
        except Exception as e:
            logging.error(f"Failed to initialize display: {e}")
            raise RuntimeError(f"Failed to initialize display: {e}")
            
    def _verify_hardware(self, address: int, bus: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify hardware requirements for the OLED display.
        
        Args:
            address: I2C address of the display
            bus: I2C bus number
            
        Returns:
            Tuple (success, details) where:
            - success: True if all requirements are met or --force flag is used
            - details: Dictionary with details of the checks
        """
        # Check for force flag
        force_mode = getattr(self, 'force_mode', False)
        require_display = not force_mode
        
        # Verify hardware requirements
        success, details = verify_hardware_requirements(
            address=address,
            bus=bus,
            auto_enable=True,
            require_display=require_display
        )
        
        # Log the results
        if not success and force_mode:
            logging.warning("Hardware check failed, but continuing due to --force flag")
            success = True
            
        return success, details
    
    def _setup_containers(self) -> None:
        """
        Set up containers for displaying content.
        
        This creates containers for metrics, services, and system information
        based on the configuration.
        """
        try:
            # Set up metric containers
            metric_configs = config.get_metrics()
            for i, metric_config in enumerate(metric_configs[:3]):  # Limit to 3 metrics
                name = metric_config['name']
                metric_type = metric_config['type']
                icon_name = metric_config['icon']
                unit = metric_config.get('unit', '%')
                
                # Get the metric provider function
                provider = get_metric_provider(metric_type)
                
                # Get the icon code
                icon_code = get_icon_code(icon_name)
                
                # Create the container
                container = MetricContainer(
                    name=name,
                    icon_code=icon_code,
                    provider=provider,
                    unit=unit
                )
                
                # Add the container to the display
                # Place each metric in its dedicated area
                # Direct mapping of metric name to grid area name
                self.display.add_container(container, name)
            
            # Set up service container
            service_configs = config.get_services()
            services = {}
            
            for service_config in service_configs:
                name = service_config['name']
                service_type = service_config['type']
                icon_name = service_config['icon']
                
                # Get the service provider function
                provider = get_service_provider(service_type)
                
                # Get the icon code
                icon_code = get_icon_code(icon_name)
                
                # Add to services dictionary
                services[name] = (icon_code, provider)
            
            # Create the service container
            if services:
                container = ServiceIconContainer(
                    name="services",
                    services=services
                )
                
                # Add the container to the display
                # Place service icons in the dedicated services area
                self.display.add_container(container, "services")
            
            # Set up divider between top and bottom sections
            divider = DividerContainer(
                name="divider",
                orientation="horizontal"
            )
            
            # Place divider between metrics and hostname at the bottom
            self.display.add_container(divider, "bottom")
            
            # Set up hostname container
            if config.get('system_info.show_hostname', True):
                hostname_provider = get_network_info_provider('hostname')
                
                hostname_container = TextContainer(
                    name="hostname",
                    provider=hostname_provider
                )
                
                self.display.add_container(hostname_container, "hostname")
            
            # Set up IP address container
            if config.get('system_info.show_ip', True):
                # Network interface to use (or None for default)
                interface = config.get('network.interface', None)
                
                # Get provider function with interface in kwargs
                ip_provider = get_network_info_provider('ip_address', interface=interface)
                
                ip_container = TextContainer(
                    name="ip_address",
                    provider=ip_provider,
                    prefix="IP: "
                )
                
                # Place IP address in its dedicated area in the bottom section
                self.display.add_container(ip_container, "ip_address")
            
            logging.info("Containers set up successfully")
        
        except Exception as e:
            logging.error(f"Failed to set up containers: {e}")
            raise RuntimeError(f"Failed to set up containers: {e}")
    
    def signal_handler(self, sig, frame) -> None:
        """
        Handle signals for graceful shutdown.
        
        Args:
            sig: Signal number
            frame: Stack frame
        """
        logging.info(f"Received signal {sig}, shutting down...")
        self.running = False
        
        if self.display:
            self.cleanup()
    
    def run(self) -> None:
        """Run the main application loop."""
        if not self.display:
            logging.error("Display not initialized")
            return
        
        update_interval = config.get('display.update_interval', 5.0)
        logging.info(f"Starting main loop with update interval of {update_interval} seconds")
        
        try:
            while self.running:
                # Update and render the display
                self.display.update()
                
                # Sleep until next update
                time.sleep(update_interval)
                
        except KeyboardInterrupt:
            logging.info("Keyboard interrupt received, shutting down...")
        
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
        
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up resources and shut down."""
        if self.display:
            try:
                self.display.cleanup()
                logging.info("Display cleaned up")
            except Exception as e:
                logging.error(f"Error cleaning up display: {e}")


def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Raspberry Pi 5 OLED Display"
    )
    
    parser.add_argument(
        '-c', '--config',
        help='Path to configuration file',
        default=None
    )
    
    parser.add_argument(
        '-v', '--verbose',
        help='Enable verbose logging',
        action='store_true'
    )
    
    parser.add_argument(
        '-r', '--reset',
        help='Reset the display before starting',
        action='store_true'
    )
    
    parser.add_argument(
        '-f', '--force',
        help='Force start even if hardware checks fail',
        action='store_true'
    )
    
    parser.add_argument(
        '--check-only',
        help='Only check hardware requirements and exit',
        action='store_true'
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Configure logging
    # Set to DEBUG for troubleshooting
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        # Handle hardware check only mode
        if args.check_only:
            from utils.hardware import check_oled_display
            display_config = config.get_display_config()
            result = check_oled_display(
                address=display_config.get('i2c_address', 0x3C),
                bus=display_config.get('i2c_port', 1)
            )
            
            print("\nHardware Check Results:")
            print(f"  Running on Raspberry Pi: {'Yes' if result['is_pi'] else 'No'}")
            print(f"  I2C Enabled: {'Yes' if result['i2c_enabled'] else 'No'}")
            print(f"  I2C Devices Found: {', '.join(result['devices_found']) or 'None'}")
            print(f"  OLED Display Connected: {'Yes' if result['display_connected'] else 'No'}")
            print(f"  Status: {result['status']}")
            
            if result['error']:
                print(f"  Error: {result['error']}")
                return 1
            
            return 0 if result['display_connected'] else 1
        
        # Initialize application with force flag if provided
        app = OLEDApplication(config_file=args.config)
        app.force_mode = args.force
        
        # Reset display if requested
        if args.reset and app.display:
            app.display.reset()
        
        # Run the application
        app.run()
    
    except Exception as e:
        logging.error(f"Error running application: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
