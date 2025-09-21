#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码搜索演示脚本
展示完整的索引和搜索流程
"""

import os
import time
import yaml
from tree_parser import TreeSitterParser
from database import CodeDatabase
from indexer import CodeIndexer
from semantic_search import SemanticSearchEngine


def create_demo_repo():
    """
    创建演示代码仓库
    
    Returns:
        演示仓库路径
    """
    demo_path = "examples/demo_repo"
    os.makedirs(demo_path, exist_ok=True)
    
    # 创建示例 Python 文件
    python_files = {
        "order_service.py": '''
"""订单服务模块"""

class OrderService:
    """订单服务类"""
    
    def __init__(self, db_connection):
        """
        初始化订单服务
        
        Args:
            db_connection: 数据库连接
        """
        self.db = db_connection
    
    def create_order(self, user_id, items):
        """
        创建新订单
        
        Args:
            user_id: 用户ID
            items: 商品列表
            
        Returns:
            订单ID
        """
        order_id = self._generate_order_id()
        total_amount = self._calculate_total(items)
        
        # 插入订单记录
        self.db.execute("""
            INSERT INTO orders (id, user_id, total_amount, status)
            VALUES (?, ?, ?, 'pending')
        """, (order_id, user_id, total_amount))
        
        return order_id
    
    def update_payment_status(self, order_id, status):
        """
        更新订单支付状态
        
        Args:
            order_id: 订单ID
            status: 支付状态
        """
        self.db.execute("""
            UPDATE orders 
            SET payment_status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, order_id))
        
        if status == 'paid':
            self._send_confirmation_email(order_id)
    
    def _generate_order_id(self):
        """生成订单ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _calculate_total(self, items):
        """计算订单总金额"""
        return sum(item['price'] * item['quantity'] for item in items)
    
    def _send_confirmation_email(self, order_id):
        """发送确认邮件"""
        print(f"发送订单确认邮件: {order_id}")
''',
        
        "payment_dao.py": '''
"""支付数据访问对象"""

class PaymentDAO:
    """支付数据访问类"""
    
    def __init__(self, db_connection):
        """
        初始化支付DAO
        
        Args:
            db_connection: 数据库连接
        """
        self.db = db_connection
    
    def create_payment(self, order_id, amount, method):
        """
        创建支付记录
        
        Args:
            order_id: 订单ID
            amount: 支付金额
            method: 支付方式
            
        Returns:
            支付ID
        """
        payment_id = self._generate_payment_id()
        
        self.db.execute("""
            INSERT INTO payments (id, order_id, amount, method, status)
            VALUES (?, ?, ?, ?, 'pending')
        """, (payment_id, order_id, amount, method))
        
        return payment_id
    
    def set_status_paid(self, payment_id):
        """
        设置支付状态为已支付
        
        Args:
            payment_id: 支付ID
        """
        self.db.execute("""
            UPDATE payments 
            SET status = 'paid', paid_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (payment_id,))
        
        # 更新相关订单状态
        self._update_order_status(payment_id)
    
    def get_payment_by_order(self, order_id):
        """
        根据订单ID获取支付信息
        
        Args:
            order_id: 订单ID
            
        Returns:
            支付信息
        """
        cursor = self.db.execute("""
            SELECT * FROM payments WHERE order_id = ?
        """, (order_id,))
        
        return cursor.fetchone()
    
    def _generate_payment_id(self):
        """生成支付ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _update_order_status(self, payment_id):
        """更新订单状态"""
        # 获取订单ID
        cursor = self.db.execute("""
            SELECT order_id FROM payments WHERE id = ?
        """, (payment_id,))
        
        result = cursor.fetchone()
        if result:
            order_id = result[0]
            self.db.execute("""
                UPDATE orders SET status = 'paid' WHERE id = ?
            """, (order_id,))
''',
        
        "admin_view.py": '''
"""管理员视图模块"""

from flask import Blueprint, request, jsonify, render_template

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/orders')
def list_orders():
    """
    列出所有订单
    
    Returns:
        订单列表页面
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 获取订单列表
    orders = get_orders_paginated(page, per_page)
    
    return render_template('admin/orders.html', orders=orders)


@admin_bp.route('/orders/<order_id>/status', methods=['POST'])
def change_order_status(order_id):
    """
    修改订单状态
    
    Args:
        order_id: 订单ID
        
    Returns:
        操作结果
    """
    new_status = request.json.get('status')
    
    if new_status not in ['pending', 'paid', 'shipped', 'delivered', 'cancelled']:
        return jsonify({'error': '无效的状态'}), 400
    
    # 更新订单状态
    update_order_status(order_id, new_status)
    
    return jsonify({'success': True, 'message': '状态更新成功'})


@admin_bp.route('/payments/<payment_id>/refund', methods=['POST'])
def change_status_to_refund(payment_id):
    """
    将支付状态改为退款
    
    Args:
        payment_id: 支付ID
        
    Returns:
        操作结果
    """
    refund_amount = request.json.get('amount')
    reason = request.json.get('reason', '')
    
    # 处理退款
    result = process_refund(payment_id, refund_amount, reason)
    
    if result['success']:
        return jsonify({'success': True, 'message': '退款处理成功'})
    else:
        return jsonify({'error': result['error']}), 400


def get_orders_paginated(page, per_page):
    """
    分页获取订单
    
    Args:
        page: 页码
        per_page: 每页数量
        
    Returns:
        订单列表
    """
    # 模拟数据库查询
    return []


def update_order_status(order_id, status):
    """
    更新订单状态
    
    Args:
        order_id: 订单ID
        status: 新状态
    """
    print(f"更新订单 {order_id} 状态为 {status}")


