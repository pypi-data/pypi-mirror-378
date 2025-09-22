"""
ProServe Migration Templates
Framework-specific migration templates and patterns
"""

from typing import Dict, Any, List


class MigrationTemplates:
    """Framework-specific migration templates and conversion patterns"""
    
    @staticmethod
    def get_templates() -> Dict[str, Dict[str, Any]]:
        """Load framework-specific migration templates"""
        return {
            'flask': {
                'manifest_template': {
                    'name': '{service_name}',
                    'version': '1.0.0',
                    'framework': 'proserve',
                    'server': {'host': '0.0.0.0', 'port': 8000},
                    'endpoints': [],
                    'logging': {'level': 'INFO', 'format': 'json'}
                },
                'handler_imports': ['from flask import Flask, request, jsonify'],
                'converter_patterns': {
                    '@app.route': 'async def {handler_name}(request):',
                    'return jsonify': 'return web.json_response'
                }
            },
            'fastapi': {
                'manifest_template': {
                    'name': '{service_name}',
                    'version': '1.0.0', 
                    'framework': 'proserve',
                    'server': {'host': '0.0.0.0', 'port': 8000},
                    'endpoints': [],
                    'logging': {'level': 'INFO', 'format': 'json'}
                },
                'handler_imports': ['from fastapi import FastAPI, Request'],
                'converter_patterns': {
                    '@app.get': 'async def {handler_name}(request):',
                    '@app.post': 'async def {handler_name}(request):'
                }
            },
            'django': {
                'manifest_template': {
                    'name': '{service_name}',
                    'version': '1.0.0',
                    'framework': 'proserve', 
                    'server': {'host': '0.0.0.0', 'port': 8000},
                    'endpoints': [],
                    'database': {'type': 'sqlite', 'url': 'sqlite:///db.sqlite3'},
                    'logging': {'level': 'INFO', 'format': 'json'}
                },
                'handler_imports': ['from django.http import JsonResponse'],
                'converter_patterns': {
                    'def ': 'async def {handler_name}(request):',
                    'JsonResponse': 'web.json_response'
                }
            }
        }
    
    @staticmethod
    def get_framework_recommendations(framework: str) -> List[str]:
        """Get framework-specific migration recommendations"""
        
        recommendations = {
            'flask': [
                "Review Flask Blueprint usage and convert to ProServe handlers",
                "Check Flask-SQLAlchemy models and convert to async database operations",
                "Update session management for async compatibility"
            ],
            'django': [
                "Convert Django models to async database operations",
                "Review middleware and convert to ProServe middleware",
                "Update URL patterns to ProServe endpoint format",
                "Convert Django ORM queries to async database operations"
            ],
            'fastapi': [
                "FastAPI migration is typically straightforward",
                "Review Pydantic models and adapt to ProServe validation",
                "Update dependency injection patterns"
            ],
            'express': [
                "Convert Express middleware to ProServe middleware",
                "Update route handlers to async Python functions",
                "Review npm dependencies and find Python equivalents"
            ]
        }
        
        return recommendations.get(framework, [
            "Review original framework patterns",
            "Update handlers for async compatibility",
            "Test all endpoints thoroughly"
        ])
    
    @staticmethod
    def get_handler_template(endpoint: Dict[str, Any]) -> str:
        """Generate ProServe handler code template"""
        
        handler_name = MigrationTemplates._generate_handler_name(endpoint['path'])
        methods = endpoint['methods']
        
        code = f'''"""
ProServe Handler for {endpoint['path']}
Auto-generated from {endpoint['framework']} migration
"""

from aiohttp import web
from typing import Dict, Any


async def {handler_name}(request: web.Request) -> web.Response:
    """Handle {' '.join(methods)} {endpoint['path']}"""
    
    method = request.method
    
'''
        
        for method in methods:
            code += f'''    if method == "{method}":
        # TODO: Implement {method} logic for {endpoint['path']}
        return web.json_response({{"message": "{method} {endpoint['path']} endpoint"}})
    
'''
        
        code += '''    return web.json_response({"error": "Method not allowed"}, status=405)
'''
        
        return code
    
    @staticmethod
    def _generate_handler_name(path: str) -> str:
        """Generate handler name from endpoint path"""
        import re
        # Convert /api/users/{id} -> api_users_id
        name = re.sub(r'[^a-zA-Z0-9_]', '_', path.strip('/'))
        name = re.sub(r'_+', '_', name)
        return name.strip('_') or 'index'
