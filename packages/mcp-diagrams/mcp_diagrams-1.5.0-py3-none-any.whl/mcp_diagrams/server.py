"""MCP Diagrams Server - Main server implementation"""

import os
import uuid
import signal
import threading
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from functools import wraps
from collections import defaultdict, deque
import time
import threading

from fastmcp import FastMCP

# Set up logger
logger = logging.getLogger("mcp_diagrams")

from .session_manager import SessionManager
from .diagram_builder import DiagramBuilder
from .provider_registry import ProviderRegistry
from .icon_validator import IconValidator
from .models import NodeInfo, ConnectionInfo, ClusterInfo
from .utils import (
    get_safe_output_path,
    validate_session_id,
    validate_direction,
    validate_output_format
)


# Initialize FastMCP server
mcp = FastMCP(
    name="mcp-diagrams",
    version="1.0.0"
)

# Initialize managers
session_manager = SessionManager()
diagram_builder = DiagramBuilder()
provider_registry = ProviderRegistry()
icon_validator = IconValidator(provider_registry)

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_CALLS = 10  # max calls per window per session
rate_limit_tracker = defaultdict(lambda: deque(maxlen=RATE_LIMIT_MAX_CALLS))
rate_limit_lock = threading.Lock()


def check_rate_limit(session_id: str, operation: str = "render") -> tuple[bool, str]:
    """Check if operation is within rate limits (thread-safe)"""
    with rate_limit_lock:
        current_time = time.time()
        key = f"{session_id}:{operation}"
        timestamps = rate_limit_tracker[key]

        # Remove old timestamps outside the window
        while timestamps and timestamps[0] < current_time - RATE_LIMIT_WINDOW:
            timestamps.popleft()

        # Check if we're at the limit
        if len(timestamps) >= RATE_LIMIT_MAX_CALLS:
            wait_time = int(RATE_LIMIT_WINDOW - (current_time - timestamps[0]))
            return False, f"Rate limit exceeded. Please wait {wait_time} seconds before trying again."

        # Add current timestamp
        timestamps.append(current_time)
        return True, ""


# Load environment variables
load_dotenv()

# Configure output directory - can be set via environment variable
# This is useful for Claude Desktop integration where you want to specify
# a specific folder for saving diagrams
default_output_dir = os.getenv("MCP_DIAGRAMS_OUTPUT_DIR", "./diagrams_output")
OUTPUT_DIR = Path(default_output_dir).expanduser().resolve()
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


