"""Diagram Builder - wraps Python Diagrams library"""

import os
import json
import logging
import importlib
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from diagrams import Diagram, Cluster, Edge
from .models import DiagramSession, NodeInfo, ConnectionInfo, ClusterInfo
from .provider_registry import ProviderRegistry
from .custom_nodes import get_custom_node_class

logger = logging.getLogger(__name__)


class DiagramBuilder:
    """Builds diagrams using the Python Diagrams library"""

    # Map direction strings to Diagrams library format
    DIRECTION_MAP = {
        "LR": "LR",
        "RL": "RL",
        "TB": "TB",
        "BT": "BT"
    }

    def __init__(self):
        self._node_references: Dict[str, Any] = {}
        self._cluster_references: Dict[str, Any] = {}
        self._provider_registry = ProviderRegistry()
        self._service_aliases = self._load_service_aliases()

    def _load_service_aliases(self) -> Dict[str, Dict[str, str]]:
        """Load service aliases from configuration file"""
        try:
            aliases_file = Path(__file__).parent / "service_aliases.json"
            if aliases_file.exists():
                with open(aliases_file, 'r') as f:
                    config = json.load(f)
                    return config.get('aliases', {})
        except Exception as e:
            logger.warning(f"Could not load service aliases: {e}")
        return {}

    def build_from_session(self, session: DiagramSession, output_path: Optional[str] = None) -> str:
        """Build a diagram from a session state"""

        # Determine output filename
        if not output_path:
            output_path = f"{session.name.replace(' ', '_')}_{session.session_id}"

        # Remove extension if provided (Diagrams library adds it)
        base_path = os.path.splitext(output_path)[0]

        # Create the main diagram context with improved spacing
        # Spacing presets
        spacing_presets = {
            "compact": {
                "ranksep": "0.5",
                "nodesep": "0.3",
                "pad": "0.2",
                "margin": "0.1",
            },
            "normal": {
                "ranksep": "1.0",
                "nodesep": "0.5",
                "pad": "0.4",
                "margin": "0.2",
            },
            "spacious": {
                "ranksep": "1.5",
                "nodesep": "1.0",
                "pad": "0.6",
                "margin": "0.3",
            },
            "extra-spacious": {
                "ranksep": "2.0",
                "nodesep": "1.5",
                "pad": "0.8",
                "margin": "0.4",
            }
        }

        # Get spacing settings based on session preference
        spacing = spacing_presets.get(
            getattr(session, 'graph_spacing', 'normal'),
            spacing_presets['normal']
        )

        # Graph attributes for better layout
        graph_attr = {
            "fontsize": "12",
            "ranksep": spacing["ranksep"],      # Vertical spacing between ranks
            "nodesep": spacing["nodesep"],      # Horizontal spacing between nodes
            "pad": spacing["pad"],              # Padding around the graph
            "margin": spacing["margin"],        # Margin to the graph
            "compound": "true",                 # Allow edges between clusters
            "splines": "ortho",                 # Use orthogonal edges for cleaner layout
            "rankdir": self.DIRECTION_MAP.get(session.direction, "LR"),
        }

        # Node attributes for better visibility
        node_attr = {
            "fontsize": "11",
            "margin": "0.2",       # Add margin around node labels
        }

        # Edge attributes for cleaner connections
        edge_attr = {
            "fontsize": "10",
            "minlen": "2",         # Minimum edge length
        }

        with Diagram(
            name=session.name,
            filename=base_path,
            direction=self.DIRECTION_MAP.get(session.direction, "LR"),
            show=False,
            outformat=session.output_format.lower(),
            graph_attr=graph_attr,
            node_attr=node_attr,
            edge_attr=edge_attr
        ) as diagram:
            # Reset references
            self._node_references = {}
            self._cluster_references = {}

            # Build clusters first (if any)
            if session.clusters:
                self._build_clusters(session)

            # Add nodes
            for node_id, node_info in session.nodes.items():
                self._create_node(node_id, node_info, session)

            # Add connections
            for connection in session.connections:
                self._create_connection(connection)

        # Return the full path with extension
        return f"{base_path}.{session.output_format.lower()}"

    def _build_clusters(self, session: DiagramSession):
        """Build cluster hierarchy"""

        # Find root clusters (no parent)
        root_clusters = [
            cluster for cluster in session.clusters.values()
            if cluster.parent_cluster_id is None
        ]

        for cluster in root_clusters:
            self._build_cluster_recursive(cluster, session, parent_context=None)

    def _build_cluster_recursive(self, cluster: ClusterInfo, session: DiagramSession,
                                parent_context: Optional[Any] = None):
        """Recursively build clusters and their children"""

        # Create cluster context
        cluster_ctx = Cluster(cluster.label)
        self._cluster_references[cluster.id] = cluster_ctx

        # Find child clusters
        child_clusters = [
            c for c in session.clusters.values()
            if c.parent_cluster_id == cluster.id
        ]

        # Build child clusters within this cluster
        with cluster_ctx:
            for child in child_clusters:
                self._build_cluster_recursive(child, session, cluster_ctx)

    def _create_node(self, node_id: str, node_info: NodeInfo, session: DiagramSession) -> Any:
        """Create a node in the diagram"""

        # Handle common aliases
        provider = node_info.provider
        service = node_info.service

        # Check for configured aliases first
        alias_key = f"{provider}.{service}".lower()
        if alias_key in self._service_aliases:
            alias = self._service_aliases[alias_key]
            provider = alias.get('provider', provider)
            service = alias.get('service', service)
            # Log the alias usage for debugging
            if alias.get('note'):
                import sys
                logger.info(f"Using {provider}.{service} for {alias_key} - {alias['note']}")
        # Fallback to hardcoded alias for backward compatibility
        elif provider == "generic" and service.lower() == "client":
            # Redirect generic.client to onprem.client which actually exists
            provider = "onprem"
            service = "client"

        # Get the service class dynamically using the registry
        node_class = self._provider_registry.get_service_class(provider, service)
        if not node_class:
            # Fallback to the old method
            node_class = self._get_service_class(provider, service)
            if not node_class:
                # Try using a custom node as last resort
                try:
                    import sys
                    logger.warning(f"Service {node_info.provider}.{node_info.service} not found, using custom node")
                    node_class = get_custom_node_class(node_info.provider, node_info.service, node_info.label)
                except Exception as e:
                    # If custom node fails, provide helpful suggestions
                    suggestions = self._get_service_suggestions(node_info.provider, node_info.service)
                    error_msg = f"Service not found: {node_info.provider}.{node_info.service}"
                    if suggestions:
                        error_msg += f"\nDid you mean one of: {', '.join(suggestions[:3])}?"
                    raise ValueError(error_msg)

        # Determine label
        label = node_info.label or node_id

        # Check if node belongs to a cluster
        if node_info.cluster_id and node_info.cluster_id in self._cluster_references:
            # Create node within cluster context
            cluster_ctx = self._cluster_references[node_info.cluster_id]
            with cluster_ctx:
                node_instance = node_class(label, **node_info.attributes)
        else:
            # Create node in main diagram
            node_instance = node_class(label, **node_info.attributes)

        self._node_references[node_id] = node_instance
        return node_instance

    def _create_connection(self, connection: ConnectionInfo):
        """Create a connection between nodes"""

        if connection.from_node not in self._node_references:
            raise ValueError(f"From node not found: {connection.from_node}")

        if connection.to_node not in self._node_references:
            raise ValueError(f"To node not found: {connection.to_node}")

        from_node = self._node_references[connection.from_node]
        to_node = self._node_references[connection.to_node]

        # Build edge attributes
        edge_attrs = {}
        if connection.label:
            edge_attrs["label"] = connection.label
        if connection.color:
            edge_attrs["color"] = connection.color
        if connection.style:
            edge_attrs["style"] = connection.style

        # Add any custom attributes
        edge_attrs.update(connection.attributes)

        # Create the connection
        if edge_attrs:
            from_node >> Edge(**edge_attrs) >> to_node
        else:
            from_node >> to_node

    def _get_service_class(self, provider: str, service: str) -> Optional[type]:
        """Dynamically get the service class from the diagrams library"""

        try:
            # Handle special cases for provider names
            provider_module = provider.lower()

            # Map common provider names to their module names
            provider_map = {
                "aws": "aws",
                "azure": "azure",
                "gcp": "gcp",
                "k8s": "k8s",
                "kubernetes": "k8s",
                "onprem": "onprem",
                "generic": "generic",
                "programming": "programming",
                "saas": "saas",
                "firebase": "firebase",
                "elastic": "elastic",
                "oci": "oci",
                "alibabacloud": "alibabacloud",
                "outscale": "outscale",
                "ibm": "ibm",
                "digitalocean": "digitalocean",
                "openstack": "openstack"
            }

            provider_module = provider_map.get(provider_module, provider_module)

            # Try to find the service in different categories
            categories = [
                "analytics", "application", "ar", "blockchain", "business",
                "compute", "cost", "database", "devtools", "enablement",
                "enduser", "engagement", "game", "general", "integration",
                "internet", "iot", "management", "media", "migration", "ml",
                "mobile", "network", "quantum", "robotics", "satellite",
                "security", "storage", "web", "generic", "chaos", "ci", "cd",
                "client", "comm", "container", "content", "control", "database",
                "disk", "dns", "firewall", "logging", "inmemory",
                "monitoring", "os", "place", "pod", "proxy", "queue", "tracing",
                "runtime", "server", "source", "user", "vcs", "workflow"
            ]

            # Convert service name to match class naming convention
            service_class_name = self._to_class_name(service)

            for category in categories:
                try:
                    module_path = f"diagrams.{provider_module}.{category}"
                    module = importlib.import_module(module_path)

                    if hasattr(module, service_class_name):
                        return getattr(module, service_class_name)

                    # Try alternate naming conventions
                    alt_names = [
                        service_class_name,
                        service.upper(),
                        service.capitalize(),
                        service.replace("_", ""),
                        service.replace("-", "")
                    ]

                    for name in alt_names:
                        if hasattr(module, name):
                            return getattr(module, name)

                except ImportError:
                    continue

            # Try direct import from provider module
            try:
                module = importlib.import_module(f"diagrams.{provider_module}")
                if hasattr(module, service_class_name):
                    return getattr(module, service_class_name)
            except ImportError:
                pass

            return None

        except Exception:
            return None

    def _get_service_suggestions(self, provider: str, service: str) -> List[str]:
        """Get suggestions for a service that wasn't found"""
        suggestions = []

        # Check fuzzy matches from config
        try:
            aliases_file = Path(__file__).parent / "service_aliases.json"
            if aliases_file.exists():
                with open(aliases_file, 'r') as f:
                    config = json.load(f)
                    fuzzy_matches = config.get('fuzzy_matches', {})

                    service_lower = service.lower()
                    for key, values in fuzzy_matches.items():
                        if key in service_lower:
                            suggestions.extend(values)
                            break
        except Exception:
            pass

        # Also search in provider registry
        search_results = self._provider_registry.search_services(service, provider)
        for result in search_results[:3]:
            suggestions.append(f"{result['provider']}.{result['service']}")

        return suggestions[:5]  # Return top 5 suggestions

    def _to_class_name(self, service: str) -> str:
        """Convert service name to class name format"""

        # Handle common abbreviations and special cases
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