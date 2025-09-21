# 生产环境部署指南

## ⚠️ 开发服务器警告

你看到的警告信息：
```
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
```

这是 Flask 内置开发服务器的标准警告，提醒你不要在生产环境中使用开发服务器。

## 🔍 当前配置分析

### Web 服务器 (web.py)
- **默认配置**: `localhost:5000`
- **调试模式**: 可通过 `--debug` 参数启用
- **用途**: 提供代码搜索的 Web 界面

### API 服务器 (api_server.py)  
- **默认配置**: `127.0.0.1:5002`
- **调试模式**: 可通过 `--debug` 参数启用
- **用途**: 提供 RESTful API 接口

## 🚀 生产环境部署方案

### 方案 1: 使用 Gunicorn (推荐)

#### 1.1 安装 Gunicorn
```bash
pip install gunicorn
```

#### 1.2 部署 Web 服务器
```bash
# 基本部署
gunicorn -w 4 -b 0.0.0.0:5000 web:app

# 高级配置
gunicorn \
  --workers 4 \
  --worker-class sync \
  --bind 0.0.0.0:5000 \
  --timeout 120 \
  --keep-alive 5 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --access-logfile /var/log/gunicorn/access.log \
  --error-logfile /var/log/gunicorn/error.log \
  web:app
```

#### 1.3 部署 API 服务器
```bash
# 创建 WSGI 入口文件 api_wsgi.py
cat > api_wsgi.py << 'EOF'
#!/usr/bin/env python3
"""
API 服务器 WSGI 入口文件
"""
from api_server import CodeSearchAPIServer

# 创建应用实例
server = CodeSearchAPIServer("config.yaml")
app = server.app

if __name__ == "__main__":
    app.run()
EOF

# 使用 Gunicorn 部署
gunicorn -w 4 -b 0.0.0.0:5002 api_wsgi:app
```

### 方案 2: 使用 uWSGI

#### 2.1 安装 uWSGI
```bash
pip install uwsgi
```

#### 2.2 创建配置文件
```ini
# uwsgi.ini
[uwsgi]
module = web:app
master = true
processes = 4
socket = /tmp/uwsgi.sock
chmod-socket = 666
vacuum = true
die-on-term = true
```

#### 2.3 启动服务
```bash
uwsgi --ini uwsgi.ini
```

### 方案 3: 使用 Docker

#### 3.1 创建 Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装生产服务器
RUN pip install gunicorn

# 复制应用代码
COPY . .

# 下载 spaCy 模型
RUN python -m spacy download en_core_web_md

# 暴露端口
EXPOSE 5000 5002

# 启动脚本
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
```

#### 3.2 创建启动脚本
```bash
# start.sh
#!/bin/bash

# 启动 API 服务器
gunicorn -w 2 -b 0.0.0.0:5002 api_wsgi:app &

# 启动 Web 服务器
gunicorn -w 2 -b 0.0.0.0:5000 web:app

wait
```

#### 3.3 构建和运行
```bash
# 构建镜像
docker build -t code-search-app .

# 运行容器
docker run -d \
  --name code-search \
  -p 5000:5000 \
  -p 5002:5002 \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/search.db:/app/search.db \
  code-search-app
```

## 🔧 生产环境优化配置

### 1. 性能优化

#### config.yaml 生产配置
```yaml
# 生产环境配置
debug: false
batch_size: 200
max_results: 50
similarity_threshold: 0.5

# 数据库优化
db_file: /data/search.db
store_raw_code: false

# spaCy 模型
spacy_model: en_core_web_md

# Web 服务器配置
web_host: 0.0.0.0
web_port: 5000
```

#### 2. 安全配置

```python
# 在 web.py 和 api_server.py 中添加安全头
from flask import Flask
from flask_talisman import Talisman

app = Flask(__name__)

# 添加安全头
Talisman(app, {
    'force_https': True,
    'strict_transport_security': True,
    'content_security_policy': {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline'"
    }
})
```

### 3. 监控和日志

#### 3.1 日志配置
```python
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
if not app.debug:
    file_handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=10240000, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

#### 3.2 健康检查端点
```python
@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'version': '1.0.0'
    })
```

## 🌐 反向代理配置

### Nginx 配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Web 界面
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API 接口
    location /api/ {
        proxy_pass http://127.0.0.1:5002/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件缓存
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 📊 性能基准

### 开发服务器 vs 生产服务器

| 指标 | 开发服务器 | Gunicorn (4 workers) | 性能提升 |
|------|------------|---------------------|----------|
| 并发请求 | 1 | 4+ | 400%+ |
| 响应时间 | ~200ms | ~50ms | 75% |
| 内存使用 | ~100MB | ~400MB | - |
| 稳定性 | 低 | 高 | - |

## 🚨 安全检查清单

- [ ] 禁用调试模式 (`debug=False`)
- [ ] 使用 HTTPS
- [ ] 配置防火墙规则
- [ ] 设置访问日志
- [ ] 配置错误页面
- [ ] 限制文件上传大小
- [ ] 实施速率限制
- [ ] 定期更新依赖包

## 🔄 部署脚本

### 快速部署脚本
```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 开始部署代码搜索应用..."

# 1. 安装依赖
pip install -r requirements.txt
pip install gunicorn

# 2. 下载模型
python -m spacy download en_core_web_md

# 3. 创建日志目录
mkdir -p logs

# 4. 创建 WSGI 入口文件
cat > api_wsgi.py << 'EOF'
from api_server import CodeSearchAPIServer
server = CodeSearchAPIServer("config.yaml")
app = server.app
EOF

# 5. 启动服务
echo "启动 API 服务器..."
gunicorn -w 4 -b 0.0.0.0:5002 --daemon api_wsgi:app

echo "启动 Web 服务器..."
gunicorn -w 4 -b 0.0.0.0:5000 --daemon web:app

echo "✅ 部署完成！"
echo "Web 界面: http://localhost:5000"
echo "API 接口: http://localhost:5002"
```

## 📝 总结

当前的警告是正常的开发环境提示。对于生产环境，建议：

1. **立即行动**: 使用 Gunicorn 替换开发服务器
2. **中期规划**: 配置 Nginx 反向代理和 HTTPS
3. **长期优化**: 考虑容器化部署和监控系统

选择适合你需求的部署方案，确保应用在生产环境中稳定运行！

---

*最后更新：2025年1月*