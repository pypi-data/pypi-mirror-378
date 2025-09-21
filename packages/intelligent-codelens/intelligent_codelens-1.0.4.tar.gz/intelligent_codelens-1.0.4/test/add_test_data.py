#!/usr/bin/env python3
"""添加测试数据到数据库"""

from database import CodeDatabase

def add_test_data():
    """添加测试数据到数据库"""
    db = CodeDatabase('search.db')
    
    # 测试数据1: 计算器类
    calculator_data = {
        'file_path': '/test/calculator.py',
        'language': 'python',
        'content': '''class Calculator:
    def add(self, a, b):
        """计算器加法运算"""
        return a + b
    
    def multiply(self, a, b):
        """计算器乘法运算"""
        return a * b
''',
        'functions': [
            {
                'name': 'add',
                'start_line': 2,
                'end_line': 4,
                'parameters': ['self', 'a', 'b'],
                'docstring': '计算器加法运算',
                'body': 'def add(self, a, b):\n    return a + b'
            },
            {
                'name': 'multiply',
                'start_line': 5,
                'end_line': 7,
                'parameters': ['self', 'a', 'b'],
                'docstring': '计算器乘法运算',
                'body': 'def multiply(self, a, b):\n    return a * b'
            }
        ],
        'classes': [
            {
                'name': 'Calculator',
                'start_line': 1,
                'end_line': 8,
                'body': 'class Calculator:\n    def add(self, a, b):\n        return a + b\n    def multiply(self, a, b):\n        return a * b'
            }
        ],
        'imports': [],
        'comments': []
    }
    
    # 测试数据2: 字符串工具类
    string_utils_data = {
        'file_path': '/test/string_utils.py',
        'language': 'python',
        'content': '''class StringUtils:
    @staticmethod
    def reverse_string(text):
        """反转字符串"""
        return text[::-1]
    
    @staticmethod
    def capitalize_words(text):
        """首字母大写"""
        return text.title()
''',
        'functions': [
            {
                'name': 'reverse_string',
                'start_line': 3,
                'end_line': 5,
                'parameters': ['text'],
                'docstring': '反转字符串',
                'body': '@staticmethod\ndef reverse_string(text):\n    return text[::-1]'
            },
            {
                'name': 'capitalize_words',
                'start_line': 7,
                'end_line': 9,
                'parameters': ['text'],
                'docstring': '首字母大写',
                'body': '@staticmethod\ndef capitalize_words(text):\n    return text.title()'
            }
        ],
        'classes': [
            {
                'name': 'StringUtils',
                'start_line': 1,
                'end_line': 9,
                'body': 'class StringUtils:\n    @staticmethod\n    def reverse_string(text):\n        return text[::-1]\n    @staticmethod\n    def capitalize_words(text):\n        return text.title()'
            }
        ],
        'imports': [],
        'comments': []
    }
    
    # 测试数据3: 数组工具类
    array_utils_data = {
        'file_path': '/test/array_utils.py',
        'language': 'python',
        'content': '''class ArrayUtils:
    @staticmethod
    def find_max(arr):
        """查找数组最大值"""
        return max(arr)
    
    @staticmethod
    def sort_array(arr):
        """数组排序"""
        return sorted(arr)
''',
        'functions': [
            {
                'name': 'find_max',
                'start_line': 3,
                'end_line': 5,
                'parameters': ['arr'],
                'docstring': '查找数组最大值',
                'body': '@staticmethod\ndef find_max(arr):\n    return max(arr)'
            },
            {
                'name': 'sort_array',
                'start_line': 7,
                'end_line': 9,
                'parameters': ['arr'],
                'docstring': '数组排序',
                'body': '@staticmethod\ndef sort_array(arr):\n    return sorted(arr)'
            }
        ],
        'classes': [
            {
                'name': 'ArrayUtils',
                'start_line': 1,
                'end_line': 9,
                'body': 'class ArrayUtils:\n    @staticmethod\n    def find_max(arr):\n        return max(arr)\n    @staticmethod\n    def sort_array(arr):\n        return sorted(arr)'
            }
        ],
        'imports': [],
        'comments': []
    }
    
    # 存储所有测试数据
    test_datasets = [calculator_data, string_utils_data, array_utils_data]
    
    for i, data in enumerate(test_datasets, 1):
        file_id = db.store_file_data(data)
        print(f'已添加测试数据 {i}，文件ID: {file_id}，文件: {data["file_path"]}')
    
    # 显示统计信息
    stats = db.get_stats()
    print(f'\n数据库统计:')
    print(f'文件数: {stats["files"]}')
    print(f'函数数: {stats["functions"]}')
    print(f'类数: {stats["classes"]}')
    print(f'数据库大小: {stats["db_size_mb"]} MB')

if __name__ == '__main__':
    add_test_data()