"""
ProServe Helper Functions
Utility functions for ProServe framework operations

This module has been refactored into modular components.
All functions are now available through the helpers package.
"""

# Import all functions from modular components to maintain backward compatibility
from .helpers.framework_detection import (
    get_framework_info,
    validate_environment,
    detect_service_framework,
    safe_import
)

from .helpers.platform_detection import (
    get_platform_info,
    detect_devices,
    detect_device_platform,
    is_embedded_platform,
    check_micropython_support,
    check_arduino_support,
    detect_micropython_board,
    detect_arduino_board
)

from .helpers.network_utilities import (
    get_available_ports,
    find_free_port
)

from .helpers.file_utilities import (
    validate_manifest_path,
    create_backup,
    load_json_file,
    save_json_file,
    normalize_path,
    get_file_hash
)

from .helpers.string_utilities import (
    generate_service_id,
    format_duration,
    sanitize_service_name
)

from .helpers.function_utilities import (
    measure_execution_time,
    retry_on_failure
)

# Maintain backward compatibility by exposing all functions at module level
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
