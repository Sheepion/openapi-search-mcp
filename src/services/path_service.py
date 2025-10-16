"""
Path and operation query service
"""

from typing import Dict, Any
from src.storage import OpenAPIStorage
from src.config import HTTP_METHODS, ERROR_PATH_NOT_FOUND, ERROR_OPERATION_NOT_FOUND
from src.utils.ref_resolver import RefResolver


class PathService:
    """
    Service for querying paths and operations.
    """

    def __init__(self, storage: OpenAPIStorage):
        """
        Initialize PathService.

        Args:
            storage: OpenAPIStorage instance
        """
        self.storage = storage

    def get_path_details(self, name: str, path: str) -> Dict[str, Any]:
        """
        Get complete documentation for a specific path.

        Args:
            name: API name
            path: API path like /users/{id}

        Returns:
            All HTTP methods and details for the path
        """
        doc_data, error = self.storage.get_or_error(name)
        if error:
            return error

        paths = doc_data.get('paths', {})

        if path not in paths:
            return {
                "error": True,
                "message": ERROR_PATH_NOT_FOUND.format(path=path, name=name)
            }

        path_item = paths[path]
        methods = {}

        for method in HTTP_METHODS:
            if method in path_item:
                methods[method] = path_item[method]

        return {
            "path": path,
            "methods": methods
        }

    def list_all_paths(self, name: str) -> Dict[str, Any]:
        """
        List all API paths.

        Args:
            name: API name

        Returns:
            All paths and supported HTTP methods
        """
        doc_data, error = self.storage.get_or_error(name)
        if error:
            return error

        paths = doc_data.get('paths', {})
        result = []

        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue

            methods = [m for m in HTTP_METHODS if m in path_item]
            result.append({
                "path": path,
                "methods": methods
            })

        return {
            "count": len(result),
            "paths": result
        }

    def get_operation_by_id(self, name: str, operation_id: str, resolve_refs: bool = True) -> Dict[str, Any]:
        """
        Quickly query endpoint by operationId.

        Args:
            name: API name
            operation_id: operationId like getUserById
            resolve_refs: If True, automatically resolve all $ref schema references (default: True)

        Returns:
            Complete operation information with optional schema resolution
        """
        doc_data, error = self.storage.get_or_error(name)
        if error:
            return error

        operation_index = doc_data.get('operation_index', {})

        if operation_id not in operation_index:
            return {
                "error": True,
                "message": ERROR_OPERATION_NOT_FOUND.format(operation_id=operation_id, name=name)
            }

        index_entry = operation_index[operation_id]
        path = index_entry['path']
        method = index_entry['method']

        paths = doc_data.get('paths', {})
        operation = paths[path][method]

        # Resolve schema references if requested
        if resolve_refs:
            raw_doc = doc_data.get('raw', {})
            resolver = RefResolver(raw_doc)
            operation = resolver.resolve_operation(operation)

        return {
            "operation_id": operation_id,
            "path": path,
            "method": method,
            "details": operation
        }
