#!/usr/bin/env python3
"""
OpenAPI Search MCP Server
A MCP server for loading, parsing and querying OpenAPI documents

Entry point for the server - all logic is organized in the src/ directory
"""

import logging
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from src.config import DEFAULT_HTTP_HOST, DEFAULT_HTTP_PORT
from src.storage import OpenAPIStorage
from src.services.api_service import ApiService
from src.services.path_service import PathService
from src.services.schema_service import SchemaService
from src.services.search_service import SearchService
from src.services.tag_service import TagService
from src.tools.loading_tools import register_loading_tools
from src.tools.query_tools import register_query_tools
from src.tools.search_tools import register_search_tools


class HealthCheckFilter(logging.Filter):
    """过滤健康检查请求的日志，避免在日志中记录 /health 端点的访问"""

    def filter(self, record: logging.LogRecord) -> bool:
        """
        过滤日志记录

        Args:
            record: 日志记录对象

        Returns:
            bool: True 表示记录该日志，False 表示过滤掉该日志
        """
        # 检查是否是访问日志，并且排除 /health 端点
        if hasattr(record, 'args') and len(record.args) >= 3:
            return record.args[2] != '/health'
        return True


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

    # Register health check endpoint for Docker container monitoring
    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> PlainTextResponse:
        """健康检查端点，用于 Docker 容器监控，不记录访问日志"""
        return PlainTextResponse("OK")

    return mcp


if __name__ == "__main__":
    # Configure logging filter to exclude /health endpoint from access logs
    logging.getLogger("uvicorn.access").addFilter(HealthCheckFilter())

    # Create the application
    mcp = create_app()

    # Start MCP server
    # For STDIO mode (Claude Desktop): mcp.run()
    # For HTTP mode: mcp.run(transport="streamable-http", host=DEFAULT_HTTP_HOST, port=DEFAULT_HTTP_PORT)
    mcp.run(transport="streamable-http", host=DEFAULT_HTTP_HOST, port=DEFAULT_HTTP_PORT)
