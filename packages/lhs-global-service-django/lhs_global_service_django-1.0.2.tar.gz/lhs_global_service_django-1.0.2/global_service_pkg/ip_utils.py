import socket
import logging

# Hostname/IP detection
class MachineIPDetector:
    def get_info(self):
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            logging.debug(f"Detected machine IP address: {ip_address}, hostname: {hostname}")
            return ip_address, hostname
        except Exception as e:
            logging.error(f"Error detecting machine IP/hostname: {e}")
            return "Unknown", "Unknown"
        
    def resolve_hostname(ip: str) -> str:
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except Exception as e:
            logging.warning(f"Could not resolve hostname for IP {ip}: {e}")
            return "unknown"
        
    