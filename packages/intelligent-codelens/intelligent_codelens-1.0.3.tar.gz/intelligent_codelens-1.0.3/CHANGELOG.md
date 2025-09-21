# 更新日志

本文档记录了MCP代码搜索服务器的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 计划中
- 支持更多编程语言的语法解析
- 添加代码质量分析功能
- 实现分布式搜索支持
- 添加Web界面的高级搜索功能

## [1.0.3] - 2025-01-21

### 修复
- 🔧 完全移除相对导入，只使用绝对导入和直接导入
- 📦 进一步优化uvx运行时的模块导入兼容性
- 🛠️ 改进包的独立运行能力

## [1.0.2] - 2025-01-21

### 修复
- 🔧 修复uvx运行时的模块导入问题
- 📦 改进包的入口点配置，支持独立运行
- 🛠️ 优化相对导入和绝对导入的兼容性

## [1.0.1] - 2025-01-21

### 安全性修复
- 🔒 修复Flask应用中硬编码的secret_key安全漏洞
- 🔐 添加环境变量支持，提升生产环境安全性
- 📝 创建.env.example文件，指导用户正确配置敏感信息
- 🛡️ 添加.gitignore文件，防止敏感文件被提交到版本控制
- 📖 创建SECURITY.md文档，提供详细的安全配置指南

### 改进
- ✨ 优化环境变量配置流程
- 📚 完善安全相关文档

## [1.0.0] - 2025-01-XX

### 新增
- 🎉 首次正式发布
- ✨ 基于MCP协议的代码搜索服务器
- 🔍 智能语义搜索功能
- 🌐 REST API接口
- 📱 Web用户界面
- 🗄️ SQLite数据库存储
- 🌳 Tree-sitter语法解析支持
- 🤖 SpaCy NLP模型集成
- 🐳 Docker容器化支持
- 📚 完整的文档和示例

### 支持的编程语言
- Python
- JavaScript/TypeScript
- Java
- Go
- 更多语言持续添加中...

### 核心功能
- **语义搜索**: 基于向量相似度的智能代码搜索
- **语法解析**: 使用Tree-sitter进行精确的代码结构分析
- **多接口支持**: 同时提供MCP协议和REST API
- **实时索引**: 支持代码库的实时索引和更新
- **高性能**: 优化的搜索算法和缓存机制

### 技术栈
- **后端**: Python 3.8+
- **搜索引擎**: 自研语义搜索引擎
- **数据库**: SQLite
- **Web框架**: Flask
- **NLP**: SpaCy + 自定义模型
- **协议**: MCP (Model Context Protocol)

### 安装和部署
- 📦 PyPI包发布
- 🐳 Docker镜像支持
- 🚀 一键安装脚本
- 📖 详细的安装文档

### 文档
- 📚 完整的API文档
- 🎯 快速开始指南
- 🔧 配置说明
- 💡 使用示例
- 🐛 故障排除指南

---

## 版本说明

### 版本号格式
- **主版本号**: 不兼容的API修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正

### 变更类型
- `新增` - 新功能
- `变更` - 对现有功能的变更
- `弃用` - 即将移除的功能
- `移除` - 已移除的功能
- `修复` - 问题修复
- `安全` - 安全相关的修复

### 发布周期
- **主版本**: 根据需要发布
- **次版本**: 每月发布
- **修订版本**: 根据需要发布

---

## 贡献指南

如果您想为项目做出贡献，请：

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 支持

如果您遇到问题或有建议，请：

- 📝 [提交Issue](https://github.com/your-org/local-code-search/issues)
- 💬 [参与讨论](https://github.com/your-org/local-code-search/discussions)
- 📧 发送邮件至 support@localcodesearch.com