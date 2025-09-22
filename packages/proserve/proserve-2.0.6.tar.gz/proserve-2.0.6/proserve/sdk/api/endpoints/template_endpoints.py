"""
ProServe API Template Endpoints - Template Operations
Handles template listing and project creation from templates
"""

import json
from typing import Dict, Any
from aiohttp.web import Request, Response, json_response
import structlog

from ..models import ManifestProject, APIResponse
from ...builders.manifest_builder import from_template, TEMPLATES


logger = structlog.get_logger(__name__)


class TemplateOperationEndpoints:
    """HTTP endpoint handlers for template operations"""
    
    def __init__(self, store):
        self.store = store
    
    async def list_templates(self, request: Request) -> Response:
        """List available templates"""
        try:
            templates_info = {}
            
            for name, template_class in TEMPLATES.items():
                templates_info[name] = {
                    'name': name,
                    'description': getattr(template_class, '__doc__', f'Template for {name} services'),
                    'class': template_class.__name__
                }
            
            return json_response(
                APIResponse.success_response({
                    'templates': templates_info,
                    'total': len(templates_info)
                }).to_dict()
            )
            
        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to list templates").to_dict(),
                status=500
            )
    
    async def create_from_template(self, request: Request) -> Response:
        """Create project from template"""
        try:
            data = await request.json()
            template_name = data.get('template')
            
            if not template_name or template_name not in TEMPLATES:
                return json_response(
                    APIResponse.error_response(
                        "Invalid template", 
                        f"Template '{template_name}' not found"
                    ).to_dict(),
                    status=400
                )
            
            # Get template parameters
            template_params = data.get('parameters', {})
            
            # Create manifest from template
            manifest_builder = from_template(template_name, **template_params)
            manifest_dict = manifest_builder.build()
            
            # Create project
            project = ManifestProject(
                id="",  # Will be auto-generated
                name=data.get('name', f"{template_name}-project"),
                description=data.get('description', f"Project created from {template_name} template"),
                version=data.get('version', '1.0.0'),
                created_at="",  # Will be auto-generated
                updated_at="",  # Will be auto-generated
                author=data.get('author', 'Unknown'),
                tags=data.get('tags', [template_name]),
                manifest=manifest_dict,
                status='draft'
            )
            
            await self.store.create_project(project)
            
            logger.info(f"Created project from template '{template_name}': {project.name}")
            
            return json_response(
                APIResponse.success_response(
                    project.to_dict(),
                    f"Project created from {template_name} template"
                ).to_dict(),
                status=201
            )
            
        except json.JSONDecodeError:
            return json_response(
                APIResponse.error_response("Invalid JSON", "Request body must be valid JSON").to_dict(),
                status=400
            )
        except Exception as e:
            logger.error(f"Error creating from template: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to create project from template").to_dict(),
                status=500
            )
