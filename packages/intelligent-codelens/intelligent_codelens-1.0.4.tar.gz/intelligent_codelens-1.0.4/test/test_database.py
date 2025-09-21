#!/usr/bin/env python3
"""
数据库功能详细测试脚本
测试数据库存储、查询、更新、删除等功能
"""

import os
import sys
import tempfile
import sqlite3
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src" / "core"))

from src.core.database import CodeDatabase

def test_database_creation():
    """测试数据库创建和表结构"""
    print("🏗️  测试数据库创建和表结构...")
    
    db_path = tempfile.mktemp(suffix=".db")
    
    try:
        db = CodeDatabase(db_path)
        
        # 检查数据库文件是否创建
        if os.path.exists(db_path):
            print("✅ 数据库文件创建成功")
        else:
            print("❌ 数据库文件创建失败")
            return
        
        # 检查表结构
        cursor = db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['files', 'functions', 'classes', 'imports', 'comments']
        
        for table in expected_tables:
            if table in tables:
                print(f"✅ 表 {table} 创建成功")
            else:
                print(f"❌ 表 {table} 创建失败")
        
        db.close()
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
    
    print()

def test_file_operations():
    """测试文件相关操作"""
    print("📁 测试文件相关操作...")
    
    db_path = tempfile.mktemp(suffix=".db")
    
    try:
        db = CodeDatabase(db_path)
        
        # 测试文件存储
        file_data = {
            'file_path': '/test/calculator.py',
            'language': 'python',
            'content': '''
def add(a, b):
    """加法函数"""
    return a + b

class Calculator:
    """计算器类"""
    def multiply(self, x, y):
        return x * y
''',
            'functions': [
                {
                    'name': 'add',
                    'start_line': 2,
                    'end_line': 4,
                    'parameters': ['a', 'b'],
                    'docstring': '加法函数',
                    'body': 'return a + b'
                },
                {
                    'name': 'multiply',
                    'start_line': 8,
                    'end_line': 9,
                    'parameters': ['self', 'x', 'y'],
                    'docstring': None,
                    'body': 'return x * y'
                }
            ],
            'classes': [
                {
                    'name': 'Calculator',
                    'start_line': 6,
                    'end_line': 9,
                    'body': 'def multiply(self, x, y):\n        return x * y'
                }
            ],
            'imports': [],
            'comments': []
        }
        
        file_id = db.store_file_data(file_data)
        if file_id:
            print(f"✅ 文件存储成功，ID: {file_id}")
        else:
            print("❌ 文件存储失败")
            return
        
        # 测试文件查询
        cursor = db.conn.cursor()
        cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
        file_record = cursor.fetchone()
        
        if file_record:
            print(f"✅ 文件查询成功: {file_record['file_path']}")
        else:
            print("❌ 文件查询失败")
        
        # 测试函数查询
        cursor.execute("SELECT * FROM functions WHERE file_id = ?", (file_id,))
        functions = cursor.fetchall()
        
        print(f"✅ 查询到 {len(functions)} 个函数:")
        for func in functions:
            print(f"   - {func['name']} (行 {func['start_line']}-{func['end_line']})")
        
        # 测试类查询
        cursor.execute("SELECT * FROM classes WHERE file_id = ?", (file_id,))
        classes = cursor.fetchall()
        
        print(f"✅ 查询到 {len(classes)} 个类:")
        for cls in classes:
            print(f"   - {cls['name']} (行 {cls['start_line']}-{cls['end_line']})")
        
        db.close()
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
    
    print()

def test_search_functions():
    """测试搜索功能"""
    print("🔍 测试搜索功能...")
    
    db_path = tempfile.mktemp(suffix=".db")
    
    try:
        db = CodeDatabase(db_path)
        
        # 存储多个文件用于搜索测试
        test_files = [
            {
                'file_path': '/test/math_utils.py',
                'language': 'python',
                'content': 'def calculate_sum(a, b): return a + b',
                'functions': [
                    {
                        'name': 'calculate_sum',
                        'start_line': 1,
                        'end_line': 1,
                        'parameters': ['a', 'b'],
                        'docstring': '计算两个数的和',
                        'body': 'return a + b'
                    }
                ],
                'classes': [],
                'imports': [],
                'comments': []
            },
            {
                'file_path': '/test/string_utils.py',
                'language': 'python',
                'content': 'def format_string(text): return text.strip().lower()',
                'functions': [
                    {
                        'name': 'format_string',
                        'start_line': 1,
                        'end_line': 1,
                        'parameters': ['text'],
                        'docstring': '格式化字符串',
                        'body': 'return text.strip().lower()'
                    }
                ],
                'classes': [],
                'imports': [],
                'comments': []
            },
            {
                'file_path': '/test/calculator.py',
                'language': 'python',
                'content': 'class Calculator: pass',
                'functions': [],
                'classes': [
                    {
                        'name': 'Calculator',
                        'start_line': 1,
                        'end_line': 1,
                        'body': 'pass'
                    }
                ],
                'imports': [],
                'comments': []
            }
        ]
        
        # 存储测试数据
        for file_data in test_files:
            db.store_file_data(file_data)
        
        # 测试函数搜索
        search_tests = [
            ('calculate', '函数名包含calculate'),
            ('sum', '函数名包含sum'),
            ('format', '函数名包含format'),
            ('nonexistent', '不存在的函数名')
        ]
        
        for search_term, description in search_tests:
            results = db.search_functions(search_term)
            print(f"✅ 搜索 '{search_term}' ({description}): 找到 {len(results)} 个结果")
            for result in results:
                print(f"   - {result['name']} in {result['file_path']}")
        
        # 测试类搜索
        class_results = db.search_classes('Calculator')
        print(f"✅ 搜索类 'Calculator': 找到 {len(class_results)} 个结果")
        for result in class_results:
            print(f"   - {result['name']} in {result['file_path']}")
        
        db.close()
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
    
    print()

