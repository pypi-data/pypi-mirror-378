#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码搜索API客户端示例
演示如何使用代码搜索API进行各种操作
"""

import json
import requests
import time
import os
from typing import Dict, List, Any, Optional

# 禁用代理
os.environ['NO_PROXY'] = '*'

class CodeSearchAPIClient:
    """代码搜索API客户端"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:5002"):
        """
        初始化API客户端
        
        Args:
            base_url: API服务器基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康检查结果
        """
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        获取API信息
        
        Returns:
            API信息
        """
        try:
            response = self.session.get(f"{self.base_url}/api/info")
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def search_code(self, query: str, limit: int = 10, file_type: str = "") -> Dict[str, Any]:
        """
        搜索代码
        
        Args:
            query: 搜索查询
            limit: 结果数量限制
            file_type: 文件类型过滤
            
        Returns:
            搜索结果
        """
        try:
            data = {
                'query': query,
                'limit': limit
            }
            if file_type:
                data['file_type'] = file_type
            
            response = self.session.post(f"{self.base_url}/api/search", json=data)
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_file_content(self, file_path: str, start_line: Optional[int] = None, 
                        end_line: Optional[int] = None) -> Dict[str, Any]:
        """
        获取文件内容
        
        Args:
            file_path: 文件路径
            start_line: 起始行号
            end_line: 结束行号
            
        Returns:
            文件内容
        """
        try:
            data = {'file_path': file_path}
            if start_line is not None:
                data['start_line'] = start_line
            if end_line is not None:
                data['end_line'] = end_line
            
            response = self.session.post(f"{self.base_url}/api/file", json=data)
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_function_details(self, function_name: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        获取函数详情
        
        Args:
            function_name: 函数名
            file_path: 文件路径（可选）
            
        Returns:
            函数详情
        """
        try:
            data = {'function_name': function_name}
            if file_path:
                data['file_path'] = file_path
            
            response = self.session.post(f"{self.base_url}/api/function", json=data)
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        获取数据库统计信息
        
        Returns:
            统计信息
        """
        try:
            response = self.session.get(f"{self.base_url}/api/stats")
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}

def print_json(data: Dict[str, Any], title: str = ""):
    """
    格式化打印JSON数据
    
    Args:
        data: 要打印的数据
        title: 标题
    """
    if title:
        print(f"\n=== {title} ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))

def run_examples():
    """运行示例测试"""
    client = CodeSearchAPIClient()
    
    print("🚀 代码搜索API客户端示例")
    print("=" * 50)
    
    # 1. 健康检查
    print("\n1. 健康检查")
    health = client.health_check()
    print_json(health)
    
    if not health.get('success'):
        print("❌ API服务器未运行，请先启动服务器")
        return
    
    # 2. 获取API信息
    print("\n2. 获取API信息")
    info = client.get_api_info()
    print_json(info)
    
    # 3. 搜索代码
    print("\n3. 搜索代码示例")
    search_queries = [
        "支付状态",
        "update_payment_status",
        "process_order",
        "calculate_total"
    ]
    
    for query in search_queries:
        print(f"\n搜索: '{query}'")
        result = client.search_code(query, limit=3)
        if result.get('success') and result.get('results'):
            print(f"找到 {result['total_results']} 个结果:")
            for i, item in enumerate(result['results'], 1):
                print(f"  {i}. {item['name']} ({item['type']}) - {item['file_path']}")
        else:
            print("  未找到结果")
    
    # 4. 获取文件内容示例
    print("\n4. 获取文件内容示例")
    # 先搜索一个文件
    search_result = client.search_code("payment", limit=1)
    if search_result.get('success') and search_result.get('results'):
        file_path = search_result['results'][0]['file_path']
        print(f"获取文件内容: {file_path}")
        
        file_content = client.get_file_content(file_path, start_line=1, end_line=20)
        if file_content.get('success'):
            print(f"文件: {file_content['file_path']}")
            print(f"行数: {file_content['line_range']}")
            print("内容预览:")
            print(file_content['content'][:200] + "..." if len(file_content['content']) > 200 else file_content['content'])
    
    # 5. 获取函数详情示例
    print("\n5. 获取函数详情示例")
    function_names = ["update_payment_status", "process_order"]
    
    for func_name in function_names:
        print(f"\n获取函数详情: {func_name}")
        func_details = client.get_function_details(func_name)
        if func_details.get('success') and func_details.get('functions'):
            print(f"找到 {func_details['total_matches']} 个匹配:")
            for func in func_details['functions']:
                print(f"  - {func['name']} in {func['file_path']} (行 {func['start_line']}-{func['end_line']})")
        else:
            print("  未找到函数")
    
    # 6. 获取统计信息
    print("\n6. 获取数据库统计信息")
    stats = client.get_database_stats()
    print_json(stats)
    
    print("\n✅ 示例测试完成!")

def interactive_mode():
    """交互模式"""
    client = CodeSearchAPIClient()
    
    print("🔍 代码搜索API交互模式")
    print("输入 'help' 查看可用命令，输入 'quit' 退出")
    print("=" * 50)
    
    while True:
        try:
            command = input("\n> ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                print("再见!")
                break
            elif command.lower() == 'help':
                print("""
可用命令:
  search <query>          - 搜索代码
  file <path>            - 获取文件内容
  function <name>        - 获取函数详情
  stats                  - 获取统计信息
  health                 - 健康检查
  info                   - API信息
  help                   - 显示帮助
  quit                   - 退出
                """)
            elif command.lower() == 'health':
                result = client.health_check()
                print_json(result)
            elif command.lower() == 'info':
                result = client.get_api_info()
                print_json(result)
            elif command.lower() == 'stats':
                result = client.get_database_stats()
                print_json(result)
            elif command.startswith('search '):
                query = command[7:].strip()
                if query:
                    result = client.search_code(query)
                    print_json(result)
                else:
                    print("请提供搜索查询")
            elif command.startswith('file '):
                file_path = command[5:].strip()
                if file_path:
                    result = client.get_file_content(file_path)
                    print_json(result)
                else:
                    print("请提供文件路径")
            elif command.startswith('function '):
                func_name = command[9:].strip()
                if func_name:
                    result = client.get_function_details(func_name)
                    print_json(result)
                else:
                    print("请提供函数名")
            else:
                print("未知命令，输入 'help' 查看可用命令")
                
        except KeyboardInterrupt:
            print("\n再见!")
            break
        except Exception as e:
            print(f"错误: {e}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='代码搜索API客户端示例')
    parser.add_argument('--url', default='http://127.0.0.1:5002', help='API服务器URL')
    parser.add_argument('--interactive', '-i', action='store_true', help='启动交互模式')
    
    args = parser.parse_args()
    
    # 更新客户端URL
    global client
    client = CodeSearchAPIClient(args.url)
    
    if args.interactive:
        interactive_mode()
    else:
        run_examples()

if __name__ == "__main__":
    main()