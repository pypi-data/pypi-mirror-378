"""
ProServe Framework-Specific Endpoint Detection
Framework-specific endpoint detection logic for Flask, FastAPI, Django, etc.
"""

import re
from typing import List
from pathlib import Path
import structlog

from .service_models import Framework, EndpointInfo

logger = structlog.get_logger(__name__)


class EndpointDetectors:
    """Framework-specific endpoint detection"""
    
    def detect_endpoints_in_file(self, file_path: Path, framework: Framework) -> List[EndpointInfo]:
        """Detect API endpoints in a source file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if framework == Framework.FLASK:
                return self._detect_flask_endpoints(content, file_path)
            elif framework == Framework.FASTAPI:
                return self._detect_fastapi_endpoints(content, file_path)
            elif framework == Framework.DJANGO:
                return self._detect_django_endpoints(content, file_path)
            elif framework == Framework.STARLETTE:
                return self._detect_starlette_endpoints(content, file_path)
            elif framework == Framework.TORNADO:
                return self._detect_tornado_endpoints(content, file_path)
            elif framework == Framework.AIOHTTP:
                return self._detect_aiohttp_endpoints(content, file_path)
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error detecting endpoints in {file_path}: {e}")
            return []
    
    def _detect_flask_endpoints(self, content: str, file_path: Path) -> List[EndpointInfo]:
        """Detect Flask endpoints using @app.route decorators"""
        endpoints = []
        
        # Pattern to match Flask route decorators
        route_pattern = r'@(?:app|bp|blueprint)\.route\([\'"]([^\'"]+)[\'"](?:,\s*methods\s*=\s*\[([^\]]+)\])?\)'
        
        matches = re.finditer(route_pattern, content, re.MULTILINE)
        
        for match in matches:
            path = match.group(1)
            methods_str = match.group(2)
            
            # Parse methods
            methods = ['GET']  # Default method
            if methods_str:
                methods = [m.strip().strip('\'"') for m in methods_str.split(',')]
            
            # Find the function name following the decorator
            start_pos = match.end()
            remaining_content = content[start_pos:]
            func_match = re.search(r'def\s+(\w+)\s*\(([^)]*)\):', remaining_content)
            
            handler_name = None
            parameters = []
            
            if func_match:
                handler_name = func_match.group(1)
                params_str = func_match.group(2)
                if params_str:
                    parameters = [p.strip().split(':')[0].strip() for p in params_str.split(',') if p.strip()]
            
            # Create endpoint for each method
            for method in methods:
                endpoints.append(EndpointInfo(
                    path=path,
                    method=method.upper(),
                    handler_name=handler_name,
                    file_path=str(file_path),
                    parameters=parameters,
                    decorators=['@app.route']
                ))
        
        return endpoints
    
    def _detect_fastapi_endpoints(self, content: str, file_path: Path) -> List[EndpointInfo]:
        """Detect FastAPI endpoints using @app.get, @app.post, etc."""
        endpoints = []
        
        # Pattern to match FastAPI decorators
        method_patterns = {
            'GET': r'@(?:app|router)\.get\([\'"]([^\'"]+)[\'"]',
            'POST': r'@(?:app|router)\.post\([\'"]([^\'"]+)[\'"]',
            'PUT': r'@(?:app|router)\.put\([\'"]([^\'"]+)[\'"]',
            'DELETE': r'@(?:app|router)\.delete\([\'"]([^\'"]+)[\'"]',
            'PATCH': r'@(?:app|router)\.patch\([\'"]([^\'"]+)[\'"]'
        }
        
        for method, pattern in method_patterns.items():
            matches = re.finditer(pattern, content, re.MULTILINE)
            
            for match in matches:
                path = match.group(1)
                
                # Find the function name following the decorator
                start_pos = match.end()
                remaining_content = content[start_pos:]
                func_match = re.search(r'(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\):', remaining_content)
                
                handler_name = None
                parameters = []
                
                if func_match:
                    handler_name = func_match.group(1)
                    params_str = func_match.group(2)
                    if params_str:
                        # Parse FastAPI parameters (including type hints)
                        parameters = [p.strip().split(':')[0].strip() for p in params_str.split(',') if p.strip()]
                
                endpoints.append(EndpointInfo(
                    path=path,
                    method=method,
                    handler_name=handler_name,
                    file_path=str(file_path),
                    parameters=parameters,
                    decorators=[f'@app.{method.lower()}']
                ))
        
        return endpoints
    
    def _detect_django_endpoints(self, content: str, file_path: Path) -> List[EndpointInfo]:
        """Detect Django endpoints from urls.py patterns"""
        endpoints = []
        
        # Django URL patterns
        url_pattern = r'path\([\'"]([^\'"]+)[\'"],\s*(\w+)(?:\.as_view\(\))?\s*(?:,\s*name\s*=\s*[\'"]([^\'"]+)[\'"])?\)'
        
        matches = re.finditer(url_pattern, content, re.MULTILINE)
        
        for match in matches:
            path = match.group(1)
            handler_name = match.group(2)
            name = match.group(3)
            
            # Django paths don't specify methods directly, assume common ones
            methods = ['GET', 'POST']  # Default assumption
            
            for method in methods:
                endpoints.append(EndpointInfo(
                    path=path,
                    method=method,
                    handler_name=handler_name,
                    file_path=str(file_path),
                    decorators=['path()']
                ))
        
        return endpoints
    
    def _detect_starlette_endpoints(self, content: str, file_path: Path) -> List[EndpointInfo]:
        """Detect Starlette endpoints"""
        endpoints = []
        
        # Starlette route patterns
        route_pattern = r'Route\([\'"]([^\'"]+)[\'"],\s*(\w+)(?:,\s*methods\s*=\s*\[([^\]]+)\])?\)'
        
        matches = re.finditer(route_pattern, content, re.MULTILINE)
        
        for match in matches:
            path = match.group(1)
            handler_name = match.group(2)
            methods_str = match.group(3)
            
            methods = ['GET']  # Default
            if methods_str:
                methods = [m.strip().strip('\'"') for m in methods_str.split(',')]
            
            for method in methods:
                endpoints.append(EndpointInfo(
                    path=path,
                    method=method.upper(),
                    handler_name=handler_name,
                    file_path=str(file_path),
                    decorators=['Route()']
                ))
        
        return endpoints
    
    def _detect_tornado_endpoints(self, content: str, file_path: Path) -> List[EndpointInfo]:
        """Detect Tornado endpoints from handler classes"""
        endpoints = []
        
        # Look for Tornado handler classes
        handler_pattern = r'class\s+(\w+)\s*\([^)]*RequestHandler[^)]*\):'
        
        matches = re.finditer(handler_pattern, content, re.MULTILINE)
        
        for match in matches:
            handler_name = match.group(1)
            
            # Look for HTTP method handlers in the class
            start_pos = match.end()
            class_content = self._extract_class_content(content, start_pos)
            
            method_patterns = ['get', 'post', 'put', 'delete', 'patch']
            
            for method in method_patterns:
                method_pattern = rf'def\s+{method}\s*\('
                if re.search(method_pattern, class_content):
                    endpoints.append(EndpointInfo(
                        path='/*',  # Tornado routing is configured elsewhere
                        method=method.upper(),
                        handler_name=handler_name,
                        file_path=str(file_path)
                    ))
        
        return endpoints
    
    def _detect_aiohttp_endpoints(self, content: str, file_path: Path) -> List[EndpointInfo]:
        """Detect aiohttp endpoints"""
        endpoints = []
        
        # aiohttp route decorators
        route_patterns = {
            'GET': r'@routes\.get\([\'"]([^\'"]+)[\'"]',
            'POST': r'@routes\.post\([\'"]([^\'"]+)[\'"]',
            'PUT': r'@routes\.put\([\'"]([^\'"]+)[\'"]',
            'DELETE': r'@routes\.delete\([\'"]([^\'"]+)[\'"]'
        }
        
        for method, pattern in route_patterns.items():
            matches = re.finditer(pattern, content, re.MULTILINE)
            
            for match in matches:
                path = match.group(1)
                
                # Find handler function
                start_pos = match.end()
                remaining_content = content[start_pos:]
                func_match = re.search(r'(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\):', remaining_content)
                
                handler_name = None
                parameters = []
                
                if func_match:
                    handler_name = func_match.group(1)
                    params_str = func_match.group(2)
                    if params_str:
                        parameters = [p.strip().split(':')[0].strip() for p in params_str.split(',') if p.strip()]
                
                endpoints.append(EndpointInfo(
                    path=path,
                    method=method,
                    handler_name=handler_name,
                    file_path=str(file_path),
                    parameters=parameters,
                    decorators=[f'@routes.{method.lower()}']
                ))
        
        return endpoints
    
    def _extract_class_content(self, content: str, start_pos: int) -> str:
        """Extract content of a class definition"""
        lines = content[start_pos:].split('\n')
        class_lines = []
        indent_level = None
        
        for line in lines:
            if line.strip() == '':
                class_lines.append(line)
                continue
            
            current_indent = len(line) - len(line.lstrip())
            
            if indent_level is None and line.strip():
                indent_level = current_indent
            
            if current_indent >= indent_level:
                class_lines.append(line)
            else:
                break
        
        return '\n'.join(class_lines)
