# 语义搜索引擎 API 文档

## 概述

本文档详细说明了语义搜索引擎的所有公共API方法、参数说明和返回值格式。

## 核心类：SemanticSearchEngine

### 初始化

#### `__init__(config_path: str = None)`

初始化语义搜索引擎实例。

**参数：**
- `config_path` (str, 可选): 配置文件路径。如果未提供，将按以下顺序查找：
  - `config/config.yaml`
  - `config/config.yaml`
  - `config.yaml`

**示例：**
```python
# 使用默认配置
engine = SemanticSearchEngine()

# 使用自定义配置文件
engine = SemanticSearchEngine("custom_config.yaml")
```

**异常：**
- `FileNotFoundError`: 配置文件不存在
- `yaml.YAMLError`: 配置文件格式错误

---

## 搜索方法

### `search(query: str, limit: int = None) -> List[Dict[str, Any]]`

执行语义搜索查询。

**参数：**
- `query` (str): 搜索查询字符串
- `limit` (int, 可选): 返回结果数量限制。如果未提供，使用配置中的默认值

**返回值：**
- `List[Dict[str, Any]]`: 搜索结果列表，每个结果包含以下字段：
  - `id` (int): 结果唯一标识
  - `name` (str): 函数/类名称
  - `type` (str): 类型（function, class, method等）
  - `file_path` (str): 文件路径
  - `start_line` (int): 起始行号
  - `end_line` (int): 结束行号
  - `docstring` (str): 文档字符串
  - `body` (str): 代码内容
  - `score` (float): 相关性评分
  - `language` (str): 编程语言

**示例：**
```python
# 基本搜索
results = engine.search("function definition")

# 限制结果数量
results = engine.search("class inheritance", limit=10)

# 中文搜索
results = engine.search("数据库连接")
```

**搜索结果示例：**
```python
[
    {
        "id": 1,
        "name": "connect_database",
        "type": "function",
        "file_path": "src/database.py",
        "start_line": 15,
        "end_line": 25,
        "docstring": "连接到数据库",
        "body": "def connect_database():\n    ...",
        "score": 8.5,
        "language": "python"
    }
]
```

---

## 关键词管理方法

### `get_keyword_weight(keyword: str) -> float`

获取指定关键词的权重值。

**参数：**
- `keyword` (str): 关键词

**返回值：**
- `float`: 关键词权重值（0.1-100.0）

**示例：**
```python
weight = engine.get_keyword_weight("function")  # 返回: 3.0
weight = engine.get_keyword_weight("unknown")   # 返回: 1.0 (默认权重)
```

### `auto_extract_keywords_from_codebase(update_config: bool = False) -> Dict[str, List[str]]`

从代码库中自动提取关键词。

**参数：**
- `update_config` (bool): 是否将提取的关键词更新到配置文件

**返回值：**
- `Dict[str, List[str]]`: 提取的关键词字典，包含以下类别：
  - `auto_functions`: 从函数名提取的关键词
  - `auto_classes`: 从类名提取的关键词
  - `auto_concepts`: 从文档字符串提取的概念关键词
  - `auto_modules`: 从文件路径提取的模块关键词

**示例：**
```python
# 提取关键词但不更新配置
keywords = engine.auto_extract_keywords_from_codebase()

# 提取关键词并更新配置文件
keywords = engine.auto_extract_keywords_from_codebase(update_config=True)

# 结果示例
{
    "auto_functions": ["connect", "query", "insert", "update"],
    "auto_classes": ["Database", "Connection", "Query"],
    "auto_concepts": ["database", "connection", "sql", "query"],
    "auto_modules": ["db", "models", "utils", "api"]
}
```

---

## 缓存管理方法

### `clear_cache()`

清空搜索结果缓存。

**参数：** 无

**返回值：** 无

**示例：**
```python
engine.clear_cache()
```

---

## 内部方法（高级用法）

### `_preprocess_query(query: str) -> Dict[str, Any]`

预处理搜索查询，提取关键信息。

**参数：**
- `query` (str): 原始查询字符串

**返回值：**
- `Dict[str, Any]`: 预处理结果，包含：
  - `original_query` (str): 原始查询
  - `tokens` (List[str]): 分词结果
  - `keywords` (List[str]): 提取的关键词
  - `intent` (str): 查询意图
  - `concepts` (List[str]): 编程概念
  - `expanded_terms` (List[str]): 扩展术语

**示例：**
```python
processed = engine._preprocess_query("数据库连接函数")
# 结果示例
{
    "original_query": "数据库连接函数",
    "tokens": ["数据库", "连接", "函数"],
    "keywords": ["database", "connection", "function"],
    "intent": "function_search",
    "concepts": ["database", "connection"],
    "expanded_terms": ["db", "connect", "func", "method"]
}
```

### `_detect_intent(query: str) -> str`

检测查询意图。

**参数：**
- `query` (str): 查询字符串

**返回值：**
- `str`: 查询意图类型
  - `function_search`: 搜索函数
  - `class_search`: 搜索类
  - `concept_search`: 搜索概念
  - `file_search`: 搜索文件
  - `general_search`: 通用搜索

