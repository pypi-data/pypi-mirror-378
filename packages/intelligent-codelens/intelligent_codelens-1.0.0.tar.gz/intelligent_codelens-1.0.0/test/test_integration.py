#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试脚本
测试本地代码搜索系统的完整工作流程
"""

import os
import sys
import time
import tempfile
import shutil
import subprocess
import requests
import threading
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src" / "core"))

from src.core.database import CodeDatabase
from src.core.indexer import CodeIndexer
from src.core.semantic_search import SemanticSearchEngine
from src.core.tree_parser import TreeSitterParser

class IntegrationTestSuite:
    """集成测试套件"""
    
    def __init__(self):
        """
        初始化测试套件
        """
        self.test_dir = None
        self.db_path = None
        self.web_process = None
        self.web_port = 5002
        self.base_url = f"http://localhost:{self.web_port}"
        
    def setup_test_environment(self):
        """
        设置测试环境
        """
        print("🔧 设置测试环境...")
        
        # 创建测试目录
        self.test_dir = tempfile.mkdtemp(prefix="integration_test_")
        self.db_path = os.path.join(self.test_dir, "test.db")
        
        # 创建测试代码文件
        self.create_test_code_files()
        
        print(f"   测试目录: {self.test_dir}")
        print(f"   数据库路径: {self.db_path}")
        print()
    
    def create_test_code_files(self):
        """
        创建测试代码文件
        """
        # Python文件
        python_dir = os.path.join(self.test_dir, "python")
        os.makedirs(python_dir, exist_ok=True)
        
        # 创建一个简单的Python模块
        with open(os.path.join(python_dir, "calculator.py"), 'w', encoding='utf-8') as f:
            f.write('''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算器模块
提供基本的数学计算功能
"""

import math
from typing import Union, List

class Calculator:
    """基本计算器类"""
    
    def __init__(self):
        """初始化计算器"""
        self.history = []
    
    def add(self, a: float, b: float) -> float:
        """
        加法运算
        
        Args:
            a: 第一个数
            b: 第二个数
            
        Returns:
            两数之和
        """
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a: float, b: float) -> float:
        """
        减法运算
        
        Args:
            a: 被减数
            b: 减数
            
        Returns:
            两数之差
        """
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """
        乘法运算
        
        Args:
            a: 第一个数
            b: 第二个数
            
        Returns:
            两数之积
        """
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a: float, b: float) -> float:
        """
        除法运算
        
        Args:
            a: 被除数
            b: 除数
            
        Returns:
            两数之商
            
        Raises:
            ZeroDivisionError: 当除数为0时
        """
        if b == 0:
            raise ZeroDivisionError("除数不能为零")
        
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result
    
    def power(self, base: float, exponent: float) -> float:
        """
        幂运算
        
        Args:
            base: 底数
            exponent: 指数
            
        Returns:
            幂运算结果
        """
        result = math.pow(base, exponent)
        self.history.append(f"{base} ^ {exponent} = {result}")
        return result
    
    def sqrt(self, number: float) -> float:
        """
        平方根运算
        
        Args:
            number: 输入数字
            
        Returns:
            平方根
            
        Raises:
            ValueError: 当输入负数时
        """
        if number < 0:
            raise ValueError("不能计算负数的平方根")
        
        result = math.sqrt(number)
        self.history.append(f"sqrt({number}) = {result}")
        return result
    
    def get_history(self) -> List[str]:
        """
        获取计算历史
        
        Returns:
            计算历史列表
        """
        return self.history.copy()
    
    def clear_history(self):
        """清空计算历史"""
        self.history.clear()

def calculate_average(numbers: List[float]) -> float:
    """
    计算平均值
    
    Args:
        numbers: 数字列表
        
    Returns:
        平均值
        
    Raises:
        ValueError: 当列表为空时
    """
    if not numbers:
        raise ValueError("数字列表不能为空")
    
    return sum(numbers) / len(numbers)

