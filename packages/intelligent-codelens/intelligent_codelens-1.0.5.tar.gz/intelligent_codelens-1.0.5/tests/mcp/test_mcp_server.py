"""
MCP服务器单元测试
测试MCP协议实现和服务器功能
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.mcp.mcp_server import SimpleMCPServer as CodeSearchServer
from src.mcp.fastmcp_server import (
    search_code,
    get_file_content,
    get_function_details,
    get_database_stats
)
from src.core.database import CodeDatabase
from src.core.semantic_search import SemanticSearchEngine


class TestCodeSearchServer:
    """测试CodeSearchServer类"""
    
    @pytest.fixture
    def temp_db(self):
        """创建临时数据库"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        db = CodeDatabase(db_path)
        yield db
        
        db.close()
        os.unlink(db_path)
    
    @pytest.fixture
    def server(self, temp_db):
        """创建测试服务器实例"""
        with patch('src.mcp.mcp_server.CodeDatabase') as mock_db_class:
            mock_db_class.return_value = temp_db
            server = CodeSearchServer()
            server.db = temp_db
            return server
    
    def test_server_initialization(self, server):
        """测试服务器初始化"""
        assert server is not None
        assert hasattr(server, 'db')
        assert hasattr(server, 'search_engine')
    
    @pytest.mark.asyncio
    async def test_search_code_handler(self, server):
        """测试搜索代码处理器"""
        # 添加测试数据
        server.db.add_file("test.py", "/test/test.py", "python")
        server.db.add_function("test_func", "test.py", 1, 10, "def test_func(): pass", "python")
        
        # 模拟搜索请求
        request = Mock()
        request.params = {
            "arguments": {
                "query": "test_func",
                "limit": 10,
                "file_type": ""
            }
        }
        
        # 执行搜索
        with patch.object(server.search_engine, 'search') as mock_search:
            mock_search.return_value = [
                {
                    'file_path': '/test/test.py',
                    'function_name': 'test_func',
                    'line_start': 1,
                    'line_end': 10,
                    'code': 'def test_func(): pass',
                    'score': 0.95
                }
            ]
            
            result = await server.search_code(request)
            
            assert result is not None
            assert 'content' in result
            results = json.loads(result['content'][0]['text'])
            assert len(results) > 0
            assert results[0]['function_name'] == 'test_func'
    
    @pytest.mark.asyncio
    async def test_get_file_content_handler(self, server):
        """测试获取文件内容处理器"""
        # 创建测试文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test_function():\n    return 'hello'\n\nclass TestClass:\n    pass")
            test_file_path = f.name
        
        try:
            request = Mock()
            request.params = {
                "arguments": {
                    "file_path": test_file_path,
                    "start_line": 1,
                    "end_line": 2
                }
            }
            
            result = await server.get_file_content(request)
            
            assert result is not None
            assert 'content' in result
            content = json.loads(result['content'][0]['text'])
            assert 'content' in content
            assert 'def test_function():' in content['content']
            
        finally:
            os.unlink(test_file_path)
    
    @pytest.mark.asyncio
    async def test_get_function_details_handler(self, server):
        """测试获取函数详情处理器"""
        # 添加测试数据
        server.db.add_file("test.py", "/test/test.py", "python")
        server.db.add_function("test_func", "test.py", 1, 10, "def test_func(): pass", "python")
        
        request = Mock()
        request.params = {
            "arguments": {
                "function_name": "test_func",
                "file_path": None
            }
        }
        
        result = await server.get_function_details(request)
        
        assert result is not None
        assert 'content' in result
        details = json.loads(result['content'][0]['text'])
        assert len(details) > 0
        assert details[0]['function_name'] == 'test_func'
    
    @pytest.mark.asyncio
    async def test_get_database_stats_handler(self, server):
        """测试获取数据库统计处理器"""
        # 添加测试数据
        server.db.add_file("test.py", "/test/test.py", "python")
        server.db.add_function("test_func", "test.py", 1, 10, "def test_func(): pass", "python")
        
        request = Mock()
        request.params = {"arguments": {}}
        
        result = await server.get_database_stats(request)
        
        assert result is not None
        assert 'content' in result
        stats = json.loads(result['content'][0]['text'])
        assert 'total_files' in stats
        assert 'total_functions' in stats
        assert stats['total_files'] >= 1
        assert stats['total_functions'] >= 1


