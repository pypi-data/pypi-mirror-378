#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码搜索API服务器
为AI提供RESTful接口来搜索和访问代码
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
import yaml

from core.semantic_search import SemanticSearchEngine
from core.database import CodeDatabase

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeSearchAPIServer:
    """代码搜索API服务器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化API服务器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.search_engine = SemanticSearchEngine(config_path)
        self.db = CodeDatabase(self.config.get('database', {}).get('file', 'search.db'))
        
        # 创建Flask应用
        self.app = Flask(__name__)
        CORS(self.app)  # 启用CORS支持
        
        # 注册路由
        self._register_routes()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件 {config_path} 不存在，使用默认配置")
            return {
                'database': {'file': 'search.db'},
                'search': {'max_results': 10},
                'repository': {'path': '.'}
            }
    
    def _register_routes(self):
        """注册API路由"""
        
        @self.app.route('/api/search', methods=['POST'])
        def search_code():
            """
            搜索代码接口
            
            POST /api/search
            {
                "query": "函数名或关键词",
                "limit": 10,
                "file_type": "python"
            }
            """
            try:
                data = request.get_json()
                if not data or 'query' not in data:
                    return jsonify({
                        'success': False,
                        'error': '缺少查询参数'
                    }), 400
                
                query = data['query']
                limit = data.get('limit', 10)
                file_type = data.get('file_type', '')
                
                # 执行搜索
                results = self.search_engine.search(query, limit)
                
                # 根据文件类型过滤结果
                if file_type:
                    results = [r for r in results if r.get('language', '').lower() == file_type.lower()]
                
                return jsonify({
                    'success': True,
                    'query': query,
                    'total_results': len(results),
                    'results': results
                })
                
            except Exception as e:
                logger.error(f"搜索错误: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/file', methods=['POST'])
        def get_file_content():
            """
            获取文件内容接口
            
            POST /api/file
            {
                "file_path": "path/to/file.py",
                "start_line": 1,
                "end_line": 50
            }
            """
            try:
                data = request.get_json()
                if not data or 'file_path' not in data:
                    return jsonify({
                        'success': False,
                        'error': '缺少文件路径参数'
                    }), 400
                
                file_path = data['file_path']
                start_line = data.get('start_line')
                end_line = data.get('end_line')
                
                # 读取文件内容
                full_path = Path(file_path)
                if not full_path.exists():
                    # 尝试相对路径
                    full_path = Path(self.config.get('repository', {}).get('path', '.')) / file_path
                
                if not full_path.exists():
                    return jsonify({
                        'success': False,
                        'error': f'文件不存在: {file_path}'
                    }), 404
                
                with open(full_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 如果指定了行号范围
                if start_line is not None or end_line is not None:
                    start_idx = (start_line - 1) if start_line else 0
                    end_idx = end_line if end_line else len(lines)
                    content_lines = lines[start_idx:end_idx]
                    content = ''.join(content_lines)
                    line_range = f"{start_line or 1}-{end_line or len(lines)}"
                else:
                    content = ''.join(lines)
                    line_range = f"1-{len(lines)}"
                
                return jsonify({
                    'success': True,
                    'file_path': file_path,
                    'line_range': line_range,
                    'total_lines': len(lines),
                    'content': content
                })
                
            except Exception as e:
                logger.error(f"读取文件错误: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/function', methods=['POST'])
        def get_function_details():
            """
            获取函数详情接口
            
            POST /api/function
            {
                "function_name": "function_name",
                "file_path": "optional/path/to/file.py"
            }
            """
            try:
                data = request.get_json()
                if not data or 'function_name' not in data:
                    return jsonify({
                        'success': False,
                        'error': '缺少函数名参数'
                    }), 400
                
                function_name = data['function_name']
                file_path = data.get('file_path')
                
                # 搜索函数
                results = self.search_engine.search(function_name, 10)
                
                # 过滤函数类型的结果
                function_results = [r for r in results if r['type'] == 'function' and r['name'] == function_name]
                
                # 如果指定了文件路径，进一步过滤
                if file_path:
                    function_results = [r for r in function_results if file_path in r['file_path']]
                
                return jsonify({
                    'success': True,
                    'function_name': function_name,
                    'total_matches': len(function_results),
                    'functions': function_results
                })
                
            except Exception as e:
                logger.error(f"获取函数详情错误: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/stats', methods=['GET'])
        def get_database_stats():
            """
            获取数据库统计信息接口
            
            GET /api/stats
            """
            try:
                stats = self.db.get_stats()
                
                return jsonify({
                    'success': True,
                    'stats': stats
                })
                
            except Exception as e:
                logger.error(f"获取统计信息错误: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """健康检查接口"""
            return jsonify({
                'success': True,
                'status': 'healthy',
                'message': '代码搜索API服务器运行正常'
            })
        
        @self.app.route('/api/info', methods=['GET'])
        def get_api_info():
            """获取API信息"""
            return jsonify({
                'success': True,
                'api_name': '代码搜索API',
                'version': '1.0.0',
                'endpoints': {
                    'POST /api/search': '搜索代码',
                    'POST /api/file': '获取文件内容',
                    'POST /api/function': '获取函数详情',
                    'GET /api/stats': '获取统计信息',
                    'GET /api/health': '健康检查',
                    'GET /api/info': '获取API信息'
                }
            })
    
    def run(self, host: str = '127.0.0.1', port: int = 5002, debug: bool = False):
        """
        运行API服务器
        
        Args:
            host: 服务器主机地址
            port: 服务器端口
            debug: 是否启用调试模式
        """
        logger.info(f"启动代码搜索API服务器 http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='代码搜索API服务器')
    parser.add_argument('--host', default='127.0.0.1', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=5002, help='服务器端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--config', default='config.yaml', help='配置文件路径')
    
    args = parser.parse_args()
    
    server = CodeSearchAPIServer(args.config)
    server.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()