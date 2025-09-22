"""
ProServe Framework Detector - Framework Detection and Analysis
Detects web frameworks and analyzes their usage patterns in source code

This module has been refactored into modular components.
All detection functionality is now available through focused modules.
"""

from typing import List, Optional, Tuple
from pathlib import Path
import structlog

from .service_models import Framework, EndpointInfo, DatabaseInfo, DeploymentInfo
from .core_detection import CoreFrameworkDetector
from .endpoint_detectors import EndpointDetectors
from .database_detection import DatabaseDetector
from .deployment_detection import DeploymentDetector

logger = structlog.get_logger(__name__)


class FrameworkDetector:
    """Advanced framework detection with confidence scoring using modular components"""
    
    def __init__(self):
        self.core_detector = CoreFrameworkDetector()
        self.endpoint_detector = EndpointDetectors()
        self.database_detector = DatabaseDetector()
        self.deployment_detector = DeploymentDetector()
    
    def detect_framework(self, file_path: Path) -> Tuple[Framework, float]:
        """Detect web framework in file with confidence score"""
        return self.core_detector.detect_framework(file_path)
    
    def detect_endpoints_in_file(self, file_path: Path, framework: Framework) -> List[EndpointInfo]:
        """Detect API endpoints in a source file"""
        return self.endpoint_detector.detect_endpoints_in_file(file_path, framework)
    
    def detect_database_usage(self, file_path: Path) -> Optional[DatabaseInfo]:
        """Detect database usage in source file"""
        return self.database_detector.detect_database_usage(file_path)
    
    def detect_deployment_config(self, project_path: Path) -> Optional[DeploymentInfo]:
        """Detect deployment configuration files"""
        return self.deployment_detector.detect_deployment_config(project_path)
