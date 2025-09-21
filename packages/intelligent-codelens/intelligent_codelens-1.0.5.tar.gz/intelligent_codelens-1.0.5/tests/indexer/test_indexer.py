"""
索引器模块单元测试
测试代码索引和解析功能
"""

import unittest
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.indexer import CodeIndexer
from src.core.database import CodeDatabase


class TestCodeIndexer(unittest.TestCase):
    """测试CodeIndexer类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = CodeDatabase(self.db_path)
        self.indexer = CodeIndexer(self.db)
        
        # 创建测试代码目录
        self.test_code_dir = os.path.join(self.temp_dir, 'test_code')
        os.makedirs(self.test_code_dir)
    
    def tearDown(self):
        """测试后清理"""
        if hasattr(self, 'db') and self.db:
            self.db.close()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_test_file(self, filename, content):
        """创建测试文件"""
        file_path = os.path.join(self.test_code_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def test_init_indexer(self):
        """测试索引器初始化"""
        self.assertIsNotNone(self.indexer)
        self.assertEqual(self.indexer.db, self.db)
        self.assertIsInstance(self.indexer.supported_extensions, set)
        self.assertIn('.py', self.indexer.supported_extensions)
    
    def test_is_supported_file(self):
        """测试文件类型支持检查"""
        # 支持的文件类型
        self.assertTrue(self.indexer.is_supported_file('test.py'))
        self.assertTrue(self.indexer.is_supported_file('test.js'))
        self.assertTrue(self.indexer.is_supported_file('test.java'))
        self.assertTrue(self.indexer.is_supported_file('test.cpp'))
        
        # 不支持的文件类型
        self.assertFalse(self.indexer.is_supported_file('test.txt'))
        self.assertFalse(self.indexer.is_supported_file('test.pdf'))
        self.assertFalse(self.indexer.is_supported_file('test.exe'))
        
        # 无扩展名文件
        self.assertFalse(self.indexer.is_supported_file('README'))
    
    def test_should_skip_directory(self):
        """测试目录跳过检查"""
        # 应该跳过的目录
        self.assertTrue(self.indexer.should_skip_directory('.git'))
        self.assertTrue(self.indexer.should_skip_directory('__pycache__'))
        self.assertTrue(self.indexer.should_skip_directory('node_modules'))
        self.assertTrue(self.indexer.should_skip_directory('.vscode'))
        
        # 不应该跳过的目录
        self.assertFalse(self.indexer.should_skip_directory('src'))
        self.assertFalse(self.indexer.should_skip_directory('tests'))
        self.assertFalse(self.indexer.should_skip_directory('utils'))
    
    def test_index_python_file(self):
        """测试Python文件索引"""
        python_code = '''
"""
这是一个测试模块
"""

import os
import sys
from typing import List, Dict

class TestClass:
    """测试类"""
    
    def __init__(self, name: str):
        """初始化方法"""
        self.name = name
    
    def get_name(self) -> str:
        """获取名称"""
        return self.name

def calculate_sum(numbers: List[int]) -> int:
    """计算数字列表的总和"""
    return sum(numbers)

def process_data(data: Dict) -> None:
    """处理数据"""
    # 这是行注释
    print(f"Processing {data}")
'''
        
        file_path = self.create_test_file('test_module.py', python_code)
        
        # 索引文件
        result = self.indexer.index_file(file_path)
        
        # 验证索引结果
        self.assertTrue(result)
        
        # 验证文件记录
        file_record = self.db.get_file_by_path(file_path)
        self.assertIsNotNone(file_record)
        
        # 验证函数记录
        functions = self.db.get_functions_by_file(file_record[0])
        function_names = [func[1] for func in functions]
        self.assertIn('__init__', function_names)
        self.assertIn('get_name', function_names)
        self.assertIn('calculate_sum', function_names)
        self.assertIn('process_data', function_names)
        
        # 验证类记录
        classes = self.db.get_classes_by_file(file_record[0])
        class_names = [cls[1] for cls in classes]
        self.assertIn('TestClass', class_names)
    
    def test_index_javascript_file(self):
        """测试JavaScript文件索引"""
        js_code = '''
/**
 * 这是一个测试模块
 */

const fs = require('fs');
const path = require('path');

class TestClass {
    /**
     * 构造函数
     */
    constructor(name) {
        this.name = name;
    }
    
    /**
     * 获取名称
     */
    getName() {
        return this.name;
    }
}

/**
 * 计算总和
 */
function calculateSum(numbers) {
    return numbers.reduce((a, b) => a + b, 0);
}

// 这是行注释
const processData = (data) => {
    console.log(`Processing ${data}`);
};
'''
        
        file_path = self.create_test_file('test_module.js', js_code)
        
        # 索引文件
        result = self.indexer.index_file(file_path)
        
        # 验证索引结果
        self.assertTrue(result)
        
        # 验证文件记录
        file_record = self.db.get_file_by_path(file_path)
        self.assertIsNotNone(file_record)
    
    def test_index_directory(self):
        """测试目录索引"""
        # 创建多个测试文件
        self.create_test_file('module1.py', '''
def function1():
    """函数1"""
    pass

class Class1:
    """类1"""
    pass
''')
        
        self.create_test_file('module2.py', '''
def function2():
    """函数2"""
    pass

class Class2:
    """类2"""
    pass
''')
        
        # 创建子目录
        sub_dir = os.path.join(self.test_code_dir, 'subdir')
        os.makedirs(sub_dir)
        
        with open(os.path.join(sub_dir, 'module3.py'), 'w') as f:
            f.write('''
def function3():
    """函数3"""
    pass
''')
        
        # 索引目录
        result = self.indexer.index_directory(self.test_code_dir)
        
        # 验证索引结果
        self.assertTrue(result)
        
        # 验证统计信息
        stats = self.db.get_statistics()
        self.assertEqual(stats['files'], 3)  # 3个Python文件
        self.assertGreaterEqual(stats['functions'], 3)  # 至少3个函数
        self.assertGreaterEqual(stats['classes'], 2)  # 至少2个类
    
    def test_index_directory_with_skip(self):
        """测试目录索引时跳过特定目录"""
        # 创建应该跳过的目录
        skip_dir = os.path.join(self.test_code_dir, '__pycache__')
        os.makedirs(skip_dir)
        
        with open(os.path.join(skip_dir, 'cached.py'), 'w') as f:
            f.write('# This should be skipped')
        
        # 创建正常文件
        self.create_test_file('normal.py', '''
def normal_function():
    pass
''')
        
        # 索引目录
        result = self.indexer.index_directory(self.test_code_dir)
        
        # 验证索引结果
        self.assertTrue(result)
        
        # 验证只索引了正常文件
        stats = self.db.get_statistics()
        self.assertEqual(stats['files'], 1)  # 只有1个文件被索引
    
    def test_update_file_index(self):
        """测试更新文件索引"""
        # 创建初始文件
        file_path = self.create_test_file('update_test.py', '''
def old_function():
    """旧函数"""
    pass
''')
        
        # 首次索引
        self.indexer.index_file(file_path)
        
        # 验证初始索引
        file_record = self.db.get_file_by_path(file_path)
        functions = self.db.get_functions_by_file(file_record[0])
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0][1], 'old_function')
        
        # 更新文件内容
        with open(file_path, 'w') as f:
            f.write('''
def new_function():
    """新函数"""
    pass

def another_function():
    """另一个函数"""
    pass
''')
        
        # 重新索引
        self.indexer.index_file(file_path)
        
        # 验证更新后的索引
        file_record = self.db.get_file_by_path(file_path)
        functions = self.db.get_functions_by_file(file_record[0])
        function_names = [func[1] for func in functions]
        
        # 应该包含新函数，不包含旧函数
        self.assertIn('new_function', function_names)
        self.assertIn('another_function', function_names)
        self.assertNotIn('old_function', function_names)
    
    def test_index_file_with_encoding_issues(self):
        """测试处理编码问题的文件"""
        # 创建包含特殊字符的文件
        file_path = os.path.join(self.test_code_dir, 'encoding_test.py')
        
        # 使用不同编码写入文件
        content = '''
# -*- coding: utf-8 -*-
"""
包含中文注释的模块
"""

def 中文函数名():
    """中文文档字符串"""
    print("中文字符串")

class 中文类名:
    """中文类文档"""
    pass
'''
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 索引文件
        result = self.indexer.index_file(file_path)
        
        # 验证索引结果
        self.assertTrue(result)
        
        # 验证中文内容被正确处理
        file_record = self.db.get_file_by_path(file_path)
        self.assertIsNotNone(file_record)
    
    def test_index_empty_file(self):
        """测试索引空文件"""
        file_path = self.create_test_file('empty.py', '')
        
        # 索引空文件
        result = self.indexer.index_file(file_path)
        
        # 验证索引结果
        self.assertTrue(result)
        
        # 验证文件记录存在
        file_record = self.db.get_file_by_path(file_path)
        self.assertIsNotNone(file_record)
        
        # 验证没有函数和类
        functions = self.db.get_functions_by_file(file_record[0])
        classes = self.db.get_classes_by_file(file_record[0])
        self.assertEqual(len(functions), 0)
        self.assertEqual(len(classes), 0)
    
    def test_index_nonexistent_file(self):
        """测试索引不存在的文件"""
        nonexistent_path = os.path.join(self.test_code_dir, 'nonexistent.py')
        
        # 索引不存在的文件
        result = self.indexer.index_file(nonexistent_path)
        
        # 验证索引失败
        self.assertFalse(result)
    
    def test_index_binary_file(self):
        """测试索引二进制文件"""
        # 创建二进制文件
        binary_path = os.path.join(self.test_code_dir, 'binary.pyc')
        with open(binary_path, 'wb') as f:
            f.write(b'\x00\x01\x02\x03')
        
        # 索引二进制文件
        result = self.indexer.index_file(binary_path)
        
        # 验证索引失败或跳过
        self.assertFalse(result)
    
    def test_get_file_statistics(self):
        """测试获取文件统计信息"""
        # 创建测试文件
        python_code = '''
import os
import sys

class TestClass:
    def method1(self):
        pass
    
    def method2(self):
        pass

def function1():
    pass

def function2():
    pass

# 注释1
# 注释2
'''
        
        file_path = self.create_test_file('stats_test.py', python_code)
        
        # 索引文件
        self.indexer.index_file(file_path)
        
        # 获取统计信息
        stats = self.indexer.get_file_statistics(file_path)
        
        # 验证统计信息
        self.assertIsInstance(stats, dict)
        self.assertIn('functions', stats)
        self.assertIn('classes', stats)
        self.assertIn('imports', stats)
        self.assertIn('lines', stats)
        
        self.assertGreaterEqual(stats['functions'], 4)  # 至少4个函数（包括方法）
        self.assertGreaterEqual(stats['classes'], 1)   # 至少1个类
        self.assertGreaterEqual(stats['imports'], 2)   # 至少2个导入
    
    def test_clear_file_index(self):
        """测试清除文件索引"""
        # 创建并索引文件
        file_path = self.create_test_file('clear_test.py', '''
def test_function():
    pass

class TestClass:
    pass
''')
        
        self.indexer.index_file(file_path)
        
        # 验证索引存在
        file_record = self.db.get_file_by_path(file_path)
        self.assertIsNotNone(file_record)
        
        functions = self.db.get_functions_by_file(file_record[0])
        classes = self.db.get_classes_by_file(file_record[0])
        self.assertGreater(len(functions), 0)
        self.assertGreater(len(classes), 0)
        
        # 清除文件索引
        result = self.indexer.clear_file_index(file_path)
        
        # 验证清除结果
        self.assertTrue(result)
        
        # 验证索引已清除
        file_record = self.db.get_file_by_path(file_path)
        self.assertIsNone(file_record)
    
    @patch('os.walk')
    def test_index_directory_with_walk_error(self, mock_walk):
        """测试目录遍历错误处理"""
        # 模拟os.walk抛出异常
        mock_walk.side_effect = OSError("Permission denied")
        
        # 索引目录
        result = self.indexer.index_directory(self.test_code_dir)
        
        # 验证错误处理
        self.assertFalse(result)
    
    def test_concurrent_indexing(self):
        """测试并发索引"""
        import threading
        
        # 创建多个测试文件
        files = []
        for i in range(5):
            file_path = self.create_test_file(f'concurrent_{i}.py', f'''
def function_{i}():
    """函数{i}"""
    pass

class Class_{i}:
    """类{i}"""
    pass
''')
            files.append(file_path)
        
        # 并发索引
        threads = []
        results = []
        
        def index_file_thread(file_path):
            result = self.indexer.index_file(file_path)
            results.append(result)
        
        for file_path in files:
            thread = threading.Thread(target=index_file_thread, args=(file_path,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有索引都成功
        self.assertEqual(len(results), 5)
        self.assertTrue(all(results))
        
        # 验证数据库中的记录
        stats = self.db.get_statistics()
        self.assertEqual(stats['files'], 5)


if __name__ == '__main__':
    unittest.main()