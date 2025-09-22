"""
ProServe API Project Endpoints - Project CRUD Operations
Handles project creation, reading, updating, and deletion
"""

import json
from typing import Dict, Any
from aiohttp import web
from aiohttp.web import Request, Response, json_response
import structlog

from ..models import ManifestProject, APIResponse, validate_project_data


logger = structlog.get_logger(__name__)


class ProjectCRUDEndpoints:
    """HTTP endpoint handlers for project CRUD operations"""
    
    def __init__(self, store):
        self.store = store
    
    async def create_project(self, request: Request) -> Response:
        """Create new project"""
        try:
            data = await request.json()
            
            # Validate project data
            validation = validate_project_data(data)
            if not validation.valid:
                return json_response(
                    APIResponse.error_response("Validation failed", str(validation.errors)).to_dict(),
                    status=400
                )
            
            # Create project
            project = ManifestProject.from_dict(data)
            await self.store.create_project(project)
            
            logger.info(f"Created new project: {project.name} ({project.id})")
            
            return json_response(
                APIResponse.success_response(
                    project.to_dict(), 
                    f"Project '{project.name}' created successfully"
                ).to_dict(),
                status=201
            )
            
        except json.JSONDecodeError:
            return json_response(
                APIResponse.error_response("Invalid JSON", "Request body must be valid JSON").to_dict(),
                status=400
            )
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to create project").to_dict(),
                status=500
            )
    
    async def get_project(self, request: Request) -> Response:
        """Get project by ID"""
        try:
            project_id = request.match_info['project_id']
            project = await self.store.get_project(project_id)
            
            if not project:
                return json_response(
                    APIResponse.error_response("Not found", f"Project {project_id} not found").to_dict(),
                    status=404
                )
            
            return json_response(APIResponse.success_response(project.to_dict()).to_dict())
            
        except Exception as e:
            logger.error(f"Error getting project: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to get project").to_dict(),
                status=500
            )
    
    async def update_project(self, request: Request) -> Response:
        """Update existing project"""
        try:
            project_id = request.match_info['project_id']
            data = await request.json()
            
            # Get existing project
            existing_project = await self.store.get_project(project_id)
            if not existing_project:
                return json_response(
                    APIResponse.error_response("Not found", f"Project {project_id} not found").to_dict(),
                    status=404
                )
            
            # Validate updated data
            validation = validate_project_data(data)
            if not validation.valid:
                return json_response(
                    APIResponse.error_response("Validation failed", str(validation.errors)).to_dict(),
                    status=400
                )
            
            # Update project (preserve ID and creation time)
            data['id'] = existing_project.id
            data['created_at'] = existing_project.created_at
            
            updated_project = ManifestProject.from_dict(data)
            success = await self.store.update_project(updated_project)
            
            if not success:
                return json_response(
                    APIResponse.error_response("Update failed", "Failed to update project").to_dict(),
                    status=500
                )
            
            logger.info(f"Updated project: {updated_project.name} ({project_id})")
            
            return json_response(
                APIResponse.success_response(
                    updated_project.to_dict(),
                    f"Project '{updated_project.name}' updated successfully"
                ).to_dict()
            )
            
        except json.JSONDecodeError:
            return json_response(
                APIResponse.error_response("Invalid JSON", "Request body must be valid JSON").to_dict(),
                status=400
            )
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to update project").to_dict(),
                status=500
            )
    
    async def delete_project(self, request: Request) -> Response:
        """Delete project by ID"""
        try:
            project_id = request.match_info['project_id']
            
            # Check if project exists
            project = await self.store.get_project(project_id)
            if not project:
                return json_response(
                    APIResponse.error_response("Not found", f"Project {project_id} not found").to_dict(),
                    status=404
                )
            
            success = await self.store.delete_project(project_id)
            
            if not success:
                return json_response(
                    ApiResponse.error_response("Delete failed", "Failed to delete project").to_dict(),
                    status=500
                )
            
            logger.info(f"Deleted project: {project.name} ({project_id})")
            
            return json_response(
                APIResponse.success_response(
                    None,
                    f"Project '{project.name}' deleted successfully"
                ).to_dict()
            )
            
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to delete project").to_dict(),
                status=500
            )
    
    async def duplicate_project(self, request: Request) -> Response:
        """Duplicate an existing project"""
        try:
            project_id = request.match_info['project_id']
            data = await request.json() if request.has_body else {}
            
            new_name = data.get('name')
            duplicated_project = await self.store.duplicate_project(project_id, new_name)
            
            if not duplicated_project:
                return json_response(
                    APIResponse.error_response("Not found", f"Project {project_id} not found").to_dict(),
                    status=404
                )
            
            logger.info(f"Duplicated project {project_id} -> {duplicated_project.id}")
            
            return json_response(
                APIResponse.success_response(
                    duplicated_project.to_dict(),
                    f"Project duplicated successfully"
                ).to_dict(),
                status=201
            )
            
        except Exception as e:
            logger.error(f"Error duplicating project: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to duplicate project").to_dict(),
                status=500
            )
