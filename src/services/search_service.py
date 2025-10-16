"""
Endpoint search service
"""

from typing import Dict, Any, Optional
from src.storage import OpenAPIStorage
from src.config import HTTP_METHODS


class SearchService:
    """
    Service for searching endpoints by various criteria.
    """

    def __init__(self, storage: OpenAPIStorage):
        """
        Initialize SearchService.

        Args:
            storage: OpenAPIStorage instance
        """
        self.storage = storage

    def search_endpoints(
        self,
        name: str,
        keyword: Optional[str] = None,
        method: Optional[str] = None,
        tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search endpoints by path, method, tag, or keyword.

        Args:
            name: API name
            keyword: Search keyword matching path, summary, description (optional)
            method: HTTP method filter like GET, POST (optional)
            tag: Tag filter (optional)

        Returns:
            List of matching endpoints
        """
        doc_data, error = self.storage.get_or_error(name)
        if error:
            return error

        paths = doc_data.get('paths', {})
        results = []

        # Normalize method parameter
        if method:
            method = method.lower()

        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue

            for http_method in HTTP_METHODS:
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
