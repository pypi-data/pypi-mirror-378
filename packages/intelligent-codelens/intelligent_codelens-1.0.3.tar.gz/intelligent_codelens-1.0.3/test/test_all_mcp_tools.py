#!/usr/bin/env python3
"""
FastMCP服务器所有工具方法的综合测试脚本

该脚本测试以下MCP工具方法：
1. search_code - 搜索代码库中的相关代码片段
2. get_file_content - 获取指定文件的内容
3. get_function_details - 获取函数的详细信息
4. get_database_stats - 获取数据库统计信息

作者: AI Assistant
日期: 2025-01-21
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# 添加父目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src" / "mcp"))

from src.mcp.fastmcp_server import search_code, get_file_content, get_function_details, get_database_stats


async def test_search_code():
    """测试search_code工具方法"""
    print('=' * 50)
    print('测试 search_code 工具方法')
    print('=' * 50)
    
    test_cases = [
        {'query': 'UserAuth', 'limit': 5, 'description': '搜索UserAuth类'},
        {'query': 'login', 'limit': 3, 'description': '搜索login相关函数'},
        {'query': 'class', 'limit': 3, 'file_type': '.py', 'description': '搜索.py文件中的class'},
        {'query': 'nonexistent_function_xyz', 'limit': 5, 'description': '搜索不存在的内容'}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f'\n{i}. {test_case["description"]}:')
        try:
            result = await search_code(
                test_case['query'], 
                limit=test_case['limit'],
                file_type=test_case.get('file_type', '')
            )
            data = json.loads(result)
            print(f'   成功: {data["success"]}')
            print(f'   结果数量: {data["total_results"]}')
            
            if data['results']:
                for j, r in enumerate(data['results'][:2]):
                    print(f'   结果{j+1}: {r.get("name", "N/A")} - {r.get("file_path", "N/A")}')
        except Exception as e:
            print(f'   错误: {e}')


async def test_get_file_content():
    """测试get_file_content工具方法"""
    print('\n' + '=' * 50)
    print('测试 get_file_content 工具方法')
    print('=' * 50)
    
    test_cases = [
        {'file_path': 'mcp_config.yaml', 'description': '读取整个配置文件'},
        {'file_path': 'fastmcp_server.py', 'start_line': 1, 'end_line': 10, 'description': '读取指定行范围'},
        {'file_path': 'fastmcp_server.py', 'start_line': 20, 'description': '从指定行开始读取'},
        {'file_path': 'fastmcp_server.py', 'end_line': 15, 'description': '读取到指定行'},
        {'file_path': 'nonexistent_file.txt', 'description': '读取不存在的文件'}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f'\n{i}. {test_case["description"]}:')
        try:
            result = await get_file_content(
                test_case['file_path'],
                start_line=test_case.get('start_line'),
                end_line=test_case.get('end_line')
            )
            data = json.loads(result)
            print(f'   成功: {data["success"]}')
            
            if data['success']:
                content_lines = data['content'].split('\n')
                print(f'   文件行数: {len(content_lines)}')
                if test_case.get('start_line'):
                    print(f'   起始行: {data.get("start_line", "N/A")}')
                if test_case.get('end_line'):
                    print(f'   结束行: {data.get("end_line", "N/A")}')
            else:
                print(f'   错误信息: {data.get("error", "未知错误")}')
        except Exception as e:
            print(f'   错误: {e}')


async def test_get_function_details():
    """测试get_function_details工具方法"""
    print('\n' + '=' * 50)
    print('测试 get_function_details 工具方法')
    print('=' * 50)
    
    test_cases = [
        {'function_name': 'login_user', 'description': '搜索已知函数'},
        {'function_name': '__init__', 'description': '搜索构造函数'},
        {'function_name': 'search', 'file_path': 'semantic_search.py', 'description': '搜索特定文件中的函数'},
        {'function_name': 'nonexistent_function_xyz', 'description': '搜索不存在的函数'},
        {'function_name': 'main', 'description': '搜索常见函数名'}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f'\n{i}. {test_case["description"]}:')
        try:
            result = await get_function_details(
                test_case['function_name'],
                file_path=test_case.get('file_path')
            )
            data = json.loads(result)
            print(f'   成功: {data["success"]}')
            
            if data['success']:
                print(f'   匹配数量: {len(data["matches"])}')
                for j, match in enumerate(data['matches'][:3]):
                    print(f'   匹配{j+1}: {match.get("name", "N/A")} - {match.get("file_path", "N/A")}')
            else:
                print(f'   错误信息: {data.get("error", "未知错误")}')
        except Exception as e:
            print(f'   错误: {e}')


async def test_get_database_stats():
    """测试get_database_stats工具方法"""
    print('\n' + '=' * 50)
    print('测试 get_database_stats 工具方法')
    print('=' * 50)
    
    print('\n获取数据库统计信息:')
    try:
        result = await get_database_stats()
        data = json.loads(result)
        
        if 'error' in data:
            print(f'   错误: {data["error"]}')
            print(f'   文件数: {data.get("files", 0)}')
            print(f'   函数数: {data.get("functions", 0)}')
            print(f'   类数: {data.get("classes", 0)}')
            print(f'   数据库大小: {data.get("database_size_mb", 0)} MB')
        else:
            print('   统计信息获取成功:')
            for key, value in data.items():
                if key == 'database_size_mb' or key == 'db_size_mb':
                    print(f'   {key}: {value} MB')
                else:
                    print(f'   {key}: {value}')
    except Exception as e:
        print(f'   错误: {e}')


async def run_all_tests():
    """运行所有测试"""
    print('FastMCP服务器工具方法综合测试')
    print('=' * 60)
    
    # 检查必要文件是否存在
    required_files = ['mcp_config.yaml', 'search.db', 'fastmcp_server.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f'警告: 以下必要文件不存在: {missing_files}')
        print('某些测试可能会失败')
    
    print(f'当前工作目录: {os.getcwd()}')
    print(f'测试开始时间: {asyncio.get_event_loop().time()}')
    
    # 运行所有测试
    await test_search_code()
    await test_get_file_content()
    await test_get_function_details()
    await test_get_database_stats()
    
    print('\n' + '=' * 60)
    print('所有测试完成')
    print('=' * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())