#!/usr/bin/env python3
"""
语义搜索引擎测试脚本
测试语义搜索、向量化、相似度计算等功能
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from semantic_search import SemanticSearchEngine
from database import CodeDatabase

def create_test_repository():
    """创建测试代码仓库"""
    test_dir = tempfile.mkdtemp(prefix="semantic_test_")
    
    # 创建多个不同功能的代码文件
    test_files = {
        'math_operations.py': '''
def calculate_sum(numbers):
    """计算数字列表的总和"""
    return sum(numbers)

def calculate_average(numbers):
    """计算数字列表的平均值"""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def find_maximum(numbers):
    """找到数字列表中的最大值"""
    return max(numbers) if numbers else None

def find_minimum(numbers):
    """找到数字列表中的最小值"""
    return min(numbers) if numbers else None
''',
        
        'string_utils.py': '''
def reverse_string(text):
    """反转字符串"""
    return text[::-1]

def capitalize_words(text):
    """将字符串中每个单词的首字母大写"""
    return ' '.join(word.capitalize() for word in text.split())

def count_characters(text):
    """统计字符串中的字符数量"""
    return len(text)

def remove_whitespace(text):
    """移除字符串中的空白字符"""
    return ''.join(text.split())
''',
        
        'file_operations.py': '''
import os
import json

def read_text_file(file_path):
    """读取文本文件内容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_text_file(file_path, content):
    """写入文本到文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def load_json_data(file_path):
    """从JSON文件加载数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_data(file_path, data):
    """保存数据到JSON文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
''',
        
        'data_structures.py': '''
class Stack:
    """栈数据结构实现"""
    
    def __init__(self):
        self.items = []
    
    def push(self, item):
        """向栈中添加元素"""
        self.items.append(item)
    
    def pop(self):
        """从栈中移除并返回顶部元素"""
        return self.items.pop() if self.items else None
    
    def peek(self):
        """查看栈顶元素但不移除"""
        return self.items[-1] if self.items else None

class Queue:
    """队列数据结构实现"""
    
    def __init__(self):
        self.items = []
    
    def enqueue(self, item):
        """向队列末尾添加元素"""
        self.items.append(item)
    
    def dequeue(self):
        """从队列前端移除并返回元素"""
        return self.items.pop(0) if self.items else None
'''
    }
    
    # 写入测试文件
    for filename, content in test_files.items():
        with open(os.path.join(test_dir, filename), 'w', encoding='utf-8') as f:
            f.write(content)
    
    return test_dir

def test_search_engine_initialization():
    """测试搜索引擎初始化"""
    print("🚀 测试语义搜索引擎初始化...")
    
    try:
        # 使用默认配置初始化搜索引擎
        search_engine = SemanticSearchEngine()
        
        if hasattr(search_engine, 'db'):
            print("✅ 搜索引擎初始化成功")
            print(f"   - 数据库连接: {type(search_engine.db).__name__}")
        else:
            print("❌ 搜索引擎初始化失败")
        
        if hasattr(search_engine, 'nlp'):
            print(f"✅ NLP模型状态: {'已加载' if search_engine.nlp else '未加载'}")
        else:
            print("❌ NLP模型初始化失败")
        
        if hasattr(search_engine, 'search_weights'):
            print("✅ 搜索权重配置成功")
        else:
            print("❌ 搜索权重配置失败")
        
    except Exception as e:
        print(f"❌ 搜索引擎初始化异常: {e}")
    
    print()

def test_text_vectorization():
    """测试文本向量化"""
    print("🔢 测试文本向量化...")
    
    try:
        search_engine = SemanticSearchEngine()
        
        # 测试文本
        test_texts = [
            "计算数字的总和",
            "反转字符串",
            "读取文件内容",
            "栈数据结构",
            "def calculate_sum(numbers): return sum(numbers)"
        ]
        
        for text in test_texts:
            try:
                # 测试文本相似度计算（间接测试向量化）
                similarity = search_engine._text_similarity(text, text)
                if similarity > 0:
                    print(f"✅ 文本处理成功: '{text[:20]}...' -> 相似度: {similarity:.3f}")
                else:
                    print(f"❌ 文本处理失败: '{text[:20]}...'")
            except Exception as e:
                print(f"❌ 文本处理异常: '{text[:20]}...' - {e}")
        
    except Exception as e:
        print(f"❌ 向量化测试异常: {e}")
    
    print()

def test_semantic_search():
    """测试语义搜索功能"""
    print("🔍 测试语义搜索功能...")
    
    test_dir = create_test_repository()
    
    try:
        # 使用默认搜索引擎（会使用默认数据库）
        search_engine = SemanticSearchEngine()
        
        # 手动添加一些测试数据到默认数据库
        test_functions = [
            {
                'file_path': '/test/math_operations.py',
                'language': 'python',
                'content': 'def calculate_sum(numbers): return sum(numbers)',
                'functions': [
                    {
                        'name': 'calculate_sum',
                        'start_line': 1,
                        'end_line': 3,
                        'parameters': ['numbers'],
                        'docstring': '计算数字列表的总和',
                        'body': 'return sum(numbers)'
                    }
                ],
                'classes': [],
                'imports': [],
                'comments': []
            },
            {
                'file_path': '/test/string_utils.py',
                'language': 'python',
                'content': 'def reverse_string(text): return text[::-1]',
                'functions': [
                    {
                        'name': 'reverse_string',
                        'start_line': 1,
                        'end_line': 3,
                        'parameters': ['text'],
                        'docstring': '反转字符串',
                        'body': 'return text[::-1]'
                    }
                ],
                'classes': [],
                'imports': [],
                'comments': []
            }
        ]
        
        # 存储测试数据
        for file_data in test_functions:
            search_engine.db.store_file_data(file_data)
        
        # 测试不同类型的搜索查询
        search_queries = [
            ("计算总和", "数学计算相关"),
            ("字符串反转", "字符串操作相关"),
            ("sum numbers", "英文数学计算"),
            ("reverse text", "英文字符串操作"),
            ("不存在的功能", "不存在的功能测试")
        ]
        
        for query, description in search_queries:
            try:
                results = search_engine.search(query, limit=3)
                print(f"✅ 搜索 '{query}' ({description}): 找到 {len(results)} 个结果")
                
                for i, result in enumerate(results, 1):
                    score = result.get('relevance_score', 0)
                    func_name = result.get('name', 'Unknown')
                    file_path = result.get('file_path', 'Unknown')
                    print(f"   {i}. {func_name} (相关度: {score:.3f}) - {file_path}")
                
            except Exception as e:
                print(f"❌ 搜索 '{query}' 异常: {e}")
        
    except Exception as e:
        print(f"❌ 语义搜索测试异常: {e}")
    
    finally:
        # 清理
        shutil.rmtree(test_dir)
    
    print()

def test_similarity_calculation():
    """测试相似度计算"""
    print("📐 测试相似度计算...")
    
    try:
        search_engine = SemanticSearchEngine()
        
        # 测试相似度计算
        similarity_tests = [
            ("计算总和", "sum calculation", "中英文相似概念"),
            ("反转字符串", "reverse string", "中英文相似概念"),
            ("读取文件", "read file", "中英文相似概念"),
            ("计算总和", "字符串反转", "不同功能概念"),
            ("hello world", "你好世界", "中英文问候语")
        ]
        
        for text1, text2, description in similarity_tests:
            try:
                similarity = search_engine._text_similarity(text1, text2)
                print(f"✅ 相似度计算 ({description}): {similarity:.3f}")
                print(f"   '{text1}' vs '{text2}'")
                    
            except Exception as e:
                print(f"❌ 相似度计算异常: '{text1}' vs '{text2}' - {e}")
        
    except Exception as e:
        print(f"❌ 相似度计算测试异常: {e}")
    
    print()

def test_search_performance():
    """测试搜索性能"""
    print("⚡ 测试搜索性能...")
    
    try:
        search_engine = SemanticSearchEngine()
        
        # 创建大量测试数据
        print("   创建测试数据...")
        for i in range(20):  # 创建20个函数（减少数量以提高测试速度）
            file_data = {
                'file_path': f'/test/module_{i}.py',
                'language': 'python',
                'content': f'def function_{i}(): pass',
                'functions': [
                    {
                        'name': f'function_{i}',
                        'start_line': 1,
                        'end_line': 1,
                        'parameters': [],
                        'docstring': f'这是第{i}个测试函数',
                        'body': 'pass'
                    }
                ],
                'classes': [],
                'imports': [],
                'comments': []
            }
            search_engine.db.store_file_data(file_data)
        
        # 测试搜索性能
        import time
        
        queries = ["测试函数", "function", "第10个", "pass"]
        
        for query in queries:
            start_time = time.time()
            results = search_engine.search(query, limit=10)
            end_time = time.time()
            
            search_time = (end_time - start_time) * 1000  # 转换为毫秒
            print(f"✅ 搜索 '{query}': {len(results)} 个结果, 耗时 {search_time:.2f}ms")
        
    except Exception as e:
        print(f"❌ 性能测试异常: {e}")
    
    print()

def main():
    """主测试函数"""
    print("🚀 开始语义搜索引擎测试")
    print("=" * 50)
    
    test_search_engine_initialization()
    test_text_vectorization()
    test_semantic_search()
    test_similarity_calculation()
    test_search_performance()
    
    print("✅ 语义搜索引擎测试完成!")

if __name__ == "__main__":
    main()