# MCP Evaluation Server
一个基于FastMCP的MCP工具评估服务器，提供工具搜索、评估和分类功能。

## 功能特性

- 🔍 **工具搜索**：支持关键词、分类、评分等多维度搜索
- 🏆 **热门工具**：提供各类评分的热门工具排行榜
- 📊 **详细评估**：包含他山评分、实用性评分等多维度评估
- 📂 **分类管理**：按工具分类进行统计和展示
- 🏥 **健康检查**：实时监控服务状态
- 🚀 **高性能**：基于FastMCP框架，响应迅速

## 安装

### 从PyPI安装

```bash
pip install mcp-evaluation-server
```

### 从源码安装

```bash
git clone <repository-url>
cd mcp-evaluation-server
pip install -e .
```

## 快速开始

### 1. 配置

安装后，需要配置数据库连接：

```bash
# 初始化配置文件
mcp-evaluation-server --init-config

# 编辑配置文件
nano .env
```

### 2. 检查配置

```bash
# 检查配置是否正确
mcp-evaluation-server --check-config
```

### 3. 启动服务

```bash
# 启动服务器
mcp-evaluation-server

# 或指定日志级别
mcp-evaluation-server --log-level DEBUG
```

## 配置选项

必需配置：
- `SUPABASE_URL`: Supabase数据库URL
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase服务密钥

可选配置：
- `REDIS_URL`: Redis缓存URL
- `CACHE_TTL`: 缓存过期时间
- `LOG_LEVEL`: 日志级别 (DEBUG, INFO, WARNING, ERROR)
- `LOG_FILE`: 日志文件路径

## 使用示例

### 命令行使用

```bash
# 查看版本
mcp-evaluation-server --version

# 检查配置
mcp-evaluation-server --check-config

# 初始化配置文件
mcp-evaluation-server --init-config
```

### 程序化使用

```python
import asyncio
from mcp_evaluation_server import (
    search_mcp_tools,
    get_top_tools,
    get_tool_evaluation
)

async def main():
    # 搜索工具
    results = await search_mcp_tools(query="github", limit=10)
    print(f"找到 {len(results['tools'])} 个工具")
    
    # 获取热门工具
    top_tools = await get_top_tools(sort_by="tashan_score", limit=5)
    print(f"热门工具: {[tool['name'] for tool in top_tools['tools']]}")
    
    # 获取工具评估
    evaluation = await get_tool_evaluation("github-mcp-server")
    print(f"评估分数: {evaluation['evaluation']['comprehensive_score']}")

asyncio.run(main())
```

## 开发

### 本地开发

```bash
# 克隆仓库
git clone <repository-url>
cd mcp-evaluation-server

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/

# 代码格式化
black src/
isort src/

# 类型检查
mypy src/
```

### 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 故障排除

### 常见问题

1. **配置加载失败**
   ```bash
   # 检查环境变量
   echo $SUPABASE_URL
   
   # 或检查.env文件
   cat .env
   ```

2. **数据库连接失败**
   ```bash
   # 检查配置
   mcp-evaluation-server --check-config
   ```

3. **权限问题**
   ```bash
   # 确保有写入权限
   chmod +x mcp_evaluation_server
   ```

### 日志调试

```bash
# 启用调试日志
mcp-evaluation-server --log-level DEBUG

# 查看日志文件
tail -f logs/mcp_server.log
```

## API文档

详细的API文档请参考项目的 `API.md` 文件。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

- 📧 **邮件支持**: support@example.com
- 🐛 **问题反馈**: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 **文档**: [项目Wiki](https://github.com/your-repo/wiki)

## 免责声明

本工具仅用于评估和推荐目的，工具评分仅供参考。用户应自行评估和决定是否使用特定工具。

## 更新日志

### v0.1.0
- 初始版本发布
- 基础搜索功能
- 工具评估系统
- 分类统计功能