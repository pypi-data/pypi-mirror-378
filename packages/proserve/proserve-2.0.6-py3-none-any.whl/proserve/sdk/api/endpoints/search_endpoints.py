"""
ProServe API Search Endpoints - Search and Statistics Operations
Handles project search, statistics, and health checks
"""

from typing import Dict, Any
from aiohttp.web import Request, Response, json_response
import structlog

from ..models import APIResponse, ProjectFilter
from ...builders.manifest_builder import TEMPLATES


logger = structlog.get_logger(__name__)


class SearchStatisticsEndpoints:
    """HTTP endpoint handlers for search and statistics operations"""
    
    def __init__(self, store):
        self.store = store
    
    async def health_check(self, request: Request) -> Response:
        """Health check endpoint"""
        stats = await self.store.get_statistics()
        
        response_data = {
            'status': 'healthy',
            'service': 'ProServe Manifest API',
            'version': '1.0.0',
            'timestamp': APIResponse.success_response().timestamp,
            'projects': {
                'total': stats.total_projects,
                'draft': stats.draft_projects,
                'published': stats.published_projects
            }
        }
        
        return json_response(APIResponse.success_response(response_data).to_dict())
    
    async def list_projects(self, request: Request) -> Response:
        """List all projects with optional filtering"""
        try:
            # Parse query parameters for filtering
            query_params = dict(request.query)
            project_filter = ProjectFilter.from_query_params(query_params)
            
            # Check if only summaries are requested
            summaries_only = query_params.get('summaries', '').lower() in ['true', '1', 'yes']
            
            if summaries_only:
                projects = await self.store.get_project_summaries(project_filter)
            else:
                projects_list = await self.store.list_projects(project_filter)
                projects = [p.to_dict() for p in projects_list]
            
            # Add pagination info if requested
            page = int(query_params.get('page', 1))
            per_page = int(query_params.get('per_page', 50))
            
            if page > 1 or per_page < len(projects):
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                paginated_projects = projects[start_idx:end_idx]
                
                response_data = {
                    'projects': paginated_projects,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': len(projects),
                        'total_pages': (len(projects) + per_page - 1) // per_page
                    }
                }
            else:
                response_data = {
                    'projects': projects,
                    'total': len(projects)
                }
            
            return json_response(APIResponse.success_response(response_data).to_dict())
            
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to list projects").to_dict(),
                status=500
            )
    
    async def search_projects(self, request: Request) -> Response:
        """Search projects by query"""
        try:
            query = request.query.get('q', '').strip()
            
            if not query:
                return json_response(
                    APIResponse.error_response("Missing query", "Search query parameter 'q' is required").to_dict(),
                    status=400
                )
            
            projects = await self.store.search_projects(query)
            
            # Check if only summaries are requested
            summaries_only = request.query.get('summaries', '').lower() in ['true', '1', 'yes']
            
            if summaries_only:
                results = [p.get_summary() for p in projects]
            else:
                results = [p.to_dict() for p in projects]
            
            return json_response(
                APIResponse.success_response({
                    'query': query,
                    'results': results,
                    'total': len(results)
                }).to_dict()
            )
            
        except Exception as e:
            logger.error(f"Error searching projects: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to search projects").to_dict(),
                status=500
            )
    
    async def get_statistics(self, request: Request) -> Response:
        """Get API statistics"""
        try:
            stats = await self.store.get_statistics()
            
            additional_stats = {
                'all_tags': list(self.store.get_all_tags()),
                'all_authors': list(self.store.get_all_authors()),
                'available_templates': list(TEMPLATES.keys())
            }
            
            return json_response(
                APIResponse.success_response({
                    **stats.to_dict(),
                    **additional_stats
                }).to_dict()
            )
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to get statistics").to_dict(),
                status=500
            )
