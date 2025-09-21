#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite 数据库模块
用于存储和查询代码索引数据
"""

import sqlite3
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


class CodeDatabase:
    """代码数据库管理器"""
    
    def __init__(self, db_path: str = "search.db"):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """初始化数据库连接和表结构"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        
        # 创建表结构
        self._create_tables()
        
        # 创建索引
        self._create_indexes()
    
    def _create_tables(self):
        """创建数据库表"""
        cursor = self.conn.cursor()
        
        # 文件表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                language TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 函数表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS functions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                start_line INTEGER NOT NULL,
                end_line INTEGER NOT NULL,
                parameters TEXT,  -- JSON 格式存储参数列表
                docstring TEXT,
                body TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
            )
        ''')
        
        # 类表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                start_line INTEGER NOT NULL,
                end_line INTEGER NOT NULL,
                body TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
            )
        ''')
        
        # 导入表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS imports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                line INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
            )
        ''')
        
        # 注释表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                line INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
            )
        ''')
        
        # 搜索历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                results_count INTEGER DEFAULT 0,
                search_time REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def _create_indexes(self):
        """创建数据库索引以提高查询性能"""
        cursor = self.conn.cursor()
        
        # 文件路径索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_path ON files (file_path)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_language ON files (language)')
        
        # 函数名索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_functions_name ON functions (name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_functions_file_id ON functions (file_id)')
        
        # 类名索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_classes_name ON classes (name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_classes_file_id ON classes (file_id)')
        
        # 全文搜索索引（如果 SQLite 支持 FTS）
        try:
            cursor.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS functions_fts USING fts5(
                    name, docstring, body, content='functions', content_rowid='id'
                )
            ''')
            
            cursor.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS classes_fts USING fts5(
                    name, body, content='classes', content_rowid='id'
                )
            ''')
        except sqlite3.OperationalError:
            # FTS5 不可用，跳过全文搜索索引
            pass
        
        self.conn.commit()
    
    def add_file(self, file_path: str, content: str, language: str = None) -> int:
        """
        添加文件到数据库（简化版本，用于测试兼容性）
        
        Args:
            file_path: 文件路径
            content: 文件内容
            language: 编程语言（可选）
            
        Returns:
            文件 ID
        """
        # 检测语言
        if not language:
            language = self._detect_language_from_path(file_path)
        
        # 构造文件数据
        file_data = {
            'file_path': file_path,
            'language': language,
            'content': content,
            'functions': [],
            'classes': [],
            'imports': [],
            'comments': []
        }
        
        return self.store_file_data(file_data)
    
    def _detect_language_from_path(self, file_path: str) -> str:
        """
        从文件路径检测编程语言
        
        Args:
            file_path: 文件路径
            
        Returns:
            编程语言
        """
        ext = os.path.splitext(file_path)[1].lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby'
        }
        return language_map.get(ext, 'unknown')

    def store_file_data(self, file_data: Dict[str, Any]) -> int:
        """
        存储文件解析数据
        
        Args:
            file_data: 文件解析结果
            
        Returns:
            文件 ID
        """
        cursor = self.conn.cursor()
        
        try:
            # 插入文件记录
            cursor.execute('''
                INSERT OR REPLACE INTO files (file_path, language, content)
                VALUES (?, ?, ?)
            ''', (
                file_data['file_path'],
                file_data['language'],
                file_data['content'] if file_data.get('store_raw_code', True) else None
            ))
            
            file_id = cursor.lastrowid
            
            # 删除旧的相关数据
            self._delete_file_relations(file_id)
            
            # 插入函数数据
            for func in file_data.get('functions', []):
                cursor.execute('''
                    INSERT INTO functions (file_id, name, start_line, end_line, parameters, docstring, body)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file_id,
                    func['name'],
                    func['start_line'],
                    func['end_line'],
                    json.dumps(func.get('parameters', [])),
                    func.get('docstring'),
                    func.get('body')
                ))
            
            # 插入类数据
            for cls in file_data.get('classes', []):
                cursor.execute('''
                    INSERT INTO classes (file_id, name, start_line, end_line, body)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    file_id,
                    cls['name'],
                    cls['start_line'],
                    cls['end_line'],
                    cls.get('body')
                ))
            
            # 插入导入数据
            for imp in file_data.get('imports', []):
                cursor.execute('''
                    INSERT INTO imports (file_id, text, line)
                    VALUES (?, ?, ?)
                ''', (
                    file_id,
                    imp['text'],
                    imp['line']
                ))
            
            # 插入注释数据
            for comment in file_data.get('comments', []):
                cursor.execute('''
                    INSERT INTO comments (file_id, text, line)
                    VALUES (?, ?, ?)
                ''', (
                    file_id,
                    comment['text'],
                    comment['line']
                ))
            
            self.conn.commit()
            return file_id
            
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def _delete_file_relations(self, file_id: int):
        """
        删除文件相关的所有数据
        
        Args:
            file_id: 文件 ID
        """
        cursor = self.conn.cursor()
        
        cursor.execute('DELETE FROM functions WHERE file_id = ?', (file_id,))
        cursor.execute('DELETE FROM classes WHERE file_id = ?', (file_id,))
        cursor.execute('DELETE FROM imports WHERE file_id = ?', (file_id,))
        cursor.execute('DELETE FROM comments WHERE file_id = ?', (file_id,))
    
    def delete_file_data(self, file_path: str) -> bool:
        """
        删除文件数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否删除成功
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('DELETE FROM files WHERE file_path = ?', (file_path,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def search_functions(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索函数
        
        Args:
            query: 搜索查询
            limit: 结果限制
            
        Returns:
            搜索结果列表
        """
        cursor = self.conn.cursor()
        
        # 使用 LIKE 进行模糊搜索
        search_pattern = f"%{query}%"
        
        cursor.execute('''
            SELECT 
                f.id,
                f.name,
                f.start_line,
                f.end_line,
                f.parameters,
                f.docstring,
                f.body,
                files.file_path,
                files.language
            FROM functions f
            JOIN files ON f.file_id = files.id
            WHERE 
                f.name LIKE ? OR 
                f.docstring LIKE ? OR 
                f.body LIKE ?
            ORDER BY 
                CASE 
                    WHEN f.name LIKE ? THEN 1
                    WHEN f.docstring LIKE ? THEN 2
                    ELSE 3
                END,
                f.name
            LIMIT ?
        ''', (search_pattern, search_pattern, search_pattern, 
              search_pattern, search_pattern, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'name': row['name'],
                'start_line': row['start_line'],
                'end_line': row['end_line'],
                'parameters': json.loads(row['parameters'] or '[]'),
                'docstring': row['docstring'],
                'body': row['body'],
                'file_path': row['file_path'],
                'language': row['language'],
                'type': 'function'
            })
        
        return results
    
    def search_classes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索类
        
        Args:
            query: 搜索查询
            limit: 结果限制
            
        Returns:
            搜索结果列表
        """
        cursor = self.conn.cursor()
        
        search_pattern = f"%{query}%"
        
        cursor.execute('''
            SELECT 
                c.id,
                c.name,
                c.start_line,
                c.end_line,
                c.body,
                files.file_path,
                files.language
            FROM classes c
            JOIN files ON c.file_id = files.id
            WHERE 
                c.name LIKE ? OR 
                c.body LIKE ?
            ORDER BY 
                CASE 
                    WHEN c.name LIKE ? THEN 1
                    ELSE 2
                END,
                c.name
            LIMIT ?
        ''', (search_pattern, search_pattern, search_pattern, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'name': row['name'],
                'start_line': row['start_line'],
                'end_line': row['end_line'],
                'body': row['body'],
                'file_path': row['file_path'],
                'language': row['language'],
                'type': 'class'
            })
        
        return results
    
    def search_all(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索所有类型的代码元素
        
        Args:
            query: 搜索查询
            limit: 结果限制
            
        Returns:
            搜索结果列表
        """
        functions = self.search_functions(query, limit // 2)
        classes = self.search_classes(query, limit // 2)
        
        # 合并结果并按相关性排序
        all_results = functions + classes
        
        return all_results[:limit]
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT id, file_path, language, created_at, updated_at
            FROM files
            WHERE file_path = ?
        ''', (file_path,))
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'file_path': row['file_path'],
                'language': row['language'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
        
        return None
    
    def get_stats(self):
        """获取数据库统计信息"""
        try:
            cursor = self.conn.cursor()
            
            # 获取文件数量
            cursor.execute("SELECT COUNT(*) FROM files")
            file_count = cursor.fetchone()[0]
            
            # 获取函数数量
            cursor.execute("SELECT COUNT(*) FROM functions")
            function_count = cursor.fetchone()[0]
            
            # 获取类数量
            cursor.execute("SELECT COUNT(*) FROM classes")
            class_count = cursor.fetchone()[0]
            
            # 获取数据库文件大小
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            db_size_mb = db_size / (1024 * 1024)
            
            return {
                'files': file_count,
                'functions': function_count,
                'classes': class_count,
                'db_size_mb': round(db_size_mb, 2)
            }
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return {
                'files': 0,
                'functions': 0,
                'classes': 0,
                'db_size_mb': 0.0
            }
    
    def clear_index(self):
        """清空所有索引数据"""
        cursor = self.conn.cursor()
        
        cursor.execute('DELETE FROM comments')
        cursor.execute('DELETE FROM imports')
        cursor.execute('DELETE FROM classes')
        cursor.execute('DELETE FROM functions')
        cursor.execute('DELETE FROM files')
        cursor.execute('DELETE FROM search_history')
        
        # 重置自增 ID
        cursor.execute('DELETE FROM sqlite_sequence')
        
        self.conn.commit()
    
    def save_search_history(self, query: str, results_count: int, search_time: float):
        """
        保存搜索历史
        
        Args:
            query: 搜索查询
            results_count: 结果数量
            search_time: 搜索耗时
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO search_history (query, results_count, search_time)
            VALUES (?, ?, ?)
        ''', (query, results_count, search_time))
        
        self.conn.commit()
    
    def get_search_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取搜索历史
        
        Args:
            limit: 结果限制
            
        Returns:
            搜索历史列表
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT query, results_count, search_time, created_at
            FROM search_history
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'query': row['query'],
                'results_count': row['results_count'],
                'search_time': row['search_time'],
                'created_at': row['created_at']
            })
        
        return results
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """析构函数，确保数据库连接被关闭"""
        self.close()


if __name__ == "__main__":
    # 测试代码
    db = CodeDatabase("test.db")
    
    # 测试数据
    test_data = {
        'file_path': '/test/example.py',
        'language': 'python',
        'content': 'def hello(): pass',
        'functions': [{
            'name': 'hello',
            'start_line': 1,
            'end_line': 1,
            'parameters': [],
            'docstring': 'Test function',
            'body': 'def hello(): pass'
        }],
        'classes': [],
        'imports': [],
        'comments': []
    }
    
    # 存储测试数据
    file_id = db.store_file_data(test_data)
    print(f"存储文件 ID: {file_id}")
    
    # 搜索测试
    results = db.search_functions("hello")
    print(f"搜索结果: {len(results)} 个")
    
    # 统计信息
    stats = db.get_stats()
    print(f"数据库统计: {stats}")
    
    # 清理测试数据
    db.close()
    os.remove("test.db")