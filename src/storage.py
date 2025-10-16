"""
In-memory storage for OpenAPI documents
"""

from typing import Dict, Any, Optional, List
from src.config import ERROR_API_NOT_FOUND


class OpenAPIStorage:
    """
    In-memory storage for OpenAPI documents.
    Provides CRUD operations and unified error handling.
    """

    def __init__(self):
        self._storage: Dict[str, Dict[str, Any]] = {}

    def add(self, name: str, document_data: Dict[str, Any]) -> None:
        """
        Add or update an OpenAPI document in storage.

        Args:
            name: API name
            document_data: Parsed and indexed OpenAPI document data
        """
        self._storage[name] = document_data

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get an OpenAPI document by name.

        Args:
            name: API name

        Returns:
            Document data or None if not found
        """
        return self._storage.get(name)

    def exists(self, name: str) -> bool:
        """
        Check if an API exists in storage.

        Args:
            name: API name

        Returns:
            True if exists, False otherwise
        """
        return name in self._storage

    def list_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all stored OpenAPI documents.

        Returns:
            Dictionary of all documents
        """
        return self._storage

    def remove(self, name: str) -> bool:
        """
        Remove an OpenAPI document from storage.

        Args:
            name: API name

        Returns:
            True if removed, False if not found
        """
        if name in self._storage:
            del self._storage[name]
            return True
        return False

    def get_available_apis(self) -> str:
        """
        Get a comma-separated list of available API names.

        Returns:
            Comma-separated API names or 'none' if empty
        """
        if not self._storage:
            return 'none'
        return ', '.join(sorted(self._storage.keys()))

    def get_or_error(self, name: str) -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Get an OpenAPI document or return an error response.

        Args:
            name: API name

        Returns:
            Tuple of (document_data, error_dict)
            If found: (document_data, None)
            If not found: (None, error_dict)
        """
        if name not in self._storage:
            return None, {
                "error": True,
                "message": ERROR_API_NOT_FOUND.format(
                    name=name,
                    available=self.get_available_apis()
                )
            }
        return self._storage[name], None