**示例：**
```python
intent = engine._detect_intent("find function")  # 返回: "function_search"
intent = engine._detect_intent("class definition")  # 返回: "class_search"
```

### `_build_term_mappings() -> Dict[str, List[str]]`

构建中英文术语映射表。

**参数：** 无

**返回值：**
- `Dict[str, List[str]]`: 术语映射字典

**示例：**
```python
mappings = engine._build_term_mappings()
# 结果示例
{
    "function": ["函数", "方法", "func", "def"],
    "class": ["类", "对象", "cls"],
    "database": ["数据库", "db"]
}
```

---

## 数据库相关方法

### 数据库访问

语义搜索引擎通过 `self.db` 属性访问底层数据库：

```python
# 获取数据库连接
cursor = engine.db.conn.cursor()

# 执行查询
cursor.execute("SELECT COUNT(*) FROM functions")
count = cursor.fetchone()[0]
```

### 数据库统计信息

```python
# 获取函数数量
cursor = engine.db.conn.cursor()
cursor.execute("SELECT COUNT(*) FROM functions")
func_count = cursor.fetchone()[0]

# 获取类数量
cursor.execute("SELECT COUNT(*) FROM classes")
class_count = cursor.fetchone()[0]

# 获取文件数量
cursor.execute("SELECT COUNT(*) FROM files")
file_count = cursor.fetchone()[0]
```

---

## 配置访问

### 访问配置信息

```python
# 获取配置文件路径
config_path = engine.config_file

# 获取完整配置
config = engine.config

# 获取特定配置项
db_config = engine.config.get('database', {})
search_config = engine.config.get('search', {})
```

---

## 错误处理

### 常见异常类型

1. **配置相关异常**
   ```python
   try:
       engine = SemanticSearchEngine("invalid_config.yaml")
   except FileNotFoundError:
       print("配置文件不存在")
   except yaml.YAMLError:
       print("配置文件格式错误")
   ```

2. **搜索相关异常**
   ```python
   try:
       results = engine.search("", limit=-1)
   except ValueError:
       print("无效的搜索参数")
   ```

3. **数据库相关异常**
   ```python
   try:
       keywords = engine.auto_extract_keywords_from_codebase()
   except sqlite3.Error:
       print("数据库访问错误")
   ```

---

## 性能优化建议

### 1. 搜索优化

```python
# 使用适当的结果限制
results = engine.search("query", limit=50)  # 推荐

# 避免过大的结果集
results = engine.search("query", limit=1000)  # 不推荐
```

### 2. 缓存管理

```python
# 定期清理缓存
engine.clear_cache()

# 在配置更改后清理缓存
engine.clear_cache()
```

### 3. 批量操作

```python
# 批量搜索时重用引擎实例
engine = SemanticSearchEngine()
for query in queries:
    results = engine.search(query)
```

---

## 扩展和自定义

### 1. 自定义关键词权重

```python
# 通过配置文件自定义权重
# 在 keywords.yaml 中添加：
keyword_weights:
  custom_keyword: 5.0
```

### 2. 自定义术语映射

```python
# 在配置中添加自定义映射
term_mappings:
  custom_term: ["自定义术语", "custom"]
```

### 3. 扩展搜索策略

```python
# 通过继承扩展功能
class CustomSearchEngine(SemanticSearchEngine):
    def custom_search(self, query: str) -> List[Dict[str, Any]]:
        # 自定义搜索逻辑
        pass
```

---

## 版本兼容性

- **Python版本**: 3.7+
- **依赖库版本**:
  - `jieba >= 0.42.1`
  - `PyYAML >= 5.4.1`
  - `sqlite3` (内置)

---

## 示例代码

### 完整使用示例

```python
from semantic_search import SemanticSearchEngine

# 初始化引擎
engine = SemanticSearchEngine()

# 执行搜索
results = engine.search("数据库连接", limit=10)

# 处理结果
for result in results:
    print(f"函数: {result['name']}")
    print(f"文件: {result['file_path']}")
    print(f"评分: {result['score']}")
    print(f"描述: {result['docstring']}")
    print("-" * 40)

# 获取关键词权重
weight = engine.get_keyword_weight("database")
print(f"关键词权重: {weight}")

# 自动提取关键词
keywords = engine.auto_extract_keywords_from_codebase()
print(f"提取的关键词: {keywords}")

# 清理缓存
engine.clear_cache()
```

### 高级用法示例

```python
# 查询预处理
processed = engine._preprocess_query("find database connection function")
print(f"处理结果: {processed}")

# 意图检测
intent = engine._detect_intent("class inheritance")
print(f"查询意图: {intent}")

# 术语映射
mappings = engine._build_term_mappings()
print(f"术语映射: {mappings}")

# 数据库统计
cursor = engine.db.conn.cursor()
cursor.execute("SELECT COUNT(*) FROM functions")
func_count = cursor.fetchone()[0]
print(f"函数总数: {func_count}")
```