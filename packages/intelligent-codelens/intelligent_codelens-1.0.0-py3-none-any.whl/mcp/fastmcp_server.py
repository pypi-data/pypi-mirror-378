#!/usr/bin/env python3
"""
AI编辑器专用FastMCP代码搜索服务器
专为 Trae AI、Claude、Cursor 等AI编辑器优化的MCP服务器实现
提供智能代码搜索、分析和上下文感知功能
"""

import argparse
import json
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from mcp.server.fastmcp import FastMCP

# 导入本地模块
import sys
from pathlib import Path

# 添加核心模块路径到系统路径
core_path = Path(__file__).parent.parent / "core"
sys.path.insert(0, str(core_path))

try:
    from ..core.semantic_search import SemanticSearchEngine
    from ..core.database import CodeDatabase
except ImportError:
    from semantic_search import SemanticSearchEngine
    from database import CodeDatabase

# AI编辑器优化的日志配置
def setup_ai_optimized_logging(config: Dict[str, Any]) -> None:
    """
    设置AI编辑器优化的日志配置
    
    Args:
        config: 配置字典
    """
    log_level = config.get('logging', {}).get('level', 'INFO')
    log_format = '%(asctime)s - %(name)s - %(levelname)s - [AI-Editor] %(message)s'
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('ai_editor_mcp.log', encoding='utf-8')
        ]
    )

logger = logging.getLogger(__name__)

# 创建AI编辑器专用FastMCP服务器实例
mcp = FastMCP("ai-editor-code-search")

# 全局变量存储配置和组件
config = {}
search_engine = None
db_manager = None
startup_time = None

