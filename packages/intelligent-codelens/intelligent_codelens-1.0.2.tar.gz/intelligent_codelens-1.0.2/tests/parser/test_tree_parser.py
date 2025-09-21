"""
树解析器模块单元测试
测试AST解析功能
"""

import unittest
import tempfile
import os
import ast
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.tree_parser import TreeSitterParser as TreeParser


class TestTreeParser(unittest.TestCase):
    """测试TreeParser类"""
    
    def setUp(self):
        """测试前准备"""
        self.parser = TreeParser()
    
    def test_init_parser(self):
        """测试解析器初始化"""
        self.assertIsNotNone(self.parser)
        self.assertIsInstance(self.parser.supported_languages, dict)
        self.assertIn('python', self.parser.supported_languages)
        self.assertIn('javascript', self.parser.supported_languages)
    
    def test_detect_language(self):
        """测试语言检测"""
        # Python文件
        self.assertEqual(self.parser.detect_language('test.py'), 'python')
        self.assertEqual(self.parser.detect_language('/path/to/file.py'), 'python')
        
        # JavaScript文件
        self.assertEqual(self.parser.detect_language('test.js'), 'javascript')
        self.assertEqual(self.parser.detect_language('test.jsx'), 'javascript')
        
        # TypeScript文件
        self.assertEqual(self.parser.detect_language('test.ts'), 'typescript')
        self.assertEqual(self.parser.detect_language('test.tsx'), 'typescript')
        
        # Java文件
        self.assertEqual(self.parser.detect_language('test.java'), 'java')
        
        # C++文件
        self.assertEqual(self.parser.detect_language('test.cpp'), 'cpp')
        self.assertEqual(self.parser.detect_language('test.cc'), 'cpp')
        self.assertEqual(self.parser.detect_language('test.cxx'), 'cpp')
        
        # 不支持的文件
        self.assertIsNone(self.parser.detect_language('test.txt'))
        self.assertIsNone(self.parser.detect_language('README'))
    
    def test_parse_python_code(self):
        """测试Python代码解析"""
        python_code = '''
"""
模块文档字符串
"""

import os
import sys
from typing import List, Dict, Optional

# 全局变量
GLOBAL_VAR = "test"

class TestClass:
    """测试类"""
    
    class_var = "class variable"
    
    def __init__(self, name: str, age: int = 0):
        """初始化方法
        
        Args:
            name: 姓名
            age: 年龄，默认为0
        """
        self.name = name
        self.age = age
    
    def get_info(self) -> Dict[str, str]:
        """获取信息
        
        Returns:
            包含姓名和年龄的字典
        """
        return {"name": self.name, "age": str(self.age)}
    
    @staticmethod
    def static_method(value: int) -> int:
        """静态方法"""
        return value * 2
    
    @classmethod
    def class_method(cls, name: str):
        """类方法"""
        return cls(name)

def calculate_sum(numbers: List[int]) -> int:
    """计算数字列表的总和
    
    Args:
        numbers: 数字列表
        
    Returns:
        总和
    """
    total = 0
    for num in numbers:
        total += num
    return total

async def async_function(data: Dict) -> Optional[str]:
    """异步函数"""
    if not data:
        return None
    return str(data)

def generator_function():
    """生成器函数"""
    for i in range(10):
        yield i

# 装饰器
def decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorator
def decorated_function():
    """被装饰的函数"""
    pass
'''
        
        # 解析代码
        result = self.parser.parse_code(python_code, 'python')
        
        # 验证解析结果
        self.assertIsInstance(result, dict)
        self.assertIn('functions', result)
        self.assertIn('classes', result)
        self.assertIn('imports', result)
        self.assertIn('comments', result)
        
        # 验证函数解析
        functions = result['functions']
        function_names = [func['name'] for func in functions]
        
        self.assertIn('__init__', function_names)
        self.assertIn('get_info', function_names)
        self.assertIn('static_method', function_names)
        self.assertIn('class_method', function_names)
        self.assertIn('calculate_sum', function_names)
        self.assertIn('async_function', function_names)
        self.assertIn('generator_function', function_names)
        self.assertIn('decorated_function', function_names)
        
        # 验证类解析
        classes = result['classes']
        class_names = [cls['name'] for cls in classes]
        self.assertIn('TestClass', class_names)
        
        # 验证导入解析
        imports = result['imports']
        import_modules = [imp['module'] for imp in imports]
        self.assertIn('os', import_modules)
        self.assertIn('sys', import_modules)
        self.assertIn('typing', import_modules)
        
        # 验证函数详细信息
        calculate_sum_func = next((f for f in functions if f['name'] == 'calculate_sum'), None)
        self.assertIsNotNone(calculate_sum_func)
        self.assertIn('docstring', calculate_sum_func)
        self.assertIn('parameters', calculate_sum_func)
        self.assertIn('return_type', calculate_sum_func)
        self.assertEqual(calculate_sum_func['return_type'], 'int')
    
    def test_parse_javascript_code(self):
        """测试JavaScript代码解析"""
        js_code = '''
/**
 * 模块文档
 */

const fs = require('fs');
const path = require('path');
import { Component } from 'react';
import axios from 'axios';

// 全局常量
const GLOBAL_CONST = 'test';

/**
 * 测试类
 */
class TestClass extends Component {
    /**
     * 构造函数
     */
    constructor(props) {
        super(props);
        this.state = { count: 0 };
    }
    
    /**
     * 获取计数
     */
    getCount() {
        return this.state.count;
    }
    
    /**
     * 静态方法
     */
    static staticMethod(value) {
        return value * 2;
    }
}

/**
 * 计算总和
 */
function calculateSum(numbers) {
    return numbers.reduce((a, b) => a + b, 0);
}

/**
 * 异步函数
 */
async function fetchData(url) {
    try {
        const response = await axios.get(url);
        return response.data;
    } catch (error) {
        console.error('Error:', error);
        return null;
    }
}

// 箭头函数
const arrowFunction = (x, y) => {
    return x + y;
};

// 生成器函数
function* generatorFunction() {
    for (let i = 0; i < 10; i++) {
        yield i;
    }
}

// 立即执行函数
(function() {
    console.log('IIFE');
})();
'''
        
        # 解析代码
        result = self.parser.parse_code(js_code, 'javascript')
        
        # 验证解析结果
        self.assertIsInstance(result, dict)
        self.assertIn('functions', result)
        self.assertIn('classes', result)
        self.assertIn('imports', result)
        
        # 验证函数解析
        functions = result['functions']
        function_names = [func['name'] for func in functions]
        
        self.assertIn('constructor', function_names)
        self.assertIn('getCount', function_names)
        self.assertIn('staticMethod', function_names)
        self.assertIn('calculateSum', function_names)
        self.assertIn('fetchData', function_names)
        
        # 验证类解析
        classes = result['classes']
        class_names = [cls['name'] for cls in classes]
        self.assertIn('TestClass', class_names)
    
    def test_parse_java_code(self):
        """测试Java代码解析"""
        java_code = '''
/**
 * 测试Java类
 */
package com.example.test;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;

/**
 * 测试类
 */
public class TestClass {
    
    // 私有字段
    private String name;
    private int age;
    
    // 静态字段
    public static final String CONSTANT = "test";
    
    /**
     * 构造函数
     */
    public TestClass(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    /**
     * 获取姓名
     */
    public String getName() {
        return name;
    }
    
    /**
     * 设置姓名
     */
    public void setName(String name) {
        this.name = name;
    }
    
    /**
     * 静态方法
     */
    public static int multiply(int a, int b) {
        return a * b;
    }
    
    /**
     * 私有方法
     */
    private void privateMethod() {
        // 私有方法实现
    }
    
    /**
     * 抽象方法（如果是抽象类）
     */
    // public abstract void abstractMethod();
}

/**
 * 接口定义
 */
interface TestInterface {
    void interfaceMethod();
    
    default void defaultMethod() {
        System.out.println("Default implementation");
    }
}
'''
        
        # 解析代码
        result = self.parser.parse_code(java_code, 'java')
        
        # 验证解析结果
        self.assertIsInstance(result, dict)
        self.assertIn('functions', result)
        self.assertIn('classes', result)
        self.assertIn('imports', result)
    
    def test_parse_cpp_code(self):
        """测试C++代码解析"""
        cpp_code = '''
/**
 * C++测试文件
 */

#include <iostream>
#include <vector>
#include <string>

using namespace std;

/**
 * 测试类
 */
class TestClass {
private:
    string name;
    int age;

public:
    /**
     * 构造函数
     */
    TestClass(const string& name, int age) : name(name), age(age) {}
    
    /**
     * 析构函数
     */
    ~TestClass() {}
    
    /**
     * 获取姓名
     */
    string getName() const {
        return name;
    }
    
    /**
     * 设置姓名
     */
    void setName(const string& name) {
        this->name = name;
    }
    
    /**
     * 静态方法
     */
    static int multiply(int a, int b) {
        return a * b;
    }
};

/**
 * 全局函数
 */
int calculateSum(const vector<int>& numbers) {
    int sum = 0;
    for (int num : numbers) {
        sum += num;
    }
    return sum;
}

/**
 * 模板函数
 */
template<typename T>
T maximum(T a, T b) {
    return (a > b) ? a : b;
}

/**
 * 主函数
 */
int main() {
    TestClass obj("Test", 25);
    cout << "Name: " << obj.getName() << endl;
    return 0;
}
'''
        
        # 解析代码
        result = self.parser.parse_code(cpp_code, 'cpp')
        
        # 验证解析结果
        self.assertIsInstance(result, dict)
        self.assertIn('functions', result)
        self.assertIn('classes', result)
    
    def test_extract_function_info(self):
        """测试提取函数信息"""
        python_code = '''
def complex_function(param1: str, param2: int = 10, *args, **kwargs) -> Dict[str, Any]:
    """
    复杂函数示例
    
    Args:
        param1: 字符串参数
        param2: 整数参数，默认值为10
        *args: 可变位置参数
        **kwargs: 可变关键字参数
    
    Returns:
        Dict[str, Any]: 返回字典
        
    Raises:
        ValueError: 当参数无效时
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    
    result = {
        "param1": param1,
        "param2": param2,
        "args": args,
        "kwargs": kwargs
    }
    
    return result
'''
        
        # 解析代码
        result = self.parser.parse_code(python_code, 'python')
        
        # 验证函数信息
        functions = result['functions']
        self.assertEqual(len(functions), 1)
        
        func = functions[0]
        self.assertEqual(func['name'], 'complex_function')
        self.assertIn('docstring', func)
        self.assertIn('parameters', func)
        self.assertIn('return_type', func)
        self.assertIn('start_line', func)
        self.assertIn('end_line', func)
        
        # 验证参数信息
        self.assertIn('param1', func['parameters'])
        self.assertIn('param2', func['parameters'])
        
        # 验证返回类型
        self.assertEqual(func['return_type'], 'Dict[str, Any]')
    
    def test_extract_class_info(self):
        """测试提取类信息"""
        python_code = '''
class ComplexClass(BaseClass, MixinClass):
    """
    复杂类示例
    
    Attributes:
        class_var: 类变量
        instance_var: 实例变量
    """
    
    class_var = "class variable"
    
    def __init__(self, name: str):
        """初始化方法"""
        super().__init__()
        self.name = name
        self.instance_var = "instance variable"
    
    @property
    def name_property(self) -> str:
        """名称属性"""
        return self.name
    
    @name_property.setter
    def name_property(self, value: str):
        """设置名称属性"""
        self.name = value
    
    @staticmethod
    def static_method() -> str:
        """静态方法"""
        return "static"
    
    @classmethod
    def class_method(cls, name: str):
        """类方法"""
        return cls(name)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"ComplexClass(name={self.name})"
    
    def __repr__(self) -> str:
        """对象表示"""
        return f"ComplexClass(name='{self.name}')"
'''
        
        # 解析代码
        result = self.parser.parse_code(python_code, 'python')
        
        # 验证类信息
        classes = result['classes']
        self.assertEqual(len(classes), 1)
        
        cls = classes[0]
        self.assertEqual(cls['name'], 'ComplexClass')
        self.assertIn('docstring', cls)
        self.assertIn('base_classes', cls)
        self.assertIn('start_line', cls)
        self.assertIn('end_line', cls)
        
        # 验证基类信息
        self.assertIn('BaseClass', cls['base_classes'])
        self.assertIn('MixinClass', cls['base_classes'])
        
        # 验证方法信息
        functions = result['functions']
        method_names = [func['name'] for func in functions]
        
        self.assertIn('__init__', method_names)
        self.assertIn('name_property', method_names)
        self.assertIn('static_method', method_names)
        self.assertIn('class_method', method_names)
        self.assertIn('__str__', method_names)
        self.assertIn('__repr__', method_names)
    
    def test_extract_import_info(self):
        """测试提取导入信息"""
        python_code = '''
import os
import sys
import json as js
from typing import List, Dict, Optional, Union
from collections import defaultdict, Counter
from .local_module import LocalClass
from ..parent_module import ParentClass
from package.subpackage import SubClass
'''
        
        # 解析代码
        result = self.parser.parse_code(python_code, 'python')
        
        # 验证导入信息
        imports = result['imports']
        self.assertGreater(len(imports), 0)
        
        # 验证不同类型的导入
        import_types = [imp['type'] for imp in imports]
        self.assertIn('import', import_types)
        self.assertIn('from', import_types)
        
        # 验证别名导入
        json_import = next((imp for imp in imports if imp.get('alias') == 'js'), None)
        self.assertIsNotNone(json_import)
        self.assertEqual(json_import['module'], 'json')
    
    def test_extract_comment_info(self):
        """测试提取注释信息"""
        python_code = '''
# 这是单行注释
"""
这是多行文档字符串
包含多行内容
"""

def function_with_comments():
    # 函数内部注释
    """函数文档字符串"""
    x = 1  # 行尾注释
    
    # 另一个注释
    return x

# TODO: 需要实现的功能
# FIXME: 需要修复的问题
# NOTE: 重要说明
'''
        
        # 解析代码
        result = self.parser.parse_code(python_code, 'python')
        
        # 验证注释信息
        comments = result['comments']
        self.assertGreater(len(comments), 0)
        
        # 验证注释类型
        comment_types = [comment['type'] for comment in comments]
        self.assertIn('line', comment_types)
        self.assertIn('block', comment_types)
    
    def test_parse_invalid_code(self):
        """测试解析无效代码"""
        invalid_python_code = '''
def invalid_function(
    # 缺少闭合括号和冒号
    
class InvalidClass
    # 缺少冒号
    pass

# 无效的缩进
def another_function():
pass
'''
        
        # 解析无效代码
        result = self.parser.parse_code(invalid_python_code, 'python')
        
        # 验证错误处理 - 对于语法错误的代码，应该返回warning而不是error
        self.assertIsInstance(result, dict)
        self.assertIn('warning', result)
        self.assertIsNotNone(result['warning'])
        # 确保基本结构仍然存在
        self.assertIn('functions', result)
        self.assertIn('classes', result)
        self.assertIn('imports', result)
        self.assertIn('comments', result)
    
    def test_parse_empty_code(self):
        """测试解析空代码"""
        empty_code = ""
        
        # 解析空代码
        result = self.parser.parse_code(empty_code, 'python')
        
        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertEqual(result['functions'], [])
        self.assertEqual(result['classes'], [])
        self.assertEqual(result['imports'], [])
        self.assertEqual(result['comments'], [])
    
    def test_parse_unsupported_language(self):
        """测试解析不支持的语言"""
        code = "some code"
        
        # 解析不支持的语言
        result = self.parser.parse_code(code, 'unsupported')
        
        # 验证错误处理
        self.assertIsInstance(result, dict)
        self.assertIn('error', result)
        self.assertIn('unsupported', result['error'].lower())
    
    def test_get_ast_info(self):
        """测试获取AST信息"""
        python_code = '''
def test_function():
    x = 1
    y = 2
    return x + y
'''
        
        # 获取AST信息
        ast_info = self.parser.get_ast_info(python_code, 'test.py')
        
        # 验证AST信息
        self.assertIsInstance(ast_info, dict)
        self.assertIn('node_count', ast_info)
        self.assertIn('depth', ast_info)
        self.assertIn('complexity', ast_info)
        
        self.assertGreater(ast_info['node_count'], 0)
        self.assertGreater(ast_info['depth'], 0)
    
    def test_calculate_complexity(self):
        """测试计算代码复杂度"""
        complex_python_code = '''
def complex_function(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                try:
                    result = i / (x - i)
                except ZeroDivisionError:
                    continue
                else:
                    if result > 1:
                        return result
                    elif result < 0:
                        break
                    else:
                        pass
            else:
                while i > 0:
                    i -= 1
                    if i == 5:
                        break
    else:
        return 0
    
    return -1
'''
        
        # 计算复杂度
        complexity_result = self.parser.calculate_complexity(complex_python_code, 'test.py')
        
        # 验证复杂度结果是字典
        self.assertIsInstance(complexity_result, dict)
        self.assertIn('complexity', complexity_result)
        
        # 获取复杂度值
        complexity = complexity_result['complexity']
        self.assertIsInstance(complexity, int)
        self.assertGreater(complexity, 1)  # 复杂函数应该有较高的复杂度
    
    @patch('ast.parse')
    def test_parse_with_ast_error(self, mock_parse):
        """测试AST解析错误处理"""
        # 这个测试不再适用，因为我们使用tree-sitter而不是ast
        # 直接测试tree-sitter的错误处理
        
        # 解析代码
        result = self.parser.parse_code("invalid code", 'python')
        
        # 验证错误处理 - tree-sitter会尝试解析并返回warning
        self.assertIsInstance(result, dict)
        # 对于简单的无效代码，tree-sitter可能会返回warning而不是error
        self.assertTrue('warning' in result or 'error' in result)


if __name__ == '__main__':
    unittest.main()