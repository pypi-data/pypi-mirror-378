#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语义搜索模块
实现基于 NLP 的语义匹配和规则重排功能
"""

import logging
import os
import re
import time
from typing import List, Dict, Any, Tuple, Optional
import yaml
import jieba
import jieba.analyse
from functools import lru_cache
try:
    from .database import CodeDatabase
except ImportError:
    from database import CodeDatabase


class SemanticSearchEngine:
    """语义搜索引擎"""
    
    def __init__(self, config_path: str = None):
        """
        初始化搜索引擎
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        # 确定配置文件路径
        if config_path is None:
            # 尝试多个可能的配置文件路径
            possible_paths = [
                os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml'),
                os.path.join(os.path.dirname(__file__), '..', 'config', 'search_config.yaml'),
                'config.yaml',
                'config/config.yaml'
            ]
            config_path = self._find_config_file(possible_paths)
        
        self.config = self._load_config(config_path)
        self.config_file = config_path  # 保存配置文件路径
        # 支持两种配置格式：新格式 database.file 和旧格式 db_file
        db_file = self.config.get('database', {}).get('file', self.config.get('db_file', 'search.db'))
        
        # 初始化数据库连接，增加错误处理
        try:
            self.db = CodeDatabase(db_file)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"数据库初始化失败: {e}")
            # 使用默认数据库文件作为备选
            self.db = CodeDatabase('search.db')
        
        # 初始化 spaCy（如果可用）
        self.nlp = None
        self._init_spacy()
        
        # 初始化中文分词
        self._init_jieba()
        
        # 编程相关关键词映射
        self.code_keywords = self._load_code_keywords()
        
        # 加载关键词权重
        self.keyword_weights = self._load_keyword_weights()
        
        # 搜索规则权重
        self.search_weights = {
            'exact_name_match': 10.0,      # 精确名称匹配
            'partial_name_match': 8.0,     # 部分名称匹配
            'docstring_match': 6.0,        # 文档字符串匹配
            'parameter_match': 5.0,        # 参数匹配
            'body_match': 3.0,             # 函数体匹配
            'semantic_similarity': 4.0,    # 语义相似度
            'keyword_bonus': 2.0,          # 关键词奖励
            'language_preference': 1.0     # 语言偏好
        }
        
        # 初始化缓存配置
        cache_config = self.config.get('cache', {})
        self.cache_enabled = cache_config.get('enabled', True)
        self.cache_size = cache_config.get('size', 128)
        self.cache_ttl = cache_config.get('ttl', 300)  # 5分钟TTL
        
        # 查询缓存 - 使用简单的字典缓存
        self._query_cache = {}
        self._cache_timestamps = {}
    
    def _find_config_file(self, possible_paths: List[str]) -> str:
        """
        查找可用的配置文件
        
        Args:
            possible_paths: 可能的配置文件路径列表
            
        Returns:
            找到的配置文件路径，如果都不存在则返回第一个路径
        """
        for path in possible_paths:
            if os.path.exists(path):
                return path
        # 如果都不存在，返回第一个路径（会在_load_config中处理）
        return possible_paths[0]
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"成功加载配置文件: {config_path}")
                return config
        except FileNotFoundError:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"配置文件 {config_path} 不存在，使用默认配置")
            return self._get_default_config()
        except yaml.YAMLError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"配置文件 {config_path} 格式错误: {e}，使用默认配置")
            return self._get_default_config()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"加载配置文件 {config_path} 时发生错误: {e}，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            默认配置字典
        """
        return {
            'database': {'file': 'search.db'},
            'search': {'max_results': 10},
            'repository': {'path': '.'},
            'spacy': {'model': 'zh_core_web_sm'},
            'jieba': {'enable': True},
            'cache': {
                'enabled': True,
                'size': 128,
                'ttl': 300
            }
        }
    
    def _init_spacy(self):
        """
        初始化 spaCy NLP 模型
        
        支持多种模型的降级处理：
        1. 优先使用配置文件中指定的模型
        2. 如果失败，尝试中文模型
        3. 如果仍失败，尝试英文模型
        4. 最后降级为无spaCy模式
        """
        spacy_config = self.config.get('spacy', {})
        model_candidates = [
            spacy_config.get('model', 'zh_core_web_sm'),  # 配置文件指定的模型
            'zh_core_web_sm',  # 中文模型
            'en_core_web_sm',  # 英文模型
        ]
        
        for model_name in model_candidates:
            try:
                import spacy
                self.nlp = spacy.load(model_name)
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"成功加载 spaCy 模型: {model_name}")
                return
            except (ImportError, OSError) as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"spaCy 模型 {model_name} 加载失败: {e}")
                continue
        
        # 所有模型都加载失败
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("所有 spaCy 模型加载失败，将使用基础文本匹配功能")
        logger.info("建议安装 spaCy 模型: python -m spacy download zh_core_web_sm")
    
    def _init_jieba(self):
        """
        初始化中文分词
        
        增强错误处理，确保即使jieba初始化失败也不影响基本功能
        """
        try:
            # 检查jieba是否可用
            if not self.config.get('jieba', {}).get('enable', True):
                import logging
                logger = logging.getLogger(__name__)
                logger.info("jieba 分词已在配置中禁用")
                return
            
            # 添加编程相关词汇到 jieba 词典
            programming_words = [
                '函数', '方法', '类', '对象', '变量', '参数', '返回值',
                '接口', '模块', '包', '库', '框架', '算法', '数据结构',
                '数据库', '查询', '更新', '删除', '插入', '连接',
                '用户', '登录', '注册', '权限', '认证', '授权',
                '支付', '订单', '商品', '购物车', '结算', '退款',
                'API', 'HTTP', 'JSON', 'XML', 'REST', 'GraphQL',
                '缓存', '队列', '消息', '事件', '异步', '同步'
            ]
            
            for word in programming_words:
                jieba.add_word(word)
            
            # 设置jieba日志级别，减少不必要的输出
            jieba.setLogLevel(20)  # INFO级别
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info("成功初始化中文分词，已添加编程词汇")
            
        except ImportError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"jieba 模块导入失败: {e}")
            logger.info("将使用基础分词功能")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"中文分词初始化失败: {e}")
            logger.info("将使用基础分词功能")
    
    def _load_code_keywords(self) -> Dict[str, List[str]]:
        """
        加载编程关键词，支持从配置文件动态加载
        
        优先级：
        1. 配置文件中的关键词
        2. 默认内置关键词
        
        Returns:
            关键词映射字典
        """
        # 尝试从配置文件加载
        keywords = self._load_keywords_from_config()
        
        # 如果配置文件加载失败，使用默认关键词
        if not keywords:
            keywords = self._get_default_keywords()
        
        # 合并用户自定义关键词（如果存在）
        custom_keywords = self._load_custom_keywords()
        if custom_keywords:
            keywords = self._merge_keywords(keywords, custom_keywords)
        
        return keywords
    
    def _load_keywords_from_config(self) -> Dict[str, List[str]]:
        """
        从配置文件加载关键词
        
        Returns:
            关键词映射字典
        """
        config_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'keywords.yaml'),
            os.path.join(os.path.expanduser('~'), '.local-code', 'keywords.yaml'),
            'keywords.yaml'
        ]
        
        for config_path in config_paths:
            try:
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f)
                    
                    # 转换配置格式为关键词映射
                    keywords = {}
                    for category, subcategories in config_data.items():
                        if category == 'keyword_weights':
                            continue  # 权重配置单独处理
                        
                        if isinstance(subcategories, dict):
                            for concept, terms in subcategories.items():
                                if isinstance(terms, list):
                                    keywords[concept] = terms
                    
                    if keywords:
                        logging.info(f"从配置文件加载关键词: {config_path}")
                        return keywords
                        
            except Exception as e:
                logging.warning(f"加载配置文件失败 {config_path}: {e}")
                continue
        
        return {}
    
    def _load_custom_keywords(self) -> Dict[str, List[str]]:
        """
        加载用户自定义关键词
        
        Returns:
            自定义关键词映射字典
        """
        custom_paths = [
            os.path.join(os.path.expanduser('~'), '.local-code', 'custom_keywords.yaml'),
            'custom_keywords.yaml'
        ]
        
        for custom_path in custom_paths:
            try:
                if os.path.exists(custom_path):
                    with open(custom_path, 'r', encoding='utf-8') as f:
                        custom_data = yaml.safe_load(f)
                    
                    if isinstance(custom_data, dict):
                        logging.info(f"加载自定义关键词: {custom_path}")
                        return custom_data
                        
            except Exception as e:
                logging.warning(f"加载自定义关键词失败 {custom_path}: {e}")
                continue
        
        return {}
    
    def _merge_keywords(self, base_keywords: Dict[str, List[str]], 
                       custom_keywords: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        合并基础关键词和自定义关键词
        
        Args:
            base_keywords: 基础关键词
            custom_keywords: 自定义关键词
            
        Returns:
            合并后的关键词字典
        """
        merged = base_keywords.copy()
        
        for concept, terms in custom_keywords.items():
            if concept in merged:
                # 合并现有概念的关键词，去重
                merged[concept] = list(set(merged[concept] + terms))
            else:
                # 添加新概念
                merged[concept] = terms
        
        return merged
    
    def _load_keyword_weights(self) -> Dict[str, float]:
        """
        加载关键词权重配置
        
        Returns:
            关键词权重字典
        """
        weights = {}
        
        # 尝试从配置文件加载权重
        config_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'keywords.yaml'),
            os.path.join(os.path.expanduser('~'), '.local-code', 'keywords.yaml'),
            'keywords.yaml'
        ]
        
        for config_path in config_paths:
            try:
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f)
                    
                    # 提取权重配置
                    weight_config = config_data.get('keyword_weights', {})
                    if weight_config:
                        # 处理不同优先级的权重
                        high_priority = weight_config.get('high_priority', [])
                        medium_priority = weight_config.get('medium_priority', [])
                        low_priority = weight_config.get('low_priority', [])
                        
                        # 分配权重
                        for keyword in high_priority:
                            weights[keyword.lower()] = 3.0
                        for keyword in medium_priority:
                            weights[keyword.lower()] = 2.0
                        for keyword in low_priority:
                            weights[keyword.lower()] = 1.0
                        
                        logging.info(f"从配置文件加载关键词权重: {config_path}")
                        break
                        
            except Exception as e:
                logging.warning(f"加载权重配置失败 {config_path}: {e}")
                continue
        
        # 如果没有配置文件，使用默认权重
        if not weights:
            weights = self._get_default_keyword_weights()
        
        return weights
    
    def _get_default_keyword_weights(self) -> Dict[str, float]:
        """
        获取默认关键词权重
        
        Returns:
            默认权重字典
        """
        return {
            # 高优先级关键词 (3.0)
            'function': 3.0,
            'class': 3.0,
            'api': 3.0,
            'database': 3.0,
            'user': 3.0,
            'login': 3.0,
            'auth': 3.0,
            'payment': 3.0,
            'order': 3.0,
            'query': 3.0,
            'search': 3.0,
            
            # 中等优先级关键词 (2.0)
            'config': 2.0,
            'log': 2.0,
            'test': 2.0,
            'cache': 2.0,
            'service': 2.0,
            'component': 2.0,
            'state': 2.0,
            'request': 2.0,
            'response': 2.0,
            'error': 2.0,
            'exception': 2.0,
            
            # 低优先级关键词 (1.0)
            'comment': 1.0,
            'debug': 1.0,
            'temp': 1.0,
            'util': 1.0,
            'helper': 1.0,
            'common': 1.0,
            'base': 1.0,
            'abstract': 1.0,
            'interface': 1.0,
            'type': 1.0
        }
    
    def get_keyword_weight(self, keyword: str) -> float:
        """
        获取关键词权重
        
        Args:
            keyword: 关键词
            
        Returns:
            权重值，默认为1.0
        """
        return self.keyword_weights.get(keyword.lower(), 1.0)
    
    def _get_default_keywords(self) -> Dict[str, List[str]]:
        """
        加载编程相关关键词映射
        
        包含现代软件开发的各个技术领域和编程概念，
        支持中英文术语，覆盖前端、后端、云原生、AI/ML等领域
        
        Returns:
            关键词映射字典
        """
        return {
            # 数据库操作
            'database': ['db', 'database', 'sql', 'query', 'select', 'insert', 'update', 'delete', 
                        'mysql', 'postgresql', 'sqlite', 'mongodb', 'redis', 'elasticsearch',
                        '数据库', '查询', '插入', '更新', '删除', '索引', '事务'],
            'crud': ['create', 'read', 'update', 'delete', 'add', 'get', 'set', 'remove',
                    '创建', '读取', '更新', '删除', '增加', '获取', '设置', '移除'],
            
            # 用户相关
            'user': ['user', 'account', 'profile', 'login', 'register', 'auth', 'authentication',
                    'oauth', 'jwt', 'token', 'session', 'cookie',
                    '用户', '账户', '登录', '注册', '认证', '授权', '会话'],
            'permission': ['permission', 'role', 'access', 'authorize', 'grant', 'deny',
                          'rbac', 'acl', 'security', '权限', '角色', '访问', '安全'],
            
            # 业务逻辑
            'payment': ['pay', 'payment', 'charge', 'bill', 'invoice', 'transaction',
                       'stripe', 'paypal', 'alipay', 'wechat', '支付', '账单', '交易'],
            'order': ['order', 'purchase', 'buy', 'sell', 'cart', 'checkout',
                     '订单', '购买', '销售', '购物车', '结账'],
            'product': ['product', 'item', 'goods', 'catalog', 'inventory', 'sku',
                       '产品', '商品', '库存', '目录'],
            
            # 前端技术
            'frontend': ['react', 'vue', 'angular', 'svelte', 'nextjs', 'nuxt',
                        'dom', 'html', 'css', 'javascript', 'typescript',
                        'jsx', 'tsx', 'component', 'hook', 'state',
                        '前端', '组件', '状态', '样式', '脚本'],
            'ui': ['ui', 'ux', 'design', 'layout', 'responsive', 'mobile',
                  'bootstrap', 'tailwind', 'material', 'antd',
                  '界面', '设计', '布局', '响应式', '移动端'],
            
            # 后端框架
            'backend': ['spring', 'django', 'flask', 'fastapi', 'express', 'koa',
                       'gin', 'echo', 'rails', 'laravel', 'symfony',
                       '后端', '框架', '服务器', '接口'],
            'microservice': ['microservice', 'service', 'api', 'gateway', 'mesh',
                           'consul', 'eureka', 'nacos', '微服务', '服务网格'],
            
            # 云原生和运维
            'cloud': ['docker', 'kubernetes', 'k8s', 'container', 'pod', 'deployment',
                     'service', 'ingress', 'configmap', 'secret',
                     'aws', 'azure', 'gcp', 'aliyun', 'tencent',
                     '容器', '部署', '云平台', '集群'],
            'devops': ['ci', 'cd', 'pipeline', 'jenkins', 'gitlab', 'github',
                      'terraform', 'ansible', 'helm', 'monitoring',
                      '持续集成', '持续部署', '流水线', '监控'],
            
            # 数据处理
            'data': ['json', 'xml', 'csv', 'yaml', 'protobuf', 'avro',
                    'serialize', 'deserialize', 'parse', 'format',
                    'etl', 'pipeline', 'stream', 'batch',
                    '数据', '序列化', '解析', '格式化', '流处理'],
            'cache': ['cache', 'redis', 'memcached', 'cdn', 'buffer',
                     'lru', 'ttl', 'expire', '缓存', '过期'],
            
            # 网络和通信
            'network': ['http', 'https', 'rest', 'graphql', 'grpc', 'websocket',
                       'tcp', 'udp', 'ssl', 'tls', 'cors', 'proxy',
                       '网络', '协议', '通信', '代理'],
            'message': ['mq', 'kafka', 'rabbitmq', 'redis', 'pulsar',
                       'queue', 'topic', 'producer', 'consumer',
                       '消息队列', '生产者', '消费者'],
            
            # 测试相关
            'testing': ['test', 'unit', 'integration', 'e2e', 'mock', 'stub',
                       'jest', 'pytest', 'junit', 'selenium', 'cypress',
                       '测试', '单元测试', '集成测试', '端到端', '模拟'],
            
            # 算法和数据结构
            'algorithm': ['sort', 'search', 'tree', 'graph', 'hash', 'queue',
                         'stack', 'heap', 'array', 'list', 'map', 'set',
                         'binary', 'recursive', 'dynamic', 'greedy',
                         '算法', '排序', '搜索', '树', '图', '哈希', '队列', '栈'],
            'performance': ['optimize', 'performance', 'benchmark', 'profile',
                          'memory', 'cpu', 'latency', 'throughput',
                          '优化', '性能', '基准测试', '内存', '延迟', '吞吐量'],
            
            # 编程语言特性
            'python': ['decorator', 'generator', 'comprehension', 'lambda',
                      'async', 'await', 'yield', 'with', 'import',
                      '装饰器', '生成器', '推导式', '异步'],
            'javascript': ['closure', 'prototype', 'hoisting', 'promise',
                          'callback', 'arrow', 'destructuring', 'spread',
                          '闭包', '原型', '提升', '回调', '箭头函数'],
            'java': ['annotation', 'reflection', 'generic', 'stream',
                    'lambda', 'interface', 'abstract', 'static',
                    '注解', '反射', '泛型', '流', '接口', '抽象'],
            'go': ['goroutine', 'channel', 'interface', 'struct',
                  'pointer', 'slice', 'map', 'defer',
                  '协程', '通道', '接口', '结构体', '指针'],
            
            # AI/ML相关
            'ai': ['ai', 'ml', 'deep', 'learning', 'neural', 'network',
                  'tensorflow', 'pytorch', 'sklearn', 'pandas', 'numpy',
                  'model', 'train', 'predict', 'feature', 'dataset',
                  '人工智能', '机器学习', '深度学习', '神经网络', '模型', '训练', '预测'],
            
            # 安全相关
            'security': ['encrypt', 'decrypt', 'hash', 'salt', 'bcrypt',
                        'oauth', 'jwt', 'csrf', 'xss', 'sql injection',
                        'https', 'certificate', 'firewall',
                        '加密', '解密', '哈希', '安全', '防火墙', '证书'],
            
            # 技术概念
            'api': ['api', 'endpoint', 'route', 'handler', 'controller',
                   'middleware', 'interceptor', 'filter',
                   '接口', '端点', '路由', '处理器', '控制器', '中间件'],
            'service': ['service', 'business', 'logic', 'process', 'workflow',
                       'domain', 'entity', 'repository', 'factory',
                       '服务', '业务', '逻辑', '流程', '工作流', '领域', '实体'],
            'util': ['util', 'helper', 'tool', 'common', 'shared', 'library',
                    'module', 'package', 'dependency',
                    '工具', '帮助', '公共', '共享', '库', '模块', '包', '依赖'],
            
            # 状态和操作
            'status': ['status', 'state', 'condition', 'flag', 'active', 'inactive',
                      'enabled', 'disabled', 'pending', 'running', 'stopped',
                      '状态', '条件', '标志', '激活', '禁用', '运行', '停止'],
            'validation': ['valid', 'validate', 'check', 'verify', 'confirm',
                          'sanitize', 'escape', 'filter', 'rule',
                          '验证', '检查', '确认', '过滤', '规则'],
            'format': ['format', 'parse', 'convert', 'transform', 'serialize',
                      'encode', 'decode', 'compress', 'decompress',
                      '格式化', '解析', '转换', '序列化', '编码', '解码', '压缩'],
            
            # 错误处理
            'error': ['error', 'exception', 'try', 'catch', 'finally',
                     'throw', 'raise', 'handle', 'retry', 'fallback',
                     '错误', '异常', '捕获', '处理', '重试', '降级'],
            
            # 配置和环境
            'config': ['config', 'setting', 'environment', 'variable',
                      'property', 'parameter', 'option', 'flag',
                      '配置', '设置', '环境', '变量', '参数', '选项'],
            
            # 日志和监控
            'logging': ['log', 'logger', 'debug', 'info', 'warn', 'error',
                       'trace', 'audit', 'metric', 'monitor',
                       '日志', '调试', '信息', '警告', '错误', '跟踪', '监控']
        }
    
    def search(self, query: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        执行语义搜索
        
        Args:
            query: 搜索查询
            limit: 结果限制
            
        Returns:
            搜索结果列表
        """
        if limit is None:
            limit = self.config.get('max_results', 10)
        
        # 检查缓存
        cache_key = f"{query}:{limit}"
        if self.cache_enabled and self._is_cache_valid(cache_key):
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"缓存命中: {query}")
            return self._query_cache[cache_key]
        
        start_time = time.time()
        
        # 预处理查询
        processed_query = self._preprocess_query(query)
        
        # 从数据库获取候选结果
        candidates = self._get_candidates(processed_query, limit * 3)  # 获取更多候选结果
        
        # 计算相关性分数并重排
        scored_results = self._score_and_rank(query, processed_query, candidates)
        
        # 限制结果数量
        final_results = scored_results[:limit]
        
        # 记录搜索历史
        search_time = time.time() - start_time
        self.db.save_search_history(query, len(final_results), search_time)
        
        # 缓存结果
        if self.cache_enabled:
            self._cache_result(cache_key, final_results)
        
        return final_results
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        检查缓存是否有效
        
        Args:
            cache_key: 缓存键
            
        Returns:
            缓存是否有效
        """
        if cache_key not in self._query_cache:
            return False
        
        # 检查TTL
        if cache_key in self._cache_timestamps:
            cache_time = self._cache_timestamps[cache_key]
            if time.time() - cache_time > self.cache_ttl:
                # 缓存过期，清理
                del self._query_cache[cache_key]
                del self._cache_timestamps[cache_key]
                return False
        
        return True
    
    def _cache_result(self, cache_key: str, result: List[Dict[str, Any]]):
        """
        缓存搜索结果
        
        Args:
            cache_key: 缓存键
            result: 搜索结果
        """
        # 检查缓存大小限制
        if len(self._query_cache) >= self.cache_size:
            # 清理最旧的缓存项
            oldest_key = min(self._cache_timestamps.keys(), 
                           key=lambda k: self._cache_timestamps[k])
            del self._query_cache[oldest_key]
            del self._cache_timestamps[oldest_key]
        
        # 添加到缓存
        self._query_cache[cache_key] = result
        self._cache_timestamps[cache_key] = time.time()
    
    def clear_cache(self):
        """
        清空缓存
        """
        self._query_cache.clear()
        self._cache_timestamps.clear()
        import logging
        logger = logging.getLogger(__name__)
        logger.info("搜索缓存已清空")
    
    def _preprocess_query(self, query: str) -> Dict[str, Any]:
        """
        预处理搜索查询
        
        Args:
            query: 原始查询
            
        Returns:
            处理后的查询信息
        """
        # 基础清理
        cleaned_query = query.strip().lower()
        
        # 中文分词
        chinese_tokens = list(jieba.cut(query))
        
        # 英文分词（简单空格分割）
        english_tokens = re.findall(r'\b\w+\b', cleaned_query)
        
        # 提取关键词
        keywords = jieba.analyse.extract_tags(query, topK=10, withWeight=True)
        
        # 检测查询意图
        intent = self._detect_intent(cleaned_query)
        
        # 提取编程概念
        concepts = self._extract_programming_concepts(cleaned_query)
        
        return {
            'original': query,
            'cleaned': cleaned_query,
            'chinese_tokens': chinese_tokens,
            'english_tokens': english_tokens,
            'keywords': keywords,
            'intent': intent,
            'concepts': concepts
        }
    
    def _detect_intent(self, query: str) -> str:
        """
        检测查询意图
        
        Args:
            query: 查询字符串
            
        Returns:
            意图类型
        """
        # 定义意图模式
        intent_patterns = {
            'find_function': [
                r'(哪里|where).*?(函数|function|方法|method)',
                r'(找|find|search).*?(函数|function)',
                r'(如何|how).*?(实现|implement|做|do)'
            ],
            'find_class': [
                r'(哪里|where).*?(类|class)',
                r'(找|find|search).*?(类|class)'
            ],
            'update_operation': [
                r'(更新|update|修改|modify|改|change).*?(状态|status|数据|data)',
                r'(设置|set|置为|mark as)'
            ],
            'create_operation': [
                r'(创建|create|新建|new|添加|add)',
                r'(生成|generate|构建|build)'
            ],
            'delete_operation': [
                r'(删除|delete|移除|remove|清除|clear)'
            ],
            'query_operation': [
                r'(查询|query|获取|get|取|fetch|检索|retrieve)'
            ]
        }
        
        for intent, patterns in intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return intent
        
        return 'general'
    
    def _extract_programming_concepts(self, query: str) -> List[str]:
        """
        提取编程概念，支持中英文术语匹配
        
        增强功能：
        1. 支持中英文关键词匹配
        2. 支持模糊匹配和词干匹配
        3. 支持同义词扩展
        
        Args:
            query: 查询字符串
            
        Returns:
            概念列表
        """
        concepts = []
        query_lower = query.lower()
        
        # 创建中英文术语映射
        term_mappings = self._build_term_mappings()
        
        for concept, keywords in self.code_keywords.items():
            concept_matched = False
            
            # 直接关键词匹配
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    concepts.append(concept)
                    concept_matched = True
                    break
            
            # 如果直接匹配失败，尝试同义词和术语映射匹配
            if not concept_matched:
                for keyword in keywords:
                    # 检查是否有对应的中英文术语
                    mapped_terms = term_mappings.get(keyword.lower(), [])
                    for term in mapped_terms:
                        if term in query_lower:
                            concepts.append(concept)
                            concept_matched = True
                            break
                    if concept_matched:
                        break
        
        return list(set(concepts))  # 去重
    
    def _build_term_mappings(self) -> Dict[str, List[str]]:
        """
        构建中英文编程术语映射表
        
        Returns:
            术语映射字典
        """
        return {
            # 基础编程概念
            'function': ['函数', 'method', '方法', 'func', 'def'],
            '函数': ['function', 'method', 'func', 'def'],
            'class': ['类', 'object', '对象', 'cls'],
            '类': ['class', 'object', 'cls'],
            'variable': ['变量', 'var', 'let', 'const'],
            '变量': ['variable', 'var', 'let', 'const'],
            'interface': ['接口', 'contract', '契约'],
            '接口': ['interface', 'contract'],
            'module': ['模块', 'package', '包', 'library', '库'],
            '模块': ['module', 'package', 'library'],
            
            # 数据库相关
            'database': ['数据库', 'db', '库'],
            '数据库': ['database', 'db'],
            'query': ['查询', 'select', '选择'],
            '查询': ['query', 'select'],
            'insert': ['插入', 'add', '添加', '新增'],
            '插入': ['insert', 'add'],
            'update': ['更新', 'modify', '修改'],
            '更新': ['update', 'modify'],
            'delete': ['删除', 'remove', '移除'],
            '删除': ['delete', 'remove'],
            
            # 用户认证
            'login': ['登录', 'signin', '登入'],
            '登录': ['login', 'signin'],
            'register': ['注册', 'signup', '注册'],
            '注册': ['register', 'signup'],
            'auth': ['认证', 'authentication', '验证'],
            '认证': ['auth', 'authentication'],
            'permission': ['权限', 'access', '访问'],
            '权限': ['permission', 'access'],
            
            # 业务逻辑
            'payment': ['支付', 'pay', '付款'],
            '支付': ['payment', 'pay'],
            'order': ['订单', 'purchase', '购买'],
            '订单': ['order', 'purchase'],
            'user': ['用户', 'customer', '客户'],
            '用户': ['user', 'customer'],
            
            # 技术概念
            'api': ['接口', 'endpoint', '端点'],
            'service': ['服务', 'business', '业务'],
            '服务': ['service', 'business'],
            'config': ['配置', 'setting', '设置'],
            '配置': ['config', 'setting'],
            'log': ['日志', 'logger', '记录'],
            '日志': ['log', 'logger'],
            'error': ['错误', 'exception', '异常'],
            '错误': ['error', 'exception'],
            '异常': ['error', 'exception'],
            'test': ['测试', 'testing', '检测'],
            '测试': ['test', 'testing'],
            
            # 前端相关
            'component': ['组件', 'widget', '控件'],
            '组件': ['component', 'widget'],
            'state': ['状态', 'status', '状况'],
            '状态': ['state', 'status'],
            'style': ['样式', 'css', '风格'],
            '样式': ['style', 'css'],
            
            # 算法相关
            'sort': ['排序', 'order', '排列'],
            '排序': ['sort', 'order'],
            'search': ['搜索', 'find', '查找'],
            '搜索': ['search', 'find'],
            'algorithm': ['算法', 'algo', '算法'],
            '算法': ['algorithm', 'algo'],
            
            # 性能相关
            'optimize': ['优化', 'performance', '性能'],
            '优化': ['optimize', 'performance'],
            '性能': ['optimize', 'performance'],
            'cache': ['缓存', 'buffer', '缓冲'],
            '缓存': ['cache', 'buffer'],
            
            # 网络相关
            'http': ['网络', 'web', '网页'],
            'request': ['请求', 'req', '要求'],
            '请求': ['request', 'req'],
            'response': ['响应', 'resp', '回应'],
            '响应': ['response', 'resp'],
            
            # 数据处理
            'json': ['数据', 'data', '信息'],
            'parse': ['解析', 'analyze', '分析'],
            '解析': ['parse', 'analyze'],
            'format': ['格式', 'structure', '结构'],
            '格式': ['format', 'structure'],
            
            # 安全相关
            'encrypt': ['加密', 'secure', '安全'],
            '加密': ['encrypt', 'secure'],
            'hash': ['哈希', 'digest', '摘要'],
            '哈希': ['hash', 'digest'],
            
            # 部署运维
            'deploy': ['部署', 'release', '发布'],
            '部署': ['deploy', 'release'],
            'monitor': ['监控', 'watch', '监视'],
            '监控': ['monitor', 'watch'],
            'docker': ['容器', 'container', '集装箱'],
            '容器': ['docker', 'container']
        }
    
    def _get_candidates(self, processed_query: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """
        从数据库获取候选结果
        
        优化策略：
        1. 减少重复查询
        2. 使用批量查询
        3. 智能搜索词选择
        
        Args:
            processed_query: 处理后的查询
            limit: 结果限制
            
        Returns:
            候选结果列表
        """
        candidates = []
        seen_ids = set()  # 用于去重
        
        # 智能选择搜索词，避免重复和无效查询
        search_terms = self._select_search_terms(processed_query)
        
        # 批量查询优化
        try:
            # 尝试使用批量搜索（如果数据库支持）
            if hasattr(self.db, 'batch_search'):
                batch_results = self.db.batch_search(search_terms, limit)
                for results in batch_results:
                    for result in results:
                        result_id = f"{result.get('file_path', '')}:{result.get('name', '')}"
                        if result_id not in seen_ids:
                            candidates.append(result)
                            seen_ids.add(result_id)
            else:
                # 传统单次查询方式
                for term in search_terms:
                    if term.strip():
                        results = self.db.search_all(term, limit)
                        for result in results:
                            result_id = f"{result.get('file_path', '')}:{result.get('name', '')}"
                            if result_id not in seen_ids:
                                candidates.append(result)
                                seen_ids.add(result_id)
                        
                        # 如果已经有足够的候选结果，提前退出
                        if len(candidates) >= limit * 2:
                            break
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"数据库查询失败: {e}")
            # 降级到基础查询
            try:
                results = self.db.search_all(processed_query['cleaned'], limit)
                candidates.extend(results)
            except Exception as fallback_e:
                logger.error(f"降级查询也失败: {fallback_e}")
                return []
        
        return candidates
    
    def _select_search_terms(self, processed_query: Dict[str, Any]) -> List[str]:
        """
        智能选择搜索词，避免重复和无效查询
        
        Args:
            processed_query: 处理后的查询
            
        Returns:
            优化后的搜索词列表
        """
        terms = []
        
        # 1. 原始查询（最重要）
        if processed_query['original'].strip():
            terms.append(processed_query['original'])
        
        # 2. 清理后的查询（如果与原始不同）
        cleaned = processed_query['cleaned']
        if cleaned.strip() and cleaned != processed_query['original']:
            terms.append(cleaned)
        
        # 3. 英文词汇（如果有意义的词汇）
        english_tokens = [token for token in processed_query['english_tokens'] 
                         if len(token) > 2 and token.isalpha()]
        if english_tokens:
            english_phrase = ' '.join(english_tokens[:3])  # 最多3个词
            if english_phrase not in terms:
                terms.append(english_phrase)
        
        # 4. 中文词汇（如果有意义的词汇）
        chinese_tokens = [token for token in processed_query['chinese_tokens'] 
                         if len(token) > 1]
        if chinese_tokens:
            chinese_phrase = ' '.join(chinese_tokens[:3])  # 最多3个词
            if chinese_phrase not in terms:
                terms.append(chinese_phrase)
        
        # 5. 编程概念（如果识别到）
        concepts = processed_query.get('concepts', [])
        for concept in concepts[:2]:  # 最多2个概念
            if concept not in terms:
                terms.append(concept)
        
        # 去重并限制数量（最多5个搜索词）
        unique_terms = []
        for term in terms:
            if term not in unique_terms and len(unique_terms) < 5:
                unique_terms.append(term)
        
        return unique_terms
        
        # 去重候选结果
        seen_ids = set()
        unique_candidates = []
        
        for candidate in candidates:
            key = (candidate['type'], candidate['id'])
            if key not in seen_ids:
                seen_ids.add(key)
                unique_candidates.append(candidate)
        
        return unique_candidates
    
    def _score_and_rank(self, original_query: str, processed_query: Dict[str, Any], 
                       candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        计算相关性分数并排序
        
        Args:
            original_query: 原始查询
            processed_query: 处理后的查询
            candidates: 候选结果
            
        Returns:
            排序后的结果列表
        """
        scored_results = []
        
        for candidate in candidates:
            score = self._calculate_relevance_score(original_query, processed_query, candidate)
            candidate['relevance_score'] = score
            candidate['score_breakdown'] = score  # 用于调试
            scored_results.append(candidate)
        
        # 按分数排序
        scored_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return scored_results
    
    def _calculate_relevance_score(self, original_query: str, processed_query: Dict[str, Any], 
                                 candidate: Dict[str, Any]) -> float:
        """
        计算单个候选结果的相关性分数
        
        Args:
            original_query: 原始查询
            processed_query: 处理后的查询
            candidate: 候选结果
            
        Returns:
            相关性分数
        """
        total_score = 0.0
        
        # 获取候选结果的文本内容
        candidate_texts = self._extract_candidate_texts(candidate)
        
        # 1. 精确名称匹配
        if self._exact_match(processed_query['cleaned'], candidate['name'].lower()):
            total_score += self.search_weights['exact_name_match']
        
        # 2. 部分名称匹配
        elif self._partial_match(processed_query['cleaned'], candidate['name'].lower()):
            total_score += self.search_weights['partial_name_match']
        
        # 3. 文档字符串匹配
        if candidate.get('docstring'):
            doc_score = self._text_similarity(processed_query['cleaned'], 
                                            candidate['docstring'].lower())
            total_score += doc_score * self.search_weights['docstring_match']
        
        # 4. 参数匹配（仅对函数）
        if candidate['type'] == 'function' and candidate.get('parameters'):
            param_text = ' '.join(candidate['parameters']).lower()
            param_score = self._text_similarity(processed_query['cleaned'], param_text)
            total_score += param_score * self.search_weights['parameter_match']
        
        # 5. 函数体匹配
        if candidate.get('body'):
            body_score = self._text_similarity(processed_query['cleaned'], 
                                             candidate['body'].lower())
            total_score += body_score * self.search_weights['body_match']
        
        # 6. 语义相似度（如果 spaCy 可用）
        if self.nlp:
            semantic_score = self._semantic_similarity(original_query, candidate_texts)
            total_score += semantic_score * self.search_weights['semantic_similarity']
        
        # 7. 关键词奖励
        keyword_score = self._keyword_bonus(processed_query, candidate)
        total_score += keyword_score * self.search_weights['keyword_bonus']
        
        # 8. 语言偏好（可配置）
        lang_score = self._language_preference(candidate['language'])
        total_score += lang_score * self.search_weights['language_preference']
        
        return total_score
    
    def _extract_candidate_texts(self, candidate: Dict[str, Any]) -> str:
        """
        提取候选结果的所有文本内容
        
        Args:
            candidate: 候选结果
            
        Returns:
            合并的文本内容
        """
        texts = [candidate['name']]
        
        if candidate.get('docstring'):
            texts.append(candidate['docstring'])
        
        if candidate.get('parameters'):
            texts.extend(candidate['parameters'])
        
        return ' '.join(texts)
    
    def _exact_match(self, query: str, text: str) -> bool:
        """
        检查精确匹配
        
        Args:
            query: 查询字符串
            text: 目标文本
            
        Returns:
            是否精确匹配
        """
        return query == text or query in text.split('_') or query in text.split('.')
    
    def _partial_match(self, query: str, text: str) -> bool:
        """
        检查部分匹配
        
        Args:
            query: 查询字符串
            text: 目标文本
            
        Returns:
            是否部分匹配
        """
        return query in text or any(word in text for word in query.split())
    
    def _text_similarity(self, query: str, text: str) -> float:
        """
        计算文本相似度
        
        Args:
            query: 查询字符串
            text: 目标文本
            
        Returns:
            相似度分数 (0-1)
        """
        if not text:
            return 0.0
        
        # 简单的词汇重叠相似度
        query_words = set(query.split())
        text_words = set(text.split())
        
        if not query_words or not text_words:
            return 0.0
        
        intersection = query_words.intersection(text_words)
        union = query_words.union(text_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _semantic_similarity(self, query: str, text: str) -> float:
        """
        计算语义相似度（使用 spaCy）
        
        Args:
            query: 查询字符串
            text: 目标文本
            
        Returns:
            语义相似度分数 (0-1)
        """
        if not self.nlp or not text:
            return 0.0
        
        try:
            query_doc = self.nlp(query)
            text_doc = self.nlp(text)
            
            return query_doc.similarity(text_doc)
        except Exception:
            return 0.0
    
    def _keyword_bonus(self, processed_query: Dict[str, Any], candidate: Dict[str, Any]) -> float:
        """
        计算关键词奖励分数（增强版，支持权重系统）
        
        Args:
            processed_query: 处理后的查询
            candidate: 候选结果
            
        Returns:
            奖励分数
        """
        bonus = 0.0
        
        # 检查编程概念匹配（使用权重系统）
        for concept in processed_query['concepts']:
            weight = self.get_keyword_weight(concept)
            
            # 在名称中匹配
            if concept in candidate['name'].lower():
                bonus += weight * 2.0  # 名称匹配权重更高
            
            # 在文档字符串中匹配
            if candidate.get('docstring') and concept in candidate['docstring'].lower():
                bonus += weight * 1.0
            
            # 在参数中匹配
            if candidate.get('parameters'):
                for param in candidate['parameters']:
                    if concept in param.lower():
                        bonus += weight * 0.5
            
            # 在文件路径中匹配
            if candidate.get('file_path') and concept in candidate['file_path'].lower():
                bonus += weight * 0.3
        
        # 检查意图匹配（使用权重系统）
        intent = processed_query['intent']
        intent_weight = self.get_keyword_weight(intent)
        
        if intent == 'update_operation' and 'update' in candidate['name'].lower():
            bonus += intent_weight * 2.0
        elif intent == 'find_function' and candidate['type'] == 'function':
            bonus += intent_weight * 1.5
        elif intent == 'find_class' and candidate['type'] == 'class':
            bonus += intent_weight * 1.5
        elif intent == 'database_operation':
            db_keywords = ['query', 'select', 'insert', 'update', 'delete', 'database', 'db']
            for keyword in db_keywords:
                if keyword in candidate['name'].lower():
                    bonus += self.get_keyword_weight(keyword) * 1.0
        elif intent == 'user_operation':
            user_keywords = ['user', 'login', 'auth', 'register', 'profile']
            for keyword in user_keywords:
                if keyword in candidate['name'].lower():
                    bonus += self.get_keyword_weight(keyword) * 1.0
        
        # 检查特殊关键词组合
        query_text = processed_query['cleaned'].lower()
        candidate_text = (candidate['name'] + ' ' + 
                         (candidate.get('docstring', '') or '')).lower()
        
        # API相关
        if any(word in query_text for word in ['api', 'endpoint', 'route']):
            if any(word in candidate_text for word in ['api', 'endpoint', 'route', 'handler']):
                bonus += self.get_keyword_weight('api') * 1.5
        
        # 测试相关
        if any(word in query_text for word in ['test', 'testing', '测试']):
            if any(word in candidate_text for word in ['test', 'spec', 'mock']):
                bonus += self.get_keyword_weight('test') * 1.0
        
        # 配置相关
        if any(word in query_text for word in ['config', 'setting', '配置']):
            if any(word in candidate_text for word in ['config', 'setting', 'option']):
                bonus += self.get_keyword_weight('config') * 1.0
        
        return bonus
    
    def _language_preference(self, language: str) -> float:
        """
        计算语言偏好分数
        
        Args:
            language: 编程语言
            
        Returns:
            偏好分数
        """
        # 可以根据项目需要调整语言偏好
        preferences = {
            'python': 1.0,
            'javascript': 0.8,
            'java': 0.6
        }
        
        return preferences.get(language, 0.5)
    
    def auto_extract_keywords_from_codebase(self, update_config: bool = False) -> Dict[str, List[str]]:
        """
        基于代码库内容自动提取关键词
        
        Args:
            update_config: 是否更新配置文件
            
        Returns:
            提取的关键词字典
        """
        extracted_keywords = {}
        
        try:
            # 从数据库获取所有代码元素
            cursor = self.db.conn.cursor()
            
            # 获取函数名和类名
            cursor.execute("""
                SELECT f.name, 'function' as type, f.docstring, files.file_path 
                FROM functions f
                JOIN files ON f.file_id = files.id
                UNION ALL
                SELECT c.name, 'class' as type, '' as docstring, files.file_path 
                FROM classes c
                JOIN files ON c.file_id = files.id
            """)
            
            elements = cursor.fetchall()
            
            # 分析函数名和类名模式
            function_keywords = self._extract_keywords_from_names(
                [elem[0] for elem in elements if elem[1] == 'function']
            )
            class_keywords = self._extract_keywords_from_names(
                [elem[0] for elem in elements if elem[1] == 'class']
            )
            
            # 分析文档字符串
            docstring_keywords = self._extract_keywords_from_docstrings(
                [elem[2] for elem in elements if elem[2]]
            )
            
            # 获取文件路径
            cursor.execute("SELECT file_path FROM files")
            file_paths = [row[0] for row in cursor.fetchall()]
            
            # 分析文件路径
            path_keywords = self._extract_keywords_from_paths(file_paths)
            
            # 合并提取的关键词
            extracted_keywords = {
                'auto_functions': function_keywords,
                'auto_classes': class_keywords,
                'auto_concepts': docstring_keywords,
                'auto_modules': path_keywords
            }
            
            # 如果需要，更新配置文件
            if update_config:
                self._update_keywords_config(extracted_keywords)
            
            logging.info(f"自动提取关键词完成，共提取 {sum(len(v) for v in extracted_keywords.values())} 个关键词")
                
        except Exception as e:
            logging.error(f"自动提取关键词失败: {e}")
        
        return extracted_keywords
    
    def _extract_keywords_from_names(self, names: List[str]) -> List[str]:
        """
        从函数名和类名中提取关键词
        
        Args:
            names: 名称列表
            
        Returns:
            提取的关键词列表
        """
        keywords = set()
        
        for name in names:
            if not name:
                continue
                
            # 处理驼峰命名和下划线命名
            words = re.findall(r'[A-Z][a-z]*|[a-z]+|[0-9]+', name)
            words.extend(name.split('_'))
            
            for word in words:
                word = word.lower().strip()
                if len(word) > 2 and word.isalpha():  # 过滤短词和数字
                    keywords.add(word)
        
        # 按频率排序，返回前50个
        return list(keywords)[:50]
    
    def _extract_keywords_from_docstrings(self, docstrings: List[str]) -> List[str]:
        """
        从文档字符串中提取关键词
        
        Args:
            docstrings: 文档字符串列表
            
        Returns:
            提取的关键词列表
        """
        keywords = set()
        
        # 合并所有文档字符串
        combined_text = ' '.join(filter(None, docstrings))
        
        if combined_text:
            try:
                # 使用jieba提取关键词
                jieba_keywords = jieba.analyse.extract_tags(
                    combined_text, 
                    topK=30,
                    withWeight=False,
                    allowPOS=('n', 'v', 'vn', 'nr', 'ns', 'nt', 'nz')
                )
                keywords.update(jieba_keywords)
                
                # 提取英文关键词
                english_words = re.findall(r'\b[a-zA-Z]{3,}\b', combined_text)
                for word in english_words:
                    word = word.lower()
                    if word not in {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}:
                        keywords.add(word)
                        
            except Exception as e:
                logging.warning(f"提取文档字符串关键词失败: {e}")
        
        return list(keywords)[:30]
    
    def _extract_keywords_from_paths(self, file_paths: List[str]) -> List[str]:
        """
        从文件路径中提取模块关键词
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            提取的关键词列表
        """
        keywords = set()
        
        for path in file_paths:
            if not path:
                continue
                
            # 提取目录名和文件名
            parts = Path(path).parts
            for part in parts:
                # 移除文件扩展名
                name = Path(part).stem
                
                # 分割单词
                words = re.findall(r'[A-Z][a-z]*|[a-z]+', name)
                words.extend(name.split('_'))
                words.extend(name.split('-'))
                
                for word in words:
                    word = word.lower().strip()
                    if len(word) > 2 and word.isalpha():
                        keywords.add(word)
        
        return list(keywords)[:20]
    
    def _update_keywords_config(self, extracted_keywords: Dict[str, List[str]]):
        """
        更新关键词配置文件
        
        Args:
            extracted_keywords: 提取的关键词
        """
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            'config', 
            'auto_keywords.yaml'
        )
        
        try:
            # 创建配置目录
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # 准备配置数据
            config_data = {
                'auto_extracted_keywords': extracted_keywords,
                'extraction_timestamp': time.time(),
                'extraction_date': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 写入配置文件
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            
            logging.info(f"自动提取的关键词已保存到: {config_path}")
            
        except Exception as e:
            logging.error(f"保存自动提取关键词失败: {e}")


if __name__ == "__main__":
    # 测试代码
    search_engine = SemanticSearchEngine()
    
    # 测试搜索
    test_queries = [
        "支付状态更新函数",
        "where is payment status updated",
        "用户登录验证",
        "数据库查询方法"
    ]
    
    for query in test_queries:
        print(f"\n搜索: {query}")
        results = search_engine.search(query, limit=3)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['name']} ({result['type']}) - 分数: {result['relevance_score']:.2f}")
            print(f"     文件: {result['file_path']}")
            if result.get('docstring'):
                print(f"     说明: {result['docstring'][:100]}...")