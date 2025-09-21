# API服务模块 (src/api/)

本目录包含各种接口服务的实现，为搜索引擎提供多种访问方式。

## 📋 模块概览

### api_server.py
**REST API服务器**
- 提供标准的HTTP REST接口
- 支持JSON格式的请求和响应
- 包含完整的API端点定义
- 支持跨域请求(CORS)

**主要端点：**
```
GET  /search?q=<query>&mode=<mode>    # 搜索代码
POST /index                           # 添加文件到索引
GET  /stats                          # 获取索引统计
GET  /health                         # 健康检查
DELETE /index/<file_id>              # 从索引中删除文件
```

### api_wsgi.py
**WSGI应用包装器**
- 用于生产环境部署
- 兼容各种WSGI服务器（Gunicorn、uWSGI等）
- 提供应用程序入口点
- 支持中间件和扩展

**部署示例：**
```bash
# 使用Gunicorn部署
gunicorn -w 4 -b 0.0.0.0:8000 src.api.api_wsgi:application

# 使用uWSGI部署
uwsgi --http :8000 --wsgi-file src/api/api_wsgi.py
```

### web.py
**Web界面服务器**
- 提供用户友好的搜索界面
- 基于Flask的Web应用
- 包含HTML模板和静态资源
- 支持实时搜索和结果展示

**主要功能：**
- 搜索表单和结果展示
- 代码高亮显示
- 分页和排序功能
- 响应式设计

## 🚀 使用方法

### 启动REST API服务器
```bash
python src/api/api_server.py
```
默认运行在 `http://localhost:8000`

### 启动Web界面
```bash
python src/api/web.py
```
默认运行在 `http://localhost:5000`

### 生产部署
```bash
# 使用Gunicorn部署API服务
gunicorn -w 4 -b 0.0.0.0:8000 src.api.api_wsgi:application

# 使用Nginx反向代理
# 配置文件示例在 docs/deployment/ 目录中
```

## 📡 API接口文档

### 搜索接口
```http
GET /search?q=function&mode=semantic&limit=10

Response:
{
  "results": [
    {
      "file_path": "/path/to/file.py",
      "function_name": "example_function",
      "line_number": 42,
      "code_snippet": "def example_function():",
      "score": 0.95
    }
  ],
  "total": 1,
  "query_time": 0.123
}
```

### 索引接口
```http
POST /index
Content-Type: application/json

{
  "file_path": "/path/to/new_file.py",
  "content": "def new_function(): pass"
}

Response:
{
  "status": "success",
  "message": "File indexed successfully",
  "file_id": "abc123"
}
```

### 统计接口
```http
GET /stats

Response:
{
  "total_files": 1234,
  "total_functions": 5678,
  "total_classes": 890,
  "index_size": "45.6 MB",
  "last_updated": "2024-01-01T12:00:00Z"
}
```

## 🔧 配置说明

API服务的配置通过 `config/config.yaml` 管理：

```yaml
api:
  host: "0.0.0.0"
  port: 8000
  debug: false
  cors_enabled: true
  max_results: 100

web:
  host: "0.0.0.0"
  port: 5000
  debug: false
  template_folder: "templates"
  static_folder: "static"
```

## 🛡️ 安全考虑

### 输入验证
- 所有用户输入都经过验证和清理
- 防止SQL注入和XSS攻击
- 限制查询长度和复杂度

### 访问控制
- 支持API密钥认证
- 请求频率限制
- IP白名单功能

### 错误处理
- 不暴露敏感的系统信息
- 统一的错误响应格式
- 详细的日志记录

## 📊 性能优化

### 缓存策略
- 查询结果缓存
- 静态资源缓存
- 数据库连接池

### 并发处理
- 异步请求处理
- 连接复用
- 负载均衡支持

## 🧪 测试

API模块的测试文件：
- `test/test_web.py` - Web界面测试
- `test/test_integration.py` - 集成测试

运行测试：
```bash
cd test/
python test_web.py
```

## 📝 开发指南

### 添加新的API端点
1. 在 `api_server.py` 中定义路由
2. 实现处理函数
3. 添加输入验证
4. 更新API文档
5. 编写测试用例

### 自定义中间件
```python
from flask import Flask, request

def auth_middleware():
    # 认证逻辑
    pass

app = Flask(__name__)
app.before_request(auth_middleware)
```

### 错误处理
```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
```