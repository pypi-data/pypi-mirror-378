#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面集成测试
测试代码搜索系统的所有功能
"""

import unittest
import os
import tempfile
import shutil
import json
import requests
import time
from pathlib import Path

from database import CodeDatabase
from semantic_search import SemanticSearchEngine
from indexer import CodeIndexer
from web import CodeSearchWebApp


class TestCodeSearchSystem(unittest.TestCase):
    """代码搜索系统集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        # 创建临时目录
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_db_path = os.path.join(cls.temp_dir, "test_search.db")
        cls.test_repo_path = os.path.join(cls.temp_dir, "test_repo")
        cls.test_config_path = os.path.join(cls.temp_dir, "test_config.yaml")
        
        # 创建测试配置文件
        cls._create_test_config()
        
        # 创建测试代码仓库
        cls._create_test_repository()
        
        # 初始化数据库和索引（使用测试配置）
        cls.db = CodeDatabase(cls.test_db_path)
        cls.indexer = CodeIndexer(config_path=cls.test_config_path)
        cls.search_engine = SemanticSearchEngine(config_path=cls.test_config_path)
        
        # 索引测试代码
        cls.indexer.index_repository(cls.test_repo_path)
        
        print(f"测试环境初始化完成:")
        print(f"  临时目录: {cls.temp_dir}")
        print(f"  测试数据库: {cls.test_db_path}")
        print(f"  测试仓库: {cls.test_repo_path}")
        print(f"  测试配置: {cls.test_config_path}")
    
    @classmethod
    def _create_test_config(cls):
        """创建测试配置文件"""
        config_content = """
batch_size: 100
db_file: {}
debug: true
exclude_dirs:
  - node_modules
  - .git
  - dist
  - build
  - __pycache__
  - .venv
  - venv
file_extensions:
  python:
    - .py
  javascript:
    - .js
    - .jsx
    - .ts
    - .tsx
  java:
    - .java
languages:
  - python
  - javascript
  - java
max_file_size: 1048576
max_results: 10
similarity_threshold: 0.6
spacy_model: en_core_web_sm
store_raw_code: true
web_host: localhost
web_port: 5000
""".format(cls.test_db_path)
        with open(cls.test_config_path, 'w', encoding='utf-8') as f:
            f.write(config_content.strip())
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        # 清理临时文件
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)
        print("测试环境清理完成")
    
    @classmethod
    def _create_test_repository(cls):
        """创建测试代码仓库"""
        os.makedirs(cls.test_repo_path, exist_ok=True)
        
        # 创建Python测试文件
        test_files = {
            "user_service.py": '''
class UserService:
    """用户服务类，处理用户相关业务逻辑"""
    
    def __init__(self):
        self.users = {}
    
    def create_user(self, username, email, password):
        """创建新用户"""
        if username in self.users:
            raise ValueError("用户名已存在")
        
        user = {
            "username": username,
            "email": email,
            "password": self._hash_password(password),
            "created_at": time.time()
        }
        self.users[username] = user
        return user
    
    def authenticate_user(self, username, password):
        """用户身份验证"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        return self._verify_password(password, user["password"])
    
    def _hash_password(self, password):
        """密码哈希处理"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password, hashed):
        """验证密码"""
        return self._hash_password(password) == hashed
''',
            
            "payment_processor.py": '''
class PaymentProcessor:
    """支付处理器，处理各种支付方式"""
    
    def __init__(self):
        self.supported_methods = ["credit_card", "alipay", "wechat_pay"]
    
    def process_payment(self, amount, method, card_info=None):
        """处理支付请求"""
        if method not in self.supported_methods:
            raise ValueError(f"不支持的支付方式: {method}")
        
        if method == "credit_card":
            return self._process_credit_card(amount, card_info)
        elif method == "alipay":
            return self._process_alipay(amount)
        elif method == "wechat_pay":
            return self._process_wechat_pay(amount)
    
    def _process_credit_card(self, amount, card_info):
        """处理信用卡支付"""
        # 模拟信用卡支付处理
        if not card_info or "number" not in card_info:
            raise ValueError("信用卡信息不完整")
        
        return {
            "status": "success",
            "transaction_id": f"cc_{int(time.time())}",
            "amount": amount,
            "method": "credit_card"
        }
    
    def _process_alipay(self, amount):
        """处理支付宝支付"""
        return {
            "status": "success", 
            "transaction_id": f"alipay_{int(time.time())}",
            "amount": amount,
            "method": "alipay"
        }
    
    def _process_wechat_pay(self, amount):
        """处理微信支付"""
        return {
            "status": "success",
            "transaction_id": f"wechat_{int(time.time())}",
            "amount": amount,
            "method": "wechat_pay"
        }

def calculate_fee(amount, method):
    """计算手续费"""
    fee_rates = {
        "credit_card": 0.03,
        "alipay": 0.006,
        "wechat_pay": 0.006
    }
    return amount * fee_rates.get(method, 0)
''',
            
            "order_manager.py": '''
import json
from datetime import datetime

class OrderManager:
    """订单管理器，处理订单相关操作"""
    
    def __init__(self):
        self.orders = {}
        self.order_counter = 1000
    
    def create_order(self, user_id, items, shipping_address):
        """创建新订单"""
        order_id = self._generate_order_id()
        
        order = {
            "id": order_id,
            "user_id": user_id,
            "items": items,
            "shipping_address": shipping_address,
            "status": "pending",
            "total_amount": self._calculate_total(items),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.orders[order_id] = order
        return order
    
    def update_order_status(self, order_id, new_status):
        """更新订单状态"""
        if order_id not in self.orders:
            raise ValueError(f"订单不存在: {order_id}")
        
        valid_statuses = ["pending", "paid", "shipped", "delivered", "cancelled"]
        if new_status not in valid_statuses:
            raise ValueError(f"无效的订单状态: {new_status}")
        
        self.orders[order_id]["status"] = new_status
        self.orders[order_id]["updated_at"] = datetime.now().isoformat()
        
        return self.orders[order_id]
    
    def get_order(self, order_id):
        """获取订单信息"""
        return self.orders.get(order_id)
    
    def get_user_orders(self, user_id):
        """获取用户的所有订单"""
        return [order for order in self.orders.values() 
                if order["user_id"] == user_id]
    
    def _generate_order_id(self):
        """生成订单ID"""
        self.order_counter += 1
        return f"ORD{self.order_counter}"
    
    def _calculate_total(self, items):
        """计算订单总金额"""
        total = 0
        for item in items:
            total += item.get("price", 0) * item.get("quantity", 1)
        return total

def format_order_summary(order):
    """格式化订单摘要"""
    return f"订单 {order['id']}: {order['status']} - ¥{order['total_amount']}"
'''
        }
        
        # 写入测试文件
        for filename, content in test_files.items():
            file_path = os.path.join(cls.test_repo_path, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def test_database_operations(self):
        """测试数据库基本操作"""
        print("\n=== 测试数据库操作 ===")
        
        # 测试统计信息
        stats = self.db.get_stats()
        print(f"数据库统计: {stats}")
        
        self.assertGreater(stats['files'], 0, "应该有文件被索引")
        self.assertGreater(stats['functions'], 0, "应该有函数被索引")
        self.assertGreater(stats['classes'], 0, "应该有类被索引")
        
        # 测试搜索历史
        self.db.add_search_history("测试查询", 5, 0.123)
        history = self.db.get_search_history(limit=1)
        self.assertEqual(len(history), 1, "应该有一条搜索历史")
        self.assertEqual(history[0]['query'], "测试查询", "搜索历史查询应该匹配")
    
    def test_semantic_search(self):
        """测试语义搜索功能"""
        print("\n=== 测试语义搜索 ===")
        
        # 测试中文搜索
        test_cases = [
            ("用户", "应该找到用户相关的函数和类"),
            ("支付", "应该找到支付相关的函数"),
            ("订单", "应该找到订单相关的函数和类"),
            ("密码", "应该找到密码相关的函数"),
            ("authentication", "应该找到身份验证相关的函数"),
            ("payment", "应该找到支付相关的函数")
        ]
        
        for query, description in test_cases:
            print(f"\n搜索: '{query}' - {description}")
            results = self.search_engine.search(query, limit=5)
            
            print(f"  找到 {len(results)} 个结果:")
            for i, result in enumerate(results):
                print(f"    {i+1}. {result['type']}: {result['name']} "
                      f"(相似度: {result['similarity']:.3f})")
            
            # 验证搜索结果
            if query in ["用户", "authentication"]:
                # 应该找到用户相关的结果
                user_results = [r for r in results if "user" in r['name'].lower() 
                               or "用户" in (r.get('docstring', '') or '')]
                self.assertGreater(len(user_results), 0, 
                                 f"搜索'{query}'应该找到用户相关结果")
            
            elif query in ["支付", "payment"]:
                # 应该找到支付相关的结果
                payment_results = [r for r in results if "payment" in r['name'].lower() 
                                  or "支付" in (r.get('docstring', '') or '')]
                self.assertGreater(len(payment_results), 0, 
                                 f"搜索'{query}'应该找到支付相关结果")
    
    def test_indexer_functionality(self):
        """测试索引器功能"""
        print("\n=== 测试索引器功能 ===")
        
        # 创建新的测试文件
        new_file_path = os.path.join(self.test_repo_path, "new_service.py")
        new_content = '''
class NewService:
    """新服务类"""
    
    def new_method(self):
        """新方法"""
        pass
'''
        
        with open(new_file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # 获取索引前的统计
        stats_before = self.db.get_stats()
        
        # 重新索引
        self.indexer.index_repository(self.test_repo_path)
        
        # 获取索引后的统计
        stats_after = self.db.get_stats()
        
        print(f"索引前: {stats_before}")
        print(f"索引后: {stats_after}")
        
        # 验证新文件被索引
        self.assertGreaterEqual(stats_after['files'], stats_before['files'], 
                               "文件数应该增加或保持不变")
        self.assertGreaterEqual(stats_after['functions'], stats_before['functions'], 
                               "函数数应该增加或保持不变")
        self.assertGreaterEqual(stats_after['classes'], stats_before['classes'], 
                               "类数应该增加或保持不变")
        
        # 搜索新添加的内容
        results = self.search_engine.search("NewService", limit=5)
        new_service_found = any(r['name'] == 'NewService' for r in results)
        self.assertTrue(new_service_found, "应该能搜索到新添加的类")
        
        # 清理测试文件
        os.remove(new_file_path)


class TestWebAPI(unittest.TestCase):
    """Web API测试"""
    
    @classmethod
    def setUpClass(cls):
        """启动Web服务器进行测试"""
        # 使用现有的数据库进行测试
        cls.base_url = "http://localhost:5001"
        
        # 配置requests会话，绕过代理
        cls.session = requests.Session()
        cls.session.trust_env = False  # 忽略环境变量中的代理设置
        
        # 等待服务器启动
        max_retries = 10
        for i in range(max_retries):
            try:
                response = cls.session.get(f"{cls.base_url}/api/stats", timeout=2)
                if response.status_code == 200:
                    print("Web服务器已就绪")
                    break
            except requests.exceptions.RequestException as e:
                print(f"连接尝试 {i+1}/{max_retries} 失败: {e}")
                if i == max_retries - 1:
                    print("警告: 无法连接到Web服务器，跳过API测试")
                    cls.skip_api_tests = True
                    return
                time.sleep(1)
        
        cls.skip_api_tests = False
    
    def test_stats_api(self):
        """测试统计信息API"""
        if self.skip_api_tests:
            self.skipTest("Web服务器不可用，跳过API测试")
            
        print("\n=== 测试统计信息API ===")
        
        response = self.session.get(f"{self.base_url}/api/stats")
        self.assertEqual(response.status_code, 200, "统计API应该返回200")
        
        data = response.json()
        print(f"统计信息: {data}")
        
        # 验证返回的数据结构
        required_fields = ['files', 'functions', 'classes', 'db_size_mb']
        for field in required_fields:
            self.assertIn(field, data, f"统计信息应该包含{field}字段")
            self.assertIsInstance(data[field], (int, float), 
                                f"{field}应该是数字类型")
    
    def test_search_api(self):
        """测试搜索API"""
        if self.skip_api_tests:
            self.skipTest("Web服务器不可用，跳过API测试")
            
        print("\n=== 测试搜索API ===")
        
        # 测试不同的搜索查询
        test_queries = [
            "用户",
            "支付",
            "订单",
            "user",
            "payment",
            "order"
        ]
        
        for query in test_queries:
            print(f"\n测试搜索: '{query}'")
            
            response = self.session.post(
                f"{self.base_url}/api/search",
                json={"query": query, "limit": 5},
                headers={"Content-Type": "application/json"}
            )
            
            self.assertEqual(response.status_code, 200, 
                           f"搜索'{query}'应该返回200")
            
            data = response.json()
            print(f"  找到 {len(data.get('results', []))} 个结果")
            print(f"  搜索时间: {data.get('search_time', 0):.3f}秒")
            
            # 验证返回数据结构
            self.assertIn('results', data, "应该包含results字段")
            self.assertIn('total_count', data, "应该包含total_count字段")
            self.assertIn('search_time', data, "应该包含search_time字段")
            
            # 验证结果格式
            for result in data['results']:
                required_fields = ['type', 'name', 'similarity']
                for field in required_fields:
                    self.assertIn(field, result, f"搜索结果应该包含{field}字段")
    
    def test_search_api_error_handling(self):
        """测试搜索API错误处理"""
        if self.skip_api_tests:
            self.skipTest("Web服务器不可用，跳过API测试")
            
        print("\n=== 测试搜索API错误处理 ===")
        
        # 测试空查询
        response = self.session.post(
            f"{self.base_url}/api/search",
            json={"query": "", "limit": 5},
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 400, "空查询应该返回400错误")
        
        # 测试无效的JSON
        response = self.session.post(
            f"{self.base_url}/api/search",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 400, "无效JSON应该返回400错误")
        
        # 测试缺少查询参数
        response = self.session.post(
            f"{self.base_url}/api/search",
            json={"limit": 5},
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 400, "缺少查询参数应该返回400错误")


def run_comprehensive_tests():
    """运行全面测试"""
    print("开始运行代码搜索系统全面测试...")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加测试用例
    suite.addTest(unittest.makeSuite(TestCodeSearchSystem))
    suite.addTest(unittest.makeSuite(TestWebAPI))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要:")
    print(f"  运行测试: {result.testsRun}")
    print(f"  成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    # 返回测试是否全部通过
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)