def process_refund(payment_id, amount, reason):
    """
    处理退款
    
    Args:
        payment_id: 支付ID
        amount: 退款金额
        reason: 退款原因
        
    Returns:
        处理结果
    """
    print(f"处理退款: {payment_id}, 金额: {amount}, 原因: {reason}")
    return {'success': True}
''',
        
        "user_auth.py": '''
"""用户认证模块"""

import hashlib
import jwt
from datetime import datetime, timedelta


class UserAuth:
    """用户认证类"""
    
    def __init__(self, secret_key):
        """
        初始化用户认证
        
        Args:
            secret_key: JWT密钥
        """
        self.secret_key = secret_key
    
    def hash_password(self, password):
        """
        密码哈希
        
        Args:
            password: 原始密码
            
        Returns:
            哈希后的密码
        """
        salt = "your_salt_here"
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def verify_password(self, password, hashed_password):
        """
        验证密码
        
        Args:
            password: 原始密码
            hashed_password: 哈希密码
            
        Returns:
            是否匹配
        """
        return self.hash_password(password) == hashed_password
    
    def generate_token(self, user_id, username):
        """
        生成JWT令牌
        
        Args:
            user_id: 用户ID
            username: 用户名
            
        Returns:
            JWT令牌
        """
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token):
        """
        验证JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            用户信息或None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return {
                'user_id': payload['user_id'],
                'username': payload['username']
            }
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def login_user(self, username, password, db_connection):
        """
        用户登录验证
        
        Args:
            username: 用户名
            password: 密码
            db_connection: 数据库连接
            
        Returns:
            登录结果
        """
        # 查询用户
        cursor = db_connection.execute("""
            SELECT id, username, password_hash, is_active
            FROM users WHERE username = ?
        """, (username,))
        
        user = cursor.fetchone()
        
        if not user:
            return {'success': False, 'error': '用户不存在'}
        
        if not user[3]:  # is_active
            return {'success': False, 'error': '账户已被禁用'}
        
        if not self.verify_password(password, user[2]):
            return {'success': False, 'error': '密码错误'}
        
        # 生成令牌
        token = self.generate_token(user[0], user[1])
        
        return {
            'success': True,
            'token': token,
            'user': {
                'id': user[0],
                'username': user[1]
            }
        }
'''
    }
    
    # 写入文件
    for filename, content in python_files.items():
        file_path = os.path.join(demo_path, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
    
    return demo_path


def run_demo():
    """
    运行完整演示
    """
    print("🚀 开始代码搜索演示")
    print("=" * 50)
    
    # 1. 创建演示仓库
    print("📁 创建演示代码仓库...")
    demo_path = create_demo_repo()
    print(f"✅ 演示仓库创建完成: {demo_path}")
    
    # 2. 更新配置文件
    print("\n⚙️ 更新配置文件...")
    config_path = "config.yaml"
    
    # 读取现有配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 更新仓库路径
    config['repo_path'] = os.path.abspath(demo_path)
    
    # 写回配置文件
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✅ 配置文件已更新，仓库路径: {config['repo_path']}")
    
    # 3. 创建索引
    print("\n🔍 开始索引代码...")
    start_time = time.time()
    
    indexer = CodeIndexer(config_path)
    stats = indexer.index_repository()
    
    index_time = time.time() - start_time
    
    print(f"✅ 索引完成，耗时: {index_time:.2f} 秒")
    print(f"📊 统计信息:")
    print(f"   - 文件数: {stats['files']}")
    print(f"   - 函数数: {stats['functions']}")
    print(f"   - 类数: {stats['classes']}")
    print(f"   - 数据库大小: {stats['db_size_mb']:.1f} MB")
    
    # 4. 演示搜索
    print("\n🔍 演示语义搜索...")
    search_engine = SemanticSearchEngine(config_path)
    
    # 测试查询
    test_queries = [
        "支付状态更新",
        "用户登录验证",
        "订单状态修改",
        "密码哈希函数",
        "退款处理"
    ]
    
    for query in test_queries:
        print(f"\n🔎 查询: '{query}'")
        
        start_time = time.time()
        results = search_engine.search(query, limit=3)
        search_time = time.time() - start_time
        
        print(f"⏱️ 搜索耗时: {search_time:.3f} 秒")
        
        if results:
            print("📋 搜索结果:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['file_path']}:{result['start_line']}  {result['name']}")
                print(f"      类型: {result['type']}, 相关性: {result['relevance_score']:.2f}")
                if result.get('docstring'):
                    print(f"      描述: {result['docstring'][:100]}...")
        else:
            print("❌ 未找到相关结果")
    
    print("\n🎉 演示完成！")
    print("=" * 50)
    print("💡 接下来你可以:")
    print("   1. 运行 'python web.py' 启动Web界面")
    print("   2. 访问 http://localhost:5000 进行搜索")
    print("   3. 修改 config.yaml 中的 repo_path 指向你的项目")
    print("   4. 运行 'python indexer.py' 重新索引")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="代码搜索演示")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--query", help="直接执行搜索查询")
    
    args = parser.parse_args()
    
    if args.query:
        # 直接搜索模式
        print(f"🔍 搜索: '{args.query}'")
        
        search_engine = SemanticSearchEngine(args.config)
        start_time = time.time()
        results = search_engine.search(args.query, limit=10)
        search_time = time.time() - start_time
        
        print(f"⏱️ 搜索耗时: {search_time:.3f} 秒")
        print(f"📊 找到 {len(results)} 个结果")
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['name']} ({result['type']})")
            print(f"   📁 {result['file_path']}:{result['start_line']}-{result['end_line']}")
            print(f"   🎯 相关性: {result['relevance_score']:.2f}")
            if result.get('docstring'):
                print(f"   📝 {result['docstring'][:150]}...")
    else:
        # 完整演示模式
        run_demo()


if __name__ == "__main__":
    main()