def load_ai_editor_config(config_path: str = "mcp_config.yaml") -> Dict[str, Any]:
    """
    加载AI编辑器优化的配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典，包含AI编辑器专用设置
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
            
        # 验证AI编辑器配置
        if not config_data.get('server', {}).get('ai_optimized', False):
            logger.warning("配置文件未启用AI编辑器优化，建议更新配置")
            
        # 设置默认的AI编辑器配置
        ai_defaults = {
            'ai_editor': {
                'response_timeout': 15,
                'max_context_lines': 50,
                'include_docstrings': True,
                'include_comments': True,
                'syntax_highlighting': True,
                'code_structure_analysis': True,
                'auto_completion_hints': True
            },
            'performance': {
                'parallel_processing': True,
                'memory_optimization': True,
                'index_preloading': True
            }
        }
        
        # 合并默认配置
        for key, value in ai_defaults.items():
            if key not in config_data:
                config_data[key] = value
            else:
                config_data[key] = {**value, **config_data[key]}
                
        return config_data
        
    except FileNotFoundError:
        logger.error(f"配置文件 {config_path} 不存在")
        # 设置默认的AI编辑器配置
        ai_defaults = {
            'ai_editor': {
                'response_timeout': 15,
                'max_context_lines': 50,
                'include_docstrings': True,
                'include_comments': True,
                'syntax_highlighting': True,
                'code_structure_analysis': True,
                'auto_completion_hints': True
            },
            'performance': {
                'parallel_processing': True,
                'memory_optimization': True,
                'index_preloading': True
            }
        }
        return {
            'database': {'file': 'search.db'},
            'search': {'max_results': 20, 'default_limit': 15},
            'repository': {'search_directories': ['.']},
            'ai_editor': ai_defaults['ai_editor'],
            'performance': ai_defaults['performance']
        }
    except yaml.YAMLError as e:
        logger.error(f"配置文件格式错误: {e}")
        raise

def initialize_ai_components(config_path: str = "mcp_config.yaml"):
    """
    初始化AI编辑器优化的搜索引擎和数据库管理器
    
    Args:
        config_path: 配置文件路径
    """
    global config, search_engine, db_manager, startup_time
    
    startup_time = time.time()
    logger.info("🚀 启动AI编辑器专用MCP代码搜索服务器...")
    
    # 加载AI编辑器优化配置
    config = load_ai_editor_config(config_path)
    
    # 设置日志
    setup_ai_optimized_logging(config)
    
    # 初始化搜索引擎
    search_engine = SemanticSearchEngine(config_path)
    
    # 使用AI编辑器优化的数据库配置
    db_file = config.get('database', {}).get('file', 'search.db')
    if not os.path.isabs(db_file):
        db_file = os.path.abspath(db_file)
    
    db_manager = CodeDatabase(db_file)
    
    # 预加载索引（AI编辑器性能优化）
    if config.get('performance', {}).get('index_preloading', True):
        logger.info("🔄 预加载代码索引以优化AI编辑器响应速度...")
        try:
            # 预热搜索引擎
            search_engine.search("__warmup__", limit=1)
        except Exception as e:
            logger.warning(f"索引预加载失败，但不影响正常使用: {e}")
    
    elapsed = time.time() - startup_time
    logger.info(f"✅ AI编辑器MCP服务器初始化完成 (耗时: {elapsed:.2f}秒)")
    logger.info(f"📊 数据库路径: {db_file}")
    logger.info(f"🎯 AI编辑器优化: 已启用")
    logger.info(f"🔍 搜索目录: {config.get('repository', {}).get('search_directories', ['.'])}")

@mcp.tool()
async def search_code(query: str, limit: int = 15, file_type: str = "") -> str:
    """
    AI编辑器优化的代码搜索功能
    为AI编辑器提供智能代码搜索，包含上下文感知和语义理解
    
    Args:
        query: 搜索查询字符串
        limit: 返回结果数量限制 (默认: 15, 最大: 50, 适合AI编辑器分析)
        file_type: 文件类型过滤（如：.py, .js等）
        
    Returns:
        AI编辑器友好的结构化搜索结果JSON字符串
    """
    try:
        start_time = time.time()
        
        # 使用全局的搜索引擎实例，如果未初始化则先初始化
        global search_engine
        logger.info(f"🔍 [AI-Editor] MCP工具调用 - 搜索查询: {query}, 限制: {limit}")
        logger.info(f"当前工作目录: {os.getcwd()}")
        logger.info(f"搜索引擎状态: {'已初始化' if search_engine is not None else '未初始化'}")
        
        if search_engine is None:
            # 确保使用正确的配置文件路径 - 使用当前工作目录
            config_path = "mcp_config.yaml"
            if not os.path.exists(config_path):
                config_path = os.path.join(os.getcwd(), "mcp_config.yaml")
            logger.info(f"初始化搜索引擎，配置文件路径: {config_path}")
            initialize_ai_components(config_path)
            logger.info("搜索引擎初始化完成")
            
        # AI编辑器优化：限制结果数量以提高响应速度
        max_results = config.get('search', {}).get('max_results', 20)
        limit = min(max(1, limit), max_results)
        
        logger.info(f"🔍 [AI-Editor] 调用搜索引擎搜索: {query}")
        results = search_engine.search(query, limit=limit)
        logger.info(f"搜索引擎返回结果数量: {len(results)}")
        
        # 如果指定了文件类型，进行过滤
        if file_type:
            results = [r for r in results if r.get('file_path', '').endswith(file_type)]
            logger.info(f"文件类型过滤后结果数量: {len(results)}")

        # AI编辑器优化：增强结果结构
        enhanced_results = []
        ai_config = config.get('ai_editor', {})
        
        for result in results:
            enhanced_result = {
                'file_path': result.get('file_path', ''),
                'content': result.get('content', ''),
                'score': result.get('score', 0.0),
                'line_number': result.get('line_number', 0),
                'function_name': result.get('function_name', ''),
                'class_name': result.get('class_name', ''),
                # AI编辑器专用字段
                'ai_context': {
                    'relevance': 'high' if result.get('score', 0) > 0.8 else 'medium' if result.get('score', 0) > 0.5 else 'low',
                    'code_type': result.get('code_type', 'unknown'),
                    'language': result.get('language', 'unknown'),
                    'has_docstring': bool(result.get('docstring')),
                    'has_comments': bool(result.get('comments')),
                    'complexity': result.get('complexity', 'unknown')
                }
            }
            
            # 添加上下文信息（如果启用）
            if ai_config.get('include_docstrings', True) and result.get('docstring'):
                enhanced_result['docstring'] = result['docstring']
            
            if ai_config.get('include_comments', True) and result.get('comments'):
                enhanced_result['comments'] = result['comments']
                
            enhanced_results.append(enhanced_result)
        
        elapsed = time.time() - start_time
        
        response = {
            'success': True,
            'query': query,
            'results': enhanced_results,
            'total_results': len(enhanced_results),
            'search_time': round(elapsed, 3),
            'ai_optimized': True,
            'metadata': {
                'server_version': config.get('server', {}).get('version', '2.0.0'),
                'ai_features_enabled': True,
                'response_format': 'structured'
            }
        }
        
        logger.info(f"✅ [AI-Editor] 搜索完成: {len(enhanced_results)} 个结果 (耗时: {elapsed:.3f}秒)")
        return json.dumps(response, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"❌ [AI-Editor] 搜索代码时出错: {e}")
        error_result = {
            'success': False,
            'error': str(e),
            'query': query,
            'results': [],
            'total_results': 0,
            'ai_optimized': True,
            'troubleshooting': {
                'suggestion': '请检查搜索查询格式或联系技术支持',
                'error_type': type(e).__name__
            }
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

@mcp.tool()
async def get_file_content(file_path: str, start_line: Optional[int] = None, 
                          end_line: Optional[int] = None) -> str:
    """
    获取指定文件的内容
    
    Args:
        file_path: 文件路径
        start_line: 起始行号（可选，从1开始）
        end_line: 结束行号（可选，包含该行）
        
    Returns:
        文件内容的JSON字符串
    """
    try:
        # 直接读取文件，不依赖数据库
        if not os.path.exists(file_path):
            result = {
                'success': False,
                'error': f'文件未找到: {file_path}',
                'file_path': file_path,
                'content': ''
            }
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            if start_line is not None and end_line is not None:
                # 注意：行号从1开始，但列表索引从0开始
                start_idx = max(0, start_line - 1)
                end_idx = min(len(lines), end_line)
                content = ''.join(lines[start_idx:end_idx])
            elif start_line is not None:
                start_idx = max(0, start_line - 1)
                content = ''.join(lines[start_idx:])
            elif end_line is not None:
                end_idx = min(len(lines), end_line)
                content = ''.join(lines[:end_idx])
            else:
                content = ''.join(lines)
                
            result = {
                'success': True,
                'file_path': file_path,
                'content': content,
                'start_line': start_line,
                'end_line': end_line
            }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"获取文件内容时出错: {e}")
        error_result = {
            'success': False,
            'error': str(e),
            'file_path': file_path,
            'content': ''
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

@mcp.tool()
async def get_function_details(function_name: str, file_path: Optional[str] = None) -> str:
    """
    获取函数的详细信息
    
    Args:
        function_name: 函数名称
        file_path: 文件路径（可选，如果不指定则搜索所有文件）
        
    Returns:
        函数详细信息的JSON字符串
    """
    try:
        # 直接创建数据库实例，不依赖全局变量
        config = load_ai_editor_config()
        db_file = config.get('database', {}).get('file', 'search.db')
        if not os.path.isabs(db_file):
            db_file = os.path.abspath(db_file)
        
        db = CodeDatabase(db_file)
        functions = db.search_functions(function_name)
        
        result = {
            'success': True,
            'function_name': function_name,
            'file_path': file_path,
            'matches': functions
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"获取函数详情时出错: {e}")
        error_result = {
            'success': False,
            'error': str(e),
            'function_name': function_name,
            'file_path': file_path
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

@mcp.tool()
async def get_database_stats() -> str:
    """
    获取数据库统计信息
    
    Returns:
        包含数据库统计信息的JSON字符串
    """
    try:
        # 使用绝对路径作为基准目录
        base_dir = Path(__file__).parent.absolute()
        config_path = base_dir / "mcp_config.yaml"
        
        # 记录调试信息
        logger.debug(f"get_database_stats - 基准目录: {base_dir}")
        logger.debug(f"get_database_stats - 配置文件路径: {config_path}")
        logger.debug(f"get_database_stats - 当前工作目录: {os.getcwd()}")
        
        # 加载配置
        config = load_ai_editor_config(str(config_path))
        
        # 获取数据库路径
        db_path = config.get('database', {}).get('file', 'search.db')
        
        # 确保使用绝对路径
        if not os.path.isabs(db_path):
            db_path = str(base_dir / db_path)
        
        logger.debug(f"get_database_stats - 配置中的数据库文件: {config.get('database', {}).get('file', 'search.db')}")
        logger.debug(f"get_database_stats - 解析后的数据库路径: {db_path}")
        logger.debug(f"get_database_stats - 数据库文件是否存在: {os.path.exists(db_path)}")
        
        if os.path.exists(db_path):
            file_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
            logger.debug(f"get_database_stats - 数据库文件大小: {file_size:.2f} MB")
        else:
            logger.warning(f"get_database_stats - 数据库文件不存在: {db_path}")
        
        # 创建数据库实例并获取统计信息
        db = CodeDatabase(db_path)
        stats = db.get_stats()
        
        logger.debug(f"get_database_stats - 获取到的统计信息: {stats}")
        
        return json.dumps(stats, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"获取数据库统计信息时出错: {e}")
        import traceback
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        return json.dumps({
            "error": str(e),
            "files": 0,
            "functions": 0,
            "classes": 0,
            "database_size_mb": 0
        }, ensure_ascii=False, indent=2)

def signal_handler(signum, frame):
    """
    AI编辑器优化的信号处理器
    优雅地关闭MCP服务器，确保AI编辑器连接正常断开
    
    Args:
        signum: 信号编号
        frame: 当前栈帧
    """
    logger.info(f"🛑 [AI-Editor] 接收到信号 {signum}，正在优雅关闭MCP服务器...")
    
    # 清理资源
    global search_engine, db_manager
    if search_engine:
        logger.info("🔄 [AI-Editor] 清理搜索引擎资源...")
    if db_manager:
        logger.info("🔄 [AI-Editor] 关闭数据库连接...")
        
    logger.info("✅ [AI-Editor] MCP服务器已安全关闭")
    sys.exit(0)

def main():
    """
    AI编辑器专用MCP服务器主函数
    启动优化的FastMCP服务器，专为AI编辑器集成设计
    """
    parser = argparse.ArgumentParser(
        description='AI编辑器专用MCP代码搜索服务器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🤖 AI编辑器支持:
  • Trae AI - 智能代码分析和建议
  • Claude Desktop - 上下文感知搜索  
  • Cursor - 代码补全和重构
  • VS Code - 通用MCP客户端支持

📖 使用示例:
  python fastmcp_server.py --config mcp_config.yaml
  python fastmcp_server.py --test
  python fastmcp_server.py --version
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        default='mcp_config.yaml',
        help='配置文件路径 (默认: mcp_config.yaml)'
    )
    
    parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='测试模式：验证配置和连接'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='store_true',
        help='显示版本信息'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='启用调试模式（详细日志）'
    )
    
    args = parser.parse_args()
    
    # 版本信息
    if args.version:
        print("🤖 AI编辑器专用MCP代码搜索服务器")
        print("版本: 2.0.0")
        print("支持: Trae AI, Claude, Cursor, VS Code")
        print("协议: MCP (Model Context Protocol)")
        return
    
    # 设置信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 初始化AI编辑器优化组件
        config_path = os.path.abspath(args.config)
        
        if not os.path.exists(config_path):
            logger.error(f"❌ 配置文件不存在: {config_path}")
            logger.info("💡 请确保配置文件路径正确，或使用 --config 参数指定")
            sys.exit(1)
            
        logger.info(f"📋 使用配置文件: {config_path}")
        
        # 测试模式
        if args.test:
            logger.info("🧪 [测试模式] 验证AI编辑器MCP服务器配置...")
            initialize_ai_components(config_path)
            logger.info("✅ [测试模式] 配置验证成功，服务器可以正常启动")
            return
            
        # 调试模式
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.info("🐛 [调试模式] 已启用详细日志")
        
        # 初始化组件
        initialize_ai_components(config_path)
        
        # 启动FastMCP服务器
        logger.info("🚀 [AI-Editor] 启动FastMCP服务器...")
        logger.info("🔗 [AI-Editor] 等待AI编辑器连接...")
        logger.info("💡 [AI-Editor] 支持的编辑器: Trae AI, Claude, Cursor, VS Code")
        
        # 运行服务器
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 [AI-Editor] 用户中断，正在关闭服务器...")
    except Exception as e:
        logger.error(f"❌ [AI-Editor] 服务器启动失败: {e}")
        logger.error("💡 请检查配置文件和依赖项，或使用 --test 模式验证配置")
        sys.exit(1)

if __name__ == "__main__":
    main()