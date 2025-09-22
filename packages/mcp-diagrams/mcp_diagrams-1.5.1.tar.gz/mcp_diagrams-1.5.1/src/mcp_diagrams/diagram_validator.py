"""Diagram validation before rendering"""

from typing import Dict, List, Tuple, Optional, Any
from .models import DiagramSession, NodeInfo, ConnectionInfo
import logging

logger = logging.getLogger("mcp_diagrams.validator")


class DiagramValidator:
    """Validates diagram structure before rendering"""

    # Limits for production
    MAX_NODES = 500
    MAX_CONNECTIONS = 1000
    MAX_CLUSTERS = 50
    MAX_NODE_ID_LENGTH = 100
    MAX_LABEL_LENGTH = 200
    MAX_ATTRIBUTE_SIZE = 10000  # bytes

    @classmethod
    def validate_diagram(cls, session: DiagramSession) -> Tuple[bool, List[str]]:
        """
        Validate a diagram session before rendering.

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check node count
        node_count = len(session.nodes)
        if node_count == 0:
            issues.append("Diagram has no nodes")
        elif node_count > cls.MAX_NODES:
            issues.append(f"Too many nodes: {node_count} (max: {cls.MAX_NODES})")

        # Check connection count
        connection_count = len(session.connections)
        if connection_count > cls.MAX_CONNECTIONS:
            issues.append(f"Too many connections: {connection_count} (max: {cls.MAX_CONNECTIONS})")

        # Check cluster count
        cluster_count = len(session.clusters)
        if cluster_count > cls.MAX_CLUSTERS:
            issues.append(f"Too many clusters: {cluster_count} (max: {cls.MAX_CLUSTERS})")

        # Validate nodes
        node_issues = cls._validate_nodes(session.nodes)
        issues.extend(node_issues)

        # Validate connections
        connection_issues = cls._validate_connections(session.connections, session.nodes)
        issues.extend(connection_issues)

        # Validate clusters
        if session.clusters:
            cluster_issues = cls._validate_clusters(session)
            issues.extend(cluster_issues)

        # Check for cycles in connections (could cause rendering issues)
        if connection_count > 0:
            cycle_issues = cls._check_for_problematic_cycles(session)
            issues.extend(cycle_issues)

        # Log validation results
        if issues:
            logger.warning(f"Diagram validation failed for session {session.session_id}: {issues}")
        else:
            logger.debug(f"Diagram validation passed for session {session.session_id}")

        return len(issues) == 0, issues

    @classmethod
    def _validate_nodes(cls, nodes: Dict[str, NodeInfo]) -> List[str]:
        """Validate individual nodes"""
        issues = []
        seen_labels = set()

        for node_id, node in nodes.items():
            # Check node ID length
            if len(node_id) > cls.MAX_NODE_ID_LENGTH:
                issues.append(f"Node ID too long: {node_id[:20]}... (max: {cls.MAX_NODE_ID_LENGTH})")

            # Check label length
            if node.label and len(node.label) > cls.MAX_LABEL_LENGTH:
                issues.append(f"Node label too long: {node.label[:20]}... (max: {cls.MAX_LABEL_LENGTH})")

            # Check for duplicate labels (warning only)
            if node.label:
                if node.label in seen_labels:
                    logger.debug(f"Duplicate node label: {node.label}")
                seen_labels.add(node.label)

            # Validate provider and service
            if not node.provider:
                issues.append(f"Node {node_id} missing provider")
            if not node.service:
                issues.append(f"Node {node_id} missing service")

            # Check attributes size
            if node.attributes:
                attr_size = len(str(node.attributes))
                if attr_size > cls.MAX_ATTRIBUTE_SIZE:
                    issues.append(f"Node {node_id} attributes too large: {attr_size} bytes")

        return issues

    @classmethod
    def _validate_connections(cls, connections: List[ConnectionInfo],
                               nodes: Dict[str, NodeInfo]) -> List[str]:
        """Validate connections"""
        issues = []
        connection_pairs = set()

        for conn in connections:
            # Check if nodes exist
            if conn.from_node not in nodes:
                issues.append(f"Connection from non-existent node: {conn.from_node}")
            if conn.to_node not in nodes:
                issues.append(f"Connection to non-existent node: {conn.to_node}")

            # Check for self-loops
            if conn.from_node == conn.to_node:
                logger.debug(f"Self-loop detected: {conn.from_node}")

            # Check for duplicate connections
            pair = (conn.from_node, conn.to_node)
            if pair in connection_pairs:
                logger.debug(f"Duplicate connection: {conn.from_node} -> {conn.to_node}")
            connection_pairs.add(pair)

            # Validate label length
            if conn.label and len(conn.label) > cls.MAX_LABEL_LENGTH:
                issues.append(f"Connection label too long: {conn.label[:20]}...")

        return issues

    @classmethod
    def _validate_clusters(cls, session: DiagramSession) -> List[str]:
        """Validate cluster configuration"""
        issues = []

        for cluster_id, cluster in session.clusters.items():
            # Check cluster has a label
            if not cluster.label:
                issues.append(f"Cluster {cluster_id} missing label")

            # Check parent cluster exists
            if cluster.parent_cluster_id and cluster.parent_cluster_id not in session.clusters:
                issues.append(f"Cluster {cluster_id} references non-existent parent: {cluster.parent_cluster_id}")

            # Check for circular cluster references
            visited = set()
            current = cluster
            while current.parent_cluster_id:
                if current.parent_cluster_id in visited:
                    issues.append(f"Circular cluster reference detected for {cluster_id}")
                    break
                visited.add(current.id)
                if current.parent_cluster_id not in session.clusters:
                    break
                current = session.clusters[current.parent_cluster_id]

        return issues

    @classmethod
    def _check_for_problematic_cycles(cls, session: DiagramSession) -> List[str]:
        """Check for problematic cycles that might cause rendering issues"""
        issues = []

        # Build adjacency list
        graph = {node_id: [] for node_id in session.nodes}
        for conn in session.connections:
            if conn.from_node in graph and conn.to_node in graph:
                graph[conn.from_node].append(conn.to_node)

        # Check if the graph is too densely connected (might cause rendering issues)
        max_connections_per_node = max(len(connections) for connections in graph.values()) if graph else 0
        if max_connections_per_node > 50:
            issues.append(f"Node with too many connections: {max_connections_per_node} (recommended max: 50)")

        # Count total unique edges
        total_edges = sum(len(set(connections)) for connections in graph.values())
        if len(session.nodes) > 10:
            density = total_edges / (len(session.nodes) * (len(session.nodes) - 1))
            if density > 0.5:  # More than 50% of possible connections exist
                logger.warning(f"Graph is very dense: {density:.2%} connection density")

        return issues

    @classmethod
    def suggest_optimizations(cls, session: DiagramSession) -> List[str]:
        """Suggest optimizations for better rendering"""
        suggestions = []

        node_count = len(session.nodes)
        connection_count = len(session.connections)

        # Suggest using clusters for large diagrams
        if node_count > 50 and len(session.clusters) == 0:
            suggestions.append("Consider using clusters to organize nodes in large diagrams")

        # Suggest connection reduction
        if connection_count > node_count * 3:
            suggestions.append("Consider reducing connections or using hierarchical layout")

        # Check for orphaned nodes
        connected_nodes = set()
        for conn in session.connections:
            connected_nodes.add(conn.from_node)
            connected_nodes.add(conn.to_node)

        orphaned = set(session.nodes.keys()) - connected_nodes
        if orphaned and len(orphaned) > node_count * 0.2:  # More than 20% orphaned
            suggestions.append(f"Many orphaned nodes ({len(orphaned)}). Consider connecting or removing them")

        # Suggest layout direction based on structure
        if connection_count > 0:
            # Count connections going "downward" vs "sideways"
            hierarchical_score = 0
            for conn in session.connections[:20]:  # Sample first 20
                from_idx = list(session.nodes.keys()).index(conn.from_node)
                to_idx = list(session.nodes.keys()).index(conn.to_node)
                if to_idx > from_idx:
                    hierarchical_score += 1

            if hierarchical_score > 15 and session.direction in ["LR", "RL"]:
                suggestions.append("Consider using TB (top-to-bottom) layout for hierarchical structure")

        return suggestions


def validate_before_render(session: DiagramSession) -> Dict[str, Any]:
    """
    Validate a diagram before rendering and return validation result.

    Returns:
        Dict with validation status and any issues/suggestions
    """
    is_valid, issues = DiagramValidator.validate_diagram(session)

    if not is_valid:
        return {
            "valid": False,
            "issues": issues,
            "status": "error",
            "error": "Diagram validation failed"
        }

    # Get optimization suggestions even if valid
    suggestions = DiagramValidator.suggest_optimizations(session)

    return {
        "valid": True,
        "issues": [],
        "suggestions": suggestions,
        "status": "success",
        "node_count": len(session.nodes),
        "connection_count": len(session.connections),
        "cluster_count": len(session.clusters)
    }