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