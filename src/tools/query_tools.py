"""
MCP tools for querying paths, operations, schemas, and auth
"""

from typing import Dict, Any
from src.services.path_service import PathService
from src.services.schema_service import SchemaService


def register_query_tools(
    mcp,
    path_service: PathService,
    schema_service: SchemaService
):
    """
    Register query-related MCP tools.

    Args:
        mcp: FastMCP instance
        path_service: PathService instance
        schema_service: SchemaService instance
    """

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
        return path_service.get_path_details(name, path)

    @mcp.tool()
    def list_all_paths(name: str) -> Dict[str, Any]:
        """
        List all API paths

        Args:
            name: API name

        Returns:
            All paths and supported HTTP methods
        """
        return path_service.list_all_paths(name)

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
        return path_service.get_operation_by_id(name, operation_id)

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
        return schema_service.get_schema_details(name, schema_name)

    @mcp.tool()
    def get_auth_info(name: str) -> Dict[str, Any]:
        """
        Get authentication configuration for an API

        Args:
            name: API name

        Returns:
            Detailed security schemes configuration
        """
        return schema_service.get_auth_info(name)
