# 配置文件 (config/)

本目录包含项目的所有配置文件，用于管理不同组件的设置和参数。

## 📁 文件说明

### config.yaml
**主配置文件**
- 搜索引擎核心配置
- 数据库连接设置
- 语义搜索参数
- 索引器配置

**主要配置项**:
```yaml
# 数据库配置
database:
  path: "code_search.db"
  
# 搜索配置
search:
  max_results: 100
  similarity_threshold: 0.7
  
# 语义搜索配置
semantic:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  embedding_dim: 384
  
# 索引配置
indexer:
  supported_extensions: [".py", ".js", ".java", ".cpp", ".c", ".h"]
  max_file_size: 1048576  # 1MB
```

### mcp_config.yaml
**MCP服务器配置文件**
- MCP服务器设置
- 工具配置
- 客户端连接参数

**主要配置项**:
```yaml
# MCP服务器配置
server:
  name: "code-search-mcp"
  version: "1.0.0"
  
# 工具配置
tools:
  search_code:
    enabled: true
    max_results: 50
  
  index_file:
    enabled: true
    max_file_size: 1048576
    
  get_stats:
    enabled: true
```

## 🔧 配置说明

### 数据库配置
- **path**: SQLite数据库文件路径
- **connection_pool_size**: 连接池大小
- **timeout**: 连接超时时间

### 搜索配置
- **max_results**: 最大搜索结果数量
- **similarity_threshold**: 语义相似度阈值
- **search_modes**: 支持的搜索模式

### 语义搜索配置
- **model_name**: 使用的预训练模型
- **embedding_dim**: 嵌入向量维度
- **batch_size**: 批处理大小

### 索引配置
- **supported_extensions**: 支持的文件扩展名
- **max_file_size**: 最大文件大小限制
- **exclude_patterns**: 排除的文件模式

## 🚀 使用方法

### 加载配置
```python
import yaml
from pathlib import Path

def load_config(config_file="config/config.yaml"):
    """加载配置文件"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# 使用示例
config = load_config()
db_path = config['database']['path']
max_results = config['search']['max_results']
```

### 环境变量覆盖
支持使用环境变量覆盖配置：

```bash
# 覆盖数据库路径
export CODE_SEARCH_DB_PATH="/custom/path/database.db"

# 覆盖最大结果数
export CODE_SEARCH_MAX_RESULTS=200

# 覆盖语义模型
export CODE_SEARCH_SEMANTIC_MODEL="sentence-transformers/paraphrase-MiniLM-L6-v2"
```

### 配置验证
```python
def validate_config(config):
    """验证配置文件的有效性"""
    required_keys = ['database', 'search', 'semantic', 'indexer']
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config section: {key}")
    
    # 验证数据库配置
    if 'path' not in config['database']:
        raise ValueError("Database path not specified")
    
    # 验证搜索配置
    if config['search']['max_results'] <= 0:
        raise ValueError("max_results must be positive")
    
    return True
```

## 🔒 安全配置

### 敏感信息处理
- 使用环境变量存储敏感信息
- 不在配置文件中硬编码密码或密钥
- 使用配置文件模板

### 配置文件权限
```bash
# 设置适当的文件权限
chmod 600 config/config.yaml
chmod 600 config/mcp_config.yaml
```

## 🧪 测试配置

### 测试环境配置
创建测试专用的配置文件：

```yaml
# test_config.yaml
database:
  path: ":memory:"  # 使用内存数据库
  
search:
  max_results: 10
  
semantic:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  
indexer:
  supported_extensions: [".py"]
  max_file_size: 10240  # 10KB for testing
```

### 配置测试
```python
import pytest
from src.config.config_loader import load_config, validate_config

def test_config_loading():
    """测试配置加载"""
    config = load_config("config/test_config.yaml")
    assert config is not None
    assert 'database' in config

def test_config_validation():
    """测试配置验证"""
    config = load_config("config/config.yaml")
    assert validate_config(config) == True
```

## 📝 配置最佳实践

### 1. 配置分层
- 基础配置：默认设置
- 环境配置：开发/测试/生产环境特定设置
- 用户配置：用户自定义设置

### 2. 配置文档
- 为每个配置项添加注释
- 提供配置示例
- 说明配置的影响和限制

### 3. 配置验证
- 在启动时验证配置
- 提供清晰的错误信息
- 支持配置热重载

### 4. 版本控制
- 提供配置模板文件
- 不提交包含敏感信息的配置
- 使用 .gitignore 排除本地配置