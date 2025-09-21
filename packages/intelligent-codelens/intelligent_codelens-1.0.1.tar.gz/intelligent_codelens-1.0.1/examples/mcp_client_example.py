#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 客户端示例
用于测试代码搜索MCP服务器的功能
"""

import asyncio
import json
import logging
from typing import Any, Dict, List
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPClientExample:
    """MCP客户端示例"""
    
    def __init__(self):
        """初始化客户端"""
        self.session = None
    
    async def connect(self, server_command: List[str]):
        """
        连接到MCP服务器
        
        Args:
            server_command: 服务器启动命令
        """
        try:
            # 创建stdio客户端
            async with stdio_client(server_command) as (read, write):
                # 创建会话
                async with ClientSession(read, write) as session:
                    self.session = session
                    
                    # 初始化会话
                    await session.initialize()
                    
                    logger.info("成功连接到MCP服务器")
                    
                    # 运行测试
                    await self.run_tests()
                    
        except Exception as e:
            logger.error(f"连接服务器失败: {e}")
    
    async def run_tests(self):
        """运行测试用例"""
        logger.info("开始运行MCP客户端测试...")
        
        # 测试1: 列出可用工具
        await self.test_list_tools()
        
        # 测试2: 搜索代码
        await self.test_search_code()
        
        # 测试3: 获取文件内容
        await self.test_get_file_content()
        
        # 测试4: 获取函数详情
        await self.test_get_function_details()
        
        # 测试5: 获取数据库统计
        await self.test_get_database_stats()
        
        # 测试6: 列出资源
        await self.test_list_resources()
        
        logger.info("所有测试完成")
    
    async def test_list_tools(self):
        """测试列出工具"""
        logger.info("测试: 列出可用工具")
        
        try:
            tools = await self.session.list_tools()
            logger.info(f"找到 {len(tools)} 个工具:")
            
            for tool in tools:
                logger.info(f"  - {tool.name}: {tool.description}")
                
        except Exception as e:
            logger.error(f"列出工具失败: {e}")
    
    async def test_search_code(self):
        """测试代码搜索"""
        logger.info("测试: 搜索代码")
        
        test_queries = [
            "支付状态",
            "create_payment",
            "PaymentDAO",
            "update_order_status"
        ]
        
        for query in test_queries:
            try:
                logger.info(f"搜索: '{query}'")
                
                result = await self.session.call_tool(
                    "search_code",
                    {"query": query, "limit": 5}
                )
                
                if result.content:
                    logger.info(f"搜索结果:\n{result.content[0].text}")
                else:
                    logger.warning("无搜索结果")
                    
            except Exception as e:
                logger.error(f"搜索 '{query}' 失败: {e}")
    
    async def test_get_file_content(self):
        """测试获取文件内容"""
        logger.info("测试: 获取文件内容")
        
        test_files = [
            "examples/demo_repo/payment_dao.py",
            "mcp_server.py"
        ]
        
        for file_path in test_files:
            try:
                logger.info(f"获取文件: {file_path}")
                
                result = await self.session.call_tool(
                    "get_file_content",
                    {
                        "file_path": file_path,
                        "start_line": 1,
                        "end_line": 20
                    }
                )
                
                if result.content:
                    logger.info(f"文件内容 (前20行):\n{result.content[0].text[:200]}...")
                else:
                    logger.warning("无文件内容")
                    
            except Exception as e:
                logger.error(f"获取文件 '{file_path}' 失败: {e}")
    
    async def test_get_function_details(self):
        """测试获取函数详情"""
        logger.info("测试: 获取函数详情")
        
        test_functions = [
            "create_payment",
            "set_payment_paid",
            "get_payment_by_order"
        ]
        
        for func_name in test_functions:
            try:
                logger.info(f"获取函数详情: {func_name}")
                
                result = await self.session.call_tool(
                    "get_function_details",
                    {"function_name": func_name}
                )
                
                if result.content:
                    logger.info(f"函数详情:\n{result.content[0].text[:300]}...")
                else:
                    logger.warning("无函数详情")
                    
            except Exception as e:
                logger.error(f"获取函数 '{func_name}' 详情失败: {e}")
    
    async def test_get_database_stats(self):
        """测试获取数据库统计"""
        logger.info("测试: 获取数据库统计")
        
        try:
            result = await self.session.call_tool(
                "get_database_stats",
                {}
            )
            
            if result.content:
                logger.info(f"数据库统计:\n{result.content[0].text}")
            else:
                logger.warning("无统计信息")
                
        except Exception as e:
            logger.error(f"获取数据库统计失败: {e}")
    
    async def test_list_resources(self):
        """测试列出资源"""
        logger.info("测试: 列出资源")
        
        try:
            resources = await self.session.list_resources()
            logger.info(f"找到 {len(resources)} 个资源:")
            
            for resource in resources:
                logger.info(f"  - {resource.name}: {resource.description}")
                
                # 尝试读取资源
                try:
                    content = await self.session.read_resource(resource.uri)
                    logger.info(f"    内容长度: {len(content)} 字符")
                except Exception as e:
                    logger.error(f"    读取资源失败: {e}")
                    
        except Exception as e:
            logger.error(f"列出资源失败: {e}")

async def main():
    """主函数"""
    logger.info("=== MCP 客户端测试 ===")
    
    # MCP服务器启动命令
    server_command = ["python3", "mcp_server.py"]
    
    # 创建客户端并连接
    client = MCPClientExample()
    await client.connect(server_command)

if __name__ == "__main__":
    asyncio.run(main())