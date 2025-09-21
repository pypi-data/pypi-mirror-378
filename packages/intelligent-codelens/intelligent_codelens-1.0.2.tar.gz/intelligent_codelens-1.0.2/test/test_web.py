#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web界面和API接口测试脚本
测试本地代码搜索系统的Web服务功能
"""

import requests
import json
import time
import os
import tempfile
import shutil
from pathlib import Path

# 测试配置
BASE_URL = "http://localhost:5001"
TEST_TIMEOUT = 10  # 请求超时时间（秒）

def test_server_status():
    """测试服务器状态"""
    print("🌐 测试服务器状态...")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TEST_TIMEOUT)
        
        if response.status_code == 200:
            print("✅ 服务器运行正常")
            print(f"   - 状态码: {response.status_code}")
            print(f"   - 响应时间: {response.elapsed.total_seconds():.3f}s")
            
            # 检查响应内容
            if "本地代码搜索系统" in response.text:
                print("✅ 主页内容正确")
            else:
                print("❌ 主页内容异常")
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保Web服务已启动")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 服务器状态测试异常: {e}")
    
    print()

def test_search_api():
    """测试搜索API接口"""
    print("🔍 测试搜索API接口...")
    
    # 测试查询列表
    test_queries = [
        ("计算总和", "中文查询"),
        ("sum calculation", "英文查询"),
        ("function", "通用关键词"),
        ("class", "类相关查询"),
        ("", "空查询"),
        ("非常长的查询字符串" * 10, "超长查询")
    ]
    
    for query, description in test_queries:
        try:
            # 测试GET请求
            params = {"q": query, "limit": 5}
            response = requests.get(f"{BASE_URL}/search", params=params, timeout=TEST_TIMEOUT)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    results = data.get('results', [])
                    total = data.get('total', 0)
                    
                    print(f"✅ 搜索API ({description}): {len(results)} 个结果 (总计: {total})")
                    print(f"   查询: '{query[:30]}{'...' if len(query) > 30 else ''}'")
                    print(f"   响应时间: {response.elapsed.total_seconds():.3f}s")
                    
                    # 检查结果格式
                    if results:
                        first_result = results[0]
                        required_fields = ['name', 'file_path', 'type', 'relevance_score']
                        missing_fields = [field for field in required_fields if field not in first_result]
                        
                        if not missing_fields:
                            print("✅ 结果格式正确")
                        else:
                            print(f"❌ 结果缺少字段: {missing_fields}")
                    
                except json.JSONDecodeError:
                    print(f"❌ 搜索API ({description}): JSON解析失败")
                    
            else:
                print(f"❌ 搜索API ({description}): 状态码 {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"❌ 搜索API ({description}): 请求超时")
        except Exception as e:
            print(f"❌ 搜索API ({description}): {e}")
    
    print()

def test_index_api():
    """测试索引API接口"""
    print("📚 测试索引API接口...")
    
    # 创建临时测试目录
    test_dir = tempfile.mkdtemp(prefix="test_index_")
    
    try:
        # 创建测试文件
        test_files = {
            "test_math.py": '''
def add_numbers(a, b):
    """计算两个数的和"""
    return a + b

def multiply_numbers(a, b):
    """计算两个数的乘积"""
    return a * b
''',
            "test_string.py": '''
def reverse_string(text):
    """反转字符串"""
    return text[::-1]

class StringProcessor:
    """字符串处理器"""
    
    def __init__(self):
        self.processed_count = 0
    
    def process(self, text):
        """处理文本"""
        self.processed_count += 1
        return text.upper()
'''
        }
        
        for filename, content in test_files.items():
            file_path = os.path.join(test_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # 测试索引API
        try:
            data = {"path": test_dir}
            response = requests.post(f"{BASE_URL}/index", json=data, timeout=30)  # 索引可能需要更长时间
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    success = result.get('success', False)
                    message = result.get('message', '')
                    stats = result.get('stats', {})
                    
                    if success:
                        print("✅ 索引API调用成功")
                        print(f"   消息: {message}")
                        if stats:
                            print(f"   统计: {stats}")
                    else:
                        print(f"❌ 索引API调用失败: {message}")
                        
                except json.JSONDecodeError:
                    print("❌ 索引API: JSON解析失败")
                    
            else:
                print(f"❌ 索引API: 状态码 {response.status_code}")
                if response.text:
                    print(f"   错误信息: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print("❌ 索引API: 请求超时")
        except Exception as e:
            print(f"❌ 索引API异常: {e}")
        
        # 等待索引完成后测试搜索
        print("   等待索引完成...")
        time.sleep(2)
        
        # 测试新索引的内容是否可搜索
        test_search_queries = ["add_numbers", "StringProcessor", "反转字符串"]
        
        for query in test_search_queries:
            try:
                params = {"q": query, "limit": 3}
                response = requests.get(f"{BASE_URL}/search", params=params, timeout=TEST_TIMEOUT)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    if results:
                        print(f"✅ 索引后搜索 '{query}': 找到 {len(results)} 个结果")
                    else:
                        print(f"⚠️  索引后搜索 '{query}': 未找到结果")
                        
            except Exception as e:
                print(f"❌ 索引后搜索异常: {e}")
    
    finally:
        # 清理测试目录
        shutil.rmtree(test_dir)
    
    print()

def test_stats_api():
    """测试统计API接口"""
    print("📊 测试统计API接口...")
    
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=TEST_TIMEOUT)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # 检查必要的统计字段
                expected_fields = ['total_files', 'total_functions', 'total_classes', 'languages']
                missing_fields = [field for field in expected_fields if field not in data]
                
                if not missing_fields:
                    print("✅ 统计API调用成功")
                    print(f"   文件总数: {data.get('total_files', 0)}")
                    print(f"   函数总数: {data.get('total_functions', 0)}")
                    print(f"   类总数: {data.get('total_classes', 0)}")
                    print(f"   支持语言: {', '.join(data.get('languages', []))}")
                else:
                    print(f"❌ 统计API缺少字段: {missing_fields}")
                    
            except json.JSONDecodeError:
                print("❌ 统计API: JSON解析失败")
                
        else:
            print(f"❌ 统计API: 状态码 {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ 统计API: 请求超时")
    except Exception as e:
        print(f"❌ 统计API异常: {e}")
    
    print()

def test_web_interface():
    """测试Web界面功能"""
    print("🖥️  测试Web界面功能...")
    
    try:
        # 测试主页
        response = requests.get(f"{BASE_URL}/", timeout=TEST_TIMEOUT)
        
        if response.status_code == 200:
            content = response.text
            
            # 检查关键元素
            checks = [
                ("搜索框", 'input' in content and 'search' in content.lower()),
                ("搜索按钮", 'button' in content or 'submit' in content),
                ("页面标题", '本地代码搜索' in content or 'Code Search' in content),
                ("CSS样式", '<style>' in content or '.css' in content),
                ("JavaScript", '<script>' in content or '.js' in content)
            ]
            
            for check_name, check_result in checks:
                if check_result:
                    print(f"✅ {check_name}: 存在")
                else:
                    print(f"❌ {check_name}: 缺失")
            
            # 检查响应头
            content_type = response.headers.get('content-type', '')
            if 'text/html' in content_type:
                print("✅ 内容类型正确: HTML")
            else:
                print(f"⚠️  内容类型: {content_type}")
                
        else:
            print(f"❌ Web界面: 状态码 {response.status_code}")
            
    except Exception as e:
        print(f"❌ Web界面测试异常: {e}")
    
    print()

def test_error_handling():
    """测试错误处理"""
    print("⚠️  测试错误处理...")
    
    error_tests = [
        ("/nonexistent", "不存在的路径"),
        ("/search?q=" + "x" * 1000, "超长查询"),
        ("/index", "POST请求缺少数据"),
        ("/search?limit=abc", "无效参数类型")
    ]
    
    for endpoint, description in error_tests:
        try:
            if endpoint == "/index":
                response = requests.post(f"{BASE_URL}{endpoint}", timeout=TEST_TIMEOUT)
            else:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=TEST_TIMEOUT)
            
            if response.status_code in [400, 404, 422, 500]:
                print(f"✅ 错误处理 ({description}): 状态码 {response.status_code}")
            else:
                print(f"⚠️  错误处理 ({description}): 状态码 {response.status_code}")
                
        except Exception as e:
            print(f"❌ 错误处理测试异常 ({description}): {e}")
    
    print()

def test_performance():
    """测试性能"""
    print("⚡ 测试Web服务性能...")
    
    # 并发搜索测试
    import threading
    import queue
    
    def search_worker(query_queue, result_queue):
        """搜索工作线程"""
        while True:
            try:
                query = query_queue.get(timeout=1)
                start_time = time.time()
                
                response = requests.get(f"{BASE_URL}/search", 
                                      params={"q": query, "limit": 5}, 
                                      timeout=TEST_TIMEOUT)
                
                end_time = time.time()
                result_queue.put({
                    'query': query,
                    'status_code': response.status_code,
                    'response_time': end_time - start_time,
                    'success': response.status_code == 200
                })
                
                query_queue.task_done()
                
            except queue.Empty:
                break
            except Exception as e:
                result_queue.put({
                    'query': query,
                    'error': str(e),
                    'success': False
                })
                query_queue.task_done()
    
    try:
        # 准备测试查询
        test_queries = ["function", "class", "import", "def", "return"] * 4  # 20个查询
        
        query_queue = queue.Queue()
        result_queue = queue.Queue()
        
        for query in test_queries:
            query_queue.put(query)
        
        # 启动5个工作线程
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=search_worker, args=(query_queue, result_queue))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # 等待所有任务完成
        query_queue.join()
        
        # 收集结果
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
        
        # 分析结果
        successful_requests = [r for r in results if r.get('success', False)]
        failed_requests = [r for r in results if not r.get('success', False)]
        
        if successful_requests:
            avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests)
            max_response_time = max(r['response_time'] for r in successful_requests)
            min_response_time = min(r['response_time'] for r in successful_requests)
            
            print(f"✅ 并发性能测试完成:")
            print(f"   成功请求: {len(successful_requests)}/{len(results)}")
            print(f"   平均响应时间: {avg_response_time:.3f}s")
            print(f"   最大响应时间: {max_response_time:.3f}s")
            print(f"   最小响应时间: {min_response_time:.3f}s")
        
        if failed_requests:
            print(f"❌ 失败请求: {len(failed_requests)}")
            for failed in failed_requests[:3]:  # 只显示前3个错误
                error = failed.get('error', '未知错误')
                print(f"   错误: {error}")
    
    except Exception as e:
        print(f"❌ 性能测试异常: {e}")
    
    print()

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 本地代码搜索系统 - Web界面和API测试")
    print("=" * 60)
    print()
    
    # 执行所有测试
    test_server_status()
    test_search_api()
    test_index_api()
    test_stats_api()
    test_web_interface()
    test_error_handling()
    test_performance()
    
    print("=" * 60)
    print("✅ Web界面和API测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()