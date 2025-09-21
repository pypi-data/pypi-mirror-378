# 安全配置指南

## 环境变量配置

### 必需的环境变量

#### FLASK_SECRET_KEY
- **用途**: Flask 应用的会话加密密钥
- **重要性**: 🔴 必需（生产环境）
- **配置方法**:
  ```bash
  export FLASK_SECRET_KEY="your-secure-random-key-here"
  ```
- **生成安全密钥**:
  ```python
  import secrets
  print(secrets.token_hex(32))
  ```

### 可选的环境变量

#### DATABASE_URL
- **用途**: 数据库连接字符串
- **默认值**: `sqlite:///data/code_database.db`
- **示例**:
  ```bash
  export DATABASE_URL="sqlite:///path/to/your/database.db"
  ```

#### SEARCH_CONFIG
- **用途**: 搜索配置文件路径
- **默认值**: `config/search_config.yaml`
- **示例**:
  ```bash
  export SEARCH_CONFIG="/path/to/custom/search_config.yaml"
  ```

#### LOG_LEVEL
- **用途**: 日志级别设置
- **默认值**: `INFO`
- **可选值**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **示例**:
  ```bash
  export LOG_LEVEL="DEBUG"
  ```

## 配置方法

### 1. 使用 .env 文件（推荐）

1. 复制示例文件：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，设置实际值：
   ```bash
   FLASK_SECRET_KEY=your-production-secret-key-here
   ```

3. 确保 `.env` 文件不会被提交到版本控制（已在 `.gitignore` 中配置）

### 2. 直接设置环境变量

```bash
# 临时设置（当前会话有效）
export FLASK_SECRET_KEY="your-secure-key"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export FLASK_SECRET_KEY="your-secure-key"' >> ~/.zshrc
source ~/.zshrc
```

### 3. 在 Docker 中使用

```dockerfile
# Dockerfile
ENV FLASK_SECRET_KEY=your-secure-key
```

或使用 docker-compose.yml：
```yaml
version: '3.8'
services:
  app:
    build: .
    environment:
      - FLASK_SECRET_KEY=your-secure-key
```

## 安全最佳实践

### 1. 密钥管理
- ✅ 使用强随机密钥（至少32字符）
- ✅ 定期轮换密钥
- ✅ 不要在代码中硬编码密钥
- ✅ 不要将密钥提交到版本控制

### 2. 环境分离
- ✅ 开发、测试、生产环境使用不同的密钥
- ✅ 使用环境变量或密钥管理服务
- ✅ 限制密钥访问权限

### 3. 监控和审计
- ✅ 监控异常的认证尝试
- ✅ 定期审查访问日志
- ✅ 实施适当的日志记录

## 故障排除

### 常见问题

1. **Flask 应用启动失败**
   - 检查是否设置了 `FLASK_SECRET_KEY`
   - 确保密钥不为空

2. **会话数据丢失**
   - 检查密钥是否在应用重启后保持一致
   - 确保密钥足够长（推荐32字符以上）

3. **开发环境配置**
   - 开发环境会使用默认密钥 `dev-key-only-not-for-production`
   - 生产环境必须设置自定义密钥

## 联系方式

如果发现安全问题，请通过以下方式联系：
- 邮箱: security@codelens.dev
- 创建私有 issue 报告安全漏洞