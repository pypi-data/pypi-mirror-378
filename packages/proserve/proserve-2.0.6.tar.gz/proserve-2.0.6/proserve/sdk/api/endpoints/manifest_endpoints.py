"""
ProServe API Manifest Endpoints - Manifest Operations
Handles manifest updates and validation
"""

import json
from typing import Dict, Any
from aiohttp.web import Request, Response, json_response
import structlog

from ..models import APIResponse
from ...validators.manifest_validator import validate_manifest_comprehensive


logger = structlog.get_logger(__name__)


class ManifestOperationEndpoints:
    """HTTP endpoint handlers for manifest operations"""
    
    def __init__(self, store):
        self.store = store
    
    async def update_manifest(self, request: Request) -> Response:
        """Update project manifest"""
        try:
            project_id = request.match_info['project_id']
            manifest_data = await request.json()
            
            # Get existing project
            project = await self.store.get_project(project_id)
            if not project:
                return json_response(
                    APIResponse.error_response("Not found", f"Project {project_id} not found").to_dict(),
                    status=404
                )
            
            # Update manifest
            project.update_manifest(manifest_data)
            success = await self.store.update_project(project)
            
            if not success:
                return json_response(
                    APIResponse.error_response("Update failed", "Failed to update manifest").to_dict(),
                    status=500
                )
            
            logger.info(f"Updated manifest for project: {project.name} ({project_id})")
            
            return json_response(
                APIResponse.success_response(
                    project.manifest,
                    "Manifest updated successfully"
                ).to_dict()
            )
            
        except json.JSONDecodeError:
            return json_response(
                APIResponse.error_response("Invalid JSON", "Request body must be valid JSON").to_dict(),
                status=400
            )
        except Exception as e:
            logger.error(f"Error updating manifest: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to update manifest").to_dict(),
                status=500
            )
    
    async def validate_manifest(self, request: Request) -> Response:
        """Validate manifest configuration"""
        try:
            manifest_data = await request.json()
            
            # Perform comprehensive validation
            validation_result = validate_manifest_comprehensive(manifest_data)
            
            return json_response(
                APIResponse.success_response(validation_result).to_dict()
            )
            
        except json.JSONDecodeError:
            return json_response(
                APIResponse.error_response("Invalid JSON", "Request body must be valid JSON").to_dict(),
                status=400
            )
        except Exception as e:
            logger.error(f"Error validating manifest: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to validate manifest").to_dict(),
                status=500
            )
