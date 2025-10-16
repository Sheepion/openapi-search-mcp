"""
Reference resolver for OpenAPI $ref references
"""

from typing import Dict, Any, Set, Optional
import copy


class RefResolver:
    """
    Resolves $ref references in OpenAPI documents.

    This class recursively resolves JSON Schema $ref references (e.g., "#/components/schemas/User")
    and replaces them with the actual schema definitions.
    """

    def __init__(self, document: Dict[str, Any]):
        """
        Initialize RefResolver with an OpenAPI document.

        Args:
            document: Complete OpenAPI document containing components/schemas or definitions
        """
        self.document = document
        # OpenAPI 3.x uses components/schemas
        self.components = document.get('components', {})
        self.schemas = self.components.get('schemas', {})
        # Swagger 2.0 uses definitions
        self.definitions = document.get('definitions', {})

    def resolve(self, obj: Any, max_depth: int = 10, _current_depth: int = 0, _resolving: Optional[Set[str]] = None) -> Any:
        """
        Recursively resolve all $ref references in an object.

        Args:
            obj: Object to resolve (can be dict, list, or primitive)
            max_depth: Maximum recursion depth to prevent infinite loops
            _current_depth: Current recursion depth (internal use)
            _resolving: Set of refs currently being resolved to detect cycles (internal use)

        Returns:
            Object with all $ref references resolved
        """
        # Initialize resolving set on first call
        if _resolving is None:
            _resolving = set()

        # Check depth limit
        if _current_depth > max_depth:
            return obj

        # Handle None and primitives
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj

        # Handle lists
        if isinstance(obj, list):
            return [
                self.resolve(item, max_depth, _current_depth + 1, _resolving)
                for item in obj
            ]

        # Handle dictionaries
        if isinstance(obj, dict):
            # Check if this is a $ref
            if '$ref' in obj:
                ref_path = obj['$ref']
                schema_name = None
                schema_dict = None

                # Handle OpenAPI 3.x format: #/components/schemas/SchemaName
                if ref_path.startswith('#/components/schemas/'):
                    schema_name = ref_path.split('/')[-1]
                    schema_dict = self.schemas
                # Handle Swagger 2.0 format: #/definitions/SchemaName
                elif ref_path.startswith('#/definitions/'):
                    schema_name = ref_path.split('/')[-1]
                    schema_dict = self.definitions

                # If we found a schema reference to resolve
                if schema_name and schema_dict:
                    # Detect circular reference
                    if ref_path in _resolving:
                        # Return a placeholder to prevent infinite recursion
                        return {
                            'x-ref-circular': ref_path,
                            'description': f'Circular reference to {schema_name}'
                        }

                    # Check if schema exists
                    if schema_name in schema_dict:
                        # Mark this ref as being resolved
                        _resolving.add(ref_path)

                        # Get the schema and resolve it recursively
                        schema = copy.deepcopy(schema_dict[schema_name])
                        resolved_schema = self.resolve(schema, max_depth, _current_depth + 1, _resolving)

                        # Unmark this ref
                        _resolving.discard(ref_path)

                        # Merge sibling properties from the original object (OpenAPI 3.1+ compatibility)
                        # Properties alongside $ref like description, example, nullable, etc.
                        if isinstance(resolved_schema, dict):
                            # Add metadata about the original reference
                            resolved_schema['x-ref-original'] = ref_path

                            # Merge all properties from original object except $ref itself
                            for key, value in obj.items():
                                if key != '$ref' and key not in resolved_schema:
                                    # Only add if not already in resolved schema to avoid overwriting
                                    resolved_schema[key] = copy.deepcopy(value)

                        return resolved_schema
                    else:
                        # Schema not found, keep the reference
                        return obj
                else:
                    # Non-schema reference (e.g., parameters, responses), keep as-is
                    return obj

            # Not a $ref, recursively resolve all values
            result = {}
            for key, value in obj.items():
                result[key] = self.resolve(value, max_depth, _current_depth + 1, _resolving)
            return result

        # Unknown type, return as-is
        return obj

    def resolve_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve all schema references in an operation object.

        This is a convenience method that resolves references in:
        - requestBody.content.*.schema
        - responses.*.content.*.schema
        - parameters[].schema

        Args:
            operation: OpenAPI operation object

        Returns:
            Operation object with all schema references resolved
        """
        return self.resolve(copy.deepcopy(operation))
