"""
Data models for OpenAPI documents
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class OperationIndexEntry(BaseModel):
    """Index entry mapping operationId to path and method"""
    path: str
    method: str


class OpenAPIDocument(BaseModel):
    """
    Structured representation of a parsed OpenAPI document.
    This model represents the processed and indexed document stored in memory.
    """

    raw: Dict[str, Any] = Field(
        description="Complete original OpenAPI document"
    )

    info: Dict[str, Any] = Field(
        default_factory=dict,
        description="Document info (title, version, description)"
    )

    servers: List[Any] = Field(
        default_factory=list,
        description="Server URLs"
    )

    paths: Dict[str, Any] = Field(
        default_factory=dict,
        description="All endpoint definitions"
    )

    components: Dict[str, Any] = Field(
        default_factory=dict,
        description="Reusable components (schemas, securitySchemes, etc.)"
    )

    tags: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of tags"
    )

    operation_index: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Fast lookup index: operationId -> {path, method}"
    )

    class Config:
        # Allow arbitrary types for flexibility with OpenAPI structures
        arbitrary_types_allowed = True

    @classmethod
    def from_raw_document(
        cls,
        raw: Dict[str, Any],
        operation_index: Dict[str, Dict[str, str]],
        tags: List[Dict[str, Any]]
    ) -> "OpenAPIDocument":
        """
        Create an OpenAPIDocument from a raw OpenAPI specification.

        Args:
            raw: The complete OpenAPI document
            operation_index: Pre-built operation index
            tags: Extracted tags list

        Returns:
            OpenAPIDocument instance
        """
        return cls(
            raw=raw,
            info=raw.get('info', {}),
            servers=raw.get('servers', []),
            paths=raw.get('paths', {}),
            components=raw.get('components', {}),
            tags=tags,
            operation_index=operation_index
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format for storage.

        Returns:
            Dictionary representation
        """
        return {
            'raw': self.raw,
            'info': self.info,
            'servers': self.servers,
            'paths': self.paths,
            'components': self.components,
            'tags': self.tags,
            'operation_index': self.operation_index
        }
