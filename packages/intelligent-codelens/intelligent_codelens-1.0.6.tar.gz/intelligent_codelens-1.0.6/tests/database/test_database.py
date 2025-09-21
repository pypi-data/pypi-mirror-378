"""
数据库模块单元测试
测试CodeDatabase类的所有方法
"""

import unittest
import tempfile
import os
import sqlite3
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.database import CodeDatabase


class TestCodeDatabase(unittest.TestCase):
    """测试CodeDatabase类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = CodeDatabase(self.db_path)
    
    def tearDown(self):
        """测试后清理"""
        if hasattr(self, 'db') and self.db:
            self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_init_database(self):
        """测试数据库初始化"""
        # 验证数据库文件存在
        self.assertTrue(os.path.exists(self.db_path))
        
        # 验证表结构
        cursor = self.db.conn.cursor()
        
        # 检查files表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files'")
        self.assertIsNotNone(cursor.fetchone())
        
        # 检查functions表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='functions'")
        self.assertIsNotNone(cursor.fetchone())
        
        # 检查classes表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='classes'")
        self.assertIsNotNone(cursor.fetchone())
        
        # 检查imports表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='imports'")
        self.assertIsNotNone(cursor.fetchone())
        
        # 检查comments表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comments'")
        self.assertIsNotNone(cursor.fetchone())
    
    def test_add_file(self):
        """测试添加文件"""
        file_path = "/test/example.py"
        content = "print('hello')"
        
        file_id = self.db.add_file(file_path, content)
        
        # 验证返回的ID
        self.assertIsInstance(file_id, int)
        self.assertGreater(file_id, 0)
        
        # 验证数据库中的记录
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT file_path, content FROM files WHERE id = ?", (file_id,))
        result = cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], file_path)
        self.assertEqual(result[1], content)
    
    def test_add_function(self):
        """测试添加函数"""
        # 先添加文件
        file_id = self.db.add_file("/test/example.py", "def test(): pass")
        
        # 添加函数
        function_id = self.db.add_function(
            file_id=file_id,
            name="test_function",
            docstring="测试函数",
            start_line=1,
            end_line=5,
            parameters="param1, param2",
            return_type="str"
        )
        
        # 验证返回的ID
        self.assertIsInstance(function_id, int)
        self.assertGreater(function_id, 0)
        
        # 验证数据库中的记录
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT name, docstring, start_line, end_line, parameters, return_type 
            FROM functions WHERE id = ?
        """, (function_id,))
        result = cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "test_function")
        self.assertEqual(result[1], "测试函数")
        self.assertEqual(result[2], 1)
        self.assertEqual(result[3], 5)
        self.assertEqual(result[4], "param1, param2")
        self.assertEqual(result[5], "str")
    
    def test_add_class(self):
        """测试添加类"""
        # 先添加文件
        file_id = self.db.add_file("/test/example.py", "class TestClass: pass")
        
        # 添加类
        class_id = self.db.add_class(
            file_id=file_id,
            name="TestClass",
            docstring="测试类",
            start_line=1,
            end_line=10,
            base_classes="object"
        )
        
        # 验证返回的ID
        self.assertIsInstance(class_id, int)
        self.assertGreater(class_id, 0)
        
        # 验证数据库中的记录
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT name, docstring, start_line, end_line, base_classes 
            FROM classes WHERE id = ?
        """, (class_id,))
        result = cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "TestClass")
        self.assertEqual(result[1], "测试类")
        self.assertEqual(result[2], 1)
        self.assertEqual(result[3], 10)
        self.assertEqual(result[4], "object")
    
    def test_add_import(self):
        """测试添加导入"""
        # 先添加文件
        file_id = self.db.add_file("/test/example.py", "import os")
        
        # 添加导入
        import_id = self.db.add_import(
            file_id=file_id,
            module_name="os",
            import_type="import",
            alias=None,
            line_number=1
        )
        
        # 验证返回的ID
        self.assertIsInstance(import_id, int)
        self.assertGreater(import_id, 0)
        
        # 验证数据库中的记录
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT module_name, import_type, alias, line_number 
            FROM imports WHERE id = ?
        """, (import_id,))
        result = cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "os")
        self.assertEqual(result[1], "import")
        self.assertIsNone(result[2])
        self.assertEqual(result[3], 1)
    
    def test_add_comment(self):
        """测试添加注释"""
        # 先添加文件
        file_id = self.db.add_file("/test/example.py", "# 这是注释")
        
        # 添加注释
        comment_id = self.db.add_comment(
            file_id=file_id,
            content="这是注释",
            line_number=1,
            comment_type="line"
        )
        
        # 验证返回的ID
        self.assertIsInstance(comment_id, int)
        self.assertGreater(comment_id, 0)
        
        # 验证数据库中的记录
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT content, line_number, comment_type 
            FROM comments WHERE id = ?
        """, (comment_id,))
        result = cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "这是注释")
        self.assertEqual(result[1], 1)
        self.assertEqual(result[2], "line")
    
    def test_get_file_by_path(self):
        """测试根据路径获取文件"""
        file_path = "/test/example.py"
        content = "print('hello')"
        
        # 添加文件
        file_id = self.db.add_file(file_path, content)
        
        # 获取文件
        result = self.db.get_file_by_path(file_path)
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], file_id)
        self.assertEqual(result[1], file_path)
        self.assertEqual(result[2], content)
    
    def test_get_functions_by_file(self):
        """测试获取文件中的函数"""
        # 添加文件
        file_id = self.db.add_file("/test/example.py", "def test(): pass")
        
        # 添加函数
        self.db.add_function(file_id, "test_func1", "函数1", 1, 5)
        self.db.add_function(file_id, "test_func2", "函数2", 6, 10)
        
        # 获取函数
        functions = self.db.get_functions_by_file(file_id)
        
        self.assertEqual(len(functions), 2)
        self.assertEqual(functions[0][1], "test_func1")
        self.assertEqual(functions[1][1], "test_func2")
    
    def test_get_classes_by_file(self):
        """测试获取文件中的类"""
        # 添加文件
        file_id = self.db.add_file("/test/example.py", "class Test: pass")
        
        # 添加类
        self.db.add_class(file_id, "TestClass1", "类1", 1, 10)
        self.db.add_class(file_id, "TestClass2", "类2", 11, 20)
        
        # 获取类
        classes = self.db.get_classes_by_file(file_id)
        
        self.assertEqual(len(classes), 2)
        self.assertEqual(classes[0][1], "TestClass1")
        self.assertEqual(classes[1][1], "TestClass2")
    
    def test_search_functions(self):
        """测试搜索函数"""
        # 添加文件和函数
        file_id = self.db.add_file("/test/example.py", "def test(): pass")
        self.db.add_function(file_id, "calculate_sum", "计算总和", 1, 5)
        self.db.add_function(file_id, "calculate_average", "计算平均值", 6, 10)
        self.db.add_function(file_id, "process_data", "处理数据", 11, 15)
        
        # 搜索包含"calculate"的函数
        results = self.db.search_functions("calculate")
        
        self.assertEqual(len(results), 2)
        function_names = [result[1] for result in results]
        self.assertIn("calculate_sum", function_names)
        self.assertIn("calculate_average", function_names)
    
    def test_search_classes(self):
        """测试搜索类"""
        # 添加文件和类
        file_id = self.db.add_file("/test/example.py", "class Test: pass")
        self.db.add_class(file_id, "DataProcessor", "数据处理器", 1, 10)
        self.db.add_class(file_id, "DataValidator", "数据验证器", 11, 20)
        self.db.add_class(file_id, "FileManager", "文件管理器", 21, 30)
        
        # 搜索包含"Data"的类
        results = self.db.search_classes("Data")
        
        self.assertEqual(len(results), 2)
        class_names = [result[1] for result in results]
        self.assertIn("DataProcessor", class_names)
        self.assertIn("DataValidator", class_names)
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        # 添加测试数据
        file_id = self.db.add_file("/test/example.py", "test content")
        self.db.add_function(file_id, "func1", "函数1", 1, 5)
        self.db.add_function(file_id, "func2", "函数2", 6, 10)
        self.db.add_class(file_id, "Class1", "类1", 11, 20)
        self.db.add_import(file_id, "os", "import", None, 1)
        self.db.add_comment(file_id, "注释", 1, "line")
        
        # 获取统计信息
        stats = self.db.get_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['files'], 1)
        self.assertEqual(stats['functions'], 2)
        self.assertEqual(stats['classes'], 1)
        self.assertEqual(stats['imports'], 1)
        self.assertEqual(stats['comments'], 1)
    
    def test_clear_database(self):
        """测试清空数据库"""
        # 添加测试数据
        file_id = self.db.add_file("/test/example.py", "test content")
        self.db.add_function(file_id, "func1", "函数1", 1, 5)
        
        # 验证数据存在
        stats_before = self.db.get_statistics()
        self.assertGreater(stats_before['files'], 0)
        self.assertGreater(stats_before['functions'], 0)
        
        # 清空数据库
        self.db.clear_database()
        
        # 验证数据已清空
        stats_after = self.db.get_statistics()
        self.assertEqual(stats_after['files'], 0)
        self.assertEqual(stats_after['functions'], 0)
        self.assertEqual(stats_after['classes'], 0)
        self.assertEqual(stats_after['imports'], 0)
        self.assertEqual(stats_after['comments'], 0)
    
    def test_close_database(self):
        """测试关闭数据库连接"""
        # 验证连接存在
        self.assertIsNotNone(self.db.conn)
        
        # 关闭连接
        self.db.close()
        
        # 验证连接已关闭
        self.assertIsNone(self.db.conn)
    
    def test_database_error_handling(self):
        """测试数据库错误处理"""
        # 关闭数据库连接
        self.db.close()
        
        # 尝试在关闭的连接上执行操作
        with self.assertRaises(Exception):
            self.db.add_file("/test/example.py", "content")
    
    def test_duplicate_file_handling(self):
        """测试重复文件处理"""
        file_path = "/test/example.py"
        content1 = "print('hello')"
        content2 = "print('world')"
        
        # 添加第一个文件
        file_id1 = self.db.add_file(file_path, content1)
        
        # 添加相同路径的文件（应该更新内容）
        file_id2 = self.db.add_file(file_path, content2)
        
        # 验证文件内容已更新
        result = self.db.get_file_by_path(file_path)
        self.assertEqual(result[2], content2)
    
    def test_transaction_rollback(self):
        """测试事务回滚"""
        # 开始事务
        cursor = self.db.conn.cursor()
        
        try:
            # 添加文件
            file_id = self.db.add_file("/test/example.py", "content")
            
            # 故意引发错误
            cursor.execute("INSERT INTO invalid_table VALUES (1)")
            
            self.db.conn.commit()
        except sqlite3.Error:
            self.db.conn.rollback()
        
        # 验证文件仍然存在（因为add_file有自己的提交）
        result = self.db.get_file_by_path("/test/example.py")
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()