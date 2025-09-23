# MCP Evaluation Server

一个基于FastMCP的MCP工具评估服务器，提供工具搜索、评估和分类功能。

## 功能特性

- 🔍 **工具搜索**：支持关键词、分类、评分等多维度搜索
- 🏆 **热门工具**：提供各类评分的热门工具排行榜
- 📊 **详细评估**：包含他山评分、实用性评分等多维度评估
- 📂 **分类管理**：按工具分类进行统计和展示
- 🏥 **健康检查**：实时监控服务状态
- 🚀 **高性能**：基于FastMCP框架，响应迅速

## 快速开始

### 安装

```bash
pip install mcp-evaluation-server
```

### 配置

创建 `.env` 文件：

```bash
# 复制模板
cp .env.example .env

# 编辑配置
nano .env
```

### 运行

```bash
# 启动服务器
mcp-evaluation-server

# 或使用Python
python -m mcp_evaluation_server
```

## 配置选项

必需配置：
- `SUPABASE_URL`: Supabase数据库URL
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase服务密钥

可选配置：
- `REDIS_URL`: Redis缓存URL
- `LOG_LEVEL`: 日志级别
- `LOG_FILE`: 日志文件路径

## API文档

### 搜索工具
```python
# 搜索MCP工具
results = await search_mcp_tools(query="github", limit=10)
```

### 获取热门工具
```python
# 获取热门工具排行榜
top_tools = await get_top_tools(sort_by="tashan_score", limit=5)
```

### 获取工具评估
```python
# 获取工具详细评估
evaluation = await get_tool_evaluation(tool_name="github-mcp-server")
```

## 开发

### 本地开发

```bash
# 克隆仓库
git clone <repository-url>
cd mcp-evaluation-server

# 安装依赖
uv sync

# 运行测试
uv run pytest tests/

# 启动开发服务器
uv run python -m src.main
```

### 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

如果您遇到问题或有建议，请：

1. 查看 [Issues](https://github.com/your-repo/issues) 页面
2. 创建新的 Issue 描述问题
3. 联系维护者

## 免责声明

本工具仅用于评估和推荐目的，工具评分仅供参考。用户应自行评估和决定是否使用特定工具。

## 更新日志

### v0.1.0
- 初始版本发布
- 基础搜索功能
- 工具评估系统
- 分类统计功能