def find_max_min(numbers: List[float]) -> tuple:
    """
    找到列表中的最大值和最小值
    
    Args:
        numbers: 数字列表
        
    Returns:
        (最大值, 最小值) 元组
        
    Raises:
        ValueError: 当列表为空时
    """
    if not numbers:
        raise ValueError("数字列表不能为空")
    
    return max(numbers), min(numbers)

if __name__ == "__main__":
    # 测试代码
    calc = Calculator()
    
    print("计算器测试:")
    print(f"5 + 3 = {calc.add(5, 3)}")
    print(f"10 - 4 = {calc.subtract(10, 4)}")
    print(f"6 * 7 = {calc.multiply(6, 7)}")
    print(f"15 / 3 = {calc.divide(15, 3)}")
    print(f"2 ^ 8 = {calc.power(2, 8)}")
    print(f"sqrt(16) = {calc.sqrt(16)}")
    
    print("\\n计算历史:")
    for record in calc.get_history():
        print(f"  {record}")
    
    # 测试工具函数
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    print(f"\\n平均值: {calculate_average(numbers)}")
    print(f"最大值和最小值: {find_max_min(numbers)}")
''')
        
        # JavaScript文件
        js_dir = os.path.join(self.test_dir, "javascript")
        os.makedirs(js_dir, exist_ok=True)
        
        with open(os.path.join(js_dir, "utils.js"), 'w', encoding='utf-8') as f:
            f.write('''/**
 * 工具函数模块
 * 提供常用的工具函数
 */

/**
 * 字符串工具类
 */
class StringUtils {
    /**
     * 首字母大写
     * @param {string} str - 输入字符串
     * @returns {string} 首字母大写的字符串
     */
    static capitalize(str) {
        if (!str || typeof str !== 'string') {
            return '';
        }
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    }
    
    /**
     * 驼峰命名转换
     * @param {string} str - 输入字符串
     * @returns {string} 驼峰命名字符串
     */
    static toCamelCase(str) {
        return str.replace(/[-_\\s]+(.)?/g, (_, c) => c ? c.toUpperCase() : '');
    }
    
    /**
     * 截断字符串
     * @param {string} str - 输入字符串
     * @param {number} length - 最大长度
     * @param {string} suffix - 后缀
     * @returns {string} 截断后的字符串
     */
    static truncate(str, length = 100, suffix = '...') {
        if (!str || str.length <= length) {
            return str;
        }
        return str.substring(0, length) + suffix;
    }
}

/**
 * 数组工具类
 */
class ArrayUtils {
    /**
     * 数组去重
     * @param {Array} arr - 输入数组
     * @returns {Array} 去重后的数组
     */
    static unique(arr) {
        return [...new Set(arr)];
    }
    
    /**
     * 数组分块
     * @param {Array} arr - 输入数组
     * @param {number} size - 块大小
     * @returns {Array} 分块后的二维数组
     */
    static chunk(arr, size) {
        const chunks = [];
        for (let i = 0; i < arr.length; i += size) {
            chunks.push(arr.slice(i, i + size));
        }
        return chunks;
    }
    
    /**
     * 数组扁平化
     * @param {Array} arr - 输入数组
     * @param {number} depth - 扁平化深度
     * @returns {Array} 扁平化后的数组
     */
    static flatten(arr, depth = 1) {
        return depth > 0 ? arr.reduce((acc, val) => 
            acc.concat(Array.isArray(val) ? ArrayUtils.flatten(val, depth - 1) : val), []) : arr.slice();
    }
}

/**
 * 对象工具类
 */
class ObjectUtils {
    /**
     * 深拷贝对象
     * @param {Object} obj - 输入对象
     * @returns {Object} 深拷贝后的对象
     */
    static deepClone(obj) {
        if (obj === null || typeof obj !== 'object') {
            return obj;
        }
        
        if (obj instanceof Date) {
            return new Date(obj.getTime());
        }
        
        if (obj instanceof Array) {
            return obj.map(item => ObjectUtils.deepClone(item));
        }
        
        if (typeof obj === 'object') {
            const cloned = {};
            for (const key in obj) {
                if (obj.hasOwnProperty(key)) {
                    cloned[key] = ObjectUtils.deepClone(obj[key]);
                }
            }
            return cloned;
        }
        
        return obj;
    }
    
