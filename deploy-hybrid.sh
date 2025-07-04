#!/bin/bash
# HYBRID Deployment script for the Raspberry Pi 5 OLED Display Framework
# This script uses a combination of apt and pip to handle PEP 668 restrictions
# Based on the original deploy.sh with modifications

set -e  # Exit on error

# Configuration
REPO_URL="https://github.com/CodeBradley/rpi5-oled.git"
BRANCH="framework"  # Change this to your target branch (main, master, framework, etc.)
INSTALL_DIR="/usr/local/lib/rpi5-oled"
CONFIG_DIR="/etc/rpi5-oled"
SERVICE_FILE="/etc/systemd/system/rpi5-oled.service"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# Check for required tools
if ! command -v git &> /dev/null; then
  echo "Git is not installed. Installing..."
  apt-get update
  apt-get install -y git
fi

# Create config directory
echo "Creating configuration directory..."
mkdir -p $CONFIG_DIR

# Remove old installation if it exists
if [ -d "$INSTALL_DIR" ]; then
  echo "Removing previous installation..."
  rm -rf $INSTALL_DIR
fi

# Clone the repository
echo "Cloning repository from $REPO_URL (branch: $BRANCH)..."
git clone -b $BRANCH $REPO_URL $INSTALL_DIR

cd $INSTALL_DIR

# Create default config if it doesn't exist
if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
  echo "Creating default configuration..."
  cat > $CONFIG_DIR/config.yaml << EOF
# Raspberry Pi 5 OLED Display Framework Configuration

# Display settings
display:
  width: 128
  height: 32
  i2c_port: 1
  i2c_address: 0x3C
  rotation: 0
  contrast: 255
  inverted: false

# Update interval in seconds
update_interval: 5

# Enabled modules
enabled_modules:
  - system_metrics
  - network_info
  - service_status
EOF
fi

# Check for I2C and install if missing
if ! lsmod | grep -q i2c_bcm; then
  echo "Enabling I2C interface..."
  raspi-config nonint do_i2c 0
fi

# ==== VIRTUAL ENVIRONMENT APPROACH ====
# Install system packages from apt
echo "Installing system dependencies..."
apt-get update

# Install Python venv package and development libraries
apt-get install -y \
    python3-venv \
    python3-dev \
    libfreetype6-dev \
    libjpeg-dev \
    libopenjp2-7 \
    i2c-tools

# Try to install libtiff - name varies by OS version
apt-get install -y libtiff5 || apt-get install -y libtiff || true

# Create and activate a virtual environment
echo "Creating Python virtual environment..."
python3 -m venv $INSTALL_DIR/venv

# Install Python packages in the virtual environment
echo "Installing Python packages into virtual environment..."
$INSTALL_DIR/venv/bin/pip install --upgrade pip
$INSTALL_DIR/venv/bin/pip install \
    pillow \
    pyyaml \
    psutil \
    luma.oled \
    RPi.GPIO
    
# Update the service file to use the Python interpreter from the venv
echo "Updating service file to use virtual environment..."
sed -i "s|ExecStart=.*|ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/app.py|" $INSTALL_DIR/rpi5-oled.service
# ==== END VIRTUAL ENVIRONMENT APPROACH ====

# Install systemd service
echo "Installing systemd service..."
cp rpi5-oled.service $SERVICE_FILE
systemctl daemon-reload
systemctl enable rpi5-oled.service

# Run hardware check (without forcing)
echo "Running hardware check..."
python3 app.py --check-only || true

echo ""
echo "Installation complete!"
echo "To start the service, run: sudo systemctl start rpi5-oled"
echo "To check status, run: sudo systemctl status rpi5-oled"
echo "To view logs, run: sudo journalctl -u rpi5-oled -f"
