#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TreeSitter 代码解析模块
用于解析不同编程语言的代码结构，提取函数、类等信息
"""

import os
import tree_sitter
from tree_sitter import Language, Parser
import yaml
from typing import List, Dict, Any, Optional


class TreeSitterParser:
    """TreeSitter 代码解析器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化解析器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.languages = {}
        self.parsers = {}
        self.supported_languages = {}  # 改为字典格式以匹配测试期望
        self._init_languages()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _init_languages(self):
        """初始化支持的编程语言"""
        try:
            # 使用tree-sitter-languages包提供的便捷方法
            from tree_sitter_languages import get_language, get_parser
            
            for lang in self.config['languages']:
                try:
                    # 使用tree-sitter-languages包的便捷方法
                    language = get_language(lang)
                    parser = get_parser(lang)
                    
                    self.languages[lang] = language
                    self.parsers[lang] = parser
                    self.supported_languages[lang] = True  # 添加到支持的语言字典
                    
                    print(f"✅ 已加载 {lang} 语言支持")
                except Exception as e:
                    print(f"❌ 加载 {lang} 语言失败: {e}")
                    continue
                    
        except ImportError:
            # 如果没有tree-sitter-languages包，回退到原始方法
            print("⚠️ 未找到tree-sitter-languages包，使用原始方法")
            self._init_languages_fallback()
    
    def _init_languages_fallback(self):
        """回退的语言初始化方法"""
        # 语言模块映射
        language_modules = {
            'python': 'tree_sitter_python',
            'javascript': 'tree_sitter_javascript', 
            'java': 'tree_sitter_java',
            'go': 'tree_sitter_go'
        }
        
        for lang in self.config['languages']:
            try:
                # 动态导入语言模块
                module_name = language_modules.get(lang)
                if module_name:
                    try:
                        # 导入对应的tree-sitter语言模块
                        module = __import__(module_name)
                        
                        # 使用正确的Language构造函数（传递PyCapsule和语言名称）
                        language = Language(module.language(), lang)
                        self.languages[lang] = language
                        
                        # 创建解析器并设置语言
                        parser = Parser(language)
                        self.parsers[lang] = parser
                        self.supported_languages[lang] = True  # 添加到支持的语言字典
                        
                        print(f"✅ 已加载 {lang} 语言支持")
                    except ImportError:
                        print(f"❌ 未找到 {lang} 语言模块: {module_name}")
                        continue
                else:
                    print(f"❌ 不支持的语言: {lang}")
            except Exception as e:
                print(f"❌ 加载 {lang} 语言失败: {e}")
                continue
    
    def parse_code(self, code: str, language: str = 'python') -> Optional[Dict[str, Any]]:
        """
        解析代码字符串
        
        Args:
            code: 代码字符串
            language: 编程语言
            
        Returns:
            解析结果字典，包含函数、类等信息
        """
        # 输入验证
        if not code or not code.strip():
            return {
                'file_path': '',
                'language': language,
                'content': code,
                'functions': [],
                'classes': [],
                'imports': [],
                'comments': [],
                'error': 'Empty or whitespace-only code'
            }
        
        if language not in self.parsers:
            return {
                'file_path': '',
                'language': language,
                'content': code,
                'functions': [],
                'classes': [],
                'imports': [],
                'comments': [],
                'error': f'Unsupported language: {language}'
            }

        try:
            # 重置注释提取标志
            if hasattr(self, '_comments_extracted'):
                delattr(self, '_comments_extracted')
                
            # 解析代码
            tree = self.parsers[language].parse(bytes(code, 'utf-8'))
            
            # 检查解析是否成功
            if not tree or not tree.root_node:
                return {
                    'file_path': '',
                    'language': language,
                    'content': code,
                    'functions': [],
                    'classes': [],
                    'imports': [],
                    'comments': [],
                    'error': 'Failed to parse code - invalid syntax'
                }
            
            # 检查是否有语法错误
            has_error = self._check_syntax_errors(tree.root_node)
            
            # 提取代码结构
            result = {
                'file_path': '',
                'language': language,
                'content': code,
                'functions': [],
                'classes': [],
                'imports': [],
                'comments': []
            }
            
            if has_error:
                result['warning'] = 'Code contains syntax errors, results may be incomplete'
            
            # 遍历语法树提取信息
            self._extract_code_elements(tree.root_node, code, result)
            
            return result
            
        except UnicodeDecodeError as e:
            return {
                'file_path': '',
                'language': language,
                'content': code,
                'functions': [],
                'classes': [],
                'imports': [],
                'comments': [],
                'error': f'Unicode decode error: {str(e)}'
            }
        except Exception as e:
            return {
                'file_path': '',
                'language': language,
                'content': code,
                'functions': [],
                'classes': [],
                'imports': [],
                'comments': [],
                'error': f'Parse error: {str(e)}'
            }
    
    def _check_syntax_errors(self, node) -> bool:
        """
        检查语法树中是否有错误节点
        
        Args:
            node: 语法树节点
            
        Returns:
            是否有语法错误
        """
        if node.type == 'ERROR':
            return True
        
        for child in node.children:
            if self._check_syntax_errors(child):
                return True
        
        return False
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """
        检测文件语言（公共方法）
        
        Args:
            file_path: 文件路径
            
        Returns:
            语言类型
        """
        return self._detect_language(file_path)
    
    def get_ast_info(self, content: str, file_path: str = "") -> Dict[str, Any]:
        """
        获取AST信息
        
        Args:
            content: 代码内容
            file_path: 文件路径
            
        Returns:
            AST信息字典
        """
        try:
            language = self.detect_language(file_path) if file_path else 'python'
            if not language or language not in self.parsers:
                return {
                    'file_path': file_path,
                    'language': 'unknown',
                    'content': content,
                    'node_count': 0,
                    'depth': 0,
                    'complexity': 0,
                    'error': '无法检测语言类型'
                }
            
            tree = self.parsers[language].parse(content.encode('utf-8'))
            node_count = self._count_nodes(tree.root_node)
            depth = self._calculate_tree_depth(tree.root_node)
            
            # 计算复杂度信息
            complexity_info = self.calculate_complexity(content, file_path)
            
            return {
                'file_path': file_path,
                'language': language,
                'content': content,
                'tree': tree,
                'root_node': tree.root_node,
                'node_count': node_count,
                'depth': depth,
                'complexity': complexity_info.get('complexity', 0)
            }
            
        except Exception as e:
            return {
                'file_path': file_path,
                'language': 'unknown',
                'content': content,
                'node_count': 0,
                'depth': 0,
                'complexity': 0,
                'error': str(e)
            }
    
    def _count_nodes(self, node) -> int:
        """
        递归计算AST节点数量
        
        Args:
            node: AST节点
            
        Returns:
            节点总数
        """
        count = 1  # 当前节点
        for child in node.children:
            count += self._count_nodes(child)
        return count
    
    def _calculate_tree_depth(self, node) -> int:
        """
        计算AST树的深度
        
        Args:
            node: AST节点
            
        Returns:
            树的深度
        """
        if not node.children:
            return 1
        
        max_depth = 0
        for child in node.children:
            depth = self._calculate_tree_depth(child)
            max_depth = max(max_depth, depth)
        
        return max_depth + 1
    
    def calculate_complexity(self, content: str, file_path: str = "") -> Dict[str, Any]:
        """
        计算代码复杂度
        
        Args:
            content: 代码内容
            file_path: 文件路径
            
        Returns:
            复杂度信息字典
        """
        try:
            language = self.detect_language(file_path) if file_path else 'python'
            if not language or language not in self.parsers:
                return {
                    'file_path': file_path,
                    'language': 'unknown',
                    'content': content,
                    'complexity': 0,
                    'error': '无法检测语言类型'
                }
            
            tree = self.parsers[language].parse(content.encode('utf-8'))
            root_node = tree.root_node
            
            # 计算圈复杂度
            cyclomatic_complexity = self._calculate_cyclomatic_complexity(root_node)
            
            # 计算其他复杂度指标
            function_count = len([node for node in self._traverse_nodes(root_node) 
                                if node.type in ['function_definition', 'method_definition']])
            class_count = len([node for node in self._traverse_nodes(root_node) 
                             if node.type == 'class_definition'])
            
            return {
                'file_path': file_path,
                'language': language,
                'content': content,
                'complexity': cyclomatic_complexity,
                'cyclomatic_complexity': cyclomatic_complexity,
                'function_count': function_count,
                'class_count': class_count,
                'node_count': self._count_nodes(root_node),
                'lines_of_code': len(content.split('\n'))
            }
            
        except Exception as e:
            return {
                'file_path': file_path,
                'language': 'unknown',
                'content': content,
                'complexity': 0,
                'error': str(e)
            }
    
    def _calculate_cyclomatic_complexity(self, node) -> int:
        """
        计算圈复杂度
        
        Args:
            node: AST根节点
            
        Returns:
            圈复杂度值
        """
        complexity = 1  # 基础复杂度
        
        # 增加复杂度的节点类型
        complexity_nodes = {
            'if_statement', 'elif_clause', 'else_clause',
            'for_statement', 'while_statement',
            'try_statement', 'except_clause',
            'and', 'or',
            'conditional_expression'
        }
        
        for node in self._traverse_nodes(node):
            if node.type in complexity_nodes:
                complexity += 1
        
        return complexity
    
    def _traverse_nodes(self, node):
        """
        遍历所有AST节点
        
        Args:
            node: 起始节点
            
        Yields:
            每个节点
        """
        yield node
        for child in node.children:
            yield from self._traverse_nodes(child)

    def parse_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        解析单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析结果字典，包含函数、类等信息
        """
        # 根据文件扩展名确定语言
        lang = self._detect_language(file_path)
        if not lang or lang not in self.parsers:
            return None
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 解析代码
            tree = self.parsers[lang].parse(bytes(content, 'utf-8'))
            
            # 提取代码结构
            result = {
                'file_path': file_path,
                'language': lang,
                'content': content,
                'functions': [],
                'classes': [],
                'imports': [],
                'comments': []
            }
            
            # 遍历语法树提取信息
            self._extract_code_elements(tree.root_node, content, result)
            
            return result
            
        except Exception as e:
            print(f"解析文件 {file_path} 失败: {e}")
            return None
    
    def _detect_language(self, file_path: str) -> Optional[str]:
        """
        根据文件扩展名检测编程语言
        
        Args:
            file_path: 文件路径
            
        Returns:
            语言名称
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        for lang, extensions in self.config['file_extensions'].items():
            if ext in extensions:
                return lang
        
        return None
    
    def _extract_code_elements(self, node, content: str, result: Dict[str, Any]):
        """
        从语法树节点中提取代码元素
        
        Args:
            node: 语法树节点
            content: 文件内容
            result: 结果字典
        """
        # 根据节点类型提取不同的代码元素
        # Python节点类型
        if node.type == 'function_definition':
            self._extract_function(node, content, result)
        elif node.type == 'class_definition':
            self._extract_class(node, content, result)
        elif node.type in ['import_statement', 'import_from_statement']:
            self._extract_import(node, content, result)
        elif node.type == 'comment':
            self._extract_comment(node, content, result)
        
        # JavaScript节点类型
        elif node.type == 'function_declaration':
            self._extract_js_function(node, content, result)
        elif node.type == 'arrow_function':
            self._extract_js_arrow_function(node, content, result)
        elif node.type == 'class_declaration':
            self._extract_js_class(node, content, result)
        elif node.type == 'method_definition':  # 添加方法定义支持，包括constructor
            self._extract_js_function(node, content, result)
        elif node.type in ['import_statement', 'export_statement']:
            self._extract_js_import_export(node, content, result)
        elif node.type in ['comment', 'line_comment', 'block_comment']:
            self._extract_comment(node, content, result)
        
        # 递归处理子节点
        for child in node.children:
            self._extract_code_elements(child, content, result)
        
        # 在处理完所有节点后，使用新的注释提取方法
        if not hasattr(self, '_comments_extracted'):
            result['comments'] = self._extract_comments(node, content)
            self._comments_extracted = True
    
    def _extract_js_function(self, node, content: str, result: Dict[str, Any]):
        """
        提取JavaScript函数信息
        
        Args:
            node: 函数节点
            content: 文件内容
            result: 结果字典
        """
        try:
            # 将内容转换为字节以确保正确的偏移计算
            content_bytes = content.encode('utf-8')
            
            # 获取函数名
            func_name = 'anonymous'
            
            if node.type == 'method_definition':
                # 对于method_definition节点，函数名可能在name或property字段中
                name_node = node.child_by_field_name('name')
                property_node = node.child_by_field_name('property')
                
                if name_node:
                    func_name = content_bytes[name_node.start_byte:name_node.end_byte].decode('utf-8')
                elif property_node:
                    func_name = content_bytes[property_node.start_byte:property_node.end_byte].decode('utf-8')
                else:
                    # 如果都没有，查找identifier或property_identifier子节点
                    for child in node.children:
                        if child.type in ['identifier', 'property_identifier']:
                            func_name = content_bytes[child.start_byte:child.end_byte].decode('utf-8')
                            break
            elif node.type == 'function_declaration':
                # 对于function_declaration节点，函数名在name字段中
                name_node = node.child_by_field_name('name')
                if name_node:
                    func_name = content_bytes[name_node.start_byte:name_node.end_byte].decode('utf-8')
            
            # 计算行号
            start_line = content[:node.start_byte].count('\n') + 1
            end_line = content[:node.end_byte].count('\n') + 1
            
            # 提取参数
            parameters = self._extract_js_parameters(node, content)
            
            # 提取文档字符串
            docstring = self._extract_js_docstring(node, content)
            
            result['functions'].append({
                'name': func_name,
                'start_line': start_line,
                'end_line': end_line,
                'parameters': parameters,
                'docstring': docstring,
                'return_type': None  # JavaScript通常没有显式返回类型
            })
            
        except Exception as e:
            print(f"提取JavaScript函数信息失败: {e}")
    
    def _extract_js_arrow_function(self, node, content: str, result: Dict[str, Any]):
        """
        提取JavaScript箭头函数信息
        
        Args:
            node: 箭头函数节点
            content: 文件内容
            result: 结果字典
        """
        try:
            # 箭头函数通常是匿名的，除非赋值给变量
            func_name = 'arrow_function'
            
            # 计算行号
            start_line = content[:node.start_byte].count('\n') + 1
            end_line = content[:node.end_byte].count('\n') + 1
            
            # 提取参数
            parameters = self._extract_js_parameters(node, content)
            
            result['functions'].append({
                'name': func_name,
                'start_line': start_line,
                'end_line': end_line,
                'parameters': parameters,
                'docstring': None,
                'return_type': None
            })
            
        except Exception as e:
            print(f"提取JavaScript箭头函数信息失败: {e}")
    
    def _extract_js_class(self, node, content: str, result: Dict[str, Any]):
        """
        提取JavaScript类信息
        
        Args:
            node: 类节点
            content: 文件内容
            result: 结果字典
        """
        try:
            # 将内容转换为字节数组以正确处理字节偏移
            content_bytes = content.encode('utf-8')
            
            # 获取类名
            name_node = node.child_by_field_name('name')
            if name_node:
                class_name = content_bytes[name_node.start_byte:name_node.end_byte].decode('utf-8')
            else:
                class_name = 'anonymous'
            
            # 计算行号
            start_line = content[:node.start_byte].count('\n') + 1
            end_line = content[:node.end_byte].count('\n') + 1
            
            # 提取文档字符串
            docstring = self._extract_js_class_docstring(node, content)
            
            result['classes'].append({
                'name': class_name,
                'start_line': start_line,
                'end_line': end_line,
                'docstring': docstring
            })
            
        except Exception as e:
            print(f"提取JavaScript类信息失败: {e}")
    
    def _extract_js_import_export(self, node, content: str, result: Dict[str, Any]):
        """
        提取JavaScript导入/导出信息
        
        Args:
            node: 导入/导出节点
            content: 文件内容
            result: 结果字典
        """
        try:
            content_bytes = content.encode('utf-8')
            import_text = content_bytes[node.start_byte:node.end_byte].decode('utf-8')
            start_line = content[:node.start_byte].count('\n') + 1
            
            # 确定类型和模块
            if import_text.strip().startswith('import'):
                import_type = 'import'
                # 简单提取模块名
                parts = import_text.strip().split()
                module = parts[-1].strip('\'"') if len(parts) > 1 else ''
            elif import_text.strip().startswith('export'):
                import_type = 'export'
                module = ''
            else:
                import_type = 'unknown'
                module = ''
            
            result['imports'].append({
                'text': import_text,
                'line': start_line,
                'module': module,
                'type': import_type
            })
            
        except Exception as e:
            print(f"提取JavaScript导入/导出信息失败: {e}")
    
    def _extract_js_parameters(self, func_node, content: str) -> List[str]:
        """
        提取JavaScript函数参数
        
        Args:
            func_node: 函数节点
            content: 文件内容
            
        Returns:
            参数列表
        """
        parameters = []
        try:
            params_node = func_node.child_by_field_name('parameters')
            if params_node:
                content_bytes = content.encode('utf-8')
                for child in params_node.children:
                    if child.type in ['identifier', 'formal_parameter', 'rest_parameter']:
                        param_text = content_bytes[child.start_byte:child.end_byte].decode('utf-8')
                        param_text = ' '.join(param_text.split())
                        if param_text and param_text not in ['(', ')', ',']:
                            parameters.append(param_text)
        except Exception as e:
            print(f"提取JavaScript参数失败: {e}")
        
        return parameters
    
    def _extract_js_docstring(self, func_node, content: str) -> Optional[str]:
        """
        提取JavaScript函数文档字符串
        
        Args:
            func_node: 函数节点
            content: 文件内容
            
        Returns:
            文档字符串
        """
        try:
            # 查找函数前面的注释
            for child in func_node.children:
                if child.type == 'comment':
                    content_bytes = content.encode('utf-8')
                    comment_text = content_bytes[child.start_byte:child.end_byte].decode('utf-8')
                    return comment_text.strip()
            return None
        except Exception as e:
            print(f"提取JavaScript文档字符串失败: {e}")
            return None
    
    def _extract_js_class_docstring(self, class_node, content: str) -> Optional[str]:
        """
        提取JavaScript类文档字符串
        
        Args:
            class_node: 类节点
            content: 文件内容
            
        Returns:
            文档字符串
        """
        try:
            # 查找类前面的注释
            for child in class_node.children:
                if child.type == 'comment':
                    content_bytes = content.encode('utf-8')
                    comment_text = content_bytes[child.start_byte:child.end_byte].decode('utf-8')
                    return comment_text.strip()
            return None
        except Exception as e:
            print(f"提取JavaScript类文档字符串失败: {e}")
            return None
    
    def _extract_function(self, node, content: str, result: Dict[str, Any]):
        """
        提取函数信息
        
        Args:
            node: 函数节点
            content: 文件内容
            result: 结果字典
        """
        try:
            # 获取函数名
            name_node = node.child_by_field_name('name')
            if name_node:
                # 使用UTF-8编码的字节来正确提取文本
                content_bytes = content.encode('utf-8')
                func_name = content_bytes[name_node.start_byte:name_node.end_byte].decode('utf-8')
                
                # 获取函数体
                func_body = content_bytes[node.start_byte:node.end_byte].decode('utf-8')
                
                # 计算行号
                start_line = content[:node.start_byte].count('\n') + 1
                end_line = content[:node.end_byte].count('\n') + 1
                
                # 提取参数
                parameters = self._extract_parameters(node, content)
                
                # 提取文档字符串
                docstring = self._extract_docstring(node, content)
                
                # 提取返回类型
                return_type = self._extract_return_type(node, content)
                
                result['functions'].append({
                    'name': func_name,
                    'start_line': start_line,
                    'end_line': end_line,
                    'parameters': parameters,
                    'docstring': docstring,
                    'return_type': return_type,
                    'body': func_body
                })
                
        except Exception as e:
            print(f"提取函数信息失败: {e}")
    
    def _extract_class(self, node, content: str, result: Dict[str, Any]):
        """
        提取类信息
        
        Args:
            node: 类节点
            content: 文件内容
            result: 结果字典
        """
        try:
            # 获取类名
            name_node = node.child_by_field_name('name')
            if name_node:
                # 使用UTF-8编码的字节来正确提取文本
                content_bytes = content.encode('utf-8')
                class_name = content_bytes[name_node.start_byte:name_node.end_byte].decode('utf-8')
                
                # 计算行号
                start_line = content[:node.start_byte].count('\n') + 1
                end_line = content[:node.end_byte].count('\n') + 1
                
                # 获取类体
                class_body = content_bytes[node.start_byte:node.end_byte].decode('utf-8')
                
                # 提取类的文档字符串
                docstring = self._extract_class_docstring(node, content)
                
                # 提取基类信息
                base_classes = []
                superclasses_node = node.child_by_field_name('superclasses')
                if superclasses_node:
                    for child in superclasses_node.children:
                        if child.type == 'identifier':
                            base_class = content_bytes[child.start_byte:child.end_byte].decode('utf-8')
                            base_classes.append(base_class)
                        elif child.type == 'attribute':
                            # 处理模块.类名的情况
                            base_class = content_bytes[child.start_byte:child.end_byte].decode('utf-8')
                            base_classes.append(base_class)
                
                result['classes'].append({
                    'name': class_name,
                    'start_line': start_line,
                    'end_line': end_line,
                    'body': class_body,
                    'docstring': docstring,
                    'base_classes': base_classes
                })
                
        except Exception as e:
            print(f"提取类信息失败: {e}")
    
    def _extract_class_docstring(self, class_node, content: str) -> Optional[str]:
        """
        提取类文档字符串
        
        Args:
            class_node: 类节点
            content: 文件内容
            
        Returns:
            文档字符串，如果没有则返回None
        """
        try:
            # 查找类体中的第一个字符串字面量作为文档字符串
            for child in class_node.children:
                if child.type == 'block':
                    for stmt in child.children:
                        if stmt.type == 'expression_statement':
                            for expr in stmt.children:
                                if expr.type == 'string':
                                    content_bytes = content.encode('utf-8')
                                    docstring = content_bytes[expr.start_byte:expr.end_byte].decode('utf-8')
                                    # 去掉引号
                                    docstring = docstring.strip().strip('"""').strip("'''").strip('"').strip("'")
                                    return docstring.strip()
            return None
            
        except Exception as e:
            print(f"提取类文档字符串失败: {e}")
            return None
    
    def _extract_import(self, node, content: str, result: Dict[str, Any]):
        """
        提取导入信息
        
        Args:
            node: 导入节点
            content: 源代码内容
            result: 结果字典
        """
        try:
            content_bytes = content.encode('utf-8')
            import_text = content_bytes[node.start_byte:node.end_byte].decode('utf-8').strip()
            line_number = node.start_point[0] + 1
            
            # 确定导入类型和模块名
            import_type, module_name = self._determine_import_type(import_text)
            
            # 检查是否有别名
            alias = None
            if ' as ' in import_text:
                parts = import_text.split(' as ')
                if len(parts) == 2:
                    alias = parts[1].strip()
            
            result['imports'].append({
                'text': import_text,
                'line': line_number,
                'module': module_name,
                'type': import_type,
                'alias': alias
            })
        except Exception as e:
            print(f"提取导入信息失败: {e}")
    
    def _determine_import_type(self, import_text):
        """
        确定导入类型并提取模块名
        
        Args:
            import_text: 导入语句文本
            
        Returns:
            tuple: (导入类型, 模块名)
        """
        import_text = import_text.strip()
        
        if import_text.startswith("from"):
            # from xxx import yyy
            import_type = "from"
            parts = import_text.split()
            if len(parts) >= 2:
                module_name = parts[1]
            else:
                module_name = "unknown"
        else:
            # import xxx
            import_type = "import"
            parts = import_text.split()
            if len(parts) >= 2:
                module_name = parts[1].split('.')[0]  # 取第一部分作为模块名
            else:
                module_name = "unknown"
        
        return import_type, module_name
    
    def _extract_comment(self, node, content: str, result: Dict[str, Any]):
        """
        提取注释信息
        
        Args:
            node: 注释节点
            content: 文件内容
            result: 结果字典
        """
        try:
            # 使用UTF-8编码的字节来正确提取文本
            content_bytes = content.encode('utf-8')
            comment_text = content_bytes[node.start_byte:node.end_byte].decode('utf-8')
            start_line = content[:node.start_byte].count('\n') + 1
            
            # 确定注释类型
            comment_type = self._determine_comment_type(comment_text)
            
            result['comments'].append({
                'text': comment_text,
                'line': start_line,
                'type': comment_type
            })
            
        except Exception as e:
            print(f"提取注释信息失败: {e}")
    
    def _extract_comments(self, node, source_code: str) -> List[Dict[str, Any]]:
        """
        提取注释信息
        
        Args:
            node: AST节点
            source_code: 源代码内容
            
        Returns:
            注释信息列表
        """
        comments = []
        
        # 遍历所有节点提取行注释
        def traverse(node):
            if node.type == 'comment':
                comment_text = source_code[node.start_byte:node.end_byte]
                # 过滤掉错误的注释节点（包含换行符或非注释内容）
                if comment_text.startswith('#') and '\n' not in comment_text.strip():
                    comment_info = {
                        'text': comment_text.strip(),
                        'line': node.start_point[0] + 1,
                        'type': self._determine_comment_type(comment_text.strip())
                    }
                    comments.append(comment_info)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
        
        # 使用正则表达式提取文档字符串
        import re
        
        # 匹配三引号字符串（双引号或单引号）
        docstring_pattern = r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')'
        
        for match in re.finditer(docstring_pattern, source_code):
            docstring_text = match.group(1)
            start_pos = match.start()
            
            # 计算行号
            line_num = source_code[:start_pos].count('\n') + 1
            
            # 检查是否为文档字符串（更宽松的条件）
            # 1. 检查前面的内容
            before_text = source_code[:start_pos]
            lines_before = before_text.split('\n')
            current_line_before = lines_before[-1] if lines_before else ''
            
            # 如果当前行在三引号前只有空格，或者前一行以冒号结尾，则认为是文档字符串
            is_docstring = (
                current_line_before.strip() == '' or  # 当前行只有空格
                (len(lines_before) > 1 and lines_before[-2].rstrip().endswith(':'))  # 前一行以冒号结尾
            )
            
            if is_docstring:
                comment_info = {
                    'text': docstring_text,
                    'line': line_num,
                    'type': 'block'
                }
                comments.append(comment_info)
        
        # 使用正则表达式提取行注释（作为备份）
        line_comment_pattern = r'#[^\n]*'
        for match in re.finditer(line_comment_pattern, source_code):
            comment_text = match.group()
            start_pos = match.start()
            line_num = source_code[:start_pos].count('\n') + 1
            
            # 检查是否已经被Tree-sitter提取过
            already_extracted = any(
                c['line'] == line_num and c['text'].strip() == comment_text.strip()
                for c in comments
            )
            
            if not already_extracted:
                comment_info = {
                    'text': comment_text,
                    'line': line_num,
                    'type': self._determine_comment_type(comment_text)
                }
                comments.append(comment_info)
        
        # 按行号排序
        comments.sort(key=lambda x: x['line'])
        
        return comments
    
    def _is_docstring(self, node, source_code: str) -> bool:
        """
        判断字符串节点是否为文档字符串
        
        Args:
            node: 字符串节点
            source_code: 源代码内容
            
        Returns:
            是否为文档字符串
        """
        # 获取字符串内容
        text = source_code[node.start_byte:node.end_byte]
        
        # 检查是否为三引号字符串
        if (text.startswith('"""') and text.endswith('"""')) or \
           (text.startswith("'''") and text.endswith("'''")):
            # 检查父节点是否为表达式语句（独立的字符串）
            parent = node.parent
            if parent and parent.type == 'expression_statement':
                return True
            # 检查是否为函数或类的第一个语句
            if parent and parent.type in ['function_definition', 'class_definition']:
                return True
        
        return False
    
    def _determine_comment_type(self, comment_text: str) -> str:
        """
        确定注释类型
        
        Args:
            comment_text: 注释文本
            
        Returns:
            注释类型
        """
        comment_text = comment_text.strip()
        
        if comment_text.startswith('"""') and comment_text.endswith('"""'):
            return 'block'
        elif comment_text.startswith("'''") and comment_text.endswith("'''"):
            return 'block'
        elif comment_text.startswith('#'):
            return 'line'
        elif comment_text.startswith('/*') and comment_text.endswith('*/'):
            return 'block'
        elif comment_text.startswith('//'):
            return 'line'
        else:
            return 'unknown'
    
    def _extract_parameters(self, func_node, content: str) -> List[str]:
        """
        提取函数参数
        
        Args:
            func_node: 函数节点
            content: 文件内容
            
        Returns:
            参数列表
        """
        parameters = []
        try:
            params_node = func_node.child_by_field_name('parameters')
            if params_node:
                content_bytes = content.encode('utf-8')
                for child in params_node.children:
                    # 处理不同类型的参数节点
                    if child.type == 'identifier':
                        param_text = content_bytes[child.start_byte:child.end_byte].decode('utf-8')
                        param_text = param_text.strip()
                        if param_text and param_text not in ['(', ')', ',']:
                            parameters.append(param_text)
                    elif child.type in ['typed_parameter', 'default_parameter', 'typed_default_parameter']:
                        # 对于带类型注解或默认值的参数，只提取参数名
                        for subchild in child.children:
                            if subchild.type == 'identifier':
                                param_text = content_bytes[subchild.start_byte:subchild.end_byte].decode('utf-8')
                                param_text = param_text.strip()
                                if param_text:
                                    parameters.append(param_text)
                                break
                    elif child.type == 'parameter':
                        # 处理简单参数
                        for subchild in child.children:
                            if subchild.type == 'identifier':
                                param_text = content_bytes[subchild.start_byte:subchild.end_byte].decode('utf-8')
                                param_text = param_text.strip()
                                if param_text:
                                    parameters.append(param_text)
                                break
                    elif child.type in ['list_splat_pattern', 'dictionary_splat_pattern']:
                        # 处理 *args 和 **kwargs
                        for subchild in child.children:
                            if subchild.type == 'identifier':
                                param_text = content_bytes[subchild.start_byte:subchild.end_byte].decode('utf-8')
                                param_text = param_text.strip()
                                if param_text:
                                    parameters.append(param_text)
                                break
        except Exception as e:
            print(f"提取参数失败: {e}")
        
        return parameters
    
    def _extract_return_type(self, func_node, content: str) -> Optional[str]:
        """
        提取函数返回类型
        
        Args:
            func_node: 函数节点
            content: 文件内容
            
        Returns:
            返回类型字符串，如果没有则返回None
        """
        try:
            # 查找返回类型注解
            return_type_node = func_node.child_by_field_name('return_type')
            if return_type_node:
                content_bytes = content.encode('utf-8')
                return_type = content_bytes[return_type_node.start_byte:return_type_node.end_byte].decode('utf-8')
                # 去掉箭头符号
                return_type = return_type.strip().lstrip('->')
                return return_type.strip()
            
            # 如果没有类型注解，尝试从函数体中提取
            func_text = content[func_node.start_byte:func_node.end_byte]
            if '->' in func_text:
                # 简单的正则匹配返回类型
                import re
                match = re.search(r'->\s*([^:]+):', func_text)
                if match:
                    return match.group(1).strip()
                    
            return None
            
        except Exception as e:
            print(f"提取返回类型失败: {e}")
            return None
    
    def _extract_docstring(self, func_node, content: str) -> Optional[str]:
        """
        提取函数文档字符串
        
        Args:
            func_node: 函数节点
            content: 文件内容
            
        Returns:
            文档字符串，如果没有则返回None
        """
        try:
            # 查找函数体中的第一个字符串字面量作为文档字符串
            for child in func_node.children:
                if child.type == 'block':
                    for stmt in child.children:
                        if stmt.type == 'expression_statement':
                            for expr in stmt.children:
                                if expr.type == 'string':
                                    content_bytes = content.encode('utf-8')
                                    docstring = content_bytes[expr.start_byte:expr.end_byte].decode('utf-8')
                                    # 去掉引号
                                    docstring = docstring.strip().strip('"""').strip("'''").strip('"').strip("'")
                                    return docstring.strip()
            return None
            
        except Exception as e:
            print(f"提取文档字符串失败: {e}")
            return None


if __name__ == "__main__":
    # 测试代码
    parser = TreeSitterParser()
    
    # 创建测试文件
    test_file = "test_example.py"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write('''
def hello_world(name: str) -> str:
    """
    打招呼函数
    
    Args:
        name: 姓名
        
    Returns:
        问候语
    """
    return f"Hello, {name}!"

class Calculator:
    """简单计算器类"""
    
    def add(self, a: int, b: int) -> int:
        """加法运算"""
        return a + b
''')
    
    # 解析测试文件
    result = parser.parse_file(test_file)
    if result:
        print("解析结果:")
        print(f"文件: {result['file_path']}")
        print(f"语言: {result['language']}")
        print(f"函数数量: {len(result['functions'])}")
        print(f"类数量: {len(result['classes'])}")
        
        for func in result['functions']:
            print(f"  函数: {func['name']} (行 {func['start_line']}-{func['end_line']})")
        
        for cls in result['classes']:
            print(f"  类: {cls['name']} (行 {cls['start_line']}-{cls['end_line']})")
    
    # 清理测试文件
    os.remove(test_file)