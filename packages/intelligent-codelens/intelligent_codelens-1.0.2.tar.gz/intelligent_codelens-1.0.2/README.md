# 🔍 CodeLens - 智能代码搜索引擎

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)](https://modelcontextprotocol.io)
[![Trae](https://img.shields.io/badge/Trae-Supported-purple.svg)](https://trae.ai)
[![Claude](https://img.shields.io/badge/Claude-Compatible-blue.svg)](https://claude.ai)
[![Cursor](https://img.shields.io/badge/Cursor-Compatible-green.svg)](https://cursor.sh)

> 🚀 **专为AI编辑器设计的智能代码搜索引擎** - 为Trae、Claude、Cursor等AI编程助手提供强大的代码理解和搜索能力

## ✨ 项目简介

CodeLens是一个专门为**AI编辑器**设计的智能代码搜索引擎，基于**MCP协议**提供语义搜索能力。它能够：

- 🤖 **AI编辑器集成** - 完美支持Trae、Claude、Cursor等主流AI编程工具
- 🧠 **智能理解代码语义** - 支持中英文自然语言查询，理解代码意图
- ⚡ **毫秒级搜索响应** - 基于向量数据库的高效检索，提升AI编程体验
- 🔧 **多语言代码支持** - Python、JavaScript、Java、C++等主流编程语言
- 🎯 **精准匹配算法** - 结合语义相似度和代码结构分析
- 🛡️ **本地部署安全** - 代码不离开本地环境，保护隐私和安全

一个高性能的智能代码搜索引擎，基于 Model Context Protocol (MCP) 构建，支持语义搜索、语法分析和智能代码理解。

## ✨ 核心特性

### 🔍 智能搜索能力
- **语义搜索**: 基于 Sentence Transformers 的深度语义理解
- **语法分析**: 使用 Tree-sitter 进行精确的代码结构解析
- **多语言支持**: Python、JavaScript、Java 等主流编程语言
- **实时索引**: 支持代码库的增量更新和实时索引

### 🚀 高性能架构
- **异步处理**: 基于 asyncio 的高并发处理能力
- **智能缓存**: 多层缓存策略，显著提升查询性能
- **批量操作**: 支持批量索引和搜索操作
- **内存优化**: 高效的内存管理和资源利用

### 🔧 本地部署
- **MCP协议**: 标准化的模型上下文协议接口
- **RESTful API**: 完整的 HTTP API 支持
- **简单配置**: 开箱即用的本地部署方案

### 📊 监控与可观测性
- **性能指标**: 详细的搜索性能统计
- **健康检查**: 完整的服务健康监控
- **日志系统**: 结构化日志和错误追踪

## 🚀 功能特性

### 🤖 AI编辑器原生支持
- **Trae AI**: 完美集成，提供智能代码补全和理解
- **Claude**: 支持代码分析和重构建议
- **Cursor**: 增强代码搜索和导航体验
- **其他MCP兼容工具**: 标准MCP协议，广泛兼容

### 🔍 智能搜索引擎
- **语义搜索**: 基于向量嵌入的深度语义理解
- **语法解析**: Tree-sitter驱动的精确代码结构分析
- **多语言支持**: Python、JavaScript、Java、Go等主流语言
- **实时索引**: 支持增量更新和实时代码变更检测

### 🤖 MCP协议支持
- **标准兼容**: 完全符合MCP 1.0规范
- **工具集成**: 提供丰富的MCP工具集
- **异步处理**: 高效的异步消息处理机制
- **扩展性**: 易于扩展的插件架构

### 🌐 多接口访问
- **Web界面**: 直观的可视化搜索界面
- **REST API**: 完整的RESTful API接口
- **命令行**: 便捷的CLI工具
- **SDK支持**: Python SDK和示例代码

### ⚡ 高性能架构
- **优化存储**: SQLite + 向量索引的混合存储
- **缓存机制**: 多层缓存提升查询速度
- **并发处理**: 支持高并发搜索请求
- **资源优化**: 内存和CPU使用优化

### 🔧 企业级特性
- **Docker支持**: 容器化部署，一键启动
- **配置管理**: 灵活的YAML配置系统
- **日志监控**: 结构化日志和性能监控
- **安全性**: 输入验证和安全防护

## 📁 项目结构

```
├── src/                    # 源代码目录
│   ├── core/              # 核心功能模块
│   │   ├── enhanced_search_engine.py  # 主搜索引擎
│   │   ├── database.py               # 数据库操作
│   │   ├── semantic_search.py        # 语义搜索
│   │   ├── tree_parser.py           # 代码解析器
│   │   └── indexer.py               # 索引构建器
│   ├── api/               # API服务模块
│   │   ├── api_server.py            # REST API服务器
│   │   ├── api_wsgi.py              # WSGI应用
│   │   └── web.py                   # Web界面
│   ├── mcp/               # MCP协议模块
│   │   ├── mcp_server.py            # MCP服务器
│   │   └── fastmcp_server.py        # 快速MCP服务器
│   ├── tools/             # 工具和演示
│   │   └── demo.py                  # 演示程序
│   └── config/            # 配置文件
│       ├── config.yaml              # 主配置文件
│       └── mcp_config.yaml          # MCP配置文件
├── examples/              # 示例代码
│   ├── api_client_example.py        # API客户端示例
│   ├── mcp_client_example.py        # MCP客户端示例
│   └── demo_repo/                   # 演示代码库
├── docs/                  # 文档目录
│   ├── api/               # API文档
│   ├── mcp/               # MCP文档
│   └── setup/             # 安装配置文档
├── test/                  # 测试文件
├── scripts/               # 脚本文件
├── grammars/              # Tree-sitter语法文件
├── temp/                  # 临时文件
├── requirements.txt       # Python依赖（包含MCP支持）
└── setup.py              # 安装脚本
```

## 🚀 快速开始

### 📋 环境要求

- **Python**: 3.8+ (推荐 3.11+)
- **内存**: 4GB+ RAM (推荐 8GB+)
- **存储**: 2GB+ 可用磁盘空间
- **AI编辑器**: Trae、Claude、Cursor 或其他支持MCP的工具

### ⚡ 一键安装

```bash
# 1. 克隆项目
git clone https://github.com/sokis/CodeLens.git
cd CodeLens

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据库
python src/core/database.py --init

# 4. 启动MCP服务器
python src/mcp/fastmcp_server.py
```

### 🔧 AI编辑器配置

#### Trae AI 配置
```json
{
  "mcpServers": {
    "code-search": {
      "command": "python",
      "args": ["/path/to/CodeLens/src/mcp/fastmcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/CodeLens/src"
      }
    }
  }
}
```

#### Claude Desktop 配置
在 `~/.claude/claude_desktop_config.json` 中添加：
```json
{
  "mcpServers": {
    "code-search": {
      "command": "python",
      "args": ["/path/to/CodeLens/src/mcp/fastmcp_server.py"],
      "env": {}
    }
  }
}
```

#### Cursor 配置
在 Cursor 设置中添加 MCP 服务器：
```json
{
  "mcp.servers": [
    {
      "name": "code-search",
      "command": "python",
      "args": ["/path/to/CodeLens/src/mcp/fastmcp_server.py"]
    }
  ]
}
```

### 🎯 启动服务

```bash
# 启动MCP服务器（推荐）
python src/mcp/fastmcp_server.py

# 指定配置文件
python src/mcp/fastmcp_server.py --config custom_config.yaml

# 查看帮助
python src/mcp/fastmcp_server.py --help
```

### 🔍 基本使用

启动服务后，在你的AI编辑器中就可以使用以下功能：

#### 代码搜索
```
# 在AI编辑器中询问：
"搜索处理用户认证的函数"
"找到所有数据库连接相关的代码"
"查找支付处理的逻辑"
```

#### 代码理解
```
# AI编辑器会自动调用MCP工具：
- search_code: 搜索相关代码片段
- get_file_content: 获取完整文件内容
- get_function_details: 获取函数详细信息
- get_database_stats: 查看索引统计
```

#### 项目分析
```
# 让AI帮你分析项目：
"这个项目的架构是什么样的？"
"有哪些主要的模块和功能？"
"代码质量如何，有什么改进建议？"
```

#### API 服务器模式
```bash
# 启动 REST API 服务器
python src/api/api_server.py

# 访问 Web 界面
open http://localhost:8000
```

#### 手动索引代码库
```bash
# 索引当前目录
python -c "
from src.core.indexer import CodeIndexer
indexer = CodeIndexer()
indexer.index_directory('.')
"
```

#### 直接搜索代码
```python
from src.core.semantic_search import SemanticSearchEngine

# 创建搜索引擎
search_engine = SemanticSearchEngine()

# 执行搜索
results = search_engine.search("用户认证相关的函数")
for result in results:
    print(f"文件: {result['file_path']}")
    print(f"函数: {result['function_name']}")
    print(f"相似度: {result['similarity']:.2f}")
```

### 🐳 Docker部署

```bash
# 拉取镜像
docker pull codelens:latest

# 运行容器
docker run -d \
  --name codelens \
  -p 8080:8080 \
  -p 3000:3000 \
  -v /path/to/your/code:/workspace \
  codelens:latest

# 访问Web界面
open http://localhost:8080
```

### 🔧 配置说明

创建配置文件 `config.yaml`：

```yaml
# 基础配置
server:
  host: "0.0.0.0"
  port: 3000
  debug: false

# 搜索引擎配置
search:
  max_results: 50
  similarity_threshold: 0.7
  enable_semantic: true

# 数据库配置
database:
  path: "./data/code_search.db"
  backup_enabled: true

# 支持的语言
languages:
  - python
  - javascript
  - java
  - go
  - typescript
```

## 💡 使用示例

### 🌐 Web界面使用

```bash
# 启动Web服务器
codelens-mcp web --port 8080

# 访问界面
open http://localhost:8080
```

**功能特点**:
- 🔍 实时搜索建议
- 📊 搜索结果可视化
- 🎯 代码高亮显示
- 📁 项目结构浏览

### 🔌 MCP协议集成

#### 与Claude Desktop集成

在 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "code-search": {
      "command": "codelens-mcp",
      "args": ["mcp-server"],
      "env": {
        "CODE_PATH": "/path/to/your/code"
      }
    }
  }
}
```

#### 可用的MCP工具

- `search_code`: 搜索代码片段
- `get_file_content`: 获取文件内容
- `get_function_details`: 获取函数详情
- `get_database_stats`: 获取索引统计

### 🚀 REST API使用

```python
import requests

# 搜索代码
response = requests.get(
    "http://localhost:3000/api/search",
    params={"q": "authentication function", "limit": 10}
)
results = response.json()

# 获取文件内容
response = requests.get(
    "http://localhost:3000/api/file",
    params={"path": "src/auth.py"}
)
content = response.json()

# 添加到索引
response = requests.post(
    "http://localhost:3000/api/index",
    json={"path": "/new/code/directory"}
)
```

### 🐍 Python SDK

```python
from mcp_code_search import CodeSearchClient

# 创建客户端
client = CodeSearchClient("http://localhost:3000")

# 搜索代码
results = client.search("user authentication", limit=5)
for result in results:
    print(f"File: {result.file_path}")
    print(f"Function: {result.function_name}")
    print(f"Score: {result.similarity_score}")

# 获取函数详情
details = client.get_function("authenticate_user")
print(f"Parameters: {details.parameters}")
print(f"Return type: {details.return_type}")
```

### 🖥️ 命令行工具

```bash
# 搜索代码
codelens-mcp query "database connection"

# 查看索引状态
codelens-mcp status

# 重建索引
codelens-mcp reindex --path /path/to/code

# 导出搜索结果
codelens-mcp export --query "api endpoints" --format json
```

## 📚 文档

### 📖 核心文档
- [AI编辑器集成指南](docs/AI_EDITOR_INTEGRATION.md) - Trae、Claude、Cursor等配置详解
- [MCP 配置指南](docs/MCP_SETUP_GUIDE.md) - MCP 协议配置和使用
- [快速开始教程](docs/QUICK_START.md) - 5分钟快速上手指南

### 🔧 技术文档
- [架构设计](docs/ARCHITECTURE.md) - 系统架构和设计理念
- [API 参考](docs/API_REFERENCE.md) - 完整的API接口文档
- [性能优化](docs/PERFORMANCE.md) - 性能调优和最佳实践

### 🎯 使用指南
- [搜索技巧](docs/SEARCH_TIPS.md) - 如何写出更好的搜索查询
- [配置选项](docs/CONFIGURATION.md) - 详细的配置参数说明
- [故障排除](docs/TROUBLESHOOTING.md) - 常见问题和解决方案

## 🧪 测试和验证

### 运行测试
```bash
# 运行所有测试
python -m pytest test/ -v

# 运行特定测试
python -m pytest test/test_semantic_search.py -v

# 运行性能测试
python test/test_performance.py
```

### 验证安装
```bash
# 检查服务状态
python status.sh

# 测试基本功能
python test/test_basic.py
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 🐛 报告问题
- 使用 GitHub Issues 报告 bug
- 提供详细的错误信息和重现步骤
- 包含系统环境信息

### 💡 功能建议
- 在 Issues 中提出新功能建议
- 详细描述功能需求和使用场景
- 讨论实现方案

### 🔧 代码贡献
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 📝 开发规范
- 遵循 PEP 8 代码风格
- 添加适当的测试用例
- 更新相关文档
- 确保所有测试通过

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢以下开源项目的支持：
- [Model Context Protocol](https://github.com/modelcontextprotocol) - MCP 协议标准
- [Sentence Transformers](https://github.com/UKPLab/sentence-transformers) - 语义搜索引擎
- [Tree-sitter](https://github.com/tree-sitter/tree-sitter) - 代码解析器
- [FastAPI](https://github.com/tiangolo/fastapi) - Web 框架
- [SpaCy](https://github.com/explosion/spaCy) - 自然语言处理

## 📞 支持与联系

- **文档**: [项目文档](docs/)
- **示例**: [使用示例](examples/)
- **问题反馈**: [GitHub Issues](https://github.com/your-org/mcp-code-search-server/issues)

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个 Star！**

Made with ❤️ for the developer community

</div>