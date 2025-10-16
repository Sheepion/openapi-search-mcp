# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an OpenAPI Search MCP Server - a Model Context Protocol server that loads, parses, and provides query tools for OpenAPI/Swagger documents. It uses a modular, layered architecture with clear separation of concerns.

## Environment Setup

```bash
# Create and activate conda environment
conda create -n openapi-search-mcp python=3.12 -y
conda activate openapi-search-mcp

# Install dependencies
pip install -r requirements.txt
```

## Running the Server

### STDIO Mode (for Claude Desktop integration)
```bash
conda activate openapi-search-mcp
python main.py
```

Edit `main.py` line 52 to use:
```python
mcp.run()  # STDIO mode
```

### HTTP Mode (standalone server)
```bash
conda activate openapi-search-mcp
python main.py
```

Edit `main.py` line 52 to use:
```python
mcp.run(transport="streamable-http", port=DEFAULT_HTTP_PORT)  # HTTP mode (default)
```

## Architecture

### Project Structure

```
openapi-search-mcp/
├── main.py                          # Entry point (~50 lines)
├── requirements.txt
├── README.zh.md
├── CLAUDE.md
├── DESIGN.md
├── main.py.backup                   # Original monolithic version
├── src/                             # Source code
│   ├── __init__.py
│   ├── config.py                   # Configuration constants
│   ├── storage.py                  # Data storage layer
│   ├── models/                     # Data models
│   │   ├── __init__.py
│   │   └── openapi_document.py    # Pydantic model for OpenAPI docs
│   ├── loaders/                    # Document loaders
│   │   ├── __init__.py
│   │   └── openapi_loader.py      # URL loading and format detection
│   ├── indexers/                   # Index builders
│   │   ├── __init__.py
│   │   └── operation_indexer.py   # operationId and tag indexing
│   ├── services/                   # Business logic layer
│   │   ├── __init__.py
│   │   ├── api_service.py         # API loading and listing
│   │   ├── path_service.py        # Path queries
│   │   ├── schema_service.py      # Schema and auth queries
│   │   ├── search_service.py      # Endpoint search
│   │   └── tag_service.py         # Tag queries
│   └── tools/                      # MCP tool definitions
│       ├── __init__.py
│       ├── loading_tools.py       # load_openapi, list_apis
│       ├── query_tools.py         # path, operation, schema queries
│       └── search_tools.py        # search, tag queries
└── tests/
    └── __init__.py
```

### Layered Architecture

The codebase follows a clean layered architecture:

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

### Module Responsibilities

#### 1. Configuration Layer (`src/config.py`)
- **Purpose**: Centralized configuration constants
- **Contents**:
  - HTTP method list (`HTTP_METHODS`)
  - Timeout settings (`HTTP_TIMEOUT`)
  - Error message templates (e.g., `ERROR_API_NOT_FOUND`)
- **Design**: Eliminates magic strings and duplicate constants

#### 2. Data Models Layer (`src/models/`)
- **Purpose**: Type-safe data structures using Pydantic
- **Key Model**: `OpenAPIDocument`
  - Represents parsed and indexed OpenAPI document
  - Provides validation and serialization
  - Factory method: `from_raw_document()`
- **Benefits**: Type safety, auto-validation, clear structure

#### 3. Storage Layer (`src/storage.py`)
- **Purpose**: Unified in-memory data access
- **Class**: `OpenAPIStorage`
- **Methods**:
  - `add()`: Store a document
  - `get()`: Retrieve a document
  - `exists()`: Check if document exists
  - `list_all()`: Get all documents
  - `get_or_error()`: Get document or return formatted error
- **Design**: Encapsulates storage logic, provides consistent error handling

#### 4. Loaders Layer (`src/loaders/`)
- **Purpose**: Load and parse OpenAPI documents from URLs
- **Class**: `OpenAPILoader`
- **Methods**:
  - `load_from_url()`: Fetch document via HTTP
  - `_parse_response()`: Auto-detect JSON/YAML format
  - `validate_document()`: Validate OpenAPI structure
- **Features**:
  - Content-Type detection
  - URL extension detection (.json, .yaml, .yml)
  - Fallback format detection (try JSON, then YAML)

#### 5. Indexers Layer (`src/indexers/`)
- **Purpose**: Build indexes for fast lookups
- **Class**: `OperationIndexer`
- **Methods**:
  - `build_operation_index()`: Create operationId → {path, method} mapping
  - `extract_tags()`: Extract tags from document
- **Strategy**: Prefers root-level tags, falls back to extracting from operations

#### 6. Services Layer (`src/services/`)
Each service handles a specific domain of business logic:

- **`ApiService`**: Load and manage APIs
  - `load_openapi()`: Orchestrate loading, validation, indexing, storage
  - `list_apis()`: List all loaded APIs with metadata

- **`PathService`**: Query paths and operations
  - `get_path_details()`: Get all methods for a path
  - `list_all_paths()`: List all paths
  - `get_operation_by_id()`: Fast operationId lookup

- **`SchemaService`**: Query schemas and auth
  - `get_schema_details()`: Get schema from components/schemas
  - `get_auth_info()`: Get securitySchemes and global security

- **`SearchService`**: Search endpoints
  - `search_endpoints()`: Multi-criteria search (keyword, method, tag)

- **`TagService`**: Query tags
  - `list_tags()`: List all tags
  - `get_endpoints_by_tag()`: Get endpoints by tag

**Design Principle**: All services receive `OpenAPIStorage` via dependency injection

#### 7. Tools Layer (`src/tools/`)
MCP tool registration functions that wire services to FastMCP:

- **`loading_tools.py`**: `load_openapi`, `list_apis`
- **`query_tools.py`**: `get_path_details`, `list_all_paths`, `get_operation_by_id`, `get_schema_details`, `get_auth_info`
- **`search_tools.py`**: `search_endpoints`, `list_tags`, `get_endpoints_by_tag`

**Pattern**: Each registration function receives `mcp` and required services, defines tool functions inline using `@mcp.tool()` decorator

#### 8. Entry Point (`main.py`)
- **Purpose**: Application initialization and startup
- **Function**: `create_app()`
  1. Create FastMCP instance
  2. Initialize storage layer
  3. Initialize service layer (with dependency injection)
  4. Register all tools
  5. Return configured MCP instance
- **Design**: Clean separation, easily testable

## Tool Categories

### Loading & Discovery
- `load_openapi(name, url)` - Load and parse OpenAPI document from URL
- `list_apis()` - List all loaded APIs with metadata

### Path Querying
- `list_all_paths(name)` - Get all paths and their HTTP methods
- `get_path_details(name, path)` - Get complete documentation for a specific path
- `get_operation_by_id(name, operation_id)` - Fast lookup by operationId

### Search & Filter
- `search_endpoints(name, keyword?, method?, tag?)` - Multi-criteria search
- `list_tags(name)` - List all tags in the API
- `get_endpoints_by_tag(name, tag)` - Get all endpoints with specific tag

### Schema & Auth
- `get_schema_details(name, schema_name)` - Get data model from components/schemas
- `get_auth_info(name)` - Get securitySchemes and global security config

## Typical Workflow Patterns

### Exploring a New API
```
1. load_openapi(name="petstore", url="...")
2. list_tags(name="petstore")
3. get_endpoints_by_tag(name="petstore", tag="pets")
4. get_path_details(name="petstore", path="/pets/{petId}")
5. get_schema_details(name="petstore", schema_name="Pet")
```

### Finding Specific Endpoints
```
1. search_endpoints(name="api", keyword="user", method="POST")
2. get_operation_by_id(name="api", operation_id="createUser")
3. get_path_details(name="api", path="/users")
```

### Understanding Authentication
```
1. get_auth_info(name="api")  # Returns securitySchemes + global security
```

## Key Implementation Details

### 1. Dependency Injection Pattern
Services receive their dependencies via constructor:
```python
storage = OpenAPIStorage()
api_service = ApiService(storage)  # Inject storage
path_service = PathService(storage)  # Inject storage
```

### 2. Unified Error Handling
`OpenAPIStorage.get_or_error()` provides consistent error responses:
```python
doc_data, error = self.storage.get_or_error(name)
if error:
    return error  # Already formatted
```

### 3. Format Detection (src/loaders/openapi_loader.py)
Priority order:
1. Content-Type header (`json` or `yaml`)
2. URL file extension (`.json`, `.yaml`, `.yml`)
3. Try JSON parsing first
4. Fall back to YAML parsing

### 4. Operation Indexing (src/indexers/operation_indexer.py)
Builds reverse index for O(1) operationId lookups:
```python
{
    "getUserById": {"path": "/users/{id}", "method": "get"}
}
```

### 5. Tag Extraction (src/indexers/operation_indexer.py)
1. Prefer root-level `tags` array if present
2. Otherwise extract unique tags from all operations
3. Return sorted list of tag objects

## Testing

Use public OpenAPI documents for testing:

```python
# Load Swagger Petstore
load_openapi(name="petstore", url="https://petstore.swagger.io/v2/swagger.json")

# Test all tool categories
list_apis()
list_tags(name="petstore")
get_endpoints_by_tag(name="petstore", tag="pet")
search_endpoints(name="petstore", keyword="pet", method="get")
get_operation_by_id(name="petstore", operation_id="getPetById")
get_path_details(name="petstore", path="/pet/{petId}")
get_schema_details(name="petstore", schema_name="Pet")
get_auth_info(name="petstore")
```

## Supported Formats

- OpenAPI 3.0.x
- OpenAPI 3.1.x
- Swagger 2.0

Supports both JSON and YAML formats via auto-detection.

## Important Notes

- Documents are **only stored in memory** - server restart requires reloading
- Loading a document with an existing name **overwrites** the previous one
- The server is **stateful** when running in HTTP mode (stateless_http=False)
- All HTTP method checks are case-insensitive (normalized to lowercase)
- Path parameters use OpenAPI syntax: `/users/{id}` not `/users/:id`

## Modifying the Codebase

### Adding a New Tool
1. Identify which service should handle the logic
2. Add method to appropriate service in `src/services/`
3. Add tool definition in appropriate tool file in `src/tools/`
4. Tool will be auto-registered via `create_app()` in `main.py`

### Adding a New Service
1. Create service file in `src/services/`
2. Implement service class with `__init__(self, storage: OpenAPIStorage)`
3. Import in `main.py`
4. Instantiate in `create_app()` with storage injection
5. Pass to tool registration functions

### Adding Configuration
1. Add constant to `src/config.py`
2. Import where needed: `from src.config import CONSTANT_NAME`

## Benefits of This Architecture

1. **Maintainability**: Clear separation of concerns, easy to locate code
2. **Testability**: Each layer can be unit tested independently
3. **Extensibility**: Add features without modifying existing code
4. **Reusability**: No duplicate code (constants, error handling, etc.)
5. **Type Safety**: Pydantic models + complete type annotations
6. **Readability**: Small, focused files instead of one 571-line file
