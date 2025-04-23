#!/bin/bash
# deploy.sh - Script to deploy the OLED display application to a Raspberry Pi using GitHub
# Usage: ./deploy.sh [hostname]

# Default hostname if not provided
HOST=${1:-boron}
REMOTE_USER="brad"
APP_DIR="/home/brad/rpi5-oled"
SERVICE_NAME="rpi5-oled"
GITHUB_REPO="https://github.com/CodeBradley/rpi5-oled.git"

echo "Deploying to $HOST..."

# First, commit and push any local changes to GitHub
echo "Pushing local changes to GitHub..."
git add .
git commit -m "Update: $(date +'%Y-%m-%d %H:%M:%S')"
git push origin main

# Check if the repository exists on the Pi
ssh $REMOTE_USER@$HOST "if [ ! -d $APP_DIR/.git ]; then \
  echo 'Cloning repository for the first time...'; \
  git clone $GITHUB_REPO $APP_DIR; \
 else \
  echo 'Updating existing repository...'; \
  cd $APP_DIR && git pull; \
fi"

# Copy the service file (this is not in the git repo)
echo "Copying service file..."
scp $SERVICE_NAME.service $REMOTE_USER@$HOST:/tmp/
ssh $REMOTE_USER@$HOST "sudo mv /tmp/$SERVICE_NAME.service /etc/systemd/system/"

# Install system dependencies
echo "Installing system dependencies..."
ssh $REMOTE_USER@$HOST "sudo apt update && sudo apt install -y python3-pip python3-venv python3-dev i2c-tools python3-smbus python3-lgpio"

# Set up virtual environment
echo "Setting up virtual environment..."
ssh $REMOTE_USER@$HOST "cd $APP_DIR && python3 -m venv venv"

# Install dependencies in the virtual environment
echo "Installing Python dependencies in virtual environment..."
ssh $REMOTE_USER@$HOST "cd $APP_DIR && ./venv/bin/pip install --upgrade pip && ./venv/bin/pip install -r requirements.txt && ./venv/bin/pip install adafruit-blinka"

# Create a symlink for lgpio in the virtual environment
echo "Setting up lgpio in virtual environment..."
ssh $REMOTE_USER@$HOST "cd $APP_DIR && python3 -c \"import site; import os; src='/usr/lib/python3/dist-packages/lgpio.py'; dst=os.path.join(site.getsitepackages()[0], 'lgpio.py'); print(f'Linking {src} to {dst}')\" && sudo ln -sf /usr/lib/python3/dist-packages/lgpio.py \$(cd $APP_DIR && ./venv/bin/python -c \"import site; print(site.getsitepackages()[0])\")"

# Create icons directory and copy icons if needed
echo "Setting up icons..."
ssh $REMOTE_USER@$HOST "mkdir -p $APP_DIR/icons"

# Copy the icon files
echo "Copying icon files..."
scp icons/*.png $REMOTE_USER@$HOST:$APP_DIR/icons/

# Reload systemd and restart the service
echo "Restarting service..."
ssh $REMOTE_USER@$HOST "sudo systemctl daemon-reload && sudo systemctl restart $SERVICE_NAME"

# Check service status
echo "Service status:"
ssh $REMOTE_USER@$HOST "sudo systemctl status $SERVICE_NAME --no-pager"

# View detailed logs
echo "\nDetailed logs:"
ssh $REMOTE_USER@$HOST "sudo journalctl -u $SERVICE_NAME -n 20 --no-pager"

echo "\nDeployment complete!"
