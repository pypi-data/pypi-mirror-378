"""
ProServe Network and Port Utilities
Handles port management and network utilities
"""

import socket
from typing import List

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def get_available_ports() -> List[int]:
    """Get list of available network ports"""
    available_ports = []
    
    # Common port ranges to check
    port_ranges = [
        (8000, 8100),  # Development ports
        (3000, 3010),  # Node.js common ports
        (5000, 5010),  # Flask common ports
        (9000, 9010)   # Various services
    ]
    
    if PSUTIL_AVAILABLE:
        # Get currently used ports
        used_ports = set()
        for conn in psutil.net_connections():
            if conn.laddr:
                used_ports.add(conn.laddr.port)
        
        # Check ranges for available ports
        for start, end in port_ranges:
            for port in range(start, end + 1):
                if port not in used_ports:
                    available_ports.append(port)
    else:
        # Fallback: suggest common development ports
        suggested_ports = [8000, 8080, 3000, 5000, 9000]
        available_ports.extend(suggested_ports)
    
    return sorted(available_ports)


def find_free_port(start_port: int = 8000, max_attempts: int = 100) -> int:
    """Find a free network port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    
    raise RuntimeError(f"Could not find free port in range {start_port}-{start_port + max_attempts}")
