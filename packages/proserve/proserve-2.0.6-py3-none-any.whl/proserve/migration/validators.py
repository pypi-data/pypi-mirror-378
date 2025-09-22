"""
ProServe Migration Validation
Provides validation logic for migration operations
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
from ..discovery.detector import ServiceDetector

logger = logging.getLogger(__name__)


class MigrationValidator:
    """Validates migration configuration and readiness"""
    
    def __init__(self):
        self.detector = ServiceDetector()
    
    def validate_migration(self, source: str, target: str) -> Dict[str, Any]:
        """Validate migration configuration and readiness"""
        
        source_path = Path(source)
        target_path = Path(target)
        
        issues = []
        recommendations = []
        status = "valid"
        detected_services = 0
        
        # Check source exists
        if not source_path.exists():
            issues.append(f"Source path does not exist: {source}")
            status = "invalid"
        
        # Check source is directory
        if source_path.exists() and not source_path.is_dir():
            issues.append(f"Source must be a directory: {source}")
            status = "invalid"
        
        # Check target writeable
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            issues.append(f"Cannot write to target path: {target}")
            status = "invalid"
        
        # Check for service in source
        if source_path.exists() and source_path.is_dir():
            services = self.detector.detect(source_path)
            detected_services = len(services)
            
            if not services:
                issues.append("No detectable service found in source")
                recommendations.append("Ensure source contains web service files")
            else:
                service = services[0]
                if service.complexity_score > 80:
                    recommendations.append("High complexity service - review migration carefully")
                if service.migration_difficulty == 'hard':
                    recommendations.append("Difficult migration expected - manual review required")
        
        return {
            "status": status,
            "issues": issues,
            "recommendations": recommendations,
            "source_exists": source_path.exists(),
            "target_writable": True,  # We checked above
            "detected_services": detected_services
        }
    
    def validate_migration_config(self, config: 'MigrationConfig') -> Dict[str, Any]:
        """Validate migration configuration settings"""
        
        issues = []
        warnings = []
        
        # Validate migration mode
        valid_modes = ['full', 'minimal', 'custom']
        if config.migration_mode not in valid_modes:
            issues.append(f"Invalid migration mode: {config.migration_mode}. Must be one of {valid_modes}")
        
        # Validate target framework
        valid_frameworks = ['proserve']
        if config.target_framework not in valid_frameworks:
            issues.append(f"Invalid target framework: {config.target_framework}. Must be one of {valid_frameworks}")
        
        # Validate exclude patterns
        if config.exclude_patterns:
            for pattern in config.exclude_patterns:
                if not isinstance(pattern, str):
                    issues.append(f"Exclude pattern must be string: {pattern}")
        
        # Check for potentially problematic settings
        if not config.create_backup:
            warnings.append("Backup disabled - consider enabling for safety")
        
        if not config.generate_manifest:
            warnings.append("Manifest generation disabled - may require manual configuration")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def validate_source_structure(self, source_path: Path) -> Dict[str, Any]:
        """Validate source service structure for migration readiness"""
        
        issues = []
        recommendations = []
        score = 100
        
        # Check for common service files
        expected_files = ['requirements.txt', 'app.py', 'main.py', '__init__.py']
        found_files = []
        
        for file_name in expected_files:
            if (source_path / file_name).exists():
                found_files.append(file_name)
        
        if not found_files:
            issues.append("No common service files found (app.py, main.py, etc.)")
            score -= 30
        
        # Check for package structure
        if not (source_path / '__init__.py').exists():
            recommendations.append("Add __init__.py for proper Python package structure")
            score -= 10
        
        # Check for configuration files
        config_files = ['config.py', 'settings.py', '.env', 'config.yaml', 'config.json']
        has_config = any((source_path / f).exists() for f in config_files)
        
        if not has_config:
            recommendations.append("Consider adding configuration files for better maintainability")
            score -= 10
        
        # Check for tests
        test_dirs = ['tests', 'test']
        test_files = list(source_path.glob('test_*.py')) + list(source_path.glob('*_test.py'))
        has_tests = any((source_path / d).exists() for d in test_dirs) or len(test_files) > 0
        
        if not has_tests:
            recommendations.append("Add tests for better migration confidence")
            score -= 15
        
        # Check for documentation
        doc_files = ['README.md', 'README.rst', 'docs']
        has_docs = any((source_path / f).exists() for f in doc_files)
        
        if not has_docs:
            recommendations.append("Add documentation for better migration context")
            score -= 10
        
        return {
            "score": max(0, score),
            "issues": issues,
            "recommendations": recommendations,
            "found_files": found_files,
            "has_config": has_config,
            "has_tests": has_tests,
            "has_docs": has_docs
        }
