"""
Operation indexer for fast lookups
"""

from typing import Dict, Any, List
from src.config import HTTP_METHODS


class OperationIndexer:
    """
    Builds indexes for fast lookup of operations and tags.
    """

    @staticmethod
    def build_operation_index(paths: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """
        Build reverse index from operationId to path and method.

        Args:
            paths: The 'paths' section of an OpenAPI document

        Returns:
            Dictionary mapping operationId to {path, method}

        Example:
            {
                "getUserById": {
                    "path": "/users/{id}",
                    "method": "get"
                }
            }
        """
        index = {}

        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue

            for method in HTTP_METHODS:
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

    @staticmethod
    def extract_tags(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract all tags from an OpenAPI document.

        Prefers root-level 'tags' array if present.
        Otherwise extracts unique tags from all operations.

        Args:
            doc: Complete OpenAPI document

        Returns:
            List of tag objects with 'name' (and optionally 'description')

        Example:
            [
                {"name": "pets", "description": "Pet operations"},
                {"name": "users"}
            ]
        """
        # Prefer root-level tags definition
        if 'tags' in doc and isinstance(doc['tags'], list):
            return doc['tags']

        # Otherwise extract unique tags from all operations
        unique_tags = set()
        paths = doc.get('paths', {})

        for path_item in paths.values():
            if not isinstance(path_item, dict):
                continue

            for method in HTTP_METHODS:
                if method in path_item:
                    operation = path_item[method]
                    if isinstance(operation, dict) and 'tags' in operation:
                        for tag in operation['tags']:
                            unique_tags.add(tag)

        # Convert to list of tag objects
        tags = []
        for tag in sorted(unique_tags):
            tags.append({'name': tag})

        return tags
