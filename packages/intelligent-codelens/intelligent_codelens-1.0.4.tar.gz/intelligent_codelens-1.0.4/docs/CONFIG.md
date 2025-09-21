# 语义搜索引擎配置文档

## 概述

本文档详细说明了语义搜索引擎的所有配置选项、参数边界和使用方法。

## 配置文件结构

### 主配置文件 (config.yaml)

```yaml
database:
  path: "search.db"
  timeout: 30
  
search:
  default_limit: 50
  max_limit: 1000
  cache_enabled: true
  cache_ttl: 3600
  similarity_threshold: 0.3
  
  # 权重配置
  weights:
    exact_match: 10.0
    partial_match: 5.0
    semantic_similarity: 3.0
    keyword_bonus: 2.0
    language_preference: 1.5
    
  # 语言偏好
  language_preferences:
    python: 1.0
    javascript: 0.9
    typescript: 0.9
    java: 0.8
    cpp: 0.7
    c: 0.7
    go: 0.8
    rust: 0.8
    
  # 搜索策略
  strategies:
    enable_fuzzy_search: true
    enable_semantic_search: true
    enable_keyword_expansion: true
    enable_chinese_support: true
```

### 关键词配置文件 (keywords.yaml)

```yaml
# 编程语言关键词
languages:
  python: ["python", "py", "django", "flask", "pandas", "numpy"]
  javascript: ["javascript", "js", "node", "react", "vue", "angular"]
  typescript: ["typescript", "ts", "interface", "type", "generic"]
  java: ["java", "spring", "maven", "gradle", "junit"]
  cpp: ["cpp", "c++", "stl", "boost", "cmake"]
  
# 编程概念关键词
concepts:
  data_structures: ["array", "list", "dict", "set", "tree", "graph", "hash"]
  algorithms: ["sort", "search", "recursion", "dynamic", "greedy", "divide"]
  patterns: ["singleton", "factory", "observer", "strategy", "decorator"]
  
# 框架和库关键词
frameworks:
  web: ["django", "flask", "express", "spring", "rails"]
  frontend: ["react", "vue", "angular", "svelte", "jquery"]
  mobile: ["react-native", "flutter", "ionic", "xamarin"]
  
# 数据库关键词
databases:
  sql: ["mysql", "postgresql", "sqlite", "oracle", "mssql"]
  nosql: ["mongodb", "redis", "cassandra", "elasticsearch"]
  
# 工具和技术关键词
tools:
  version_control: ["git", "svn", "mercurial"]
  build_tools: ["maven", "gradle", "webpack", "gulp", "grunt"]
  testing: ["junit", "pytest", "jest", "mocha", "cypress"]
  
# 自定义关键词（用户可扩展）
custom:
  business_logic: []
  domain_specific: []
```

## 配置参数详解

### 数据库配置 (database)

| 参数 | 类型 | 默认值 | 边界 | 说明 |
|------|------|--------|------|------|
| path | string | "search.db" | 有效文件路径 | 数据库文件路径 |
| timeout | int | 30 | 1-300 | 数据库连接超时时间（秒） |

### 搜索配置 (search)

| 参数 | 类型 | 默认值 | 边界 | 说明 |
|------|------|--------|------|------|
| default_limit | int | 50 | 1-1000 | 默认搜索结果数量 |
| max_limit | int | 1000 | 1-10000 | 最大搜索结果数量 |
| cache_enabled | bool | true | true/false | 是否启用搜索缓存 |
| cache_ttl | int | 3600 | 60-86400 | 缓存生存时间（秒） |
| similarity_threshold | float | 0.3 | 0.0-1.0 | 相似度阈值 |

### 权重配置 (weights)

| 参数 | 类型 | 默认值 | 边界 | 说明 |
|------|------|--------|------|------|
| exact_match | float | 10.0 | 0.1-100.0 | 精确匹配权重 |
| partial_match | float | 5.0 | 0.1-50.0 | 部分匹配权重 |
| semantic_similarity | float | 3.0 | 0.1-20.0 | 语义相似度权重 |
| keyword_bonus | float | 2.0 | 0.1-10.0 | 关键词奖励权重 |
| language_preference | float | 1.5 | 0.1-5.0 | 语言偏好权重 |

### 语言偏好配置 (language_preferences)

| 参数 | 类型 | 默认值 | 边界 | 说明 |
|------|------|--------|------|------|
| python | float | 1.0 | 0.1-2.0 | Python语言偏好系数 |
| javascript | float | 0.9 | 0.1-2.0 | JavaScript语言偏好系数 |
| typescript | float | 0.9 | 0.1-2.0 | TypeScript语言偏好系数 |
| java | float | 0.8 | 0.1-2.0 | Java语言偏好系数 |
| cpp | float | 0.7 | 0.1-2.0 | C++语言偏好系数 |
| c | float | 0.7 | 0.1-2.0 | C语言偏好系数 |
| go | float | 0.8 | 0.1-2.0 | Go语言偏好系数 |
| rust | float | 0.8 | 0.1-2.0 | Rust语言偏好系数 |

