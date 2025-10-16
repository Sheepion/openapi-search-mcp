#!/usr/bin/env python3
"""
OpenAPI Search MCP Server
A MCP server for loading, parsing and querying OpenAPI documents
"""

import json
import yaml
import httpx
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP

# Create FastMCP server instance
mcp = FastMCP("OpenAPI Search MCP")

# Global memory storage
openapi_docs: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# Helper Functions
# ============================================================================

async def load_openapi_doc(url: str) -> Dict[str, Any]:
    """Load OpenAPI document from URL (supports JSON and YAML)"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()

        content_type = response.headers.get('content-type', '').lower()

        # Try to determine format by Content-Type or file extension
        if 'json' in content_type or url.endswith('.json'):
            return response.json()

        if 'yaml' in content_type or url.endswith(('.yaml', '.yml')):
            return yaml.safe_load(response.text)

        # Auto-detect format
        try:
            return response.json()
        except json.JSONDecodeError:
            return yaml.safe_load(response.text)


def build_operation_index(paths: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """Build index from operationId to path and method"""
    index = {}
    http_methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace']

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        for method in http_methods:
            if method in path_item:
                operation = path_item[method]
                if isinstance(operation, dict):
                    operation_id = operation.get('operationId')
                    if operation_id:
                        index[operation_id] = {
                            'path': path,
                            'method': method
                        }

    return index


def extract_tags_from_doc(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract all tags from document"""
    tags = []

    # Prefer root-level tags definition
    if 'tags' in doc and isinstance(doc['tags'], list):
        return doc['tags']

    # Otherwise extract unique tags from all operations
    unique_tags = set()
    paths = doc.get('paths', {})
    http_methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace']

    for path_item in paths.values():
        if not isinstance(path_item, dict):
            continue

        for method in http_methods:
            if method in path_item:
                operation = path_item[method]
                if isinstance(operation, dict) and 'tags' in operation:
                    for tag in operation['tags']:
                        unique_tags.add(tag)

    # Convert to list of tag objects
    for tag in sorted(unique_tags):
        tags.append({'name': tag})

    return tags


# ============================================================================
# MCP Tools Definition
# ============================================================================

@mcp.tool()
async def load_openapi(name: str, url: str) -> Dict[str, Any]:
    """
    Load OpenAPI document from URL and save to memory

    Args:
        name: API name for later queries
        url: URL of the OpenAPI document

    Returns:
        Loading status and document basic info
    """
    try:
        # Load document
        doc = await load_openapi_doc(url)

        # Validate required fields
        if 'openapi' not in doc and 'swagger' not in doc:
            return {
                "error": True,
                "message": "Invalid OpenAPI document: missing 'openapi' or 'swagger' field"
            }

        if 'info' not in doc:
            return {
                "error": True,
                "message": "Invalid OpenAPI document: missing 'info' field"
            }

        if 'paths' not in doc:
            return {
                "error": True,
                "message": "Invalid OpenAPI document: missing 'paths' field"
            }

        # Build indexes
        operation_index = build_operation_index(doc.get('paths', {}))
        tags = extract_tags_from_doc(doc)

        # Save to memory
        openapi_docs[name] = {
            'raw': doc,
            'info': doc.get('info', {}),
            'servers': doc.get('servers', []),
            'paths': doc.get('paths', {}),
            'components': doc.get('components', {}),
            'tags': tags,
            'operation_index': operation_index
        }

        # Return success info
        return {
            "status": "success",
            "message": f"API '{name}' loaded successfully",
            "info": {
                "title": doc['info'].get('title', 'N/A'),
                "version": doc['info'].get('version', 'N/A'),
                "description": doc['info'].get('description', '')
            },
            "servers": [s.get('url') if isinstance(s, dict) else str(s) for s in doc.get('servers', [])],
            "paths_count": len(doc.get('paths', {})),
            "tags_count": len(tags)
        }

    except httpx.HTTPError as e:
        return {
            "error": True,
            "message": f"Failed to fetch URL: {str(e)}"
        }
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        return {
            "error": True,
            "message": f"Failed to parse document: {str(e)}"
        }
    except Exception as e:
        return {
            "error": True,
            "message": f"Unexpected error: {str(e)}"
        }


