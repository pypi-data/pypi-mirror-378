#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语义搜索引擎单元测试

测试SemanticSearchEngine类的所有功能，包括：
- 初始化和配置加载
- 搜索功能
- 关键词管理
- 缓存管理
- 内部方法
"""

import unittest
import tempfile
import os
import sys
import sqlite3
import yaml
from unittest.mock import Mock, patch, MagicMock

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from src.core.semantic_search import SemanticSearchEngine
from src.core.database import CodeDatabase


class TestSemanticSearchEngine(unittest.TestCase):
    """语义搜索引擎测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录和文件
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = os.path.join(self.temp_dir, 'test.db')
        self.temp_config = os.path.join(self.temp_dir, 'test_config.yaml')
        self.temp_keywords = os.path.join(self.temp_dir, 'test_keywords.yaml')
        
        # 创建测试配置文件
        config_data = {
            'database': {
                'path': self.temp_db
            },
            'search': {
                'default_limit': 50,
                'max_limit': 1000,
                'cache_size': 100
            },
            'keywords': {
                'config_file': self.temp_keywords,
                'auto_extract': True
            }
        }
        
        with open(self.temp_config, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True)
        
        # 创建测试关键词文件
        keywords_data = {
            'keyword_weights': {
                'function': 3.0,
                'class': 2.5,
                'method': 2.8,
                'test': 1.5
            },
            'term_mappings': {
                'function': ['函数', '方法', 'func', 'def'],
                'class': ['类', '对象', 'cls'],
                'test': ['测试', 'test', 'testing']
            }
        }
        
        with open(self.temp_keywords, 'w', encoding='utf-8') as f:
            yaml.dump(keywords_data, f, allow_unicode=True)
        
        # 创建测试数据库
        self._create_test_database()
    
    def tearDown(self):
        """测试后的清理工作"""
        # 清理临时文件
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_test_database(self):
        """创建测试数据库和测试数据"""
        db = CodeDatabase(self.temp_db)
        
        # 添加测试文件
        file_data = {
            'file_path': 'test.py',
            'language': 'python',
            'content': 'def test_function():\n    """测试函数"""\n    pass\n\nclass TestClass:\n    """测试类"""\n    pass',
            'functions': [{
                'name': 'test_function',
                'start_line': 1,
                'end_line': 3,
                'parameters': [],
                'docstring': '测试函数',
                'body': 'def test_function():\n    """测试函数"""\n    pass'
            }],
            'classes': [{
                'name': 'TestClass',
                'start_line': 5,
                'end_line': 7,
                'docstring': '测试类',
                'body': 'class TestClass:\n    """测试类"""\n    pass',
                'methods': [],
                'inheritance': []
            }],
            'imports': [],
            'comments': []
        }
        file_id = db.store_file_data(file_data)
        
        db.conn.close()
    
    def test_init_with_config(self):
        """测试使用配置文件初始化"""
        engine = SemanticSearchEngine(self.temp_config)
        
        self.assertIsNotNone(engine.config)
        self.assertEqual(engine.config['database']['path'], self.temp_db)
        self.assertEqual(engine.config['search']['default_limit'], 50)
        self.assertIsNotNone(engine.db)
    
    def test_init_without_config(self):
        """测试不使用配置文件初始化"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            with self.assertRaises(FileNotFoundError):
                SemanticSearchEngine()
    
    def test_init_with_invalid_config(self):
        """测试使用无效配置文件初始化"""
        invalid_config = os.path.join(self.temp_dir, 'invalid.yaml')
        with open(invalid_config, 'w') as f:
            f.write('invalid: yaml: content:')
        
        with self.assertRaises(yaml.YAMLError):
            SemanticSearchEngine(invalid_config)
    
    def test_search_basic(self):
        """测试基本搜索功能"""
        engine = SemanticSearchEngine(self.temp_config)
        
        # 测试搜索函数
        results = engine.search('function')
        self.assertIsInstance(results, list)
        
        # 测试搜索类
        results = engine.search('class')
        self.assertIsInstance(results, list)
        
        # 测试空查询
        results = engine.search('')
        self.assertEqual(results, [])
    
    def test_search_with_limit(self):
        """测试带限制的搜索"""
        engine = SemanticSearchEngine(self.temp_config)
        
        # 测试正常限制
        results = engine.search('test', limit=5)
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 5)
        
        # 测试无限制
        results = engine.search('test')
        self.assertIsInstance(results, list)
    
    def test_search_chinese(self):
        """测试中文搜索"""
        engine = SemanticSearchEngine(self.temp_config)
        
        results = engine.search('测试')
        self.assertIsInstance(results, list)
        
        results = engine.search('函数')
        self.assertIsInstance(results, list)
    
    def test_get_keyword_weight(self):
        """测试获取关键词权重"""
        engine = SemanticSearchEngine(self.temp_config)
        
        # 测试已知关键词
        weight = engine.get_keyword_weight('function')
        self.assertEqual(weight, 3.0)
        
        weight = engine.get_keyword_weight('class')
        self.assertEqual(weight, 2.5)
        
        # 测试未知关键词
        weight = engine.get_keyword_weight('unknown')
        self.assertEqual(weight, 1.0)  # 默认权重
    
    def test_auto_extract_keywords_from_codebase(self):
        """测试从代码库自动提取关键词"""
        engine = SemanticSearchEngine(self.temp_config)
        
        # 创建测试数据库并添加数据
        self._create_test_database()
        
        # 测试不更新配置
        keywords = engine.auto_extract_keywords_from_codebase(update_config=False)
        self.assertIsInstance(keywords, dict)
        
        # 检查是否有提取到的关键词（如果数据库有数据的话）
        if any(keywords.values()):
            self.assertIn('auto_functions', keywords)
            self.assertIn('auto_classes', keywords)
        
        # 测试更新配置
        keywords = engine.auto_extract_keywords_from_codebase(update_config=True)
        self.assertIsInstance(keywords, dict)
    
    def test_clear_cache(self):
        """测试清空缓存"""
        engine = SemanticSearchEngine(self.temp_config)
        
        # 执行一些搜索以填充缓存
        engine.search('test')
        engine.search('function')
        
        # 清空缓存应该不抛出异常
        engine.clear_cache()
        
        # 清空后再次搜索应该正常工作
        results = engine.search('test')
        self.assertIsInstance(results, list)
    
    def test_preprocess_query(self):
        """测试查询预处理"""
        engine = SemanticSearchEngine(self.temp_config)
        
        # 测试英文查询
        result = engine._preprocess_query('find function')
        self.assertIsInstance(result, dict)
        self.assertIn('original_query', result)
        self.assertIn('tokens', result)
        self.assertIn('keywords', result)
        
        # 测试中文查询
        result = engine._preprocess_query('查找函数')
        self.assertIsInstance(result, dict)
        self.assertIn('original_query', result)
        
        # 测试空查询
        result = engine._preprocess_query('')
        self.assertIsInstance(result, dict)
    
    def test_detect_intent(self):
        """测试意图检测"""
        engine = SemanticSearchEngine(self.temp_config)
        
        # 测试函数搜索意图
        intent = engine._detect_intent('find function')
        self.assertIn(intent, ['function_search', 'general_search'])
        
        # 测试类搜索意图
        intent = engine._detect_intent('class definition')
        self.assertIn(intent, ['class_search', 'general_search'])
        
        # 测试概念搜索意图
        intent = engine._detect_intent('database connection')
        self.assertIn(intent, ['concept_search', 'general_search'])
        
        # 测试文件搜索意图
        intent = engine._detect_intent('config file')
        self.assertIn(intent, ['file_search', 'general_search'])
    
    def test_build_term_mappings(self):
        """测试构建术语映射"""
        engine = SemanticSearchEngine(self.temp_config)
        
        mappings = engine._build_term_mappings()
        self.assertIsInstance(mappings, dict)
        
        # 检查配置中的映射是否存在
        self.assertIn('function', mappings)
        self.assertIn('class', mappings)
        
        # 检查映射内容
        self.assertIn('函数', mappings['function'])
        self.assertIn('类', mappings['class'])
    
    def test_search_with_different_intents(self):
        """测试不同意图的搜索"""
        engine = SemanticSearchEngine(self.temp_config)
        
        # 测试函数搜索
        results = engine.search('function definition')
        self.assertIsInstance(results, list)
        
        # 测试类搜索
        results = engine.search('class inheritance')
        self.assertIsInstance(results, list)
        
        # 测试概念搜索
        results = engine.search('test concept')
        self.assertIsInstance(results, list)
    
    def test_search_result_format(self):
        """测试搜索结果格式"""
        engine = SemanticSearchEngine(self.temp_config)
        
        results = engine.search('test', limit=1)
        
        if results:  # 如果有结果
            result = results[0]
            
            # 检查必需字段
            required_fields = ['id', 'name', 'type', 'file_path', 'start_line', 
                             'end_line', 'docstring', 'body', 'score', 'language']
            
            for field in required_fields:
                self.assertIn(field, result, f"缺少字段: {field}")
            
            # 检查字段类型
            self.assertIsInstance(result['id'], int)
            self.assertIsInstance(result['name'], str)
            self.assertIsInstance(result['type'], str)
            self.assertIsInstance(result['file_path'], str)
            self.assertIsInstance(result['start_line'], int)
            self.assertIsInstance(result['end_line'], int)
            self.assertIsInstance(result['score'], (int, float))
    
    def test_error_handling(self):
        """测试错误处理"""
        engine = SemanticSearchEngine(self.temp_config)
        
        # 测试数据库连接错误处理
        with patch.object(engine.db, 'conn') as mock_conn:
            mock_conn.cursor.side_effect = sqlite3.Error("Database error")
            
            # 搜索应该处理数据库错误
            results = engine.search('test')
            self.assertIsInstance(results, list)
    
    def test_caching_behavior(self):
        """测试缓存行为"""
        engine = SemanticSearchEngine(self.temp_config)
        
        # 第一次搜索
        results1 = engine.search('test function')
        
        # 第二次相同搜索（应该使用缓存）
        results2 = engine.search('test function')
        
        # 结果应该相同
        self.assertEqual(len(results1), len(results2))
        
        # 清空缓存后再次搜索
        engine.clear_cache()
        results3 = engine.search('test function')
        
        # 结果应该仍然相同
        self.assertEqual(len(results1), len(results3))
    
    def test_config_validation(self):
        """测试配置验证"""
        # 测试缺少必需配置项
        incomplete_config = os.path.join(self.temp_dir, 'incomplete.yaml')
        with open(incomplete_config, 'w') as f:
            yaml.dump({'search': {'default_limit': 50}}, f)
        
        # 应该能够处理不完整的配置
        engine = SemanticSearchEngine(incomplete_config)
        self.assertIsNotNone(engine.config)
    
    def test_multilingual_search(self):
        """测试多语言搜索"""
        engine = SemanticSearchEngine(self.temp_config)
        
        # 测试中英文混合搜索
        results = engine.search('test 函数 function')
        self.assertIsInstance(results, list)
        
        # 测试纯中文搜索
        results = engine.search('测试函数')
        self.assertIsInstance(results, list)
        
        # 测试纯英文搜索
        results = engine.search('test function')
        self.assertIsInstance(results, list)


class TestSemanticSearchEngineIntegration(unittest.TestCase):
    """语义搜索引擎集成测试"""
    
    def setUp(self):
        """集成测试准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_config = os.path.join(self.temp_dir, 'integration_config.yaml')
        
        # 创建更复杂的测试配置
        config_data = {
            'database': {
                'path': os.path.join(self.temp_dir, 'integration.db')
            },
            'search': {
                'default_limit': 20,
                'max_limit': 500,
                'cache_size': 50
            },
            'keywords': {
                'config_file': os.path.join(self.temp_dir, 'integration_keywords.yaml'),
                'auto_extract': True
            }
        }
        
        with open(self.temp_config, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True)
    
    def tearDown(self):
        """集成测试清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_full_workflow(self):
        """测试完整工作流程"""
        # 1. 初始化引擎
        engine = SemanticSearchEngine(self.temp_config)
        self.assertIsNotNone(engine)
        
        # 2. 执行搜索
        results = engine.search('test')
        self.assertIsInstance(results, list)
        
        # 3. 获取关键词权重
        weight = engine.get_keyword_weight('test')
        self.assertIsInstance(weight, (int, float))
        
        # 4. 清空缓存
        engine.clear_cache()
        
        # 5. 再次搜索
        results2 = engine.search('test')
        self.assertIsInstance(results2, list)


if __name__ == '__main__':
    # 设置测试环境
    unittest.main(verbosity=2)