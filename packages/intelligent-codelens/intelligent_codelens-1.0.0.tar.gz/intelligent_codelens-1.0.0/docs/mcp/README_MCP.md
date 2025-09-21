# MCP 代码搜索模块

这是一个基于 Model Context Protocol (MCP) 的代码搜索模块，允许AI通过MCP协议按需搜索和访问代码库。

## 功能特性

### 🔍 代码搜索工具
- **search_code**: 搜索代码库中的函数、类和其他代码元素
- **get_file_content**: 获取指定文件的完整内容或指定行范围
- **get_function_details**: 获取指定函数的详细信息
- **get_database_stats**: 获取代码库的统计信息

### 📊 资源管理
- **config://server**: 服务器配置信息
- **stats://database**: 数据库统计信息

### 🛡️ 安全特性
- 路径访问控制
- 文件大小限制
- 超时保护
- 错误处理

## 文件结构

```
├── mcp_server.py           # MCP服务器主程序
├── mcp_config.yaml         # 服务器配置文件
├── mcp_client_example.py   # 客户端测试示例
├── start_mcp_server.sh     # 服务器启动脚本
├── requirements.txt        # 项目依赖（包含MCP支持）
└── README_MCP.md          # 本说明文档
```

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置服务器

编辑 `mcp_config.yaml` 文件，根据需要调整配置：

```yaml
# 数据库配置
database:
  file: "search.db"

# 搜索配置
search:
  max_results: 50
  default_limit: 10

# 代码库配置
repository:
  path: "."
  supported_languages:
    - python
    - javascript
    - java
    # ... 更多语言
```

### 3. 确保数据库存在

在启动MCP服务器之前，确保已经运行过代码索引器：

```bash
python3 indexer.py
```

## 使用方法

### 启动服务器

使用提供的启动脚本：

```bash
./start_mcp_server.sh
```

或直接运行：

```bash
python3 mcp_server.py
```

### 客户端连接

MCP服务器通过stdio协议与客户端通信。客户端可以是：

1. **AI助手**: 支持MCP协议的AI助手可以直接连接
2. **测试客户端**: 使用提供的测试客户端

```bash
python3 mcp_client_example.py
```

## MCP工具详解

### 1. search_code

搜索代码库中的函数、类和其他代码元素。

**参数**:
- `query` (必需): 搜索查询字符串
- `limit` (可选): 返回结果数量限制 (默认: 10)
- `file_type` (可选): 文件类型过滤

**示例**:
```json
{
  "query": "支付状态",
  "limit": 5,
  "file_type": "python"
}
```

### 2. get_file_content

获取指定文件的内容。

**参数**:
- `file_path` (必需): 文件路径
- `start_line` (可选): 起始行号
- `end_line` (可选): 结束行号

**示例**:
```json
{
  "file_path": "examples/demo_repo/payment_dao.py",
  "start_line": 1,
  "end_line": 50
}
```

### 3. get_function_details

获取指定函数的详细信息。

**参数**:
- `function_name` (必需): 函数名称
- `file_path` (可选): 文件路径，用于精确匹配

**示例**:
```json
{
  "function_name": "create_payment",
  "file_path": "examples/demo_repo/payment_dao.py"
}
```

### 4. get_database_stats

获取代码库的统计信息。

**参数**: 无

**返回**: 包含文件数量、函数数量、类数量等统计信息

## 配置选项

### 数据库配置
- `file`: 数据库文件路径
- `backup_enabled`: 是否启用备份
- `backup_interval`: 备份间隔（秒）

### 搜索配置
- `max_results`: 最大搜索结果数
- `default_limit`: 默认结果数量限制
- `enable_fuzzy_search`: 是否启用模糊搜索
- `min_relevance_score`: 最小相关性分数

### 安全配置
- `allowed_paths`: 允许访问的路径列表
- `forbidden_paths`: 禁止访问的路径列表
- `max_file_read_size`: 最大文件读取大小

### 性能配置
- `max_file_size`: 最大文件大小限制
- `batch_size`: 批处理大小
- `timeout`: 超时时间
- `cache_enabled`: 是否启用缓存

## 日志和调试

服务器日志配置在 `mcp_config.yaml` 中：

```yaml
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "mcp_server.log"
```

查看日志：

```bash
tail -f mcp_server.log
```

## 故障排除

### 常见问题

1. **服务器启动失败**
   - 检查Python版本 (需要 3.8+)
   - 确保安装了所有依赖
   - 检查配置文件语法

2. **搜索无结果**
   - 确保数据库文件存在
   - 检查索引是否完整
   - 验证搜索查询语法

3. **文件访问被拒绝**
   - 检查安全配置中的路径限制
   - 确保文件路径正确
   - 验证文件权限

### 调试模式

启用调试模式：

```bash
export MCP_DEBUG=1
python3 mcp_server.py
```

## 扩展开发

### 添加新工具

1. 在 `CodeSearchMCPServer` 类中添加工具定义
2. 实现对应的处理函数
3. 更新配置文件（如需要）

### 自定义搜索算法

可以通过修改 `semantic_search.py` 来自定义搜索算法，MCP服务器会自动使用新的搜索引擎。

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0
- 初始版本
- 基本的代码搜索功能
- MCP协议支持
- 安全和性能优化