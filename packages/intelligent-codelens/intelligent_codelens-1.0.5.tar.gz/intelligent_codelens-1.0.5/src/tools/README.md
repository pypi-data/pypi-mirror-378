# 工具集 (src/tools/)

本目录包含各种实用工具和脚本，用于辅助开发、测试和维护搜索引擎系统。

## 📁 文件说明

### demo.py
**演示和测试工具**
- 提供交互式的搜索引擎演示
- 包含各种功能的测试用例
- 支持批量测试和性能评估

**主要功能**:
```python
def interactive_demo():
    """交互式演示搜索功能"""
    
def batch_test():
    """批量测试搜索性能"""
    
def performance_benchmark():
    """性能基准测试"""
```

**使用方法**:
```bash
# 运行交互式演示
python src/tools/demo.py --interactive

# 运行批量测试
python src/tools/demo.py --batch-test

# 运行性能测试
python src/tools/demo.py --benchmark
```

## 🛠️ 工具功能

### 1. 搜索演示
- **关键词搜索**: 演示基本的关键词搜索功能
- **语义搜索**: 展示基于语义理解的搜索
- **混合搜索**: 结合关键词和语义的搜索模式
- **实时搜索**: 展示实时搜索建议功能

### 2. 性能测试
- **响应时间测试**: 测量搜索响应时间
- **并发测试**: 测试系统并发处理能力
- **内存使用测试**: 监控内存使用情况
- **索引性能测试**: 测试索引构建和更新性能

### 3. 数据管理
- **索引重建**: 重新构建搜索索引
- **数据清理**: 清理无效或过期的索引数据
- **数据导入导出**: 支持索引数据的备份和恢复
- **统计报告**: 生成系统使用统计报告

## 🚀 使用示例

### 基本演示
```python
from src.tools.demo import SearchDemo

# 创建演示实例
demo = SearchDemo()

# 运行基本搜索演示
demo.basic_search_demo()

# 运行语义搜索演示
demo.semantic_search_demo()

# 运行性能测试
demo.performance_test()
```

### 自定义测试
```python
from src.tools.demo import PerformanceTester

# 创建性能测试器
tester = PerformanceTester()

# 自定义测试参数
test_config = {
    'queries': ['function definition', 'class inheritance', 'database connection'],
    'iterations': 100,
    'concurrent_users': 10
}

# 运行测试
results = tester.run_test(test_config)
print(f"平均响应时间: {results['avg_response_time']}ms")
```

### 批量索引
```python
from src.tools.demo import IndexManager

# 创建索引管理器
manager = IndexManager()

# 批量索引目录
directories = [
    '/path/to/project1',
    '/path/to/project2',
    '/path/to/project3'
]

for directory in directories:
    manager.index_directory(directory)
    print(f"已索引: {directory}")
```

## 📊 测试报告

### 性能基准
工具会生成详细的性能报告：

```
=== 搜索性能测试报告 ===
测试时间: 2024-01-20 10:30:00
测试查询数: 1000
并发用户数: 10

响应时间统计:
- 平均响应时间: 45ms
- 最小响应时间: 12ms
- 最大响应时间: 156ms
- 95%分位数: 89ms

内存使用:
- 峰值内存: 256MB
- 平均内存: 128MB

索引统计:
- 总文件数: 15,432
- 总代码行数: 1,234,567
- 索引大小: 45MB
```

### 准确性测试
```
=== 搜索准确性测试报告 ===
测试查询: "database connection function"

关键词搜索结果:
- 相关结果: 85/100
- 准确率: 85%

语义搜索结果:
- 相关结果: 92/100
- 准确率: 92%

混合搜索结果:
- 相关结果: 95/100
- 准确率: 95%
```

## 🔧 配置选项

### 演示配置
```python
DEMO_CONFIG = {
    'search_engine': {
        'database_path': 'search.db',
        'max_results': 50
    },
    'performance_test': {
        'iterations': 100,
        'concurrent_users': 5,
        'timeout': 30
    },
    'output': {
        'verbose': True,
        'save_results': True,
        'report_format': 'html'
    }
}
```

### 测试数据
```python
TEST_QUERIES = [
    "function definition",
    "class inheritance", 
    "database connection",
    "error handling",
    "API endpoint",
    "data validation",
    "user authentication",
    "file processing"
]
```

## 🧪 开发工具

### 调试模式
```bash
# 启用调试模式
python src/tools/demo.py --debug

# 详细日志输出
python src/tools/demo.py --verbose

# 保存测试结果
python src/tools/demo.py --save-results
```

### 自定义扩展
```python
from src.tools.demo import BaseTool

class CustomTool(BaseTool):
    """自定义工具示例"""
    
    def __init__(self):
        super().__init__()
        self.name = "CustomTool"
    
    def run(self, **kwargs):
        """运行自定义工具"""
        print(f"运行 {self.name}")
        # 实现自定义逻辑
        return self.process_data(kwargs)
    
    def process_data(self, data):
        """处理数据的具体实现"""
        # 自定义数据处理逻辑
        pass

# 注册自定义工具
tool = CustomTool()
tool.run(query="test query")
```

## 📝 最佳实践

### 1. 测试策略
- 定期运行性能测试
- 使用真实数据进行测试
- 测试不同规模的代码库
- 监控长期性能趋势

### 2. 结果分析
- 保存测试结果用于对比
- 分析性能瓶颈
- 识别准确性问题
- 优化搜索算法

### 3. 工具维护
- 定期更新测试用例
- 添加新的测试场景
- 优化工具性能
- 完善错误处理

### 4. 文档更新
- 记录工具使用方法
- 更新配置说明
- 添加使用示例
- 维护测试报告模板