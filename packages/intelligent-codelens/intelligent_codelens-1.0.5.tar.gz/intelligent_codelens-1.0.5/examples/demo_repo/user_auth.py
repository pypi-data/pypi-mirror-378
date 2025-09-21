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