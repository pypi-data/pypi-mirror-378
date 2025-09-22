"""
ProServe Core Framework Detection
Core framework detection logic with confidence scoring
"""

import re
from typing import Tuple
from pathlib import Path
import structlog

from .service_models import Framework
from .framework_patterns import get_framework_patterns

logger = structlog.get_logger(__name__)


class CoreFrameworkDetector:
    """Core framework detection with confidence scoring"""
    
    def __init__(self):
        self.framework_patterns = get_framework_patterns()
    
    def detect_framework(self, file_path: Path) -> Tuple[Framework, float]:
        """Detect web framework in file with confidence score"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            framework_scores = {}
            
            for framework, patterns in self.framework_patterns.items():
                score = self._calculate_framework_score(content, patterns)
                if score > 0:
                    framework_scores[framework] = score
            
            if not framework_scores:
                return Framework.UNKNOWN, 0.0
            
            # Get framework with highest score
            best_framework = max(framework_scores.keys(), key=lambda f: framework_scores[f])
            confidence = min(1.0, framework_scores[best_framework] / 10.0)  # Normalize to 0-1
            
            return best_framework, confidence
            
        except Exception as e:
            logger.error(f"Error detecting framework in {file_path}: {e}")
            return Framework.UNKNOWN, 0.0
    
    def _calculate_framework_score(self, content: str, patterns: dict) -> float:
        """Calculate confidence score for a framework based on patterns"""
        score = 0.0
        
        # Check import patterns
        for pattern in patterns.get('import_patterns', []):
            matches = len(re.findall(pattern, content, re.IGNORECASE | re.MULTILINE))
            score += matches * 3.0  # Import patterns are strong indicators
        
        # Check decorator patterns
        for pattern in patterns.get('decorator_patterns', []):
            matches = len(re.findall(pattern, content, re.IGNORECASE | re.MULTILINE))
            score += matches * 2.0  # Decorators are good indicators
        
        return score
