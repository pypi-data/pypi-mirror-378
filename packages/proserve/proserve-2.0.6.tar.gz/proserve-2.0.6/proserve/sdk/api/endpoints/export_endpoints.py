"""
ProServe API Export Endpoints - Export Operations
Handles YAML, JSON, and bulk export functionality
"""

import json
import yaml
from typing import Dict, Any
from aiohttp.web import Request, Response, json_response
import structlog

from ..models import APIResponse


logger = structlog.get_logger(__name__)


class ExportOperationEndpoints:
    """HTTP endpoint handlers for export operations"""
    
    def __init__(self, store):
        self.store = store
    
    async def export_yaml(self, request: Request) -> Response:
        """Export manifest as YAML"""
        try:
            project_id = request.match_info['project_id']
            project = await self.store.get_project(project_id)
            
            if not project:
                return json_response(
                    APIResponse.error_response("Not found", f"Project {project_id} not found").to_dict(),
                    status=404
                )
            
            # Convert to YAML
            yaml_content = yaml.dump(project.manifest, default_flow_style=False, indent=2)
            
            return Response(
                text=yaml_content,
                headers={
                    'Content-Type': 'application/x-yaml',
                    'Content-Disposition': f'attachment; filename="{project.name}.yml"'
                }
            )
            
        except Exception as e:
            logger.error(f"Error exporting YAML: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to export YAML").to_dict(),
                status=500
            )
    
    async def export_json(self, request: Request) -> Response:
        """Export manifest as JSON"""
        try:
            project_id = request.match_info['project_id']
            project = await self.store.get_project(project_id)
            
            if not project:
                return json_response(
                    APIResponse.error_response("Not found", f"Project {project_id} not found").to_dict(),
                    status=404
                )
            
            # Convert to formatted JSON
            json_content = json.dumps(project.manifest, indent=2)
            
            return Response(
                text=json_content,
                headers={
                    'Content-Type': 'application/json',
                    'Content-Disposition': f'attachment; filename="{project.name}.json"'
                }
            )
            
        except Exception as e:
            logger.error(f"Error exporting JSON: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to export JSON").to_dict(),
                status=500
            )
    
    async def export_all(self, request: Request) -> Response:
        """Export all projects"""
        try:
            export_data = await self.store.export_all_projects()
            
            return json_response(
                APIResponse.success_response(export_data, "All projects exported").to_dict()
            )
            
        except Exception as e:
            logger.error(f"Error exporting all projects: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to export projects").to_dict(),
                status=500
            )
