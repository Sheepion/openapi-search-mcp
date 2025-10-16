"""
API management service
"""

import json
import yaml
import httpx
from typing import Dict, Any
from src.storage import OpenAPIStorage
from src.loaders.openapi_loader import OpenAPILoader
from src.indexers.operation_indexer import OperationIndexer
from src.models.openapi_document import OpenAPIDocument


class ApiService:
    """
    Service for loading and managing OpenAPI documents.
    """

    def __init__(self, storage: OpenAPIStorage):
        """
        Initialize ApiService.

        Args:
            storage: OpenAPIStorage instance
        """
        self.storage = storage
        self.loader = OpenAPILoader()
        self.indexer = OperationIndexer()

    async def load_openapi(self, name: str, url: str) -> Dict[str, Any]:
        """
        Load an OpenAPI document from URL and save to storage.

        Args:
            name: API name for later queries
            url: URL of the OpenAPI document

        Returns:
            Loading status and document basic info
        """
        try:
            # Load document from URL
            doc = await self.loader.load_from_url(url)

            # Validate document structure
            is_valid, error_message = self.loader.validate_document(doc)
            if not is_valid:
                return {
                    "error": True,
                    "message": error_message
                }

            # Build indexes
            operation_index = self.indexer.build_operation_index(doc.get('paths', {}))
            tags = self.indexer.extract_tags(doc)

            # Create document model
            openapi_doc = OpenAPIDocument.from_raw_document(doc, operation_index, tags)

            # Save to storage
            self.storage.add(name, openapi_doc.to_dict())

            # Return success info
            return {
                "status": "success",
                "message": f"API '{name}' loaded successfully",
                "info": {
                    "title": doc['info'].get('title', 'N/A'),
                    "version": doc['info'].get('version', 'N/A'),
                    "description": doc['info'].get('description', '')
                },
                "servers": [s.get('url') if isinstance(s, dict) else str(s) for s in doc.get('servers', [])],
                "paths_count": len(doc.get('paths', {})),
                "tags_count": len(tags)
            }

        except httpx.HTTPError as e:
            return {
                "error": True,
                "message": f"Failed to fetch URL: {str(e)}"
            }
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            return {
                "error": True,
                "message": f"Failed to parse document: {str(e)}"
            }
        except Exception as e:
            return {
                "error": True,
                "message": f"Unexpected error: {str(e)}"
            }

    def list_apis(self) -> Dict[str, Any]:
        """
        List all loaded APIs with basic information.

        Returns:
            List of all loaded APIs
        """
        apis = []

        for name, data in self.storage.list_all().items():
            info = data.get('info', {})
            apis.append({
                "name": name,
                "title": info.get('title', 'N/A'),
                "version": info.get('version', 'N/A'),
                "description": info.get('description', ''),
                "servers": [s.get('url') if isinstance(s, dict) else str(s) for s in data.get('servers', [])],
                "paths_count": len(data.get('paths', {})),
                "tags_count": len(data.get('tags', []))
            })

        return {
            "count": len(apis),
            "apis": apis
        }
