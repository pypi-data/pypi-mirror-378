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