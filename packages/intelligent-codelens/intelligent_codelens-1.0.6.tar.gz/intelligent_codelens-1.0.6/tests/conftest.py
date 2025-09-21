"""
pytest配置文件
设置测试环境和共享fixtures
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path
import sqlite3
import shutil

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.database import CodeDatabase
from src.core.semantic_search import SemanticSearchEngine
from src.core.indexer import CodeIndexer
from src.core.tree_parser import TreeSitterParser as TreeParser


@pytest.fixture(scope="session")
def test_data_dir():
    """创建测试数据目录"""
    test_dir = tempfile.mkdtemp(prefix="test_code_search_")
    
    # 创建测试文件
    test_files = {
        "test_python.py": '''
def hello_world():
    """打印Hello World"""
    print("Hello, World!")
    return "Hello, World!"

class Calculator:
    """简单计算器类"""
    
    def add(self, a, b):
        """加法运算"""
        return a + b
    
    def multiply(self, a, b):
        """乘法运算"""
        return a * b

def fibonacci(n):
    """计算斐波那契数列"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
''',
        "test_javascript.js": '''
function greetUser(name) {
    /**
     * 问候用户
     * @param {string} name - 用户名
     * @returns {string} 问候语
     */
    return `Hello, ${name}!`;
}

class DataProcessor {
    /**
     * 数据处理器类
     */
    constructor() {
        this.data = [];
    }
    
    addData(item) {
        /**
         * 添加数据项
         * @param {any} item - 数据项
         */
        this.data.push(item);
    }
    
    processData() {
        /**
         * 处理数据
         * @returns {Array} 处理后的数据
         */
        return this.data.map(item => item.toString().toUpperCase());
    }
}

const utils = {
    formatDate: function(date) {
        return date.toISOString().split('T')[0];
    },
    
    validateEmail: function(email) {
        const regex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
        return regex.test(email);
    }
};
''',
        "test_java.java": '''
public class StringUtils {
    /**
     * 字符串工具类
     */
    
    public static boolean isEmpty(String str) {
        /**
         * 检查字符串是否为空
         * @param str 待检查的字符串
         * @return 是否为空
         */
        return str == null || str.length() == 0;
    }
    
    public static String reverse(String str) {
        /**
         * 反转字符串
         * @param str 待反转的字符串
         * @return 反转后的字符串
         */
        if (isEmpty(str)) {
            return str;
        }
        return new StringBuilder(str).reverse().toString();
    }
}

public class MathHelper {
    /**
     * 数学辅助类
     */
    
    public static int factorial(int n) {
        /**
         * 计算阶乘
         * @param n 输入数字
         * @return 阶乘结果
         */
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }
    
    public static boolean isPrime(int n) {
        /**
         * 检查是否为质数
         * @param n 待检查的数字
         * @return 是否为质数
         */
        if (n <= 1) {
            return false;
        }
        for (int i = 2; i <= Math.sqrt(n); i++) {
            if (n % i == 0) {
                return false;
            }
        }
        return true;
    }
}
'''
    }
    
    # 写入测试文件
    for filename, content in test_files.items():
        file_path = os.path.join(test_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    yield test_dir
    
    # 清理测试目录
    shutil.rmtree(test_dir, ignore_errors=True)


@pytest.fixture
def temp_db():
    """创建临时数据库"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    db = CodeDatabase(db_path)
    yield db
    
    db.close()
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def populated_db(temp_db, test_data_dir):
    """创建填充了测试数据的数据库"""
    # 使用索引器填充数据库
    indexer = CodeIndexer(temp_db)
    indexer.index_directory(test_data_dir)
    
    return temp_db


@pytest.fixture
def search_engine(populated_db):
    """创建搜索引擎实例"""
    return SemanticSearchEngine(populated_db)


@pytest.fixture
def tree_parser():
    """创建树解析器实例"""
    return TreeParser()


@pytest.fixture
def code_indexer(temp_db):
    """创建代码索引器实例"""
    return CodeIndexer(temp_db)


@pytest.fixture
def sample_python_code():
    """示例Python代码"""
    return '''
def calculate_area(radius):
    """计算圆的面积"""
    import math
    return math.pi * radius ** 2

class Shape:
    """形状基类"""
    
    def __init__(self, name):
        self.name = name
    
    def get_area(self):
        """获取面积"""
        raise NotImplementedError("子类必须实现此方法")

class Circle(Shape):
    """圆形类"""
    
    def __init__(self, radius):
        super().__init__("Circle")
        self.radius = radius
    
    def get_area(self):
        """获取圆的面积"""
        return calculate_area(self.radius)
'''


@pytest.fixture
def sample_javascript_code():
    """示例JavaScript代码"""
    return '''
function calculateDistance(x1, y1, x2, y2) {
    /**
     * 计算两点间距离
     */
    const dx = x2 - x1;
    const dy = y2 - y1;
    return Math.sqrt(dx * dx + dy * dy);
}

class Point {
    /**
     * 点类
     */
    constructor(x, y) {
        this.x = x;
        this.y = y;
    }
    
    distanceTo(other) {
        /**
         * 计算到另一点的距离
         */
        return calculateDistance(this.x, this.y, other.x, other.y);
    }
}
'''


@pytest.fixture
def sample_java_code():
    """示例Java代码"""
    return '''
public class ArrayUtils {
    /**
     * 数组工具类
     */
    
    public static int findMax(int[] array) {
        /**
         * 查找数组中的最大值
         */
        if (array == null || array.length == 0) {
            throw new IllegalArgumentException("数组不能为空");
        }
        
        int max = array[0];
        for (int i = 1; i < array.length; i++) {
            if (array[i] > max) {
                max = array[i];
            }
        }
        return max;
    }
    
    public static void bubbleSort(int[] array) {
        /**
         * 冒泡排序
         */
        int n = array.length;
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (array[j] > array[j + 1]) {
                    int temp = array[j];
                    array[j] = array[j + 1];
                    array[j + 1] = temp;
                }
            }
        }
    }
}
'''


# 测试配置
def pytest_configure(config):
    """pytest配置"""
    # 添加自定义标记
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试项目收集"""
    # 为没有标记的测试添加unit标记
    for item in items:
        if not any(item.iter_markers()):
            item.add_marker(pytest.mark.unit)


# 测试会话钩子
def pytest_sessionstart(session):
    """测试会话开始"""
    print("\\n开始运行代码搜索系统单元测试...")


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束"""
    if exitstatus == 0:
        print("\\n所有测试通过! ✅")
    else:
        print(f"\\n测试失败，退出状态: {exitstatus} ❌")


# 测试失败时的处理
def pytest_runtest_makereport(item, call):
    """生成测试报告"""
    if call.when == "call" and call.excinfo is not None:
        # 测试失败时的额外信息
        print(f"\\n测试失败: {item.name}")
        print(f"错误信息: {call.excinfo.value}")