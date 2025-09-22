"""
ProServe Framework and Environment Detection
Handles framework detection and environment validation
"""

import sys
import ast
import platform
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional, Union


def get_framework_info() -> Dict[str, Any]:
    """Get ProServe framework information"""
    return {
        'name': 'ProServe',
        'version': '1.0.0',
        'author': 'ProServe Development Team',
        'license': 'MIT',
        'url': 'https://github.com/proserve/proserve',
        'description': 'Professional Service Framework for Python',
        'features': [
            'Multi-platform service deployment',
            'MicroPython and Arduino support',
            'Service discovery and migration',
            'Advanced logging and monitoring',
            'Docker and container isolation',
            'WebSocket real-time communication',
            'Manifest-driven configuration',
            'CLI management tools'
        ],
        'environments': [
            'Linux (x86_64, ARM64)',
            'macOS (Intel, Apple Silicon)',
            'Windows (x86_64)',
            'MicroPython (RP2040, ESP32, ESP8266)',
            'Arduino (Uno, Nano, ESP32)',
            'Docker containers',
            'Kubernetes clusters'
        ],
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'platform': platform.platform(),
        'architecture': platform.machine(),
        'build_date': '2024-01-01'
    }


def validate_environment() -> Dict[str, Any]:
    """Validate ProServe environment and dependencies"""
    status = {
        'status': 'ok',
        'core_available': True,
        'python_version': sys.version_info[:3],
        'platform': platform.system(),
        'architecture': platform.machine(),
        'dependencies': {}
    }
    
    # Check core dependencies
    core_deps = [
        'aiohttp', 'yaml', 'structlog', 'asyncio', 'pathlib', 'dataclasses'
    ]
    
    for dep in core_deps:
        try:
            importlib.import_module(dep)
            status['dependencies'][dep] = True
        except ImportError:
            status['dependencies'][dep] = False
            if dep in ['aiohttp', 'yaml']:  # Critical dependencies
                status['status'] = 'error'
    
    # Check optional dependencies
    optional_deps = {
        'rich': 'Enhanced CLI output',
        'docker': 'Docker isolation support',
        'serial': 'Serial device communication',
        'psutil': 'System monitoring',
        'prometheus_client': 'Prometheus metrics',
        'dotenv': 'Environment file support'
    }
    
    for dep, description in optional_deps.items():
        try:
            importlib.import_module(dep)
            status['dependencies'][dep] = True
        except ImportError:
            status['dependencies'][dep] = False
    
    # Check embedded platform support
    from .platform_detection import check_micropython_support, check_arduino_support
    
    status['micropython_available'] = check_micropython_support()
    status['arduino_available'] = check_arduino_support()
    
    try:
        import serial
        status['serial_available'] = True
    except ImportError:
        status['serial_available'] = False
    
    try:
        import psutil
        status['psutil_available'] = True
    except ImportError:
        status['psutil_available'] = False
    
    return status


def detect_service_framework(file_path: Union[str, Path]) -> Optional[str]:
    """Detect web framework used in Python service file"""
    file_path = Path(file_path)
    
    if not file_path.exists() or not file_path.suffix == '.py':
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST to detect imports and framework patterns
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return None
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        # Framework detection patterns
        framework_patterns = {
            'flask': ['flask', 'Flask', '@app.route'],
            'fastapi': ['fastapi', 'FastAPI', '@app.get', '@app.post'],
            'django': ['django', 'from django', 'urls.py', 'models.py'],
            'aiohttp': ['aiohttp', 'web.Application', 'web.get', 'web.post'],
            'tornado': ['tornado', 'RequestHandler', 'Application'],
            'bottle': ['bottle', '@route', 'run('],
            'starlette': ['starlette', 'Starlette'],
            'quart': ['quart', 'Quart'],
            'sanic': ['sanic', 'Sanic']
        }
        
        # Check imports
        for framework, patterns in framework_patterns.items():
            for pattern in patterns:
                if any(pattern in imp for imp in imports):
                    return framework
        
        # Check content patterns
        for framework, patterns in framework_patterns.items():
            for pattern in patterns:
                if pattern in content:
                    return framework
        
        return None
        
    except Exception:
        return None


def safe_import(module_name: str, package: Optional[str] = None) -> Optional[object]:
    """Safely import module without raising exception"""
    try:
        if package:
            return importlib.import_module(module_name, package)
        else:
            return importlib.import_module(module_name)
    except ImportError:
        return None