def test_statistics():
    """测试统计功能"""
    print("📊 测试统计功能...")
    
    db_path = tempfile.mktemp(suffix=".db")
    
    try:
        db = CodeDatabase(db_path)
        
        # 存储一些测试数据
        for i in range(3):
            file_data = {
                'file_path': f'/test/file_{i}.py',
                'language': 'python',
                'content': f'def func_{i}(): pass\nclass Class_{i}: pass',
                'functions': [
                    {
                        'name': f'func_{i}',
                        'start_line': 1,
                        'end_line': 1,
                        'parameters': [],
                        'docstring': None,
                        'body': 'pass'
                    }
                ],
                'classes': [
                    {
                        'name': f'Class_{i}',
                        'start_line': 2,
                        'end_line': 2,
                        'body': 'pass'
                    }
                ],
                'imports': [],
                'comments': []
            }
            db.store_file_data(file_data)
        
        # 获取统计信息
        stats = db.get_stats()
        
        print("✅ 统计信息:")
        print(f"   - 文件数: {stats['files']}")
        print(f"   - 函数数: {stats['functions']}")
        print(f"   - 类数: {stats['classes']}")
        print(f"   - 数据库大小: {stats['db_size_mb']:.2f} MB")
        
        # 验证统计数据
        expected_files = 3
        expected_functions = 3
        expected_classes = 3
        
        if stats['files'] == expected_files:
            print(f"✅ 文件数统计正确: {stats['files']}")
        else:
            print(f"❌ 文件数统计错误: 期望 {expected_files}, 实际 {stats['files']}")
        
        if stats['functions'] == expected_functions:
            print(f"✅ 函数数统计正确: {stats['functions']}")
        else:
            print(f"❌ 函数数统计错误: 期望 {expected_functions}, 实际 {stats['functions']}")
        
        if stats['classes'] == expected_classes:
            print(f"✅ 类数统计正确: {stats['classes']}")
        else:
            print(f"❌ 类数统计错误: 期望 {expected_classes}, 实际 {stats['classes']}")
        
        db.close()
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
    
    print()

def test_database_integrity():
    """测试数据库完整性"""
    print("🔒 测试数据库完整性...")
    
    db_path = tempfile.mktemp(suffix=".db")
    
    try:
        db = CodeDatabase(db_path)
        
        # 测试重复文件路径处理
        file_data = {
            'file_path': '/test/duplicate.py',
            'language': 'python',
            'content': 'def test(): pass',
            'functions': [
                {
                    'name': 'test',
                    'start_line': 1,
                    'end_line': 1,
                    'parameters': [],
                    'docstring': None,
                    'body': 'pass'
                }
            ],
            'classes': [],
            'imports': [],
            'comments': []
        }
        
        # 第一次存储
        file_id1 = db.store_file_data(file_data)
        
        # 修改内容后再次存储相同路径
        file_data['content'] = 'def test_updated(): pass'
        file_data['functions'][0]['name'] = 'test_updated'
        file_id2 = db.store_file_data(file_data)
        
        if file_id1 == file_id2:
            print("✅ 重复文件路径处理正确 (更新现有记录)")
        else:
            print("❌ 重复文件路径处理错误")
        
        # 检查是否只有一个文件记录
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM files WHERE file_path = ?", ('/test/duplicate.py',))
        count = cursor.fetchone()[0]
        
        if count == 1:
            print("✅ 文件记录唯一性保持正确")
        else:
            print(f"❌ 文件记录唯一性错误: 找到 {count} 个记录")
        
        # 检查函数是否正确更新
        cursor.execute("SELECT name FROM functions WHERE file_id = ?", (file_id2,))
        func_names = [row[0] for row in cursor.fetchall()]
        
        if 'test_updated' in func_names and 'test' not in func_names:
            print("✅ 函数记录更新正确")
        else:
            print(f"❌ 函数记录更新错误: {func_names}")
        
        db.close()
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
    
    print()

def main():
    """主测试函数"""
    print("🚀 开始数据库功能详细测试")
    print("=" * 50)
    
    test_database_creation()
    test_file_operations()
    test_search_functions()
    test_statistics()
    test_database_integrity()
    
    print("✅ 数据库功能测试完成!")

if __name__ == "__main__":
    main()