@mcp.tool()
def list_apis() -> Dict[str, Any]:
    """
    List all loaded APIs with basic info

    Returns:
        List of all loaded APIs
    """
    apis = []

    for name, data in openapi_docs.items():
        info = data.get('info', {})
        apis.append({
            "name": name,
            "title": info.get('title', 'N/A'),
            "version": info.get('version', 'N/A'),
            "description": info.get('description', ''),
            "servers": [s.get('url') if isinstance(s, dict) else str(s) for s in data.get('servers', [])],
            "paths_count": len(data.get('paths', {})),
            "tags_count": len(data.get('tags', []))
        })

    return {
        "count": len(apis),
        "apis": apis
    }


@mcp.tool()
def get_path_details(name: str, path: str) -> Dict[str, Any]:
    """
    Get complete documentation for a specific path

    Args:
        name: API name
        path: API path like /users/{id}

    Returns:
        All HTTP methods and details for the path
    """
    if name not in openapi_docs:
        available = ', '.join(openapi_docs.keys()) if openapi_docs else 'none'
        return {
            "error": True,
            "message": f"API '{name}' not found. Available APIs: {available}"
        }

    paths = openapi_docs[name].get('paths', {})

    if path not in paths:
        return {
            "error": True,
            "message": f"Path '{path}' not found in API '{name}'"
        }

    path_item = paths[path]
    http_methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace']
    methods = {}

    for method in http_methods:
        if method in path_item:
            methods[method] = path_item[method]

    return {
        "path": path,
        "methods": methods
    }


@mcp.tool()
def get_auth_info(name: str) -> Dict[str, Any]:
    """
    Get authentication configuration for an API

    Args:
        name: API name

    Returns:
        Detailed security schemes configuration
    """
    if name not in openapi_docs:
        available = ', '.join(openapi_docs.keys()) if openapi_docs else 'none'
        return {
            "error": True,
            "message": f"API '{name}' not found. Available APIs: {available}"
        }

    doc = openapi_docs[name]['raw']
    components = openapi_docs[name].get('components', {})

    security_schemes = components.get('securitySchemes', {})
    global_security = doc.get('security', [])

    return {
        "security_schemes": security_schemes,
        "global_security": global_security
    }


