# This is an AI Test
This repo was just a test of the AI features of Windsurf and whether or not it was capable of creating an OLED grid system where I can display certain widgets based on a mockup I provided it with. I have not fully reviewed the code and do not plan to use it for my project. There could be some successes, but there's definitely some failures. 

# RPi5 OLED Framework

A modular, grid-based layout system for Raspberry Pi OLED displays, showing resource utilization metrics, service statuses, and network information.

## Features

- Grid-based layout system (CSS Grid-like)
- Modular architecture with pluggable components
- System resource monitoring (CPU, RAM, temperature)
- Network status information
- Service status indicators
- Hardware connectivity checks
- Systemd service integration
- Custom icon support using Boxicons

## Supported Hardware

- Raspberry Pi 5 (compatible with 3/4 as well)
- 0.91" OLED display (128x32 pixels) via I2C
- SSD1306 display controller

## Project Structure

```
rpi5-oled/
├── app.py              # Main entry point
├── config.py           # Configuration handling
├── display.py          # Display controller
├── layout/             # Layout system
│   ├── grid.py         # Grid layout framework
│   └── containers.py   # UI components
├── providers/          # Data providers
│   ├── system.py       # System metrics (CPU, RAM, temp)
│   ├── services.py     # Service status (Docker, CephFS)
│   └── network.py      # Network info (hostname, IP)
├── utils/              # Utility functions
│   └── hardware.py     # Hardware checks and utilities
├── fonts/              # Font resources
│   └── lakenet-boxicons.ttf  # Custom icon font
└── tests/              # Unit tests
```

## Installation

### Quick Install

The easiest way to install is by using our deployment script, which pulls directly from GitHub:

```bash
# One-line install (pulls latest code and sets up service)
curl -sSL https://raw.githubusercontent.com/CodeBradley/rpi5-oled/framework/deploy-hybrid.sh | sudo bash
```

### Manual Installation

If you prefer more control over the installation:

```bash
# Clone the repository
git clone -b framework https://github.com/CodeBradley/rpi5-oled.git
cd rpi5-oled

# Run the deployment script
sudo ./deploy.sh
```

The deployment script will:
1. Install necessary system dependencies
2. Enable the I2C interface if needed
3. Install Python dependencies
4. Set up the systemd service
5. Create a default configuration
6. Run a hardware check

## Configuration

The framework uses a YAML configuration file at `/etc/rpi5-oled/config.yaml`.

Example configuration:

```yaml
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
```

## Hardware Setup

Connect your OLED display to the Raspberry Pi:

- VCC → 3.3V
- GND → Ground
- SDA → GPIO 2 (I2C1 SDA)
- SCL → GPIO 3 (I2C1 SCL)

Make sure I2C is enabled on your Raspberry Pi:

```bash
sudo raspi-config
```

Navigate to: Interface Options > I2C > Enable

## Usage

### Managing the Service

```bash
# Start the service
sudo systemctl start rpi5-oled

# Check status
sudo systemctl status rpi5-oled

# View logs
sudo journalctl -u rpi5-oled -f

# Stop the service
sudo systemctl stop rpi5-oled
```

### Hardware Verification

To check if your hardware is properly connected:

```bash
cd /usr/local/lib/rpi5-oled
sudo python3 app.py --check-only
```

### Development Mode

For testing without hardware (ignores hardware check failures):

```bash
python3 app.py --force
```

## Development

### Setting Up a Development Environment

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies for development
pip install -r requirements.txt
pip install pytest pillow pyyaml psutil
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test files
python -m pytest tests/test_grid.py
python -m pytest tests/test_containers.py
```

## Extending the Framework

### Adding a New Metric

To add a custom metric, implement a provider function in `providers/system.py`:

```python
def get_custom_metric():
    # Implementation logic
    return value
```

### Creating a Custom Container

Extend the base Container class in `layout/containers.py`:

```python
class CustomContainer(Container):
    def __init__(self, position, size, custom_param):
        super().__init__(position, size)
        self.custom_param = custom_param
        
    def render(self, draw, fonts):
        # Custom rendering logic
        pass
        
    def update(self):
        # Update container state
        pass
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
