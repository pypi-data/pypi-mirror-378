"""
ProServe Platform and Device Detection
Handles platform detection, device discovery, and embedded platform support
"""

import os
import sys
import platform
import subprocess
import importlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def get_platform_info() -> Dict[str, Any]:
    """Get detailed platform information"""
    info = {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'architecture': platform.architecture(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
        'is_embedded': False,
        'embedded_type': None
    }
    
    # Detect embedded platforms
    if 'micropython' in sys.implementation.name.lower():
        info['is_embedded'] = True
        info['embedded_type'] = 'micropython'
        info['board'] = detect_micropython_board()
    elif hasattr(sys, 'platform') and 'arduino' in sys.platform.lower():
        info['is_embedded'] = True
        info['embedded_type'] = 'arduino'
        info['board'] = detect_arduino_board()
    
    # Add system resources if available
    if PSUTIL_AVAILABLE:
        info.update({
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'disk_usage': psutil.disk_usage('/').total if os.name != 'nt' else psutil.disk_usage('C:').total,
            'boot_time': psutil.boot_time()
        })
    
    return info


def detect_devices() -> List[Dict[str, Any]]:
    """Detect connected devices (USB, serial, etc.)"""
    devices = []
    
    if not SERIAL_AVAILABLE:
        return devices
    
    try:
        # Detect serial ports
        ports = serial.tools.list_ports.comports()
        for port in ports:
            device_info = {
                'type': 'serial',
                'port': port.device,
                'description': port.description,
                'hwid': port.hwid,
                'vid': getattr(port, 'vid', None),
                'pid': getattr(port, 'pid', None),
                'serial_number': getattr(port, 'serial_number', None),
                'manufacturer': getattr(port, 'manufacturer', None),
                'product': getattr(port, 'product', None),
                'platform': None,
                'board': None
            }
            
            # Detect platform and board based on VID/PID
            platform_type, board = detect_device_platform(device_info)
            device_info['platform'] = platform_type
            device_info['board'] = board
            
            devices.append(device_info)
    
    except Exception as e:
        pass
    
    return devices


def detect_device_platform(device_info: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """Detect platform and board from device information"""
    vid = device_info.get('vid')
    pid = device_info.get('pid')
    description = device_info.get('description', '').lower()
    
    # Known VID/PID mappings for embedded platforms
    device_mappings = {
        # Raspberry Pi Pico (RP2040)
        (0x2E8A, 0x0005): ('rp2040', 'pico'),
        (0x2E8A, 0x000A): ('rp2040', 'pico-w'),
        
        # ESP32 devices
        (0x10C4, 0xEA60): ('esp32', 'esp32-devkit'),
        (0x1A86, 0x7523): ('esp32', 'esp32-generic'),
        (0x0403, 0x6001): ('esp32', 'esp32-ftdi'),
        
        # Arduino devices
        (0x2341, 0x0043): ('arduino', 'uno-r3'),
        (0x2341, 0x0001): ('arduino', 'uno'),
        (0x2341, 0x8036): ('arduino', 'leonardo'),
        (0x2341, 0x0036): ('arduino', 'leonardo'),
        (0x2341, 0x804D): ('arduino', 'zero'),
        (0x1B4F, 0x9206): ('arduino', 'nano'),
        
        # ESP8266 devices
        (0x10C4, 0xEA60): ('esp8266', 'nodemcu'),
        (0x1A86, 0x7523): ('esp8266', 'wemos-d1'),
    }
    
    # Check VID/PID mapping
    if vid and pid:
        mapping = device_mappings.get((vid, pid))
        if mapping:
            return mapping
    
    # Check description patterns
    description_patterns = {
        'pico': ('rp2040', 'pico'),
        'raspberry pi pico': ('rp2040', 'pico'),
        'esp32': ('esp32', 'esp32-generic'),
        'esp8266': ('esp8266', 'esp8266-generic'),
        'arduino uno': ('arduino', 'uno'),
        'arduino nano': ('arduino', 'nano'),
        'arduino leonardo': ('arduino', 'leonardo'),
        'nodemcu': ('esp8266', 'nodemcu'),
        'wemos': ('esp8266', 'wemos-d1')
    }
    
    for pattern, (platform_type, board) in description_patterns.items():
        if pattern in description:
            return platform_type, board
    
    return None, None


def is_embedded_platform(platform_name: str) -> bool:
    """Check if platform is an embedded platform"""
    embedded_platforms = [
        'rp2040', 'esp32', 'esp8266', 
        'arduino-uno', 'arduino-nano', 'arduino-leonardo',
        'micropython', 'circuitpython'
    ]
    return platform_name.lower() in embedded_platforms


def check_micropython_support() -> bool:
    """Check if MicroPython support is available"""
    try:
        # Check for common MicroPython tools
        tools = ['ampy', 'rshell', 'mpremote']
        for tool in tools:
            result = subprocess.run(['which', tool], capture_output=True, text=True)
            if result.returncode == 0:
                return True
        
        # Check for Python packages
        packages = ['ampy', 'adafruit-ampy', 'mpremote']
        for package in packages:
            try:
                importlib.import_module(package)
                return True
            except ImportError:
                continue
        
        return False
    except Exception:
        return False


def check_arduino_support() -> bool:
    """Check if Arduino support is available"""
    try:
        # Check for Arduino CLI
        result = subprocess.run(['arduino-cli', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True
        
        # Check for PlatformIO
        result = subprocess.run(['pio', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True
        
        return False
    except Exception:
        return False


def detect_micropython_board() -> Optional[str]:
    """Detect MicroPython board type"""
    try:
        # This would typically require connection to the device
        # For now, return None - can be enhanced with device communication
        return None
    except Exception:
        return None


def detect_arduino_board() -> Optional[str]:
    """Detect Arduino board type"""
    try:
        # This would typically require Arduino CLI or similar tool
        # For now, return None - can be enhanced with tool integration
        return None
    except Exception:
        return None
