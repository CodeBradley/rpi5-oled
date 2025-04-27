#!/bin/bash
# One-line installer for the RPi5 OLED Framework
# Usage: curl -sSL https://raw.githubusercontent.com/CodeBradley/rpi5-oled/framework/install.sh | sudo bash

set -e  # Exit on error

echo "RPi5 OLED Framework - One-line Installer"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# Check for git and install if missing
if ! command -v git &> /dev/null; then
  echo "Installing git..."
  apt-get update
  apt-get install -y git
fi

# Create a temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Clone the repository
echo "Cloning repository..."
git clone -b framework https://github.com/CodeBradley/rpi5-oled.git
cd rpi5-oled

# Run the deployment script
echo "Running deployment script..."
bash deploy.sh

# Clean up
cd /
rm -rf "$TEMP_DIR"

echo ""
echo "Installation complete!"
echo "The service should be running now. To check the status:"
echo "sudo systemctl status rpi5-oled"
