#!/usr/bin/env python3
"""
OpenAPI Search MCP Server
A MCP server for loading, parsing and querying OpenAPI documents

Entry point for the server - all logic is organized in the src/ directory
"""

from fastmcp import FastMCP
from src.config import DEFAULT_HTTP_PORT
from src.storage import OpenAPIStorage
from src.services.api_service import ApiService
from src.services.path_service import PathService
from src.services.schema_service import SchemaService
from src.services.search_service import SearchService
from src.services.tag_service import TagService
from src.tools.loading_tools import register_loading_tools
from src.tools.query_tools import register_query_tools
from src.tools.search_tools import register_search_tools


def create_app() -> FastMCP:
    """
    Create and configure the FastMCP application.

    Returns:
        Configured FastMCP instance
    """
    # Create FastMCP server instance
    mcp = FastMCP("OpenAPI Search MCP")

    # Initialize storage layer
    storage = OpenAPIStorage()

    # Initialize service layer (with dependency injection)
    api_service = ApiService(storage)
    path_service = PathService(storage)
    schema_service = SchemaService(storage)
    search_service = SearchService(storage)
    tag_service = TagService(storage)

    # Register all MCP tools
    register_loading_tools(mcp, api_service)
    register_query_tools(mcp, path_service, schema_service)
    register_search_tools(mcp, search_service, tag_service)

    return mcp


if __name__ == "__main__":
    # Create the application
    mcp = create_app()

    # Start MCP server
    # For STDIO mode (Claude Desktop): mcp.run()
    # For HTTP mode: mcp.run(transport="streamable-http", port=DEFAULT_HTTP_PORT)
    mcp.run(transport="streamable-http", port=DEFAULT_HTTP_PORT)
