# 源代码目录 (src/)

本目录包含项目的所有源代码，按功能模块组织。

## 📁 目录结构

### core/ - 核心功能模块
包含搜索引擎的核心功能实现：

- **enhanced_search_engine.py** - 主搜索引擎类，整合所有搜索功能
- **database.py** - 数据库操作和管理，处理代码索引的存储
- **semantic_search.py** - 语义搜索实现，基于向量嵌入
- **tree_parser.py** - 代码解析器，使用Tree-sitter进行语法分析
- **indexer.py** - 索引构建器，负责代码文件的索引化

### api/ - API服务模块
提供各种接口服务：

- **api_server.py** - REST API服务器，提供HTTP接口
- **api_wsgi.py** - WSGI应用包装器，用于生产部署
- **web.py** - Web界面服务器，提供用户友好的搜索界面

### mcp/ - MCP协议模块
实现Model Context Protocol支持：

- **mcp_server.py** - 标准MCP服务器实现
- **fastmcp_server.py** - 优化的快速MCP服务器

### tools/ - 工具和演示
辅助工具和演示程序：

- **demo.py** - 演示程序，展示搜索引擎的基本功能

### config/ - 配置文件
系统配置文件：

- **config.yaml** - 主配置文件，包含数据库、搜索等配置
- **mcp_config.yaml** - MCP服务专用配置文件

## 🔧 模块依赖关系

```
enhanced_search_engine.py
├── database.py
├── semantic_search.py
├── tree_parser.py
└── indexer.py

api_server.py
├── database.py
└── semantic_search.py

web.py
├── database.py
└── semantic_search.py

mcp_server.py
├── database.py
└── semantic_search.py
```

## 🚀 使用说明

### 核心模块使用
```python
from src.core.enhanced_search_engine import EnhancedSearchEngine

# 初始化搜索引擎
engine = EnhancedSearchEngine()

# 执行搜索
results = engine.search("function definition")
```

### API服务使用
```bash
# 启动REST API服务
python src/api/api_server.py

# 启动Web界面
python src/api/web.py
```

### MCP服务使用
```bash
# 启动MCP服务器
python src/mcp/mcp_server.py

# 启动快速MCP服务器
python src/mcp/fastmcp_server.py
```

## 📝 开发注意事项

1. **导入路径**: 使用相对导入或绝对导入，确保模块间正确引用
2. **配置管理**: 所有配置应通过config/目录中的YAML文件管理
3. **错误处理**: 每个模块都应包含适当的错误处理和日志记录
4. **文档**: 保持代码注释和文档的更新

## 🧪 测试

每个模块都应有对应的测试文件在test/目录中。运行测试前确保已安装所有依赖。