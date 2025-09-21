#!/usr/bin/env python3
"""
基础功能测试脚本
测试代码解析、索引和数据库存储功能
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tree_parser import TreeSitterParser
from database import CodeDatabase
from indexer import CodeIndexer

def create_test_files():
    """创建测试用的代码文件"""
    test_dir = tempfile.mkdtemp(prefix="code_search_test_")
    
    # Python测试文件
    python_code = '''
def calculate_sum(a, b):
    """计算两个数的和"""
    return a + b

class Calculator:
    """简单计算器类"""
    
    def __init__(self):
        self.history = []
    
    def add(self, x, y):
        """加法运算"""
        result = x + y
        self.history.append(f"{x} + {y} = {result}")
        return result
    
    def multiply(self, x, y):
        """乘法运算"""
        result = x * y
        self.history.append(f"{x} * {y} = {result}")
        return result
'''
    
    # JavaScript测试文件
    js_code = '''
function validateEmail(email) {
    // 验证邮箱格式
    const regex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
    return regex.test(email);
}

class UserManager {
    constructor() {
        this.users = [];
    }
    
    addUser(name, email) {
        if (!validateEmail(email)) {
            throw new Error('Invalid email format');
        }
        
        const user = {
            id: this.users.length + 1,
            name: name,
            email: email,
            createdAt: new Date()
        };
        
        this.users.push(user);
        return user;
    }
    
    findUserByEmail(email) {
        return this.users.find(user => user.email === email);
    }
}
'''
    
    # Java测试文件
    java_code = '''
public class StringUtils {
    
    /**
     * 检查字符串是否为空或null
     */
    public static boolean isEmpty(String str) {
        return str == null || str.trim().length() == 0;
    }
    
    /**
     * 反转字符串
     */
    public static String reverse(String str) {
        if (isEmpty(str)) {
            return str;
        }
        return new StringBuilder(str).reverse().toString();
    }
    
    /**
     * 首字母大写
     */
    public static String capitalize(String str) {
        if (isEmpty(str)) {
            return str;
        }
        return str.substring(0, 1).toUpperCase() + str.substring(1).toLowerCase();
    }
}

public class DataProcessor {
    private List<String> data;
    
    public DataProcessor() {
        this.data = new ArrayList<>();
    }
    
    public void processData(String input) {
        if (!StringUtils.isEmpty(input)) {
            data.add(StringUtils.capitalize(input));
        }
    }
    
    public List<String> getData() {
        return new ArrayList<>(data);
    }
}
'''
    
    # 写入测试文件
    with open(os.path.join(test_dir, "calculator.py"), "w", encoding="utf-8") as f:
        f.write(python_code)
    
    with open(os.path.join(test_dir, "user_manager.js"), "w", encoding="utf-8") as f:
        f.write(js_code)
    
    with open(os.path.join(test_dir, "StringUtils.java"), "w", encoding="utf-8") as f:
        f.write(java_code)
    
    return test_dir

def test_tree_parser():
    """测试TreeSitter解析器"""
    print("🔍 测试TreeSitter解析器...")
    
    test_dir = create_test_files()
    parser = TreeSitterParser()
    
    try:
        # 测试Python文件解析
        python_file = os.path.join(test_dir, "calculator.py")
        result = parser.parse_file(python_file)
        
        if result:
            print(f"✅ Python文件解析成功")
            print(f"   - 函数数量: {len(result.get('functions', []))}")
            print(f"   - 类数量: {len(result.get('classes', []))}")
            
            # 检查具体函数
            functions = result.get('functions', [])
            expected_functions = ['calculate_sum', 'add', 'multiply']
            found_functions = [f['name'] for f in functions]
            
            for func_name in expected_functions:
                if func_name in found_functions:
                    print(f"   ✅ 找到函数: {func_name}")
                else:
                    print(f"   ❌ 未找到函数: {func_name}")
        else:
            print("❌ Python文件解析失败")
        
        # 测试JavaScript文件解析
        js_file = os.path.join(test_dir, "user_manager.js")
        result = parser.parse_file(js_file)
        
        if result:
            print(f"✅ JavaScript文件解析成功")
            print(f"   - 函数数量: {len(result.get('functions', []))}")
            print(f"   - 类数量: {len(result.get('classes', []))}")
        else:
            print("❌ JavaScript文件解析失败")
        
        # 测试Java文件解析
        java_file = os.path.join(test_dir, "StringUtils.java")
        result = parser.parse_file(java_file)
        
        if result:
            print(f"✅ Java文件解析成功")
            print(f"   - 函数数量: {len(result.get('functions', []))}")
            print(f"   - 类数量: {len(result.get('classes', []))}")
        else:
            print("❌ Java文件解析失败")
            
    finally:
        # 清理测试文件
        shutil.rmtree(test_dir)
    
    print()

def test_database():
    """测试数据库功能"""
    print("💾 测试数据库功能...")
    
    # 创建临时数据库
    db_path = tempfile.mktemp(suffix=".db")
    db = CodeDatabase(db_path)
    
    try:
        # 测试文件存储
        file_data = {
            'path': '/test/example.py',
            'language': 'python',
            'size': 1024,
            'modified_time': '2025-01-01 12:00:00',
            'content': 'def hello(): return "world"'
        }
        
        # 构造完整的文件数据
        complete_file_data = {
            'file_path': '/test/example.py',
            'language': 'python',
            'content': 'def hello(): return "world"',
            'functions': [{
                'name': 'hello',
                'start_line': 1,
                'end_line': 1,
                'parameters': [],
                'docstring': 'Test function',
                'body': 'return "world"'
            }],
            'classes': [],
            'imports': [],
            'comments': []
        }
        
        file_id = db.store_file_data(complete_file_data)
        if file_id:
            print("✅ 文件存储成功")
        else:
            print("❌ 文件存储失败")
        
        # 测试搜索功能
        results = db.search_functions("hello")
        if results:
            print(f"✅ 函数搜索成功，找到 {len(results)} 个结果")
        else:
            print("❌ 函数搜索失败")
        
        # 测试统计信息
        stats = db.get_stats()
        print(f"✅ 统计信息获取成功:")
        print(f"   - 文件数: {stats['files']}")
        print(f"   - 函数数: {stats['functions']}")
        print(f"   - 类数: {stats['classes']}")
        
    finally:
        db.close()
        if os.path.exists(db_path):
            os.remove(db_path)
    
    print()

def test_indexer():
    """测试索引器功能"""
    print("📚 测试索引器功能...")
    
    test_dir = create_test_files()
    db_path = tempfile.mktemp(suffix=".db")
    
    try:
        # 创建临时配置
        config = {
            'repo_path': test_dir,
            'languages': ['python', 'javascript', 'java'],
            'file_extensions': {
                'python': ['.py'],
                'javascript': ['.js'],
                'java': ['.java']
            },
            'exclude_patterns': ['__pycache__', '.git', 'node_modules'],
            'batch_size': 10
        }
        
        # 创建索引器
        indexer = CodeIndexer()
        indexer.config = config
        indexer.db = CodeDatabase(db_path)
        
        # 执行索引
        stats = indexer.index_repository(test_dir)
        
        print(f"✅ 索引完成:")
        print(f"   - 处理文件数: {stats.get('total_files', 0)}")
        print(f"   - 成功处理: {stats.get('success_count', 0)}")
        print(f"   - 处理失败: {stats.get('error_count', 0)}")
        print(f"   - 函数数: {stats.get('functions', 0)}")
        print(f"   - 类数: {stats.get('classes', 0)}")
        
    finally:
        # 清理
        shutil.rmtree(test_dir)
        if os.path.exists(db_path):
            os.remove(db_path)
    
    print()

def main():
    """主测试函数"""
    print("🚀 开始基础功能测试")
    print("=" * 50)
    
    test_tree_parser()
    test_database()
    test_indexer()
    
    print("✅ 基础功能测试完成!")

if __name__ == "__main__":
    main()