# MCP Evaluation Server

基于 Model Context Protocol (MCP) 的工具智能搜索、评估和推荐系统，专为他山研究院打造。

## 特性

- 🚀 **高性能**: 基于异步Python和FastMCP框架
- 🔍 **智能搜索**: 支持关键词、分类、评分等多维度搜索
- 📊 **专业评估**: 提供详细的工具评估报告和使用建议
- 🏆 **排行榜**: 基于多维度评分的热门工具排行
- 📈 **统计分析**: 完整的分类统计和趋势分析
- ⚡ **快速开发**: 使用 FastMCP 框架，开发效率高
- 🎯 **MVP原则**: 专注核心功能，快速迭代

## 技术栈

- **包管理**: UV (现代Python包管理器)
- **MCP框架**: FastMCP (轻量级MCP服务器框架)
- **数据处理**: Pandas (数据处理)
- **数据库**: Supabase (PostgreSQL)
- **类型检查**: MyPy (静态类型检查)
- **代码格式**: Black + isort (代码格式化)

## 环境要求

- Python 3.12+
- UV 包管理器

## 安装

```bash
uv sync
```

### 开发环境

```bash
uv sync --dev
```

### 启动服务器

```bash
uv run python -m mcp_evaluation_server.main
```

## 项目结构

```
mcp-evaluation-server/
├── pyproject.toml          # 项目配置
├── README.md              # 项目说明
├── mcp_evaluation_server/ # 源代码
│   ├── main.py            # MCP服务器入口
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库管理
│   ├── models.py          # 数据模型
│   ├── utils.py           # 工具函数
│   ├── practical_security.py     # 安全编码混淆
│   ├── secure_config_manager.py  # 安全配置管理
│   └── memory_protection.py     # 内存保护
├── scripts/               # 构建和部署脚本
├── docs/                  # 文档目录
│   ├── API.md            # API文档
│   ├── DEPLOYMENT.md     # 部署指南
│   ├── SECURITY_GUIDE.md # 安全指南
│   └── ...
├── tests/                 # 测试文件
├── .env.example           # 环境变量模板
└── monitoring/            # 监控配置
```

## MCP 工具列表

### search_mcp_tools
搜索MCP工具，支持关键词、分类、评分等多维度搜索

### get_tool_evaluation
获取工具详细评估报告，包含评分、建议和适用场景

### get_top_tools
获取热门工具排行榜，支持多种排序方式

### get_tool_categories
获取工具分类统计信息，包含数量和平均评分

## 开发

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行单元测试
uv run pytest tests/ -m "unit"

# 运行集成测试
uv run pytest tests/ -m "integration"

# 生成测试覆盖率报告
uv run pytest --cov=src
```

### 代码格式化

```bash
uv run black src/ tests/
uv run isort src/ tests/
```

### 类型检查

```bash
uv run mypy src/
```

## 配置

### 环境变量

```bash
# Supabase数据库配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# 数据表名称
MCP_TOOLS_TABLE=mcp_tools
MCP_TEST_RESULTS_TABLE=mcp_test_results

# 可选：Redis缓存
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/mcp_server.log
```

## 文档

详细文档请查看 `docs/` 目录：

- [API文档](docs/API.md) - MCP工具API接口文档
- [部署指南](docs/DEPLOYMENT.md) - 详细的部署说明
- [安全指南](docs/SECURITY_GUIDE.md) - 安全功能配置说明
- [Supabase设置](docs/SUPABASE_SETUP.md) - 数据库设置指南
- [GitHub版说明](docs/README_GITHUB.md) - GitHub仓库说明
- [PyPI版说明](docs/README_PYPI.md) - PyPI包说明

## 许可证

MIT License