# OpenAPI Search MCP 设计文档

## 项目概述

这是一个基于 Model Context Protocol (MCP) 的 HTTP 服务，用于加载、解析和查询 OpenAPI 文档。用户可以通过多个工具来灵活查询 API 接口的详细信息。

### 核心功能
- 从 URL 加载 OpenAPI 文档（支持 JSON 和 YAML 格式）
- 将文档解析后保存到内存中
- 提供 10 个查询工具，支持多维度的接口查询

---

## 技术栈

- **Python 3.12** - 运行环境
- **FastMCP** - 快速构建 MCP 服务器框架
- **httpx** - 异步 HTTP 客户端，用于获取远程 OpenAPI 文档
- **PyYAML** - 解析 YAML 格式的 OpenAPI 文档
- **Pydantic** - 数据验证和类型检查

---

## 架构设计

### 1. 内存存储结构

使用全局字典存储多个 OpenAPI 文档：

```python
openapi_docs = {
    "api_name_1": {
        "raw": {...},           # 原始的 OpenAPI 文档（完整 dict）
        "info": {...},          # 基本信息（title, version, description）
        "servers": [...],       # 服务器地址列表
        "paths": {...},         # 路径定义
        "components": {...},    # 组件定义（schemas, securitySchemes 等）
        "tags": [...],          # 标签列表
        "operation_index": {    # operationId 到路径和方法的映射
            "getUserById": {
                "path": "/users/{id}",
                "method": "get"
            }
        }
    },
    "api_name_2": {...}
}
```

### 2. 服务器模式

- **传输模式**: `streamable-http`
- **端口**: 默认 8080（可配置）
- **状态**: 有状态服务（stateless_http=False），保持内存中的文档

---

## 工具设计

### 1. load_openapi

**功能**: 从 URL 加载 OpenAPI 文档并解析保存到内存

**参数**:
- `name` (str, 必需): API 名称，用于后续查询的标识
- `url` (str, 必需): OpenAPI 文档的 URL

**返回**:
```json
{
  "status": "success",
  "message": "API 'petstore' loaded successfully",
  "info": {
    "title": "Swagger Petstore",
    "version": "1.0.0",
    "description": "A sample Pet Store Server"
  },
  "servers": ["https://petstore.swagger.io/v2"],
  "paths_count": 14,
  "tags_count": 3
}
```

**实现逻辑**:
1. 使用 httpx 获取 URL 内容
2. 根据 Content-Type 或内容特征判断是 JSON 还是 YAML
3. 解析文档
4. 验证是否包含必要字段（openapi/swagger, info, paths）
5. 构建 operation_index（遍历所有路径和方法，提取 operationId）
6. 保存到内存
7. 返回加载成功信息

**错误处理**:
- URL 无法访问
- 格式不正确（非 JSON/YAML）
- OpenAPI 文档结构不完整
- 名称已存在（覆盖警告）

---

### 2. list_apis

**功能**: 列出所有已加载的 API 名称和基本信息

**参数**: 无

**返回**:
```json
{
  "count": 2,
  "apis": [
    {
      "name": "petstore",
      "title": "Swagger Petstore",
      "version": "1.0.0",
      "description": "A sample Pet Store Server",
      "servers": ["https://petstore.swagger.io/v2"],
      "paths_count": 14,
      "tags_count": 3
    },
    {
      "name": "github",
      "title": "GitHub v3 REST API",
      "version": "1.1.4",
      "paths_count": 356,
      "tags_count": 25
    }
  ]
}
```

**实现逻辑**:
- 遍历 openapi_docs 字典
- 返回每个 API 的摘要信息

---

### 3. get_path_details

**功能**: 查询特定 path 的完整接口文档

**参数**:
- `name` (str, 必需): API 名称
- `path` (str, 必需): 接口路径，如 `/users/{id}`

**返回**:
```json
{
  "path": "/users/{id}",
  "methods": {
    "get": {
      "summary": "Get user by ID",
      "description": "Returns a single user",
      "operationId": "getUserById",
      "tags": ["users"],
      "parameters": [...],
      "responses": {...},
      "security": [...]
    },
    "put": {...},
    "delete": {...}
  }
}
```