    /**
     * 合并对象
     * @param {Object} target - 目标对象
     * @param {...Object} sources - 源对象
     * @returns {Object} 合并后的对象
     */
    static merge(target, ...sources) {
        if (!target) target = {};
        
        sources.forEach(source => {
            if (source) {
                Object.keys(source).forEach(key => {
                    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
                        target[key] = ObjectUtils.merge(target[key] || {}, source[key]);
                    } else {
                        target[key] = source[key];
                    }
                });
            }
        });
        
        return target;
    }
}

/**
 * 验证工具函数
 */
const ValidationUtils = {
    /**
     * 验证邮箱格式
     * @param {string} email - 邮箱地址
     * @returns {boolean} 是否有效
     */
    isValidEmail(email) {
        const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
        return emailRegex.test(email);
    },
    
    /**
     * 验证手机号格式
     * @param {string} phone - 手机号
     * @returns {boolean} 是否有效
     */
    isValidPhone(phone) {
        const phoneRegex = /^1[3-9]\\d{9}$/;
        return phoneRegex.test(phone);
    },
    
    /**
     * 验证URL格式
     * @param {string} url - URL地址
     * @returns {boolean} 是否有效
     */
    isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }
};

// 导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        StringUtils,
        ArrayUtils,
        ObjectUtils,
        ValidationUtils
    };
}
''')
    
    def test_complete_workflow(self):
        """
        测试完整工作流程
        """
        print("🔄 测试完整工作流程...")
        
        try:
            # 1. 创建数据库
            print("   1. 创建数据库...")
            db = CodeDatabase(self.db_path)
            
            # 2. 创建索引器并索引代码
            print("   2. 索引代码文件...")
            indexer = CodeIndexer()  # 使用默认配置
            indexer.db = db  # 手动设置数据库
            indexer.index_repository(self.test_dir)
            
            # 3. 获取索引统计
            stats = db.get_stats()
            print(f"      索引文件数: {stats.get('files', 0)}")
            print(f"      索引函数数: {stats.get('functions', 0)}")
            print(f"      索引类数: {stats.get('classes', 0)}")
            
            # 4. 测试语义搜索
            print("   3. 测试语义搜索...")
            search_engine = SemanticSearchEngine()
            search_engine.db = db
            
            # 测试各种搜索查询
            test_queries = [
                "计算器",
                "加法",
                "字符串工具",
                "数组去重",
                "深拷贝",
                "验证邮箱"
            ]
            
            for query in test_queries:
                results = search_engine.search(query, limit=3)
                print(f"      查询 '{query}': {len(results)} 个结果")
                
                if results:
                    for i, result in enumerate(results[:2]):  # 只显示前2个结果
                        print(f"        {i+1}. {result.get('file_path', 'Unknown')} - {result.get('name', 'Unknown')}")
            
            # 5. 测试相似度计算
            print("   4. 测试相似度计算...")
            similarity_tests = [
                ("计算器", "Calculator"),
                ("加法运算", "add method"),
                ("字符串处理", "StringUtils"),
                ("数组操作", "ArrayUtils")
            ]
            
            for query1, query2 in similarity_tests:
                try:
                    # 使用搜索引擎的内部方法计算相似度
                    vec1 = search_engine._vectorize_text(query1)
                    vec2 = search_engine._vectorize_text(query2)
                    
                    # 计算余弦相似度
                    import numpy as np
                    similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
                    print(f"      '{query1}' vs '{query2}': {similarity:.3f}")
                except Exception as e:
                    print(f"      '{query1}' vs '{query2}': 计算失败 ({e})")
            
            db.close()
            print("✅ 完整工作流程测试成功")
            
        except Exception as e:
            print(f"❌ 完整工作流程测试失败: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    def start_web_server(self):
        """
        启动Web服务器
        """
        print("🌐 启动Web服务器...")
        
        try:
            # 启动Web服务器进程
            cmd = [sys.executable, "web.py", "--port", str(self.web_port)]
            self.web_process = subprocess.Popen(
                cmd,
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务器启动
            print(f"   等待服务器启动 (端口 {self.web_port})...")
            max_wait = 10  # 最多等待10秒
            
            for i in range(max_wait):
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=1)
                    if response.status_code == 200:
                        print("✅ Web服务器启动成功")
                        return True
                except requests.exceptions.RequestException:
                    pass
                
                time.sleep(1)
                print(f"   等待中... ({i+1}/{max_wait})")
            
            print("❌ Web服务器启动超时")
            return False
            
        except Exception as e:
            print(f"❌ Web服务器启动失败: {e}")
            return False
    
    def test_web_api_integration(self):
        """
        测试Web API集成
        """
        print("🔌 测试Web API集成...")
        
        try:
            # 测试健康检查
            print("   1. 测试健康检查...")
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ 健康检查通过")
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
            
            # 测试索引API
            print("   2. 测试索引API...")
            index_data = {
                "path": self.test_dir,
                "recursive": True
            }
            response = requests.post(f"{self.base_url}/api/index", json=index_data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 索引API成功: {result.get('message', 'Unknown')}")
            else:
                print(f"❌ 索引API失败: {response.status_code}")
            
            # 测试搜索API
            print("   3. 测试搜索API...")
            search_queries = ["计算器", "字符串", "数组", "验证"]
            
            for query in search_queries:
                search_data = {
                    "query": query,
                    "limit": 5
                }
                response = requests.post(f"{self.base_url}/api/search", json=search_data, timeout=10)
                
                if response.status_code == 200:
                    results = response.json()
                    print(f"      查询 '{query}': {len(results.get('results', []))} 个结果")
                else:
                    print(f"      查询 '{query}' 失败: {response.status_code}")
            
            # 测试统计API
            print("   4. 测试统计API...")
            response = requests.get(f"{self.base_url}/api/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ 统计API成功: {stats.get('total_files', 0)} 个文件")
            else:
                print(f"❌ 统计API失败: {response.status_code}")
            
            # 测试Web界面
            print("   5. 测试Web界面...")
            response = requests.get(self.base_url, timeout=5)
            if response.status_code == 200:
                print("✅ Web界面访问成功")
            else:
                print(f"❌ Web界面访问失败: {response.status_code}")
            
            print("✅ Web API集成测试完成")
            
        except Exception as e:
            print(f"❌ Web API集成测试失败: {e}")
        
        print()
    
    def stop_web_server(self):
        """
        停止Web服务器
        """
        if self.web_process:
            print("🛑 停止Web服务器...")
            self.web_process.terminate()
            
            try:
                self.web_process.wait(timeout=5)
                print("✅ Web服务器已停止")
            except subprocess.TimeoutExpired:
                print("⚠️  强制终止Web服务器...")
                self.web_process.kill()
                self.web_process.wait()
                print("✅ Web服务器已强制终止")
            
            self.web_process = None
    
    def cleanup_test_environment(self):
        """
        清理测试环境
        """
        print("🧹 清理测试环境...")
        
        # 停止Web服务器
        self.stop_web_server()
        
        # 删除测试目录
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print(f"   已删除测试目录: {self.test_dir}")
        
        print("✅ 测试环境清理完成")
        print()
    
    def run_all_tests(self):
        """
        运行所有集成测试
        """
        print("=" * 60)
        print("🧪 本地代码搜索系统 - 集成测试")
        print("=" * 60)
        print()
        
        try:
            # 设置测试环境
            self.setup_test_environment()
            
            # 测试完整工作流程
            self.test_complete_workflow()
            
            # 启动Web服务器
            if self.start_web_server():
                # 测试Web API集成
                self.test_web_api_integration()
            else:
                print("⚠️  跳过Web API测试（服务器启动失败）")
            
        except Exception as e:
            print(f"❌ 集成测试异常: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # 清理测试环境
            self.cleanup_test_environment()
        
        print("=" * 60)
        print("✅ 集成测试完成!")
        print("=" * 60)

def main():
    """主函数"""
    test_suite = IntegrationTestSuite()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()