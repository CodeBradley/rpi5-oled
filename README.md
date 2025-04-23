# Raspberry Pi 5 OLED System Monitor

This application displays system information on a 0.91" I2C OLED display connected to a Raspberry Pi 5.

## Features

- Displays IP address
- Shows hostname
- Shows system uptime
- Displays SSH service status
- Displays Docker service status
- Modular design for easy expansion

## Hardware Requirements

- Raspberry Pi 5
- 0.91" I2C OLED Display (128x32 pixels)
- Connections: SCLK, DATA, VCC, GND

## Installation

1. Clone this repository to your Raspberry Pi 5:
   ```
   git clone https://github.com/yourusername/rpi5-oled.git
   cd rpi5-oled
   ```

2. Install the required dependencies:
   ```
   pip3 install -r requirements.txt
   ```

3. Set up the application to run at boot:
   ```
   sudo cp rpi5-oled.service /etc/systemd/system/
   sudo systemctl enable rpi5-oled.service
   sudo systemctl start rpi5-oled.service
   ```

## Configuration

Edit the `config.py` file to customize the display settings or add new modules.

## Wiring

Connect your OLED display to the Raspberry Pi as follows:

- VCC → 3.3V
- GND → Ground
- SDA → GPIO 2 (SDA)
- SCL → GPIO 3 (SCL)

## Usage

The application will start automatically at boot. To manually start or stop the service:

```
sudo systemctl start rpi5-oled.service
sudo systemctl stop rpi5-oled.service
```

To view logs:

```
sudo journalctl -u rpi5-oled.service
```
