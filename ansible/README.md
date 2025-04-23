# Ansible Role: rpi5-oled

This Ansible role deploys the Raspberry Pi 5 OLED display system monitor application to multiple Raspberry Pi devices.

## Features

- Installs required system dependencies
- Enables I2C interface on Raspberry Pi
- Deploys the OLED display application
- Configures and starts the systemd service
- Customizable configuration via variables

## Requirements

- Ansible 2.9 or higher
- Target Raspberry Pi devices with Debian-based OS (Raspberry Pi OS)
- SSH access to the target devices

## Usage

1. Copy your inventory file or create a new one based on the example:
   ```
   cp inventory.example.yml inventory.yml
   ```

2. Edit the inventory file to include your Raspberry Pi devices:
   ```yaml
   all:
     children:
       rpi5:
         hosts:
           rpi5-1:
             ansible_host: 192.168.1.101
             ansible_user: pi
   ```

3. Run the playbook:
   ```
   ansible-playbook -i inventory.yml deploy-oled.yml
   ```

## Customization

You can customize the deployment by overriding variables either in the inventory file or in the playbook. See `roles/rpi5-oled/defaults/main.yml` for all available variables.

### Examples

#### Change network interface for IP display

```yaml
# In inventory.yml
all:
  children:
    rpi5:
      vars:
        rpi5_oled_ip_address_interface: "eth0"  # Use wired connection
```

#### Change update interval

```yaml
# In playbook
- name: Deploy OLED display to Raspberry Pi 5 hosts
  hosts: rpi5
  roles:
    - role: rpi5-oled
      rpi5_oled_update_interval: 10  # Update every 10 seconds
```

## Troubleshooting

If the OLED display is not working after deployment:

1. Check if I2C is enabled:
   ```
   sudo raspi-config
   ```

2. Check if the OLED device is detected:
   ```
   sudo i2cdetect -y 1
   ```

3. Check the service status:
   ```
   sudo systemctl status rpi5-oled
   ```

4. View logs:
   ```
   sudo journalctl -u rpi5-oled
   ```