@mcp.tool()
def search_endpoints(
    name: str,
    keyword: Optional[str] = None,
    method: Optional[str] = None,
    tag: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search endpoints by path, method, tag, or keyword

    Args:
        name: API name
        keyword: Search keyword matching path, summary, description (optional)
        method: HTTP method filter like GET, POST (optional)
        tag: Tag filter (optional)

    Returns:
        List of matching endpoints
    """
    if name not in openapi_docs:
        available = ', '.join(openapi_docs.keys()) if openapi_docs else 'none'
        return {
            "error": True,
            "message": f"API '{name}' not found. Available APIs: {available}"
        }

    paths = openapi_docs[name].get('paths', {})
    results = []
    http_methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace']

    # Normalize method parameter
    if method:
        method = method.lower()

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        for http_method in http_methods:
            if http_method not in path_item:
                continue

            operation = path_item[http_method]
            if not isinstance(operation, dict):
                continue

            # Apply filters
            # 1. HTTP method filter
            if method and http_method != method:
                continue

            # 2. Tag filter
            if tag:
                operation_tags = operation.get('tags', [])
                if tag not in operation_tags:
                    continue

            # 3. Keyword filter
            if keyword:
                keyword_lower = keyword.lower()
                summary = operation.get('summary', '').lower()
                description = operation.get('description', '').lower()
                path_lower = path.lower()

                if not (keyword_lower in path_lower or
                       keyword_lower in summary or
                       keyword_lower in description):
                    continue

            # Match successful, add to results
            results.append({
                "path": path,
                "method": http_method,
                "operationId": operation.get('operationId', ''),
                "summary": operation.get('summary', ''),
                "tags": operation.get('tags', [])
            })

    return {
        "count": len(results),
        "results": results
    }


@mcp.tool()
def list_all_paths(name: str) -> Dict[str, Any]:
    """
    List all API paths

    Args:
        name: API name

    Returns:
        All paths and supported HTTP methods
    """
    if name not in openapi_docs:
        available = ', '.join(openapi_docs.keys()) if openapi_docs else 'none'
        return {
            "error": True,
            "message": f"API '{name}' not found. Available APIs: {available}"
        }

    paths = openapi_docs[name].get('paths', {})
    result = []
    http_methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace']

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        methods = [m for m in http_methods if m in path_item]
        result.append({
            "path": path,
            "methods": methods
        })

    return {
        "count": len(result),
        "paths": result
    }


@mcp.tool()
def get_schema_details(name: str, schema_name: str) -> Dict[str, Any]:
    """
    Get data model definition from components/schemas

    Args:
        name: API name
        schema_name: Schema name like User, Pet

    Returns:
        Detailed schema definition
    """
    if name not in openapi_docs:
        available = ', '.join(openapi_docs.keys()) if openapi_docs else 'none'
        return {
            "error": True,
            "message": f"API '{name}' not found. Available APIs: {available}"
        }

    components = openapi_docs[name].get('components', {})
    schemas = components.get('schemas', {})

    if schema_name not in schemas:
        available = ', '.join(schemas.keys()) if schemas else 'none'
        return {
            "error": True,
            "message": f"Schema '{schema_name}' not found in API '{name}'. Available schemas: {available}"
        }

    schema = schemas[schema_name]

    return {
        "schema_name": schema_name,
        **schema
    }


@mcp.tool()
def get_operation_by_id(name: str, operation_id: str) -> Dict[str, Any]:
    """
    Quickly query endpoint by operationId

    Args:
        name: API name
        operation_id: operationId like getUserById

    Returns:
        Complete operation information
    """
    if name not in openapi_docs:
        available = ', '.join(openapi_docs.keys()) if openapi_docs else 'none'
        return {
            "error": True,
            "message": f"API '{name}' not found. Available APIs: {available}"
        }

    operation_index = openapi_docs[name].get('operation_index', {})

    if operation_id not in operation_index:
        return {
            "error": True,
            "message": f"Operation ID '{operation_id}' not found in API '{name}'"
        }

    index_entry = operation_index[operation_id]
    path = index_entry['path']
    method = index_entry['method']

    paths = openapi_docs[name].get('paths', {})
    operation = paths[path][method]

    return {
        "operation_id": operation_id,
        "path": path,
        "method": method,
        "details": operation
    }


@mcp.tool()
def list_tags(name: str) -> Dict[str, Any]:
    """
    List all tags for an API

    Args:
        name: API name

    Returns:
        List of all tags with names and descriptions
    """
    if name not in openapi_docs:
        available = ', '.join(openapi_docs.keys()) if openapi_docs else 'none'
        return {
            "error": True,
            "message": f"API '{name}' not found. Available APIs: {available}"
        }

    tags = openapi_docs[name].get('tags', [])

    return {
        "count": len(tags),
        "tags": tags
    }


@mcp.tool()
def get_endpoints_by_tag(name: str, tag: str) -> Dict[str, Any]:
    """
    Get endpoints list by tag (overview only)

    Args:
        name: API name
        tag: Tag name

    Returns:
        Overview of all endpoints under the tag
    """
    if name not in openapi_docs:
        available = ', '.join(openapi_docs.keys()) if openapi_docs else 'none'
        return {
            "error": True,
            "message": f"API '{name}' not found. Available APIs: {available}"
        }

    paths = openapi_docs[name].get('paths', {})
    endpoints = []
    http_methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace']

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        for method in http_methods:
            if method not in path_item:
                continue

            operation = path_item[method]
            if not isinstance(operation, dict):
                continue

            operation_tags = operation.get('tags', [])
            if tag in operation_tags:
                endpoints.append({
                    "path": path,
                    "method": method,
                    "operationId": operation.get('operationId', ''),
                    "summary": operation.get('summary', '')
                })

    return {
        "tag": tag,
        "count": len(endpoints),
        "endpoints": endpoints
    }


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    # Start MCP server in HTTP mode
    # Default port is 8080
    # For stdio mode use: mcp.run()
    mcp.run(transport="streamable-http", port=8848)