**实现逻辑**:
1. 检查 API 是否存在
2. 检查路径是否存在
3. 返回该路径下所有 HTTP 方法的完整定义

**错误处理**:
- API 不存在
- 路径不存在

---

### 4. get_auth_info

**功能**: 查询 API 的鉴权配置信息

**参数**:
- `name` (str, 必需): API 名称

**返回**:
```json
{
  "security_schemes": {
    "bearerAuth": {
      "type": "http",
      "scheme": "bearer",
      "bearerFormat": "JWT"
    },
    "apiKey": {
      "type": "apiKey",
      "in": "header",
      "name": "X-API-Key"
    },
    "oauth2": {
      "type": "oauth2",
      "flows": {...}
    }
  },
  "global_security": [
    {"bearerAuth": []}
  ]
}
```

**实现逻辑**:
1. 提取 `components.securitySchemes`
2. 提取根级别的 `security` 定义（全局安全要求）
3. 返回完整的鉴权信息

**错误处理**:
- API 不存在
- 没有定义安全方案（返回空对象）

---

### 5. search_endpoints

**功能**: 搜索接口（支持按路径、方法、标签、描述关键词搜索）

**参数**:
- `name` (str, 必需): API 名称
- `keyword` (str, 可选): 搜索关键词，匹配路径、summary、description
- `method` (str, 可选): HTTP 方法过滤（如 GET、POST）
- `tag` (str, 可选): 标签过滤

**返回**:
```json
{
  "count": 5,
  "results": [
    {
      "path": "/users/{id}",
      "method": "get",
      "operationId": "getUserById",
      "summary": "Get user by ID",
      "tags": ["users"]
    },
    ...
  ]
}
```

**实现逻辑**:
1. 遍历所有路径和方法
2. 应用过滤条件：
   - keyword: 匹配路径、summary、description（不区分大小写）
   - method: 精确匹配 HTTP 方法
   - tag: 检查 tags 数组是否包含指定标签
3. 返回匹配的接口概览

---

### 6. list_all_paths

**功能**: 列出某个 API 的所有接口路径

**参数**:
- `name` (str, 必需): API 名称

**返回**:
```json
{
  "count": 14,
  "paths": [
    {
      "path": "/pets",
      "methods": ["get", "post"]
    },
    {
      "path": "/pets/{petId}",
      "methods": ["get", "put", "delete"]
    },
    ...
  ]
}
```

**实现逻辑**:
- 遍历 paths 对象
- 提取每个路径和支持的方法列表

---

### 7. get_schema_details

**功能**: 查询 components/schemas 中定义的数据模型

**参数**:
- `name` (str, 必需): API 名称
- `schema_name` (str, 必需): Schema 名称（如 `User`, `Pet`）

**返回**:
```json
{
  "schema_name": "User",
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "username": {
      "type": "string"
    },
    "email": {
      "type": "string",
      "format": "email"
    }
  },
  "required": ["username", "email"]
}
```

**实现逻辑**:
1. 提取 `components.schemas[schema_name]`
2. 返回完整的 Schema 定义

**错误处理**:
- API 不存在
- Schema 不存在

---

### 8. get_operation_by_id

**功能**: 根据 operationId 快速查询接口

**参数**:
- `name` (str, 必需): API 名称
- `operation_id` (str, 必需): operationId（如 `getUserById`）

**返回**:
```json
{
  "operation_id": "getUserById",
  "path": "/users/{id}",
  "method": "get",
  "details": {
    "summary": "Get user by ID",
    "description": "Returns a single user",
    "parameters": [...],
    "responses": {...}
  }
}
```

**实现逻辑**:
1. 从 operation_index 中查找 operationId
2. 获取对应的路径和方法
3. 返回完整的 operation 定义

**错误处理**:
- API 不存在
- operationId 不存在

---

### 9. list_tags

**功能**: 列出某个 API 的所有标签（tags）

**参数**:
- `name` (str, 必需): API 名称

