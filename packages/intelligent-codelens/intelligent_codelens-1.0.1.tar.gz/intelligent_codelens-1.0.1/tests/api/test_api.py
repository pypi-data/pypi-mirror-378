"""
API模块单元测试
测试Web API接口
"""

import unittest
import json
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# 导入Flask测试客户端
try:
    from api import app, semantic_engine
    from database import CodeDatabase
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


@unittest.skipUnless(HAS_FLASK, "Flask not available")
class TestAPI(unittest.TestCase):
    """测试API接口"""
    
    def setUp(self):
        """测试前准备"""
        # 配置测试环境
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        
        # 创建测试客户端
        self.client = app.test_client()
        
        # 创建临时数据库
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        
        # 模拟语义搜索引擎
        self.mock_engine = MagicMock()
        
        # 设置测试数据
        self.setup_test_data()
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def setup_test_data(self):
        """设置测试数据"""
        # 模拟搜索结果
        self.mock_search_results = [
            {
                'type': 'function',
                'name': 'test_function',
                'file_path': '/test/example.py',
                'line_number': 10,
                'score': 0.95,
                'content': 'def test_function(): pass',
                'docstring': '测试函数'
            },
            {
                'type': 'class',
                'name': 'TestClass',
                'file_path': '/test/example.py',
                'line_number': 20,
                'score': 0.88,
                'content': 'class TestClass: pass',
                'docstring': '测试类'
            }
        ]
        
        # 模拟统计信息
        self.mock_stats = {
            'files': 10,
            'functions': 50,
            'classes': 20,
            'imports': 30,
            'comments': 100
        }
    
    def test_health_check(self):
        """测试健康检查接口"""
        response = self.client.get('/health')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('version', data)
    
    @patch('api.semantic_engine')
    def test_search_endpoint(self, mock_engine):
        """测试搜索接口"""
        # 配置模拟对象
        mock_engine.search.return_value = self.mock_search_results
        
        # 发送搜索请求
        response = self.client.post('/api/search', 
                                  json={'query': 'test function'})
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('results', data)
        self.assertIn('total', data)
        self.assertIn('query', data)
        self.assertIn('execution_time', data)
        
        # 验证搜索结果
        results = data['results']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['name'], 'test_function')
        self.assertEqual(results[1]['name'], 'TestClass')
        
        # 验证搜索引擎被调用
        mock_engine.search.assert_called_once_with('test function')
    
    @patch('api.semantic_engine')
    def test_search_with_filters(self, mock_engine):
        """测试带过滤器的搜索"""
        mock_engine.search.return_value = self.mock_search_results
        
        # 发送带过滤器的搜索请求
        response = self.client.post('/api/search', json={
            'query': 'test',
            'filters': {
                'type': 'function',
                'file_path': '/test/',
                'min_score': 0.8
            },
            'limit': 10,
            'offset': 0
        })
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('results', data)
        
        # 验证搜索引擎被正确调用
        mock_engine.search.assert_called_once()
        call_args = mock_engine.search.call_args
        self.assertEqual(call_args[0][0], 'test')  # query参数
    
    def test_search_invalid_request(self):
        """测试无效搜索请求"""
        # 缺少query参数
        response = self.client.post('/api/search', json={})
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('query', data['error'].lower())
        
        # 空query
        response = self.client.post('/api/search', json={'query': ''})
        self.assertEqual(response.status_code, 400)
        
        # 无效JSON
        response = self.client.post('/api/search', 
                                  data='invalid json',
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    @patch('api.semantic_engine')
    def test_search_with_error(self, mock_engine):
        """测试搜索时发生错误"""
        # 模拟搜索引擎抛出异常
        mock_engine.search.side_effect = Exception("Search engine error")
        
        response = self.client.post('/api/search', 
                                  json={'query': 'test'})
        
        self.assertEqual(response.status_code, 500)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('internal server error', data['error'].lower())
    
    @patch('api.semantic_engine')
    def test_statistics_endpoint(self, mock_engine):
        """测试统计信息接口"""
        # 配置模拟对象
        mock_engine.get_statistics.return_value = self.mock_stats
        
        response = self.client.get('/api/statistics')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['files'], 10)
        self.assertEqual(data['functions'], 50)
        self.assertEqual(data['classes'], 20)
        self.assertEqual(data['imports'], 30)
        self.assertEqual(data['comments'], 100)
        
        # 验证统计方法被调用
        mock_engine.get_statistics.assert_called_once()
    
    @patch('api.semantic_engine')
    def test_keywords_endpoint(self, mock_engine):
        """测试关键词接口"""
        mock_keywords = ['function', 'class', 'method', 'variable']
        mock_engine.get_all_keywords.return_value = mock_keywords
        
        response = self.client.get('/api/keywords')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('keywords', data)
        self.assertEqual(data['keywords'], mock_keywords)
        self.assertIn('total', data)
        self.assertEqual(data['total'], len(mock_keywords))
    
    @patch('api.semantic_engine')
    def test_add_keywords_endpoint(self, mock_engine):
        """测试添加关键词接口"""
        new_keywords = ['new_keyword1', 'new_keyword2']
        
        response = self.client.post('/api/keywords', 
                                  json={'keywords': new_keywords})
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('added', data['message'].lower())
        
        # 验证添加关键词方法被调用
        mock_engine.add_keywords.assert_called_once_with(new_keywords)
    
    @patch('api.semantic_engine')
    def test_remove_keywords_endpoint(self, mock_engine):
        """测试删除关键词接口"""
        keywords_to_remove = ['old_keyword1', 'old_keyword2']
        
        response = self.client.delete('/api/keywords', 
                                    json={'keywords': keywords_to_remove})
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('removed', data['message'].lower())
        
        # 验证删除关键词方法被调用
        mock_engine.remove_keywords.assert_called_once_with(keywords_to_remove)
    
    @patch('api.semantic_engine')
    def test_index_directory_endpoint(self, mock_engine):
        """测试索引目录接口"""
        directory_path = '/test/directory'
        
        response = self.client.post('/api/index', 
                                  json={'directory': directory_path})
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('indexed', data['message'].lower())
        
        # 验证索引方法被调用
        mock_engine.index_directory.assert_called_once_with(directory_path)
    
    @patch('api.semantic_engine')
    def test_index_file_endpoint(self, mock_engine):
        """测试索引文件接口"""
        file_path = '/test/file.py'
        
        response = self.client.post('/api/index/file', 
                                  json={'file_path': file_path})
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('indexed', data['message'].lower())
        
        # 验证索引方法被调用
        mock_engine.index_file.assert_called_once_with(file_path)
    
    @patch('api.semantic_engine')
    def test_clear_index_endpoint(self, mock_engine):
        """测试清空索引接口"""
        response = self.client.delete('/api/index')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('cleared', data['message'].lower())
        
        # 验证清空方法被调用
        mock_engine.clear_index.assert_called_once()
    
    @patch('api.semantic_engine')
    def test_config_endpoint(self, mock_engine):
        """测试配置接口"""
        mock_config = {
            'search_limit': 50,
            'similarity_threshold': 0.7,
            'cache_enabled': True
        }
        mock_engine.get_config.return_value = mock_config
        
        response = self.client.get('/api/config')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data, mock_config)
    
    @patch('api.semantic_engine')
    def test_update_config_endpoint(self, mock_engine):
        """测试更新配置接口"""
        new_config = {
            'search_limit': 100,
            'similarity_threshold': 0.8
        }
        
        response = self.client.put('/api/config', json=new_config)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('updated', data['message'].lower())
        
        # 验证更新配置方法被调用
        mock_engine.update_config.assert_called_once_with(new_config)
    
    def test_cors_headers(self):
        """测试CORS头部"""
        response = self.client.get('/health')
        
        # 检查CORS头部
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertIn('Access-Control-Allow-Methods', response.headers)
        self.assertIn('Access-Control-Allow-Headers', response.headers)
    
    def test_options_request(self):
        """测试OPTIONS请求"""
        response = self.client.options('/api/search')
        
        self.assertEqual(response.status_code, 200)
        
        # 检查CORS头部
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertIn('Access-Control-Allow-Methods', response.headers)
    
    def test_rate_limiting(self):
        """测试速率限制"""
        # 发送多个快速请求
        responses = []
        for i in range(10):
            response = self.client.get('/health')
            responses.append(response)
        
        # 验证所有请求都成功（假设没有严格的速率限制）
        for response in responses:
            self.assertIn(response.status_code, [200, 429])  # 200或429（太多请求）
    
    def test_request_logging(self):
        """测试请求日志"""
        with patch('api.app.logger') as mock_logger:
            response = self.client.get('/health')
            
            # 验证日志记录
            self.assertTrue(mock_logger.info.called or mock_logger.debug.called)
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试404错误
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('not found', data['error'].lower())
        
        # 测试405错误（方法不允许）
        response = self.client.put('/health')
        self.assertEqual(response.status_code, 405)
    
    def test_request_validation(self):
        """测试请求验证"""
        # 测试Content-Type验证
        response = self.client.post('/api/search', 
                                  data='{"query": "test"}',
                                  content_type='text/plain')
        self.assertEqual(response.status_code, 400)
        
        # 测试请求大小限制
        large_query = 'x' * 10000  # 很长的查询
        response = self.client.post('/api/search', 
                                  json={'query': large_query})
        # 根据实际实现，可能返回400或413
        self.assertIn(response.status_code, [400, 413])
    
    @patch('api.semantic_engine')
    def test_async_operations(self, mock_engine):
        """测试异步操作"""
        # 模拟长时间运行的操作
        import time
        
        def slow_search(query):
            time.sleep(0.1)  # 模拟慢查询
            return self.mock_search_results
        
        mock_engine.search.side_effect = slow_search
        
        # 发送搜索请求
        response = self.client.post('/api/search', 
                                  json={'query': 'test'})
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('execution_time', data)
        self.assertGreater(data['execution_time'], 0.05)  # 至少50ms
    
    def test_api_versioning(self):
        """测试API版本控制"""
        # 测试版本1
        response = self.client.get('/api/v1/health')
        # 根据实际实现，可能返回200或404
        self.assertIn(response.status_code, [200, 404])
        
        # 测试默认版本
        response = self.client.get('/api/health')
        # 应该重定向到当前版本或直接处理
        self.assertIn(response.status_code, [200, 301, 302])
    
    def test_authentication(self):
        """测试身份验证（如果实现了）"""
        # 如果API需要身份验证
        # response = self.client.get('/api/admin/config')
        # self.assertEqual(response.status_code, 401)
        
        # 带有有效token的请求
        # headers = {'Authorization': 'Bearer valid_token'}
        # response = self.client.get('/api/admin/config', headers=headers)
        # self.assertEqual(response.status_code, 200)
        pass
    
    def test_response_format(self):
        """测试响应格式"""
        response = self.client.get('/health')
        
        # 验证Content-Type
        self.assertEqual(response.content_type, 'application/json')
        
        # 验证JSON格式
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
        
        # 验证响应结构
        self.assertIn('status', data)
        self.assertIn('timestamp', data)


class TestAPIIntegration(unittest.TestCase):
    """API集成测试"""
    
    @unittest.skipUnless(HAS_FLASK, "Flask not available")
    def setUp(self):
        """测试前准备"""
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # 创建真实的数据库和搜索引擎
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_full_workflow(self):
        """测试完整工作流程"""
        # 1. 检查健康状态
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        # 2. 获取初始统计信息
        response = self.client.get('/api/statistics')
        self.assertEqual(response.status_code, 200)
        
        # 3. 执行搜索
        response = self.client.post('/api/search', 
                                  json={'query': 'function'})
        self.assertEqual(response.status_code, 200)
        
        # 4. 获取关键词
        response = self.client.get('/api/keywords')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()