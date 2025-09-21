#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web 搜索服务
基于 Flask 的代码搜索 Web 界面和 API
"""

import os
import json
import sys
from pathlib import Path
import time
from flask import Flask, request, jsonify, render_template_string, send_from_directory

# 导入本地模块
# 添加核心模块路径
core_path = Path(__file__).parent.parent / "core"
sys.path.insert(0, str(core_path))

# 直接使用绝对导入，避免相对导入问题
try:
    from core.semantic_search import SemanticSearchEngine
    from core.database import CodeDatabase
except ImportError:
    # 如果绝对导入失败，尝试直接导入
    try:
        from semantic_search import SemanticSearchEngine
        from database import CodeDatabase
    except ImportError:
        # 最后尝试从当前包导入
        import semantic_search
        import database
        SemanticSearchEngine = semantic_search.SemanticSearchEngine
        CodeDatabase = database.CodeDatabase

import yaml


class CodeSearchWebApp:
    """代码搜索 Web 应用"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化 Web 应用
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.search_engine = SemanticSearchEngine(config_path)
        self.db = CodeDatabase(self.config['db_file'])
        
        # 创建 Flask 应用
        self.app = Flask(__name__)
        self.app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key-only-not-for-production')  # 生产环境必须设置FLASK_SECRET_KEY环境变量
        
        # 注册路由
        self._register_routes()
    
    def _load_config(self, config_path: str) -> dict:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _register_routes(self):
        """注册 Flask 路由"""
        
        @self.app.route('/')
        def index():
            """主页"""
            return render_template_string(self._get_index_template())
        
        @self.app.route('/api/search', methods=['POST'])
        def api_search():
            """搜索 API"""
            try:
                # 首先尝试解析JSON，如果失败则返回400错误
                try:
                    data = request.get_json(force=True)
                except Exception as json_error:
                    return jsonify({'error': '无效的JSON格式'}), 400
                
                if not data or 'query' not in data:
                    return jsonify({'error': '缺少查询参数'}), 400
                
                query = data['query'].strip()
                if not query:
                    return jsonify({'error': '查询不能为空'}), 400
                
                limit = data.get('limit', self.config.get('max_results', 10))
                
                # 执行搜索
                start_time = time.time()
                results = self.search_engine.search(query, limit)
                search_time = time.time() - start_time
                
                # 格式化结果
                formatted_results = []
                for result in results:
                    formatted_result = {
                        'id': result['id'],
                        'name': result['name'],
                        'type': result['type'],
                        'file_path': result['file_path'],
                        'language': result['language'],
                        'start_line': result['start_line'],
                        'end_line': result['end_line'],
                        'relevance_score': round(result['relevance_score'], 2),
                        'docstring': result.get('docstring', ''),
                        'parameters': result.get('parameters', []),
                        'code_snippet': self._get_code_snippet(result)
                    }
                    formatted_results.append(formatted_result)
                
                return jsonify({
                    'query': query,
                    'results': formatted_results,
                    'total_count': len(formatted_results),
                    'search_time': round(search_time, 3)
                })
                
            except Exception as e:
                return jsonify({'error': f'搜索失败: {str(e)}'}), 500
        
        @self.app.route('/api/stats')
        def api_stats():
            """获取统计信息 API"""
            try:
                stats = self.db.get_stats()
                # 添加CORS头部以支持跨域请求
                response = jsonify(stats)
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
            except Exception as e:
                return jsonify({'error': f'获取统计信息失败: {str(e)}'}), 500
        
        @self.app.route('/api/history')
        def api_history():
            """获取搜索历史 API"""
            try:
                limit = request.args.get('limit', 20, type=int)
                history = self.db.get_search_history(limit)
                return jsonify(history)
            except Exception as e:
                return jsonify({'error': f'获取搜索历史失败: {str(e)}'}), 500
        
        @self.app.route('/api/file/<path:file_path>')
        def api_file_content(file_path):
            """获取文件内容 API"""
            try:
                # 安全检查：确保文件路径在允许的范围内
                if not self._is_safe_path(file_path):
                    return jsonify({'error': '文件路径不安全'}), 403
                
                if not os.path.exists(file_path):
                    return jsonify({'error': '文件不存在'}), 404
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                return jsonify({
                    'file_path': file_path,
                    'content': content,
                    'line_count': len(content.splitlines())
                })
                
            except Exception as e:
                return jsonify({'error': f'读取文件失败: {str(e)}'}), 500
        
        @self.app.errorhandler(404)
        def not_found(error):
            """404 错误处理"""
            return jsonify({'error': '页面未找到'}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            """500 错误处理"""
            return jsonify({'error': '服务器内部错误'}), 500
    
    def _get_code_snippet(self, result: dict, context_lines: int = 3) -> str:
        """
        获取代码片段
        
        Args:
            result: 搜索结果
            context_lines: 上下文行数
            
        Returns:
            代码片段
        """
        try:
            file_path = result['file_path']
            start_line = max(1, result['start_line'] - context_lines)
            end_line = result['end_line'] + context_lines
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                # 提取指定行范围
                snippet_lines = lines[start_line-1:end_line]
                snippet = ''.join(snippet_lines)
                
                return snippet
            
        except Exception as e:
            print(f"获取代码片段失败: {e}")
        
        return result.get('body', '')[:500] + '...' if result.get('body') else ''
    
    def _is_safe_path(self, file_path: str) -> bool:
        """
        检查文件路径是否安全
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否安全
        """
        # 基本安全检查
        if '..' in file_path or file_path.startswith('/'):
            return False
        
        # 检查是否在允许的目录范围内
        repo_path = self.config.get('repo_path', '')
        if repo_path and not file_path.startswith(repo_path):
            return False
        
        return True
    
    def _get_index_template(self) -> str:
        """
        获取主页 HTML 模板
        
        Returns:
            HTML 模板字符串
        """
        return '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>本地代码语义搜索</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .search-section {
            padding: 40px;
            background: #f8f9fa;
        }
        
        .search-box {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .search-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .search-btn {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .search-btn:hover {
            transform: translateY(-2px);
        }
        
        .search-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #6c757d;
            margin-top: 5px;
        }
        
        .results {
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .result-item {
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            transition: background-color 0.2s;
        }
        
        .result-item:hover {
            background-color: #f8f9fa;
        }
        
        .result-item:last-child {
            border-bottom: none;
        }
        
        .result-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .result-name {
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .result-type {
            background: #667eea;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin-left: 10px;
        }
        
        .result-score {
            color: #28a745;
            font-weight: bold;
            margin-left: auto;
        }
        
        .result-meta {
            color: #6c757d;
            margin-bottom: 10px;
        }
        
        .result-description {
            color: #495057;
            margin-bottom: 10px;
            font-style: italic;
        }
        
        .result-code {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 15px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9em;
            overflow-x: auto;
            white-space: pre;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #6c757d;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        
        .search-info {
            text-align: center;
            color: #6c757d;
            margin-bottom: 20px;
        }
        
        @media (max-width: 768px) {
            .search-box {
                flex-direction: column;
            }
            
            .stats {
                flex-direction: column;
                gap: 20px;
            }
            
            .result-header {
                flex-direction: column;
                align-items: flex-start;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 本地代码语义搜索</h1>
            <p>TreeSitter + SQLite + NLP 驱动的智能代码搜索引擎</p>
        </div>
        
        <div class="search-section">
            <div class="search-box">
                <input type="text" class="search-input" id="searchInput" 
                       placeholder="输入搜索内容，如：支付状态更新函数、用户登录验证..." 
                       onkeypress="handleKeyPress(event)">
                <button class="search-btn" id="searchBtn" onclick="performSearch()">搜索</button>
            </div>
            
            <div class="stats" id="stats">
                <div class="stat-item">
                    <div class="stat-number" id="totalFiles">-</div>
                    <div class="stat-label">文件数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="totalFunctions">-</div>
                    <div class="stat-label">函数数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="totalClasses">-</div>
                    <div class="stat-label">类数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="dbSize">-</div>
                    <div class="stat-label">索引大小</div>
                </div>
            </div>
            
            <div id="searchInfo" class="search-info" style="display: none;"></div>
            <div id="error" class="error" style="display: none;"></div>
            <div id="loading" class="loading" style="display: none;">
                <p>🔍 搜索中...</p>
            </div>
            
            <div id="results" class="results"></div>
        </div>
    </div>

    <script>
        // 页面加载时获取统计信息
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
        });
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                performSearch();
            }
        }
        
        async function loadStats() {
            try {
                console.log('开始加载统计信息...');
                const response = await fetch('/api/stats');
                const stats = await response.json();
                console.log('API返回数据:', stats);
                
                document.getElementById('totalFiles').textContent = stats.files || 0;
                document.getElementById('totalFunctions').textContent = stats.functions || 0;
                document.getElementById('totalClasses').textContent = stats.classes || 0;
                document.getElementById('dbSize').textContent = (stats.db_size_mb || 0).toFixed(1) + ' MB';
                console.log('统计信息更新完成');
            } catch (error) {
                console.error('加载统计信息失败:', error);
            }
        }
        
        async function performSearch() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) {
                showError('请输入搜索内容');
                return;
            }
            
            hideError();
            showLoading(true);
            
            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query: query })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    displayResults(data);
                } else {
                    showError(data.error || '搜索失败');
                }
            } catch (error) {
                showError('网络错误: ' + error.message);
            } finally {
                showLoading(false);
            }
        }
        
        function displayResults(data) {
            const resultsDiv = document.getElementById('results');
            const searchInfoDiv = document.getElementById('searchInfo');
            
            // 显示搜索信息
            searchInfoDiv.innerHTML = `找到 <strong>${data.total_count}</strong> 个结果，耗时 <strong>${data.search_time}</strong> 秒`;
            searchInfoDiv.style.display = 'block';
            
            if (data.results.length === 0) {
                resultsDiv.innerHTML = '<div class="loading"><p>😔 没有找到相关结果</p></div>';
                return;
            }
            
            let html = '';
            data.results.forEach(result => {
                html += `
                    <div class="result-item">
                        <div class="result-header">
                            <span class="result-name">${escapeHtml(result.name)}</span>
                            <span class="result-type">${result.type}</span>
                            <span class="result-score">分数: ${result.relevance_score}</span>
                        </div>
                        <div class="result-meta">
                            📁 ${escapeHtml(result.file_path)} (${result.language}) 
                            📍 第 ${result.start_line}-${result.end_line} 行
                        </div>
                        ${result.docstring ? `<div class="result-description">${escapeHtml(result.docstring)}</div>` : ''}
                        ${result.parameters && result.parameters.length > 0 ? 
                            `<div class="result-meta">参数: ${result.parameters.join(', ')}</div>` : ''}
                        ${result.code_snippet ? 
                            `<div class="result-code">${escapeHtml(result.code_snippet)}</div>` : ''}
                    </div>
                `;
            });
            
            resultsDiv.innerHTML = html;
        }
        
        function showLoading(show) {
            const loadingDiv = document.getElementById('loading');
            const searchBtn = document.getElementById('searchBtn');
            
            loadingDiv.style.display = show ? 'block' : 'none';
            searchBtn.disabled = show;
            searchBtn.textContent = show ? '搜索中...' : '搜索';
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
        
        function hideError() {
            const errorDiv = document.getElementById('error');
            errorDiv.style.display = 'none';
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
        '''
    
    def run(self, host: str = None, port: int = None, debug: bool = None):
        """
        启动 Web 服务
        
        Args:
            host: 主机地址
            port: 端口号
            debug: 调试模式
        """
        host = host or self.config.get('web_host', 'localhost')
        port = port or self.config.get('web_port', 5000)
        debug = debug if debug is not None else self.config.get('debug', False)
        
        print(f"🚀 启动代码搜索服务...")
        print(f"📍 访问地址: http://{host}:{port}")
        print(f"🔍 数据库: {self.config['db_file']}")
        print(f"📁 仓库路径: {self.config.get('repo_path', 'N/A')}")
        
        self.app.run(host=host, port=port, debug=debug)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="代码搜索 Web 服务")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--host", default="localhost", help="主机地址")
    parser.add_argument("--port", type=int, default=5000, help="端口号")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    
    args = parser.parse_args()
    
    # 创建并启动 Web 应用
    app = CodeSearchWebApp(args.config)
    app.run(host=args.host, port=args.port, debug=args.debug)


# 创建全局app实例供导入使用（使用默认配置避免文件依赖）
try:
    app = CodeSearchWebApp()
except Exception:
    # 如果配置文件不存在，创建一个最小化的app实例
    app = None

if __name__ == "__main__":
    main()