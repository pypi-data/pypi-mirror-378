"""Data models for MCP Diagrams Server"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class NodeInfo(BaseModel):
    """Represents a node in the diagram"""
    id: str
    provider: str
    service: str
    label: Optional[str] = None
    cluster_id: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class ConnectionInfo(BaseModel):
    """Represents a connection between nodes"""
    from_node: str
    to_node: str
    label: Optional[str] = None
    color: Optional[str] = None
    style: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)


class ClusterInfo(BaseModel):
    """Represents a cluster/group of nodes"""
    id: str
    label: str
    parent_cluster_id: Optional[str] = None
    nodes: List[str] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)


class DiagramSession(BaseModel):
    """Complete diagram session state"""
    session_id: UUID
    name: str
    direction: str = "LR"  # LR, RL, TB, BT
    output_format: str = "png"
    graph_spacing: str = "normal"  # compact, normal, spacious, extra-spacious
    nodes: Dict[str, NodeInfo] = Field(default_factory=dict)
    connections: List[ConnectionInfo] = Field(default_factory=list)
    clusters: Dict[str, ClusterInfo] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Use Pydantic v2 serializers instead of deprecated json_encoders
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Example Diagram",
                "direction": "LR"
            }]
        }
    }