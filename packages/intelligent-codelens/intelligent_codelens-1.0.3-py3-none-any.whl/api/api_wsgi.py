#!/usr/bin/env python3
"""
API 服务器 WSGI 入口文件
用于生产环境部署
"""
from api_server import CodeSearchAPIServer

# 创建应用实例
server = CodeSearchAPIServer("config.yaml")
app = server.app

if __name__ == "__main__":
    app.run()