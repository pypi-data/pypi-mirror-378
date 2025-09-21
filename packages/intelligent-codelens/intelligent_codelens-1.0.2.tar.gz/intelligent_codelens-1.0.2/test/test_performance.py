#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能和边界情况测试脚本
测试本地代码搜索系统的性能表现和边界情况处理
"""

import os
import time
import tempfile
import shutil
import threading
import random
import string
from pathlib import Path
from database import CodeDatabase
from indexer import CodeIndexer
from semantic_search import SemanticSearchEngine
from tree_parser import TreeSitterParser

def create_large_test_repository():
    """
    创建大型测试代码仓库
    
    Returns:
        str: 测试目录路径
    """
    test_dir = tempfile.mkdtemp(prefix="large_test_repo_")
    
    # 创建多种语言的测试文件
    languages = {
        'python': '.py',
        'javascript': '.js',
        'java': '.java'
    }
    
    # 生成大量测试文件
    for lang, ext in languages.items():
        lang_dir = os.path.join(test_dir, lang)
        os.makedirs(lang_dir, exist_ok=True)
        
        # 每种语言创建50个文件
        for i in range(50):
            file_path = os.path.join(lang_dir, f"module_{i}{ext}")
            
            if lang == 'python':
                content = generate_python_code(i)
            elif lang == 'javascript':
                content = generate_javascript_code(i)
            elif lang == 'java':
                content = generate_java_code(i)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    return test_dir

def generate_python_code(index):
    """
    生成Python测试代码
    
    Args:
        index: 文件索引
        
    Returns:
        str: 生成的代码内容
    """
    return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块 {index} - 测试用Python代码
包含各种函数和类的定义
"""

import os
import sys
import json
from typing import List, Dict, Optional

