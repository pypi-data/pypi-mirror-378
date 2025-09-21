# 核心模块 (Core Modules)

本目录包含系统的核心功能模块，提供基础的搜索、数据库和配置管理能力。

## 文件说明

### enhanced_search_engine.py
**通用增强搜索引擎**

提供可配置的智能搜索功能，支持多种搜索策略和权重系统。

#### 主要功能
- **多模式搜索**: 支持基础搜索、增强搜索、语义搜索等模式
- **可配置权重系统**: 支持内容匹配、路径匹配、语言特定等权重配置
- **查询意图识别**: 自动识别查询意图（如何做、定义、示例、调试等）
- **代码类型检测**: 识别函数、类、变量等不同代码类型
- **预设配置**: 提供快速、深度、精确、语义等预设搜索模式
- **动态配置**: 支持运行时更新搜索权重和策略

#### 配置文件
- 主配置: `config/config.yaml`
- 搜索配置: `config/search_config.yaml`

#### 使用示例
```python
from src.core.enhanced_search_engine import EnhancedSearchEngine

# 初始化搜索引擎
engine = EnhancedSearchEngine()

# 基础搜索
results = engine.search("python function", mode="basic")

# 增强搜索
results = engine.search("如何实现数据库连接", mode="enhanced")

# 加载预设配置
engine.load_preset_config("deep")

# 动态更新权重
engine.update_search_weights({
    "content_match": 2.0,
    "path_match": 1.5
})
```

#### 配置选项
- **search_weights**: 搜索权重配置
- **search_strategies**: 搜索策略配置
- **language_weights**: 编程语言权重
- **intent_weights**: 查询意图权重
- **code_type_weights**: 代码类型权重
- **file_type_weights**: 文件类型权重
- **optimization**: 优化配置

### database.py
**数据库管理模块**

提供数据库连接、查询和管理功能。

#### 主要功能
- 数据库连接管理
- SQL查询执行
- 事务处理
- 连接池管理

### config_manager.py
**配置管理模块**

统一管理系统配置文件的加载和验证。

#### 主要功能
- 配置文件加载
- 配置验证
- 环境变量覆盖
- 配置热重载

## 设计原则

1. **通用性**: 所有模块都设计为通用组件，避免特定场景的硬编码
2. **可配置性**: 通过配置文件控制行为，支持不同使用场景
3. **可扩展性**: 模块化设计，便于功能扩展和定制
4. **性能优化**: 内置缓存和优化机制，提供高效的搜索体验

## 最佳实践

1. **配置管理**: 使用配置文件而非硬编码参数
2. **错误处理**: 完善的异常处理和日志记录
3. **性能监控**: 支持搜索性能统计和调试
4. **测试覆盖**: 提供完整的单元测试和集成测试

### semantic_search.py
**语义搜索实现**
- 基于向量嵌入的语义搜索
- 使用预训练模型进行文本编码
- 向量相似度计算和排序
- 支持多种嵌入模型

**主要功能：**
```python
class SemanticSearch:
    def encode_text(text)               # 文本编码
    def search_similar(query_vector)    # 相似度搜索
    def update_embeddings()             # 更新嵌入向量
    def get_similarity_score()          # 计算相似度分数
```

### tree_parser.py
**代码解析器**
- 使用Tree-sitter进行精确的语法分析
- 支持多种编程语言（Python、JavaScript、Java等）
- 提取代码结构信息（函数、类、变量等）
- 生成抽象语法树(AST)

**主要功能：**
```python
class TreeParser:
    def parse_file(file_path)           # 解析文件
    def extract_functions()             # 提取函数定义
    def extract_classes()               # 提取类定义
    def get_code_structure()            # 获取代码结构
```

### indexer.py
**索引构建器**
- 负责代码文件的索引化处理
- 文件变更检测和增量更新
- 多线程并行索引处理
- 索引进度跟踪和错误处理

**主要功能：**
```python
class Indexer:
    def index_repository(repo_path)     # 索引代码库
    def update_index(file_path)         # 更新单个文件索引
    def remove_from_index(file_path)    # 从索引中移除文件
    def get_index_status()              # 获取索引状态
```

## 🔗 模块依赖关系

```
enhanced_search_engine.py (主入口)
├── database.py (数据存储)
├── semantic_search.py (语义搜索)
├── tree_parser.py (代码解析)
└── indexer.py (索引构建)
    ├── tree_parser.py
    └── database.py
```

## 🚀 使用示例

### 基本搜索
```python
from src.core.enhanced_search_engine import EnhancedSearchEngine

# 初始化搜索引擎
engine = EnhancedSearchEngine()

# 执行搜索
results = engine.search("function definition", mode='semantic')
for result in results:
    print(f"文件: {result['file_path']}")
    print(f"函数: {result['function_name']}")
    print(f"相似度: {result['score']}")
```

### 索引构建
```python
from src.core.indexer import Indexer

# 创建索引器
indexer = Indexer()

# 索引整个项目
indexer.index_repository("/path/to/project")

# 获取索引状态
status = indexer.get_index_status()
print(f"已索引文件: {status['indexed_files']}")
```

### 语义搜索
```python
from src.core.semantic_search import SemanticSearch

# 初始化语义搜索
semantic = SemanticSearch()

# 编码查询
query_vector = semantic.encode_text("database connection")

# 搜索相似代码
results = semantic.search_similar(query_vector, top_k=10)
```

## ⚙️ 配置说明

核心模块的配置通过 `config/config.yaml` 文件管理：

```yaml
database:
  path: "search.db"
  timeout: 30

semantic_search:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  max_length: 512

tree_parser:
  languages: ["python", "javascript", "java"]
  grammar_path: "grammars/"

indexer:
  batch_size: 100
  max_workers: 4
```

## 🧪 测试

每个模块都有对应的测试文件：
- `test/test_database.py`
- `test/test_semantic_search.py`
- `test/test_basic.py`

运行测试：
```bash
cd test/
python test_basic.py
```

## 📝 开发指南

### 添加新的搜索功能
1. 在相应模块中添加新方法
2. 更新 `enhanced_search_engine.py` 中的接口
3. 添加相应的测试用例
4. 更新文档

### 性能优化
- 数据库查询优化：使用索引和查询计划分析
- 向量搜索优化：考虑使用FAISS等专业库
- 并发处理：合理使用多线程和异步处理

### 错误处理
- 所有模块都应包含适当的异常处理
- 使用日志记录重要操作和错误信息
- 提供有意义的错误消息给上层调用者