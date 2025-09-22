"""Utility functions for MCP Diagrams Server"""

import os
import re
import uuid
from pathlib import Path
from typing import Optional


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal attacks"""
    # First, handle actual path separators by extracting basename
    # This handles cases like /etc/passwd or ../../../etc/passwd
    if '/' in filename or '\\' in filename:
        # Check if this looks like a real path (not just invalid characters)
        if ('/' in filename and not any(c in filename for c in '<>:"|?*')) or \
           ('\\' in filename and not any(c in filename for c in '<>:"/|?*')):
            filename = os.path.basename(filename)
    
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading dots and spaces
    sanitized = sanitized.lstrip('. ')
    
    # If filename becomes empty or only underscores, use default
    if not sanitized or sanitized.replace('_', '').strip() == '':
        sanitized = "diagram"
    
    # Limit length
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    
    return sanitized


def get_safe_output_path(
    output_dir: Path, 
    filename: Optional[str] = None,
    extension: str = "png"
) -> Path:
    """Get a safe output path within the output directory"""
    if filename:
        # Sanitize the filename
        safe_filename = sanitize_filename(filename)
        
        # Remove any existing extension
        base_name = os.path.splitext(safe_filename)[0]
        
        # Ensure it has the correct extension
        safe_filename = f"{base_name}.{extension}"
    else:
        # Generate a unique filename
        safe_filename = f"diagram_{uuid.uuid4().hex[:8]}.{extension}"
    
    # Construct the full path
    full_path = output_dir / safe_filename
    
    # Ensure the path is within the output directory
    try:
        full_path.resolve().relative_to(output_dir.resolve())
    except ValueError:
        # Path is outside output directory, use safe default
        safe_filename = f"diagram_{uuid.uuid4().hex[:8]}.{extension}"
        full_path = output_dir / safe_filename
    
    return full_path


def validate_session_id(session_id: str) -> bool:
    """Validate that a session ID is a valid UUID"""
    try:
        # Check if it's a proper UUID format with hyphens
        uuid_obj = uuid.UUID(session_id)
        # Ensure the string representation matches (has hyphens)
        return str(uuid_obj) == session_id
    except (ValueError, TypeError):
        return False


def validate_direction(direction: str) -> bool:
    """Validate diagram direction"""
    return direction in ["LR", "RL", "TB", "BT"]


def validate_output_format(output_format: str) -> bool:
    """Validate output format"""
    return output_format.lower() in ["png", "svg", "pdf", "dot"]
