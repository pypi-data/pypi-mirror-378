# AI编辑器配置示例

本目录包含了各种AI编辑器的MCP代码搜索服务配置示例。

## 配置文件说明

### 🎯 Trae AI
- **文件**: `trae_config.json`
- **特点**: 完整的MCP服务器配置，包含AI助手集成设置
- **功能**: 智能代码分析、自动搜索、上下文感知建议

### 🤖 Claude Desktop
- **文件**: `claude_desktop_config.json`
- **特点**: 简洁的配置格式，支持全局快捷键
- **功能**: 代码高亮、行号显示、主题自适应

### 🎯 Cursor
- **文件**: `cursor_config.json`
- **特点**: 深度集成AI代码补全和聊天功能
- **功能**: MCP上下文集成、自动搜索阈值、编辑器集成

### 📝 VS Code
- **文件**: `vscode_mcp_config.json`
- **特点**: 标准MCP客户端配置
- **功能**: 自动重启、日志记录、扩展管理

## 使用方法

### 1. 修改路径
将配置文件中的 `/absolute/path/to/mcp-code-search` 替换为实际的项目路径：

```bash
# 获取当前项目路径
pwd
# 例如: /Users/username/projects/mcp-code-search
```

### 2. 配置搜索目录
在 `mcp_config.yaml` 中设置要搜索的代码目录：

```yaml
search_directories:
  - "/path/to/your/project1"
  - "/path/to/your/project2"
```

### 3. 应用配置

#### Trae AI
```bash
# 将配置复制到Trae配置目录
cp trae_config.json ~/.trae/mcp_servers.json
```

#### Claude Desktop
```bash
# macOS
cp claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Windows
cp claude_desktop_config.json %APPDATA%\Claude\claude_desktop_config.json
```

#### Cursor
```bash
# 在Cursor设置中导入MCP配置
# Settings > Extensions > MCP > Import Configuration
```

#### VS Code
```bash
# 安装MCP扩展后，在设置中配置
# Settings > Extensions > MCP Client > Configuration
```

## 验证配置

### 启动测试
```bash
# 测试MCP服务器
python src/mcp/fastmcp_server.py --test

# 检查配置文件
python -c "import yaml; print(yaml.safe_load(open('config/mcp_config.yaml')))"
```

### 功能测试
1. **代码搜索**: 在AI编辑器中搜索函数或类名
2. **文件内容**: 请求查看特定文件内容
3. **函数详情**: 获取函数签名和文档
4. **数据库统计**: 查看索引状态和性能指标

## 故障排除

### 常见问题
1. **路径错误**: 确保所有路径都是绝对路径
2. **权限问题**: 检查Python和配置文件的执行权限
3. **依赖缺失**: 运行 `pip install -r requirements.txt`
4. **端口冲突**: 检查是否有其他服务占用相同端口

### 调试技巧
```bash
# 启用详细日志
export MCP_LOG_LEVEL=DEBUG
python src/mcp/fastmcp_server.py

# 检查进程状态
ps aux | grep fastmcp_server

# 查看日志文件
tail -f logs/mcp_server.log
```

## 性能优化

### 推荐设置
- **搜索结果数量**: 10-20个（平衡性能和完整性）
- **缓存启用**: 建议开启以提高响应速度
- **超时设置**: 30秒（适合大型项目）
- **重启策略**: 启用自动重启以确保稳定性

### 大型项目优化
```yaml
# mcp_config.yaml 优化配置
performance:
  max_file_size: 1048576  # 1MB
  cache_size: 1000
  index_batch_size: 100
  search_timeout: 10
```

## 技术支持

如果遇到问题，请检查：
1. Python版本 (>= 3.8)
2. 依赖包版本
3. 配置文件语法
4. 文件路径权限
5. 网络连接状态

更多帮助请参考主项目文档或提交Issue。