"""
ProServe Migration Configuration and Data Classes
Defines configuration structures and result data for migration operations
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class MigrationResult:
    """Migration operation result"""
    success: bool
    source_path: str
    target_path: str
    framework: str
    migration_type: str
    files_created: List[str]
    files_modified: List[str]
    issues: List[str]
    recommendations: List[str]
    manifest_path: Optional[str]
    complexity_score: int
    migration_time: float
    timestamp: str


@dataclass
class MigrationConfig:
    """Migration configuration settings"""
    preserve_structure: bool = True
    create_backup: bool = True
    generate_manifest: bool = True
    include_examples: bool = True
    migration_mode: str = "full"  # full, minimal, custom
    target_framework: str = "proserve"
    custom_handlers: Dict[str, Any] = None
    exclude_patterns: List[str] = None

    def __post_init__(self):
        """Initialize default values for mutable defaults"""
        if self.custom_handlers is None:
            self.custom_handlers = {}
        if self.exclude_patterns is None:
            self.exclude_patterns = []
