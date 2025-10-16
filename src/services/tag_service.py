"""
Tag query service
"""

from typing import Dict, Any
from src.storage import OpenAPIStorage
from src.config import HTTP_METHODS


class TagService:
    """
    Service for querying tags and endpoints by tag.
    """

    def __init__(self, storage: OpenAPIStorage):
        """
        Initialize TagService.

        Args:
            storage: OpenAPIStorage instance
        """
        self.storage = storage

    def list_tags(self, name: str) -> Dict[str, Any]:
        """
        List all tags for an API.

        Args:
            name: API name

        Returns:
            List of all tags with names and descriptions
        """
        doc_data, error = self.storage.get_or_error(name)
        if error:
            return error

        tags = doc_data.get('tags', [])

        return {
            "count": len(tags),
            "tags": tags
        }

    def get_endpoints_by_tag(self, name: str, tag: str) -> Dict[str, Any]:
        """
        Get endpoints list by tag (overview only).

        Args:
            name: API name
            tag: Tag name

        Returns:
            Overview of all endpoints under the tag
        """
        doc_data, error = self.storage.get_or_error(name)
        if error:
            return error

        paths = doc_data.get('paths', {})
        endpoints = []

        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue

            for method in HTTP_METHODS:
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
