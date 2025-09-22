# MCP Diagrams 🎨

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://github.com/modelcontextprotocol)

Create beautiful infrastructure and architecture diagrams through Model Context Protocol (MCP) with Claude. Build cloud architectures, network diagrams, and system designs using simple commands.

## 🌟 Features

- **20+ Cloud Providers**: AWS, Azure, GCP, Kubernetes, Alibaba Cloud, and more
- **2000+ Services**: Comprehensive icon library for all major cloud services
- **Session Management**: Maintain diagram state across multiple operations
- **Smart Layouts**: Automatic arrangement with customizable directions
- **Production Ready**: Rate limiting, validation, metrics, and health monitoring
- **Format Support**: PNG, SVG, PDF, and DOT output formats

## Quick Start

### Installation

#### Using uv (Recommended)
```bash
uv pip install mcp-diagrams
```

#### Using pip
```bash
pip install mcp-diagrams
```

#### From source
```bash
git clone https://github.com/vrknetha/mcp-diagrams.git
cd mcp-diagrams
uv pip install -e .
```

### Running the Server

```bash
# Using uv
uv run mcp-diagrams

# Using Python directly
python -m mcp_diagrams

# With custom output directory
MCP_DIAGRAMS_OUTPUT_DIR=~/my-diagrams uv run mcp-diagrams
```

## Configuration

### Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

#### Option 1: Using uvx (Recommended)
```json
{
  "mcpServers": {
    "mcp-diagrams": {
      "command": "uvx",
      "args": ["mcp-diagrams"],
      "env": {
        "MCP_DIAGRAMS_OUTPUT_DIR": "/Users/your-username/Documents/diagrams"
      }
    }
  }
}
```

#### Option 2: Using Python directly
```json
{
  "mcpServers": {
    "mcp-diagrams": {
      "command": "python",
      "args": ["-m", "mcp_diagrams"],
      "env": {
        "MCP_DIAGRAMS_OUTPUT_DIR": "/Users/your-username/Documents/diagrams"
      }
    }
  }
}
```

### Cursor

Add to your Cursor settings:

```json
{
  "mcp.servers": {
    "mcp-diagrams": {
      "command": "python",
      "args": ["-m", "mcp_diagrams"],
      "env": {
        "MCP_DIAGRAMS_OUTPUT_DIR": "./diagrams"
      }
    }
  }
}
```

## 📚 Usage Examples in Claude Desktop

Once configured, use natural language to create diagrams:

### Basic Web Architecture

**You:** "Create an AWS web architecture diagram with a load balancer, two web servers, and a PostgreSQL database"

**Claude:** *Creates the diagram with proper AWS icons and connections*

### Kubernetes Cluster

**You:** "Create a Kubernetes cluster diagram showing an ingress controller, service, deployment, and pods with proper connections"

**Claude:** *Generates a K8s architecture with all components properly connected*

### Complex Microservices (Using Bulk Operations v1.1.0)

**You:** "Create a microservices architecture with:
- Frontend cluster with 2 web apps
- Backend cluster with 2 API servers
- Data layer with PostgreSQL and Redis
- Connect web apps to APIs, and APIs to both database and cache"

**Claude:** *Uses bulk operations to create the entire architecture 8-10x faster than before*

### Real-World Examples

**E-commerce Platform:**
"Create an e-commerce architecture with CloudFlare CDN, AWS ALB, 3 EC2 web servers, ECS containers for microservices, RDS for main database, ElastiCache for sessions, and S3 for static assets"

**Data Pipeline:**
"Design a data pipeline with Kinesis for streaming, Lambda for processing, EMR for analytics, Redshift for data warehouse, and QuickSight for visualization"

**Multi-Cloud Setup:**
"Show a multi-cloud architecture with AWS EC2 instances, Azure Functions, GCP BigQuery, connected via VPN"

## 🛠️ Available Tools

### Session Management
- `create_diagram()` - Initialize a new diagram session
- `list_sessions()` - List all active sessions
- `get_session_state()` - Get complete session details
- `delete_session()` - Clean up a session
- `get_session_ttl_info()` - Session expiry information

### Node Operations
- `add_node()` - Add a single node
- `add_nodes_bulk()` - Add multiple nodes at once (up to 100)
- `edit_node()` - **NEW v1.4.0: Edit node properties (label, cluster, icon)**
- `edit_nodes_bulk()` - **NEW v1.4.0: Edit multiple nodes at once**
- `remove_node()` - Remove a node
- `list_nodes()` - List all nodes in session