class TestMCPFunctions:
    """测试MCP功能函数"""
    
    @pytest.fixture
    def temp_db(self):
        """创建临时数据库"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        db = CodeDatabase(db_path)
        yield db
        
        db.close()
        os.unlink(db_path)
    
    @pytest.mark.asyncio
    async def test_search_code_function(self, temp_db):
        """测试搜索代码函数"""
        # 添加测试数据
        temp_db.add_file("test.py", "/test/test.py", "python")
        temp_db.add_function("test_func", "test.py", 1, 10, "def test_func(): pass", "python")
        
        with patch('mcp_server.db', temp_db):
            with patch('mcp_server.search_engine') as mock_engine:
                mock_engine.search.return_value = [
                    {
                        'file_path': '/test/test.py',
                        'function_name': 'test_func',
                        'line_start': 1,
                        'line_end': 10,
                        'code': 'def test_func(): pass',
                        'score': 0.95
                    }
                ]
                
                result = await search_code("test_func", 10, "")
                
                assert result is not None
                results = json.loads(result)
                assert len(results) > 0
                assert results[0]['function_name'] == 'test_func'
    
    @pytest.mark.asyncio
    async def test_get_file_content_function(self):
        """测试获取文件内容函数"""
        # 创建测试文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test_function():\n    return 'hello'\n\nclass TestClass:\n    pass")
            test_file_path = f.name
        
        try:
            result = await get_file_content(test_file_path, 1, 2)
            
            assert result is not None
            content = json.loads(result)
            assert 'content' in content
            assert 'def test_function():' in content['content']
            assert content['start_line'] == 1
            assert content['end_line'] == 2
            
        finally:
            os.unlink(test_file_path)
    
    @pytest.mark.asyncio
    async def test_get_file_content_entire_file(self):
        """测试获取整个文件内容"""
        # 创建测试文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test_function():\n    return 'hello'\n\nclass TestClass:\n    pass")
            test_file_path = f.name
        
        try:
            result = await get_file_content(test_file_path)
            
            assert result is not None
            content = json.loads(result)
            assert 'content' in content
            assert 'def test_function():' in content['content']
            assert 'class TestClass:' in content['content']
            
        finally:
            os.unlink(test_file_path)
    
    @pytest.mark.asyncio
    async def test_get_file_content_nonexistent_file(self):
        """测试获取不存在文件的内容"""
        result = await get_file_content("/nonexistent/file.py")
        
        assert result is not None
        content = json.loads(result)
        assert 'error' in content
        assert 'not found' in content['error'].lower()
    
    @pytest.mark.asyncio
    async def test_get_function_details_function(self, temp_db):
        """测试获取函数详情函数"""
        # 添加测试数据
        temp_db.add_file("test.py", "/test/test.py", "python")
        temp_db.add_function("test_func", "test.py", 1, 10, "def test_func(): pass", "python")
        
        with patch('mcp_server.db', temp_db):
            result = await get_function_details("test_func")
            
            assert result is not None
            details = json.loads(result)
            assert len(details) > 0
            assert details[0]['function_name'] == 'test_func'
    
    @pytest.mark.asyncio
    async def test_get_function_details_with_file_path(self, temp_db):
        """测试指定文件路径获取函数详情"""
        # 添加测试数据
        temp_db.add_file("test.py", "/test/test.py", "python")
        temp_db.add_function("test_func", "test.py", 1, 10, "def test_func(): pass", "python")
        
        with patch('mcp_server.db', temp_db):
            result = await get_function_details("test_func", "/test/test.py")
            
            assert result is not None
            details = json.loads(result)
            assert len(details) > 0
            assert details[0]['function_name'] == 'test_func'
            assert details[0]['file_path'] == '/test/test.py'
    
    @pytest.mark.asyncio
    async def test_get_function_details_not_found(self, temp_db):
        """测试获取不存在函数的详情"""
        with patch('mcp_server.db', temp_db):
            result = await get_function_details("nonexistent_func")
            
            assert result is not None
            details = json.loads(result)
            assert len(details) == 0
    
    @pytest.mark.asyncio
    async def test_get_database_stats_function(self, temp_db):
        """测试获取数据库统计函数"""
        # 添加测试数据
        temp_db.add_file("test.py", "/test/test.py", "python")
        temp_db.add_function("test_func", "test.py", 1, 10, "def test_func(): pass", "python")
        temp_db.add_class("TestClass", "test.py", 15, 25, "class TestClass: pass", "python")
        
        with patch('mcp_server.db', temp_db):
            result = await get_database_stats()
            
            assert result is not None
            stats = json.loads(result)
            assert 'total_files' in stats
            assert 'total_functions' in stats
            assert 'total_classes' in stats
            assert stats['total_files'] >= 1
            assert stats['total_functions'] >= 1
            assert stats['total_classes'] >= 1


class TestMCPErrorHandling:
    """测试MCP错误处理"""
    
    @pytest.mark.asyncio
    async def test_search_code_with_invalid_limit(self):
        """测试无效限制参数的搜索"""
        with patch('mcp_server.db') as mock_db:
            with patch('mcp_server.search_engine') as mock_engine:
                mock_engine.search.side_effect = ValueError("Invalid limit")
                
                result = await search_code("test", -1, "")
                
                assert result is not None
                # 应该返回错误信息或空结果
    
    @pytest.mark.asyncio
    async def test_search_code_with_database_error(self):
        """测试数据库错误的搜索"""
        with patch('mcp_server.db') as mock_db:
            mock_db.get_stats.side_effect = Exception("Database error")
            
            with patch('mcp_server.search_engine') as mock_engine:
                mock_engine.search.side_effect = Exception("Database error")
                
                result = await search_code("test", 10, "")
                
                assert result is not None
                # 应该处理错误并返回适当的响应
    
    @pytest.mark.asyncio
    async def test_get_file_content_with_permission_error(self):
        """测试权限错误的文件读取"""
        # 创建一个无权限访问的文件路径
        result = await get_file_content("/root/restricted_file.py")
        
        assert result is not None
        content = json.loads(result)
        assert 'error' in content or 'content' in content
    
    @pytest.mark.asyncio
    async def test_get_function_details_with_database_error(self):
        """测试数据库错误的函数详情获取"""
        with patch('mcp_server.db') as mock_db:
            mock_db.get_functions.side_effect = Exception("Database error")
            
            result = await get_function_details("test_func")
            
            assert result is not None
            # 应该处理错误并返回适当的响应
    
    @pytest.mark.asyncio
    async def test_get_database_stats_with_error(self):
        """测试数据库统计错误"""
        with patch('mcp_server.db') as mock_db:
            mock_db.get_stats.side_effect = Exception("Database error")
            
            result = await get_database_stats()
            
            assert result is not None
            # 应该处理错误并返回适当的响应


class TestMCPIntegration:
    """测试MCP集成功能"""
    
    @pytest.fixture
    def temp_db(self):
        """创建临时数据库"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        db = CodeDatabase(db_path)
        yield db
        
        db.close()
        os.unlink(db_path)
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, temp_db):
        """测试完整的工作流程"""
        # 1. 添加测试数据
        temp_db.add_file("example.py", "/test/example.py", "python")
        temp_db.add_function("example_func", "example.py", 1, 10, 
                           "def example_func(x):\n    return x * 2", "python")
        temp_db.add_class("ExampleClass", "example.py", 15, 25, 
                         "class ExampleClass:\n    def method(self): pass", "python")
        
        with patch('mcp_server.db', temp_db):
            # 2. 测试搜索功能
            with patch('mcp_server.search_engine') as mock_engine:
                mock_engine.search.return_value = [
                    {
                        'file_path': '/test/example.py',
                        'function_name': 'example_func',
                        'line_start': 1,
                        'line_end': 10,
                        'code': 'def example_func(x):\n    return x * 2',
                        'score': 0.95
                    }
                ]
                
                search_result = await search_code("example", 10, "")
                assert search_result is not None
                
                results = json.loads(search_result)
                assert len(results) > 0
                assert results[0]['function_name'] == 'example_func'
            
            # 3. 测试函数详情获取
            function_result = await get_function_details("example_func")
            assert function_result is not None
            
            details = json.loads(function_result)
            assert len(details) > 0
            assert details[0]['function_name'] == 'example_func'
            
            # 4. 测试数据库统计
            stats_result = await get_database_stats()
            assert stats_result is not None
            
            stats = json.loads(stats_result)
            assert stats['total_files'] >= 1
            assert stats['total_functions'] >= 1
            assert stats['total_classes'] >= 1
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, temp_db):
        """测试并发请求处理"""
        # 添加测试数据
        temp_db.add_file("test.py", "/test/test.py", "python")
        temp_db.add_function("test_func", "test.py", 1, 10, "def test_func(): pass", "python")
        
        with patch('mcp_server.db', temp_db):
            with patch('mcp_server.search_engine') as mock_engine:
                mock_engine.search.return_value = []
                
                # 创建多个并发任务
                tasks = [
                    search_code("test", 10, ""),
                    get_function_details("test_func"),
                    get_database_stats(),
                    search_code("func", 5, "py"),
                    get_function_details("nonexistent")
                ]
                
                # 并发执行
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 验证所有任务都完成了
                assert len(results) == 5
                for result in results:
                    assert not isinstance(result, Exception)
                    assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])