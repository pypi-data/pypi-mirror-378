# Trae IDE MCP 配置指南

## 概述

本指南将帮助您在 Trae IDE 中配置和使用当前项目的 MCP (Model Context Protocol) 代码搜索服务器。

## 配置步骤

### 1. 创建 .trae 目录

在项目根目录下创建 `.trae` 目录（如果不存在）：

```bash
mkdir -p .trae
```

### 2. 配置 MCP 服务器

在 `.trae` 目录下创建 `mcp.json` 配置文件：

```json
{
  "mcpServers": {
    "code-search-server": {
      "command": "python3",
      "args": [
        "/Users/zengyi/work/2025/local-code/mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/zengyi/work/2025/local-code"
      },
      "cwd": "/Users/zengyi/work/2025/local-code"
    }
  }
}
```

### 3. 在 Trae IDE 中启用 MCP

1. **打开 MCP 设置**：
   - 在 AI 侧边对话框的右上角，点击 **设置** 图标
   - 在菜单中选择 **MCP**

2. **添加 MCP 服务器**：
   - 点击 **+ 添加 MCP Servers** 按钮
   - 选择 **手动添加**

3. **填写配置信息**：
   - **名称**: `code-search-server`
   - **命令**: `python3`
   - **参数**: `/Users/zengyi/work/2025/local-code/mcp_server.py`
   - **工作目录**: `/Users/zengyi/work/2025/local-code`
   - **环境变量**: 
     - `PYTHONPATH`: `/Users/zengyi/work/2025/local-code`

4. **确认配置**：
   - 点击 **确认** 按钮
   - 等待服务器连接成功

## 可用工具

配置成功后，您可以在 Trae IDE 中使用以下 MCP 工具：

### 🔍 search_code
搜索代码库中的函数、类和其他代码元素

**使用示例**：
```
搜索支付相关的函数
```

### 📄 get_file_content
获取指定文件的内容

**使用示例**：
```
获取 payment_dao.py 文件的内容
```

### 🔧 get_function_details
获取指定函数的详细信息

**使用示例**：
```
获取 create_payment 函数的详细信息
```

### 📊 get_database_stats
获取代码库的统计信息

**使用示例**：
```
显示代码库统计信息
```

## 验证配置

### 1. 检查服务器状态

在 Trae IDE 的 MCP 设置页面中，确认 `code-search-server` 的状态为 **已连接**。

### 2. 测试工具功能

在 AI 对话框中输入以下命令测试：

```
/search_code 支付
```

如果配置正确，AI 助手将能够搜索并返回相关的代码结果。

## 故障排除

### 常见问题

1. **服务器连接失败**
   - 确保 Python 3.8+ 已安装
   - 检查文件路径是否正确
   - 验证工作目录权限

2. **工具不可用**
   - 重启 Trae IDE
   - 重新配置 MCP 服务器
   - 检查服务器日志

3. **搜索无结果**
   - 确保数据库文件 `search.db` 存在
   - 运行索引器：`python3 indexer.py`
   - 检查配置文件 `mcp_config.yaml`

### 调试步骤

1. **检查服务器日志**：
   ```bash
   tail -f mcp_server.log
   ```

2. **手动测试服务器**：
   ```bash
   cd /Users/zengyi/work/2025/local-code
   python3 mcp_server.py
   ```

3. **验证依赖**：
   ```bash
   pip install -r requirements.txt
   ```

## 高级配置

### 自定义搜索参数

您可以在 `mcp_config.yaml` 中调整搜索参数：

```yaml
search:
  max_results: 50
  default_limit: 10
  enable_fuzzy_search: true
  min_relevance_score: 0.1
```

### 添加环境变量

在 MCP 配置中添加更多环境变量：

```json
{
  "mcpServers": {
    "code-search-server": {
      "command": "python3",
      "args": ["/Users/zengyi/work/2025/local-code/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/Users/zengyi/work/2025/local-code",
        "MCP_DEBUG": "1",
        "LOG_LEVEL": "DEBUG"
      },
      "cwd": "/Users/zengyi/work/2025/local-code"
    }
  }
}
```

## 最佳实践

1. **定期更新索引**：
   ```bash
   python3 indexer.py
   ```

2. **监控服务器性能**：
   - 检查内存使用情况
   - 监控响应时间
   - 定期清理日志

3. **备份配置文件**：
   - 将 `.trae/mcp.json` 加入版本控制
   - 定期备份 `mcp_config.yaml`

4. **安全考虑**：
   - 限制文件访问权限
   - 定期更新依赖包
   - 监控异常访问

## 相关文档

- [MCP 服务器配置指南](../MCP_SETUP_GUIDE.md)
- [代码搜索模块说明](./README_MCP.md)
- [Trae IDE 官方文档](https://docs.trae.ai/)

---

*配置完成后，您就可以在 Trae IDE 中享受智能代码搜索功能了！*