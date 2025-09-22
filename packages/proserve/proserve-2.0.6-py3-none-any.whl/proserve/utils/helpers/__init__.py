"""
ProServe Helpers Package
Modular utility functions for ProServe framework operations
"""

# Framework and Environment Detection
from .framework_detection import (
    get_framework_info,
    validate_environment,
    detect_service_framework,
    safe_import
)

# Platform and Device Detection
from .platform_detection import (
    get_platform_info,
    detect_devices,
    detect_device_platform,
    is_embedded_platform,
    check_micropython_support,
    check_arduino_support,
    detect_micropython_board,
    detect_arduino_board
)

# Network and Port Utilities
from .network_utilities import (
    get_available_ports,
    find_free_port
)

# File System Utilities
from .file_utilities import (
    validate_manifest_path,
    create_backup,
    load_json_file,
    save_json_file,
    normalize_path,
    get_file_hash
)

# String and Formatting Utilities
from .string_utilities import (
    generate_service_id,
    format_duration,
    sanitize_service_name
)

# Function Utilities and Decorators
from .function_utilities import (
    measure_execution_time,
    retry_on_failure
)

__all__ = [
    # Framework and Environment Detection
    'get_framework_info',
    'validate_environment',
    'detect_service_framework',
    'safe_import',
    
    # Platform and Device Detection
    'get_platform_info',
    'detect_devices',
    'detect_device_platform',
    'is_embedded_platform',
    'check_micropython_support',
    'check_arduino_support',
    'detect_micropython_board',
    'detect_arduino_board',
    
    # Network and Port Utilities
    'get_available_ports',
    'find_free_port',
    
    # File System Utilities
    'validate_manifest_path',
    'create_backup',
    'load_json_file',
    'save_json_file',
    'normalize_path',
    'get_file_hash',
    
    # String and Formatting Utilities
    'generate_service_id',
    'format_duration',
    'sanitize_service_name',
    
    # Function Utilities and Decorators
    'measure_execution_time',
    'retry_on_failure'
]
