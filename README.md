# Raspberry Pi 5 OLED Display Framework

A modular, grid-based layout system for OLED displays on Raspberry Pi 5, designed for displaying system metrics, service statuses, and network information.

## Features

- **Grid Layout System**: CSS-grid inspired layout framework for organizing display content
- **Modular Architecture**: Easily add or remove components without modifying core code
- **Metrics Display**: Show CPU usage, memory usage, temperature, and more
- **Service Status**: Monitor Docker, CephFS, and other services with icon indicators
- **Network Information**: Display hostname and IP address
- **Icon Font Support**: Uses custom BoxIcons font for scalable, low-memory icons
- **Flexible Configuration**: YAML or JSON configuration files

## Architecture

The framework is designed with modularity and separation of concerns in mind:

```
rpi5_oled/
  - layout/
    - grid.py       # Grid layout system
    - containers.py # Container types (metrics, services, text)
  - providers/
    - system.py     # System metrics (CPU, RAM, temp)
    - services.py   # Service status (Docker, CephFS)
    - network.py    # Network info (hostname, IP)
  - fonts/
    - icons.py      # Icon utilities and mappings
  - display.py      # OLED hardware controller
  - config.py       # Configuration management
  - app.py          # Main application
```

## Hardware Requirements

- Raspberry Pi 5 (works with Pi 3/4 as well)
- 0.91" I2C OLED Display (128x32 pixels)
- Connections: SDA, SCL, VCC, GND

## Installation

### Method 1: Install from pip

```bash
pip install rpi5-oled
```

### Method 2: Install from source

1. Clone this repository:
   ```bash
   git clone https://github.com/CodeBradley/rpi5-oled.git
   cd rpi5-oled
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

3. Set up as a systemd service:
   ```bash
   sudo cp examples/rpi5-oled.service /etc/systemd/system/
   sudo systemctl enable rpi5-oled.service
   sudo systemctl start rpi5-oled.service
   ```

## Configuration

The framework uses YAML or JSON configuration files. Create a configuration file at `/etc/rpi5-oled/config.yaml` or specify a custom path with the `-c` flag.

## Wiring

Connect your OLED display to the Raspberry Pi as follows:

- VCC → 3.3V
- GND → Ground
- SDA → GPIO 2 (SDA)
- SCL → GPIO 3 (SCL)

## Usage

### Command Line

```bash
# Run with default configuration
rpi5-oled

# Specify a configuration file
rpi5-oled -c /path/to/config.yaml

# Enable verbose logging
rpi5-oled -v

# Reset the display before starting
rpi5-oled -r
```

### As a systemd service

```bash
# Start, stop, or restart the service
sudo systemctl start rpi5-oled.service
sudo systemctl stop rpi5-oled.service
sudo systemctl restart rpi5-oled.service

# View logs
sudo journalctl -u rpi5-oled.service
```

## Extending the Framework

### Adding a New Metric

To add a custom metric, create a new provider function in `system.py` and register it in the configuration:

```python
# In providers/system.py
def get_custom_metric():
    # Your implementation here
    return value

# Register in get_metric_provider function
def get_metric_provider(metric_type):
    metric_types = {
        # ... existing metrics
        'custom_metric': get_custom_metric,
    }
```

### Adding a New Service

To monitor a new service, add a provider function in `services.py`:

```python
# In providers/services.py
def check_custom_service():
    # Your implementation here
    return True  # or False if service is down

# Register in get_service_provider function
def get_service_provider(service_type):
    service_types = {
        # ... existing services
        'custom_service': check_custom_service,
    }
```

### Creating a Custom Container

Extend the `Container` class in `containers.py` to create a new type of display element.