### 搜索策略配置 (strategies)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| enable_fuzzy_search | bool | true | 启用模糊搜索 |
| enable_semantic_search | bool | true | 启用语义搜索 |
| enable_keyword_expansion | bool | true | 启用关键词扩展 |
| enable_chinese_support | bool | true | 启用中文支持 |

## 关键词配置详解

### 关键词权重系统

每个关键词都有对应的权重值，用于计算搜索相关性：

```yaml
keyword_weights:
  # 高权重关键词（3.0-5.0）
  function: 3.0
  class: 3.0
  method: 3.0
  api: 4.0
  database: 4.0
  
  # 中权重关键词（1.5-2.9）
  variable: 2.0
  parameter: 2.0
  return: 2.0
  loop: 2.5
  condition: 2.5
  
  # 低权重关键词（0.5-1.4）
  import: 1.0
  export: 1.0
  const: 1.0
  let: 1.0
  var: 1.0
```

### 中英文术语映射

系统支持中英文术语的自动映射：

```yaml
term_mappings:
  function: ["函数", "方法", "func", "def"]
  class: ["类", "对象", "cls"]
  variable: ["变量", "var"]
  parameter: ["参数", "param", "arg"]
  return: ["返回", "返回值"]
  loop: ["循环", "遍历"]
  condition: ["条件", "判断"]
  database: ["数据库", "db"]
  api: ["接口", "API"]
  server: ["服务器", "服务端"]
  client: ["客户端", "前端"]
```

## 配置边界和限制

### 性能相关边界

1. **搜索结果数量**
   - 最小值：1
   - 最大值：10000
   - 推荐值：50-500

2. **缓存配置**
   - 最小TTL：60秒
   - 最大TTL：86400秒（24小时）
   - 推荐TTL：3600秒（1小时）

3. **相似度阈值**
   - 最小值：0.0（返回所有结果）
   - 最大值：1.0（只返回完全匹配）
   - 推荐值：0.2-0.5

### 内存使用边界

1. **关键词数量**
   - 每个类别最大关键词数：1000
   - 总关键词数量上限：10000
   - 推荐每个类别：50-200个关键词

2. **权重配置**
   - 权重值范围：0.1-100.0
   - 推荐权重范围：0.5-10.0

### 文件大小限制

1. **配置文件大小**
   - config.yaml：最大1MB
   - keywords.yaml：最大5MB
   - 推荐大小：config.yaml < 100KB，keywords.yaml < 1MB

## 配置最佳实践

### 1. 性能优化配置

```yaml
search:
  default_limit: 50        # 平衡性能和结果完整性
  cache_enabled: true      # 启用缓存提高响应速度
  cache_ttl: 3600         # 1小时缓存，平衡实时性和性能
  similarity_threshold: 0.3 # 过滤低相关性结果
```

### 2. 精确度优化配置

```yaml
search:
  weights:
    exact_match: 10.0      # 提高精确匹配权重
    partial_match: 3.0     # 降低部分匹配权重
    semantic_similarity: 2.0 # 适度语义匹配
```

### 3. 多语言支持配置

```yaml
search:
  strategies:
    enable_chinese_support: true
    enable_keyword_expansion: true
  
  language_preferences:
    python: 1.0
    javascript: 0.9
    # 根据项目主要语言调整权重
```

## 配置验证

系统会在启动时验证配置的有效性：

1. **数值范围检查**：确保所有数值参数在有效范围内
2. **文件路径检查**：验证数据库路径的可访问性
3. **关键词格式检查**：验证关键词配置的格式正确性
4. **权重一致性检查**：确保权重配置的逻辑一致性

## 故障排除

### 常见配置错误

1. **数据库路径错误**
   ```
   错误：database.path: "/invalid/path/search.db"
   解决：使用相对路径或确保目录存在
   ```

2. **权重值超出范围**
   ```
   错误：weights.exact_match: 150.0
   解决：将值调整到0.1-100.0范围内
   ```

3. **关键词格式错误**
   ```
   错误：keywords应为列表格式
   解决：确保使用YAML列表语法
   ```

### 性能问题诊断

1. **搜索速度慢**
   - 检查default_limit是否过大
   - 确认cache_enabled为true
   - 调整similarity_threshold提高过滤效果

2. **内存使用过高**
   - 减少关键词数量
   - 降低cache_ttl值
   - 调整max_limit限制

## 配置示例

### 轻量级配置（适合小项目）

```yaml
database:
  path: "search.db"
  
search:
  default_limit: 20
  max_limit: 100
  cache_enabled: false
  similarity_threshold: 0.5
```

### 高性能配置（适合大项目）

```yaml
database:
  path: "search.db"
  timeout: 60
  
search:
  default_limit: 100
  max_limit: 1000
  cache_enabled: true
  cache_ttl: 7200
  similarity_threshold: 0.2
  
  weights:
    exact_match: 15.0
    partial_match: 8.0
    semantic_similarity: 5.0
```

### 多语言配置（适合国际化项目）

```yaml
search:
  strategies:
    enable_chinese_support: true
    enable_keyword_expansion: true
    
  language_preferences:
    python: 1.0
    javascript: 1.0
    typescript: 1.0
    java: 0.9
    go: 0.9
```