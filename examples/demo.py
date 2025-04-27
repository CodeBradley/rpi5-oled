#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script for the rpi5-oled framework.

This script demonstrates how to use the framework to create
a customized OLED display layout and content.
"""

import time
import logging
import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from display import OLEDDisplay
from layout.containers import (
    MetricContainer, ServiceIconContainer, TextContainer, DividerContainer
)
from providers.system import get_cpu_usage, get_memory_usage, get_cpu_temperature
from providers.services import check_docker_service, check_systemd_service
from providers.network import get_hostname, get_ip_address
from fonts.icons import get_icon_code


def main():
    """Run the demo application."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize the display (use appropriate settings for your hardware)
    display = OLEDDisplay(
        width=128,
        height=32,
        i2c_port=1,
        i2c_address=0x3C
    )
    
    # Create a standard layout
    areas = display.create_standard_layout()
    
    # Create metric containers
    cpu_container = MetricContainer(
        name="cpu",
        icon_code=get_icon_code("cpu"),
        provider=get_cpu_usage,
        unit="%"
    )
    display.add_container(cpu_container, "metric_0")
    
    memory_container = MetricContainer(
        name="memory",
        icon_code=get_icon_code("memory"),
        provider=get_memory_usage,
        unit="%"
    )
    display.add_container(memory_container, "metric_1")
    
    temp_container = MetricContainer(
        name="temperature",
        icon_code=get_icon_code("temperature"),
        provider=get_cpu_temperature,
        unit="°C"
    )
    display.add_container(temp_container, "metric_2")
    
    # Create services container
    services = {
        "Docker": (get_icon_code("docker"), check_docker_service),
        "SSH": (get_icon_code("terminal"), lambda: check_systemd_service("sshd"))
    }
    
    service_container = ServiceIconContainer(
        name="services",
        services=services
    )
    display.add_container(service_container, "services")
    
    # Create divider
    divider = DividerContainer(
        name="divider",
        orientation="horizontal"
    )
    display.add_container(divider, "divider")
    
    # Create hostname container
    hostname_container = TextContainer(
        name="hostname",
        provider=get_hostname
    )
    display.add_container(hostname_container, "hostname")
    
    # Create IP address container
    ip_container = TextContainer(
        name="ip_address",
        provider=lambda: get_ip_address(),
        prefix="IP: "
    )
    display.add_container(ip_container, "ip_address")
    
    # Main loop
    try:
        print("Running demo. Press Ctrl+C to exit.")
        while True:
            # Update and render the display
            display.update()
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("Keyboard interrupt received, exiting.")
    
    finally:
        # Clean up
        display.cleanup()


if __name__ == "__main__":
    main()
