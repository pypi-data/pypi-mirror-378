# TRAE AI 使用 uvx 配置 MCP 指南

## 概述

本指南详细介绍如何在 TRAE AI 中使用 `uvx` 工具配置和运行 intelligent-codelens MCP 服务器，实现智能代码搜索功能。

## 什么是 uvx？

`uvx` 是一个现代的 Python 包执行工具，类似于 `npx`，可以直接运行 Python 包而无需全局安装。它具有以下优势：

- 🚀 **无需安装** - 直接运行包，无需全局安装
- 🔄 **自动管理** - 自动处理依赖和虚拟环境
- ⚡ **快速启动** - 缓存机制，快速启动应用
- 🛡️ **环境隔离** - 每个包运行在独立环境中

## 前置要求

### 1. 安装 uv 工具

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 Homebrew (macOS)
brew install uv

# 验证安装
uv --version
```

### 2. 确保 Python 环境

```bash
# 检查 Python 版本 (需要 3.8+)
python3 --version
```

## TRAE AI 配置步骤

### 方法一：使用 uvx 直接运行（推荐）

#### 1. 在 TRAE AI 中配置 MCP 服务器

1. **打开 TRAE AI 设置**：
   - 点击 AI 对话框右上角的 **设置** 图标
   - 选择 **MCP** 选项

2. **添加 MCP 服务器**：
   - 点击 **+ 添加 MCP Servers** 按钮
   - 选择 **手动添加**

3. **填写配置信息**：

```json
{
  "name": "intelligent-codelens",
  "command": "uvx",
  "args": [
    "--from",
    "intelligent-codelens",
    "codelens-mcp"
  ],
  "env": {
    "CODE_PATH": "/Users/zengyi/work/2025/local-code"
  },
  "cwd": "/Users/zengyi/work/2025/local-code"
}
```

#### 2. 配置参数说明

| 参数 | 值 | 说明 |
|------|----|----|
| **名称** | `intelligent-codelens` | MCP 服务器名称 |
| **命令** | `uvx` | 使用 uvx 工具 |
| **参数** | `--from intelligent-codelens codelens-mcp` | 从 PyPI 安装并运行 |
| **环境变量** | `CODE_PATH: /path/to/your/project` | 要搜索的代码路径 |
| **工作目录** | `/path/to/your/project` | 项目根目录 |

### 方法二：指定版本运行

如果需要使用特定版本的 intelligent-codelens：

```json
{
  "name": "intelligent-codelens-v1.0.5",
  "command": "uvx",
  "args": [
    "--from",
    "intelligent-codelens==1.0.5",
    "codelens-mcp"
  ],
  "env": {
    "CODE_PATH": "/Users/zengyi/work/2025/local-code",
    "LOG_LEVEL": "INFO"
  },
  "cwd": "/Users/zengyi/work/2025/local-code"
}
```

### 方法三：使用配置文件

#### 1. 创建 TRAE 配置文件

在项目根目录创建 `.trae/mcp.json`：

```json
{
  "mcpServers": {
    "intelligent-codelens": {
      "name": "智能代码搜索引擎",
      "description": "基于 uvx 的智能代码搜索服务",
      "command": "uvx",
      "args": [
        "--from",
        "intelligent-codelens",
        "codelens-mcp"
      ],
      "env": {
        "CODE_PATH": "/Users/zengyi/work/2025/local-code",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUNBUFFERED": "1"
      },
      "cwd": "/Users/zengyi/work/2025/local-code",
      "timeout": 30000,
      "restart": true
    }
  }
}
```

#### 2. 在 TRAE 中导入配置

1. 在 TRAE AI 的 MCP 设置页面
2. 点击 **导入配置** 按钮
3. 选择 `.trae/mcp.json` 文件

## 验证配置

### 1. 检查服务器状态

在 TRAE AI 的 MCP 设置页面中，确认服务器状态为 **已连接**。

### 2. 测试功能

在 TRAE AI 对话框中输入以下测试命令：

```
搜索支付相关的函数
```

预期响应：
```
🔍 正在搜索支付相关的函数...

找到以下相关函数：
1. process_payment() - 处理支付逻辑
2. validate_payment() - 验证支付信息
3. refund_payment() - 处理退款
```

### 3. 验证命令行

也可以在终端中直接测试：

```bash
# 测试 uvx 运行
uvx --from intelligent-codelens codelens-mcp --help