**返回**:
```json
{
  "count": 3,
  "tags": [
    {
      "name": "pets",
      "description": "Everything about your Pets"
    },
    {
      "name": "store",
      "description": "Access to Petstore orders"
    },
    {
      "name": "users",
      "description": "Operations about user"
    }
  ]
}
```

**实现逻辑**:
1. 提取根级别的 `tags` 数组
2. 如果不存在，遍历所有 operations 提取唯一的 tag 名称
3. 返回标签列表

---

### 10. get_endpoints_by_tag

**功能**: 根据 tag 查询接口列表（仅返回概览信息）

**参数**:
- `name` (str, 必需): API 名称
- `tag` (str, 必需): 标签名称

**返回**:
```json
{
  "tag": "users",
  "count": 5,
  "endpoints": [
    {
      "path": "/users",
      "method": "get",
      "operationId": "listUsers",
      "summary": "List all users"
    },
    {
      "path": "/users",
      "method": "post",
      "operationId": "createUser",
      "summary": "Create a new user"
    },
    {
      "path": "/users/{id}",
      "method": "get",
      "operationId": "getUserById",
      "summary": "Get user by ID"
    },
    ...
  ]
}
```

**实现逻辑**:
1. 遍历所有路径和方法
2. 筛选包含指定 tag 的 operations
3. 仅返回概览信息（不包含详细的参数、响应等）

---

## 实现细节

### 1. OpenAPI 版本支持

支持以下版本：
- OpenAPI 3.0.x
- OpenAPI 3.1.x
- Swagger 2.0（向后兼容）

### 2. 格式检测

```python
async def load_openapi_doc(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

        content_type = response.headers.get('content-type', '')

        # 尝试 JSON
        if 'json' in content_type or url.endswith('.json'):
            return response.json()

        # 尝试 YAML
        if 'yaml' in content_type or url.endswith(('.yaml', '.yml')):
            return yaml.safe_load(response.text)

        # 自动检测
        try:
            return response.json()
        except:
            return yaml.safe_load(response.text)
```

### 3. operation_index 构建

```python
def build_operation_index(paths: dict) -> dict:
    index = {}
    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                operation_id = operation.get('operationId')
                if operation_id:
                    index[operation_id] = {
                        'path': path,
                        'method': method
                    }
    return index
```

### 4. 错误响应格式

统一的错误响应格式：

```json
{
  "error": true,
  "message": "API 'unknown' not found. Available APIs: petstore, github"
}
```

---

## 使用场景示例

### 场景 1: 加载和浏览 API

```
1. load_openapi(name="petstore", url="https://petstore.swagger.io/v2/swagger.json")
   → 成功加载，返回基本信息

2. list_tags(name="petstore")
   → 查看有哪些功能模块（tags）

3. get_endpoints_by_tag(name="petstore", tag="pets")
   → 查看 pets 相关的所有接口概览

4. get_path_details(name="petstore", path="/pets/{petId}")
   → 查看具体接口的详细信息
```

### 场景 2: 搜索和查询

```
1. search_endpoints(name="petstore", keyword="user", method="POST")
   → 搜索包含 "user" 关键词的 POST 接口

2. get_operation_by_id(name="petstore", operation_id="getUserById")
   → 通过 operationId 快速定位接口

3. get_schema_details(name="petstore", schema_name="User")
   → 查看 User 数据模型定义
```

### 场景 3: 鉴权信息

```
1. get_auth_info(name="petstore")
   → 查看 API 的鉴权方式（Bearer Token, API Key, OAuth2 等）
```

---

## 启动方式

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务器（默认端口 8080）
python3.12 main.py

# 自定义端口
python3.12 main.py --port 3000
```

---

## 项目结构

```
openapi-search-mcp/
├── main.py              # MCP 服务器主程序
├── requirements.txt     # 依赖列表
├── DESIGN.md           # 本设计文档
└── README.md           # 使用说明（待创建）
```

---

## 未来扩展

可能的扩展功能：
1. 支持从本地文件加载 OpenAPI 文档
2. 支持导出查询结果为 Markdown 文档
3. 支持接口调用测试（根据 OpenAPI 定义生成请求）
4. 支持多版本 API 对比
5. 持久化存储（保存到文件或数据库）
6. 支持 GraphQL schema 解析
