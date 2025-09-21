# MCP 代码搜索服务器配置指南

## 概述

本MCP（Model Context Protocol）服务器提供强大的代码搜索和分析功能。为了让其他用户能够安全有效地使用，请按照以下步骤进行配置。

## 快速开始

### 1. 环境准备

确保系统已安装：
- Python 3.8+
- 必要的依赖包（运行 `pip install -r requirements.txt`）

### 2. 基础配置

#### 修改搜索目录

编辑 `config/mcp_config.yaml` 文件：

```yaml
repository:
  # 设置要搜索的代码目录
  path: "/path/to/your/project"  # 修改为实际项目路径
```

**示例配置：**
- 搜索当前目录：`path: "."`
- 搜索特定项目：`path: "/Users/username/projects/my-project"`
- 搜索多个目录：需要在代码中动态配置

#### 配置安全访问路径

```yaml
security:
  allowed_paths:
    - "."                    # 当前目录
    - "./src"               # 源代码目录
    - "./docs"              # 文档目录
    - "/path/to/your/project"  # 添加你的项目路径
```

### 3. 启动服务器

#### 方式一：FastMCP服务器（推荐）
```bash
cd /path/to/local-code
python src/mcp/fastmcp_server.py
```

#### 方式二：标准MCP服务器
```bash
cd /path/to/local-code
python src/mcp/mcp_server.py
```

## 详细配置说明

### 搜索目录配置

搜索目录主要在以下位置配置：

1. **主配置文件**：`config/mcp_config.yaml`
   ```yaml
   repository:
     path: "."  # 修改为目标目录
   ```

2. **安全路径**：限制可访问的目录
   ```yaml
   security:
     allowed_paths:
       - "."
       - "./src"
       - "./examples"
       # 添加更多允许的路径
   ```

### 忽略文件配置

配置要忽略的文件和目录：

```yaml
repository:
  ignore_patterns:
    - "*.pyc"
    - "__pycache__"
    - ".git"
    - "node_modules"
    - ".vscode"
    - "*.log"
    - "dist"
    - "build"
```

### 安全设置

#### 允许访问的路径
```yaml
security:
  allowed_paths:
    - "."                    # 当前目录
    - "./src"               # 源代码目录
    - "./examples"          # 示例目录
    - "./docs"              # 文档目录
    - "./tests"             # 测试目录
```

#### 禁止访问的路径（系统安全）
```yaml
security:
  forbidden_paths:
    - "/etc"                # 系统配置
    - "/var"                # 系统变量
    - "/usr"                # 系统程序
    - "~/.ssh"              # SSH密钥
    - "~/.aws"              # AWS凭证
```

## 使用场景配置

### 场景1：个人项目
```yaml
repository:
  path: "/Users/username/my-project"
security:
  allowed_paths:
    - "/Users/username/my-project"
    - "/Users/username/my-project/src"
```

### 场景2：团队共享项目
```yaml
repository:
  path: "/shared/projects/team-project"
security:
  allowed_paths:
    - "/shared/projects/team-project"
    - "/shared/projects/team-project/src"
    - "/shared/projects/team-project/docs"
```

### 场景3：多项目搜索
需要在代码中动态配置，或者启动多个服务器实例。

## 性能优化

### 文件大小限制
```yaml
performance:
  max_file_size: 1048576    # 1MB
  batch_size: 100
  timeout: 30
  cache_enabled: true
  cache_size: 1000

security:
  max_file_read_size: 5242880  # 5MB
```

### 缓存配置
```yaml
search:
  cache_size: 1000          # 搜索结果缓存大小
  similarity_threshold: 0.7  # 相似度阈值
```

## 常见问题

### Q1: 如何搜索多个目录？
A: 目前需要在 `allowed_paths` 中添加所有需要的目录，或者修改代码支持多路径。

### Q2: 如何提高搜索性能？
A: 
- 增加缓存大小
- 优化忽略模式，排除不必要的文件
- 调整批处理大小

### Q3: 安全性如何保证？
A: 
- 严格配置 `allowed_paths` 和 `forbidden_paths`
- 设置文件大小限制
- 定期检查配置文件

### Q4: 如何添加新的编程语言支持？
A: 在 `supported_languages` 中添加语言名称，并确保相应的解析器可用。

## 注意事项

1. **路径安全**：确保 `allowed_paths` 只包含必要的目录
2. **文件权限**：确保MCP服务器有读取目标目录的权限
3. **资源限制**：根据系统资源调整缓存和批处理大小
4. **定期更新**：定期重新索引代码库以获取最新内容

## 技术支持

如遇问题，请检查：
1. 配置文件语法是否正确
2. 路径是否存在且有访问权限
3. 依赖包是否完整安装
4. 日志文件中的错误信息

---

配置完成后，其他用户就可以通过MCP客户端连接到你的代码搜索服务器，安全地搜索和分析指定的代码库了。