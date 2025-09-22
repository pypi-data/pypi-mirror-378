"""
ProServe Migration Utilities
Convenience functions for common migration operations
"""

import asyncio
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from .config import MigrationConfig, MigrationResult
from .validators import MigrationValidator

logger = logging.getLogger(__name__)


async def migrate_service_to_proserve(source: str, target: str = None, 
                                    config: MigrationConfig = None) -> MigrationResult:
    """Migrate any service to ProServe format"""
    
    # Import locally to avoid circular import
    from .migrator import ServiceMigrator
    
    if target is None:
        source_path = Path(source)
        target = str(source_path.parent / f"{source_path.name}_proserve")
    
    migrator = ServiceMigrator(config)
    return await migrator.migrate(source, target)


async def migrate_framework_service(framework: str, service_path: str, 
                                  target_path: str = None) -> MigrationResult:
    """Migrate specific framework service to ProServe"""
    
    # Import locally to avoid circular import
    from .migrator import ServiceMigrator
    
    if target_path is None:
        source_path = Path(service_path)
        target_path = str(source_path.parent / f"{source_path.name}_proserve")
    
    config = MigrationConfig()
    migrator = ServiceMigrator(config)
    return await migrator.migrate(service_path, target_path)


def validate_migration(source: str, target: str) -> dict:
    """Validate migration configuration and readiness"""
    validator = MigrationValidator()
    return validator.validate_migration(source, target)


async def create_backup(source: Path) -> str:
    """Create backup of source service"""
    backup_dir = source.parent / f"{source.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copytree(source, backup_dir)
    logger.info(f"Created backup at {backup_dir}")
    return str(backup_dir)


def validate_migration_config(config: MigrationConfig) -> dict:
    """Validate migration configuration settings"""
    validator = MigrationValidator()
    return validator.validate_migration_config(config)


def get_migration_summary(result: MigrationResult) -> str:
    """Generate a human-readable summary of migration results"""
    
    if not result.success:
        return f"❌ Migration failed: {', '.join(result.issues)}"
    
    summary = f"✅ Migration successful!\n"
    summary += f"   • Framework: {result.framework} → ProServe\n"
    summary += f"   • Files created: {len(result.files_created)}\n"
    summary += f"   • Files modified: {len(result.files_modified)}\n"
    summary += f"   • Complexity score: {result.complexity_score}/100\n"
    summary += f"   • Migration time: {result.migration_time:.2f}s\n"
    
    if result.issues:
        summary += f"   • Issues: {len(result.issues)}\n"
    
    if result.recommendations:
        summary += f"   • Recommendations: {len(result.recommendations)}\n"
    
    return summary


def print_migration_details(result: MigrationResult) -> None:
    """Print detailed migration results"""
    
    print(get_migration_summary(result))
    
    if result.files_created:
        print("\n📁 Created files:")
        for file_path in result.files_created:
            print(f"   • {file_path}")
    
    if result.files_modified:
        print("\n✏️  Modified files:")
        for file_path in result.files_modified:
            print(f"   • {file_path}")
    
    if result.issues:
        print("\n⚠️  Issues:")
        for issue in result.issues:
            print(f"   • {issue}")
    
    if result.recommendations:
        print("\n💡 Recommendations:")
        for rec in result.recommendations:
            print(f"   • {rec}")


async def batch_migrate_services(services: list, target_dir: str, 
                                config: MigrationConfig = None) -> list:
    """Migrate multiple services in parallel"""
    
    if config is None:
        config = MigrationConfig()
    
    migrator = ServiceMigrator(config)
    tasks = []
    
    for service_path in services:
        service_name = Path(service_path).name
        target_path = Path(target_dir) / f"{service_name}_proserve"
        task = migrator.migrate(service_path, str(target_path))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Convert exceptions to failed results
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append(MigrationResult(
                success=False,
                source_path=services[i],
                target_path="",
                framework="unknown",
                migration_type="batch_error",
                files_created=[],
                files_modified=[],
                issues=[str(result)],
                recommendations=["Check service structure and permissions"],
                manifest_path=None,
                complexity_score=0,
                migration_time=0.0,
                timestamp=datetime.now().isoformat()
            ))
        else:
            processed_results.append(result)
    
    return processed_results