@mcp.tool()
def create_diagram(
    name: str,
    direction: str = "LR",
    output_format: str = "png",
    show: bool = False,
    filename: Optional[str] = None,
    graph_spacing: Optional[str] = "normal"
) -> Dict[str, Any]:
    """
    Initialize a new diagram session to start building an infrastructure/architecture diagram.

    IMPORTANT: This is ALWAYS the FIRST tool to call when creating any diagram. It creates
    a stateful session that persists across multiple tool calls. The returned session_id
    must be used for all subsequent operations (adding nodes, connections, rendering).

    What are infrastructure diagrams?
    Infrastructure diagrams are visual representations of system architectures, showing:
    - Cloud resources (servers, databases, storage)
    - Network connections and data flow
    - Service relationships and dependencies
    - Logical groupings (clusters, tiers, regions)

    Args:
        name: Display name for the diagram (e.g., "AWS Infrastructure", "Microservices Architecture")
            This appears as the diagram title. Keep it concise but descriptive.

        direction: Graph layout direction - determines how nodes are arranged:
            - "LR": Left to Right (default) - Best for:
                * Data pipelines (input → processing → output)
                * Request flows (user → frontend → backend → database)
                * Sequential processes
            - "RL": Right to Left - Best for:
                * RTL languages or reverse flows
            - "TB": Top to Bottom - Best for:
                * Hierarchical architectures (UI → Logic → Data layers)
                * Organization charts
                * Network layers (Internet → DMZ → Internal)
            - "BT": Bottom to Top - Best for:
                * Stack representations (Hardware → OS → Application)

        output_format: Desired output format:
            - "png": Raster image (default) - Best for presentations, documents
            - "svg": Scalable vector graphics - Best for web, infinite zoom
            - "pdf": Portable document format - Best for printing, archival
            - "dot": GraphViz DOT format - Best for further processing

        show: Whether to auto-display after rendering (default: False)
            Set to False for headless/server environments

        filename: Optional custom filename (without extension)
            If not provided, generates timestamp-based name

        graph_spacing: Spacing preset for the diagram (default: "normal")
            - "compact": Minimal spacing, good for small diagrams
            - "normal": Balanced spacing for most diagrams
            - "spacious": Extra spacing for complex diagrams with many nodes
            - "extra-spacious": Maximum spacing for very complex architectures

            TIP: If your diagram looks cluttered, try "spacious" or "extra-spacious"

    Returns:
        Dictionary with session_id and status:
        - session_id: UUID to use for ALL subsequent operations (SAVE THIS!)
        - status: "success" or "error"
        - message: Human-readable status message
        - name: The diagram name
        - direction: The chosen layout direction
        - format: The chosen output format

    Example Usage Flow:
        1. Create diagram: create_diagram("My System", direction="TB")
        2. Add nodes: add_node(session_id, "web", "aws", "ec2")
        3. Connect: connect_nodes(session_id, "web", "db")
        4. Render: render_diagram(session_id)

    Example:
        >>> create_diagram(
        ...     name="E-commerce Platform",
        ...     direction="TB",
        ...     output_format="svg"
        ... )
        {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "success",
            "message": "Created diagram session: E-commerce Platform",
            "name": "E-commerce Platform",
            "direction": "TB",
            "format": "svg"
        }

    Common Patterns by Diagram Type:
        - Web Application: direction="LR" (user → app → database)
        - Microservices: direction="TB" (gateway → services → data)
        - Network Architecture: direction="TB" (internet → firewall → internal)
        - Data Pipeline: direction="LR" (source → transform → sink)

    Spacing Guidelines (IMPORTANT for complex diagrams):
        - If diagram looks cluttered → Use graph_spacing="spacious" or "extra-spacious"
        - < 10 nodes: "compact" or "normal"
        - 10-30 nodes: "normal" (default)
        - 30-50 nodes: "spacious"
        - 50+ nodes: "extra-spacious"
    """
    try:
        # Validate parameters
        if not validate_direction(direction):
            return {
                "error": f"Invalid direction: {direction}. Must be one of: LR, RL, TB, BT",
                "status": "error"
            }

        if not validate_output_format(output_format):
            return {
                "error": f"Invalid format: {output_format}. Must be one of: png, svg, pdf, dot",
                "status": "error"
            }

        # Validate name length and content
        if not name or len(name.strip()) == 0:
            return {
                "error": "Diagram name cannot be empty",
                "status": "error"
            }

        if len(name) > 100:
            return {
                "error": "Diagram name too long (max 100 characters)",
                "status": "error"
            }

        # Validate spacing parameter
        valid_spacings = ["compact", "normal", "spacious", "extra-spacious"]
        if graph_spacing not in valid_spacings:
            graph_spacing = "normal"

        session_id = session_manager.create_session(
            name=name.strip(),
            direction=direction,
            output_format=output_format.lower(),
            show=show,
            filename=filename,
            graph_spacing=graph_spacing
        )

        return {
            "session_id": session_id,
            "status": "success",
            "message": f"Created diagram session: {name}"
        }

    except Exception as e:
        return {
            "error": f"Failed to create diagram: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def add_node(
    session_id: str,
    node_id: str,
    provider: str,
    service: str,
    label: Optional[str] = None,
    cluster_id: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Add a single cloud service node to the diagram.

    Note: For adding multiple nodes, use add_nodes_bulk() for better performance.
    This tool is for adding individual nodes only.

    Workflow Position:
        1. create_diagram()     ← Initialize session
        2. create_clusters()    ← Optional grouping
        3. add_node()          ← YOU ARE HERE (use add_nodes_bulk for multiple)
        4. connect_nodes()     ← Define relationships
        5. render_diagram()    ← Generate output

    Nodes represent infrastructure components like servers, databases, or services.
    Each node must have a unique ID within the session.

    Args:
        session_id: UUID from create_diagram response
        node_id: Unique identifier for this node (e.g., "web-server", "db-primary")
            Use descriptive IDs that explain the node's purpose
        provider: Technology provider/platform (20 available, ~2000 total services)

            COMPLETE PROVIDER LIST WITH SERVICE COUNTS:
            - "aws" (550 services): Amazon Web Services
              Categories: compute, storage, database, network, analytics, ml, iot, security
              Common: ec2, s3, lambda, rds, dynamodb, ecs, eks, elb, iam
            - "azure" (232 services): Microsoft Azure
              Categories: compute, storage, databases, web, ai, analytics
              Common: vm, storage, sqldatabase, functions, appservice, cosmosdb
            - "gcp" (109 services): Google Cloud Platform
              Categories: compute, storage, databases, analytics, ml
              Common: gce, gcs, cloudsql, bigquery, pubsub, gke
            - "alibabacloud" (131 services): Alibaba Cloud
              Common: ecs, rds, oss, slb, vpc, cdn, waf
            - "oci" (152 services): Oracle Cloud Infrastructure
            - "ibm" (180 services): IBM Cloud
              Common: vm, containers, watson, cloudant, db2
            - "k8s" (69 services): Kubernetes
              Common: pod, deployment, service, ingress, configmap, secret
            - "onprem" (206 services): On-premises/Traditional Infrastructure
              Common: nginx, postgresql, mysql, redis, kafka, jenkins, gitlab
            - "digitalocean" (25 services): Digital Ocean
              Common: droplet, spaces, database, kubernetes, loadbalancer
            - "elastic" (47 services): Elastic Stack
              Common: elasticsearch, kibana, logstash, beats, apm
            - "firebase" (23 services): Google Firebase
              Common: auth, firestore, storage, functions, hosting
            - "openstack" (54 services): OpenStack
              Common: nova, neutron, swift, cinder, keystone
            - "programming" (81 services): Languages & Frameworks
              Common: python, javascript, java, react, django, nodejs
            - "saas" (37 services): Software as a Service
              Common: datadog, github, gitlab, slack, jira, splunk
            - "generic" (26 services): Generic Shapes
              Common: blank, device, database, client, user, firewall
            - "gis" (64 services): Geographic Information Systems
            - "outscale" (12 services): Outscale Cloud
            - "c4": C4 Model Diagrams
            - "custom": Custom User Icons
            - "base": Base Classes (internal)

            Use discovery tools for complete lists:
            - list_providers() - See all providers
            - list_categories(provider) - See provider categories
            - list_services(provider, category) - See specific services
            - search_services("database") - Search by keyword

        service: Specific service within provider (usually lowercase)

            SERVICE EXAMPLES BY PROVIDER (2000 total available!):

            AWS (550 services across 26 categories):
            - Compute: ec2, lambda, ecs, eks, fargate, batch, lightsail
            - Storage: s3, efs, ebs, glacier, backup, storagegateway
            - Database: rds, dynamodb, aurora, elasticache, neptune, documentdb
            - Network: elb, alb, nlb, route53, cloudfront, apigateway, vpc
            - Analytics: kinesis, athena, emr, glue, quicksight, redshift
            - ML: sagemaker, rekognition, comprehend, polly, translate
            - IoT: iotcore, iotgreengrass, iotanalytics (63 IoT services!)
            - Security: iam, secretsmanager, waf, shield, guardduty, kms

            Azure (232 services):
            - Compute: vm, functions, containerinstances, aks, appservice
            - Storage: storageaccounts, blobstorage, files, disks
            - Database: sqldatabase, cosmosdb, postgresql, mysql, redis
            - AI/ML: cognitiveservices, machinelearning, botservices

            GCP (109 services):
            - Compute: gce, gke, run, functions, appengine
            - Storage: gcs, filestore, persistentdisk
            - Database: cloudsql, bigtable, firestore, spanner, memorystore
            - Data: bigquery, pubsub, dataflow, dataproc

            Kubernetes (69 services):
            - Workloads: pod, deployment, statefulset, daemonset, job, cronjob
            - Network: service, ingress, networkpolicy
            - Storage: persistentvolume, persistentvolumeclaim
            - Config: configmap, secret, serviceaccount

            OnPrem (206 services!):
            - Web: nginx, apache, tomcat, iis, haproxy
            - Database: postgresql, mysql, mongodb, redis, cassandra, oracle
            - Queue: rabbitmq, activemq, kafka, zeromq
            - CI/CD: jenkins, gitlab, teamcity, bamboo, ansible
            - Monitoring: prometheus, grafana, nagios, zabbix

            Programming (81 services):
            - Languages: python, javascript, java, go, rust, cpp, csharp
            - Frameworks: react, angular, vue, django, flask, spring
            - Runtime: nodejs, dotnet, ruby, php

            SaaS (37 services):
            - datadog, newrelic, splunk, github, gitlab, slack, jira

            NOTE: Service names are usually lowercase. The provider_registry
            will attempt to match variations (ec2, EC2, Ec2 all work).
        label: Optional display text (defaults to node_id if not provided)
            Use concise labels like "Web Server", "User DB", "API Gateway"
        cluster_id: Optional cluster ID to group this node visually
            Must be created first with create_cluster

            CLUSTER PLACEMENT GUIDELINES:
            - Always specify cluster_id for proper architecture boundaries
            - Place nodes in logical groups (frontend, backend, data, etc.)
            - Nodes without cluster_id appear outside all clusters (use sparingly)
            - Related services should be in the same cluster
            - External services can be outside clusters

            COMMON CLUSTER ASSIGNMENTS:
            - Load balancers → "frontend" or "dmz" cluster
            - Web servers → "application" or "web" cluster
            - API servers → "application" or "api" cluster
            - Databases → "data" or "database" cluster
            - Caches → "data" or "cache" cluster
            - Message queues → "messaging" or "integration" cluster
            - Monitoring tools → "monitoring" or "observability" cluster

        attributes: Optional metadata dictionary for advanced customization

    Returns:
        Dictionary with node creation status:
        - status: "success" or "error"
        - message: Confirmation or error details
        - node_id: The ID of created node

    Example:
        >>> add_node(
        ...     session_id="550e8400-e29b-41d4-a716-446655440000",
        ...     node_id="web-api",
        ...     provider="aws",
        ...     service="ecs",
        ...     label="API Service"
        ... )
        {
            "status": "success",
            "message": "Node added successfully",
            "node_id": "web-api"
        }

    Common Patterns:
        - Web tier: provider="aws", service="ec2" or "ecs"
        - Database: provider="aws", service="rds" or "dynamodb"
        - Storage: provider="aws", service="s3"
        - Serverless: provider="aws", service="lambda"
        - Container: provider="k8s", service="pod" or "deployment"

    Performance Note:
        - Adding 10 nodes individually: ~2 seconds
        - Adding 10 nodes with add_nodes_bulk: ~0.2 seconds (10x faster)

    When to Use This Tool:
        - Adding a single node to existing diagram
        - Quick prototyping with 1-2 nodes
        - Testing specific node configurations

    When NOT to Use This Tool:
        - Adding 3+ nodes → Use add_nodes_bulk() instead
        - Building complete architectures → Use add_nodes_bulk()
        - Performance-critical operations → Use add_nodes_bulk()
    """
    try:
        # Validate session ID
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        session = session_manager.get_session(session_id)
        if not session:
            return {
                "error": f"Session not found: {session_id}",
                "status": "error"
            }

        # Validate inputs
        if not node_id or len(node_id.strip()) == 0:
            return {
                "error": "Node ID cannot be empty",
                "status": "error"
            }

        if len(node_id) > 50:
            return {
                "error": "Node ID too long (max 50 characters)",
                "status": "error"
            }

        node_id = node_id.strip()

        # Validate attributes - handle empty string "{}" case
        if attributes is not None:
            if isinstance(attributes, str):
                # Handle case where empty object is passed as string
                if attributes == "{}" or attributes.strip() == "{}":
                    attributes = None
                else:
                    return {
                        "error": "attributes must be a dictionary, not a string",
                        "status": "error"
                    }
            elif not isinstance(attributes, dict):
                return {
                    "error": "attributes must be a dictionary",
                    "status": "error"
                }
            else:
                # Validate attribute keys to prevent pollution
                reserved_keys = {"id", "provider", "service", "label", "cluster_id"}
                invalid_keys = set(attributes.keys()) & reserved_keys
                if invalid_keys:
                    return {
                        "error": f"Attributes cannot use reserved keys: {', '.join(invalid_keys)}",
                        "status": "error"
                    }
                # Limit attribute size to prevent abuse
                if len(str(attributes)) > 1000:
                    return {
                        "error": "Attributes too large (max 1000 characters when serialized)",
                        "status": "error"
                    }

        # Check if node ID already exists
        if node_id in session.nodes:
            return {
                "error": f"Node already exists: {node_id}",
                "status": "error"
            }

        # Prepare node with defaults
        clean_provider = provider.strip() if provider else "generic"
        clean_service = service.strip() if service else "blank"
        clean_label = label.strip() if label else None

        # Validate icon exists or suggest alternatives
        is_valid, error_msg = icon_validator.validate_icon(clean_provider, clean_service)

        if not is_valid:
            # Get fallback suggestions
            suggestions = icon_validator.suggest_fallback_icons(
                clean_provider,
                clean_service,
                clean_label,
                limit=3
            )

            # Use the first suggestion as fallback
            if suggestions:
                fallback = suggestions[0]
                clean_provider = fallback["provider"]
                clean_service = fallback["service"]

                # Include a warning in the response
                warning_msg = (
                    f"Icon '{provider}.{service}' not found. "
                    f"Using fallback: '{clean_provider}.{clean_service}' ({fallback['reason']})"
                )
            else:
                # Should never happen as validator always provides generic fallback
                clean_provider = "generic"
                clean_service = "blank"
                warning_msg = f"Icon '{provider}.{service}' not found. Using generic placeholder."

        node = NodeInfo(
            id=node_id,
            provider=clean_provider,
            service=clean_service,
            label=clean_label,
            cluster_id=cluster_id.strip() if cluster_id else None,
            attributes=attributes if attributes is not None else {}
        )

        if session_manager.add_node(session_id, node):
            response = {
                "node_id": node_id,
                "status": "success",
                "message": f"Added node: {node_id}",
                "provider": clean_provider,
                "service": clean_service
            }
            # Add warning if fallback was used
            if not is_valid:
                response["warning"] = warning_msg
                response["suggestions"] = suggestions[:3] if 'suggestions' in locals() else []
            return response
        else:
            return {
                "error": "Failed to add node",
                "status": "error"
            }

    except Exception as e:
        return {
            "error": f"Failed to add node: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def connect_nodes(
    session_id: str,
    from_node: str,
    to_node: str,
    label: Optional[str] = None,
    color: Optional[str] = None,
    style: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a single connection between two nodes.

    Note: For connecting multiple nodes, use connect_nodes_bulk() for better performance.
    This tool is for individual connections only.

    Workflow Position:
        1. create_diagram()      ← Initialize session
        2. create_clusters()     ← Optional grouping
        3. add_nodes()          ← Add nodes
        4. connect_nodes()      ← YOU ARE HERE (use connect_nodes_bulk for multiple)
        5. render_diagram()     ← Generate output

    Connections represent relationships like data flow, API calls, or dependencies.
    The visual direction follows the diagram's layout direction.

    Args:
        session_id: UUID from create_diagram response
        from_node: Source node ID (must exist in diagram)
        to_node: Target node ID (must exist in diagram)
        label: Optional text to display on the connection
            Examples: "HTTPS", "API Call", "Reads/Writes", "Sync", "5432/tcp"
        color: Optional connection line color
            Examples: "red", "blue", "green", "orange", "gray", "#FF5733"
        style: Optional line style:
            - "solid": Default solid line
            - "dashed": Dashed line (good for optional/backup connections)
            - "dotted": Dotted line (good for planned/future connections)
            - "bold": Thicker solid line (good for main data flows)

    Returns:
        Dictionary with connection status:
        - status: "success" or "error"
        - message: Confirmation or error details
        - connection: Created connection information

    Example:
        >>> connect_nodes(
        ...     session_id="550e8400-e29b-41d4-a716-446655440000",
        ...     from_node="load-balancer",
        ...     to_node="web-server",
        ...     label="HTTPS",
        ...     color="green"
        ... )
        {
            "status": "success",
            "message": "Connection created successfully",
            "connection": {
                "from": "load-balancer",
                "to": "web-server",
                "label": "HTTPS"
            }
        }

    Common Connection Patterns:
        - User → Load Balancer: label="HTTPS"
        - Load Balancer → Web Server: label="HTTP"
        - Web Server → Database: label="SQL", "MongoDB"
        - Web Server → Cache: label="Redis", "Memcached"
        - Service → Queue: label="Publish", "SQS"
        - Queue → Service: label="Subscribe", "Process"
        - Service → Storage: label="Read/Write", "S3 API"

    Tips:
        - Use consistent labeling (e.g., always "HTTPS" not "https")
        - Use color to differentiate traffic types (green=success, red=error)
        - Use style to show importance (bold=primary, dashed=backup)

    Performance Comparison:
        - Connecting 10 node pairs individually: ~1.5 seconds
        - Connecting 10 pairs with connect_nodes_bulk: ~0.15 seconds (10x faster)

    When to Use This Tool:
        - Adding a single connection to existing diagram
        - Testing connection appearance
        - Quick prototyping with 1-2 connections

    When NOT to Use This Tool:
        - Connecting 3+ node pairs → Use connect_nodes_bulk()
        - Building complete architectures → Use connect_nodes_bulk()
        - Performance matters → Use connect_nodes_bulk()

    Complete Example Workflow:
        # Step 1: Create diagram
        session = create_diagram("Simple App", direction="LR")
        session_id = session["session_id"]

        # Step 2: Add nodes (prefer bulk for 3+)
        add_node(session_id, "user", "generic", "user", "User")
        add_node(session_id, "app", "aws", "ec2", "App Server")
        add_node(session_id, "db", "aws", "rds", "Database")

        # Step 3: Connect nodes (THIS TOOL)
        connect_nodes(session_id, "user", "app", "HTTPS")
        connect_nodes(session_id, "app", "db", "SQL")

        # Step 4: Render
        render_diagram(session_id)
    """
    try:
        # Validate session ID
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        session = session_manager.get_session(session_id)
        if not session:
            return {
                "error": f"Session not found: {session_id}",
                "status": "error"
            }

        # Validate node IDs
        if not from_node or not to_node:
            return {
                "error": "Both from_node and to_node must be specified",
                "status": "error"
            }

        from_node = from_node.strip()
        to_node = to_node.strip()

        # Check if nodes exist
        if from_node not in session.nodes:
            return {
                "error": f"Source node not found: {from_node}",
                "status": "error"
            }

        if to_node not in session.nodes:
            return {
                "error": f"Target node not found: {to_node}",
                "status": "error"
            }

        connection = ConnectionInfo(
            from_node=from_node,
            to_node=to_node,
            label=label.strip() if label else None,
            color=color.strip() if color else None,
            style=style.strip() if style else None
        )

        if session_manager.add_connection(session_id, connection):
            return {
                "from_node": from_node,
                "to_node": to_node,
                "status": "success",
                "message": f"Connected {from_node} -> {to_node}"
            }
        else:
            return {
                "error": "Failed to connect nodes",
                "status": "error"
            }

    except Exception as e:
        return {
            "error": f"Failed to connect nodes: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def list_sessions() -> Dict[str, Any]:
    """
    List all active diagram sessions currently in memory.

    USE THIS TOOL WHEN: You need to:
    - See what diagrams are currently being worked on
    - Find a session_id you forgot to save
    - Check the status of multiple diagrams
    - Clean up old sessions

    Sessions are automatically cleaned up after their TTL expires (default 1 hour).

    Returns:
        Dictionary containing:
        - sessions: List of active sessions with their details
        - count: Total number of active sessions
        - status: "success" or "error"

    Session Details Include:
        - session_id: The UUID to use for operations
        - name: The diagram name
        - created_at: When the session was created
        - node_count: Number of nodes in the diagram
        - connection_count: Number of connections

    Example Response:
        {
            "sessions": [
                {
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Production Architecture",
                    "created_at": "2024-01-10T10:30:00",
                    "node_count": 15,
                    "connection_count": 22
                },
                {
                    "session_id": "660e9500-f39c-51e5-b827-557766551111",
                    "name": "Microservices Design",
                    "created_at": "2024-01-10T11:00:00",
                    "node_count": 8,
                    "connection_count": 12
                }
            ],
            "count": 2,
            "status": "success"
        }

    Tips:
        - Sessions persist in memory only (not saved to disk)
        - Save important session_ids immediately after creation
        - Use get_session_state() for full details of a session
        - Maximum 100 concurrent sessions (older ones auto-delete)
    """
    try:
        sessions_list = []
        for session_id, session in session_manager._sessions.items():
            sessions_list.append({
                "session_id": str(session_id),
                "name": session.name,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "node_count": len(session.nodes),
                "connection_count": len(session.connections),
                "cluster_count": len(session.clusters),
                "direction": session.direction,
                "output_format": session.output_format
            })

        return {
            "sessions": sessions_list,
            "count": len(sessions_list),
            "status": "success"
        }
    except Exception as e:
        return {
            "error": f"Failed to list sessions: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def get_session_state(session_id: str) -> Dict[str, Any]:
    """
    Get the complete state of a diagram session.

    Args:
        session_id: UUID of the diagram session

    Returns:
        Complete session state including nodes, connections, and clusters

    Example Response:
        {
            "session_id": "uuid-here",
            "name": "My Architecture",
            "nodes": {"web": {...}, "db": {...}},
            "connections": [{"from_node": "web", "to_node": "db"}],
            "clusters": {},
            "metadata": {},
            "status": "success"
        }
    """
    try:
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        session = session_manager.get_session(session_id)
        if not session:
            return {
                "error": f"Session not found: {session_id}",
                "status": "error"
            }

        # Convert session to dict, handling datetime serialization
        session_dict = session.model_dump()

        # Convert datetime objects to ISO format strings
        for node in session_dict["nodes"].values():
            if "created_at" in node:
                node["created_at"] = node["created_at"].isoformat()

        session_dict["created_at"] = session_dict["created_at"].isoformat()
        session_dict["updated_at"] = session_dict["updated_at"].isoformat()
        session_dict["session_id"] = str(session_dict["session_id"])

        return {
            **session_dict,
            "status": "success"
        }
    except Exception as e:
        return {
            "error": f"Failed to get session state: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def create_clusters_bulk(
    session_id: str,
    clusters: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Create multiple clusters at once for organizing complex diagrams.

    Clusters help organize nodes into logical groups. Create clusters before adding
    nodes when dealing with 10+ nodes or complex architectures for better organization.

    Workflow Order (CRITICAL):
        1. create_diagram()      ← Initialize session
        2. create_clusters_bulk() ← Create logical groups (YOU ARE HERE)
        3. add_nodes_bulk()      ← Add nodes to clusters
        4. connect_nodes_bulk()  ← Connect nodes
        5. render_diagram()      ← Generate output

    Performance: 8-10x faster than individual create_cluster() calls.

    Common Architecture Patterns:

    1. Three-Tier Web Application (Most Common):
        clusters = [
            {"id": "frontend", "label": "Frontend Tier"},
            {"id": "backend", "label": "Application Tier"},
            {"id": "data", "label": "Data Tier"}
        ]

    2. Microservices Architecture:
        clusters = [
            {"id": "gateway", "label": "API Gateway"},
            {"id": "services", "label": "Microservices"},
            {"id": "data", "label": "Data Layer"},
            {"id": "messaging", "label": "Message Queue"}
        ]

    3. Kubernetes Deployment:
        clusters = [
            {"id": "k8s-cluster", "label": "Kubernetes Cluster"},
            {"id": "ingress", "label": "Ingress", "parent_id": "k8s-cluster"},
            {"id": "apps", "label": "Applications", "parent_id": "k8s-cluster"},
            {"id": "storage", "label": "Storage", "parent_id": "k8s-cluster"}
        ]

    4. AWS Multi-Region:
        clusters = [
            {"id": "us-east-1", "label": "US East (N. Virginia)"},
            {"id": "us-west-2", "label": "US West (Oregon)"},
            {"id": "eu-west-1", "label": "EU (Ireland)"},
            {"id": "global", "label": "Global Services"}
        ]

    5. DevOps Pipeline:
        clusters = [
            {"id": "dev", "label": "Development"},
            {"id": "staging", "label": "Staging"},
            {"id": "prod", "label": "Production"},
            {"id": "ci-cd", "label": "CI/CD Pipeline"}
        ]

    When to Use Clusters:
        - 10+ nodes: Organize into logical groups
        - Multi-tier apps: Separate presentation, logic, data
        - Microservices: Group by service or domain
        - Cloud resources: Group by region, VPC, or service type
        - Security zones: DMZ, public, private, restricted

    Args:
        session_id: UUID of the diagram session (from create_diagram)
        clusters: List of cluster definitions, each containing:
            - id: Unique identifier for the cluster (required)
            - label: Display label for the cluster (required)
            - parent_id: ID of parent cluster for nesting (optional)

    Nesting Example (Hierarchical Clusters):
        clusters = [
            {"id": "cloud", "label": "AWS Cloud"},
            {"id": "vpc", "label": "VPC", "parent_id": "cloud"},
            {"id": "public", "label": "Public Subnet", "parent_id": "vpc"},
            {"id": "private", "label": "Private Subnet", "parent_id": "vpc"}
        ]

    Returns:
        Dict with:
            - created: List of successfully created cluster IDs
            - created_count: Number of clusters created
            - errors: List of any errors encountered
            - status: "success" or "error"

    Pro Tips:
        - Create all clusters before adding any nodes
        - Use consistent naming: "tier-frontend", "tier-backend", etc.
        - Keep cluster labels concise but descriptive
        - Nest clusters for complex hierarchies (max 3 levels recommended)
    """
    try:
        result = session_manager.create_clusters_bulk(session_id, clusters)

        return {
            "session_id": session_id,
            "created": result["created"],
            "created_count": len(result["created"]),
            "errors": result["errors"],
            "status": "success" if len(result["created"]) > 0 else "error"
        }
    except Exception as e:
        logger.error(f"Failed to create clusters in bulk: {str(e)}")
        return {
            "error": f"Failed to create clusters: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def add_nodes_bulk(
    session_id: str,
    nodes: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Add multiple nodes at once for optimal performance (8-10x faster than individual calls).

    This bulk operation is 8-10x faster than multiple add_node() calls.
    Can add up to 100 nodes in a single operation.

    Performance Comparison:
        SLOW approach (avoid):
            for node in nodes:
                add_node(session_id, node['id'], node['provider'], node['service'])

        FAST approach (recommended - 8-10x faster):
            add_nodes_bulk(session_id, nodes)

    Args:
        session_id: UUID of the diagram session (from create_diagram)
        nodes: List of node definitions, each containing:
            - id: Unique identifier for the node (required)
            - provider: Provider name (required) - e.g., "aws", "azure", "gcp", "k8s"
            - service: Service name (required) - e.g., "EC2", "RDS", "Lambda"
            - label: Display label for the node (optional, defaults to service name)
            - cluster_id: ID of cluster to place node in (optional)
            - metadata: Additional metadata (optional)

    Common Architecture Patterns:

    1. Three-Tier Web Application:
        nodes = [
            # Frontend tier
            {"id": "cdn", "provider": "aws", "service": "CloudFront", "label": "CDN"},
            {"id": "lb", "provider": "aws", "service": "ALB", "label": "Load Balancer"},
            # Application tier
            {"id": "web1", "provider": "aws", "service": "EC2", "label": "Web Server 1"},
            {"id": "web2", "provider": "aws", "service": "EC2", "label": "Web Server 2"},
            # Data tier
            {"id": "db", "provider": "aws", "service": "RDS", "label": "PostgreSQL"},
            {"id": "cache", "provider": "aws", "service": "ElastiCache", "label": "Redis"}
        ]

    2. Microservices with Clusters:
        nodes = [
            # Gateway cluster
            {"id": "alb", "provider": "aws", "service": "ALB", "label": "Load Balancer", "cluster_id": "gateway"},
            {"id": "api", "provider": "aws", "service": "APIGateway", "label": "API Gateway", "cluster_id": "gateway"},
            # Services cluster
            {"id": "users", "provider": "aws", "service": "Lambda", "label": "User Service", "cluster_id": "services"},
            {"id": "orders", "provider": "aws", "service": "ECS", "label": "Order Service", "cluster_id": "services"},
            {"id": "payments", "provider": "aws", "service": "Lambda", "label": "Payment Service", "cluster_id": "services"},
            # Data cluster
            {"id": "userdb", "provider": "aws", "service": "DynamoDB", "label": "User DB", "cluster_id": "data"},
            {"id": "orderdb", "provider": "aws", "service": "RDS", "label": "Order DB", "cluster_id": "data"}
        ]

    3. Kubernetes Deployment:
        nodes = [
            {"id": "ingress", "provider": "k8s", "service": "Ingress", "label": "Ingress Controller", "cluster_id": "k8s-cluster"},
            {"id": "svc", "provider": "k8s", "service": "Service", "label": "App Service", "cluster_id": "k8s-cluster"},
            {"id": "deploy", "provider": "k8s", "service": "Deployment", "label": "App Deployment", "cluster_id": "k8s-cluster"},
            {"id": "pod1", "provider": "k8s", "service": "Pod", "label": "Pod 1", "cluster_id": "k8s-cluster"},
            {"id": "pod2", "provider": "k8s", "service": "Pod", "label": "Pod 2", "cluster_id": "k8s-cluster"},
            {"id": "pvc", "provider": "k8s", "service": "PersistentVolumeClaim", "label": "Storage", "cluster_id": "k8s-cluster"}
        ]

    Most Common Services by Provider:
        AWS: EC2, S3, RDS, Lambda, DynamoDB, ElastiCache, ALB, CloudFront, APIGateway
        Azure: VirtualMachine, StorageAccounts, SQLDatabase, Functions, CosmosDB
        GCP: ComputeEngine, CloudStorage, CloudSQL, CloudFunctions, Firestore
        Kubernetes: Pod, Deployment, Service, Ingress, ConfigMap, Secret

    Returns:
        Dict with:
            - added: List of successfully added node IDs
            - added_count: Number of nodes added
            - errors: List of any errors encountered
            - icon_warnings: List of icons that were auto-corrected to fallbacks
            - status: "success" or "error"

    Note: Invalid icons are automatically corrected to appropriate fallbacks.
    """
    try:
        # Validate and fix icons for all nodes
        validated_nodes = []
        validation_warnings = []

        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue

            provider = node.get('provider', 'generic')
            service = node.get('service', 'blank')
            label = node.get('label')

            # Validate icon
            is_valid, error_msg = icon_validator.validate_icon(provider, service)

            if not is_valid:
                # Get fallback suggestions
                suggestions = icon_validator.suggest_fallback_icons(
                    provider,
                    service,
                    label,
                    limit=1
                )

                if suggestions:
                    fallback = suggestions[0]
                    # Update node with fallback icon
                    node = dict(node)  # Create a copy
                    node['provider'] = fallback["provider"]
                    node['service'] = fallback["service"]

                    validation_warnings.append({
                        "node": node.get('id'),
                        "original": f"{provider}.{service}",
                        "fallback": f"{fallback['provider']}.{fallback['service']}",
                        "reason": fallback['reason']
                    })

            validated_nodes.append(node)

        # Now add the validated nodes
        result = session_manager.add_nodes_bulk(session_id, validated_nodes)

        response = {
            "session_id": session_id,
            "added": result["added"],
            "added_count": len(result["added"]),
            "errors": result["errors"],
            "status": "success" if len(result["added"]) > 0 else "error"
        }

        # Add warnings if any icons were replaced
        if validation_warnings:
            response["icon_warnings"] = validation_warnings

        return response
    except Exception as e:
        logger.error(f"Failed to add nodes in bulk: {str(e)}")
        return {
            "error": f"Failed to add nodes: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def connect_nodes_bulk(
    session_id: str,
    connections: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Create multiple node connections at once for optimal performance.

    This bulk operation is 8-10x faster than multiple connect_nodes() calls.
    Recommended for connecting 3 or more node pairs.

    Performance Comparison:
        SLOW approach (avoid):
            connect_nodes(session_id, "lb", "web1")
            connect_nodes(session_id, "lb", "web2")
            connect_nodes(session_id, "web1", "db")

        FAST approach (recommended):
            connect_nodes_bulk(session_id, [
                {"from": "lb", "to": "web1"},
                {"from": "lb", "to": "web2"},
                {"from": "web1", "to": "db"}
            ])

    Args:
        session_id: UUID of the diagram session (from create_diagram)
        connections: List of connection definitions, each containing:
            - from: ID of source node (required)
            - to: ID of target node (required)
            - label: Connection label (optional) - e.g., "HTTP", "SQL", "API"
            - style: Line style (optional) - "solid" (default), "dashed", "dotted", "bold"
            - color: Hex color code (optional) - e.g., "#FF0000"

    Common Architecture Patterns:

    1. Load Balanced Web Application:
        connections = [
            {"from": "cdn", "to": "lb", "label": "HTTPS"},
            {"from": "lb", "to": "web1", "label": "HTTP"},
            {"from": "lb", "to": "web2", "label": "HTTP"},
            {"from": "web1", "to": "db", "label": "SQL"},
            {"from": "web2", "to": "db", "label": "SQL"},
            {"from": "web1", "to": "cache", "style": "dashed"},
            {"from": "web2", "to": "cache", "style": "dashed"}
        ]

    2. Microservices Communication:
        connections = [
            # API Gateway to services
            {"from": "gateway", "to": "users", "label": "REST"},
            {"from": "gateway", "to": "orders", "label": "REST"},
            {"from": "gateway", "to": "payments", "label": "REST"},
            # Service to service
            {"from": "orders", "to": "users", "label": "gRPC", "style": "dashed"},
            {"from": "orders", "to": "payments", "label": "Event", "style": "dotted"},
            # Services to data stores
            {"from": "users", "to": "userdb", "label": "SQL"},
            {"from": "orders", "to": "orderdb", "label": "NoSQL"},
            {"from": "payments", "to": "paymentdb", "label": "SQL"}
        ]

    3. Data Pipeline Flow:
        connections = [
            {"from": "source", "to": "ingest", "label": "Raw Data"},
            {"from": "ingest", "to": "transform", "label": "Validated"},
            {"from": "transform", "to": "enrich", "label": "Cleaned"},
            {"from": "enrich", "to": "warehouse", "label": "Processed"},
            {"from": "warehouse", "to": "analytics", "label": "Query"},
            {"from": "warehouse", "to": "ml", "label": "Training Data", "style": "dashed"}
        ]

    Connection Label Best Practices:
        - Network: "HTTP", "HTTPS", "TCP", "UDP", "WebSocket"
        - Database: "SQL", "NoSQL", "Read", "Write", "Replica"
        - Messaging: "Pub/Sub", "Queue", "Event", "Stream"
        - API: "REST", "GraphQL", "gRPC", "SOAP"
        - Data: "Sync", "Async", "Batch", "Stream"

    Returns:
        Dict with:
            - connected: Number of successful connections created
            - errors: List of any errors encountered
            - status: "success" or "error"
    """
    try:
        result = session_manager.connect_nodes_bulk(session_id, connections)

        return {
            "session_id": session_id,
            "connected": result["connected"],
            "errors": result["errors"],
            "status": "success" if result["connected"] > 0 else "error"
        }
    except Exception as e:
        logger.error(f"Failed to connect nodes in bulk: {str(e)}")
        return {
            "error": f"Failed to connect nodes: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def edit_node(
    session_id: str,
    node_id: str,
    provider: Optional[str] = None,
    service: Optional[str] = None,
    label: Optional[str] = None,
    cluster_id: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Edit an existing node's properties in the diagram.

    Use this to update node properties after creation, such as changing labels,
    moving to different clusters, or updating the icon.

    Args:
        session_id: UUID of the diagram session
        node_id: ID of the node to edit
        provider: New provider (optional) - will validate icon exists
        service: New service (optional) - will validate icon exists
        label: New display label (optional)
        cluster_id: New cluster assignment (optional, use empty string to remove from cluster)
        attributes: Additional attributes to merge (optional)

    Returns:
        Dict with:
            - node_id: The edited node ID
            - status: "success" or "error"
            - warning: Any icon validation warnings
            - message: Result message

    Example:
        # Change node label
        edit_node(session_id, "web1", label="Primary Web Server")

        # Move node to different cluster
        edit_node(session_id, "web1", cluster_id="frontend")

        # Update icon
        edit_node(session_id, "db1", provider="aws", service="Aurora")

        # Remove from cluster
        edit_node(session_id, "monitor", cluster_id="")
    """
    try:
        # Validate session
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        # Prepare updates dictionary
        updates = {}
        warning_msg = None

        # Validate and handle icon changes
        if provider is not None or service is not None:
            # Get current node to fill in missing provider/service
            session = session_manager.get_session(session_id)
            if not session or node_id not in session.nodes:
                return {
                    "error": f"Node not found: {node_id}",
                    "status": "error"
                }

            current_node = session.nodes[node_id]
            check_provider = provider if provider is not None else current_node.provider
            check_service = service if service is not None else current_node.service

            # Validate icon
            is_valid, error_msg = icon_validator.validate_icon(check_provider, check_service)

            if not is_valid:
                # Get fallback suggestions
                suggestions = icon_validator.suggest_fallback_icons(
                    check_provider,
                    check_service,
                    label or current_node.label,
                    limit=1
                )

                if suggestions:
                    fallback = suggestions[0]
                    check_provider = fallback["provider"]
                    check_service = fallback["service"]
                    warning_msg = (
                        f"Icon '{provider or current_node.provider}.{service or current_node.service}' not found. "
                        f"Using fallback: '{check_provider}.{check_service}' ({fallback['reason']})"
                    )

            if provider is not None:
                updates['provider'] = check_provider
            if service is not None:
                updates['service'] = check_service

        if label is not None:
            updates['label'] = label.strip() if label else None

        if cluster_id is not None:
            updates['cluster_id'] = cluster_id.strip() if cluster_id else None

        if attributes is not None:
            updates['attributes'] = attributes

        # Execute the edit
        result = session_manager.edit_node(session_id, node_id, updates)

        if result['success']:
            response = {
                "node_id": node_id,
                "status": "success",
                "message": f"Node '{node_id}' updated successfully"
            }
            if warning_msg:
                response["warning"] = warning_msg
            return response
        else:
            return {
                "error": result.get('error', 'Failed to edit node'),
                "status": "error"
            }

    except Exception as e:
        logger.error(f"Failed to edit node: {str(e)}")
        return {
            "error": f"Failed to edit node: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def edit_nodes_bulk(
    session_id: str,
    edits: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Edit multiple nodes at once for better performance.

    Args:
        session_id: UUID of the diagram session
        edits: List of edit specifications, each containing:
            - id: Node ID to edit (required)
            - provider: New provider (optional)
            - service: New service (optional)
            - label: New label (optional)
            - cluster_id: New cluster (optional)
            - attributes: Attributes to merge (optional)

    Example:
        edits = [
            {"id": "web1", "label": "Primary Web", "cluster_id": "frontend"},
            {"id": "web2", "label": "Secondary Web", "cluster_id": "frontend"},
            {"id": "db1", "provider": "aws", "service": "Aurora"},
            {"id": "cache1", "cluster_id": ""}  # Remove from cluster
        ]

    Returns:
        Dict with:
            - edited: List of successfully edited node IDs
            - errors: List of any errors
            - icon_warnings: List of icon validation warnings
            - status: "success" or "error"
    """
    try:
        # Validate session
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        # Process edits with icon validation
        validated_edits = []
        icon_warnings = []

        for edit in edits:
            if not isinstance(edit, dict):
                continue

            node_id = edit.get('id')
            if not node_id:
                continue

            # Handle icon validation if provider/service is being changed
            if 'provider' in edit or 'service' in edit:
                session = session_manager.get_session(session_id)
                if session and node_id in session.nodes:
                    current_node = session.nodes[node_id]
                    check_provider = edit.get('provider', current_node.provider)
                    check_service = edit.get('service', current_node.service)

                    # Validate icon
                    is_valid, error_msg = icon_validator.validate_icon(check_provider, check_service)

                    if not is_valid:
                        suggestions = icon_validator.suggest_fallback_icons(
                            check_provider,
                            check_service,
                            edit.get('label', current_node.label),
                            limit=1
                        )

                        if suggestions:
                            fallback = suggestions[0]
                            edit = dict(edit)  # Copy to avoid modifying original
                            if 'provider' in edit:
                                edit['provider'] = fallback["provider"]
                            if 'service' in edit:
                                edit['service'] = fallback["service"]

                            icon_warnings.append({
                                "node": node_id,
                                "original": f"{check_provider}.{check_service}",
                                "fallback": f"{fallback['provider']}.{fallback['service']}",
                                "reason": fallback['reason']
                            })

            validated_edits.append(edit)

        # Execute bulk edit
        result = session_manager.edit_nodes_bulk(session_id, validated_edits)

        response = {
            "session_id": session_id,
            "edited": result["edited"],
            "edited_count": len(result["edited"]),
            "errors": result["errors"],
            "status": "success" if len(result["edited"]) > 0 else "error"
        }

        if icon_warnings:
            response["icon_warnings"] = icon_warnings

        return response

    except Exception as e:
        logger.error(f"Failed to edit nodes in bulk: {str(e)}")
        return {
            "error": f"Failed to edit nodes: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def edit_cluster(
    session_id: str,
    cluster_id: str,
    label: Optional[str] = None,
    parent_cluster_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Edit an existing cluster's properties.

    Args:
        session_id: UUID of the diagram session
        cluster_id: ID of the cluster to edit
        label: New display label (optional)
        parent_cluster_id: New parent cluster for nesting (optional, use empty string to remove nesting)

    Returns:
        Dict with:
            - cluster_id: The edited cluster ID
            - status: "success" or "error"
            - message: Result message

    Example:
        # Change cluster label
        edit_cluster(session_id, "frontend", label="Web Tier")

        # Nest cluster under another
        edit_cluster(session_id, "services", parent_cluster_id="backend")

        # Remove nesting
        edit_cluster(session_id, "services", parent_cluster_id="")
    """
    try:
        # Validate session
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        # Prepare updates
        updates = {}
        if label is not None:
            updates['label'] = label.strip() if label else None
        if parent_cluster_id is not None:
            updates['parent_cluster_id'] = parent_cluster_id.strip() if parent_cluster_id else None

        # Execute edit
        result = session_manager.edit_cluster(session_id, cluster_id, updates)

        if result['success']:
            return {
                "cluster_id": cluster_id,
                "status": "success",
                "message": f"Cluster '{cluster_id}' updated successfully"
            }
        else:
            return {
                "error": result.get('error', 'Failed to edit cluster'),
                "status": "error"
            }

    except Exception as e:
        logger.error(f"Failed to edit cluster: {str(e)}")
        return {
            "error": f"Failed to edit cluster: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def edit_clusters_bulk(
    session_id: str,
    edits: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Edit multiple clusters at once.

    Args:
        session_id: UUID of the diagram session
        edits: List of edit specifications, each containing:
            - id: Cluster ID to edit (required)
            - label: New label (optional)
            - parent_cluster_id: New parent cluster (optional)

    Example:
        edits = [
            {"id": "frontend", "label": "Web Tier"},
            {"id": "backend", "label": "Application Tier"},
            {"id": "services", "parent_cluster_id": "backend"}
        ]

    Returns:
        Dict with:
            - edited: List of successfully edited cluster IDs
            - errors: List of any errors
            - status: "success" or "error"
    """
    try:
        # Validate session
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        result = session_manager.edit_clusters_bulk(session_id, edits)

        return {
            "session_id": session_id,
            "edited": result["edited"],
            "edited_count": len(result["edited"]),
            "errors": result["errors"],
            "status": "success" if len(result["edited"]) > 0 else "error"
        }

    except Exception as e:
        logger.error(f"Failed to edit clusters in bulk: {str(e)}")
        return {
            "error": f"Failed to edit clusters: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def edit_connection(
    session_id: str,
    from_node: str,
    to_node: str,
    label: Optional[str] = None,
    color: Optional[str] = None,
    style: Optional[str] = None
) -> Dict[str, Any]:
    """
    Edit an existing connection's properties.

    Connections are identified by their source and target nodes.

    Args:
        session_id: UUID of the diagram session
        from_node: Source node ID
        to_node: Target node ID
        label: New connection label (optional)
        color: New color hex code (optional, e.g., "#FF5733")
        style: New line style (optional): "solid", "dashed", "dotted", "bold"

    Returns:
        Dict with:
            - from_node: Source node ID
            - to_node: Target node ID
            - status: "success" or "error"
            - message: Result message

    Example:
        # Change connection label
        edit_connection(session_id, "web1", "db1", label="Encrypted SQL")

        # Change connection style
        edit_connection(session_id, "web1", "cache1", style="dashed", color="#00FF00")
    """
    try:
        # Validate session
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        # Find the connection
        conn_index = session_manager.find_connection(session_id, from_node, to_node)
        if conn_index is None:
            return {
                "error": f"Connection not found from '{from_node}' to '{to_node}'",
                "status": "error"
            }

        # Prepare updates
        updates = {}
        if label is not None:
            updates['label'] = label.strip() if label else None
        if color is not None:
            updates['color'] = color.strip() if color else None
        if style is not None:
            if style not in ["solid", "dashed", "dotted", "bold", ""]:
                return {
                    "error": f"Invalid style: {style}. Must be solid, dashed, dotted, or bold",
                    "status": "error"
                }
            updates['style'] = style if style else None

        # Execute edit
        result = session_manager.edit_connection(session_id, conn_index, updates)

        if result['success']:
            return {
                "from_node": from_node,
                "to_node": to_node,
                "status": "success",
                "message": f"Connection from '{from_node}' to '{to_node}' updated successfully"
            }
        else:
            return {
                "error": result.get('error', 'Failed to edit connection'),
                "status": "error"
            }

    except Exception as e:
        logger.error(f"Failed to edit connection: {str(e)}")
        return {
            "error": f"Failed to edit connection: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def edit_connections_bulk(
    session_id: str,
    edits: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Edit multiple connections at once.

    Args:
        session_id: UUID of the diagram session
        edits: List of edit specifications, each containing:
            - from_node: Source node ID (required)
            - to_node: Target node ID (required)
            - label: New label (optional)
            - color: New color (optional)
            - style: New style (optional)

    Example:
        edits = [
            {"from_node": "lb", "to_node": "web1", "label": "HTTPS", "color": "#00FF00"},
            {"from_node": "lb", "to_node": "web2", "label": "HTTPS", "color": "#00FF00"},
            {"from_node": "web1", "to_node": "db1", "style": "dashed"}
        ]

    Returns:
        Dict with:
            - edited: Number of successfully edited connections
            - errors: List of any errors
            - status: "success" or "error"
    """
    try:
        # Validate session
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        edited_count = 0
        errors = []

        for edit in edits:
            from_node = edit.get('from_node')
            to_node = edit.get('to_node')

            if not from_node or not to_node:
                errors.append({"error": "Missing from_node or to_node", "edit": edit})
                continue

            # Find the connection
            conn_index = session_manager.find_connection(session_id, from_node, to_node)
            if conn_index is None:
                errors.append({
                    "error": f"Connection not found",
                    "from": from_node,
                    "to": to_node
                })
                continue

            # Prepare updates
            updates = {}
            if 'label' in edit:
                updates['label'] = edit['label']
            if 'color' in edit:
                updates['color'] = edit['color']
            if 'style' in edit:
                if edit['style'] not in ["solid", "dashed", "dotted", "bold", "", None]:
                    errors.append({
                        "error": f"Invalid style: {edit['style']}",
                        "from": from_node,
                        "to": to_node
                    })
                    continue
                updates['style'] = edit['style']

            # Execute edit
            result = session_manager.edit_connection(session_id, conn_index, updates)

            if result['success']:
                edited_count += 1
            else:
                errors.append({
                    "error": result.get('error'),
                    "from": from_node,
                    "to": to_node
                })

        return {
            "session_id": session_id,
            "edited": edited_count,
            "errors": errors,
            "status": "success" if edited_count > 0 else "error"
        }

    except Exception as e:
        logger.error(f"Failed to edit connections in bulk: {str(e)}")
        return {
            "error": f"Failed to edit connections: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def search_services_bulk(
    queries: List[str],
    limit_per_query: int = 10
) -> Dict[str, Any]:
    """
    Search for multiple services at once across all providers.

    Much faster than searching one by one when you need to find multiple services.

    Args:
        queries: List of search terms
        limit_per_query: Maximum results per query (default: 10)

    Example:
        queries = ["database", "cache", "queue", "storage"]

    Returns:
        Dict mapping each query to its search results
    """
    try:
        if len(queries) > 20:
            return {
                "error": "Too many queries (max 20)",
                "status": "error"
            }

        results = provider_registry.search_services_bulk(queries, limit_per_query)

        return {
            "results": results,
            "query_count": len(queries),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to search services in bulk: {str(e)}")
        return {
            "error": f"Failed to search services: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def validate_icon(
    provider: str,
    service: str,
    label: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validate if an icon exists and get fallback suggestions if it doesn't.

    This tool helps ensure nodes can be created with valid icons. Always use this
    before creating nodes if you're unsure whether an icon exists.

    Args:
        provider: Provider name (e.g., "aws", "azure", "k8s")
        service: Service name (e.g., "ec2", "rds", "pod")
        label: Optional label to help with categorization

    Returns:
        Dict with:
            - valid: Boolean indicating if the icon exists
            - provider: The provider to use (original or fallback)
            - service: The service to use (original or fallback)
            - suggestions: List of alternative icon suggestions if invalid
            - help_message: Detailed help message with suggestions

    Example Usage:
        # Check if an icon exists
        validate_icon("aws", "myservice")
        # Returns suggestions if icon doesn't exist

        # Get fallback for a database service
        validate_icon("custom", "database", "User Database")
        # Returns appropriate database icon suggestions
    """
    try:
        # Validate the icon
        is_valid, error_msg = icon_validator.validate_icon(provider, service)

        if is_valid:
            return {
                "valid": True,
                "provider": provider,
                "service": service,
                "message": f"Icon '{provider}.{service}' is valid and available",
                "status": "success"
            }

        # Icon not valid, get suggestions
        suggestions = icon_validator.suggest_fallback_icons(
            provider,
            service,
            label,
            limit=5
        )

        # Format suggestions for response
        formatted_suggestions = []
        for suggestion in suggestions:
            formatted_suggestions.append({
                "provider": suggestion["provider"],
                "service": suggestion["service"],
                "category": suggestion["category"],
                "reason": suggestion["reason"],
                "confidence": suggestion["confidence"],
                "icon_path": f"{suggestion['provider']}.{suggestion['service']}"
            })

        # Get help message
        help_message = icon_validator.get_icon_help_message(provider, service, label)

        # Use the best suggestion as recommended fallback
        best_fallback = suggestions[0] if suggestions else {
            "provider": "generic",
            "service": "blank"
        }

        return {
            "valid": False,
            "provider": best_fallback["provider"],
            "service": best_fallback["service"],
            "error": error_msg,
            "suggestions": formatted_suggestions,
            "help_message": help_message,
            "recommended": f"{best_fallback['provider']}.{best_fallback['service']}",
            "status": "warning"
        }

    except Exception as e:
        logger.error(f"Failed to validate icon: {str(e)}")
        return {
            "error": f"Failed to validate icon: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def get_services_by_categories(
    provider: str,
    categories: List[str]
) -> Dict[str, Any]:
    """
    Get services for multiple categories at once from a provider.

    Faster than querying categories one by one.

    Args:
        provider: Provider name (e.g., "aws", "azure", "gcp")
        categories: List of category names

    Example:
        provider = "aws"
        categories = ["compute", "database", "storage", "network"]

    Returns:
        Dict mapping each category to its services
    """
    try:
        if len(categories) > 50:
            return {
                "error": "Too many categories (max 50)",
                "status": "error"
            }

        results = provider_registry.get_services_by_category(provider, categories)

        total_services = sum(len(services) for services in results.values())

        return {
            "provider": provider,
            "results": results,
            "category_count": len(categories),
            "total_services": total_services,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to get services by categories: {str(e)}")
        return {
            "error": f"Failed to get services: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def render_diagram(
    session_id: str,
    output_path: Optional[str] = None,
    format: Optional[str] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Generate the final diagram image from the current session state.

    This should be the last tool called after completing all node additions,
    connections, and cluster definitions.

    Complete Workflow:
        1. create_diagram(name, direction, graph_spacing)  # Get session_id
        2. create_clusters_bulk() [optional]               # Organize nodes
        3. add_nodes_bulk()                                # Add all nodes
        4. connect_nodes_bulk()                            # Connect nodes
        5. render_diagram(session_id)                      # Generate output

    Prerequisites Before Rendering:
        - Valid session_id from create_diagram()
        - At least one node added
        - Connections added (optional but recommended)
        - Clusters created (optional for organization)

    Args:
        session_id: UUID from create_diagram response (REQUIRED)
        output_path: Optional custom filename (basename only, no path)
        format: Optional format override ("png", "svg", "pdf", "dot")
        timeout: Max seconds to wait (default: 30, max: 120)

    Returns:
        Success: {"file_path": "/path/to/output.png", "status": "success", ...}
        Error: {"error": "reason", "status": "error"}

    Troubleshooting Guide:

    Problem: "Diagram is cluttered/overlapping"
    Solution: Recreate with graph_spacing="spacious" or "extra-spacious"
        create_diagram(name, direction="TB", graph_spacing="spacious")

    Problem: "No nodes to render"
    Solution: Ensure nodes were added successfully:
        result = add_nodes_bulk(session_id, nodes)
        # Check result["added_count"] > 0

    Problem: "Session not found"
    Solution: Always save and use the session_id:
        session = create_diagram(...)
        session_id = session["session_id"]  # SAVE THIS!

    Problem: "Rate limit exceeded"
    Solution: Wait 60 seconds or check existing sessions:
        list_sessions()  # Find existing session to reuse

    Problem: "Timeout on large diagram"
    Solution: Increase timeout for 100+ nodes:
        render_diagram(session_id, timeout=60)

    Problem: "Icons not showing correctly"
    Solution: Icons are auto-validated, check icon_warnings in add_nodes_bulk response

    Format Selection Guide:
        - < 50 nodes: "png" (default, best quality)
        - 50-100 nodes: "svg" (scalable, smaller file)
        - 100+ nodes: "svg" or increase timeout
        - Web display: "svg"
        - Documents: "png" or "pdf"
        - Further editing: "dot"

    Complete Example - AWS Web Application:
        # Step 1: Create with appropriate spacing
        session = create_diagram("AWS Web App", direction="TB", graph_spacing="normal")
        session_id = session["session_id"]

        # Step 2: Add all nodes at once
        add_nodes_bulk(session_id, [
            {"id": "cdn", "provider": "aws", "service": "CloudFront", "label": "CDN"},
            {"id": "lb", "provider": "aws", "service": "ALB", "label": "Load Balancer"},
            {"id": "web1", "provider": "aws", "service": "EC2", "label": "Web 1"},
            {"id": "web2", "provider": "aws", "service": "EC2", "label": "Web 2"},
            {"id": "db", "provider": "aws", "service": "RDS", "label": "Database"}
        ])

        # Step 3: Connect all at once
        connect_nodes_bulk(session_id, [
            {"from": "cdn", "to": "lb", "label": "HTTPS"},
            {"from": "lb", "to": "web1"},
            {"from": "lb", "to": "web2"},
            {"from": "web1", "to": "db", "label": "SQL"},
            {"from": "web2", "to": "db", "label": "SQL"}
        ])

        # Step 4: Render (THIS TOOL)
        result = render_diagram(session_id)
        # Output: {"file_path": "/path/to/AWS_Web_App.png", "status": "success"}

    Pro Tips:
        - ALWAYS render last after all modifications
        - If diagram looks bad, recreate with better spacing
        - Check icon_warnings from add_nodes_bulk for icon issues
        - For complex diagrams, validate architecture first:
          validate_architecture(session_id)
    """
    try:
        # Check rate limit
        allowed, rate_msg = check_rate_limit(session_id, "render")
        if not allowed:
            return {
                "error": rate_msg,
                "status": "error",
                "retry_after": 60
            }

        # Validate session ID
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        session = session_manager.get_session(session_id)
        if not session:
            return {
                "error": f"Session not found: {session_id}",
                "status": "error"
            }

        # Check if there are nodes to render
        if not session.nodes:
            return {
                "error": "No nodes to render",
                "status": "error"
            }

        # Validate and override format if specified
        if format:
            if not validate_output_format(format):
                return {
                    "error": f"Invalid format: {format}. Must be one of: png, svg, pdf, dot",
                    "status": "error"
                }
            session.output_format = format.lower()

        # Get output directory (use custom if specified in session metadata)
        output_base_dir = OUTPUT_DIR
        if "output_dir" in session.metadata:
            output_base_dir = Path(session.metadata["output_dir"])

        # Get safe output path
        full_path = get_safe_output_path(
            output_base_dir,
            output_path,
            session.output_format
        )

        # Ensure parent directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Build the diagram with timeout
        def build_with_timeout():
            return diagram_builder.build_from_session(session, str(full_path.with_suffix("")))

        # Use thread pool executor for timeout handling
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(build_with_timeout)
            try:
                result_path = future.result(timeout=timeout)
            except FutureTimeoutError:
                future.cancel()
                return {
                    "error": f"Diagram generation timed out after {timeout} seconds. Consider using fewer nodes or increasing timeout.",
                    "status": "error"
                }
            except Exception as e:
                return {
                    "error": f"Failed to generate diagram: {str(e)}",
                    "status": "error"
                }

        # Verify file was created and get size
        if not os.path.exists(result_path):
            return {
                "error": "Failed to create diagram file",
                "status": "error"
            }

        file_size = os.path.getsize(result_path)

        response = {
            "file_path": str(result_path),
            "file_size": file_size,
            "status": "success",
            "message": "Diagram rendered successfully"
        }

        return response

    except Exception as e:
        return {
            "error": f"Failed to render diagram: {str(e)}",
            "status": "error"
        }


# Duplicate session management functions removed - see lines 453-558 for primary implementations


@mcp.tool()
def delete_session(session_id: str) -> Dict[str, Any]:
    """
    Delete a diagram session.

    Args:
        session_id: UUID of the diagram session

    Returns:
        Dictionary with deletion status
    """
    try:
        # Validate session ID
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        if session_manager.delete_session(session_id):
            return {
                "status": "success",
                "message": f"Deleted session: {session_id}"
            }
        else:
            return {
                "error": f"Session not found: {session_id}",
                "status": "error"
            }

    except Exception as e:
        return {
            "error": f"Failed to delete session: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def list_nodes(session_id: str) -> Dict[str, Any]:
    """
    List all nodes in a diagram session.

    Args:
        session_id: UUID of the diagram session

    Returns:
        Dictionary with list of nodes
    """
    try:
        # Validate session ID
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        session = session_manager.get_session(session_id)
        if not session:
            return {
                "error": f"Session not found: {session_id}",
                "status": "error"
            }

        nodes_list = []
        for node_id, node in session.nodes.items():
            nodes_list.append({
                "id": node_id,
                "provider": node.provider,
                "service": node.service,
                "label": node.label,
                "cluster_id": node.cluster_id
            })

        return {
            "nodes": nodes_list,
            "count": len(nodes_list),
            "status": "success"
        }

    except Exception as e:
        return {
            "error": f"Failed to list nodes: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def remove_node(session_id: str, node_id: str) -> Dict[str, Any]:
    """
    Remove a node from the diagram.

    Args:
        session_id: UUID of the diagram session
        node_id: ID of the node to remove

    Returns:
        Dictionary with removal status
    """
    try:
        # Validate session ID
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        if not node_id or len(node_id.strip()) == 0:
            return {
                "error": "Node ID cannot be empty",
                "status": "error"
            }

        node_id = node_id.strip()

        if session_manager.remove_node(session_id, node_id):
            return {
                "status": "success",
                "message": f"Removed node: {node_id}"
            }
        else:
            return {
                "error": f"Node not found: {node_id}",
                "status": "error"
            }

    except Exception as e:
        return {
            "error": f"Failed to remove node: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def add_nodes_bulk(
    session_id: str,
    nodes: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Add multiple nodes at once.

    Args:
        session_id: UUID of the diagram session
        nodes: List of node specifications

    Returns:
        Dictionary with added nodes and any failures
    """
    try:
        # Validate session ID
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        session = session_manager.get_session(session_id)
        if not session:
            return {
                "error": f"Session not found: {session_id}",
                "status": "error"
            }

        if not nodes or not isinstance(nodes, list):
            return {
                "error": "Nodes must be a non-empty list",
                "status": "error"
            }

        if len(nodes) > 100:
            return {
                "error": "Too many nodes (max 100 per bulk operation)",
                "status": "error"
            }

        added_nodes = []
        failed_nodes = []

        for i, node_spec in enumerate(nodes):
            try:
                if not isinstance(node_spec, dict):
                    failed_nodes.append({
                        "index": i,
                        "spec": node_spec,
                        "error": "Node specification must be a dictionary"
                    })
                    continue

                node_id = node_spec.get("node_id")
                if not node_id or len(str(node_id).strip()) == 0:
                    failed_nodes.append({
                        "index": i,
                        "spec": node_spec,
                        "error": "Missing or empty node_id"
                    })
                    continue

                node_id = str(node_id).strip()

                if len(node_id) > 50:
                    failed_nodes.append({
                        "index": i,
                        "spec": node_spec,
                        "error": "Node ID too long (max 50 characters)"
                    })
                    continue

                if node_id in session.nodes:
                    failed_nodes.append({
                        "index": i,
                        "spec": node_spec,
                        "error": f"Node already exists: {node_id}"
                    })
                    continue

                node = NodeInfo(
                    id=node_id,
                    provider=str(node_spec.get("provider", "generic")).strip(),
                    service=str(node_spec.get("service", "blank")).strip(),
                    label=str(node_spec.get("label", "")).strip() or None,
                    cluster_id=str(node_spec.get(
                        "cluster_id", "")).strip() or None,
                    attributes=node_spec.get("attributes") if node_spec.get(
                        "attributes") is not None else {}
                )

                if session_manager.add_node(session_id, node):
                    added_nodes.append(node_id)
                else:
                    failed_nodes.append({
                        "index": i,
                        "spec": node_spec,
                        "error": "Failed to add node"
                    })

            except Exception as e:
                failed_nodes.append({
                    "index": i,
                    "spec": node_spec,
                    "error": f"Error processing node: {str(e)}"
                })

        return {
            "added_nodes": added_nodes,
            "failed_nodes": failed_nodes,
            "added_count": len(added_nodes),
            "failed_count": len(failed_nodes),
            "status": "success" if not failed_nodes else "partial"
        }

    except Exception as e:
        return {
            "error": f"Failed to add bulk nodes: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def list_providers() -> Dict[str, Any]:
    """
    List all available diagram providers.

    Returns:
        Dictionary with list of providers
    """
    try:
        providers = provider_registry.list_providers()
        return {
            "providers": providers,
            "count": len(providers),
            "status": "success"
        }
    except Exception as e:
        return {
            "error": f"Failed to list providers: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def list_categories(provider: str) -> Dict[str, Any]:
    """
    List categories for a specific provider.

    Args:
        provider: Provider name (aws, azure, gcp, k8s, etc.)

    Returns:
        Dictionary with list of categories
    """
    try:
        if not provider or len(provider.strip()) == 0:
            return {
                "error": "Provider name cannot be empty",
                "status": "error"
            }

        provider = provider.strip().lower()
        categories = provider_registry.list_categories(provider)

        return {
            "provider": provider,
            "categories": categories,
            "count": len(categories),
            "status": "success"
        }
    except Exception as e:
        return {
            "error": f"Failed to list categories: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def list_services(provider: str, category: str) -> Dict[str, Any]:
    """
    List specific services available within a provider's category.

    USE THIS TOOL WHEN: You need to find the exact service name
    to use in add_node() for a specific provider and category.

    What are services?
    Services are the specific components you can add to your diagram.
    Each service has a unique icon. The service name is what you pass
    to add_node() along with the provider name.

    Args:
        provider: Provider name from list_providers()
            Examples: "aws", "azure", "gcp", "k8s"

        category: Category name from list_categories(provider)
            Examples: "compute", "storage", "database", "network"

    Returns:
        Dictionary containing:
        - provider: The provider name
        - category: The category name
        - services: List of service identifiers
        - count: Number of services
        - status: "success" or "error"
        - descriptions: Service descriptions (when available)

    Common Services by Provider/Category:

    AWS Compute Services:
        - "ec2": Elastic Compute Cloud (virtual servers)
        - "lambda": Serverless functions
        - "ecs": Elastic Container Service
        - "batch": Batch computing jobs
        - "lightsail": Simplified virtual servers
        - "elasticbeanstalk": Application platform

    AWS Storage Services:
        - "s3": Simple Storage Service (object storage)
        - "efs": Elastic File System (NFS)
        - "ebs": Elastic Block Store (disk volumes)
        - "glacier": Archive storage
        - "storagegateway": Hybrid storage

    AWS Database Services:
        - "rds": Relational Database Service
        - "dynamodb": NoSQL database
        - "elasticache": In-memory cache (Redis/Memcached)
        - "redshift": Data warehouse
        - "documentdb": Document database (MongoDB compatible)
        - "neptune": Graph database

    Azure Compute Services:
        - "vm": Virtual Machines
        - "functions": Serverless functions
        - "containerinstances": Container instances
        - "appservice": Web app hosting

    GCP Compute Services:
        - "gce": Compute Engine (virtual machines)
        - "functions": Cloud Functions
        - "run": Cloud Run (containers)
        - "gke": Kubernetes Engine

    Kubernetes Workload Services:
        - "pod": Single container or group
        - "deploy": Deployment (manages pods)
        - "sts": StatefulSet (stateful apps)
        - "ds": DaemonSet (runs on all nodes)
        - "job": One-time job
        - "cronjob": Scheduled job

    Example Response:
        {
            "provider": "aws",
            "category": "compute",
            "services": [
                "ec2",
                "lambda",
                "ecs",
                "eks",
                "batch",
                "lightsail",
                "elasticbeanstalk"
            ],
            "count": 7,
            "status": "success"
        }

    Usage in add_node():
        Once you have the service name, use it in add_node():
        >>> add_node(
        ...     session_id=session_id,
        ...     node_id="webserver1",
        ...     provider="aws",        # From list_providers()
        ...     service="ec2",         # From this tool
        ...     label="Web Server"
        ... )

    Tips:
        - Service names are usually lowercase abbreviations
        - Some services have multiple variants (ec2, ec2_instance, ec2_spot)
        - If unsure, use search_services() to find by keyword
        - Generic provider services include: "blank", "device", "client"
    """
    try:
        if not provider or len(provider.strip()) == 0:
            return {
                "error": "Provider name cannot be empty",
                "status": "error"
            }

        if not category or len(category.strip()) == 0:
            return {
                "error": "Category name cannot be empty",
                "status": "error"
            }

        provider = provider.strip().lower()
        category = category.strip().lower()

        services = provider_registry.list_services(provider, category)

        return {
            "provider": provider,
            "category": category,
            "services": services,
            "count": len(services),
            "status": "success"
        }
    except Exception as e:
        return {
            "error": f"Failed to list services: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def search_services(query: str, provider: Optional[str] = None) -> Dict[str, Any]:
    """
    Search for services by keyword to find the right provider/service combination.

    Use this tool when you're not sure what provider/service to use for a particular
    technology or service.

    Args:
        query: Search term (e.g., "client", "database", "storage", "api", "cache")
        provider: Optional - limit search to specific provider (e.g., "aws", "azure", "gcp")

    Returns:
        Dictionary with matching services:
        - results: List of matches with provider, category, and service name
        - count: Number of matches found

    Example:
        >>> search_services("client")
        Returns matches like: onprem.client.Client, aws.general.Client

        >>> search_services("database", "aws")
        Returns AWS database services: aws.database.RDS, aws.database.DynamoDB, etc.
    """
    try:
        if not query or len(query.strip()) == 0:
            return {
                "error": "Search query cannot be empty",
                "status": "error"
            }

        query = query.strip()
        if len(query) > 100:
            return {
                "error": "Search query too long (max 100 characters)",
                "status": "error"
            }

        provider_clean = provider.strip().lower() if provider else None

        results = provider_registry.search_services(query, provider_clean)

        return {
            "query": query,
            "provider": provider_clean,
            "results": results,
            "count": len(results),
            "status": "success"
        }
    except Exception as e:
        return {
            "error": f"Failed to search services: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def create_cluster(
    session_id: str,
    cluster_id: str,
    label: str,
    attributes: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a cluster (logical grouping) for nodes in the diagram.

    Clusters visually group related nodes with a rounded rectangle boundary.
    The diagrams library automatically handles visual styling including background colors.

    IMPORTANT CLUSTERING RULES FOR PROPER BOUNDARIES:
    1. **Create clusters BEFORE adding nodes** - Clusters must exist before nodes can be placed in them
    2. **Use meaningful hierarchy** - Group by logical layers (frontend/backend/data) or by function
    3. **Don't overlap clusters** - Each cluster should contain distinct services
    4. **Keep related services together** - Services that communicate frequently should be in same or adjacent clusters
    5. **Limit nesting depth** - Maximum 3-4 levels for clarity
    6. **One cluster per logical boundary** - Don't create multiple clusters for same purpose

    COMMON ARCHITECTURE PATTERNS:

    Three-Tier Architecture:
    - "frontend" cluster: Load balancers, CDN, static content
    - "application" cluster: Web servers, API servers, microservices
    - "data" cluster: Databases, caches, message queues

    Kubernetes Architecture:
    - "ingress" cluster: Ingress controllers, load balancers
    - "services" cluster: Service mesh, API gateway
    - "workloads" cluster: Deployments, pods, jobs
    - "storage" cluster: PVCs, storage classes

    Microservices Architecture:
    - Separate cluster per bounded context/domain
    - "shared-services" cluster for common components
    - "infrastructure" cluster for platform services

    TECHNICAL DETAILS (from diagrams library Cluster class):
    - Automatic background colors that cycle based on nesting depth:
      Level 0: #E5F5FD (light blue), Level 1: #EBF3E7 (light green),
      Level 2: #ECE8F6 (light purple), Level 3: #FDF7E3 (light yellow)
    - Default border color: #AEB6BE (gray)
    - Default style: "rounded" rectangle
    - Cluster IDs are prefixed with "cluster_" internally for Graphviz
    - Supports nesting (clusters within clusters)

    Args:
        session_id: UUID of the diagram session (from create_diagram)
        cluster_id: Unique identifier for the cluster (e.g., "web-tier", "db-cluster")
            Note: Don't prefix with "cluster_" - added automatically
        label: Display label shown on the cluster (e.g., "Web Servers", "Database Cluster")
            This appears at the top of the cluster boundary
        attributes: Optional Graphviz styling attributes for the cluster
            Common attributes:
            - "style": "rounded" (default), "filled", "dashed", "bold"
            - "pencolor": Border color (default #AEB6BE)
            - "bgcolor": Background color (auto-set by library)
            - "fontsize": Label font size (default "12")
            - "penwidth": Border thickness

    Returns:
        Dictionary with cluster_id and status

    Example Response:
        {
            "cluster_id": "web-tier",
            "status": "success",
            "message": "Created cluster: Web Servers"
        }

    Example Usage:
        1. Create web tier: create_cluster(session_id, "web-tier", "Web Servers")
        2. Create DB cluster: create_cluster(session_id, "db-cluster", "Database Cluster")
        3. Add nodes to cluster: add_node(..., cluster_id="web-tier")
        4. Nest clusters: nest_cluster(parent_id="vpc", child_id="web-tier")

    Visual Hierarchy Examples:
        - Network layers: DMZ → Public Subnet → Private Subnet
        - Environments: Production VPC → Web Tier → Individual Servers
        - Regions: US-East → Availability Zone A → Services
    """
    try:
        # Validate session ID
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        session = session_manager.get_session(session_id)
        if not session:
            return {
                "error": f"Session not found: {session_id}",
                "status": "error"
            }

        # Validate inputs
        if not cluster_id or len(cluster_id.strip()) == 0:
            return {
                "error": "Cluster ID cannot be empty",
                "status": "error"
            }

        if not label or len(label.strip()) == 0:
            return {
                "error": "Cluster label cannot be empty",
                "status": "error"
            }

        cluster_id = cluster_id.strip()
        label = label.strip()

        # Validate attributes - handle empty string "{}" case
        if attributes is not None:
            if isinstance(attributes, str):
                # Handle case where empty object is passed as string
                if attributes == "{}" or attributes.strip() == "{}" or attributes == "null":
                    attributes = None
                else:
                    try:
                        # Try to parse if it's a JSON string
                        import json
                        attributes = json.loads(attributes)
                    except:
                        return {
                            "error": "attributes must be a dictionary or valid JSON string",
                            "status": "error"
                        }
            elif not isinstance(attributes, dict):
                return {
                    "error": "attributes must be a dictionary",
                    "status": "error"
                }

        # Check if cluster already exists
        if cluster_id in session.clusters:
            return {
                "error": f"Cluster already exists: {cluster_id}",
                "status": "error"
            }

        cluster = ClusterInfo(
            id=cluster_id,
            label=label,
            attributes=attributes if attributes is not None else {}
        )

        if session_manager.add_cluster(session_id, cluster):
            return {
                "cluster_id": cluster_id,
                "status": "success",
                "message": f"Created cluster: {label}"
            }
        else:
            return {
                "error": "Failed to create cluster",
                "status": "error"
            }

    except Exception as e:
        return {
            "error": f"Failed to create cluster: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def add_to_cluster(
    session_id: str,
    cluster_id: str,
    node_ids: List[str]
) -> Dict[str, Any]:
    """
    Add existing nodes to a cluster.

    This moves nodes into a cluster for visual grouping. Nodes must already exist
    in the diagram before being added to a cluster.

    Args:
        session_id: UUID of the diagram session
        cluster_id: ID of the cluster to add nodes to
        node_ids: List of node IDs to add to the cluster

    Returns:
        Dictionary with success status and nodes added

    Example Response:
        {
            "cluster_id": "web-tier",
            "nodes_added": ["web1", "web2", "web3"],
            "status": "success",
            "message": "Added 3 nodes to cluster"
        }

    Example Usage:
        add_to_cluster(session_id, "web-tier", ["web1", "web2", "web3"])
    """
    try:
        # Validate session ID
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        session = session_manager.get_session(session_id)
        if not session:
            return {
                "error": f"Session not found: {session_id}",
                "status": "error"
            }

        # Check if cluster exists
        if cluster_id not in session.clusters:
            return {
                "error": f"Cluster not found: {cluster_id}",
                "status": "error"
            }

        if not node_ids or not isinstance(node_ids, list):
            return {
                "error": "node_ids must be a non-empty list",
                "status": "error"
            }

        # Validate all nodes exist
        nodes_added = []
        for node_id in node_ids:
            if node_id not in session.nodes:
                continue  # Skip non-existent nodes

            # Update node's cluster_id
            session.nodes[node_id].cluster_id = cluster_id
            nodes_added.append(node_id)

            # Add to cluster's node list
            if node_id not in session.clusters[cluster_id].nodes:
                session.clusters[cluster_id].nodes.append(node_id)

        session.updated_at = datetime.now()

        return {
            "cluster_id": cluster_id,
            "nodes_added": nodes_added,
            "status": "success",
            "message": f"Added {len(nodes_added)} nodes to cluster"
        }

    except Exception as e:
        return {
            "error": f"Failed to add nodes to cluster: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def nest_cluster(
    session_id: str,
    parent_cluster_id: str,
    child_cluster_id: str
) -> Dict[str, Any]:
    """
    Create nested clusters by placing one cluster inside another.

    This allows hierarchical organization, like having a "Microservices" cluster
    inside a "Backend" cluster.

    Args:
        session_id: UUID of the diagram session
        parent_cluster_id: ID of the parent cluster
        child_cluster_id: ID of the child cluster to nest

    Returns:
        Dictionary with nesting status

    Example Response:
        {
            "parent": "backend",
            "child": "microservices",
            "status": "success",
            "message": "Nested microservices cluster inside backend"
        }

    Example Usage:
        1. Create parent: create_cluster(session_id, "backend", "Backend Services")
        2. Create child: create_cluster(session_id, "apis", "API Layer")
        3. Nest them: nest_cluster(session_id, "backend", "apis")
    """
    try:
        # Validate session ID
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        session = session_manager.get_session(session_id)
        if not session:
            return {
                "error": f"Session not found: {session_id}",
                "status": "error"
            }

        # Check if both clusters exist
        if parent_cluster_id not in session.clusters:
            return {
                "error": f"Parent cluster not found: {parent_cluster_id}",
                "status": "error"
            }

        if child_cluster_id not in session.clusters:
            return {
                "error": f"Child cluster not found: {child_cluster_id}",
                "status": "error"
            }

        # Prevent circular nesting
        if parent_cluster_id == child_cluster_id:
            return {
                "error": "Cannot nest a cluster inside itself",
                "status": "error"
            }

        # Check for circular dependency
        current = parent_cluster_id
        while current:
            parent = session.clusters.get(current)
            if parent and parent.parent_cluster_id == child_cluster_id:
                return {
                    "error": "Circular nesting detected",
                    "status": "error"
                }
            current = parent.parent_cluster_id if parent else None

        # Set the parent
        session.clusters[child_cluster_id].parent_cluster_id = parent_cluster_id
        session.updated_at = datetime.now()

        return {
            "parent": parent_cluster_id,
            "child": child_cluster_id,
            "status": "success",
            "message": f"Nested {child_cluster_id} cluster inside {parent_cluster_id}"
        }

    except Exception as e:
        return {
            "error": f"Failed to nest clusters: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def list_clusters(session_id: str) -> Dict[str, Any]:
    """
    List all clusters in the diagram session.

    Args:
        session_id: UUID of the diagram session

    Returns:
        Dictionary with list of clusters and their hierarchy

    Example Response:
        {
            "clusters": [
                {
                    "id": "web-tier",
                    "label": "Web Servers",
                    "nodes": ["web1", "web2"],
                    "parent": null
                },
                {
                    "id": "db-cluster",
                    "label": "Databases",
                    "nodes": ["db1", "db2"],
                    "parent": "backend"
                }
            ],
            "count": 2,
            "status": "success"
        }
    """
    try:
        # Validate session ID
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        session = session_manager.get_session(session_id)
        if not session:
            return {
                "error": f"Session not found: {session_id}",
                "status": "error"
            }

        clusters_list = []
        for cluster_id, cluster in session.clusters.items():
            clusters_list.append({
                "id": cluster_id,
                "label": cluster.label,
                "nodes": cluster.nodes,
                "parent": cluster.parent_cluster_id
            })

        return {
            "clusters": clusters_list,
            "count": len(clusters_list),
            "status": "success"
        }

    except Exception as e:
        return {
            "error": f"Failed to list clusters: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def connect_bulk(
    session_id: str,
    connections: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Create multiple connections between nodes efficiently in a single operation.

    This is useful for connecting many nodes at once, like connecting all web servers
    to a load balancer or all services to a database.

    Args:
        session_id: UUID of the diagram session
        connections: List of connection specifications, each containing:
            - from_node: Source node ID (required)
            - to_node: Target node ID (required)
            - label: Optional connection label
            - color: Optional connection color
            - style: Optional style ("solid", "dashed", "dotted", "bold")

    Returns:
        Dictionary with created connections and any failures

    Example Input:
        connections=[
            {"from_node": "lb", "to_node": "web1", "label": "HTTP"},
            {"from_node": "lb", "to_node": "web2", "label": "HTTP"},
            {"from_node": "web1", "to_node": "db", "label": "SQL", "style": "dashed"},
            {"from_node": "web2", "to_node": "db", "label": "SQL", "style": "dashed"}
        ]

    Example Response:
        {
            "created_connections": 4,
            "failed_connections": [],
            "status": "success",
            "message": "Created 4 connections"
        }

    Example Usage:
        # Connect load balancer to all web servers
        connections = [
            {"from_node": "lb", "to_node": f"web{i}", "label": "HTTPS"}
            for i in range(1, 4)
        ]
        connect_bulk(session_id, connections)
    """
    try:
        # Validate session ID
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        session = session_manager.get_session(session_id)
        if not session:
            return {
                "error": f"Session not found: {session_id}",
                "status": "error"
            }

        if not connections or not isinstance(connections, list):
            return {
                "error": "Connections must be a non-empty list",
                "status": "error"
            }

        if len(connections) > 100:
            return {
                "error": "Too many connections (max 100 per bulk operation)",
                "status": "error"
            }

        created_count = 0
        failed_connections = []

        for i, conn_spec in enumerate(connections):
            try:
                if not isinstance(conn_spec, dict):
                    failed_connections.append({
                        "index": i,
                        "spec": conn_spec,
                        "error": "Connection specification must be a dictionary"
                    })
                    continue

                from_node = conn_spec.get("from_node")
                to_node = conn_spec.get("to_node")

                if not from_node or not to_node:
                    failed_connections.append({
                        "index": i,
                        "spec": conn_spec,
                        "error": "Both from_node and to_node are required"
                    })
                    continue

                # Validate nodes exist
                if from_node not in session.nodes:
                    failed_connections.append({
                        "index": i,
                        "spec": conn_spec,
                        "error": f"Source node not found: {from_node}"
                    })
                    continue

                if to_node not in session.nodes:
                    failed_connections.append({
                        "index": i,
                        "spec": conn_spec,
                        "error": f"Target node not found: {to_node}"
                    })
                    continue

                connection = ConnectionInfo(
                    from_node=str(from_node).strip(),
                    to_node=str(to_node).strip(),
                    label=str(conn_spec.get("label", "")).strip() or None,
                    color=str(conn_spec.get("color", "")).strip() or None,
                    style=str(conn_spec.get("style", "")).strip() or None
                )

                if session_manager.add_connection(session_id, connection):
                    created_count += 1
                else:
                    failed_connections.append({
                        "index": i,
                        "spec": conn_spec,
                        "error": "Failed to create connection"
                    })

            except Exception as e:
                failed_connections.append({
                    "index": i,
                    "spec": conn_spec,
                    "error": f"Error processing connection: {str(e)}"
                })

        return {
            "created_connections": created_count,
            "failed_connections": failed_connections,
            "status": "success" if not failed_connections else "partial",
            "message": f"Created {created_count} connections"
        }

    except Exception as e:
        return {
            "error": f"Failed to create bulk connections: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def get_health_status() -> Dict[str, Any]:
    """
    Get server health status and metrics for monitoring.

    Returns a comprehensive health check including:
    - Server status (healthy/degraded/warning)
    - Active session count
    - Recent error tracking
    - Performance indicators
    - Any detected issues

    Returns:
        Dictionary with health status and metrics

    Example Response:
        {
            "status": "healthy",
            "active_sessions": 5,
            "issues": [],
            "metrics": {
                "uptime_hours": "24.5",
                "error_rate": "0.5%"
            }
        }
    """
    try:
        from .metrics import metrics_collector
        health = metrics_collector.log_health_check()

        return {
            **health,
            "active_sessions": len(session_manager.sessions),
            "status": "success"
        }
    except Exception as e:
        return {
            "error": f"Failed to get health status: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def validate_architecture(session_id: str) -> Dict[str, Any]:
    """
    Validate the architectural design of a diagram for best practices.

    This tool helps ensure proper cluster boundaries, logical grouping,
    and architectural patterns are followed.

    WHAT IT CHECKS:
    1. **Cluster Organization**
       - Proper grouping of related services
       - No orphaned nodes outside clusters
       - Logical tier separation

    2. **Service Placement**
       - Databases in data tier, not frontend
       - Load balancers in frontend/DMZ
       - Proper separation of concerns

    3. **Connection Patterns**
       - No circular dependencies
       - Proper tier communication
       - Avoiding direct frontend-to-database connections

    4. **Architectural Best Practices**
       - Identifying single points of failure
       - Checking for redundancy needs
       - Ensuring proper security boundaries

    Args:
        session_id: UUID of the diagram session to validate

    Returns:
        Dictionary with:
        - valid: Boolean indicating if architecture follows best practices
        - issues: List of critical problems that should be fixed
        - warnings: List of potential problems to consider
        - suggestions: List of improvements for better architecture
        - summary: Text summary of validation results

    Example Issues Detected:
        - "Database in frontend cluster"
        - "No clusters defined for complex diagram"
        - "Circular dependency detected"
        - "Single point of failure: Database has 10+ direct connections"

    When to Use:
        - After creating initial diagram structure
        - Before finalizing and rendering
        - When diagram looks cluttered or disorganized
        - To ensure production-ready architecture patterns
    """
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return {
                "error": f"Session not found: {session_id}",
                "status": "error"
            }

        # Import validator
        from .architecture_validator import validate_architecture as run_validation

        # Run validation
        validation_results = run_validation(session)

        return {
            "session_id": session_id,
            "validation": validation_results,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to validate architecture: {str(e)}")
        return {
            "error": f"Failed to validate: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def get_metrics() -> Dict[str, Any]:
    """
    Get detailed server metrics for production monitoring.

    Provides comprehensive metrics including:
    - Operation counts and success rates
    - Session statistics
    - Node creation metrics
    - Rate limiting hits
    - Performance timing (min/max/avg)
    - Recent errors log

    Automatically saves a metrics snapshot for analysis.

    Returns:
        Dictionary with detailed metrics

    Example Response:
        {
            "server": {
                "uptime_hours": "48.2",
                "version": "1.0.0"
            },
            "sessions": {
                "active": 10,
                "total_created": 500,
                "total_expired": 450
            },
            "operations": {
                "render_diagram": {
                    "total_count": 1000,
                    "success_rate": "99.5%",
                    "avg_duration_ms": "245.3"
                }
            },
            "status": "success"
        }
    """
    try:
        from .metrics import metrics_collector
        metrics = metrics_collector.get_metrics_summary()

        # Save snapshot
        metrics_collector.save_metrics_snapshot()

        return {
            **metrics,
            "status": "success"
        }
    except Exception as e:
        return {
            "error": f"Failed to get metrics: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def cleanup_expired_sessions() -> Dict[str, Any]:
    """
    Manually trigger cleanup of expired sessions.

    Forces immediate cleanup of sessions that have exceeded their TTL.
    Useful for maintenance or when you need to free up resources immediately.

    Note: Cleanup also runs automatically every 5 minutes.

    Returns:
        Dictionary with cleanup results

    Example Response:
        {
            "sessions_cleaned": 3,
            "status": "success",
            "message": "Cleaned up 3 expired sessions"
        }
    """
    try:
        cleaned_count = 0
        if hasattr(session_manager, '_cleanup_expired_sessions'):
            cleaned_count = session_manager._cleanup_expired_sessions()

        return {
            "sessions_cleaned": cleaned_count,
            "active_sessions_remaining": len(session_manager.sessions),
            "status": "success",
            "message": f"Cleaned up {cleaned_count} expired sessions"
        }
    except Exception as e:
        return {
            "error": f"Failed to cleanup sessions: {str(e)}",
            "status": "error"
        }


@mcp.tool()
def get_session_ttl_info(session_id: str) -> Dict[str, Any]:
    """
    Get TTL (time-to-live) information for a specific session.

    Shows when a session will expire and how much time is remaining.
    Useful for monitoring session lifecycle and preventing unexpected expiration.

    Args:
        session_id: UUID of the diagram session

    Returns:
        Dictionary with TTL information

    Example Response:
        {
            "session_id": "uuid-here",
            "created_at": "2024-01-20T10:30:00",
            "last_access": "2024-01-20T11:25:00",
            "expires_at": "2024-01-20T12:25:00",
            "ttl_remaining_seconds": 1800,
            "ttl_remaining_minutes": 30,
            "status": "success"
        }
    """
    try:
        if not validate_session_id(session_id):
            return {
                "error": "Invalid session ID format",
                "status": "error"
            }

        session = session_manager.get_session(session_id)
        if not session:
            return {
                "error": f"Session not found: {session_id}",
                "status": "error"
            }

        # Get TTL information
        last_access = session_manager._session_last_access.get(
            session_id, session.created_at)
        age_seconds = (datetime.now() - last_access).total_seconds()
        ttl_remaining = max(0, session_manager.session_timeout - age_seconds)
        expires_at = last_access + \
            timedelta(seconds=session_manager.session_timeout)

        return {
            "session_id": session_id,
            "created_at": session.created_at.isoformat(),
            "last_access": last_access.isoformat(),
            "expires_at": expires_at.isoformat(),
            "ttl_remaining_seconds": int(ttl_remaining),
            "ttl_remaining_minutes": round(ttl_remaining / 60, 1),
            "is_expired": ttl_remaining <= 0,
            "status": "success"
        }
    except Exception as e:
        return {
            "error": f"Failed to get TTL info: {str(e)}",
            "status": "error"
        }


def run_server():
    """Run the MCP server with production setup"""
    import asyncio
    import sys
    import logging
    import atexit

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("mcp_diagrams")

    # Graceful shutdown handler
    def shutdown_handler():
        logger.info("Shutting down MCP Diagrams Server...")
        try:
            from .metrics import metrics_collector
            metrics_collector.save_metrics_snapshot()
            logger.info("Metrics saved")
        except:
            pass

    atexit.register(shutdown_handler)

    # Add async handler for Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    logger.info("Starting MCP Diagrams Server v1.0.0")
    mcp.run()


if __name__ == "__main__":
    run_server()
