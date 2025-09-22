"""Session Manager for maintaining diagram state"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .models import DiagramSession, NodeInfo, ConnectionInfo, ClusterInfo


class SessionManager:
    """Manages diagram sessions with state persistence"""

    def __init__(self, max_sessions: int = 100, session_timeout: int = 3600):
        self.sessions: Dict[str, DiagramSession] = {}
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout
        self._diagram_instances: Dict[str, Any] = {}  # Store actual diagram objects
        self._session_last_access: Dict[str, datetime] = {}  # Track last access times

    def create_session(
        self, 
        name: str, 
        direction: str = "LR",
        output_format: str = "png", 
        **config
    ) -> str:
        """Create a new diagram session"""

        # Clean up expired sessions first
        self._cleanup_expired_sessions()

        # Check session limit
        if len(self.sessions) >= self.max_sessions:
            # Remove oldest session
            oldest_id = min(
                self.sessions.keys(),
                key=lambda k: self.sessions[k].created_at
            )
            self.delete_session(oldest_id)

        session_id = str(uuid.uuid4())

        # Extract graph_spacing from config if provided
        graph_spacing = config.pop('graph_spacing', 'normal')

        session = DiagramSession(
            session_id=uuid.UUID(session_id),
            name=name,
            direction=direction,
            output_format=output_format,
            graph_spacing=graph_spacing,
            metadata=config
        )

        self.sessions[session_id] = session
        self._session_last_access[session_id] = datetime.now()
        return session_id

    def get_session(self, session_id: str) -> Optional[DiagramSession]:
        """Retrieve a session by ID"""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]

        # Check if session has expired
        if self._is_session_expired(session):
            self.delete_session(session_id)
            return None

        # Update last accessed time
        session.updated_at = datetime.now()
        self._session_last_access[session_id] = datetime.now()
        return session

    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session properties"""
        session = self.get_session(session_id)
        if not session:
            return False

        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)

        session.updated_at = datetime.now()
        return True

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and clean up resources"""
        try:
            if session_id in self.sessions:
                del self.sessions[session_id]

                # Clean up diagram instance if exists
                if session_id in self._diagram_instances:
                    del self._diagram_instances[session_id]

                # Clean up last access tracking
                if session_id in self._session_last_access:
                    del self._session_last_access[session_id]

                return True
            return False
        except Exception:
            # Log error in production
            return False

    def list_sessions(self) -> List[DiagramSession]:
        """List all active sessions"""
        self._cleanup_expired_sessions()
        return list(self.sessions.values())

    def add_node(self, session_id: str, node: NodeInfo) -> bool:
        """Add a node to the session"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.nodes[node.id] = node
        session.updated_at = datetime.now()
        return True

    def remove_node(self, session_id: str, node_id: str) -> bool:
        """Remove a node from the session"""
        session = self.get_session(session_id)
        if not session or node_id not in session.nodes:
            return False

        # Remove the node
        del session.nodes[node_id]

        # Remove any connections involving this node
        session.connections = [
            conn for conn in session.connections
            if conn.from_node != node_id and conn.to_node != node_id
        ]

        # Remove from clusters
        for cluster in session.clusters.values():
            if node_id in cluster.nodes:
                cluster.nodes.remove(node_id)

        session.updated_at = datetime.now()
        return True

    def add_connection(self, session_id: str, connection: ConnectionInfo) -> bool:
        """Add a connection between nodes"""
        session = self.get_session(session_id)
        if not session:
            return False

        # Verify both nodes exist
        if (connection.from_node not in session.nodes or
            connection.to_node not in session.nodes):
            return False

        session.connections.append(connection)
        session.updated_at = datetime.now()
        return True

    def remove_connection(self, session_id: str, from_node: str, to_node: str) -> bool:
        """Remove a connection between nodes"""
        session = self.get_session(session_id)
        if not session:
            return False

        original_count = len(session.connections)
        session.connections = [
            conn for conn in session.connections
            if not (conn.from_node == from_node and conn.to_node == to_node)
        ]

        if len(session.connections) < original_count:
            session.updated_at = datetime.now()
            return True
        return False

    def add_cluster(self, session_id: str, cluster: ClusterInfo) -> bool:
        """Add a cluster to the session"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.clusters[cluster.id] = cluster
        session.updated_at = datetime.now()
        return True

    def store_diagram_instance(self, session_id: str, diagram_instance: Any) -> None:
        """Store the actual diagram object for rendering"""
        self._diagram_instances[session_id] = diagram_instance

    def get_diagram_instance(self, session_id: str) -> Optional[Any]:
        """Retrieve the stored diagram instance"""
        return self._diagram_instances.get(session_id)

    def _is_session_expired(self, session_or_id) -> bool:
        """Check if a session has expired"""
        # Handle both session object and session ID
        if isinstance(session_or_id, str):
            session_id = session_or_id
            if session_id not in self.sessions:
                return True
            session = self.sessions[session_id]
        else:
            session = session_or_id
            session_id = str(session.session_id)

        # Use last access time if available
        if session_id in self._session_last_access:
            last_time = self._session_last_access[session_id]
        else:
            last_time = session.updated_at

        expiry_time = last_time + timedelta(seconds=self.session_timeout)
        return datetime.now() > expiry_time

    def _cleanup_expired_sessions(self) -> None:
        """Remove all expired sessions"""
        expired_ids = [
            session_id for session_id, session in self.sessions.items()
            if self._is_session_expired(session)
        ]

        for session_id in expired_ids:
            self.delete_session(session_id)

    def _check_circular_dependency(self, session: DiagramSession, cluster_id: str, parent_id: str) -> bool:
        """Check if adding parent_id to cluster_id would create a circular dependency

        Returns True if circular dependency would be created
        """
        if parent_id == cluster_id:
            return True

        # Trace parent chain to detect cycles
        visited = {cluster_id}
        current = parent_id

        while current:
            if current in visited:
                return True
            visited.add(current)

            # Get parent of current cluster
            if current in session.clusters:
                current = session.clusters[current].parent_id
            else:
                # Parent doesn't exist yet (will be created in batch)
                break

        return False

    def create_clusters_bulk(self, session_id: str, clusters: List[Dict[str, str]]) -> Dict[str, Any]:
        """Create multiple clusters at once

        Args:
            session_id: Session ID
            clusters: List of cluster definitions with 'id', 'label', and optional 'parent_id'

        Returns:
            Dict with 'created' list and 'errors' list
        """
        session = self.get_session(session_id)
        if not session:
            return {"created": [], "errors": [{"error": "Session not found"}]}

        created = []
        errors = []

        for cluster_def in clusters:
            try:
                cluster_id = cluster_def.get('id')
                label = cluster_def.get('label', cluster_id)
                parent_id = cluster_def.get('parent_id')

                if not cluster_id:
                    errors.append({"cluster": cluster_def, "error": "Missing cluster id"})
                    continue

                if cluster_id in session.clusters:
                    errors.append({"cluster": cluster_id, "error": "Cluster already exists"})
                    continue

                # Check for circular dependency
                if parent_id and self._check_circular_dependency(session, cluster_id, parent_id):
                    errors.append({"cluster": cluster_id, "error": f"Circular dependency detected with parent '{parent_id}'"})
                    continue

                cluster = ClusterInfo(
                    id=cluster_id,
                    label=label,
                    parent_id=parent_id
                )
                session.clusters[cluster_id] = cluster
                created.append(cluster_id)

            except Exception as e:
                errors.append({"cluster": cluster_def, "error": str(e)})

        session.updated_at = datetime.now()
        return {"created": created, "errors": errors}

    def add_nodes_bulk(self, session_id: str, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add multiple nodes at once

        Args:
            session_id: Session ID
            nodes: List of node definitions with 'id', 'provider', 'service', 'label', optional 'cluster_id'

        Returns:
            Dict with 'added' list and 'errors' list
        """
        session = self.get_session(session_id)
        if not session:
            return {"added": [], "errors": [{"error": "Session not found"}]}

        added = []
        errors = []

        for node_def in nodes:
            try:
                node = NodeInfo(
                    id=node_def.get('id'),
                    provider=node_def.get('provider'),
                    service=node_def.get('service'),
                    label=node_def.get('label', node_def.get('id')),
                    cluster_id=node_def.get('cluster_id'),
                    metadata=node_def.get('metadata', {})
                )

                if node.id in session.nodes:
                    errors.append({"node": node.id, "error": "Node already exists"})
                    continue

                session.nodes[node.id] = node
                added.append(node.id)

            except Exception as e:
                errors.append({"node": node_def, "error": str(e)})

        session.updated_at = datetime.now()
        return {"added": added, "errors": errors}

    def connect_nodes_bulk(self, session_id: str, connections: List[Dict[str, str]]) -> Dict[str, Any]:
        """Create multiple connections at once

        Args:
            session_id: Session ID
            connections: List of connection definitions with 'from', 'to', optional 'label', 'style', 'color'

        Returns:
            Dict with 'connected' count and 'errors' list
        """
        session = self.get_session(session_id)
        if not session:
            return {"connected": 0, "errors": [{"error": "Session not found"}]}

        connected = 0
        errors = []

        for conn_def in connections:
            try:
                from_node = conn_def.get('from')
                to_node = conn_def.get('to')

                if not from_node or not to_node:
                    errors.append({"connection": conn_def, "error": "Missing from or to node"})
                    continue

                if from_node not in session.nodes:
                    errors.append({"connection": conn_def, "error": f"From node '{from_node}' not found"})
                    continue

                if to_node not in session.nodes:
                    errors.append({"connection": conn_def, "error": f"To node '{to_node}' not found"})
                    continue

                connection = ConnectionInfo(
                    from_node=from_node,
                    to_node=to_node,
                    label=conn_def.get('label', ''),
                    style=conn_def.get('style', 'solid'),
                    color=conn_def.get('color', '#7B8894')
                )

                session.connections.append(connection)
                connected += 1

            except Exception as e:
                errors.append({"connection": conn_def, "error": str(e)})

        session.updated_at = datetime.now()
        return {"connected": connected, "errors": errors}

    def edit_node(self, session_id: str, node_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Edit a node's properties

        Args:
            session_id: Session ID
            node_id: ID of node to edit
            updates: Dictionary of properties to update (provider, service, label, cluster_id, attributes)

        Returns:
            Dict with 'success' bool and 'node' or 'error'
        """
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}

        if node_id not in session.nodes:
            return {"success": False, "error": f"Node not found: {node_id}"}

        node = session.nodes[node_id]

        # Update allowed properties
        if 'provider' in updates:
            node.provider = updates['provider']
        if 'service' in updates:
            node.service = updates['service']
        if 'label' in updates:
            node.label = updates['label']
        if 'cluster_id' in updates:
            # Handle cluster assignment changes
            old_cluster_id = node.cluster_id
            new_cluster_id = updates['cluster_id']

            # Remove from old cluster
            if old_cluster_id and old_cluster_id in session.clusters:
                if node_id in session.clusters[old_cluster_id].nodes:
                    session.clusters[old_cluster_id].nodes.remove(node_id)

            # Add to new cluster
            if new_cluster_id and new_cluster_id in session.clusters:
                if node_id not in session.clusters[new_cluster_id].nodes:
                    session.clusters[new_cluster_id].nodes.append(node_id)

            node.cluster_id = new_cluster_id

        if 'attributes' in updates:
            if updates['attributes'] is None:
                node.attributes = {}
            else:
                node.attributes.update(updates['attributes'])

        session.updated_at = datetime.now()
        return {"success": True, "node": node}

    def edit_nodes_bulk(self, session_id: str, edits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Edit multiple nodes at once

        Args:
            session_id: Session ID
            edits: List of edit specifications with 'id' and update fields

        Returns:
            Dict with 'edited' list and 'errors' list
        """
        session = self.get_session(session_id)
        if not session:
            return {"edited": [], "errors": [{"error": "Session not found"}]}

        edited = []
        errors = []

        for edit_spec in edits:
            try:
                node_id = edit_spec.get('id')
                if not node_id:
                    errors.append({"error": "Missing node id", "spec": edit_spec})
                    continue

                result = self.edit_node(session_id, node_id, edit_spec)
                if result['success']:
                    edited.append(node_id)
                else:
                    errors.append({"node": node_id, "error": result.get('error')})

            except Exception as e:
                errors.append({"node": edit_spec.get('id', 'unknown'), "error": str(e)})

        return {"edited": edited, "errors": errors}

    def edit_cluster(self, session_id: str, cluster_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Edit a cluster's properties

        Args:
            session_id: Session ID
            cluster_id: ID of cluster to edit
            updates: Dictionary of properties to update (label, parent_cluster_id)

        Returns:
            Dict with 'success' bool and 'cluster' or 'error'
        """
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}

        if cluster_id not in session.clusters:
            return {"success": False, "error": f"Cluster not found: {cluster_id}"}

        cluster = session.clusters[cluster_id]

        # Update allowed properties
        if 'label' in updates:
            cluster.label = updates['label']
        if 'parent_cluster_id' in updates:
            # Circular dependency validation is handled in create_clusters_bulk
            cluster.parent_cluster_id = updates['parent_cluster_id']

        session.updated_at = datetime.now()
        return {"success": True, "cluster": cluster}

    def edit_clusters_bulk(self, session_id: str, edits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Edit multiple clusters at once

        Args:
            session_id: Session ID
            edits: List of edit specifications with 'id' and update fields

        Returns:
            Dict with 'edited' list and 'errors' list
        """
        session = self.get_session(session_id)
        if not session:
            return {"edited": [], "errors": [{"error": "Session not found"}]}

        edited = []
        errors = []

        for edit_spec in edits:
            try:
                cluster_id = edit_spec.get('id')
                if not cluster_id:
                    errors.append({"error": "Missing cluster id", "spec": edit_spec})
                    continue

                result = self.edit_cluster(session_id, cluster_id, edit_spec)
                if result['success']:
                    edited.append(cluster_id)
                else:
                    errors.append({"cluster": cluster_id, "error": result.get('error')})

            except Exception as e:
                errors.append({"cluster": edit_spec.get('id', 'unknown'), "error": str(e)})

        return {"edited": edited, "errors": errors}

    def edit_connection(self, session_id: str, conn_index: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Edit a connection's properties

        Args:
            session_id: Session ID
            conn_index: Index of connection in connections list
            updates: Dictionary of properties to update (label, color, style)

        Returns:
            Dict with 'success' bool and 'connection' or 'error'
        """
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}

        if conn_index < 0 or conn_index >= len(session.connections):
            return {"success": False, "error": f"Connection index out of range: {conn_index}"}

        connection = session.connections[conn_index]

        # Update allowed properties
        if 'label' in updates:
            connection.label = updates['label']
        if 'color' in updates:
            connection.color = updates['color']
        if 'style' in updates:
            connection.style = updates['style']

        session.updated_at = datetime.now()
        return {"success": True, "connection": connection, "index": conn_index}

    def find_connection(self, session_id: str, from_node: str, to_node: str) -> Optional[int]:
        """Find connection index by node IDs

        Args:
            session_id: Session ID
            from_node: Source node ID
            to_node: Target node ID

        Returns:
            Connection index or None if not found
        """
        session = self.get_session(session_id)
        if not session:
            return None

        for i, conn in enumerate(session.connections):
            if conn.from_node == from_node and conn.to_node == to_node:
                return i
        return None
