# OpenAPI Search MCP Server

一个用于加载、解析和查询 OpenAPI 文档的 Model Context Protocol (MCP) 服务器。

## 功能特性

- 🔄 从 URL 加载 OpenAPI 文档（支持 JSON 和 YAML 格式）
- 💾 将文档解析后保存到内存中
- 🔍 提供 10 个强大的查询工具
- 🚀 支持 OpenAPI 3.0.x, 3.1.x 和 Swagger 2.0

## 安装

### 1. 创建 Conda 环境

```bash
conda create -n openapi-search-mcp python=3.12 -y
conda activate openapi-search-mcp
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 启动服务器

### STDIO 模式（默认，适用于 Claude Desktop）

```bash
conda activate openapi-search-mcp
python main.py
```

### HTTP 模式

修改 `main.py` 最后一行为：

```python
mcp.run(transport="streamable-http", port=8080)
```

然后运行：

```bash
conda activate openapi-search-mcp
python main.py
```

## 可用工具

### 1. load_openapi
从 URL 加载 OpenAPI 文档并保存到内存

**参数：**
- `name` (str): API 名称，用于后续查询
- `url` (str): OpenAPI 文档的 URL

**示例：**
```json
{
  "name": "petstore",
  "url": "https://petstore.swagger.io/v2/swagger.json"
}
```

### 2. list_apis
列出所有已加载的 API 及其基本信息

**参数：** 无

### 3. get_path_details
查询特定路径的完整接口文档

**参数：**
- `name` (str): API 名称
- `path` (str): 接口路径，如 `/users/{id}`

### 4. get_auth_info
查询 API 的鉴权配置信息

**参数：**
- `name` (str): API 名称

### 5. search_endpoints
搜索接口（支持按路径、方法、标签、描述关键词搜索）

**参数：**
- `name` (str): API 名称
- `keyword` (str, 可选): 搜索关键词
- `method` (str, 可选): HTTP 方法过滤（GET/POST/etc）
- `tag` (str, 可选): 标签过滤

### 6. list_all_paths
列出某个 API 的所有接口路径

**参数：**
- `name` (str): API 名称

### 7. get_schema_details
查询 components/schemas 中定义的数据模型

**参数：**
- `name` (str): API 名称
- `schema_name` (str): Schema 名称（如 `User`, `Pet`）

### 8. get_operation_by_id
根据 operationId 快速查询接口

**参数：**
- `name` (str): API 名称
- `operation_id` (str): operationId（如 `getUserById`）

### 9. list_tags
列出某个 API 的所有标签（tags）

**参数：**
- `name` (str): API 名称

### 10. get_endpoints_by_tag
根据标签查询接口列表（仅返回概览信息）

**参数：**
- `name` (str): API 名称
- `tag` (str): 标签名称

## 使用示例

### 典型工作流

```
1. 加载 OpenAPI 文档
   load_openapi(name="petstore", url="https://petstore.swagger.io/v2/swagger.json")

2. 查看所有标签
   list_tags(name="petstore")

3. 根据标签查看接口概览
   get_endpoints_by_tag(name="petstore", tag="pets")

4. 查看具体接口详情
   get_path_details(name="petstore", path="/pets/{petId}")

5. 查看数据模型
   get_schema_details(name="petstore", schema_name="Pet")

6. 查看鉴权信息
   get_auth_info(name="petstore")
```

## Claude Desktop 配置

在 Claude Desktop 的配置文件中添加：

**macOS/Linux:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "openapi-search": {
      "command": "conda",
      "args": ["run", "-n", "openapi-search-mcp", "python", "/path/to/openapi-search-mcp/main.py"]
    }
  }
}
```

或者直接使用 python：

```json
{
  "mcpServers": {
    "openapi-search": {
      "command": "/path/to/conda/envs/openapi-search-mcp/bin/python",
      "args": ["/path/to/openapi-search-mcp/main.py"]
    }
  }
}
```

## 项目结构

```
openapi-search-mcp/
├── main.py              # MCP 服务器主程序
├── requirements.txt     # 依赖列表
├── DESIGN.md           # 设计文档
└── README.md           # 本文档
```

## 技术栈

- **Python 3.12** - 运行环境
- **FastMCP** - MCP 服务器框架
- **httpx** - 异步 HTTP 客户端
- **PyYAML** - YAML 解析
- **Pydantic** - 数据验证

## 支持的 OpenAPI 版本

- ✅ OpenAPI 3.0.x
- ✅ OpenAPI 3.1.x
- ✅ Swagger 2.0

## 常见问题

### Q: 如何加载本地的 OpenAPI 文件？
A: 目前仅支持从 URL 加载。未来版本将支持本地文件。

### Q: 如何切换到 HTTP 模式？
A: 修改 `main.py` 最后的 `mcp.run()` 为 `mcp.run(transport="streamable-http", port=8080)`

### Q: 文档加载后会持久化吗？
A: 不会，文档仅保存在内存中。服务重启后需要重新加载。

## 开发

查看 [DESIGN.md](./DESIGN.md) 了解详细的设计思路和实现细节。

## License

MIT

## 作者

Created with Claude Code
