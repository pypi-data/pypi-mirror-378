# 语义搜索引擎使用指南

## 目录

1. [快速开始](#快速开始)
2. [基本使用](#基本使用)
3. [高级配置](#高级配置)
4. [最佳实践](#最佳实践)
5. [常见问题](#常见问题)
6. [性能优化](#性能优化)
7. [故障排除](#故障排除)
8. [扩展开发](#扩展开发)

---

## 快速开始

### 1. 环境要求

- **Python版本**: 3.7+
- **操作系统**: Windows, macOS, Linux
- **内存**: 建议 4GB+
- **磁盘空间**: 至少 1GB 可用空间

### 2. 安装依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt
```

### 3. 初始化配置

```bash
# 复制默认配置文件
cp config/config.yaml config.yaml

# 编辑配置文件（可选）
vim config.yaml
```

### 4. 第一次使用

```python
from src.core.semantic_search import SemanticSearchEngine

# 创建搜索引擎实例
engine = SemanticSearchEngine()

# 执行第一次搜索
results = engine.search("数据库连接")

# 查看结果
for result in results:
    print(f"函数: {result['name']}")
    print(f"文件: {result['file_path']}")
    print(f"评分: {result['score']}")
    print("-" * 40)
```

---

## 基本使用

### 搜索功能

#### 1. 基本搜索

```python
# 中文搜索
results = engine.search("数据库连接")

# 英文搜索
results = engine.search("database connection")

# 混合搜索
results = engine.search("database 连接 function")
```

#### 2. 限制结果数量

```python
# 限制返回10个结果
results = engine.search("function", limit=10)

# 获取所有结果（使用配置中的默认限制）
results = engine.search("function")
```

#### 3. 不同类型的搜索

```python
# 搜索函数
results = engine.search("find function definition")

# 搜索类
results = engine.search("class inheritance")

# 搜索概念
results = engine.search("authentication logic")

# 搜索文件
results = engine.search("config file")
```

### 关键词管理

#### 1. 查看关键词权重

```python
# 查看特定关键词权重
weight = engine.get_keyword_weight("function")
print(f"关键词 'function' 的权重: {weight}")

# 查看不存在的关键词（返回默认权重）
weight = engine.get_keyword_weight("unknown_keyword")
print(f"未知关键词的权重: {weight}")
```

#### 2. 自动提取关键词

```python
# 从代码库提取关键词
keywords = engine.auto_extract_keywords_from_codebase()

# 查看提取结果
print("提取的函数关键词:", keywords['auto_functions'])
print("提取的类关键词:", keywords['auto_classes'])
print("提取的概念关键词:", keywords['auto_concepts'])

# 提取并更新配置文件
keywords = engine.auto_extract_keywords_from_codebase(update_config=True)
```

### 缓存管理

```python
# 清空搜索缓存
engine.clear_cache()

# 在配置更改后清空缓存
engine.clear_cache()
```

---

## 高级配置

### 1. 配置文件结构

```yaml
# config.yaml
database:
  path: "search.db"
  
search:
  default_limit: 50
  max_limit: 1000
  cache_size: 1000
  
keywords:
  config_file: "config/keywords.yaml"
  auto_extract: true
  
weights:
  function: 3.0
  class: 2.5
  concept: 2.0
  
term_mappings:
  function: ["函数", "方法", "func", "def"]
  class: ["类", "对象", "cls"]
```

### 2. 关键词配置

```yaml
# config/keywords.yaml
keyword_weights:
  # 编程概念
  function: 3.0
  class: 2.5
  method: 2.8
  variable: 1.5
  
  # 数据库相关
  database: 4.0
  connection: 3.5
  query: 3.0
  
  # 网络相关
  api: 3.5
  http: 2.5
  request: 2.0

# 术语映射
term_mappings:
  function: ["函数", "方法", "func", "def", "method"]
  class: ["类", "对象", "cls", "class"]
  database: ["数据库", "db", "数据存储"]
  api: ["接口", "API", "应用程序接口"]
```

### 3. 自定义配置路径

```python
# 使用自定义配置文件
engine = SemanticSearchEngine("custom_config.yaml")

# 使用环境变量指定配置
import os
config_path = os.getenv('SEARCH_CONFIG', 'config.yaml')
engine = SemanticSearchEngine(config_path)
```

### 4. 动态配置更新

```python
# 修改配置后重新加载
engine.clear_cache()  # 清空缓存以应用新配置

# 或者重新创建引擎实例
engine = SemanticSearchEngine("updated_config.yaml")
```

---

## 最佳实践

### 1. 搜索策略

#### 使用具体的关键词

```python
# 好的做法：使用具体关键词
results = engine.search("database connection pool")

# 避免：过于宽泛的搜索
results = engine.search("code")
```

#### 组合中英文关键词

```python
# 利用中英文映射提高搜索准确性
results = engine.search("用户 authentication 验证")
```

#### 使用意图明确的查询

```python
# 明确搜索意图
results = engine.search("find login function")
results = engine.search("class for user management")
results = engine.search("database connection configuration")
```

### 2. 性能优化

#### 合理设置结果限制

```python
# 对于快速预览，使用较小的限制
results = engine.search("function", limit=10)

# 对于详细分析，使用较大的限制
results = engine.search("function", limit=100)
```

#### 重用引擎实例

```python
# 好的做法：重用实例
engine = SemanticSearchEngine()
for query in queries:
    results = engine.search(query)

# 避免：频繁创建实例
for query in queries:
    engine = SemanticSearchEngine()  # 不推荐
    results = engine.search(query)
```

#### 定期清理缓存

```python
# 在长时间运行的应用中定期清理
import time

last_cache_clear = time.time()
for query in continuous_queries:
    results = engine.search(query)
    
    # 每小时清理一次缓存
    if time.time() - last_cache_clear > 3600:
        engine.clear_cache()
        last_cache_clear = time.time()
```

### 3. 关键词管理

#### 定期更新关键词

```python
# 定期从代码库提取新关键词
keywords = engine.auto_extract_keywords_from_codebase(update_config=True)
print(f"更新了 {len(keywords['auto_functions'])} 个函数关键词")
```

#### 自定义权重调优

```python
# 根据项目特点调整权重
# 在 keywords.yaml 中：
keyword_weights:
  # 如果项目主要是API开发，提高API相关权重
  api: 5.0
  endpoint: 4.5
  request: 4.0
  
  # 如果项目主要是数据处理，提高数据相关权重
  data: 5.0
  process: 4.5
  transform: 4.0
```

### 4. 错误处理

```python
def safe_search(engine, query, max_retries=3):
    """安全的搜索函数，包含重试机制"""
    for attempt in range(max_retries):
        try:
            results = engine.search(query)
            return results
        except Exception as e:
            print(f"搜索失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(1)  # 等待1秒后重试
```

---

## 常见问题

### Q1: 搜索结果为空怎么办？

**A1:** 检查以下几点：

1. **确认数据库中有数据**
   ```python
   cursor = engine.db.conn.cursor()
   cursor.execute("SELECT COUNT(*) FROM functions")
   count = cursor.fetchone()[0]
   print(f"数据库中有 {count} 个函数")
   ```

2. **尝试更宽泛的搜索词**
   ```python
   # 如果 "specific_function" 没结果，尝试：
   results = engine.search("function")
   ```

3. **检查关键词权重**
   ```python
   weight = engine.get_keyword_weight("your_keyword")
   print(f"关键词权重: {weight}")
   ```

### Q2: 搜索速度慢怎么办？

**A2:** 优化建议：

1. **减少结果数量**
   ```python
   results = engine.search("query", limit=20)  # 而不是默认的50
   ```

2. **清理缓存**
   ```python
   engine.clear_cache()
   ```

3. **检查数据库大小**
   ```python
   import os
   db_size = os.path.getsize("search.db") / (1024 * 1024)  # MB
   print(f"数据库大小: {db_size:.2f} MB")
   ```

### Q3: 中文搜索效果不好？

**A3:** 改进方法：

1. **更新术语映射**
   ```yaml
   # 在 keywords.yaml 中添加更多中文映射
   term_mappings:
     function: ["函数", "方法", "功能", "func"]
     database: ["数据库", "数据存储", "db", "存储"]
   ```

2. **使用混合搜索**
   ```python
   results = engine.search("数据库 database 连接 connection")
   ```

### Q4: 配置文件找不到？

**A4:** 检查配置文件路径：

```python
# 查看当前使用的配置文件
print(f"配置文件路径: {engine.config_file}")

# 手动指定配置文件
engine = SemanticSearchEngine("path/to/your/config.yaml")
```

---

## 性能优化

### 1. 数据库优化

#### 定期重建索引

```python
# 重建数据库索引（需要直接访问数据库）
cursor = engine.db.conn.cursor()
cursor.execute("REINDEX")
engine.db.conn.commit()
```

#### 数据库维护

```python
# 清理数据库
cursor = engine.db.conn.cursor()
cursor.execute("VACUUM")
engine.db.conn.commit()
```

### 2. 内存优化

#### 监控内存使用

```python
import psutil
import os

def check_memory_usage():
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"当前内存使用: {memory_mb:.2f} MB")

# 在搜索前后检查内存
check_memory_usage()
results = engine.search("query")
check_memory_usage()
```

#### 批量处理优化

```python
def batch_search(engine, queries, batch_size=10):
    """批量搜索，定期清理缓存"""
    results = []
    for i, query in enumerate(queries):
        result = engine.search(query)
        results.append(result)
        
        # 每处理一批后清理缓存
        if (i + 1) % batch_size == 0:
            engine.clear_cache()
    
    return results
```

### 3. 搜索优化

#### 预热搜索

```python
# 预热常用搜索，提高后续搜索速度
common_queries = ["function", "class", "database", "api"]
for query in common_queries:
    engine.search(query, limit=5)  # 小批量预热
```

#### 智能缓存策略

```python
class SmartSearchEngine:
    def __init__(self, config_path=None):
        self.engine = SemanticSearchEngine(config_path)
        self.search_count = 0
        
    def search(self, query, limit=None):
        self.search_count += 1
        
        # 每100次搜索清理一次缓存
        if self.search_count % 100 == 0:
            self.engine.clear_cache()
            
        return self.engine.search(query, limit)
```

---

## 故障排除

### 1. 常见错误及解决方案

#### 配置文件错误

```python
# 错误: FileNotFoundError: 配置文件不存在
try:
    engine = SemanticSearchEngine("nonexistent.yaml")
except FileNotFoundError as e:
    print(f"配置文件不存在: {e}")
    # 使用默认配置
    engine = SemanticSearchEngine()
```

#### 数据库连接错误

```python
# 错误: sqlite3.OperationalError
try:
    results = engine.search("query")
except sqlite3.OperationalError as e:
    print(f"数据库错误: {e}")
    # 重新初始化数据库
    engine.db._init_database()
```

#### 内存不足错误

```python
# 错误: MemoryError
try:
    results = engine.search("query", limit=10000)
except MemoryError:
    print("内存不足，减少结果数量")
    results = engine.search("query", limit=100)
```

### 2. 调试技巧

#### 启用详细日志

```python
import logging

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)

# 查看搜索过程
results = engine.search("query")
```

#### 查看查询预处理结果

```python
# 查看查询是如何被处理的
processed = engine._preprocess_query("数据库连接函数")
print("预处理结果:", processed)

# 查看意图检测
intent = engine._detect_intent("find database function")
print("检测到的意图:", intent)
```

#### 分析搜索结果

```python
def analyze_results(results):
    """分析搜索结果的分布"""
    if not results:
        print("没有搜索结果")
        return
    
    # 按类型分组
    by_type = {}
    for result in results:
        result_type = result.get('type', 'unknown')
        by_type[result_type] = by_type.get(result_type, 0) + 1
    
    print("结果类型分布:")
    for type_name, count in by_type.items():
        print(f"  {type_name}: {count}")
    
    # 评分分布
    scores = [r['score'] for r in results]
    print(f"评分范围: {min(scores):.2f} - {max(scores):.2f}")
    print(f"平均评分: {sum(scores)/len(scores):.2f}")

# 使用示例
results = engine.search("database")
analyze_results(results)
```

---

## 扩展开发

### 1. 自定义搜索引擎

```python
class CustomSearchEngine(SemanticSearchEngine):
    """自定义搜索引擎，添加额外功能"""
    
    def __init__(self, config_path=None):
        super().__init__(config_path)
        self.custom_filters = []
    
    def add_filter(self, filter_func):
        """添加自定义过滤器"""
        self.custom_filters.append(filter_func)
    
    def search(self, query, limit=None):
        """重写搜索方法，应用自定义过滤器"""
        results = super().search(query, limit)
        
        # 应用自定义过滤器
        for filter_func in self.custom_filters:
            results = filter_func(results)
        
        return results

# 使用示例
def python_only_filter(results):
    """只返回Python文件的结果"""
    return [r for r in results if r['file_path'].endswith('.py')]

custom_engine = CustomSearchEngine()
custom_engine.add_filter(python_only_filter)
results = custom_engine.search("function")
```

### 2. 自定义关键词提取器

```python
class CustomKeywordExtractor:
    """自定义关键词提取器"""
    
    def __init__(self, engine):
        self.engine = engine
    
    def extract_from_comments(self):
        """从注释中提取关键词"""
        cursor = self.engine.db.conn.cursor()
        cursor.execute("SELECT content FROM comments")
        
        keywords = set()
        for (content,) in cursor.fetchall():
            # 简单的关键词提取逻辑
            words = content.lower().split()
            keywords.update(word for word in words if len(word) > 3)
        
        return list(keywords)
    
    def extract_from_filenames(self):
        """从文件名中提取关键词"""
        cursor = self.engine.db.conn.cursor()
        cursor.execute("SELECT file_path FROM files")
        
        keywords = set()
        for (file_path,) in cursor.fetchall():
            # 从文件名提取关键词
            filename = os.path.basename(file_path)
            name_parts = filename.replace('.', '_').split('_')
            keywords.update(part for part in name_parts if len(part) > 2)
        
        return list(keywords)

# 使用示例
extractor = CustomKeywordExtractor(engine)
comment_keywords = extractor.extract_from_comments()
filename_keywords = extractor.extract_from_filenames()
```

### 3. 集成到其他工具

#### 命令行工具

```python
#!/usr/bin/env python3
"""命令行搜索工具"""

import argparse
import sys
from src.core.semantic_search import SemanticSearchEngine

def main():
    parser = argparse.ArgumentParser(description='语义搜索命令行工具')
    parser.add_argument('query', help='搜索查询')
    parser.add_argument('-l', '--limit', type=int, default=10, help='结果数量限制')
    parser.add_argument('-c', '--config', help='配置文件路径')
    
    args = parser.parse_args()
    
    try:
        engine = SemanticSearchEngine(args.config)
        results = engine.search(args.query, limit=args.limit)
        
        if not results:
            print("没有找到匹配的结果")
            sys.exit(1)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['name']} ({result['type']})")
            print(f"   文件: {result['file_path']}")
            print(f"   评分: {result['score']:.2f}")
            if result['docstring']:
                print(f"   描述: {result['docstring'][:100]}...")
            print()
            
    except Exception as e:
        print(f"搜索失败: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
```

#### Web API

```python
from flask import Flask, request, jsonify
from src.core.semantic_search import SemanticSearchEngine

app = Flask(__name__)
engine = SemanticSearchEngine()

@app.route('/search', methods=['GET'])
def search_api():
    """搜索API端点"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 50, type=int)
    
    if not query:
        return jsonify({'error': '查询参数不能为空'}), 400
    
    try:
        results = engine.search(query, limit=limit)
        return jsonify({
            'query': query,
            'count': len(results),
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/keywords', methods=['GET'])
def keywords_api():
    """关键词API端点"""
    try:
        keywords = engine.auto_extract_keywords_from_codebase()
        return jsonify(keywords)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

---

## 总结

本使用指南涵盖了语义搜索引擎的各个方面，从基本使用到高级配置，从性能优化到扩展开发。通过遵循这些最佳实践和建议，您可以：

1. **快速上手** - 通过快速开始部分立即开始使用
2. **优化性能** - 通过性能优化建议提高搜索效率
3. **解决问题** - 通过故障排除部分快速定位和解决问题
4. **扩展功能** - 通过扩展开发部分添加自定义功能

如果您在使用过程中遇到问题，请参考常见问题部分或查看API文档获取更详细的技术信息。