### Connections
- `connect_nodes()` - Create a connection between nodes
- `connect_nodes_bulk()` - Create multiple connections at once
- `edit_connection()` - **NEW v1.4.0: Edit connection properties (label, style, color)**
- `edit_connections_bulk()` - **NEW v1.4.0: Edit multiple connections at once**

### Clustering
- `create_cluster()` - Create a logical grouping
- `create_clusters_bulk()` - Create multiple clusters at once
- `edit_cluster()` - **NEW v1.4.0: Edit cluster properties (label, parent)**
- `edit_clusters_bulk()` - **NEW v1.4.0: Edit multiple clusters at once**
- `add_to_cluster()` - Add nodes to a cluster
- `nest_cluster()` - Create hierarchical clusters

### Discovery
- `list_providers()` - See all 20 available providers
- `list_categories()` - List categories for a provider
- `list_services()` - List services in a category
- `search_services()` - Search across all providers
- `search_services_bulk()` - **NEW: Search multiple terms at once**
- `get_services_by_categories()` - **NEW: Get services for multiple categories**

### Rendering
- `render_diagram()` - Generate the final diagram

### Monitoring
- `get_health_status()` - Server health check
- `get_metrics()` - Performance metrics

### Validation
- `validate_architecture()` - **v1.2.0: Check diagram for best practices and issues**
  - Validates proper cluster boundaries
  - Detects architectural anti-patterns
  - Identifies single points of failure
  - Ensures proper service placement
- `validate_icon()` - **NEW v1.3.0: Check if an icon exists and get fallback suggestions**
  - Validates provider/service combinations
  - Provides intelligent fallback suggestions
  - Returns confidence levels for alternatives

## 📊 Supported Providers

| Provider | Services | Description |
|----------|----------|-------------|
| aws | 550+ | Amazon Web Services |
| azure | 232+ | Microsoft Azure |
| gcp | 109+ | Google Cloud Platform |
| alibabacloud | 131+ | Alibaba Cloud |
| k8s | 69+ | Kubernetes |
| onprem | 206+ | On-premises/Traditional |
| oci | 152+ | Oracle Cloud |
| ibm | 180+ | IBM Cloud |
| programming | 81+ | Languages & Frameworks |
| saas | 37+ | Software as a Service |

And 10 more providers! Use `list_providers()` to see all.

## 🏗️ Architecture

```
mcp-diagrams/
├── src/
│   ├── mcp_diagrams/
│   │   ├── __init__.py
│   │   ├── server.py          # Main MCP server
│   │   ├── diagram_builder.py # Diagram generation
│   │   ├── session_manager.py # Session state
│   │   ├── provider_registry.py # Service discovery
│   │   ├── models.py          # Data models
│   │   └── utils.py           # Utilities
│   └── ...
├── tests/                      # Test suite
├── examples/                   # Example diagrams
└── docs/                       # Documentation
```

## 🧪 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/vrknetha/mcp-diagrams.git
cd mcp-diagrams

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
uv pip install -e ".[dev]"
```

### Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=mcp_diagrams

# Run specific test file
uv run pytest tests/test_session_manager.py
```

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint
uv run ruff src/ tests/

# Type checking
uv run mypy src/
```

## 📦 Publishing to PyPI

### First Time Setup

1. Create account on [PyPI](https://pypi.org)
2. Create API token: Account Settings → API tokens
3. Save token securely

### Build and Upload

```bash
# Install build tools
uv pip install build twine

# Build distribution
python -m build

# Upload to TestPyPI first (recommended)
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```

### Using GitHub Actions (Automated)

See `.github/workflows/publish.yml` for automated releases on tags.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Diagrams](https://diagrams.mingrammer.com/) - The amazing Python library powering our diagrams
- [MCP](https://github.com/modelcontextprotocol) - Model Context Protocol specification
- [FastMCP](https://github.com/jlowin/fastmcp) - Fast MCP implementation for Python

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/vrknetha/mcp-diagrams/issues)
- **Discussions**: [GitHub Discussions](https://github.com/vrknetha/mcp-diagrams/discussions)
- **Email**: vrknetha@gmail.com

## 🗺️ Roadmap

- [ ] Web UI for diagram preview
- [ ] Export to Terraform/CloudFormation
- [ ] Real-time collaboration
- [ ] Custom icon support
- [ ] Diagram templates library
- [ ] Cost estimation integration

---

Made with ❤️ by the MCP Diagrams Team