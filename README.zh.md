# OpenAPI Search MCP Server

**本项目在 [Claude Code](https://claude.ai/code) 的帮助下完成开发。** Claude Code 是 Anthropic 推出的 AI 编程助手。

<div align="center">

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/MCP-FastMCP-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个用于加载、解析和查询 OpenAPI 文档的 Model Context Protocol (MCP) 服务器。

[功能特性](#功能特性) • [快速开始](#快速开始) • [安装](#安装) • [Docker 部署](#docker-部署) • [使用方法](#使用方法) • [架构设计](#架构设计)

</div>

---

## 项目简介

OpenAPI Search MCP Server 是一个专门的 MCP 服务器，它让 OpenAPI/Swagger 文档可以被 AI 助手和其他 MCP 客户端轻松访问。它提供了 10 个强大的工具，用于加载、搜索和查询 API 规范。

### 为什么使用？

- **AI 友好的 API 文档** - 让您的 OpenAPI 规范可以被 Claude 等 AI 助手查询
- **智能搜索** - 跨路径、方法、标签和关键词的多条件搜索
- **快速查找** - 为 operationId 查询预建索引，实现 O(1) 查找
- **格式灵活** - 自动检测 JSON 和 YAML 格式
- **模块化架构** - 遵循 Python 最佳实践的清晰、可维护代码库

---

## 快速开始

```bash
# 1. 创建 conda 环境
conda create -n openapi-search-mcp python=3.12 -y
conda activate openapi-search-mcp

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行服务器
python main.py
```

就这样！服务器现在正在运行，准备接受 MCP 连接。

---

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

---

## Docker 部署

使用 Docker 可以快速、隔离地部署项目。

### 前置要求

- 已安装 Docker ([获取 Docker](https://docs.docker.com/get-docker/))
- Docker Compose（可选，Docker Desktop 已包含）

### 方式 1：使用 Docker Compose（推荐）

最简单的部署方式：

```bash
# 克隆仓库
git clone https://github.com/yourusername/openapi-search-mcp.git
cd openapi-search-mcp

# 构建并启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止容器
docker-compose down
```

服务器将在 `http://localhost:8848` 上运行

### 方式 2：直接使用 Docker

手动构建和运行：

```bash
# 构建镜像
docker build -t openapi-search-mcp:latest .

# 运行容器
docker run -d \
  --name openapi-search-mcp \
  -p 8848:8848 \
  --restart unless-stopped \
  openapi-search-mcp:latest

# 查看日志
docker logs -f openapi-search-mcp

# 停止并删除容器
docker stop openapi-search-mcp
docker rm openapi-search-mcp
```

### Docker 配置说明

Docker 部署包含以下特性：

- **基础镜像**: `python:3.12-slim`（轻量级）
- **端口**: 8848（可通过环境变量配置）
- **健康检查**: 自动健康监控
- **资源限制**: 在 `docker-compose.yml` 中可配置
- **日志管理**: JSON 文件驱动，自动轮转

### 环境变量

您可以通过设置环境变量来自定义部署：

```yaml
environment:
  - DEFAULT_HTTP_PORT=8848  # 修改服务器端口
  - PYTHONUNBUFFERED=1      # 启用实时日志
```

### 从 Claude Desktop 访问

使用 Docker 部署时，更新 Claude Desktop 配置以指向 HTTP 端点：

```json
{
  "mcpServers": {
    "openapi-search": {
      "url": "http://localhost:8848"
    }
  }
}
```

---

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

## 架构设计

OpenAPI Search MCP 遵循清晰的分层架构，借鉴企业级设计模式：

```
┌─────────────────────────────────────┐
│         main.py (入口层)            │  → 应用程序初始化
├─────────────────────────────────────┤
│    工具层 (src/tools/)              │  → MCP 工具定义
├─────────────────────────────────────┤
│   服务层 (src/services/)            │  → 业务逻辑
├─────────────────────────────────────┤
│  存储层 (src/storage.py)            │  → 数据访问
├─────────────────────────────────────┤
│ 加载器/索引器 (src/loaders/,        │  → 工具类
│                src/indexers/)       │
├─────────────────────────────────────┤
│  模型层 (src/models/)               │  → 数据结构
├─────────────────────────────────────┤
│  配置层 (src/config.py)             │  → 常量配置
└─────────────────────────────────────┘
```

### 核心设计原则

1. **关注点分离** - 每一层都有单一职责
2. **依赖注入** - 服务通过构造函数接收依赖
3. **类型安全** - 全面使用 Pydantic 模型
4. **面向接口** - 层之间有清晰的契约
5. **可测试性** - 每一层都可以独立单元测试

### 各层说明

- **配置层** - 集中管理常量和错误消息
- **模型层** - 带验证的类型安全数据结构
- **存储层** - 内存文档存储，提供一致的错误处理
- **加载器层** - HTTP 获取和格式检测（JSON/YAML）
- **索引器层** - 构建反向索引以实现快速查找
- **服务层** - 业务逻辑（5 个服务：API、路径、Schema、搜索、标签）
- **工具层** - MCP 工具注册（3 个模块）
- **入口层** - 应用程序初始化和依赖装配

---

## 项目结构

```
openapi-search-mcp/
├── main.py                          # 入口文件 (~50 行)
├── requirements.txt                 # Python 依赖
├── README.md                        # 英文文档
├── README.zh.md                     # 本文档
├── CLAUDE.md                        # Claude Code 指导文档
├── DESIGN.md                        # 详细设计文档
├── src/                             # 源代码
│   ├── config.py                   # 配置常量
│   ├── storage.py                  # 数据存储层
│   ├── models/                     # 数据模型
│   │   └── openapi_document.py    # Pydantic 模型
│   ├── loaders/                    # 文档加载器
│   │   └── openapi_loader.py      # URL 加载和格式检测
│   ├── indexers/                   # 索引构建器
│   │   └── operation_indexer.py   # operationId 和标签索引
│   ├── services/                   # 业务逻辑
│   │   ├── api_service.py         # API 加载和列表
│   │   ├── path_service.py        # 路径查询
│   │   ├── schema_service.py      # Schema 和鉴权查询
│   │   ├── search_service.py      # 端点搜索
│   │   └── tag_service.py         # 标签查询
│   └── tools/                      # MCP 工具定义
│       ├── loading_tools.py       # load_openapi, list_apis
│       ├── query_tools.py         # 路径、操作、schema 查询
│       └── search_tools.py        # 搜索、标签查询
└── tests/                          # 测试文件
```

---

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.12+ | 运行环境 |
| FastMCP | >=0.2.0 | MCP 服务器框架 |
| httpx | >=0.27.0 | 异步 HTTP 客户端，用于获取文档 |
| PyYAML | >=6.0 | YAML 格式解析 |
| Pydantic | >=2.0.0 | 类型安全的数据模型和验证 |

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

### 运行测试

```bash
pytest tests/
```

### 代码结构

查看 [CLAUDE.md](./CLAUDE.md) 了解详细的架构文档和开发指南。

### 贡献

欢迎贡献！请：
1. Fork 本仓库
2. 创建特性分支
3. 进行更改
4. 添加测试
5. 提交 Pull Request

---

## 许可证

MIT License - 详见 [LICENSE](./LICENSE)

---

## 致谢

**本项目在 [Claude Code](https://claude.ai/code) 的帮助下开发完成**，这是 Anthropic 推出的 AI 编程助手。Claude Code 协助完成了：

- 从单体结构到分层架构的架构设计和重构
- 使用依赖注入的服务层实现
- 文档编写和代码组织
- Python 企业级开发的最佳实践

本项目展示了人类与 AI 在软件开发中协作的力量。

---

## 相关链接

- [FastMCP 文档](https://github.com/jlowin/fastmcp)
- [OpenAPI 规范](https://swagger.io/specification/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

**Built with Claude Code • OpenAPI Search MCP Server • MIT License**
