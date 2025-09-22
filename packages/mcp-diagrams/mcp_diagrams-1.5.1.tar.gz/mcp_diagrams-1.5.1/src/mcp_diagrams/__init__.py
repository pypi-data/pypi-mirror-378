"""MCP Diagrams Server - Architecture Diagram Creation via MCP Protocol

A Model Context Protocol (MCP) server that enables AI assistants to create
cloud architecture diagrams programmatically using the Python Diagrams library.

Features:
- Multi-provider support (AWS, Azure, GCP, Kubernetes, and 20+ providers)
- Incremental diagram building through tool calls
- Session management for maintaining diagram state
- Dynamic provider and service discovery
- Multiple output formats (PNG, SVG, PDF, DOT)
- Support for clusters and complex layouts

Example usage:
    from src.server import run_server
    run_server()

Or run as a module:
    python -m src
"""

__version__ = "1.0.0"
__author__ = "MCP Diagrams Team"
__email__ = "info@mcp-diagrams.com"

# Don't import other modules here to avoid circular imports
# when running as a module

__all__ = [
    "__version__",
    "__author__",
    "__email__",
]