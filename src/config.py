"""
Configuration constants for the OpenAPI Search MCP Server
"""

# HTTP methods supported by OpenAPI
HTTP_METHODS = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace']

# HTTP client timeout in seconds
HTTP_TIMEOUT = 30.0

# Default HTTP server settings
DEFAULT_HTTP_HOST = "0.0.0.0"  # Listen on all network interfaces
DEFAULT_HTTP_PORT = 8848

# Error message templates
ERROR_API_NOT_FOUND = "API '{name}' not found. Available APIs: {available}"
ERROR_PATH_NOT_FOUND = "Path '{path}' not found in API '{name}'"
ERROR_SCHEMA_NOT_FOUND = "Schema '{schema_name}' not found in API '{name}'. Available schemas: {available}"
ERROR_OPERATION_NOT_FOUND = "Operation ID '{operation_id}' not found in API '{name}'"
ERROR_INVALID_OPENAPI_MISSING_VERSION = "Invalid OpenAPI document: missing 'openapi' or 'swagger' field"
ERROR_INVALID_OPENAPI_MISSING_INFO = "Invalid OpenAPI document: missing 'info' field"
ERROR_INVALID_OPENAPI_MISSING_PATHS = "Invalid OpenAPI document: missing 'paths' field"
