"""Icon Validator - Ensures all nodes have valid icons and provides fallbacks"""

from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class IconValidator:
    """Validates and suggests icons for diagram nodes"""

    # Generic fallback icons by category
    CATEGORY_FALLBACKS = {
        # Compute
        "compute": [
            ("generic", "compute", "rack", "Generic compute resource"),
            ("onprem", "compute", "server", "Generic server"),
            ("generic", "device", "mobile", "Generic device")
        ],

        # Storage
        "storage": [
            ("generic", "storage", "storage", "Generic storage"),
            ("onprem", "storage", "glusterfs", "Generic distributed storage"),
        ],

        # Database
        "database": [
            ("generic", "database", "sql", "Generic database"),
            ("onprem", "database", "postgresql", "Generic SQL database"),
            ("onprem", "database", "mongodb", "Generic NoSQL database"),
        ],

        # Network
        "network": [
            ("generic", "network", "router", "Generic router"),
            ("generic", "network", "switch", "Generic switch"),
            ("generic", "network", "firewall", "Generic firewall"),
            ("onprem", "network", "haproxy", "Generic load balancer"),
        ],

        # Container
        "container": [
            ("onprem", "container", "docker", "Generic container"),
            ("k8s", "compute", "pod", "Kubernetes pod"),
        ],

        # Messaging
        "messaging": [
            ("onprem", "queue", "rabbitmq", "Generic message queue"),
            ("onprem", "queue", "kafka", "Generic streaming"),
        ],

        # Monitoring
        "monitoring": [
            ("onprem", "monitoring", "prometheus", "Generic monitoring"),
            ("onprem", "monitoring", "grafana", "Generic dashboard"),
        ],

        # Security
        "security": [
            ("generic", "network", "firewall", "Generic security"),
            ("onprem", "security", "vault", "Generic secrets management"),
        ],

        # API/Service
        "api": [
            ("onprem", "network", "nginx", "Generic API gateway"),
            ("onprem", "network", "kong", "Generic API management"),
        ],

        # Default fallback for unknown categories
        "default": [
            ("generic", "blank", "blank", "Generic component"),
            ("onprem", "client", "client", "Generic service"),
            ("generic", "device", "mobile", "Generic device"),
        ]
    }

    # Service keyword mappings to categories
    SERVICE_KEYWORDS = {
        "compute": ["ec2", "vm", "instance", "server", "compute", "machine", "host"],
        "storage": ["s3", "storage", "bucket", "blob", "disk", "volume", "filesystem"],
        "database": ["rds", "db", "database", "sql", "nosql", "postgres", "mysql", "mongo", "redis", "cache"],
        "network": ["lb", "load", "balancer", "gateway", "router", "switch", "firewall", "cdn", "dns"],
        "container": ["container", "docker", "pod", "kubernetes", "k8s", "ecs", "aks", "gke"],
        "messaging": ["queue", "message", "sns", "sqs", "kafka", "rabbitmq", "pubsub", "event"],
        "monitoring": ["monitor", "metrics", "logging", "prometheus", "grafana", "datadog"],
        "security": ["security", "iam", "auth", "vault", "secrets", "certificate", "waf"],
        "api": ["api", "gateway", "rest", "graphql", "service", "endpoint"],
    }

    def __init__(self, provider_registry):
        """Initialize with a provider registry instance"""
        self.provider_registry = provider_registry

    def validate_icon(self, provider: str, service: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if an icon exists for the given provider and service.

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if provider exists
            providers = self.provider_registry.list_providers()
            if provider not in providers:
                return False, f"Provider '{provider}' not found. Available: {', '.join(providers[:5])}..."

            # Check if service exists in provider
            categories = self.provider_registry.list_categories(provider)

            for category in categories:
                services = self.provider_registry.list_services(provider, category)
                if services and service in services:
                    return True, None

            # Service not found
            return False, f"Service '{service}' not found in provider '{provider}'"

        except Exception as e:
            logger.error(f"Error validating icon: {str(e)}")
            return False, f"Validation error: {str(e)}"

    def categorize_service(self, service_name: str, label: Optional[str] = None) -> str:
        """
        Categorize a service based on its name and label.

        Args:
            service_name: The service identifier
            label: Optional label that might contain hints

        Returns:
            Category name (compute, storage, database, etc.)
        """
        combined_text = f"{service_name} {label or ''}".lower()

        # Check each category's keywords
        for category, keywords in self.SERVICE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in combined_text:
                    return category

        # Default category
        return "default"

    def suggest_fallback_icons(
        self,
        provider: str,
        service: str,
        label: Optional[str] = None,
        limit: int = 3
    ) -> List[Dict[str, str]]:
        """
        Suggest fallback icons when the requested icon doesn't exist.

        Args:
            provider: Requested provider
            service: Requested service
            label: Optional node label for better categorization
            limit: Maximum number of suggestions

        Returns:
            List of fallback suggestions with provider, service, and reason
        """
        suggestions = []

        # First, try to find similar services in the same provider
        if provider in self.provider_registry.list_providers():
            similar = self._find_similar_services(provider, service)
            for svc in similar[:limit]:
                suggestions.append({
                    "provider": provider,
                    "service": svc["service"],
                    "category": svc["category"],
                    "reason": f"Similar service in {provider}",
                    "confidence": "high"
                })

        # If not enough suggestions, use category fallbacks
        if len(suggestions) < limit:
            category = self.categorize_service(service, label)
            fallbacks = self.CATEGORY_FALLBACKS.get(category, self.CATEGORY_FALLBACKS["default"])

            for provider_fb, category_fb, service_fb, description in fallbacks:
                if len(suggestions) >= limit:
                    break

                # Verify the fallback actually exists
                is_valid, _ = self.validate_icon(provider_fb, service_fb)
                if is_valid:
                    suggestions.append({
                        "provider": provider_fb,
                        "service": service_fb,
                        "category": category_fb,
                        "reason": description,
                        "confidence": "medium" if category != "default" else "low"
                    })

        # Always ensure at least one suggestion (generic blank)
        if not suggestions:
            suggestions.append({
                "provider": "generic",
                "service": "blank",
                "category": "blank",
                "reason": "Generic placeholder when no specific icon available",
                "confidence": "low"
            })

        return suggestions[:limit]

    def _find_similar_services(self, provider: str, service: str) -> List[Dict[str, str]]:
        """
        Find similar services in the same provider.

        Args:
            provider: Provider name
            service: Service name to match

        Returns:
            List of similar services with their categories
        """
        similar = []
        service_lower = service.lower()

        try:
            categories = self.provider_registry.list_categories(provider)

            for category in categories:
                services = self.provider_registry.list_services(provider, category)
                if not services:
                    continue

                for svc in services:
                    svc_lower = svc.lower()

                    # Exact match (different case)
                    if svc_lower == service_lower:
                        similar.insert(0, {"service": svc, "category": category, "score": 100})

                    # Partial match
                    elif service_lower in svc_lower or svc_lower in service_lower:
                        score = 80 if service_lower in svc_lower else 70
                        similar.append({"service": svc, "category": category, "score": score})

                    # Similar category match
                    elif self.categorize_service(svc) == self.categorize_service(service):
                        similar.append({"service": svc, "category": category, "score": 50})

            # Sort by score and return top matches
            similar.sort(key=lambda x: x["score"], reverse=True)
            return similar[:5]

        except Exception as e:
            logger.error(f"Error finding similar services: {str(e)}")
            return []

    def get_icon_help_message(
        self,
        provider: str,
        service: str,
        label: Optional[str] = None
    ) -> str:
        """
        Generate a helpful error message with suggestions when an icon is not found.

        Args:
            provider: Requested provider
            service: Requested service
            label: Optional node label

        Returns:
            Formatted help message with suggestions
        """
        is_valid, error_msg = self.validate_icon(provider, service)

        if is_valid:
            return f"Icon '{provider}.{service}' is valid and available."

        # Get suggestions
        suggestions = self.suggest_fallback_icons(provider, service, label, limit=3)

        message_parts = [
            f"Icon not found: {error_msg}",
            "\nSuggested alternatives:"
        ]

        for i, suggestion in enumerate(suggestions, 1):
            confidence_emoji = {
                "high": "[HIGH]",
                "medium": "🔄",
                "low": "🔍"
            }.get(suggestion["confidence"], "")

            message_parts.append(
                f"\n{i}. {confidence_emoji} Use provider='{suggestion['provider']}' "
                f"service='{suggestion['service']}'\n   Reason: {suggestion['reason']}"
            )

        message_parts.append("\n\nTips:")
        message_parts.append("\n- Use 'search_services' to find exact service names")
        message_parts.append("\n- Use 'list_services' to see all available services for a provider")
        message_parts.append("\n- Generic icons (generic.blank) always work as fallback")

        return "\n".join(message_parts)


def validate_and_suggest_icon(
    provider_registry,
    provider: str,
    service: str,
    label: Optional[str] = None
) -> Dict[str, any]:
    """
    Convenience function to validate an icon and get suggestions if invalid.

    Args:
        provider_registry: Provider registry instance
        provider: Provider name
        service: Service name
        label: Optional node label

    Returns:
        Dictionary with validation results and suggestions
    """
    validator = IconValidator(provider_registry)
    is_valid, error_msg = validator.validate_icon(provider, service)

    result = {
        "valid": is_valid,
        "provider": provider,
        "service": service,
        "error": error_msg
    }

    if not is_valid:
        result["suggestions"] = validator.suggest_fallback_icons(provider, service, label)
        result["help_message"] = validator.get_icon_help_message(provider, service, label)

    return result