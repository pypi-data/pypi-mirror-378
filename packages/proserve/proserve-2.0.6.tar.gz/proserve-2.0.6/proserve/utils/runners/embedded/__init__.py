"""
ProServe Embedded Runners Package
Modular embedded device support for MicroPython and Arduino platforms
"""

from .device_connection import DeviceConnectionManager
from .micropython_generator import MicroPythonCodeGenerator
from .arduino_generator import ArduinoCodeGenerator
from .health_checker import EmbeddedHealthChecker
from .device_info import EmbeddedDeviceInfo
from .embedded_utils import (
    detect_platform_from_device,
    optimize_code_for_platform,
    validate_platform_compatibility,
    get_platform_memory_constraints,
    estimate_code_size,
    suggest_optimizations,
    generate_deployment_script,
    create_platform_manifest
)

__all__ = [
    'DeviceConnectionManager',
    'MicroPythonCodeGenerator', 
    'ArduinoCodeGenerator',
    'EmbeddedHealthChecker',
    'EmbeddedDeviceInfo',
    'detect_platform_from_device',
    'optimize_code_for_platform',
    'validate_platform_compatibility',
    'get_platform_memory_constraints',
    'estimate_code_size',
    'suggest_optimizations',
    'generate_deployment_script',
    'create_platform_manifest'
]
