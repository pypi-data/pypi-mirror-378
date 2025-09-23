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

### 使用uv安装

```bash
uv add mcp-evaluation-server
```

### 使用uvx运行（推荐）

无需安装，直接运行：

```bash
uvx mcp-evaluation-server
```

## 作为MCP服务器使用

本服务器可以作为MCP（Model Context Protocol）服务器在支持的AI客户端中使用，如Cursor、Cherry Studio等。

### 在Cursor中使用

1. **打开Cursor设置**
   - 按下 `Ctrl+,` (Windows/Linux) 或 `Cmd+,` (Mac)
   - 进入 `Extensions` → `MCP`

2. **添加MCP服务器配置**
   在 `mcp.json` 配置文件中添加：

   ```json
   {
     "mcpServers": {
       "mcp-evaluation": {
         "command": "uvx",
         "args": ["mcp-evaluation-server"]
       }
     }
   }
   ```

3. **重启Cursor**
   - 完成配置后重启Cursor使设置生效

4. **使用功能**
   - 重启后，您可以在对话中直接询问关于MCP工具的问题
   - 例如："搜索GitHub相关的MCP工具"
   - 或："获取评分最高的MCP工具"

### 在Cherry Studio中使用

1. **打开Cherry Studio**
   - 启动Cherry Studio应用

2. **进入MCP设置**
   - 点击设置图标
   - 找到MCP服务器配置选项

3. **添加服务器**
   添加以下配置：
   - **服务器名称**: `mcp-evaluation`
   - **命令**: `uvx`
   - **参数**: `mcp-evaluation-server`

4. **启用服务器**
   - 启用刚添加的MCP服务器
   - 重启Cherry Studio

5. **开始使用**
   - 在对话中可以直接使用MCP工具评估功能
   - 询问工具推荐、评分等信息

## 程序化使用

### Python API调用

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

### 直接启动服务器

```bash
# 使用uvx启动MCP服务器（推荐）
uvx mcp-evaluation-server

# 使用uvx启用调试模式
uvx mcp-evaluation-server --log-level DEBUG

# 或使用已安装的命令
mcp-evaluation-server
```

## 开发

### 本地开发

```bash
# 克隆仓库
git clone <repository-url>
cd mcp-evaluation-server

# 使用uv安装开发依赖
uv add --dev pytest pytest-asyncio pytest-cov black isort mypy

# 运行测试
pytest tests/

# 代码格式化
black mcp_evaluation_server/
isort mcp_evaluation_server/

# 类型检查
mypy mcp_evaluation_server/
```

### 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 故障排除

### 常见问题

1. **安装失败**
   ```bash
   # 尝试使用uvx直接运行（无需安装）
   uvx mcp-evaluation-server
   
   # 或使用uv安装
   uv add mcp-evaluation-server
   
   # 或使用pip安装
   pip install mcp-evaluation-server
   ```

2. **MCP服务器连接失败**
   - 确保网络连接正常
   - 检查AI客户端的MCP配置是否使用`uvx`
   - 重启AI客户端
   - 尝试直接运行测试：`uvx mcp-evaluation-server`

3. **权限问题**
   ```bash
   # 测试uvx是否可用
   uvx mcp-evaluation-server --help
   ```

### 日志调试

```bash
# 使用uvx启用调试模式
uvx mcp-evaluation-server --log-level DEBUG

# 查看帮助信息
uvx mcp-evaluation-server --help
```

## 支持的AI客户端

### 官方支持
- **Cursor**: 完全支持，通过MCP配置
- **Cherry Studio**: 完全支持，通过MCP配置
- **Claude**: 完全支持，通过MCP配置

### 其他支持MCP的客户端
任何支持MCP协议的AI客户端都可以使用此服务器，包括：
- Continue
- Codeium
- 其他基于MCP的开发工具

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

- 🐛 **问题反馈**: [GitHub Issues](https://github.com/gqy20/mcp_evaluate/issues)
- 📖 **源码**: [GitHub Repository](https://github.com/gqy20/mcp_evaluate)

## 免责声明

本工具仅用于评估和推荐目的，工具评分仅供参考。用户应自行评估和决定是否使用特定工具。

## 更新日志

### v0.1.0
- 初始版本发布
- 支持MCP协议
- 工具搜索和评估功能
- Cursor和Cherry Studio集成支持
- 数据库连接已内置，无需额外配置