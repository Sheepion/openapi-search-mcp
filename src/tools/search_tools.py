"""
MCP tools for searching endpoints and tags
"""

from typing import Dict, Any, Optional
from src.services.search_service import SearchService
from src.services.tag_service import TagService


def register_search_tools(
    mcp,
    search_service: SearchService,
    tag_service: TagService
):
    """
    Register search-related MCP tools.

    Args:
        mcp: FastMCP instance
        search_service: SearchService instance
        tag_service: TagService instance
    """

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
        return search_service.search_endpoints(name, keyword, method, tag)

    @mcp.tool()
    def list_tags(name: str) -> Dict[str, Any]:
        """
        List all tags for an API

        Args:
            name: API name

        Returns:
            List of all tags with names and descriptions
        """
        return tag_service.list_tags(name)

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
        return tag_service.get_endpoints_by_tag(name, tag)
