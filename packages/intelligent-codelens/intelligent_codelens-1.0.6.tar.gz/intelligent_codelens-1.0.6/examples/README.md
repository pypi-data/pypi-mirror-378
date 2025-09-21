# 示例代码 (examples/)

本目录包含各种使用示例和演示代码，帮助用户快速了解和使用搜索引擎的各种功能。

## 📁 文件说明

### api_client_example.py
**REST API客户端示例**
- 演示如何使用REST API进行代码搜索
- 包含各种搜索模式的示例
- 展示错误处理和结果解析

**使用方法**:
```bash
python examples/api_client_example.py
```

### mcp_client_example.py
**MCP客户端示例**
- 演示如何连接和使用MCP服务器
- 展示各种MCP工具的调用方法
- 包含异步调用示例

**使用方法**:
```bash
python examples/mcp_client_example.py
```

### demo_repo/
**演示代码库**
- 包含多种编程语言的示例文件
- 用于测试搜索功能的完整性
- 展示不同代码结构的索引效果

**包含文件**:
- `admin_view.py` - Python管理界面示例
- `order_service.py` - 订单服务示例
- `payment_dao.py` - 支付数据访问对象
- `user_auth.py` - 用户认证模块

## 🚀 快速开始

### 1. 启动搜索引擎服务
```bash
# 启动REST API服务
python src/api/api_server.py

# 或启动MCP服务
python src/mcp/mcp_server.py
```

### 2. 运行示例
```bash
# 运行API客户端示例
python examples/api_client_example.py

# 运行MCP客户端示例
python examples/mcp_client_example.py
```

### 3. 索引演示代码库
```bash
python src/core/indexer.py examples/demo_repo/
```

## 📖 示例详解

### API客户端示例功能
- **基本搜索**: 关键词搜索演示
- **语义搜索**: 基于含义的搜索
- **混合搜索**: 结合关键词和语义的搜索
- **文件索引**: 添加新文件到索引
- **统计查询**: 获取索引统计信息

### MCP客户端示例功能
- **工具发现**: 列出可用的MCP工具
- **代码搜索**: 使用MCP工具进行搜索
- **代码分析**: 分析代码结构和信息
- **批量操作**: 批量索引和搜索操作

## 🔧 自定义示例

### 创建自己的API客户端
```python
import requests

class CustomSearchClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def search(self, query, mode='hybrid'):
        response = requests.get(
            f"{self.base_url}/search",
            params={'q': query, 'mode': mode}
        )
        return response.json()

# 使用示例
client = CustomSearchClient()
results = client.search("database connection")
```

### 创建自己的MCP客户端
```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def custom_mcp_client():
    server_params = StdioServerParameters(
        command="python",
        args=["src/mcp/mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 调用搜索工具
            result = await session.call_tool(
                "search_code",
                {"query": "function definition"}
            )
            print(result)

# 运行示例
asyncio.run(custom_mcp_client())
```

## 🧪 测试示例

所有示例都包含基本的测试功能：

```bash
# 测试API客户端
python -m pytest examples/test_api_client.py

# 测试MCP客户端
python -m pytest examples/test_mcp_client.py
```

## 📝 贡献指南

### 添加新示例
1. 创建新的示例文件
2. 添加详细的注释和文档字符串
3. 包含错误处理和边界情况
4. 更新本README文档
5. 添加相应的测试

### 示例代码规范
- 使用清晰的变量名和函数名
- 包含完整的错误处理
- 添加详细的注释说明
- 提供使用说明和预期输出