# 预期输出应显示帮助信息
```

## 可用工具

配置成功后，TRAE AI 可以使用以下 MCP 工具：

### 🔍 search_code
**功能**：搜索代码库中的函数、类和其他代码元素

**使用示例**：
```
搜索用户认证相关的代码
查找数据库连接函数
寻找错误处理逻辑
```

### 📄 get_file_content
**功能**：获取指定文件的内容

**使用示例**：
```
显示 main.py 文件的内容
查看配置文件 config.yaml
```

### 🔧 get_function_details
**功能**：获取指定函数的详细信息

**使用示例**：
```
分析 authenticate_user 函数
查看 process_payment 函数的实现
```

### 📊 get_database_stats
**功能**：获取代码库的统计信息

**使用示例**：
```
显示项目统计信息
分析代码库结构
```

## 高级配置

### 环境变量配置

可以通过环境变量自定义服务器行为：

```json
{
  "env": {
    "CODE_PATH": "/path/to/your/project",
    "LOG_LEVEL": "DEBUG",
    "MAX_RESULTS": "20",
    "SEARCH_TIMEOUT": "30",
    "CACHE_ENABLED": "true"
  }
}
```

### 多项目配置

如果需要为不同项目配置不同的 MCP 服务器：

```json
{
  "mcpServers": {
    "project-a-codelens": {
      "name": "项目A代码搜索",
      "command": "uvx",
      "args": ["--from", "intelligent-codelens", "codelens-mcp"],
      "env": {
        "CODE_PATH": "/path/to/project-a"
      },
      "cwd": "/path/to/project-a"
    },
    "project-b-codelens": {
      "name": "项目B代码搜索",
      "command": "uvx",
      "args": ["--from", "intelligent-codelens", "codelens-mcp"],
      "env": {
        "CODE_PATH": "/path/to/project-b"
      },
      "cwd": "/path/to/project-b"
    }
  }
}
```

## 故障排除

### 常见问题

#### 1. uvx 命令未找到

**错误信息**：`command not found: uvx`

**解决方案**：
```bash
# 重新安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 重新加载 shell 配置
source ~/.bashrc  # 或 ~/.zshrc
```

#### 2. 包安装失败

**错误信息**：`Failed to install intelligent-codelens`

**解决方案**：
```bash
# 清理 uv 缓存
uv cache clean

# 手动测试安装
uvx --from intelligent-codelens codelens-mcp --help
```

#### 3. 服务器连接失败

**可能原因**：
- 路径配置错误
- 权限问题
- Python 版本不兼容

**解决方案**：
```bash
# 检查路径是否存在
ls -la /path/to/your/project

# 检查 Python 版本
python3 --version

# 查看详细错误日志
uvx --from intelligent-codelens codelens-mcp --debug
```

#### 4. 搜索无结果

**可能原因**：
- 代码路径配置错误
- 项目中没有支持的代码文件

**解决方案**：
1. 确认 `CODE_PATH` 环境变量指向正确的项目目录
2. 检查项目中是否包含 Python、JavaScript 等支持的代码文件
3. 查看服务器日志获取详细信息

### 调试模式

启用调试模式获取更多信息：

```json
{
  "env": {
    "LOG_LEVEL": "DEBUG",
    "MCP_DEBUG": "1"
  }
}
```

## 性能优化

### 1. 缓存配置

uvx 会自动缓存已安装的包，提高启动速度：

```bash
# 查看缓存状态
uv cache info

# 清理缓存（如果需要）
uv cache clean
```

### 2. 预热缓存

首次使用前可以预热缓存：

```bash
# 预先安装包到缓存
uvx --from intelligent-codelens codelens-mcp --version
```

## 最佳实践

### 1. 版本管理

建议在生产环境中固定版本：

```json
{
  "args": [
    "--from",
    "intelligent-codelens==1.0.5",
    "codelens-mcp"
  ]
}
```

### 2. 环境隔离

为不同项目使用不同的配置：

```bash
# 项目A
export CODE_PATH="/path/to/project-a"
uvx --from intelligent-codelens codelens-mcp

# 项目B  
export CODE_PATH="/path/to/project-b"
uvx --from intelligent-codelens codelens-mcp
```

### 3. 监控和日志

启用适当的日志级别：

```json
{
  "env": {
    "LOG_LEVEL": "INFO"
  }
}
```

## 相关文档

- [TRAE MCP 配置指南](./TRAE_MCP_CONFIG.md)
- [MCP 服务器配置指南](../MCP_SETUP_GUIDE.md)
- [AI 编辑器集成指南](../AI_EDITOR_INTEGRATION.md)
- [uv 官方文档](https://docs.astral.sh/uv/)

---

*配置完成后，您就可以在 TRAE AI 中通过 uvx 享受智能代码搜索功能了！* 🚀