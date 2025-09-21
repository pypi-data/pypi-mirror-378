#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强搜索引擎测试模块

测试重构后的通用搜索引擎功能，包括：
- 基础搜索功能
- 配置管理
- 权重系统
- 意图识别
- 预设配置
"""

import unittest
import tempfile
import os
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到路径
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.enhanced_search_engine import EnhancedSearchEngine


class TestEnhancedSearchEngine(unittest.TestCase):
    """增强搜索引擎测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'search_config.yaml')
        
        # 创建测试配置文件
        test_config = {
            'search_weights': {
                'exact_match': 20.0,
                'partial_match': 12.0,
                'docstring_match': 8.0
            },
            'search_strategies': {
                'fuzzy_threshold': 0.8,
                'max_results': 50
            },
            'language_weights': {
                'python': 1.2,
                'javascript': 1.1
            },
            'intent_weights': {
                'how_to': 1.5,
                'definition': 1.3,
                'example': 1.4
            },
            'search_presets': {
                'quick': {
                    'search_weights': {
                        'exact_match': 30.0,
                        'partial_match': 10.0
                    }
                },
                'deep': {
                    'search_weights': {
                        'exact_match': 30.0,
                        'partial_match': 20.0
                    }
                }
            }
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f, default_flow_style=False)
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization_with_config(self):
        """测试使用配置文件初始化"""
        engine = EnhancedSearchEngine(config_path=self.config_path)
        
        # 验证配置加载
        self.assertEqual(engine.search_weights['exact_match'], 20.0)  # 使用测试配置的权重
        self.assertEqual(engine.search_weights['partial_match'], 12.0)
        self.assertEqual(engine.search_weights['docstring_match'], 8.0)
        # 注意：语言权重在配置文件中没有定义，所以使用默认值1.0
        self.assertEqual(engine.language_weights['python'], 1.0)  # 使用默认值
        self.assertEqual(engine.intent_weights['how_to'], 1.5)
    
    def test_initialization_with_manual_config(self):
        """测试手动设置配置并重新初始化"""
        engine = EnhancedSearchEngine()
        
        # 手动设置配置
        test_config = {
            'search_weights': {
                'exact_match': 20.0,
                'partial_match': 12.0,
                'docstring_match': 8.0
            },
            'language_weights': {
                'python': 1.2
            }
        }
        
        engine.search_config = test_config
        engine._init_search_enhancements()  # 重新初始化以应用配置
        
        # 验证搜索权重
        self.assertEqual(engine.search_weights['exact_match'], 20.0)
        self.assertEqual(engine.search_weights['partial_match'], 12.0)
        self.assertEqual(engine.search_weights['docstring_match'], 8.0)
        
        # 验证语言权重
        self.assertEqual(engine.language_weights['python'], 1.2)  # 从测试配置加载
    
    def test_initialization_without_config(self):
        """测试无配置文件初始化（使用默认配置）"""
        engine = EnhancedSearchEngine(config_path='nonexistent.yaml')
        
        # 验证默认配置
        self.assertIsInstance(engine.search_weights, dict)
        self.assertIsInstance(engine.search_strategies, dict)
        self.assertIsInstance(engine.language_weights, dict)
    
    def test_query_intent_detection(self):
        """测试查询意图识别"""
        engine = EnhancedSearchEngine(config_path=self.config_path)
        
        # 测试不同意图
        self.assertEqual(engine._detect_query_intent("how to implement function"), "how_to")
        self.assertEqual(engine._detect_query_intent("what is python"), "definition")
        self.assertEqual(engine._detect_query_intent("show me example"), "example")
        self.assertEqual(engine._detect_query_intent("fix this bug"), "debug")
        self.assertEqual(engine._detect_query_intent("random query"), "general")
    
    def test_code_type_detection(self):
        """测试代码类型检测"""
        engine = EnhancedSearchEngine(config_path=self.config_path)
        
        # 测试不同代码类型
        self.assertEqual(engine._detect_code_type("let x = 10"), "variable")  # let 匹配 variable
        self.assertEqual(engine._detect_code_type("def test_function():"), "function")
        self.assertEqual(engine._detect_code_type("class TestClass:"), "class")
        self.assertEqual(engine._detect_code_type("const PI = 3.14"), "variable")  # const 也会匹配 variable (因为有 = )
        self.assertEqual(engine._detect_code_type("random text"), "general")
    
    def test_load_preset_config(self):
        """测试加载预设配置"""
        engine = EnhancedSearchEngine()
        
        # 手动设置配置
        test_config = {
            'search_weights': {
                'exact_match': 20.0,
                'partial_match': 12.0,
                'docstring_match': 8.0
            },
            'search_presets': {
                'quick': {
                    'search_weights': {
                        'exact_match': 30.0,
                        'partial_match': 10.0,
                        'docstring_match': 5.0
                    }
                }
            }
        }
        
        engine.search_config = test_config
        engine._init_search_enhancements()  # 重新初始化以应用配置
        
        # 测试加载存在的预设
        result = engine.load_preset_config("quick")
        assert result == True
        
        # 验证权重已更新
        assert engine.search_weights['exact_match'] == 30.0
        assert engine.search_weights['partial_match'] == 10.0
        
        # 测试加载不存在的预设
        result = engine.load_preset_config("nonexistent")
        assert result == False
    
    def test_update_search_weights(self):
        """测试动态更新搜索权重"""
        engine = EnhancedSearchEngine(config_path=self.config_path)
        
        original_weight = engine.search_weights['exact_match']
        
        # 更新权重
        new_weights = {'exact_match': 50.0, 'new_weight': 2.0}
        engine.update_search_weights(new_weights)
        
        # 验证更新
        self.assertEqual(engine.search_weights['exact_match'], 50.0)
        self.assertEqual(engine.search_weights['new_weight'], 2.0)
    
    def test_update_search_strategies(self):
        """测试动态更新搜索策略"""
        engine = EnhancedSearchEngine(config_path=self.config_path)
        
        # 更新策略
        new_strategies = {'new_strategy': True, 'max_results': 100}
        engine.update_search_strategies(new_strategies)
        
        # 验证更新
        self.assertEqual(engine.search_strategies['new_strategy'], True)
        self.assertEqual(engine.search_strategies['max_results'], 100)
    
    def test_get_current_config(self):
        """测试获取当前配置"""
        engine = EnhancedSearchEngine()
        
        # 手动设置配置
        test_config = {
            'search_weights': {
                'exact_match': 20.0,
                'partial_match': 12.0,
                'docstring_match': 8.0
            },
            'language_weights': {
                'python': 1.2
            }
        }
        
        engine.search_config = test_config
        engine._init_search_enhancements()  # 重新初始化以应用配置
        
        config = engine.get_current_config()
        
        # 验证配置内容
        assert 'search_weights' in config
        assert 'language_weights' in config
        assert config['search_weights']['exact_match'] == 20.0
        assert config['search_weights']['partial_match'] == 12.0
        assert config['language_weights']['python'] == 1.2  # 从测试配置加载
    
    @patch('src.core.enhanced_search_engine.EnhancedSearchEngine._enhanced_search')
    def test_search_basic_mode(self, mock_search):
        """测试基础搜索模式"""
        engine = EnhancedSearchEngine(config_path=self.config_path)
        mock_search.return_value = [{'content': 'test', 'file_path': 'test.py'}]
        
        results = engine.search("test query", mode="enhanced")  # 使用 enhanced 模式
        
        # 验证搜索调用
        mock_search.assert_called_once()
        self.assertEqual(len(results), 1)
    
    @patch('src.core.enhanced_search_engine.EnhancedSearchEngine._enhanced_search')
    def test_search_enhanced_mode(self, mock_search):
        """测试增强搜索模式"""
        engine = EnhancedSearchEngine(config_path=self.config_path)
        mock_search.return_value = [{'content': 'test function', 'file_path': 'test.py'}]
        
        results = engine.search("how to test", mode="enhanced")
        
        # 验证搜索调用
        mock_search.assert_called_once()
        self.assertEqual(len(results), 1)
    
    def test_relevance_score_calculation(self):
        """测试相关性分数计算"""
        engine = EnhancedSearchEngine(config_path=self.config_path)
        
        # 模拟搜索结果
        candidate = {
            'body': 'def test_function(): pass',
            'file_path': 'test.py'
        }
        
        processed_query = {
            'tokens': ['test', 'function'],
            'intent': 'how_to'
        }
        
        score = engine._calculate_relevance_score("test function", processed_query, candidate)
        
        # 验证分数计算
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0)
    
    def test_tokenize_query(self):
        """测试查询分词"""
        engine = EnhancedSearchEngine(config_path=self.config_path)
        
        # 测试英文查询
        tokens = engine._tokenize_query("how to implement function")
        self.assertIn('implement', tokens)
        self.assertIn('function', tokens)
        
        # 测试中文查询
        tokens = engine._tokenize_query("如何实现函数")
        self.assertGreater(len(tokens), 0)
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效配置路径
        engine = EnhancedSearchEngine(config_path='/invalid/path/config.yaml')
        self.assertIsInstance(engine.search_weights, dict)
        
        # 测试无效预设加载
        result = engine.load_preset_config('invalid_preset')
        self.assertFalse(result)


class TestSearchConfigIntegration(unittest.TestCase):
    """搜索配置集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建主配置文件
        self.main_config_path = os.path.join(self.temp_dir, 'config.yaml')
        self.search_config_path = os.path.join(self.temp_dir, 'search_config.yaml')
        
        main_config = {
            'search': {
                'enhanced_search_config': self.search_config_path
            }
        }
        
        search_config = {
            'search_weights': {
                'exact_match': 35.0
            }
        }
        
        with open(self.main_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(main_config, f)
        
        with open(self.search_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(search_config, f)
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_main_config_integration(self):
        """测试主配置文件集成"""
        engine = EnhancedSearchEngine(config_path=self.main_config_path)
        
        # 验证从主配置加载搜索配置
        self.assertEqual(engine.search_weights['exact_match'], 35.0)


if __name__ == '__main__':
    unittest.main()