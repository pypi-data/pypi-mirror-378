"""Provider Registry - Dynamic discovery of available providers and services"""

import importlib
import pkgutil
from typing import Dict, List, Optional, Set, Tuple, Any
import diagrams


class ProviderRegistry:
    """Registry for discovering and managing diagram providers and services"""

    def __init__(self):
        self._providers_cache: Optional[Dict[str, Dict[str, List[Tuple[str, type]]]]] = None
        self._service_map: Dict[str, type] = {}

    def discover_providers(self) -> Dict[str, Dict[str, List[str]]]:
        """Discover all available providers and their services"""

        if self._providers_cache is not None:
            # Return simplified version for external use
            result = {}
            for provider, categories in self._providers_cache.items():
                result[provider] = {}
                for category, services in categories.items():
                    result[provider][category] = [name for name, _ in services]
            return result

        providers = {}
        self._service_map = {}

        # Get the diagrams package path
        diagrams_path = diagrams.__path__[0]

        # Iterate through all modules in diagrams package
        for importer, modname, ispkg in pkgutil.iter_modules([diagrams_path]):
            if ispkg and not modname.startswith('_'):
                provider = modname
                providers[provider] = {}

                # Look for category modules within the provider
                try:
                    provider_module = importlib.import_module(f"diagrams.{provider}")
                    provider_path = provider_module.__path__[0]

                    for cat_importer, cat_modname, cat_ispkg in pkgutil.iter_modules([provider_path]):
                        if not cat_ispkg and not cat_modname.startswith('_'):
                            category = cat_modname
                            services = []

                            # Import the category module and find service classes
                            try:
                                cat_module = importlib.import_module(f"diagrams.{provider}.{category}")

                                # Find all classes in the module
                                for attr_name in dir(cat_module):
                                    if not attr_name.startswith('_'):
                                        attr = getattr(cat_module, attr_name)
                                        if isinstance(attr, type):
                                            # This is a class - likely a service
                                            services.append((attr_name, attr))

                                            # Store in service map with various keys
                                            self._service_map[f"{provider}.{category}.{attr_name}"] = attr
                                            self._service_map[f"{provider}.{attr_name.lower()}"] = attr
                                            self._service_map[f"{provider}.{attr_name}"] = attr

                                if services:
                                    providers[provider][category] = services

                            except ImportError:
                                continue

                except ImportError:
                    continue

        self._providers_cache = providers
        return self.discover_providers()  # Return simplified version

    def get_service_class(self, provider: str, service: str, category: Optional[str] = None) -> Optional[type]:
        """Get the service class for a given provider and service"""

        # Ensure cache is populated
        if self._providers_cache is None:
            self.discover_providers()

        # Try direct lookup first
        if category:
            key = f"{provider}.{category}.{service}"
            if key in self._service_map:
                return self._service_map[key]

        # Try provider.service lookup
        for key_variant in [
            f"{provider}.{service}",
            f"{provider}.{service.lower()}",
            f"{provider}.{self._to_class_name(service)}"
        ]:
            if key_variant in self._service_map:
                return self._service_map[key_variant]

        # Search through all categories for this provider
        if provider in self._providers_cache:
            for cat_name, services in self._providers_cache[provider].items():
                for svc_name, svc_class in services:
                    if (svc_name.lower() == service.lower() or
                        svc_name == service or
                        svc_name == self._to_class_name(service)):
                        return svc_class

        return None

    def list_providers(self) -> List[str]:
        """List all available providers"""
        if self._providers_cache is None:
            self.discover_providers()
        return list(self._providers_cache.keys())

    def list_categories(self, provider: str) -> List[str]:
        """List categories for a provider"""
        if self._providers_cache is None:
            self.discover_providers()

        if provider in self._providers_cache:
            return list(self._providers_cache[provider].keys())
        return []

    def list_services(self, provider: str, category: str) -> List[str]:
        """List services in a category"""
        if self._providers_cache is None:
            self.discover_providers()

        if provider in self._providers_cache:
            if category in self._providers_cache[provider]:
                return [name for name, _ in self._providers_cache[provider][category]]
        return []

    def search_services(self, query: str, provider: Optional[str] = None) -> List[Dict[str, str]]:
        """Search for services by keyword"""
        if self._providers_cache is None:
            self.discover_providers()

        results = []
        query_lower = query.lower()

        for prov_name, categories in self._providers_cache.items():
            if provider and prov_name != provider:
                continue

            for cat_name, services in categories.items():
                for svc_name, _ in services:
                    if query_lower in svc_name.lower():
                        results.append({
                            "provider": prov_name,
                            "category": cat_name,
                            "service": svc_name
                        })

        return results

    def validate_service(self, provider: str, service: str) -> bool:
        """Check if a provider/service combination is valid"""
        return self.get_service_class(provider, service) is not None

    def _to_class_name(self, service: str) -> str:
        """Convert service name to class name format"""

        # Handle common abbreviations
        special_cases = {
            "ec2": "EC2",
            "s3": "S3",
            "rds": "RDS",
            "ecs": "ECS",
            "eks": "EKS",
            "elb": "ELB",
            "alb": "ALB",
            "nlb": "NLB",
            "vpc": "VPC",
            "iam": "IAM",
            "kms": "KMS",
            "sqs": "SQS",
            "sns": "SNS",
            "api": "API",
            "cdn": "CDN",
            "waf": "WAF",
            "acm": "ACM",
            "sql": "SQL",
            "apigateway": "APIGateway",
            "api_gateway": "APIGateway",
            "lambda": "Lambda",
            "dynamodb": "DynamoDB",
            "cloudfront": "CloudFront",
            "cloudwatch": "CloudWatch",
            "route53": "Route53"
        }

        lower_service = service.lower()
        if lower_service in special_cases:
            return special_cases[lower_service]

        # Convert to PascalCase
        parts = service.replace("-", "_").split("_")
        return "".join(word.capitalize() for word in parts)

    def search_services_bulk(self, queries: List[str], limit_per_query: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Search for multiple services at once

        Args:
            queries: List of search terms
            limit_per_query: Maximum results per query

        Returns:
            Dict mapping each query to its search results
        """
        results = {}

        for query in queries:
            # Get all results then limit them
            search_results = self.search_services(query)
            results[query] = search_results[:limit_per_query] if limit_per_query else search_results

        return results

    def get_services_by_category(self, provider: str, categories: List[str]) -> Dict[str, List[str]]:
        """Get services for multiple categories at once

        Args:
            provider: Provider name
            categories: List of category names

        Returns:
            Dict mapping each category to its services
        """
        results = {}

        for category in categories:
            services = self.list_services(provider, category)
            if services:
                results[category] = services
            else:
                results[category] = []

        return results

    def get_all_services_for_providers(self, providers: List[str]) -> Dict[str, Dict[str, List[str]]]:
        """Get all services for multiple providers at once

        Args:
            providers: List of provider names

        Returns:
            Dict mapping each provider to its categories and services
        """
        results = {}

        for provider in providers:
            if provider not in self.providers:
                results[provider] = {"error": f"Provider '{provider}' not found"}
                continue

            categories = self.list_categories(provider)
            provider_services = {}

            for category in categories:
                services = self.list_services(provider, category)
                if services:
                    provider_services[category] = services

            results[provider] = provider_services

        return results