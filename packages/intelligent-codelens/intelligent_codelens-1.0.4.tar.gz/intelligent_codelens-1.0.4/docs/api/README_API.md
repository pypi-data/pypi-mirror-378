# 代码搜索API服务器

## 概述

这是一个基于Flask的RESTful API服务器，为AI系统提供代码搜索和分析功能。服务器集成了语义搜索引擎，支持中英文代码搜索、文件内容获取、函数详情查询等功能。

## 功能特性

- 🔍 **语义搜索**: 支持中英文代码语义搜索
- 📁 **文件管理**: 获取文件内容和结构信息
- 🔧 **函数分析**: 查询函数详情和代码片段
- 📊 **统计信息**: 提供数据库统计和索引状态
- 🌐 **CORS支持**: 支持跨域请求
- 📝 **详细日志**: 完整的请求和错误日志

## 快速开始

### 1. 安装依赖

```bash
# 安装Python依赖
pip install Flask Flask-CORS PyYAML requests jieba sentence-transformers tree-sitter
```

### 2. 启动服务器

```bash
# 使用默认配置启动 (127.0.0.1:5000)
python3 api_server.py

# 指定主机和端口
python3 api_server.py --host 127.0.0.1 --port 5002

# 指定配置文件
python3 api_server.py --config custom_config.yaml
```

### 3. 验证服务

```bash
# 健康检查
curl http://127.0.0.1:5002/api/health

# 获取API信息
curl http://127.0.0.1:5002/api/info
```

## API端点

### 1. 健康检查
- **URL**: `GET /api/health`
- **描述**: 检查服务器运行状态
- **响应**:
```json
{
  "success": true,
  "status": "healthy",
  "message": "代码搜索API服务器运行正常"
}
```

### 2. API信息
- **URL**: `GET /api/info`
- **描述**: 获取API版本和端点信息
- **响应**:
```json
{
  "success": true,
  "api_name": "代码搜索API",
  "version": "1.0.0",
  "endpoints": {
    "GET /api/health": "健康检查",
    "GET /api/info": "获取API信息",
    "POST /api/search": "搜索代码",
    "POST /api/file": "获取文件内容",
    "POST /api/function": "获取函数详情",
    "GET /api/stats": "获取统计信息"
  }
}
```

### 3. 代码搜索
- **URL**: `POST /api/search`
- **描述**: 搜索代码片段和函数
- **请求体**:
```json
{
  "query": "支付状态",
  "limit": 10,
  "file_types": ["py", "js"],
  "include_content": true
}
```
- **响应**:
```json
{
  "success": true,
  "query": "支付状态",
  "total_results": 5,
  "results": [
    {
      "file_path": "examples/demo_repo/payment_dao.py",
      "function_name": "update_payment_status",
      "type": "function",
      "score": 0.95,
      "content": "def update_payment_status(order_id, status):\n    ..."
    }
  ]
}
```

### 4. 获取文件内容
- **URL**: `POST /api/file`
- **描述**: 获取指定文件的内容
- **请求体**:
```json
{
  "file_path": "examples/demo_repo/order_service.py",
  "start_line": 1,
  "end_line": 50
}
```
- **响应**:
```json
{
  "success": true,
  "file_path": "examples/demo_repo/order_service.py",
  "content": "\"\"\"订单服务模块\"\"\"\n\nclass OrderService:\n    ...",
  "total_lines": 120,
  "start_line": 1,
  "end_line": 50
}
```

### 5. 获取函数详情
- **URL**: `POST /api/function`
- **描述**: 获取指定函数的详细信息
- **请求体**:
```json
{
  "function_name": "update_payment_status",
  "file_path": "examples/demo_repo/payment_dao.py"
}
```
- **响应**:
```json
{
  "success": true,
  "function_name": "update_payment_status",
  "file_path": "examples/demo_repo/payment_dao.py",
  "start_line": 15,
  "end_line": 25,
  "content": "def update_payment_status(order_id, status):\n    ...",
  "docstring": "更新订单支付状态",
  "parameters": ["order_id", "status"]
}
```

### 6. 统计信息
- **URL**: `GET /api/stats`
- **描述**: 获取数据库统计信息
- **响应**:
```json
{
  "success": true,
  "stats": {
    "files": 7,
    "functions": 30,
    "classes": 6,
    "db_size_mb": 0.14
  }
}
```

## 客户端示例

项目包含完整的客户端示例 `api_client_example.py`，演示如何使用所有API端点：

```bash
# 运行客户端示例
python3 api_client_example.py

# 交互模式
python3 api_client_example.py --interactive
```

## 配置选项

服务器支持通过配置文件自定义行为，默认配置文件为 `config.yaml`：

```yaml
# 数据库配置
database:
  path: "search.db"
  
# 搜索引擎配置
search:
  model_name: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
  max_results: 50
  
# 服务器配置
server:
  host: "127.0.0.1"
  port: 5000
  debug: false
```

## 错误处理

API使用标准HTTP状态码和统一的错误响应格式：

```json
{
  "success": false,
  "error": "错误描述",
  "error_type": "ValidationError",
  "details": {
    "field": "query",
    "message": "查询参数不能为空"
  }
}
```

常见错误码：
- `400`: 请求参数错误
- `404`: 资源未找到
- `500`: 服务器内部错误

## 性能优化

- 使用缓存机制提高搜索性能
- 支持分页查询大量结果
- 异步处理长时间运行的任务
- 连接池管理数据库连接

## 安全考虑

- 输入验证和清理
- 路径遍历攻击防护
- 请求频率限制
- CORS配置管理

## 开发和调试

启用调试模式：
```bash
python3 api_server.py --debug
```

查看详细日志：
```bash
tail -f api_server.log
```

## 部署建议

生产环境建议使用WSGI服务器：

```bash
# 使用Gunicorn
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5002 api_server:app

# 使用uWSGI
pip install uwsgi
uwsgi --http 127.0.0.1:5002 --wsgi-file api_server.py --callable app
```

## 许可证

MIT License