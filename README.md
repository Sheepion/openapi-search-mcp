# OpenAPI Search MCP Server

**This project was built with the assistance of [Claude Code](https://claude.ai/code), Anthropic's AI-powered coding assistant.**

<div align="center">

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/MCP-FastMCP-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Model Context Protocol (MCP) server for loading, parsing, and querying OpenAPI/Swagger documentation.

[Features](#features) • [Quick Start](#quick-start) • [Installation](#installation) • [Docker](#docker-deployment) • [Usage](#usage) • [Architecture](#architecture)

</div>

---

## Overview

OpenAPI Search MCP Server is a specialized MCP server that makes OpenAPI/Swagger documentation easily accessible to AI assistants and other MCP clients. It provides 10 powerful tools for loading, searching, and querying API specifications in multiple formats.

### Why Use This?

- **AI-Friendly API Documentation**: Make your OpenAPI specs queryable by AI assistants like Claude
- **Intelligent Search**: Multi-criteria search across paths, methods, tags, and keywords
- **Fast Lookups**: Pre-built indexes for O(1) operationId queries
- **Format Flexibility**: Auto-detects JSON and YAML formats
- **Modular Architecture**: Clean, maintainable codebase following Python best practices

---

## Features

- 🔄 **Load from URL** - Fetch OpenAPI documents from any HTTP/HTTPS endpoint
- 💾 **In-Memory Storage** - Fast access with structured document storage
- 🔍 **10 Query Tools** - Comprehensive API exploration capabilities
- 📚 **Multi-Format Support** - JSON and YAML with automatic detection
- 🚀 **Version Support** - OpenAPI 3.0.x, 3.1.x, and Swagger 2.0
- 🏗️ **Layered Architecture** - Modular design with dependency injection
- ⚡ **Fast Indexing** - Pre-built operationId and tag indexes
- 🔐 **Auth Discovery** - Extract security schemes and requirements
- 🏷️ **Tag-Based Navigation** - Browse APIs by functional categories
- 🎯 **Precise Search** - Filter by keyword, method, tag, or combinations

---

## Quick Start

```bash
# 1. Create conda environment
conda create -n openapi-search-mcp python=3.12 -y
conda activate openapi-search-mcp

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
python main.py
```

That's it! The server is now running and ready to accept MCP connections.

---

## Installation

### Prerequisites

- Python 3.12 or higher
- Conda (recommended) or venv

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/openapi-search-mcp.git
cd openapi-search-mcp
```

### Step 2: Create Virtual Environment

**Using Conda (Recommended):**

```bash
conda create -n openapi-search-mcp python=3.12 -y
conda activate openapi-search-mcp
```

**Using venv:**

```bash
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Dependencies

- **FastMCP** (>=0.2.0) - MCP server framework
- **httpx** (>=0.27.0) - Async HTTP client for fetching documents
- **PyYAML** (>=6.0) - YAML parsing support
- **Pydantic** (>=2.0.0) - Type-safe data models

---

## Docker Deployment

For quick and isolated deployment, you can use Docker.

### Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose (optional, included with Docker Desktop)

### Option 1: Using Docker Compose (Recommended)

The easiest way to deploy:

```bash
# Clone the repository
git clone https://github.com/yourusername/openapi-search-mcp.git
cd openapi-search-mcp

# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The server will be available at `http://localhost:8848`

### Option 2: Using Docker Directly

Build and run manually:

```bash
# Build the image
docker build -t openapi-search-mcp:latest .

# Run the container
docker run -d \
  --name openapi-search-mcp \
  -p 8848:8848 \
  --restart unless-stopped \
  openapi-search-mcp:latest

# View logs
docker logs -f openapi-search-mcp

# Stop and remove
docker stop openapi-search-mcp
docker rm openapi-search-mcp
```

### Docker Configuration

The Docker setup includes:

- **Base Image**: `python:3.12-slim` (lightweight)
- **Port**: 8848 (configurable via environment variable)
- **Health Check**: Automatic health monitoring
- **Resource Limits**: Configurable in `docker-compose.yml`
- **Logging**: JSON file driver with rotation

### Environment Variables

You can customize the deployment by setting environment variables:

```yaml
environment:
  - DEFAULT_HTTP_PORT=8848  # Change server port
  - PYTHONUNBUFFERED=1      # Enable real-time logs
```

### Accessing from Claude Desktop

When using Docker, update your Claude Desktop configuration to point to the HTTP endpoint:

```json
{
  "mcpServers": {
    "openapi-search": {
      "url": "http://localhost:8848"
    }
  }
}
```

---

## Configuration

### Claude Desktop Integration

To use this MCP server with Claude Desktop, add the following configuration:

**macOS/Linux:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

#### Option 1: Using Conda

```json
{
  "mcpServers": {
    "openapi-search": {
      "command": "conda",
      "args": [
        "run",
        "-n",
        "openapi-search-mcp",
        "python",
        "/absolute/path/to/openapi-search-mcp/main.py"
      ]
    }
  }
}
```

#### Option 2: Using Direct Python Path

```json
{
  "mcpServers": {
    "openapi-search": {
      "command": "/path/to/conda/envs/openapi-search-mcp/bin/python",
      "args": ["/absolute/path/to/openapi-search-mcp/main.py"]
    }
  }
}
```

After adding the configuration, restart Claude Desktop to load the MCP server.

### HTTP Mode (Standalone Server)

By default, the server runs in HTTP mode on port 8848. To customize:

Edit `main.py` line 57:

```python
# STDIO mode (for Claude Desktop)
mcp.run()

# HTTP mode with custom port
mcp.run(transport="streamable-http", port=8848)
```

---

## Usage

### Available Tools

The server provides 10 MCP tools for comprehensive API exploration:

#### 1. `load_openapi`

Load an OpenAPI document from URL and save to memory.

**Parameters:**
- `name` (string, required) - API identifier for subsequent queries
- `url` (string, required) - URL of the OpenAPI document

**Example:**

```json
{
  "name": "petstore",
  "url": "https://petstore.swagger.io/v2/swagger.json"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "API 'petstore' loaded successfully",
  "info": {
    "title": "Swagger Petstore",
    "version": "1.0.0"
  },
  "paths_count": 14,
  "tags_count": 3
}
```

---

#### 2. `list_apis`

List all loaded APIs with basic information.

**Parameters:** None

**Response:**

```json
{
  "count": 2,
  "apis": [
    {
      "name": "petstore",
      "title": "Swagger Petstore",
      "version": "1.0.0",
      "paths_count": 14
    }
  ]
}
```

---

#### 3. `get_path_details`

Get complete documentation for a specific API path.

**Parameters:**
- `name` (string, required) - API name
- `path` (string, required) - API path, e.g., `/users/{id}`

**Example:**

```json
{
  "name": "petstore",
  "path": "/pet/{petId}"
}
```

**Response:**

```json
{
  "path": "/pet/{petId}",
  "methods": {
    "get": {
      "summary": "Find pet by ID",
      "operationId": "getPetById",
      "parameters": [...],
      "responses": {...}
    }
  }
}
```

---

#### 4. `list_all_paths`

List all paths in an API.

**Parameters:**
- `name` (string, required) - API name

**Response:**

```json
{
  "count": 14,
  "paths": [
    {
      "path": "/pet",
      "methods": ["post", "put"]
    },
    {
      "path": "/pet/{petId}",
      "methods": ["get", "post", "delete"]
    }
  ]
}
```

---

#### 5. `get_operation_by_id`

Fast lookup by operationId.

**Parameters:**
- `name` (string, required) - API name
- `operation_id` (string, required) - operationId, e.g., `getUserById`

**Example:**

```json
{
  "name": "petstore",
  "operation_id": "getPetById"
}
```

**Response:**

```json
{
  "operation_id": "getPetById",
  "path": "/pet/{petId}",
  "method": "get",
  "details": {
    "summary": "Find pet by ID",
    "parameters": [...],
    "responses": {...}
  }
}
```

---

#### 6. `search_endpoints`

Search endpoints by keyword, method, tag, or combinations.

**Parameters:**
- `name` (string, required) - API name
- `keyword` (string, optional) - Search in path, summary, description
- `method` (string, optional) - HTTP method filter (GET, POST, etc.)
- `tag` (string, optional) - Tag filter

**Example:**

```json
{
  "name": "petstore",
  "keyword": "pet",
  "method": "GET"
}
```

**Response:**

```json
{
  "count": 3,
  "results": [
    {
      "path": "/pet/{petId}",
      "method": "get",
      "operationId": "getPetById",
      "summary": "Find pet by ID"
    }
  ]
}
```

---

#### 7. `list_tags`

List all tags in an API.

**Parameters:**
- `name` (string, required) - API name

**Response:**

```json
{
  "count": 3,
  "tags": [
    {
      "name": "pet",
      "description": "Everything about your Pets"
    }
  ]
}
```

---

#### 8. `get_endpoints_by_tag`

Get all endpoints with a specific tag (overview only).

**Parameters:**
- `name` (string, required) - API name
- `tag` (string, required) - Tag name

**Example:**

```json
{
  "name": "petstore",
  "tag": "pet"
}
```

**Response:**

```json
{
  "tag": "pet",
  "count": 8,
  "endpoints": [
    {
      "path": "/pet",
      "method": "post",
      "operationId": "addPet",
      "summary": "Add a new pet"
    }
  ]
}
```

---

#### 9. `get_schema_details`

Get data model definition from components/schemas.

**Parameters:**
- `name` (string, required) - API name
- `schema_name` (string, required) - Schema name, e.g., `User`, `Pet`

**Example:**

```json
{
  "name": "petstore",
  "schema_name": "Pet"
}
```

**Response:**

```json
{
  "schema_name": "Pet",
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "name": {
      "type": "string"
    }
  },
  "required": ["name"]
}
```

---

#### 10. `get_auth_info`

Get authentication configuration.

**Parameters:**
- `name` (string, required) - API name

**Response:**

```json
{
  "security_schemes": {
    "bearerAuth": {
      "type": "http",
      "scheme": "bearer"
    }
  },
  "global_security": [
    {"bearerAuth": []}
  ]
}
```

---

## Typical Workflows

### Workflow 1: Exploring a New API

```bash
# Step 1: Load the API
load_openapi(name="petstore", url="https://petstore.swagger.io/v2/swagger.json")

# Step 2: See what tags/categories exist
list_tags(name="petstore")

# Step 3: Explore endpoints in a category
get_endpoints_by_tag(name="petstore", tag="pet")

# Step 4: Get detailed info for a specific endpoint
get_path_details(name="petstore", path="/pet/{petId}")

# Step 5: Check the data models
get_schema_details(name="petstore", schema_name="Pet")
```

### Workflow 2: Finding Specific Functionality

```bash
# Search for user-related POST endpoints
search_endpoints(name="api", keyword="user", method="POST")

# Quick lookup by operationId
get_operation_by_id(name="api", operation_id="createUser")

# Get full path details
get_path_details(name="api", path="/users")
```

### Workflow 3: Understanding Authentication

```bash
# Check what auth methods are required
get_auth_info(name="api")
```

---

## Architecture

OpenAPI Search MCP follows a clean layered architecture inspired by enterprise patterns:

```
┌─────────────────────────────────────┐
│         main.py (Entry)             │  → Application initialization
├─────────────────────────────────────┤
│    Tools Layer (src/tools/)         │  → MCP tool definitions
├─────────────────────────────────────┤
│   Services Layer (src/services/)    │  → Business logic
├─────────────────────────────────────┤
│  Storage Layer (src/storage.py)     │  → Data access
├─────────────────────────────────────┤
│ Loaders/Indexers (src/loaders/,     │  → Utilities
│                   src/indexers/)    │
├─────────────────────────────────────┤
│  Models (src/models/)               │  → Data structures
├─────────────────────────────────────┤
│  Config (src/config.py)             │  → Constants
└─────────────────────────────────────┘
```

### Key Design Principles

1. **Separation of Concerns** - Each layer has a single responsibility
2. **Dependency Injection** - Services receive dependencies via constructor
3. **Type Safety** - Pydantic models throughout
4. **Interface-Oriented** - Clear contracts between layers
5. **Testability** - Each layer can be unit tested independently

### Layers Explained

- **Config Layer** - Centralized constants and error messages
- **Models Layer** - Type-safe data structures with validation
- **Storage Layer** - In-memory document storage with consistent error handling
- **Loaders Layer** - HTTP fetching and format detection (JSON/YAML)
- **Indexers Layer** - Building reverse indexes for fast lookups
- **Services Layer** - Business logic (5 services: API, Path, Schema, Search, Tag)
- **Tools Layer** - MCP tool registrations (3 modules)
- **Entry Layer** - Application initialization with dependency wiring

---

## Project Structure

```
openapi-search-mcp/
├── main.py                          # Entry point (~50 lines)
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── README.zh.md                     # Chinese documentation
├── CLAUDE.md                        # Claude Code guidance
├── DESIGN.md                        # Detailed design docs
├── src/                             # Source code
│   ├── config.py                   # Configuration constants
│   ├── storage.py                  # Data storage layer
│   ├── models/                     # Data models
│   │   └── openapi_document.py    # Pydantic model
│   ├── loaders/                    # Document loaders
│   │   └── openapi_loader.py      # URL loading & format detection
│   ├── indexers/                   # Index builders
│   │   └── operation_indexer.py   # operationId and tag indexing
│   ├── services/                   # Business logic
│   │   ├── api_service.py         # API loading and listing
│   │   ├── path_service.py        # Path queries
│   │   ├── schema_service.py      # Schema and auth queries
│   │   ├── search_service.py      # Endpoint search
│   │   └── tag_service.py         # Tag queries
│   └── tools/                      # MCP tool definitions
│       ├── loading_tools.py       # load_openapi, list_apis
│       ├── query_tools.py         # path, operation, schema queries
│       └── search_tools.py        # search, tag queries
└── tests/                          # Test files
```

---

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.12+ | Runtime environment |
| FastMCP | >=0.2.0 | MCP server framework |
| httpx | >=0.27.0 | Async HTTP client for fetching documents |
| PyYAML | >=6.0 | YAML format parsing |
| Pydantic | >=2.0.0 | Type-safe data models and validation |

---

## Supported OpenAPI Versions

- ✅ OpenAPI 3.0.x
- ✅ OpenAPI 3.1.x
- ✅ Swagger 2.0

Both JSON and YAML formats are automatically detected and supported.

---

## FAQ

### How do I load a local OpenAPI file?

Currently, only URL loading is supported. You can:
1. Use a local file server: `python -m http.server 8000`
2. Access via: `http://localhost:8000/openapi.json`

Future versions will support direct file path loading.

### Are documents persisted between restarts?

No, documents are stored in memory only. After server restart, you'll need to reload your OpenAPI documents. This design prioritizes simplicity and speed over persistence.

### How do I switch between STDIO and HTTP mode?

Edit `main.py` line 57:

```python
# STDIO mode (for Claude Desktop)
mcp.run()

# HTTP mode (standalone server)
mcp.run(transport="streamable-http", port=8848)
```

### Can I load multiple versions of the same API?

Yes, just use different names:

```python
load_openapi(name="petstore-v1", url="...")
load_openapi(name="petstore-v2", url="...")
```

### What happens if I load an API with an existing name?

The new document will overwrite the existing one. The server will log a warning message.

---

## Development

### Running Tests

```bash
pytest tests/
```

### Code Structure

See [CLAUDE.md](./CLAUDE.md) for detailed architecture documentation and development guidelines.

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## License

MIT License - see [LICENSE](./LICENSE) for details.

---

## Acknowledgments

**This project was developed with the assistance of [Claude Code](https://claude.ai/code)**, Anthropic's AI-powered coding assistant. Claude Code helped with:

- Architectural design and refactoring from monolithic to layered structure
- Implementation of the service layer with dependency injection
- Documentation and code organization
- Best practices for Python enterprise development

The project demonstrates the power of human-AI collaboration in software development.

---

## Links

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

**Built with Claude Code • OpenAPI Search MCP Server • MIT License**
