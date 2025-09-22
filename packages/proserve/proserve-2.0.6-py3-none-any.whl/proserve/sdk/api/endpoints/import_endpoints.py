"""
ProServe API Import Endpoints - Import Operations
Handles bulk import functionality
"""

import json
from typing import Dict, Any
from aiohttp.web import Request, Response, json_response
import structlog

from ..models import APIResponse


logger = structlog.get_logger(__name__)


class ImportOperationEndpoints:
    """HTTP endpoint handlers for import operations"""
    
    def __init__(self, store):
        self.store = store
    
    async def import_all(self, request: Request) -> Response:
        """Import projects from JSON"""
        try:
            data = await request.json()
            overwrite = request.query.get('overwrite', '').lower() in ['true', '1', 'yes']
            
            import_result = await self.store.import_projects(data, overwrite=overwrite)
            
            return json_response(
                APIResponse.success_response(import_result, "Projects imported").to_dict()
            )
            
        except json.JSONDecodeError:
            return json_response(
                APIResponse.error_response("Invalid JSON", "Request body must be valid JSON").to_dict(),
                status=400
            )
        except Exception as e:
            logger.error(f"Error importing projects: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to import projects").to_dict(),
                status=500
            )
