"""
ProServe Service Migrator
Advanced service migration and framework conversion tools
Ported from edpmt-framework with enhanced capabilities
"""

import asyncio
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from ..discovery.detector import ServiceDetector, ServiceInfo
from .config import MigrationConfig, MigrationResult
from .templates import MigrationTemplates
from .generators import ManifestGenerator, RequirementsGenerator, ReadmeGenerator, HandlerGenerator
from .utils import create_backup

logger = logging.getLogger(__name__)


class ServiceMigrator:
    """Advanced service migration with multi-framework support"""
    
    def __init__(self, config: Optional[MigrationConfig] = None):
        self.config = config or MigrationConfig()
        self.detector = ServiceDetector()
        self.migration_templates = self._load_migration_templates()
        
    def _load_migration_templates(self):
        """Load framework-specific migration templates"""
        return MigrationTemplates.get_templates()

    async def migrate(self, source_path: str, target_path: str) -> MigrationResult:
        """Migrate service from source to target path"""
        
        start_time = asyncio.get_event_loop().time()
        source = Path(source_path)
        target = Path(target_path)
        
        logger.info(f"Starting migration from {source} to {target}")
        
        try:
            # Detect source service
            services = self.detector.detect(source)
            if not services:
                return MigrationResult(
                    success=False,
                    source_path=source_path,
                    target_path=target_path,
                    framework="unknown",
                    migration_type="detection_failed",
                    files_created=[],
                    files_modified=[],
                    issues=["No detectable service found in source path"],
                    recommendations=["Ensure source contains a valid web service"],
                    manifest_path=None,
                    complexity_score=0,
                    migration_time=0.0,
                    timestamp=datetime.now().isoformat()
                )
            
            # Use first detected service
            service_info = services[0]
            
            # Create backup if requested
            if self.config.create_backup:
                await create_backup(source)
            
            # Prepare target directory
            target.mkdir(parents=True, exist_ok=True)
            
            # Perform migration based on framework
            result = await self._migrate_framework_service(service_info, target)
            
            # Calculate migration time
            migration_time = asyncio.get_event_loop().time() - start_time
            result.migration_time = migration_time
            
            logger.info(f"Migration completed in {migration_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return MigrationResult(
                success=False,
                source_path=source_path,
                target_path=target_path,
                framework="unknown",
                migration_type="error",
                files_created=[],
                files_modified=[],
                issues=[str(e)],
                recommendations=["Check source service structure and permissions"],
                manifest_path=None,
                complexity_score=0,
                migration_time=asyncio.get_event_loop().time() - start_time,
                timestamp=datetime.now().isoformat()
            )

    async def _migrate_framework_service(self, service_info: ServiceInfo, target: Path) -> MigrationResult:
        """Migrate service based on detected framework"""
        
        files_created = []
        files_modified = []
        issues = []
        recommendations = []
        
        framework = service_info.framework
        template = self.migration_templates.get(framework, self.migration_templates['flask'])
        
        # Generate manifest
        manifest_path = None
        if self.config.generate_manifest:
            manifest_path = await ManifestGenerator.generate(service_info, target, template)
            files_created.append(str(manifest_path))
        
        # Copy and convert handlers
        handlers_dir = target / "handlers"
        handlers_dir.mkdir(exist_ok=True)
        
        for endpoint in service_info.endpoints:
            handler_file = await HandlerGenerator.convert_handler(
                service_info, endpoint, handlers_dir, template
            )
            if handler_file:
                files_created.append(str(handler_file))
        
        # Create requirements.txt
        requirements_file = await RequirementsGenerator.generate(service_info, target)
        files_created.append(str(requirements_file))
        
        # Create README
        readme_file = await ReadmeGenerator.generate(service_info, target)
        files_created.append(str(readme_file))
        
        # Add framework-specific recommendations
        recommendations.extend(MigrationTemplates.get_framework_recommendations(framework))
        
        return MigrationResult(
            success=True,
            source_path=str(service_info.path),
            target_path=str(target),
            framework=framework,
            migration_type="framework_conversion",
            files_created=files_created,
            files_modified=files_modified,
            issues=issues,
            recommendations=recommendations,
            manifest_path=str(manifest_path) if manifest_path else None,
            complexity_score=service_info.complexity_score,
            migration_time=0.0,  # Will be set by caller
            timestamp=datetime.now().isoformat()
        )



class EDPMTMigrator(ServiceMigrator):
    """EDPMT to ProServe migration with legacy support"""
    
    async def migrate_from_edpmt(self, edpmt_service: str, proserve_target: str) -> MigrationResult:
        """Migrate from EDPMT framework to ProServe"""
        
        logger.info(f"Migrating EDPMT service: {edpmt_service}")
        
        # Use base migration with EDPMT-specific handling
        result = await self.migrate(edpmt_service, proserve_target)
        result.migration_type = "edpmt_conversion"
        
        # Add EDPMT-specific recommendations
        result.recommendations.extend([
            "Review EDPMT-specific configurations",
            "Update isolation manager usage", 
            "Convert EDPMT manifest to ProServe format",
            "Test process isolation features"
        ])
        
        return result
