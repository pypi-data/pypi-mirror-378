"""Architecture Validator - Detects common diagramming issues and anti-patterns"""

from typing import Dict, List, Any, Optional, Set, Tuple
from .models import DiagramSession, NodeInfo, ConnectionInfo, ClusterInfo


class ArchitectureValidator:
    """Validates architectural diagrams for common issues and best practices"""

    def __init__(self):
        self.issues: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.suggestions: List[Dict[str, Any]] = []

    def validate_session(self, session: DiagramSession) -> Dict[str, Any]:
        """
        Validate a complete diagram session for architectural best practices.

        Returns:
            Dictionary with validation results including issues, warnings, and suggestions
        """
        self.issues = []
        self.warnings = []
        self.suggestions = []

        # Run all validation checks
        self._check_cluster_organization(session)
        self._check_node_placement(session)
        self._check_connection_patterns(session)
        self._check_naming_conventions(session)
        self._check_architectural_patterns(session)

        return {
            "valid": len(self.issues) == 0,
            "issues": self.issues,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "summary": self._generate_summary()
        }

    def _check_cluster_organization(self, session: DiagramSession) -> None:
        """Check for proper cluster organization and boundaries"""

        # Check if clusters exist
        if len(session.clusters) == 0 and len(session.nodes) > 5:
            self.warnings.append({
                "type": "no_clusters",
                "message": "No clusters defined for diagram with multiple nodes",
                "suggestion": "Consider grouping related nodes into clusters (frontend, backend, data)"
            })

        # Check for orphaned nodes (nodes without clusters)
        nodes_with_clusters = {node.id for node in session.nodes.values() if node.cluster_id}
        orphaned_nodes = set(session.nodes.keys()) - nodes_with_clusters

        if orphaned_nodes and len(orphaned_nodes) / len(session.nodes) > 0.3:
            self.warnings.append({
                "type": "orphaned_nodes",
                "message": f"{len(orphaned_nodes)} nodes are not in any cluster",
                "nodes": list(orphaned_nodes),
                "suggestion": "Place nodes in appropriate clusters for better organization"
            })

        # Check for overlapping responsibilities in clusters
        self._check_cluster_coherence(session)

    def _check_cluster_coherence(self, session: DiagramSession) -> None:
        """Check if clusters contain logically related services"""

        cluster_services: Dict[str, Set[str]] = {}

        for node in session.nodes.values():
            if node.cluster_id:
                if node.cluster_id not in cluster_services:
                    cluster_services[node.cluster_id] = set()

                # Categorize service type
                service_type = self._categorize_service(node)
                cluster_services[node.cluster_id].add(service_type)

        # Check for mixed responsibilities
        for cluster_id, services in cluster_services.items():
            if len(services) > 2:  # Multiple unrelated service types in one cluster
                cluster = session.clusters.get(cluster_id)
                if cluster:
                    self.warnings.append({
                        "type": "mixed_cluster_responsibilities",
                        "cluster": cluster.label,
                        "services": list(services),
                        "suggestion": "Consider separating different service types into distinct clusters"
                    })

    def _categorize_service(self, node: NodeInfo) -> str:
        """Categorize a service based on its type"""

        service_lower = node.service.lower()

        # Database services
        if any(db in service_lower for db in ['rds', 'dynamodb', 'postgresql', 'mysql', 'mongodb', 'redis', 'cache', 'aurora']):
            return "database"

        # Compute services
        if any(comp in service_lower for comp in ['ec2', 'vm', 'instance', 'droplet', 'compute', 'server']):
            return "compute"

        # Container services
        if any(cont in service_lower for cont in ['pod', 'container', 'ecs', 'aks', 'gke', 'docker', 'kubernetes']):
            return "container"

        # Networking services
        if any(net in service_lower for net in ['elb', 'alb', 'nlb', 'loadbalancer', 'gateway', 'cdn', 'route', 'vpc']):
            return "network"

        # Storage services
        if any(stor in service_lower for stor in ['s3', 'storage', 'blob', 'efs', 'disk']):
            return "storage"

        # Messaging services
        if any(msg in service_lower for msg in ['sqs', 'sns', 'kafka', 'rabbitmq', 'queue', 'pubsub']):
            return "messaging"

        # Monitoring services
        if any(mon in service_lower for mon in ['prometheus', 'grafana', 'datadog', 'monitoring', 'metrics']):
            return "monitoring"

        return "other"

    def _check_node_placement(self, session: DiagramSession) -> None:
        """Check for proper node placement within clusters"""

        # Check for databases in frontend clusters
        for node in session.nodes.values():
            if node.cluster_id:
                cluster = session.clusters.get(node.cluster_id)
                if cluster and self._categorize_service(node) == "database":
                    cluster_label_lower = cluster.label.lower()
                    if any(front in cluster_label_lower for front in ['frontend', 'web', 'presentation']):
                        self.issues.append({
                            "type": "database_in_frontend",
                            "node": node.label,
                            "cluster": cluster.label,
                            "suggestion": "Move database to a data or backend cluster"
                        })

    def _check_connection_patterns(self, session: DiagramSession) -> None:
        """Check for proper connection patterns between services"""

        # Check for circular dependencies
        self._detect_circular_dependencies(session)

        # Check for database connections from frontend
        for conn in session.connections:
            from_node = session.nodes.get(conn.from_node)
            to_node = session.nodes.get(conn.to_node)

            if from_node and to_node:
                from_category = self._categorize_service(from_node)
                to_category = self._categorize_service(to_node)

                # Frontend directly connecting to database
                if from_category == "network" and to_category == "database":
                    if from_node.cluster_id != to_node.cluster_id:
                        self.warnings.append({
                            "type": "direct_frontend_database_connection",
                            "from": from_node.label,
                            "to": to_node.label,
                            "suggestion": "Consider adding an API/application layer between frontend and database"
                        })

    def _detect_circular_dependencies(self, session: DiagramSession) -> None:
        """Detect circular dependencies in the architecture"""

        # Build adjacency list
        graph: Dict[str, Set[str]] = {}
        for conn in session.connections:
            if conn.from_node not in graph:
                graph[conn.from_node] = set()
            graph[conn.from_node].add(conn.to_node)

        # DFS to detect cycles
        visited = set()
        rec_stack = set()

        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for node in graph:
            if node not in visited:
                if has_cycle(node):
                    self.warnings.append({
                        "type": "circular_dependency",
                        "message": "Circular dependencies detected in architecture",
                        "suggestion": "Review connection patterns to eliminate circular dependencies"
                    })
                    break

    def _check_naming_conventions(self, session: DiagramSession) -> None:
        """Check for consistent naming conventions"""

        # Check for inconsistent cluster naming
        cluster_patterns = set()
        for cluster in session.clusters.values():
            if '-' in cluster.id:
                cluster_patterns.add('kebab-case')
            elif '_' in cluster.id:
                cluster_patterns.add('snake_case')
            elif cluster.id[0].isupper():
                cluster_patterns.add('PascalCase')
            else:
                cluster_patterns.add('lowercase')

        if len(cluster_patterns) > 1:
            self.suggestions.append({
                "type": "inconsistent_naming",
                "message": "Inconsistent naming patterns in cluster IDs",
                "patterns": list(cluster_patterns),
                "suggestion": "Use consistent naming convention (kebab-case recommended)"
            })

    def _check_architectural_patterns(self, session: DiagramSession) -> None:
        """Check for common architectural patterns and anti-patterns"""

        # Check for proper tier separation
        tier_keywords = {
            'frontend': ['frontend', 'web', 'ui', 'presentation', 'client'],
            'application': ['app', 'api', 'service', 'backend', 'logic'],
            'data': ['data', 'database', 'storage', 'cache', 'persistence']
        }

        found_tiers = set()
        for cluster in session.clusters.values():
            cluster_label_lower = cluster.label.lower()
            for tier, keywords in tier_keywords.items():
                if any(keyword in cluster_label_lower for keyword in keywords):
                    found_tiers.add(tier)
                    break

        # Suggest missing tiers
        if len(session.clusters) > 0:
            missing_tiers = set(tier_keywords.keys()) - found_tiers
            if missing_tiers and len(session.nodes) > 10:
                self.suggestions.append({
                    "type": "missing_architectural_tiers",
                    "missing": list(missing_tiers),
                    "suggestion": f"Consider adding {', '.join(missing_tiers)} tier(s) for better separation of concerns"
                })

        # Check for single point of failure
        self._check_single_points_of_failure(session)

    def _check_single_points_of_failure(self, session: DiagramSession) -> None:
        """Identify potential single points of failure"""

        # Count connections per node
        connection_count: Dict[str, int] = {}
        for conn in session.connections:
            connection_count[conn.to_node] = connection_count.get(conn.to_node, 0) + 1

        # Find critical nodes (many services depend on them)
        critical_threshold = max(3, len(session.nodes) * 0.3)
        critical_nodes = [
            node_id for node_id, count in connection_count.items()
            if count >= critical_threshold
        ]

        if critical_nodes:
            for node_id in critical_nodes:
                node = session.nodes.get(node_id)
                if node:
                    # Check if it's a database or critical service
                    if self._categorize_service(node) in ['database', 'messaging']:
                        self.warnings.append({
                            "type": "single_point_of_failure",
                            "node": node.label,
                            "connections": connection_count[node_id],
                            "suggestion": f"Consider adding redundancy or replica for {node.label}"
                        })

    def _generate_summary(self) -> str:
        """Generate a summary of the validation results"""

        if not self.issues and not self.warnings:
            return "Architecture looks well-organized with proper cluster boundaries."

        summary_parts = []

        if self.issues:
            summary_parts.append(f"{len(self.issues)} critical issues found")

        if self.warnings:
            summary_parts.append(f"{len(self.warnings)} warnings")

        if self.suggestions:
            summary_parts.append(f"{len(self.suggestions)} suggestions for improvement")

        return ", ".join(summary_parts)


def validate_architecture(session: DiagramSession) -> Dict[str, Any]:
    """
    Validate a diagram session for architectural best practices.

    Args:
        session: DiagramSession to validate

    Returns:
        Validation results with issues, warnings, and suggestions
    """
    validator = ArchitectureValidator()
    return validator.validate_session(session)