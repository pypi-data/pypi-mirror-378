"""
ProServe Migration Generators
Generates manifest files, requirements, and documentation for migrated services
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
from ..discovery.detector import ServiceInfo

logger = logging.getLogger(__name__)


class ManifestGenerator:
    """Generates ProServe manifest files from service information"""
    
    @staticmethod
    async def generate(service_info: ServiceInfo, target: Path, template: Dict) -> Path:
        """Generate ProServe manifest from service info"""
        
        manifest_data = template['manifest_template'].copy()
        manifest_data['name'] = service_info.name
        
        # Convert endpoints to ProServe format
        endpoints = []
        for endpoint in service_info.endpoints:
            for method in endpoint['methods']:
                endpoints.append({
                    'path': endpoint['path'],
                    'method': method.lower(),
                    'handler': f"handlers.{endpoint['file'].replace('.py', '')}.{ManifestGenerator._generate_handler_name(endpoint['path'])}"
                })
        
        manifest_data['endpoints'] = endpoints
        
        # Add database info if detected
        if service_info.database_info:
            manifest_data['database'] = {
                'type': service_info.database_info['primary'],
                'url': f"{service_info.database_info['primary']}://localhost:5432/db"
            }
        
        # Add deployment info
        if service_info.deployment_info:
            manifest_data['deployment'] = service_info.deployment_info
        
        manifest_path = target / "manifest.yml"
        
        # Write YAML manifest
        import yaml
        with open(manifest_path, 'w') as f:
            yaml.dump(manifest_data, f, default_flow_style=False)
        
        logger.info(f"Generated manifest: {manifest_path}")
        return manifest_path
    
    @staticmethod
    def _generate_handler_name(path: str) -> str:
        """Generate handler name from endpoint path"""
        import re
        # Convert /api/users/{id} -> api_users_id
        name = re.sub(r'[^a-zA-Z0-9_]', '_', path.strip('/'))
        name = re.sub(r'_+', '_', name)
        return name.strip('_') or 'index'


class RequirementsGenerator:
    """Generates requirements.txt for migrated services"""
    
    @staticmethod
    async def generate(service_info: ServiceInfo, target: Path) -> Path:
        """Generate requirements.txt for migrated service"""
        
        requirements = [
            "# ProServe Migration Generated Requirements",
            "",
            "# Core ProServe Framework", 
            "aiohttp>=3.8.0",
            "PyYAML>=6.0",
            "structlog>=22.3.0",
            ""
        ]
        
        # Add original dependencies (filtered)
        if service_info.dependencies:
            requirements.append("# Original Dependencies (filtered)")
            for dep in service_info.dependencies:
                if dep.lower() not in ['flask', 'django', 'fastapi', 'express']:
                    requirements.append(f"{dep}")
            requirements.append("")
        
        # Add framework-specific requirements
        if service_info.database_info:
            requirements.append("# Database Dependencies")
            for db_type in service_info.database_info['types']:
                if db_type == 'postgresql':
                    requirements.append("asyncpg>=0.27.0")
                elif db_type == 'mysql':
                    requirements.append("aiomysql>=0.1.1")
                elif db_type == 'redis':
                    requirements.append("aioredis>=2.0.0")
        
        requirements_file = target / "requirements.txt"
        with open(requirements_file, 'w') as f:
            f.write('\n'.join(requirements))
        
        logger.info(f"Generated requirements: {requirements_file}")
        return requirements_file


class ReadmeGenerator:
    """Generates README documentation for migrated services"""
    
    @staticmethod
    async def generate(service_info: ServiceInfo, target: Path) -> Path:
        """Generate README for migrated service"""
        
        readme_content = f'''# {service_info.name}

Auto-migrated from {service_info.framework} to ProServe

## Service Information

- **Framework**: {service_info.framework} → ProServe  
- **Version**: {service_info.version or "1.0.0"}
- **Complexity Score**: {service_info.complexity_score}/100
- **Migration Difficulty**: {service_info.migration_difficulty}
- **Confidence**: {service_info.confidence_score:.1%}

## Endpoints

'''
        
        for endpoint in service_info.endpoints:
            readme_content += f"- **{' '.join(endpoint['methods'])}** `{endpoint['path']}`\n"
        
        readme_content += f'''

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the service:
   ```bash
   python -m proserve manifest.yml
   ```

3. Test endpoints:
   ```bash
   curl http://localhost:8000/
   ```

## Database

'''
        
        if service_info.database_info:
            readme_content += f"- **Type**: {service_info.database_info['primary']}\n"
            readme_content += f"- **All Types**: {', '.join(service_info.database_info['types'])}\n"
        else:
            readme_content += "No database detected\n"
        
        readme_content += f'''

## Deployment

'''
        
        if service_info.deployment_info:
            readme_content += f"- **Containerized**: {service_info.deployment_info.get('containerized', False)}\n"
            readme_content += f"- **Types**: {', '.join(service_info.deployment_info['types'])}\n"
        else:
            readme_content += "No deployment configuration detected\n"
        
        readme_content += '''

## Migration Notes

This service has been automatically migrated from {framework}. 
Please review and test all handlers before production use.

## TODO

- [ ] Review generated handlers
- [ ] Test all endpoints
- [ ] Update database configuration
- [ ] Configure logging
- [ ] Add error handling
- [ ] Write tests

'''.format(framework=service_info.framework)
        
        readme_file = target / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        logger.info(f"Generated README: {readme_file}")
        return readme_file


class HandlerGenerator:
    """Generates ProServe handler files from endpoint information"""
    
    @staticmethod
    async def convert_handler(service_info: ServiceInfo, endpoint: Dict, 
                             handlers_dir: Path, template: Dict) -> Path:
        """Convert endpoint to ProServe handler"""
        
        from .templates import MigrationTemplates
        
        handler_name = HandlerGenerator._generate_handler_name(endpoint['path'])
        handler_file = handlers_dir / f"{handler_name}.py"
        
        # Generate handler code
        handler_code = MigrationTemplates.get_handler_template(endpoint)
        
        with open(handler_file, 'w') as f:
            f.write(handler_code)
        
        logger.info(f"Created handler: {handler_file}")
        return handler_file
    
    @staticmethod
    def _generate_handler_name(path: str) -> str:
        """Generate handler name from endpoint path"""
        import re
        # Convert /api/users/{id} -> api_users_id
        name = re.sub(r'[^a-zA-Z0-9_]', '_', path.strip('/'))
        name = re.sub(r'_+', '_', name)
        return name.strip('_') or 'index'
