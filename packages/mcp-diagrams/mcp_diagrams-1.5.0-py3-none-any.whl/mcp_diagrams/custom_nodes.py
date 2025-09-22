"""Custom node support for services not in the Diagrams library"""

from diagrams.custom import Custom
from typing import Optional
import os
from pathlib import Path


class GenericCustomNode:
    """Factory for creating custom nodes with generic icons"""

    # Default icon paths (can be overridden)
    ICON_DIR = Path(__file__).parent / "icons"

    # Generic icon URLs that can be used as fallbacks
    DEFAULT_ICONS = {
        "generic": "https://raw.githubusercontent.com/mingrammer/diagrams/master/resources/generic/blank/blank.png",
        "api": "https://raw.githubusercontent.com/mingrammer/diagrams/master/resources/aws/network/api-gateway.png",
        "database": "https://raw.githubusercontent.com/mingrammer/diagrams/master/resources/generic/database/sql.png",
        "storage": "https://raw.githubusercontent.com/mingrammer/diagrams/master/resources/generic/storage/storage.png",
        "user": "https://raw.githubusercontent.com/mingrammer/diagrams/master/resources/onprem/client/user.png",
        "server": "https://raw.githubusercontent.com/mingrammer/diagrams/master/resources/generic/compute/rack.png",
    }

    @classmethod
    def create_custom_node(cls, service_name: str, label: Optional[str] = None):
        """Create a custom node class for a given service"""

        # Try to find a local icon first
        icon_path = cls._find_icon(service_name)

        # If no local icon, use a default based on service type
        if not icon_path:
            icon_path = cls._get_default_icon(service_name)

        # Create the custom node class
        class DynamicCustomNode(Custom):
            def __init__(self, label_text: str = None):
                super().__init__(label_text or label or service_name, icon_path)

        return DynamicCustomNode

    @classmethod
    def _find_icon(cls, service_name: str) -> Optional[str]:
        """Try to find a local icon file for the service"""
        if not cls.ICON_DIR.exists():
            return None

        # Try different extensions
        for ext in ['.png', '.svg', '.jpg', '.jpeg']:
            icon_file = cls.ICON_DIR / f"{service_name.lower()}{ext}"
            if icon_file.exists():
                return str(icon_file)

        return None

    @classmethod
    def _get_default_icon(cls, service_name: str) -> str:
        """Get a default icon based on service type"""
        service_lower = service_name.lower()

        # Try to match common patterns
        if any(x in service_lower for x in ['api', 'gateway', 'endpoint']):
            return cls.DEFAULT_ICONS['api']
        elif any(x in service_lower for x in ['db', 'database', 'sql', 'mongo', 'redis']):
            return cls.DEFAULT_ICONS['database']
        elif any(x in service_lower for x in ['storage', 's3', 'blob', 'file']):
            return cls.DEFAULT_ICONS['storage']
        elif any(x in service_lower for x in ['user', 'client', 'customer']):
            return cls.DEFAULT_ICONS['user']
        elif any(x in service_lower for x in ['server', 'compute', 'vm', 'instance']):
            return cls.DEFAULT_ICONS['server']
        else:
            return cls.DEFAULT_ICONS['generic']


def get_custom_node_class(provider: str, service: str, label: Optional[str] = None):
    """Get a custom node class for any provider/service combination"""

    # Special handling for specific missing services
    if provider == "saas":
        if service.lower() in ['sharepoint', 'office365']:
            # Use a specific icon or URL for these services
            return GenericCustomNode.create_custom_node("office365", label or "Office 365")
        elif service.lower() in ['googledrive', 'googleworkspace']:
            return GenericCustomNode.create_custom_node("googledrive", label or "Google Drive")
        elif service.lower() == 'openai':
            return GenericCustomNode.create_custom_node("openai", label or "OpenAI")

    # Generic custom node
    return GenericCustomNode.create_custom_node(service, label)