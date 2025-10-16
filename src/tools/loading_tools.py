"""
MCP tools for loading and listing APIs
"""

from typing import Dict, Any
from src.services.api_service import ApiService


def register_loading_tools(mcp, api_service: ApiService):
    """
    Register loading-related MCP tools.

    Args:
        mcp: FastMCP instance
        api_service: ApiService instance
    """

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
        return await api_service.load_openapi(name, url)

    @mcp.tool()
    def list_apis() -> Dict[str, Any]:
        """
        List all loaded APIs with basic info

        Returns:
            List of all loaded APIs
        """
        return api_service.list_apis()
