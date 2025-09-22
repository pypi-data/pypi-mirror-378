"""
ProServe API Endpoints - HTTP API Endpoint Handlers
Modular endpoint handlers for the manifest API server
"""

from typing import Dict, Any, Optional
from aiohttp.web import Request, Response
import structlog

from .storage import AsyncManifestStore
from .endpoints import (
    ProjectCRUDEndpoints,
    ManifestOperationEndpoints,
    ExportOperationEndpoints,
    TemplateOperationEndpoints,
    SearchStatisticsEndpoints,
    ImportOperationEndpoints
)


logger = structlog.get_logger(__name__)


class ManifestAPIEndpoints:
    """HTTP endpoint handlers for manifest API"""
    
    def __init__(self, store: AsyncManifestStore):
        self.store = store
        
        # Initialize modular endpoint handlers
        self.project_endpoints = ProjectCRUDEndpoints(store)
        self.manifest_endpoints = ManifestOperationEndpoints(store)
        self.export_endpoints = ExportOperationEndpoints(store)
        self.template_endpoints = TemplateOperationEndpoints(store)
        self.search_endpoints = SearchStatisticsEndpoints(store)
        self.import_endpoints = ImportOperationEndpoints(store)
    
    # Health and listing endpoints
    async def health_check(self, request: Request) -> Response:
        """Health check endpoint"""
        return await self.search_endpoints.health_check(request)
    
    async def list_projects(self, request: Request) -> Response:
        """List all projects with optional filtering"""
        return await self.search_endpoints.list_projects(request)
    
    # Project CRUD endpoints
    async def create_project(self, request: Request) -> Response:
        """Create new project"""
        return await self.project_endpoints.create_project(request)
    
    async def get_project(self, request: Request) -> Response:
        """Get project by ID"""
        return await self.project_endpoints.get_project(request)
    
    async def update_project(self, request: Request) -> Response:
        """Update existing project"""
        return await self.project_endpoints.update_project(request)
    
    async def delete_project(self, request: Request) -> Response:
        """Delete project by ID"""
        return await self.project_endpoints.delete_project(request)
    
    async def duplicate_project(self, request: Request) -> Response:
        """Duplicate an existing project"""
        return await self.project_endpoints.duplicate_project(request)
    
    # Manifest endpoints
    async def update_manifest(self, request: Request) -> Response:
        """Update project manifest"""
        return await self.manifest_endpoints.update_manifest(request)
    
    async def validate_manifest(self, request: Request) -> Response:
        """Validate manifest configuration"""
        return await self.manifest_endpoints.validate_manifest(request)
    
    # Export endpoints
    async def export_yaml(self, request: Request) -> Response:
        """Export manifest as YAML"""
        return await self.export_endpoints.export_yaml(request)
    
    async def export_json(self, request: Request) -> Response:
        """Export manifest as JSON"""
        return await self.export_endpoints.export_json(request)
    
    async def export_all(self, request: Request) -> Response:
        """Export all projects"""
        return await self.export_endpoints.export_all(request)
    
    # Template endpoints
    async def list_templates(self, request: Request) -> Response:
        """List available templates"""
        return await self.template_endpoints.list_templates(request)
    
    async def create_from_template(self, request: Request) -> Response:
        """Create project from template"""
        return await self.template_endpoints.create_from_template(request)
    
    # Search and statistics endpoints
    async def search_projects(self, request: Request) -> Response:
        """Search projects by query"""
        return await self.search_endpoints.search_projects(request)
    
    async def get_statistics(self, request: Request) -> Response:
        """Get API statistics"""
        return await self.search_endpoints.get_statistics(request)
    
    # Import endpoints
    async def import_all(self, request: Request) -> Response:
        """Import projects from JSON"""
        return await self.import_endpoints.import_all(request)
