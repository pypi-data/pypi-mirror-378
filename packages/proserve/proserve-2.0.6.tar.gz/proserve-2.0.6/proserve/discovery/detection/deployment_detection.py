"""
ProServe Deployment Detection
Deployment configuration detection logic
"""

import re
from typing import Optional
from pathlib import Path
import structlog

from .service_models import DeploymentInfo
from .framework_patterns import get_deployment_files

logger = structlog.get_logger(__name__)


class DeploymentDetector:
    """Deployment configuration detection"""
    
    def __init__(self):
        self.deployment_files = get_deployment_files()
    
    def detect_deployment_config(self, project_path: Path) -> Optional[DeploymentInfo]:
        """Detect deployment configuration files"""
        deployment_info = DeploymentInfo()
        
        config_files = []
        platform = None
        
        for file_name, detected_platform in self.deployment_files.items():
            file_path = project_path / file_name
            if file_path.exists():
                config_files.append(file_name)
                if not platform:  # Set first detected platform
                    platform = detected_platform
        
        if config_files:
            deployment_info.platform = platform
            deployment_info.config_files = config_files
            
            # Try to extract build/run commands from common files
            if 'Dockerfile' in config_files:
                deployment_info.build_commands = ['docker build -t app .']
                deployment_info.run_commands = ['docker run -p 8000:8000 app']
            elif 'Procfile' in config_files:
                try:
                    procfile_path = project_path / 'Procfile'
                    with open(procfile_path, 'r') as f:
                        content = f.read()
                        # Extract web process command
                        web_match = re.search(r'web:\s*(.+)', content)
                        if web_match:
                            deployment_info.run_commands = [web_match.group(1)]
                except Exception:
                    pass
            
            return deployment_info
        
        return None
