"""
Schema and authentication query service
"""

from typing import Dict, Any
from src.storage import OpenAPIStorage
from src.config import ERROR_SCHEMA_NOT_FOUND


class SchemaService:
    """
    Service for querying schemas and authentication info.
    """

    def __init__(self, storage: OpenAPIStorage):
        """
        Initialize SchemaService.

        Args:
            storage: OpenAPIStorage instance
        """
        self.storage = storage

    def get_schema_details(self, name: str, schema_name: str) -> Dict[str, Any]:
        """
        Get data model definition from components/schemas.

        Args:
            name: API name
            schema_name: Schema name like User, Pet

        Returns:
            Detailed schema definition
        """
        doc_data, error = self.storage.get_or_error(name)
        if error:
            return error

        components = doc_data.get('components', {})
        schemas = components.get('schemas', {})

        if schema_name not in schemas:
            available = ', '.join(schemas.keys()) if schemas else 'none'
            return {
                "error": True,
                "message": ERROR_SCHEMA_NOT_FOUND.format(
                    schema_name=schema_name,
                    name=name,
                    available=available
                )
            }

        schema = schemas[schema_name]

        return {
            "schema_name": schema_name,
            **schema
        }

    def get_auth_info(self, name: str) -> Dict[str, Any]:
        """
        Get authentication configuration for an API.

        Args:
            name: API name

        Returns:
            Detailed security schemes configuration
        """
        doc_data, error = self.storage.get_or_error(name)
        if error:
            return error

        raw_doc = doc_data['raw']
        components = doc_data.get('components', {})

        security_schemes = components.get('securitySchemes', {})
        global_security = raw_doc.get('security', [])

        return {
            "security_schemes": security_schemes,
            "global_security": global_security
        }
