#!/bin/bash
# deploy.sh - Script to deploy the OLED display application to a Raspberry Pi using GitHub
# Usage: ./deploy.sh [hostname]

# Exit on error
set -e

# Function to log messages with timestamps
log_message() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Default hostname if not provided
HOST=${1:-boron}
REMOTE_USER="brad"
APP_DIR="/home/brad/rpi5-oled"
SERVICE_NAME="rpi5-oled"
GITHUB_REPO="https://github.com/CodeBradley/rpi5-oled.git"
CURRENT_BRANCH=$(git branch --show-current)

log_message "Deploying to $HOST from branch $CURRENT_BRANCH..."

# First, commit and push any local changes to GitHub if there are changes
log_message "Checking for local changes..."
if ! git diff-index --quiet HEAD; then
  log_message "Changes detected, committing and pushing..."
  git add .
  git commit -m "Update: $(date +'%Y-%m-%d %H:%M:%S')"
  git push origin $CURRENT_BRANCH
else
  log_message "No local changes to commit."
fi

# Check if the repository exists on the Pi
log_message "Checking repository on $HOST..."
ssh $REMOTE_USER@$HOST "if [ ! -d $APP_DIR/.git ]; then \
  echo 'Cloning repository for the first time...'; \
  git clone $GITHUB_REPO $APP_DIR; \
  cd $APP_DIR && git checkout $CURRENT_BRANCH; \
 else \
  echo 'Updating existing repository...'; \
  cd $APP_DIR && git fetch && git checkout $CURRENT_BRANCH && git pull; \
fi"

# Copy the service file only if it doesn't exist or has changed
log_message "Checking service file..."
LOCAL_SERVICE_HASH=$(md5sum $SERVICE_NAME.service | awk '{print $1}')
REMOTE_SERVICE_HASH=$(ssh $REMOTE_USER@$HOST "if [ -f /etc/systemd/system/$SERVICE_NAME.service ]; then md5sum /etc/systemd/system/$SERVICE_NAME.service | awk '{print \$1}'; else echo 'not_found'; fi")

if [ "$LOCAL_SERVICE_HASH" != "$REMOTE_SERVICE_HASH" ]; then
  log_message "Service file changed or not found, copying..."
  scp $SERVICE_NAME.service $REMOTE_USER@$HOST:/tmp/
  ssh $REMOTE_USER@$HOST "sudo mv /tmp/$SERVICE_NAME.service /etc/systemd/system/"
else
  log_message "Service file unchanged, skipping copy."
fi

# Install system dependencies
log_message "Installing system dependencies..."
ssh $REMOTE_USER@$HOST "sudo apt update && sudo apt install -y python3-pip python3-venv python3-dev i2c-tools python3-smbus python3-rpi.gpio python3-pil libfreetype6-dev libjpeg-dev"

# Set up virtual environment only if it doesn't exist
log_message "Checking virtual environment..."
ssh $REMOTE_USER@$HOST "cd $APP_DIR && [ -d venv ] || python3 -m venv venv"

# Install Python dependencies from requirements.txt in the virtual environment
log_message "Installing Python dependencies..."
ssh $REMOTE_USER@$HOST "cd $APP_DIR && \
  source venv/bin/activate && \
  if [ -f requirements.txt ]; then \
    pip3 install -r requirements.txt; \
  else \
    pip3 install RPi.GPIO luma.oled psutil docker; \
  fi"

# Create icons directory and copy icons if needed
log_message "Setting up icons..."
ssh $REMOTE_USER@$HOST "mkdir -p $APP_DIR/icons"

# Copy the icon files (only copy if they don't exist or have changed)
log_message "Copying icon files..."
for icon in icons/*.png; do
  if [ -f "$icon" ]; then
    ICON_NAME=$(basename "$icon")
    LOCAL_ICON_HASH=$(md5sum "$icon" | awk '{print $1}')
    REMOTE_ICON_HASH=$(ssh $REMOTE_USER@$HOST "if [ -f $APP_DIR/icons/$ICON_NAME ]; then md5sum $APP_DIR/icons/$ICON_NAME | awk '{print \$1}'; else echo 'not_found'; fi")
    
    if [ "$LOCAL_ICON_HASH" != "$REMOTE_ICON_HASH" ]; then
      log_message "Copying updated icon: $ICON_NAME"
      scp "$icon" $REMOTE_USER@$HOST:$APP_DIR/icons/
    fi
  fi
done

# Reload systemd and restart the service
log_message "Restarting service..."
ssh $REMOTE_USER@$HOST "sudo systemctl daemon-reload && sudo systemctl restart $SERVICE_NAME"

# Check service status
log_message "Service status:"
ssh $REMOTE_USER@$HOST "sudo systemctl status $SERVICE_NAME --no-pager"

# View detailed logs
log_message "Detailed logs:"
ssh $REMOTE_USER@$HOST "sudo journalctl -u $SERVICE_NAME -n 20 --no-pager"

log_message "Deployment complete!"

# Check for any errors during deployment
if [ $? -eq 0 ]; then
  log_message "Deployment successful!"
else
  log_message "Deployment encountered errors. Please check the logs above."
  exit 1
fi
