"""
ProServe Embedded Utilities
Helper functions for embedded device operations and code optimization
"""

from typing import List
from .device_connection import detect_connected_devices


def detect_platform_from_device(device_port: str) -> str:
    """Detect platform type from connected device"""
    devices = detect_connected_devices()
    
    for device in devices:
        if device.port == device_port:
            return device.platform
    
    return 'unknown'


def optimize_code_for_platform(code: str, platform: str) -> str:
    """Optimize code for specific embedded platform"""
    if platform in ['esp8266']:
        # Very memory-constrained, aggressive optimization
        lines = code.split('\n')
        optimized = []
        
        for line in lines:
            # Remove comments and extra whitespace
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('//'):
                optimized.append(line)
        
        return '\n'.join(optimized)
    
    elif platform in ['rp2040', 'esp32']:
        # Moderate optimization - reduce indentation
        return code.replace('    ', '  ')
    
    else:
        # No optimization needed for platforms with more resources
        return code


def validate_platform_compatibility(platform: str, code_type: str) -> bool:
    """Validate if platform supports the specified code type"""
    micropython_platforms = ['rp2040', 'esp32', 'esp8266', 'pyboard']
    arduino_platforms = ['uno_r4_wifi', 'esp32dev', 'nano33iot', 'leonardo']
    
    if code_type.lower() == 'micropython':
        return platform in micropython_platforms
    elif code_type.lower() == 'arduino':
        return platform in arduino_platforms
    
    return False


def get_platform_memory_constraints(platform: str) -> dict:
    """Get memory constraints for different platforms"""
    constraints = {
        'esp8266': {
            'flash': 4 * 1024 * 1024,  # 4MB
            'ram': 80 * 1024,          # ~80KB usable
            'heap': 36 * 1024,         # ~36KB heap
            'optimization_level': 'aggressive'
        },
        'rp2040': {
            'flash': 2 * 1024 * 1024,  # 2MB
            'ram': 264 * 1024,         # 264KB
            'heap': 200 * 1024,        # ~200KB heap
            'optimization_level': 'moderate'
        },
        'esp32': {
            'flash': 4 * 1024 * 1024,  # 4MB+
            'ram': 520 * 1024,         # 520KB
            'heap': 300 * 1024,        # ~300KB heap
            'optimization_level': 'minimal'
        },
        'uno_r4_wifi': {
            'flash': 256 * 1024,       # 256KB
            'ram': 32 * 1024,          # 32KB
            'heap': 20 * 1024,         # ~20KB usable
            'optimization_level': 'aggressive'
        }
    }
    
    return constraints.get(platform, {
        'flash': 'unknown',
        'ram': 'unknown',
        'heap': 'unknown',
        'optimization_level': 'minimal'
    })


def estimate_code_size(code: str, code_type: str) -> dict:
    """Estimate compiled code size for different platforms"""
    lines = code.split('\n')
    non_empty_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
    
    if code_type.lower() == 'micropython':
        # Rough estimation for MicroPython bytecode
        estimated_size = len(non_empty_lines) * 20  # ~20 bytes per line average
        return {
            'source_lines': len(lines),
            'code_lines': len(non_empty_lines),
            'estimated_bytecode': estimated_size,
            'estimated_ram': estimated_size * 1.5  # Runtime overhead
        }
    
    elif code_type.lower() == 'arduino':
        # Rough estimation for Arduino compilation
        estimated_size = len(non_empty_lines) * 50  # ~50 bytes per line average
        return {
            'source_lines': len(lines),
            'code_lines': len(non_empty_lines),
            'estimated_flash': estimated_size,
            'estimated_ram': estimated_size * 0.3  # Static variables
        }
    
    return {'error': 'Unknown code type'}


def suggest_optimizations(platform: str, code: str, code_type: str) -> List[str]:
    """Suggest code optimizations for specific platform"""
    suggestions = []
    constraints = get_platform_memory_constraints(platform)
    
    if constraints.get('optimization_level') == 'aggressive':
        suggestions.extend([
            "Remove all comments and debug prints",
            "Use single-character variable names where possible",
            "Minimize string literals",
            "Avoid dynamic memory allocation",
            "Use integer arithmetic instead of floating point"
        ])
    elif constraints.get('optimization_level') == 'moderate':
        suggestions.extend([
            "Remove debug prints in production",
            "Optimize string usage",
            "Consider using const variables",
            "Minimize global variables"
        ])
    
    # Code-specific suggestions
    if 'print(' in code and code_type == 'micropython':
        suggestions.append("Consider removing print statements to save memory")
    
    if 'Serial.println(' in code and code_type == 'arduino':
        suggestions.append("Consider conditional compilation for debug output")
    
    # Platform-specific suggestions
    if platform == 'esp8266':
        suggestions.extend([
            "Avoid using large arrays",
            "Use PROGMEM for constant data",
            "Consider deep sleep for power management"
        ])
    
    return suggestions


def generate_deployment_script(platform: str, code: str, code_type: str) -> str:
    """Generate deployment script for the platform"""
    if code_type.lower() == 'micropython':
        return f"""
# MicroPython Deployment Script for {platform}
import os
import time

def deploy_service():
    print("Deploying ProServe service to {platform}...")
    
    # Save service code to main.py
    with open('main.py', 'w') as f:
        f.write('''
{code}
''')
    
    print("Service deployed successfully!")
    print("Device will restart and run the service...")
    
    # Soft reset to start the service
    import machine
    machine.soft_reset()

if __name__ == '__main__':
    deploy_service()
"""
    
    elif code_type.lower() == 'arduino':
        return f"""
/*
 * Arduino Deployment Instructions for {platform}
 * 
 * 1. Copy the generated code to your Arduino IDE
 * 2. Select the correct board: {platform}
 * 3. Select the correct port
 * 4. Upload the sketch
 * 
 * Required libraries (install via Library Manager):
 * - ArduinoJson (if using JSON)
 * - WiFiNINA (for WiFi-capable boards)
 */

// Generated ProServe service code:
{code}
"""
    
    return f"# Deployment script not available for {code_type}"


def create_platform_manifest(platform: str, service_name: str) -> dict:
    """Create a platform-specific manifest template"""
    base_manifest = {
        'name': service_name,
        'version': '1.0.0',
        'platform': platform,
        'isolation': {
            'mode': 'micropython' if platform in ['rp2040', 'esp32', 'esp8266'] else 'arduino',
            'platform': platform
        }
    }
    
    # Add platform-specific configurations
    if platform == 'esp8266':
        base_manifest.update({
            'memory_optimization': True,
            'debug_output': False,
            'power_management': 'deep_sleep'
        })
    elif platform == 'esp32':
        base_manifest.update({
            'wifi_enabled': True,
            'bluetooth_enabled': False,
            'dual_core': True
        })
    elif platform == 'rp2040':
        base_manifest.update({
            'pio_support': True,
            'multicore': True,
            'usb_serial': True
        })
    
    return base_manifest
