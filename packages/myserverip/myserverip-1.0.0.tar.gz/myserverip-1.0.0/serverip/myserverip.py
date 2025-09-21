"""
serverip - A Python library to get server's public IP address from system interfaces

Author: Your Name
Version: 1.0.0
License: MIT
"""

import socket
import subprocess
import platform
import re
import netifaces
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
import ipaddress


@dataclass
class NetworkInterface:
    """Data class to store network interface information"""
    name: str
    ip_address: str
    netmask: str
    is_public: bool
    is_up: bool
    mac_address: Optional[str] = None


@dataclass
class ServerIPInfo:
    """Data class to store server IP information"""
    public_ips: List[str]
    private_ips: List[str]
    interfaces: List[NetworkInterface]
    hostname: str
    platform: str


class ServerIPLocator:
    """
    Get server's public IP address from system network interfaces
    without making external requests
    """
    
    def __init__(self):
        self.platform = platform.system().lower()
    
    def get_public_ip(self) -> Optional[str]:
        """
        Get the first available public IP address of the server
        
        Returns:
            str: Public IP address or None if not found
        """
        public_ips = self.get_all_public_ips()
        return public_ips[0] if public_ips else None
    
    def get_all_public_ips(self) -> List[str]:
        """
        Get all public IP addresses assigned to this server
        
        Returns:
            List[str]: List of public IP addresses
        """
        public_ips = []
        
        
        try:
            for interface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        ip = addr.get('addr')
                        if ip and self._is_public_ip(ip):
                            public_ips.append(ip)
        except Exception:
            pass
        

        if not public_ips:
            public_ips.extend(self._get_ips_from_system())
        
        seen = set()
        result = []
        for ip in public_ips:
            if ip not in seen:
                seen.add(ip)
                result.append(ip)
        
        return result
    
    def get_server_info(self) -> ServerIPInfo:
        """
        Get comprehensive server IP information
        
        Returns:
            ServerIPInfo: Complete server network information
        """
        interfaces = self._get_all_interfaces()
        public_ips = [iface.ip_address for iface in interfaces if iface.is_public]
        private_ips = [iface.ip_address for iface in interfaces if not iface.is_public and iface.ip_address]
        
        return ServerIPInfo(
            public_ips=public_ips,
            private_ips=private_ips,
            interfaces=interfaces,
            hostname=socket.gethostname(),
            platform=self.platform
        )
    
    def _get_all_interfaces(self) -> List[NetworkInterface]:
        """Get information about all network interfaces"""
        interfaces = []
        
        try:
            for interface_name in netifaces.interfaces():
                addrs = netifaces.ifaddresses(interface_name)
                
                # Get IPv4 addresses
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        ip = addr.get('addr')
                        netmask = addr.get('netmask')
                        
                        if ip and ip != '127.0.0.1':  # Skip localhost
                            # Get MAC address
                            mac = None
                            if netifaces.AF_LINK in addrs:
                                mac_addrs = addrs[netifaces.AF_LINK]
                                if mac_addrs:
                                    mac = mac_addrs[0].get('addr')
                            
                            interface = NetworkInterface(
                                name=interface_name,
                                ip_address=ip,
                                netmask=netmask or '',
                                is_public=self._is_public_ip(ip),
                                is_up=self._is_interface_up(interface_name),
                                mac_address=mac
                            )
                            interfaces.append(interface)
        
        except Exception as e:
            try:
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                if ip and ip != '127.0.0.1':
                    interfaces.append(NetworkInterface(
                        name='default',
                        ip_address=ip,
                        netmask='',
                        is_public=self._is_public_ip(ip),
                        is_up=True
                    ))
            except Exception:
                pass
        
        return interfaces
    
    def _get_ips_from_system(self) -> List[str]:
        """Fallback method using system commands"""
        public_ips = []
        
        try:
            if self.platform == 'linux':
                public_ips.extend(self._get_linux_ips())
            elif self.platform == 'windows':
                public_ips.extend(self._get_windows_ips())
            elif self.platform == 'darwin': 
                public_ips.extend(self._get_macos_ips())
        except Exception:
            pass
        
        return public_ips
    
    def _get_linux_ips(self) -> List[str]:
        """Get public IPs on Linux systems"""
        public_ips = []
        
        try:
            # Try ip command first
            result = subprocess.run(['ip', 'addr', 'show'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', line)
                    if match:
                        ip = match.group(1)
                        if self._is_public_ip(ip):
                            public_ips.append(ip)
        except Exception:
            pass
        
        # Fallback to ifconfig
        if not public_ips:
            try:
                result = subprocess.run(['ifconfig'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', line)
                        if match:
                            ip = match.group(1)
                            if self._is_public_ip(ip):
                                public_ips.append(ip)
            except Exception:
                pass
        
        return public_ips
    
    def _get_windows_ips(self) -> List[str]:
        """Get public IPs on Windows systems"""
        public_ips = []
        
        try:
            result = subprocess.run(['ipconfig'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'IPv4 Address' in line:
                        match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                        if match:
                            ip = match.group(1)
                            if self._is_public_ip(ip):
                                public_ips.append(ip)
        except Exception:
            pass
        
        return public_ips
    
    def _get_macos_ips(self) -> List[str]:
        """Get public IPs on macOS systems"""
        public_ips = []
        
        try:
            result = subprocess.run(['ifconfig'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'inet ' in line and 'netmask' in line:
                        match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', line)
                        if match:
                            ip = match.group(1)
                            if self._is_public_ip(ip):
                                public_ips.append(ip)
        except Exception:
            pass
        
        return public_ips
    
    def _is_public_ip(self, ip: str) -> bool:
        """Check if an IP address is public (not private/reserved)"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return not (ip_obj.is_private or 
                       ip_obj.is_loopback or 
                       ip_obj.is_multicast or 
                       ip_obj.is_reserved or 
                       ip_obj.is_link_local)
        except ValueError:
            return False
    
    def _is_interface_up(self, interface_name: str) -> bool:
        """Check if network interface is up"""
        try:
            if self.platform == 'linux':
                with open(f'/sys/class/net/{interface_name}/operstate', 'r') as f:
                    return f.read().strip() == 'up'
            else:
                return True
        except Exception:
            return True
    
    def get_default_route_ip(self) -> Optional[str]:
        """Get IP address of the default route interface"""
        try:
            gws = netifaces.gateways()
            default_gateway = gws.get('default', {}).get(netifaces.AF_INET)
            if default_gateway:
                interface = default_gateway[1]
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        ip = addr.get('addr')
                        if ip and self._is_public_ip(ip):
                            return ip
        except Exception:
            pass
        
        return None
    
    def get_interface_by_name(self, name: str) -> Optional[NetworkInterface]:
        """Get specific interface information by name"""
        interfaces = self._get_all_interfaces()
        for interface in interfaces:
            if interface.name == name:
                return interface
        return None


# Convenience functions
def get_server_public_ip() -> Optional[str]:
    """Quick function to get server's public IP"""
    locator = ServerIPLocator()
    return locator.get_public_ip()


def get_all_server_ips() -> List[str]:
    """Quick function to get all server public IPs"""
    locator = ServerIPLocator()
    return locator.get_all_public_ips()


def get_server_info() -> ServerIPInfo:
    """Quick function to get comprehensive server info"""
    locator = ServerIPLocator()
    return locator.get_server_info()


def is_public_ip(ip: str) -> bool:
    """Quick function to check if IP is public"""
    locator = ServerIPLocator()
    return locator._is_public_ip(ip)


# CLI functionality
def main():
    """Command line interface"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='Get server IP information')
    parser.add_argument('--all', action='store_true', help='Show all public IPs')
    parser.add_argument('--interfaces', action='store_true', help='Show all interfaces')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--info', action='store_true', help='Show comprehensive server info')
    
    args = parser.parse_args()
    
    try:
        locator = ServerIPLocator()
        
        if args.info:
            info = locator.get_server_info()
            if args.json:
                # Convert to dict for JSON serialization
                info_dict = {
                    'public_ips': info.public_ips,
                    'private_ips': info.private_ips,
                    'hostname': info.hostname,
                    'platform': info.platform,
                    'interfaces': [
                        {
                            'name': iface.name,
                            'ip_address': iface.ip_address,
                            'netmask': iface.netmask,
                            'is_public': iface.is_public,
                            'is_up': iface.is_up,
                            'mac_address': iface.mac_address
                        } for iface in info.interfaces
                    ]
                }
                print(json.dumps(info_dict, indent=2))
            else:
                print(f"Hostname: {info.hostname}")
                print(f"Platform: {info.platform}")
                print(f"Public IPs: {', '.join(info.public_ips) if info.public_ips else 'None'}")
                print(f"Private IPs: {', '.join(info.private_ips) if info.private_ips else 'None'}")
                print("\nInterfaces:")
                for iface in info.interfaces:
                    status = "UP" if iface.is_up else "DOWN"
                    ip_type = "PUBLIC" if iface.is_public else "PRIVATE"
                    print(f"  {iface.name}: {iface.ip_address} ({ip_type}, {status})")
        
        elif args.all:
            ips = locator.get_all_public_ips()
            if args.json:
                print(json.dumps(ips, indent=2))
            else:
                if ips:
                    print("Public IP addresses:")
                    for ip in ips:
                        print(f"  {ip}")
                else:
                    print("No public IP addresses found")
        
        elif args.interfaces:
            interfaces = locator._get_all_interfaces()
            if args.json:
                interfaces_dict = [
                    {
                        'name': iface.name,
                        'ip_address': iface.ip_address,
                        'netmask': iface.netmask,
                        'is_public': iface.is_public,
                        'is_up': iface.is_up,
                        'mac_address': iface.mac_address
                    } for iface in interfaces
                ]
                print(json.dumps(interfaces_dict, indent=2))
            else:
                print("Network Interfaces:")
                for iface in interfaces:
                    status = "UP" if iface.is_up else "DOWN"
                    ip_type = "PUBLIC" if iface.is_public else "PRIVATE"
                    print(f"  {iface.name}:")
                    print(f"    IP: {iface.ip_address} ({ip_type})")
                    print(f"    Netmask: {iface.netmask}")
                    print(f"    Status: {status}")
                    if iface.mac_address:
                        print(f"    MAC: {iface.mac_address}")
        
        else:
            # Default: show primary public IP
            ip = locator.get_public_ip()
            if ip:
                print(ip)
            else:
                print("No public IP address found")
                exit(1)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == '__main__':
    main()