#!/usr/bin/env python3
"""
MCP代码搜索服务器 - 简化版本
提供代码搜索功能的MCP服务器实现，兼容Python 3.8+
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import yaml

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

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleMCPServer:
    """简化的MCP代码搜索服务器类"""
    
    def __init__(self, config_path: str = "mcp_config.yaml"):
        """
        初始化MCP服务器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.search_engine = SemanticSearchEngine(config_path)
        self.db_manager = CodeDatabase(self.config.get('database', {}).get('file', 'search.db'))
        
        # 服务器信息
        self.server_info = {
            'name': self.config.get('server', {}).get('name', 'code-search-server'),
            'version': self.config.get('server', {}).get('version', '1.0.0'),
            'description': self.config.get('server', {}).get('description', 'Code Search MCP Server')
        }
    
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
    
    async def search_code(self, query: str, limit: int = 10, file_type: str = "") -> Dict[str, Any]:
        """
        搜索代码
        
        Args:
            query: 搜索查询
            limit: 结果数量限制
            file_type: 文件类型过滤
            
        Returns:
            搜索结果字典
        """
        try:
            results = self.search_engine.search(query, limit=limit)
            
            # 如果指定了文件类型，进行过滤
            if file_type:
                results = [r for r in results if file_type.lower() in r.get('file_path', '').lower()]
            
            return {
                'success': True,
                'query': query,
                'results': results,
                'total_results': len(results)
            }
        except Exception as e:
            logger.error(f"搜索代码时出错: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'results': []
            }
    
    async def get_file_content(self, file_path: str, start_line: Optional[int] = None, 
                              end_line: Optional[int] = None) -> Dict[str, Any]:
        """
        获取文件内容
        
        Args:
            file_path: 文件路径
            start_line: 起始行号
            end_line: 结束行号
            
        Returns:
            文件内容字典
        """
        try:
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'文件不存在: {file_path}',
                    'content': ''
                }
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 处理行号范围
            if start_line is not None:
                start_idx = max(0, start_line - 1)
                if end_line is not None:
                    end_idx = min(len(lines), end_line)
                    lines = lines[start_idx:end_idx]
                else:
                    lines = lines[start_idx:]
            elif end_line is not None:
                end_idx = min(len(lines), end_line)
                lines = lines[:end_idx]
            
            content = ''.join(lines)
            
            return {
                'success': True,
                'file_path': file_path,
                'content': content,
                'total_lines': len(lines)
            }
        except Exception as e:
            logger.error(f"读取文件时出错: {e}")
            return {
                'success': False,
                'error': str(e),
                'content': ''
            }
    
    async def get_function_details(self, function_name: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        获取函数详细信息
        
        Args:
            function_name: 函数名称
            file_path: 文件路径（可选）
            
        Returns:
            函数详细信息字典
        """
        try:
            # 从数据库查询函数信息
            functions = self.db_manager.search_functions(function_name)
            
            if file_path:
                # 如果指定了文件路径，进行过滤
                functions = [f for f in functions if f.get('file_path') == file_path]
            
            if not functions:
                return {
                    'success': False,
                    'error': f'未找到函数: {function_name}',
                    'functions': []
                }
            
            return {
                'success': True,
                'function_name': function_name,
                'functions': functions,
                'total_found': len(functions)
            }
        except Exception as e:
            logger.error(f"获取函数详情时出错: {e}")
            return {
                'success': False,
                'error': str(e),
                'functions': []
            }
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """
        获取数据库统计信息
        
        Returns:
            统计信息字典
        """
        try:
            stats = self.db_manager.get_stats()
            return {
                'success': True,
                'stats': stats
            }
        except Exception as e:
            logger.error(f"获取统计信息时出错: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': {}
            }
    
    async def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理请求
        
        Args:
            method: 方法名
            params: 参数
            
        Returns:
            响应字典
        """
        try:
            if method == "initialize":
                # 处理MCP初始化请求
                return {
                    'protocolVersion': '2024-11-05',
                    'capabilities': {
                        'tools': {
                            'listChanged': True
                        }
                    },
                    'serverInfo': {
                        'name': self.server_info['name'],
                        'version': self.server_info['version'],
                        'description': self.server_info['description']
                    }
                }
            elif method == "tools/list":
                # 处理工具列表请求 - 确保返回正确的MCP格式
                tools = [
                    {
                        'name': 'search_code',
                        'description': '搜索代码库中的相关代码片段',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'query': {
                                    'type': 'string',
                                    'description': '搜索查询字符串'
                                },
                                'limit': {
                                    'type': 'integer',
                                    'description': '返回结果数量限制',
                                    'default': 10,
                                    'minimum': 1,
                                    'maximum': 100
                                },
                                'file_type': {
                                    'type': 'string',
                                    'description': '文件类型过滤（如：.py, .js等）',
                                    'default': ''
                                }
                            },
                            'required': ['query']
                        }
                    },
                    {
                        'name': 'get_file_content',
                        'description': '获取指定文件的内容',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'file_path': {
                                    'type': 'string',
                                    'description': '文件路径'
                                },
                                'start_line': {
                                    'type': 'integer',
                                    'description': '起始行号（可选）',
                                    'minimum': 1
                                },
                                'end_line': {
                                    'type': 'integer',
                                    'description': '结束行号（可选）',
                                    'minimum': 1
                                }
                            },
                            'required': ['file_path']
                        }
                    },
                    {
                        'name': 'get_function_details',
                        'description': '获取函数的详细信息',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'function_name': {
                                    'type': 'string',
                                    'description': '函数名称'
                                },
                                'file_path': {
                                    'type': 'string',
                                    'description': '文件路径（可选）'
                                }
                            },
                            'required': ['function_name']
                        }
                    },
                    {
                         'name': 'get_database_stats',
                         'description': '获取代码库索引的统计信息',
                         'inputSchema': {
                             'type': 'object',
                             'properties': {},
                             'additionalProperties': False
                         }
                     }
                ]
                
                return {
                    'tools': tools
                }
            elif method == "tools/call":
                # 处理工具调用请求
                tool_name = params.get('name')
                arguments = params.get('arguments', {})
                
                if tool_name == 'search_code':
                    result = await self.search_code(**arguments)
                    return {
                        'content': [
                            {
                                'type': 'text',
                                'text': json.dumps(result, ensure_ascii=False, indent=2)
                            }
                        ]
                    }
                elif tool_name == 'get_file_content':
                    result = await self.get_file_content(**arguments)
                    return {
                        'content': [
                            {
                                'type': 'text',
                                'text': json.dumps(result, ensure_ascii=False, indent=2)
                            }
                        ]
                    }
                elif tool_name == 'get_function_details':
                    result = await self.get_function_details(**arguments)
                    return {
                        'content': [
                            {
                                'type': 'text',
                                'text': json.dumps(result, ensure_ascii=False, indent=2)
                            }
                        ]
                    }
                elif tool_name == 'get_database_stats':
                    result = await self.get_database_stats()
                    return {
                        'content': [
                            {
                                'type': 'text',
                                'text': json.dumps(result, ensure_ascii=False, indent=2)
                            }
                        ]
                    }
                else:
                    return {
                        'success': False,
                        'error': f'未知工具: {tool_name}'
                    }
            elif method == "search_code":
                return await self.search_code(**params)
            elif method == "get_file_content":
                return await self.get_file_content(**params)
            elif method == "get_function_details":
                return await self.get_function_details(**params)
            elif method == "get_database_stats":
                return await self.get_database_stats()
            elif method == "server_info":
                return {
                    'success': True,
                    'server_info': self.server_info
                }
            else:
                return {
                    'success': False,
                    'error': f'未知方法: {method}'
                }
        except Exception as e:
            logger.error(f"处理请求时出错: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def run_stdio(self):
        """
        运行STDIO模式的MCP服务器
        """
        logger.info("启动简化MCP服务器 (STDIO模式)")
        
        try:
            while True:
                # 读取输入
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                try:
                    request = json.loads(line.strip())
                    method = request.get('method', '')
                    params = request.get('params', {})
                    request_id = request.get('id')
                    
                    # 处理请求
                    response = await self.handle_request(method, params)
                    
                    # 发送响应
                    result = {
                        'jsonrpc': '2.0',
                        'id': request_id,
                        'result': response
                    }
                    
                    print(json.dumps(result, ensure_ascii=False))
                    sys.stdout.flush()
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析错误: {e}")
                except Exception as e:
                    logger.error(f"处理请求时出错: {e}")
                    
        except KeyboardInterrupt:
            logger.info("服务器停止")
        except Exception as e:
            logger.error(f"服务器运行时出错: {e}")
    

    

    

    

    


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='MCP代码搜索服务器')
    parser.add_argument('--config', '-c', 
                       default='mcp_config.yaml',
                       help='配置文件路径 (默认: mcp_config.yaml)')
    
    args = parser.parse_args()
    
    try:
        # 创建服务器实例，使用指定的配置文件
        server = SimpleMCPServer(config_path=args.config)
        
        # 运行服务器
        asyncio.run(server.run_stdio())
        
    except Exception as e:
        logger.error(f"启动服务器时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()