# 项目文档索引

欢迎来到代码搜索服务器项目的文档中心！本项目提供基于语义搜索的代码搜索功能，支持多种接口和协议。

## 📚 文档导航

### 🏠 项目概览
- [项目主文档](README.md) - 项目介绍、功能特性和快速开始指南

### 🔧 安装配置
- [MCP设置指南](MCP_SETUP_GUIDE.md) - Model Context Protocol 服务器设置详细指南
- [Trae MCP配置](setup/TRAE_MCP_CONFIG.md) - 在Trae IDE中配置MCP服务器的说明

### 🌐 API文档
- [API接口文档](api/README_API.md) - REST API接口详细说明和使用示例

### 🔌 MCP协议
- [MCP协议文档](mcp/README_MCP.md) - Model Context Protocol 实现说明和使用指南

## 🚀 快速开始

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **启动服务**
   - REST API服务：`python api_server.py`
   - MCP服务器：`python mcp_server.py`

3. **配置IDE**
   - 参考 [Trae MCP配置](setup/TRAE_MCP_CONFIG.md) 在IDE中配置MCP服务器

## 📖 文档结构

```
docs/
├── index.md                    # 本文档 - 文档索引
├── README.md                   # 项目主文档
├── api/                        # API相关文档
│   └── README_API.md          # REST API文档
├── mcp/                        # MCP协议相关文档
│   └── README_MCP.md          # MCP协议文档
├── MCP_SETUP_GUIDE.md         # MCP设置指南
└── setup/                      # 安装配置文档
    ├── TRAE_MCP_CONFIG.md     # Trae配置说明
    ├── PRODUCTION_DEPLOYMENT_GUIDE.md  # 生产部署指南
    └── SPACY_MODEL_GUIDE.md   # SpaCy模型指南
```

## 🛠️ 项目特性

- **语义搜索** - 基于向量相似度的智能代码搜索
- **多语言支持** - 支持Python、JavaScript、Java等多种编程语言
- **多种接口** - 提供REST API和MCP协议两种访问方式
- **IDE集成** - 可与Trae IDE等现代开发环境无缝集成
- **高性能** - 优化的索引和搜索算法，快速响应

## 📞 获取帮助

如果您在使用过程中遇到问题，请：

1. 查看相关文档章节
2. 检查配置文件是否正确
3. 查看日志输出获取错误信息
4. 参考示例代码和配置

## 🔄 文档更新

本文档会随着项目的发展持续更新。建议定期查看最新版本以获取最新信息。

---

*最后更新时间：2025年1月*