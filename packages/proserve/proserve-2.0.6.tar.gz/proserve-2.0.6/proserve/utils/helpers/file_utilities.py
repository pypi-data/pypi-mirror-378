"""
ProServe File System Utilities
Handles file operations, JSON handling, and backup creation
"""

import os
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Union, Optional


def validate_manifest_path(path: Union[str, Path]) -> Path:
    """Validate and normalize manifest file path"""
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Manifest file not found: {path}")
    
    if path.suffix.lower() not in ['.yml', '.yaml']:
        raise ValueError(f"Invalid manifest file extension: {path.suffix}")
    
    return path.resolve()


def create_backup(source_path: Union[str, Path], backup_dir: Union[str, Path]) -> Path:
    """Create backup of file or directory"""
    source_path = Path(source_path)
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{source_path.name}_{timestamp}"
    backup_path = backup_dir / backup_name
    
    if source_path.is_file():
        shutil.copy2(source_path, backup_path)
    elif source_path.is_dir():
        shutil.copytree(source_path, backup_path)
    else:
        raise ValueError(f"Source path does not exist: {source_path}")
    
    return backup_path


def load_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Load JSON file with error handling"""
    file_path = Path(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in file {file_path}: {e}")


def save_json_file(data: Dict[str, Any], file_path: Union[str, Path], indent: int = 2):
    """Save data to JSON file"""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def normalize_path(path: Union[str, Path], relative_to: Optional[Path] = None) -> Path:
    """Normalize and resolve file path"""
    path = Path(path)
    
    if relative_to:
        if not path.is_absolute():
            path = relative_to / path
    
    return path.resolve()


def get_file_hash(file_path: Union[str, Path], algorithm: str = 'sha256') -> str:
    """Get file hash using specified algorithm"""
    file_path = Path(file_path)
    hash_obj = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()
