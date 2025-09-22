"""
ProServe Database Detection
Database and ORM detection logic
"""

import re
from typing import Optional
from pathlib import Path
import structlog

from .service_models import DatabaseInfo
from .framework_patterns import get_database_patterns, get_orm_patterns

logger = structlog.get_logger(__name__)


class DatabaseDetector:
    """Database and ORM detection"""
    
    def __init__(self):
        self.db_patterns = get_database_patterns()
        self.orm_patterns = get_orm_patterns()
    
    def detect_database_usage(self, file_path: Path) -> Optional[DatabaseInfo]:
        """Detect database usage in source file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            detected_dbs = []
            detected_orm = None
            
            # Check for database types
            for db_type, patterns in self.db_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                        detected_dbs.append(db_type)
                        break
            
            # Check for ORMs
            for orm, patterns in self.orm_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                        detected_orm = orm
                        break
                if detected_orm:
                    break
            
            if detected_dbs or detected_orm:
                return DatabaseInfo(
                    type=detected_dbs[0] if detected_dbs else 'unknown',
                    orm=detected_orm
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting database usage in {file_path}: {e}")
            return None
