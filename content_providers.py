"""
Content providers for the Raspberry Pi 5 OLED display application.
Each provider is responsible for generating specific content for the display.
"""
import utils
import config


class ContentProvider:
    """Base class for all content providers."""
    
    def __init__(self):
        """Initialize the content provider."""
        pass
    
    def get_content(self):
        """Get the content to display. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement get_content()")


class IPAddressProvider(ContentProvider):
    """Provider for IP address information."""
    
    def __init__(self):
        super().__init__()
        self.interface = config.MODULE_SETTINGS['ip_address']['interface']
    
    def get_content(self):
        """Get the IP address content."""
        ip = utils.get_ip_address(self.interface)
        return {
            'text': f"IP: {ip}"
        }


class HostnameProvider(ContentProvider):
    """Provider for hostname information."""
    
    def get_content(self):
        """Get the hostname content."""
        hostname = utils.get_hostname()
        return {
            'text': f"Host: {hostname}"
        }


class UptimeProvider(ContentProvider):
    """Provider for system uptime information."""
    
    def get_content(self):
        """Get the uptime content."""
        uptime = utils.get_uptime()
        return {
            'text': f"Up: {uptime}"
        }


class SSHStatusProvider(ContentProvider):
    """Provider for SSH service status."""
    
    def __init__(self):
        super().__init__()
        self.service_name = config.MODULE_SETTINGS['ssh_status']['service_name']
    
    def get_content(self):
        """Get the SSH status content."""
        is_active = utils.check_service_status(self.service_name)
        icon_name = "ssh_active" if is_active else "ssh_inactive"
        
        return {
            'text': "SSH: " + ("ON" if is_active else "OFF"),
            'icon': icon_name,
            'position': (120, 0)  # Position at the right side of the display
        }


class DockerStatusProvider(ContentProvider):
    """Provider for Docker service status."""
    
    def get_content(self):
        """Get the Docker status content."""
        is_active = utils.check_docker_status()
        icon_name = "docker_active" if is_active else "docker_inactive"
        
        return {
            'text': "Docker: " + ("ON" if is_active else "OFF"),
            'icon': icon_name,
            'position': (120, 24)  # Position at the bottom right of the display
        }


def get_enabled_providers():
    """Get a list of enabled content providers based on configuration."""
    providers = []
    
    provider_map = {
        'ip_address': IPAddressProvider,
        'hostname': HostnameProvider,
        'uptime': UptimeProvider,
        'ssh_status': SSHStatusProvider,
        'docker_status': DockerStatusProvider,
    }
    
    for module_name in config.ENABLED_MODULES:
        if module_name in provider_map:
            providers.append(provider_map[module_name]())
    
    return providers
