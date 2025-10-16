"""
OpenAPI document loader and parser
"""

import json
import yaml
import httpx
from typing import Dict, Any
from src.config import (
    HTTP_TIMEOUT,
    ERROR_INVALID_OPENAPI_MISSING_VERSION,
    ERROR_INVALID_OPENAPI_MISSING_INFO,
    ERROR_INVALID_OPENAPI_MISSING_PATHS
)


class OpenAPILoader:
    """
    Loads and parses OpenAPI documents from URLs.
    Supports both JSON and YAML formats with auto-detection.
    """

    @staticmethod
    async def load_from_url(url: str) -> Dict[str, Any]:
        """
        Load an OpenAPI document from a URL.

        Args:
            url: URL of the OpenAPI document

        Returns:
            Parsed OpenAPI document as dictionary

        Raises:
            httpx.HTTPError: If HTTP request fails
            json.JSONDecodeError: If JSON parsing fails
            yaml.YAMLError: If YAML parsing fails
        """
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.get(url)
            response.raise_for_status()

            # Determine format and parse
            return OpenAPILoader._parse_response(response, url)

    @staticmethod
    def _parse_response(response: httpx.Response, url: str) -> Dict[str, Any]:
        """
        Parse HTTP response content as JSON or YAML.

        Args:
            response: HTTP response object
            url: Original URL (for format detection)

        Returns:
            Parsed document dictionary

        Raises:
            json.JSONDecodeError: If JSON parsing fails
            yaml.YAMLError: If YAML parsing fails
        """
        content_type = response.headers.get('content-type', '').lower()

        # Try to determine format by Content-Type
        if 'json' in content_type or url.endswith('.json'):
            return response.json()

        if 'yaml' in content_type or url.endswith(('.yaml', '.yml')):
            return yaml.safe_load(response.text)

        # Auto-detect format: try JSON first, then YAML
        try:
            return response.json()
        except json.JSONDecodeError:
            return yaml.safe_load(response.text)

    @staticmethod
    def validate_document(doc: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate that the document is a valid OpenAPI specification.

        Args:
            doc: Parsed OpenAPI document

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for OpenAPI/Swagger version field
        if 'openapi' not in doc and 'swagger' not in doc:
            return False, ERROR_INVALID_OPENAPI_MISSING_VERSION

        # Check for required 'info' field
        if 'info' not in doc:
            return False, ERROR_INVALID_OPENAPI_MISSING_INFO

        # Check for required 'paths' field
        if 'paths' not in doc:
            return False, ERROR_INVALID_OPENAPI_MISSING_PATHS

        return True, ""
