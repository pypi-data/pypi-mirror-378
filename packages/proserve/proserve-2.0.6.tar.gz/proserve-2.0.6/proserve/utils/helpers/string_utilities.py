"""
ProServe String and Formatting Utilities
Handles ID generation, name sanitization, and duration formatting
"""

import re
import uuid


def generate_service_id() -> str:
    """Generate unique service ID"""
    return f"proserve-{uuid.uuid4().hex[:8]}"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.2f}h"


def sanitize_service_name(name: str) -> str:
    """Sanitize service name for use in filenames and identifiers"""
    # Remove special characters and replace with hyphens
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '-', name)
    # Remove multiple consecutive hyphens
    sanitized = re.sub(r'-+', '-', sanitized)
    # Remove leading/trailing hyphens
    sanitized = sanitized.strip('-')
    # Convert to lowercase
    return sanitized.lower()
