# MCP协议模块 (src/mcp/)

本目录实现Model Context Protocol (MCP) 支持，为AI模型提供代码搜索和分析能力。

## 📋 模块概览

### mcp_server.py
**标准MCP服务器实现**
- 完整的MCP协议支持
- 标准化的工具和资源接口
- 支持多种MCP客户端
- 完整的错误处理和日志记录

**主要工具：**
```python
# 搜索工具
search_code(query, mode='hybrid', limit=10)

# 索引工具
index_file(file_path)
index_directory(directory_path)

# 分析工具
analyze_code_structure(file_path)
get_function_info(file_path, function_name)

# 统计工具
get_search_stats()
```

### fastmcp_server.py
**优化的快速MCP服务器**
- 基于FastMCP框架的高性能实现
- 异步处理和并发优化
- 更快的响应时间
- 适合高频率调用场景

**性能特点：**
- 异步I/O处理
- 连接池优化
- 内存缓存机制
- 批量操作支持

## 🚀 使用方法

### 启动标准MCP服务器
```bash
python src/mcp/mcp_server.py
```

### 启动快速MCP服务器
```bash
python src/mcp/fastmcp_server.py
```

### 使用启动脚本
```bash
./start_mcp_server.sh
```

## 🔧 MCP工具详解

### 搜索工具 (search_code)
**功能**: 在代码库中搜索相关代码片段

**参数**:
- `query` (string): 搜索查询
- `mode` (string): 搜索模式 ('keyword', 'semantic', 'hybrid')
- `limit` (integer): 结果数量限制

**返回**:
```json
{
  "results": [
    {
      "file_path": "/path/to/file.py",
      "function_name": "example_function",
      "line_number": 42,
      "code_snippet": "def example_function():",
      "score": 0.95,
      "context": "surrounding code context"
    }
  ],
  "total": 1,
  "query_time": 0.123
}
```

### 索引工具 (index_file/index_directory)
**功能**: 将文件或目录添加到搜索索引

**参数**:
- `file_path` / `directory_path` (string): 文件或目录路径

**返回**:
```json
{
  "status": "success",
  "indexed_files": 42,
  "skipped_files": 3,
  "errors": []
}
```

### 代码分析工具 (analyze_code_structure)
**功能**: 分析代码文件的结构信息

**参数**:
- `file_path` (string): 文件路径

**返回**:
```json
{
  "file_info": {
    "language": "python",
    "lines_of_code": 150,
    "functions": [
      {
        "name": "example_function",
        "line_start": 10,
        "line_end": 25,
        "parameters": ["param1", "param2"],
        "docstring": "Function description"
      }
    ],
    "classes": [
      {
        "name": "ExampleClass",
        "line_start": 30,
        "line_end": 80,
        "methods": ["method1", "method2"]
      }
    ]
  }
}
```

### 统计工具 (get_search_stats)
**功能**: 获取搜索索引的统计信息

**返回**:
```json
{
  "total_files": 1234,
  "total_functions": 5678,
  "total_classes": 890,
  "supported_languages": ["python", "javascript", "java"],
  "index_size": "45.6 MB",
  "last_updated": "2024-01-01T12:00:00Z"
}
```

## ⚙️ 配置说明

MCP服务的配置通过 `config/mcp_config.yaml` 管理：

```yaml
mcp:
  server_name: "local-code-search"
  version: "1.0.0"
  description: "Local code search and analysis tools"
  
  # 服务器配置
  host: "localhost"
  port: 3000
  
  # 工具配置
  tools:
    search_code:
      enabled: true
      max_results: 100
      timeout: 30
    
    index_file:
      enabled: true
      max_file_size: "10MB"
      supported_extensions: [".py", ".js", ".java", ".cpp"]
    
    analyze_code:
      enabled: true
      include_docstrings: true
      include_comments: false

  # 性能配置
  performance:
    max_concurrent_requests: 10
    cache_size: 1000
    cache_ttl: 3600
```

## 🔌 客户端集成

### Claude Desktop集成
在Claude Desktop的配置文件中添加：

```json
{
  "mcpServers": {
    "local-code-search": {
      "command": "python",
      "args": ["/path/to/src/mcp/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/project"
      }
    }
  }
}
```

### 其他MCP客户端
支持任何符合MCP协议的客户端，包括：
- Claude Desktop
- 自定义MCP客户端
- 其他AI工具和IDE插件

## 🛠️ 开发指南

### 添加新的MCP工具
1. 在服务器类中定义新工具
2. 实现工具处理函数
3. 添加参数验证
4. 更新工具列表
5. 编写测试用例

**示例**:
```python
@server.tool()
async def new_tool(query: str) -> dict:
    """
    新工具的描述
    
    Args:
        query: 查询参数
        
    Returns:
        工具执行结果
    """
    # 工具实现逻辑
    result = process_query(query)
    return {"result": result}
```

### 错误处理
```python
from mcp.server.models import McpError

try:
    # 工具逻辑
    pass
except Exception as e:
    raise McpError(
        code="TOOL_ERROR",
        message=f"Tool execution failed: {str(e)}"
    )
```

## 🧪 测试

MCP模块的测试文件：
- `test/test_all_mcp_tools.py` - 所有MCP工具测试
- `examples/mcp_client_example.py` - 客户端示例

运行测试：
```bash
cd test/
python test_all_mcp_tools.py
```

## 📊 性能监控

### 日志记录
- 请求/响应日志
- 性能指标记录
- 错误追踪

### 监控指标
- 请求处理时间
- 并发连接数
- 工具调用频率
- 错误率统计

## 🔍 故障排除

### 常见问题
1. **连接失败**: 检查端口和防火墙设置
2. **工具不可用**: 验证配置文件和依赖
3. **性能问题**: 检查索引大小和缓存配置
4. **内存使用过高**: 调整批处理大小和缓存设置

### 调试模式
```bash
# 启用调试模式
export MCP_DEBUG=1
python src/mcp/mcp_server.py
```