class DataProcessor{index}:
    """数据处理器类 {index}"""
    
    def __init__(self, config: Dict = None):
        """
        初始化数据处理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {{}}
        self.processed_count = 0
        self.error_count = 0
    
    def process_data(self, data: List[Dict]) -> List[Dict]:
        """
        处理数据列表
        
        Args:
            data: 输入数据列表
            
        Returns:
            处理后的数据列表
        """
        results = []
        
        for item in data:
            try:
                processed_item = self._process_single_item(item)
                results.append(processed_item)
                self.processed_count += 1
            except Exception as e:
                self.error_count += 1
                print(f"处理错误: {{e}}")
        
        return results
    
    def _process_single_item(self, item: Dict) -> Dict:
        """
        处理单个数据项
        
        Args:
            item: 数据项
            
        Returns:
            处理后的数据项
        """
        # 模拟数据处理逻辑
        processed = item.copy()
        processed['processed'] = True
        processed['timestamp'] = time.time()
        processed['processor_id'] = {index}
        
        return processed
    
    def get_statistics(self) -> Dict:
        """
        获取处理统计信息
        
        Returns:
            统计信息字典
        """
        return {{
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'success_rate': self.processed_count / (self.processed_count + self.error_count) if (self.processed_count + self.error_count) > 0 else 0
        }}

def calculate_sum_{index}(numbers: List[float]) -> float:
    """
    计算数字列表的总和
    
    Args:
        numbers: 数字列表
        
    Returns:
        总和
    """
    return sum(numbers)

def find_max_{index}(numbers: List[float]) -> float:
    """
    找到数字列表中的最大值
    
    Args:
        numbers: 数字列表
        
    Returns:
        最大值
    """
    return max(numbers) if numbers else 0

def filter_data_{index}(data: List[Dict], condition: str) -> List[Dict]:
    """
    根据条件过滤数据
    
    Args:
        data: 数据列表
        condition: 过滤条件
        
    Returns:
        过滤后的数据列表
    """
    # 简单的过滤逻辑
    return [item for item in data if condition in str(item)]

if __name__ == "__main__":
    # 测试代码
    processor = DataProcessor{index}()
    test_data = [
        {{"id": 1, "name": "test1", "value": 100}},
        {{"id": 2, "name": "test2", "value": 200}},
        {{"id": 3, "name": "test3", "value": 300}}
    ]
    
    results = processor.process_data(test_data)
    stats = processor.get_statistics()
    
    print(f"处理结果: {{len(results)}} 项")
    print(f"统计信息: {{stats}}")
'''

def generate_javascript_code(index):
    """
    生成JavaScript测试代码
    
    Args:
        index: 文件索引
        
    Returns:
        str: 生成的代码内容
    """
    return f'''/**
 * 模块 {index} - 测试用JavaScript代码
 * 包含各种函数和类的定义
 */

const fs = require('fs');
const path = require('path');

/**
 * 数据管理器类 {index}
 */
class DataManager{index} {{
    /**
     * 构造函数
     * @param {{Object}} config - 配置对象
     */
    constructor(config = {{}}) {{
        this.config = config;
        this.data = [];
        this.listeners = [];
    }}
    
    /**
     * 添加数据
     * @param {{Object}} item - 数据项
     * @returns {{boolean}} 是否添加成功
     */
    addData(item) {{
        try {{
            this.data.push({{
                ...item,
                id: this.generateId(),
                timestamp: Date.now(),
                managerId: {index}
            }});
            
            this.notifyListeners('add', item);
            return true;
        }} catch (error) {{
            console.error('添加数据失败:', error);
            return false;
        }}
    }}
    
    /**
     * 获取数据
     * @param {{string}} id - 数据ID
     * @returns {{Object|null}} 数据项或null
     */
    getData(id) {{
        return this.data.find(item => item.id === id) || null;
    }}
    
    /**
     * 更新数据
     * @param {{string}} id - 数据ID
     * @param {{Object}} updates - 更新内容
     * @returns {{boolean}} 是否更新成功
     */
    updateData(id, updates) {{
        const index = this.data.findIndex(item => item.id === id);
        
        if (index !== -1) {{
            this.data[index] = {{ ...this.data[index], ...updates }};
            this.notifyListeners('update', this.data[index]);
            return true;
        }}
        
        return false;
    }}
    
    /**
     * 删除数据
     * @param {{string}} id - 数据ID
     * @returns {{boolean}} 是否删除成功
     */
    deleteData(id) {{
        const index = this.data.findIndex(item => item.id === id);
        
        if (index !== -1) {{
            const deleted = this.data.splice(index, 1)[0];
            this.notifyListeners('delete', deleted);
            return true;
        }}
        
        return false;
    }}
    
    /**
     * 生成唯一ID
     * @returns {{string}} 唯一ID
     */
    generateId() {{
        return `${{Date.now()}}-${{Math.random().toString(36).substr(2, 9)}}`;
    }}
    
    /**
     * 通知监听器
     * @param {{string}} event - 事件类型
     * @param {{Object}} data - 事件数据
     */
    notifyListeners(event, data) {{
        this.listeners.forEach(listener => {{
            try {{
                listener(event, data);
            }} catch (error) {{
                console.error('监听器执行错误:', error);
            }}
        }});
    }}
    
    /**
     * 添加监听器
     * @param {{Function}} listener - 监听器函数
     */
    addListener(listener) {{
        this.listeners.push(listener);
    }}
    
    /**
     * 获取统计信息
     * @returns {{Object}} 统计信息
     */
    getStatistics() {{
        return {{
            totalItems: this.data.length,
            listeners: this.listeners.length,
            managerId: {index}
        }};
    }}
}}

/**
 * 计算数组平均值
 * @param {{number[]}} numbers - 数字数组
 * @returns {{number}} 平均值
 */
function calculateAverage{index}(numbers) {{
    if (!numbers || numbers.length === 0) {{
        return 0;
    }}
    
    const sum = numbers.reduce((acc, num) => acc + num, 0);
    return sum / numbers.length;
}}

/**
 * 格式化数据
 * @param {{Object}} data - 原始数据
 * @param {{string}} format - 格式类型
 * @returns {{string}} 格式化后的字符串
 */
function formatData{index}(data, format = 'json') {{
    switch (format.toLowerCase()) {{
        case 'json':
            return JSON.stringify(data, null, 2);
        case 'csv':
            // 简单的CSV格式化
            if (Array.isArray(data)) {{
                const headers = Object.keys(data[0] || {{}});
                const rows = data.map(item => headers.map(h => item[h] || '').join(','));
                return [headers.join(','), ...rows].join('\\n');
            }}
            return '';
        default:
            return String(data);
    }}
}}

/**
 * 验证数据
 * @param {{Object}} data - 待验证数据
 * @param {{Object}} schema - 验证模式
 * @returns {{boolean}} 是否有效
 */
function validateData{index}(data, schema) {{
    // 简单的验证逻辑
    for (const [key, type] of Object.entries(schema)) {{
        if (!(key in data) || typeof data[key] !== type) {{
            return false;
        }}
    }}
    return true;
}}

// 导出模块
module.exports = {{
    DataManager{index},
    calculateAverage{index},
    formatData{index},
    validateData{index}
}};

// 测试代码
if (require.main === module) {{
    const manager = new DataManager{index}();
    
    // 添加测试数据
    manager.addData({{ name: 'test1', value: 100 }});
    manager.addData({{ name: 'test2', value: 200 }});
    manager.addData({{ name: 'test3', value: 300 }});
    
    console.log('统计信息:', manager.getStatistics());
    console.log('平均值:', calculateAverage{index}([100, 200, 300]));
}}
'''

def generate_java_code(index):
    """
    生成Java测试代码
    
    Args:
        index: 文件索引
        
    Returns:
        str: 生成的代码内容
    """
    return f'''/**
 * 模块 {index} - 测试用Java代码
 * 包含各种类和方法的定义
 */

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * 服务管理器类 {index}
 */
public class ServiceManager{index} {{
    
    private final Map<String, Object> services;
    private final List<ServiceListener> listeners;
    private final int managerId;
    
    /**
     * 构造函数
     */
    public ServiceManager{index}() {{
        this.services = new ConcurrentHashMap<>();
        this.listeners = new ArrayList<>();
        this.managerId = {index};
    }}
    
    /**
     * 注册服务
     * @param name 服务名称
     * @param service 服务实例
     * @return 是否注册成功
     */
    public boolean registerService(String name, Object service) {{
        if (name == null || service == null) {{
            return false;
        }}
        
        try {{
            services.put(name, service);
            notifyListeners("register", name, service);
            return true;
        }} catch (Exception e) {{
            System.err.println("注册服务失败: " + e.getMessage());
            return false;
        }}
    }}
    
    /**
     * 获取服务
     * @param name 服务名称
     * @param type 服务类型
     * @return 服务实例或null
     */
    @SuppressWarnings("unchecked")
    public <T> T getService(String name, Class<T> type) {{
        Object service = services.get(name);
        
        if (service != null && type.isInstance(service)) {{
            return (T) service;
        }}
        
        return null;
    }}
    
    /**
     * 注销服务
     * @param name 服务名称
     * @return 是否注销成功
     */
    public boolean unregisterService(String name) {{
        Object service = services.remove(name);
        
        if (service != null) {{
            notifyListeners("unregister", name, service);
            return true;
        }}
        
        return false;
    }}
    
    /**
     * 获取所有服务名称
     * @return 服务名称列表
     */
    public List<String> getServiceNames() {{
        return new ArrayList<>(services.keySet());
    }}
    
    /**
     * 添加监听器
     * @param listener 监听器
     */
    public void addListener(ServiceListener listener) {{
        if (listener != null) {{
            listeners.add(listener);
        }}
    }}
    
    /**
     * 移除监听器
     * @param listener 监听器
     */
    public void removeListener(ServiceListener listener) {{
        listeners.remove(listener);
    }}
    
    /**
     * 通知监听器
     * @param event 事件类型
     * @param name 服务名称
     * @param service 服务实例
     */
    private void notifyListeners(String event, String name, Object service) {{
        for (ServiceListener listener : listeners) {{
            try {{
                listener.onServiceEvent(event, name, service);
            }} catch (Exception e) {{
                System.err.println("监听器执行错误: " + e.getMessage());
            }}
        }}
    }}
    
    /**
     * 获取统计信息
     * @return 统计信息
     */
    public Map<String, Object> getStatistics() {{
        Map<String, Object> stats = new HashMap<>();
        stats.put("serviceCount", services.size());
        stats.put("listenerCount", listeners.size());
        stats.put("managerId", managerId);
        stats.put("serviceNames", getServiceNames());
        
        return stats;
    }}
    
    /**
     * 服务监听器接口
     */
    public interface ServiceListener {{
        /**
         * 服务事件处理
         * @param event 事件类型
         * @param name 服务名称
         * @param service 服务实例
         */
        void onServiceEvent(String event, String name, Object service);
    }}
    
    /**
     * 数据处理工具类
     */
    public static class DataUtils{index} {{
        
        /**
         * 计算列表总和
         * @param numbers 数字列表
         * @return 总和
         */
        public static double calculateSum(List<Double> numbers) {{
            return numbers.stream()
                    .mapToDouble(Double::doubleValue)
                    .sum();
        }}
        
        /**
         * 计算列表平均值
         * @param numbers 数字列表
         * @return 平均值
         */
        public static double calculateAverage(List<Double> numbers) {{
            return numbers.isEmpty() ? 0.0 : calculateSum(numbers) / numbers.size();
        }}
        
        /**
         * 过滤数据
         * @param data 原始数据
         * @param predicate 过滤条件
         * @return 过滤后的数据
         */
        public static <T> List<T> filterData(List<T> data, java.util.function.Predicate<T> predicate) {{
            return data.stream()
                    .filter(predicate)
                    .collect(Collectors.toList());
        }}
        
        /**
         * 转换数据
         * @param data 原始数据
         * @param mapper 转换函数
         * @return 转换后的数据
         */
        public static <T, R> List<R> transformData(List<T> data, java.util.function.Function<T, R> mapper) {{
            return data.stream()
                    .map(mapper)
                    .collect(Collectors.toList());
        }}
    }}
    
    /**
     * 主方法 - 测试代码
     * @param args 命令行参数
     */
    public static void main(String[] args) {{
        ServiceManager{index} manager = new ServiceManager{index}();
        
        // 注册测试服务
        manager.registerService("testService1", "Service Instance 1");
        manager.registerService("testService2", "Service Instance 2");
        manager.registerService("testService3", "Service Instance 3");
        
        // 添加监听器
        manager.addListener((event, name, service) -> {{
            System.out.println("服务事件: " + event + ", 名称: " + name);
        }});
        
        // 输出统计信息
        System.out.println("统计信息: " + manager.getStatistics());
        
        // 测试数据工具
        List<Double> numbers = Arrays.asList(1.0, 2.0, 3.0, 4.0, 5.0);
        System.out.println("总和: " + DataUtils{index}.calculateSum(numbers));
        System.out.println("平均值: " + DataUtils{index}.calculateAverage(numbers));
    }}
}}
'''

def test_large_scale_indexing():
    """测试大规模索引性能"""
    print("📚 测试大规模索引性能...")
    
    test_dir = create_large_test_repository()
    db_path = tempfile.mktemp(suffix=".db")
    
    try:
        # 创建数据库和索引器
        db = CodeDatabase(db_path)
        indexer = CodeIndexer(db)
        
        # 测试索引性能
        start_time = time.time()
        
        print("   开始索引大型代码仓库...")
        indexer.index_repository(test_dir)
        
        end_time = time.time()
        indexing_time = end_time - start_time
        
        # 获取统计信息
        stats = db.get_statistics()
        
        print(f"✅ 大规模索引完成:")
        print(f"   索引时间: {indexing_time:.2f}秒")
        print(f"   文件总数: {stats.get('total_files', 0)}")
        print(f"   函数总数: {stats.get('total_functions', 0)}")
        print(f"   类总数: {stats.get('total_classes', 0)}")
        print(f"   平均每文件索引时间: {indexing_time / max(stats.get('total_files', 1), 1):.3f}秒")
        
        db.close()
        
    except Exception as e:
        print(f"❌ 大规模索引测试异常: {e}")
    
    finally:
        # 清理
        shutil.rmtree(test_dir)
        if os.path.exists(db_path):
            os.remove(db_path)
    
    print()

def test_concurrent_search():
    """测试并发搜索性能"""
    print("🔄 测试并发搜索性能...")
    
    test_dir = create_large_test_repository()
    db_path = tempfile.mktemp(suffix=".db")
    
    try:
        # 创建并填充数据库
        db = CodeDatabase(db_path)
        indexer = CodeIndexer(db)
        indexer.index_repository(test_dir)
        
        search_engine = SemanticSearchEngine()
        search_engine.db = db
        
        # 准备测试查询
        test_queries = [
            "数据处理", "calculate", "manager", "service", "function",
            "class", "method", "process", "统计", "average"
        ] * 5  # 50个查询
        
        # 并发搜索测试
        results = []
        errors = []
        
        def search_worker(queries):
            """搜索工作线程"""
            for query in queries:
                try:
                    start_time = time.time()
                    search_results = search_engine.search(query, limit=10)
                    end_time = time.time()
                    
                    results.append({
                        'query': query,
                        'results_count': len(search_results),
                        'search_time': end_time - start_time
                    })
                except Exception as e:
                    errors.append({
                        'query': query,
                        'error': str(e)
                    })
        
        # 启动多个线程
        threads = []
        queries_per_thread = len(test_queries) // 5
        
        start_time = time.time()
        
        for i in range(5):
            start_idx = i * queries_per_thread
            end_idx = start_idx + queries_per_thread if i < 4 else len(test_queries)
            thread_queries = test_queries[start_idx:end_idx]
            
            thread = threading.Thread(target=search_worker, args=(thread_queries,))
            thread.start()
            threads.append(thread)
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 分析结果
        if results:
            avg_search_time = sum(r['search_time'] for r in results) / len(results)
            max_search_time = max(r['search_time'] for r in results)
            min_search_time = min(r['search_time'] for r in results)
            total_results = sum(r['results_count'] for r in results)
            
            print(f"✅ 并发搜索测试完成:")
            print(f"   总查询数: {len(results)}")
            print(f"   总耗时: {total_time:.2f}秒")
            print(f"   平均搜索时间: {avg_search_time:.3f}秒")
            print(f"   最大搜索时间: {max_search_time:.3f}秒")
            print(f"   最小搜索时间: {min_search_time:.3f}秒")
            print(f"   总结果数: {total_results}")
            print(f"   QPS (查询/秒): {len(results) / total_time:.2f}")
        
        if errors:
            print(f"❌ 搜索错误: {len(errors)} 个")
            for error in errors[:3]:  # 只显示前3个错误
                print(f"   查询 '{error['query']}': {error['error']}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ 并发搜索测试异常: {e}")
    
    finally:
        # 清理
        shutil.rmtree(test_dir)
        if os.path.exists(db_path):
            os.remove(db_path)
    
    print()

def test_memory_usage():
    """测试内存使用情况"""
    print("💾 测试内存使用情况...")
    
    try:
        import psutil
        process = psutil.Process()
        
        # 记录初始内存使用
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"   初始内存使用: {initial_memory:.2f} MB")
        
        # 创建大型测试数据
        test_dir = create_large_test_repository()
        db_path = tempfile.mktemp(suffix=".db")
        
        # 测试索引过程中的内存使用
        db = CodeDatabase(db_path)
        indexer = CodeIndexer(db)
        
        memory_before_index = process.memory_info().rss / 1024 / 1024
        print(f"   索引前内存使用: {memory_before_index:.2f} MB")
        
        indexer.index_repository(test_dir)
        
        memory_after_index = process.memory_info().rss / 1024 / 1024
        print(f"   索引后内存使用: {memory_after_index:.2f} MB")
        print(f"   索引过程内存增长: {memory_after_index - memory_before_index:.2f} MB")
        
        # 测试搜索过程中的内存使用
        search_engine = SemanticSearchEngine()
        search_engine.db = db
        
        memory_before_search = process.memory_info().rss / 1024 / 1024
        
        # 执行多次搜索
        for i in range(100):
            search_engine.search(f"test query {i}", limit=10)
        
        memory_after_search = process.memory_info().rss / 1024 / 1024
        print(f"   搜索后内存使用: {memory_after_search:.2f} MB")
        print(f"   搜索过程内存变化: {memory_after_search - memory_before_search:.2f} MB")
        
        # 清理并检查内存释放
        db.close()
        del search_engine
        del indexer
        del db
        
        # 强制垃圾回收
        import gc
        gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024
        print(f"   清理后内存使用: {final_memory:.2f} MB")
        print(f"   总内存增长: {final_memory - initial_memory:.2f} MB")
        
        # 清理测试文件
        shutil.rmtree(test_dir)
        if os.path.exists(db_path):
            os.remove(db_path)
        
        print("✅ 内存使用测试完成")
        
    except ImportError:
        print("⚠️  psutil 未安装，跳过内存测试")
    except Exception as e:
        print(f"❌ 内存测试异常: {e}")
    
    print()

def test_edge_cases():
    """测试边界情况"""
    print("⚠️  测试边界情况...")
    
    db_path = tempfile.mktemp(suffix=".db")
    
    try:
        db = CodeDatabase(db_path)
        search_engine = SemanticSearchEngine()
        search_engine.db = db
        
        # 测试各种边界情况
        edge_cases = [
            ("", "空查询"),
            ("   ", "空白查询"),
            ("a" * 1000, "超长查询"),
            ("特殊字符!@#$%^&*()", "特殊字符查询"),
            ("中文查询测试", "中文查询"),
            ("🚀🔍📚", "表情符号查询"),
            ("SELECT * FROM files", "SQL注入尝试"),
            ("../../../etc/passwd", "路径遍历尝试"),
            ("<script>alert('xss')</script>", "XSS尝试"),
            ("null", "null值"),
            ("undefined", "undefined值"),
            ("0", "数字查询"),
            ("true", "布尔值查询"),
            ("[]", "数组符号"),
            ("{}", "对象符号")
        ]
        
        for query, description in edge_cases:
            try:
                results = search_engine.search(query, limit=5)
                print(f"✅ 边界测试 ({description}): {len(results)} 个结果")
                
                # 检查结果格式
                if results:
                    first_result = results[0]
                    if not isinstance(first_result, dict):
                        print(f"❌ 结果格式错误: {type(first_result)}")
                
            except Exception as e:
                print(f"❌ 边界测试异常 ({description}): {e}")
        
        # 测试数据库边界情况
        print("   测试数据库边界情况...")
        
        # 测试空文件数据
        try:
            empty_file_data = {
                'file_path': '/test/empty.py',
                'language': 'python',
                'content': '',
                'functions': [],
                'classes': [],
                'imports': [],
                'comments': []
            }
            db.store_file_data(empty_file_data)
            print("✅ 空文件数据存储成功")
        except Exception as e:
            print(f"❌ 空文件数据存储失败: {e}")
        
        # 测试超大文件数据
        try:
            large_content = "# " + "x" * 10000  # 10KB注释
            large_file_data = {
                'file_path': '/test/large.py',
                'language': 'python',
                'content': large_content,
                'functions': [],
                'classes': [],
                'imports': [],
                'comments': [{'text': large_content, 'line': 1}]
            }
            db.store_file_data(large_file_data)
            print("✅ 大文件数据存储成功")
        except Exception as e:
            print(f"❌ 大文件数据存储失败: {e}")
        
        # 测试特殊字符文件路径
        try:
            special_path_data = {
                'file_path': '/test/特殊文件名!@#$%^&*().py',
                'language': 'python',
                'content': 'def test(): pass',
                'functions': [{'name': 'test', 'start_line': 1, 'end_line': 1, 'parameters': [], 'docstring': '', 'body': 'pass'}],
                'classes': [],
                'imports': [],
                'comments': []
            }
            db.store_file_data(special_path_data)
            print("✅ 特殊字符路径存储成功")
        except Exception as e:
            print(f"❌ 特殊字符路径存储失败: {e}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ 边界情况测试异常: {e}")
    
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
    
    print()

def test_error_recovery():
    """测试错误恢复能力"""
    print("🔧 测试错误恢复能力...")
    
    # 测试损坏的数据库文件
    try:
        corrupted_db_path = tempfile.mktemp(suffix=".db")
        
        # 创建一个损坏的数据库文件
        with open(corrupted_db_path, 'w') as f:
            f.write("这不是一个有效的数据库文件")
        
        try:
            db = CodeDatabase(corrupted_db_path)
            print("❌ 损坏数据库检测失败")
        except Exception:
            print("✅ 损坏数据库正确检测")
        
        os.remove(corrupted_db_path)
        
    except Exception as e:
        print(f"❌ 损坏数据库测试异常: {e}")
    
    # 测试不存在的文件解析
    try:
        parser = TreeSitterParser()
        result = parser.parse_file("/nonexistent/file.py")
        
        if result is None:
            print("✅ 不存在文件正确处理")
        else:
            print("❌ 不存在文件处理异常")
            
    except Exception as e:
        print(f"✅ 不存在文件异常正确捕获: {type(e).__name__}")
    
    # 测试权限不足的文件
    try:
        # 创建一个无权限的测试文件
        no_permission_file = tempfile.mktemp(suffix=".py")
        with open(no_permission_file, 'w') as f:
            f.write("def test(): pass")
        
        # 移除读权限
        os.chmod(no_permission_file, 0o000)
        
        try:
            parser = TreeSitterParser()
            result = parser.parse_file(no_permission_file)
            
            if result is None:
                print("✅ 无权限文件正确处理")
            else:
                print("❌ 无权限文件处理异常")
                
        except Exception:
            print("✅ 无权限文件异常正确捕获")
        
        # 恢复权限并删除文件
        os.chmod(no_permission_file, 0o644)
        os.remove(no_permission_file)
        
    except Exception as e:
        print(f"❌ 权限测试异常: {e}")
    
    print()

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 本地代码搜索系统 - 性能和边界情况测试")
    print("=" * 60)
    print()
    
    # 执行所有测试
    test_large_scale_indexing()
    test_concurrent_search()
    test_memory_usage()
    test_edge_cases()
    test_error_recovery()
    
    print("=" * 60)
    print("✅ 性能和边界情况测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()