#!/usr/bin/env python3
"""
增强版搜索引擎
提供通用的代码搜索能力，支持多种搜索策略和可配置的权重系统
"""

import re
import yaml
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

try:
    from semantic_search import SemanticSearchEngine
except ImportError:
    # 如果语义搜索模块不存在，使用占位符
    class SemanticSearchEngine:
        def __init__(self, *args, **kwargs):
            pass
        def search(self, *args, **kwargs):
            return []

try:
    from database import CodeDatabase
except ImportError:
    # 如果数据库模块不存在，使用占位符
    class CodeDatabase:
        def __init__(self, *args, **kwargs):
            pass

class EnhancedSearchEngine(SemanticSearchEngine):
    """
    增强版搜索引擎
    提供通用的代码搜索能力，支持多种搜索策略和权重配置
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化增强搜索引擎
        
        Args:
            config_path: 配置文件路径
        """
        super().__init__(config_path)
        
        # 加载主配置
        self.main_config = self._load_main_config(config_path)
        
        # 加载搜索配置
        enhanced_config_path = self.main_config.get('search', {}).get('enhanced_search_config', 'config/search_config.yaml')
        self.search_config = self._load_search_config(enhanced_config_path)
        
        # 搜索权重配置
        self.search_weights = self.search_config.get('search_weights', {
            'exact_match': 20.0,           # 精确匹配
            'partial_match': 12.0,         # 部分匹配
            'docstring_match': 8.0,        # 文档匹配
            'parameter_match': 3.0,        # 参数匹配
            'body_match': 2.0,             # 函数体匹配
            'semantic_similarity': 4.0,    # 语义相似度
            'keyword_bonus': 6.0,          # 关键词奖励
            'language_preference': 2.0,    # 语言偏好
            'fuzzy_match': 5.0,            # 模糊匹配
            'context_match': 3.0           # 上下文匹配
        })
        
        # 搜索策略配置
        self.search_strategies = self.search_config.get('search_strategies', {
            'enable_fuzzy_search': True,
            'enable_context_search': True,
            'enable_multi_language': True,
            'enable_semantic_boost': True
        })
        
        # 初始化搜索增强功能
        self._init_search_enhancements()
    
    def _load_main_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载主配置文件
        
        Args:
            config_path: 主配置文件路径
            
        Returns:
            主配置字典
        """
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            else:
                print(f"主配置文件不存在: {config_path}，使用默认配置")
                return {}
        except Exception as e:
            print(f"加载主配置文件失败: {e}，使用默认配置")
            return {}
    
    def _load_search_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载搜索配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            搜索配置字典
        """
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    return config.get('enhanced_search', config)  # 支持直接配置或嵌套配置
            else:
                print(f"搜索配置文件不存在: {config_path}，使用默认配置")
                return {}
        except Exception as e:
            print(f"加载搜索配置文件失败: {e}，使用默认配置")
            return {}
    
    def load_preset_config(self, preset_name: str) -> bool:
        """
        加载预设搜索配置
        
        Args:
            preset_name: 预设名称 (quick, deep, precise, semantic)
            
        Returns:
            是否加载成功
        """
        try:
            presets = self.search_config.get('search_presets', {})
            if preset_name not in presets:
                print(f"预设配置不存在: {preset_name}")
                return False
            
            preset_config = presets[preset_name]
            
            # 更新权重配置
            if 'search_weights' in preset_config:
                self.search_weights.update(preset_config['search_weights'])
            
            # 更新策略配置
            if 'search_strategies' in preset_config:
                self.search_strategies.update(preset_config['search_strategies'])
            
            print(f"已加载预设配置: {preset_name}")
            return True
            
        except Exception as e:
            print(f"加载预设配置失败: {e}")
            return False
    
    def update_search_weights(self, weights: Dict[str, float]) -> None:
        """
        动态更新搜索权重
        
        Args:
            weights: 权重配置字典
        """
        self.search_weights.update(weights)
        print(f"已更新搜索权重: {list(weights.keys())}")
    
    def update_search_strategies(self, strategies: Dict[str, Any]) -> None:
        """
        动态更新搜索策略
        
        Args:
            strategies: 策略配置字典
        """
        self.search_strategies.update(strategies)
        print(f"已更新搜索策略: {list(strategies.keys())}")
    
    def get_current_config(self) -> Dict[str, Any]:
        """
        获取当前搜索配置
        
        Returns:
            当前配置字典
        """
        return {
            'search_weights': self.search_weights.copy(),
            'search_strategies': self.search_strategies.copy(),
            'language_weights': self.language_weights.copy(),
            'keyword_patterns': self.keyword_patterns.copy()
        }
    
    def _init_search_enhancements(self):
        """
        初始化搜索增强功能
        """
        # 通用关键词模式
        self.keyword_patterns = {
            'function_indicators': [
                r'\b(function|def|method|func)\b',
                r'\b(class|interface|struct)\b',
                r'\b(api|endpoint|service)\b'
            ],
            'action_indicators': [
                r'\b(create|build|make|generate)\b',
                r'\b(get|fetch|retrieve|find)\b',
                r'\b(update|modify|change|edit)\b',
                r'\b(delete|remove|destroy)\b'
            ],
            'technical_terms': [
                r'\b(database|db|sql|query)\b',
                r'\b(auth|authentication|login|user)\b',
                r'\b(api|rest|http|request)\b',
                r'\b(config|configuration|setting)\b'
            ]
        }
        
        # 语言特定的权重
        self.language_weights = self.search_config.get('language_weights', {
            'python': 1.0,
            'javascript': 1.0,
            'java': 1.0,
            'cpp': 1.0,
            'c': 1.0
        })
        
        # 意图权重配置
        self.intent_weights = self.search_config.get('intent_weights', {
            'how_to': 1.5,
            'definition': 1.3,
            'search': 1.0,
            'example': 1.4,
            'debug': 1.6,
            'implementation': 1.5,
            'general': 1.0
        })
        
        # 代码类型权重配置
        self.code_type_weights = self.search_config.get('code_type_weights', {
            'function': 1.2,
            'method': 1.2,
            'class': 1.1,
            'interface': 1.0,
            'variable': 0.8,
            'constant': 0.9,
            'enum': 0.9,
            'struct': 1.0,
            'module': 0.9,
            'namespace': 0.8
        })
        
        # 文件类型权重配置
        self.file_type_weights = self.search_config.get('file_type_weights', {})
        
        # 优化配置
        self.optimization_config = self.search_config.get('optimization', {
            'ranking_strategy': 'weighted_score',
            'diversity_factor': 0.3,
            'max_same_file_results': 3,
            'max_same_type_results': 5,
            'enable_query_expansion': True
        })
    
    def search(self, query: str, mode: str = 'enhanced', limit: int = 50) -> List[Dict[str, Any]]:
        """
        执行增强搜索
        
        Args:
            query: 搜索查询
            mode: 搜索模式 ('enhanced', 'semantic', 'keyword', 'hybrid')
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        # 预处理查询
        processed_query = self._preprocess_query(query)
        
        # 根据模式选择搜索策略
        if mode == 'enhanced':
            candidates = self._enhanced_search(processed_query, limit)
        elif mode == 'semantic':
            candidates = self._semantic_search_only(processed_query, limit)
        elif mode == 'keyword':
            candidates = self._keyword_search_only(processed_query, limit)
        elif mode == 'hybrid':
            candidates = self._hybrid_search(processed_query, limit)
        else:
            # 默认使用增强搜索
            candidates = self._enhanced_search(processed_query, limit)
        
        # 计算相关性分数并排序
        scored_results = []
        for candidate in candidates:
            score = self._calculate_relevance_score(query, processed_query, candidate)
            candidate['relevance_score'] = score
            scored_results.append(candidate)
        
        # 按分数排序并返回
        scored_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_results[:limit]
    
    def _preprocess_query(self, query: str) -> Dict[str, Any]:
        """
        预处理查询字符串
        
        Args:
            query: 原始查询字符串
            
        Returns:
            处理后的查询信息
        """
        processed = {
            'original': query,
            'normalized': query.lower().strip(),
            'tokens': [],
            'keywords': [],
            'patterns': [],
            'intent': self._detect_query_intent(query)
        }
        
        # 分词处理
        processed['tokens'] = self._tokenize_query(query)
        
        # 提取关键词
        processed['keywords'] = self._extract_keywords(query)
        
        # 检测模式
        processed['patterns'] = self._detect_patterns(query)
        
        return processed
    
    def _detect_query_intent(self, query: str) -> str:
        """
        检测查询意图
        
        Args:
            query: 查询字符串
            
        Returns:
            查询意图类型
        """
        query_lower = query.lower()
        
        # 获取意图模式配置
        intent_patterns = self.search_config.get('intent_patterns', {
            'how_to': ['how to', 'how do', 'how can', '如何', '怎么', '怎样'],
            'definition': ['what is', 'define', 'definition', '什么是', '定义'],
            'example': ['example', 'sample', 'demo', '例子', '示例', '演示'],
            'debug': ['error', 'bug', 'fix', 'debug', 'issue', '错误', '调试', '修复'],
            'implementation': ['implement', 'create', 'build', 'make', '实现', '创建', '构建']
        })
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                return intent
        
        return 'general'
    
    def _detect_code_type(self, content: str) -> str:
        """
        检测代码类型
        
        Args:
            content: 代码内容
            
        Returns:
            代码类型
        """
        content_lower = content.lower()
        
        # 获取代码类型模式配置
        code_patterns = self.search_config.get('code_type_patterns', {
            'function': ['def ', 'function ', 'func ', 'fn '],
            'method': ['def ', 'method', 'public ', 'private ', 'protected '],
            'class': ['class ', 'interface ', 'struct '],
            'variable': ['var ', 'let ', 'const ', '= '],
            'constant': ['const ', 'final ', 'static final'],
            'enum': ['enum ', 'enumeration'],
            'module': ['module ', 'import ', 'from '],
            'namespace': ['namespace ', 'package ']
        })
        
        for code_type, patterns in code_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                return code_type
        
        return 'general'
    
    def _tokenize_query(self, query: str) -> List[str]:
        """
        查询分词
        
        Args:
            query: 查询字符串
            
        Returns:
            分词结果列表
        """
        # 简单的分词实现，可以根据需要替换为更复杂的分词器
        tokens = re.findall(r'\b\w+\b', query.lower())
        return [token for token in tokens if len(token) > 1]
    
    def _extract_keywords(self, query: str) -> List[str]:
        """
        提取关键词
        
        Args:
            query: 查询字符串
            
        Returns:
            关键词列表
        """
        keywords = []
        
        # 使用正则表达式提取技术关键词
        for category, patterns in self.keyword_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, query.lower())
                keywords.extend(matches)
        
        return list(set(keywords))
    
    def _detect_patterns(self, query: str) -> List[str]:
        """
        检测查询模式
        
        Args:
            query: 查询字符串
            
        Returns:
            检测到的模式列表
        """
        patterns = []
        query_lower = query.lower()
        
        # 检测各种模式
        if re.search(r'\b(function|method|def)\s+\w+', query_lower):
            patterns.append('function_definition')
        
        if re.search(r'\b(class|interface)\s+\w+', query_lower):
            patterns.append('class_definition')
        
        if re.search(r'\b(import|include|require)\b', query_lower):
            patterns.append('import_statement')
        
        if re.search(r'\b(error|exception|bug)\b', query_lower):
            patterns.append('error_handling')
        
        return patterns
    
    def _enhanced_search(self, processed_query: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """
        执行增强搜索
        
        Args:
            processed_query: 预处理的查询信息
            limit: 结果数量限制
            
        Returns:
            候选结果列表
        """
        candidates = []
        
        # 1. 基础语义搜索
        semantic_candidates = super()._get_candidates(processed_query, limit)
        candidates.extend(semantic_candidates)
        
        # 2. 模糊匹配搜索
        if self.search_strategies.get('enable_fuzzy_search', True):
            fuzzy_candidates = self._get_fuzzy_candidates(processed_query, limit)
            candidates.extend(fuzzy_candidates)
        
        # 3. 上下文搜索
        if self.search_strategies.get('enable_context_search', True):
            context_candidates = self._get_context_candidates(processed_query, limit)
            candidates.extend(context_candidates)
        
        # 4. 多语言搜索
        if self.search_strategies.get('enable_multi_language', True):
            multi_lang_candidates = self._get_multi_language_candidates(processed_query, limit)
            candidates.extend(multi_lang_candidates)
        
        # 去重
        return self._deduplicate_candidates(candidates)
    
    def _semantic_search_only(self, processed_query: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """
        仅执行语义搜索
        """
        return super()._get_candidates(processed_query, limit)
    
    def _keyword_search_only(self, processed_query: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """
        仅执行关键词搜索
        """
        # 实现基于关键词的搜索逻辑
        return self._get_keyword_candidates(processed_query, limit)
    
    def _hybrid_search(self, processed_query: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """
        执行混合搜索（语义+关键词）
        """
        semantic_candidates = self._semantic_search_only(processed_query, limit // 2)
        keyword_candidates = self._keyword_search_only(processed_query, limit // 2)
        
        candidates = semantic_candidates + keyword_candidates
        return self._deduplicate_candidates(candidates)
    
    def _get_fuzzy_candidates(self, processed_query: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """
        获取模糊匹配候选结果
        """
        # 实现模糊匹配逻辑
        candidates = []
        
        # 使用数据库进行模糊搜索
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建模糊搜索查询
                tokens = processed_query.get('tokens', [])
                if tokens:
                    # 使用LIKE进行模糊匹配
                    like_conditions = []
                    params = []
                    
                    for token in tokens[:3]:  # 限制token数量避免查询过慢
                        like_conditions.append("(name LIKE ? OR docstring LIKE ? OR body LIKE ?)")
                        params.extend([f"%{token}%", f"%{token}%", f"%{token}%"])
                    
                    if like_conditions:
                        query = f"""
                        SELECT * FROM code_snippets 
                        WHERE {' OR '.join(like_conditions)}
                        LIMIT ?
                        """
                        params.append(limit)
                        
                        cursor.execute(query, params)
                        results = cursor.fetchall()
                        
                        for row in results:
                            candidates.append(dict(row))
        
        except Exception as e:
            print(f"模糊搜索失败: {e}")
        
        return candidates
    
    def _get_context_candidates(self, processed_query: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """
        获取上下文相关的候选结果
        """
        # 实现上下文搜索逻辑
        candidates = []
        
        # 根据查询意图调整搜索策略
        intent = processed_query.get('intent', 'general')
        
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                if intent == 'how_to':
                    # 优先搜索包含实现逻辑的函数
                    query = """
                    SELECT * FROM code_snippets 
                    WHERE type = 'function' AND (
                        docstring LIKE '%implement%' OR 
                        docstring LIKE '%example%' OR
                        body LIKE '%def %' OR
                        body LIKE '%function %'
                    )
                    LIMIT ?
                    """
                    cursor.execute(query, (limit,))
                    
                elif intent == 'definition':
                    # 优先搜索类和接口定义
                    query = """
                    SELECT * FROM code_snippets 
                    WHERE type IN ('class', 'interface') OR (
                        docstring LIKE '%define%' OR
                        docstring LIKE '%description%'
                    )
                    LIMIT ?
                    """
                    cursor.execute(query, (limit,))
                
                else:
                    # 通用搜索
                    query = "SELECT * FROM code_snippets LIMIT ?"
                    cursor.execute(query, (limit,))
                
                results = cursor.fetchall()
                for row in results:
                    candidates.append(dict(row))
        
        except Exception as e:
            print(f"上下文搜索失败: {e}")
        
        return candidates
    
    def _get_multi_language_candidates(self, processed_query: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """
        获取多语言候选结果
        """
        candidates = []
        
        # 根据语言权重调整搜索
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # 按语言权重排序搜索
                languages = sorted(self.language_weights.items(), key=lambda x: x[1], reverse=True)
                
                for language, weight in languages:
                    if weight > 0:
                        query = """
                        SELECT * FROM code_snippets 
                        WHERE language = ?
                        LIMIT ?
                        """
                        cursor.execute(query, (language, limit // len(languages)))
                        results = cursor.fetchall()
                        
                        for row in results:
                            candidate = dict(row)
                            candidate['language_weight'] = weight
                            candidates.append(candidate)
        
        except Exception as e:
            print(f"多语言搜索失败: {e}")
        
        return candidates
    
    def _get_keyword_candidates(self, processed_query: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """
        获取基于关键词的候选结果
        """
        candidates = []
        keywords = processed_query.get('keywords', [])
        
        if not keywords:
            return candidates
        
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建关键词搜索查询
                keyword_conditions = []
                params = []
                
                for keyword in keywords:
                    keyword_conditions.append("(name LIKE ? OR docstring LIKE ?)")
                    params.extend([f"%{keyword}%", f"%{keyword}%"])
                
                if keyword_conditions:
                    query = f"""
                    SELECT * FROM code_snippets 
                    WHERE {' OR '.join(keyword_conditions)}
                    LIMIT ?
                    """
                    params.append(limit)
                    
                    cursor.execute(query, params)
                    results = cursor.fetchall()
                    
                    for row in results:
                        candidates.append(dict(row))
        
        except Exception as e:
            print(f"关键词搜索失败: {e}")
        
        return candidates
    
    def _deduplicate_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        去除重复的候选结果
        
        Args:
            candidates: 候选结果列表
            
        Returns:
            去重后的候选结果列表
        """
        seen = set()
        unique_candidates = []
        
        for candidate in candidates:
            # 使用文件路径和名称作为唯一标识
            key = (candidate.get('file_path', ''), candidate.get('name', ''))
            if key not in seen:
                seen.add(key)
                unique_candidates.append(candidate)
        
        return unique_candidates
    
    def _calculate_relevance_score(self, original_query: str, processed_query: Dict[str, Any], 
                                 candidate: Dict[str, Any]) -> float:
        """
        计算相关性分数
        
        Args:
            original_query: 原始查询
            processed_query: 预处理的查询信息
            candidate: 候选结果
            
        Returns:
            相关性分数
        """
        score = 0.0
        
        # 1. 精确匹配分数
        score += self._calculate_exact_match_score(processed_query, candidate)
        
        # 2. 部分匹配分数
        score += self._calculate_partial_match_score(processed_query, candidate)
        
        # 3. 语义相似度分数
        score += self._calculate_semantic_score(original_query, candidate)
        
        # 4. 关键词匹配分数
        score += self._calculate_keyword_score(processed_query, candidate)
        
        # 5. 语言偏好分数
        score += self._calculate_language_score(candidate)
        
        # 6. 上下文匹配分数
        score += self._calculate_context_score(processed_query, candidate)
        
        # 7. 意图权重加成
        intent = processed_query.get('intent', 'general')
        intent_weight = self.intent_weights.get(intent, 1.0)
        score *= intent_weight
        
        # 8. 代码类型权重加成
        content = candidate.get('body', '') or candidate.get('content', '')
        code_type = self._detect_code_type(content)
        code_type_weight = self.code_type_weights.get(code_type, 1.0)
        score *= code_type_weight
        
        # 9. 文件类型权重加成
        if self.file_type_weights:
            file_path = candidate.get('file_path', '')
            file_ext = Path(file_path).suffix.lstrip('.') if file_path else ''
            file_type_weight = self.file_type_weights.get(file_ext, 1.0)
            score *= file_type_weight
        
        # 10. 长度惩罚（避免过长的结果）
        content_length = len(content)
        if content_length > 0:
            length_penalty = min(1.0, 1000 / content_length)
            score *= (1 + length_penalty * 0.1)
        
        return score
    
    def _calculate_exact_match_score(self, processed_query: Dict[str, Any], candidate: Dict[str, Any]) -> float:
        """计算精确匹配分数"""
        score = 0.0
        query_tokens = set(processed_query.get('tokens', []))
        
        # 检查名称精确匹配
        candidate_name = candidate.get('name', '').lower()
        if any(token in candidate_name for token in query_tokens):
            score += self.search_weights.get('exact_match', 20.0)
        
        return score
    
    def _calculate_partial_match_score(self, processed_query: Dict[str, Any], candidate: Dict[str, Any]) -> float:
        """计算部分匹配分数"""
        score = 0.0
        query_tokens = processed_query.get('tokens', [])
        
        # 检查各个字段的部分匹配
        fields = ['name', 'docstring', 'body']
        for field in fields:
            field_content = candidate.get(field, '').lower()
            matches = sum(1 for token in query_tokens if token in field_content)
            if matches > 0:
                field_weight = {
                    'name': self.search_weights.get('partial_match', 12.0),
                    'docstring': self.search_weights.get('docstring_match', 8.0),
                    'body': self.search_weights.get('body_match', 2.0)
                }.get(field, 1.0)
                score += matches * field_weight / len(query_tokens)
        
        return score
    
    def _calculate_semantic_score(self, original_query: str, candidate: Dict[str, Any]) -> float:
        """计算语义相似度分数"""
        # 这里可以集成更复杂的语义相似度计算
        # 暂时返回基础分数
        return self.search_weights.get('semantic_similarity', 4.0)
    
    def _calculate_keyword_score(self, processed_query: Dict[str, Any], candidate: Dict[str, Any]) -> float:
        """计算关键词匹配分数"""
        score = 0.0
        keywords = processed_query.get('keywords', [])
        
        if keywords:
            candidate_text = f"{candidate.get('name', '')} {candidate.get('docstring', '')}".lower()
            matches = sum(1 for keyword in keywords if keyword in candidate_text)
            if matches > 0:
                score += matches * self.search_weights.get('keyword_bonus', 6.0) / len(keywords)
        
        return score
    
    def _calculate_language_score(self, candidate: Dict[str, Any]) -> float:
        """计算语言偏好分数"""
        language = candidate.get('language', '')
        weight = self.language_weights.get(language, 0.5)
        return weight * self.search_weights.get('language_preference', 2.0)
    
    def _calculate_context_score(self, processed_query: Dict[str, Any], candidate: Dict[str, Any]) -> float:
        """计算上下文匹配分数"""
        score = 0.0
        intent = processed_query.get('intent', 'general')
        candidate_type = candidate.get('type', '')
        
        # 根据查询意图调整分数
        context_bonus = {
            'how_to': {'function': 2.0, 'method': 2.0},
            'definition': {'class': 2.0, 'interface': 2.0},
            'example': {'function': 1.5, 'method': 1.5},
            'general': {}
        }.get(intent, {})
        
        if candidate_type in context_bonus:
            score += context_bonus[candidate_type] * self.search_weights.get('context_match', 3.0)
        
        return score


def test_enhanced_search():
    """
    测试增强搜索引擎功能
    """
    print("测试增强搜索引擎...")
    
    try:
        # 初始化搜索引擎
        engine = EnhancedSearchEngine()
        
        # 测试不同类型的查询
        test_queries = [
            "database connection function",
            "user authentication method",
            "how to create API endpoint",
            "class definition example",
            "error handling pattern"
        ]
        
        for query in test_queries:
            print(f"\n搜索查询: '{query}'")
            results = engine.search(query, mode='enhanced', limit=5)
            
            print(f"找到 {len(results)} 个结果:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.get('name', 'Unknown')} "
                      f"(分数: {result.get('relevance_score', 0):.2f}) "
                      f"[{result.get('language', 'Unknown')}]")
        
        print("\n增强搜索引擎测试完成!")
        
    except Exception as e:
        print(f"测试失败: {e}")


def main():
    """
    主函数
    """
    test_enhanced_search()


if __name__ == "__main__":
    main()