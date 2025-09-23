# API 文档

MCP Evaluation Server 提供了完整的 MCP (Model Context Protocol) 工具接口，用于工具搜索、评估和推荐。

## MCP 工具列表

### 1. search_mcp_tools

搜索 MCP 工具，支持多维度过滤和排序。

**参数：**
- `query` (可选): 搜索关键词
- `category` (可选): 工具分类
- `min_tashan_score` (可选): 最小他山评分
- `max_tashan_score` (可选): 最大他山评分
- `deployment_method` (可选): 部署方式
- `author` (可选): 作者名称
- `limit` (可选): 返回结果数量限制 (默认: 20)
- `offset` (可选): 偏移量 (默认: 0)

**返回值：**
```json
{
  "success": true,
  "tools": [
    {
      "tool_id": "tool-001",
      "name": "工具名称",
      "author": "作者",
      "description": "工具描述",
      "category": "工具分类",
      "github_url": "GitHub地址",
      "url": "项目地址",
      "deployment_method": "部署方式",
      "package_name": "包名",
      "requires_api_key": false,
      "scores": {
        "tashan_score": 85.0,
        "utility_score": 80.0,
        "sustainability_score": 90.0,
        "popularity_score": 75.0,
        "lobehub_score": 82.0,
        "lobehub_evaluate": "优质"
      },
      "stats": {
        "test_success_rate": 95.0,
        "test_count": 100,
        "last_test_time": "2023-01-01 12:00:00"
      },
      "lobehub_data": {
        "stars": 150,
        "forks": 30
      }
    }
  ],
  "total_count": 100,
  "search_summary": "找到 5 个工具 (共 100 个)。基于条件: 关键词 '测试'",
  "filters": {
    "query": "测试",
    "limit": 20,
    "offset": 0
  }
}
```

### 2. get_tool_evaluation

获取工具详细评估报告。

**参数：**
- `tool_name` (必需): 工具名称

**返回值：**
```json
{
  "success": true,
  "tool": {
    "tool_id": "tool-001",
    "name": "工具名称",
    "author": "作者",
    "description": "工具描述",
    "category": "工具分类",
    "github_url": "GitHub地址",
    "url": "项目地址",
    "deployment_method": "部署方式",
    "package_name": "包名",
    "requires_api_key": false,
    "scores": {
      "tashan_score": 85.0,
      "utility_score": 80.0,
      "sustainability_score": 90.0,
      "popularity_score": 75.0,
      "lobehub_score": 82.0,
      "lobehub_evaluate": "优质"
    },
    "stats": {
      "test_success_rate": 95.0,
      "test_count": 100,
      "last_test_time": "2023-01-01 12:00:00"
    },
    "lobehub_data": {
      "stars": 150,
      "forks": 30
    }
  },
  "recommendations": [
    "该工具评分优秀，推荐优先考虑使用",
    "LobeHub平台评定为优质工具，质量有保障",
    "工具测试成功率高，稳定性良好",
    "项目活跃度高，维护情况良好"
  ],
  "use_cases": [
    "软件开发",
    "代码生成",
    "开发辅助",
    "IDE集成"
  ],
  "test_results": [
    {
      "test_id": "test-001",
      "tool_name": "工具名称",
      "test_type": "功能测试",
      "result": "通过",
      "test_time": "2023-01-01 12:00:00",
      "error_message": null
    }
  ],
  "comprehensive_score": 85.0
}
```

### 3. get_top_tools

获取热门工具排行榜。

**参数：**
- `category` (可选): 工具分类
- `limit` (可选): 返回结果数量限制 (默认: 10)
- `sort_by` (可选): 排序字段 (默认: tashan_score)
  - 可选值: tashan_score, utility_score, sustainability_score, popularity_score, lobehub_score, test_success_rate

**返回值：**
```json
{
  "success": true,
  "tools": [
    {
      "rank": 1,
      "tool_id": "tool-001",
      "name": "工具名称",
      "author": "作者",
      "description": "工具描述",
      "category": "工具分类",
      "comprehensive_score": 85.0,
      "tashan_score": 85.0,
      "utility_score": 80.0,
      "sustainability_score": 90.0,
      "popularity_score": 75.0,
      "lobehub_score": 82.0,
      "test_success_rate": 95.0,
      "lobehub_stars": 150,
      "lobehub_forks": 30
    }
  ],
  "category": "开发工具推荐",
  "sort_by": "tashan_score",
  "limit": 10
}
```

### 4. get_tool_categories

获取工具分类统计信息。

**参数：**
- `include_percentages` (可选): 是否包含百分比 (默认: true)

**返回值：**
```json
{
  "success": true,
  "categories": [
    {
      "category": "开发工具推荐",
      "tool_count": 50,
      "percentage": 50.0,
      "avg_tashan_score": 82.5,
      "avg_utility_score": 78.0,
      "avg_sustainability_score": 85.0,
      "avg_popularity_score": 72.0
    },
    {
      "category": "文档处理",
      "tool_count": 30,
      "percentage": 30.0,
      "avg_tashan_score": 80.0,
      "avg_utility_score": 75.0,
      "avg_sustainability_score": 82.0,
      "avg_popularity_score": 70.0
    }
  ],
  "total_tools": 100
}
```

### 5. health_check

服务健康检查。

**参数：**
无

**返回值：**
```json
{
  "success": true,
  "status": "healthy",
  "database": "connected",
  "timestamp": "2023-01-01T12:00:00Z",
  "uptime": "1h 30m 45s",
  "version": "1.0.0"
}
```

## 错误处理

所有 API 响应都包含统一的错误格式：

```json
{
  "success": false,
  "error": {
    "code": "TOOL_NOT_FOUND",
    "message": "工具不存在",
    "details": "工具 '未知工具' 未在数据库中找到"
  },
  "timestamp": "2023-01-01T12:00:00Z"
}
```

### 错误代码列表

| 错误代码 | 描述 |
|---------|------|
| `TOOL_NOT_FOUND` | 工具不存在 |
| `INVALID_PARAMETERS` | 参数无效 |
| `DATABASE_ERROR` | 数据库错误 |
| `NETWORK_ERROR` | 网络错误 |
| `SERVICE_UNAVAILABLE` | 服务不可用 |

## 使用示例

### Python 客户端

```python
import asyncio
from mcp import ClientSession, StdioServerParameters

async def main():
    # 连接到 MCP 服务器
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "src.main"]
    )
    
    async with ClientSession(server_params) as session:
        # 初始化连接
        await session.initialize()
        
        # 搜索工具
        tools = await session.call_tool(
            "search_mcp_tools",
            {
                "query": "开发工具",
                "category": "开发工具推荐",
                "limit": 10
            }
        )
        print(tools)
        
        # 获取工具评估
        evaluation = await session.call_tool(
            "get_tool_evaluation",
            {"tool_name": "测试工具"}
        )
        print(evaluation)
        
        # 获取热门工具
        top_tools = await session.call_tool(
            "get_top_tools",
            {"limit": 5, "sort_by": "tashan_score"}
        )
        print(top_tools)

if __name__ == "__main__":
    asyncio.run(main())
```

### JavaScript 客户端

```javascript
const { MCPClient } = require('@modelcontextprotocol/sdk');

async function main() {
    // 创建客户端
    const client = new MCPClient({
        name: "mcp-evaluation-client",
        version: "1.0.0"
    });
    
    // 连接到服务器
    await client.connectToServer({
        command: "uv",
        args: ["run", "python", "-m", "src.main"]
    });
    
    try {
        // 搜索工具
        const tools = await client.callTool("search_mcp_tools", {
            query: "开发工具",
            category: "开发工具推荐",
            limit: 10
        });
        console.log(tools);
        
        // 获取工具评估
        const evaluation = await client.callTool("get_tool_evaluation", {
            tool_name: "测试工具"
        });
        console.log(evaluation);
        
        // 获取热门工具
        const topTools = await client.callTool("get_top_tools", {
            limit: 5,
            sort_by: "tashan_score"
        });
        console.log(topTools);
        
    } finally {
        await client.close();
    }
}

main().catch(console.error);
```

### cURL 示例

```bash
# 搜索工具
curl -X POST http://localhost:8000/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "search_mcp_tools",
    "arguments": {
      "query": "开发工具",
      "limit": 10
    }
  }'

# 获取工具评估
curl -X POST http://localhost:8000/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_tool_evaluation",
    "arguments": {
      "tool_name": "测试工具"
    }
  }'

# 获取热门工具
curl -X POST http://localhost:8000/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_top_tools",
    "arguments": {
      "limit": 10,
      "sort_by": "tashan_score"
    }
  }'

# 健康检查
curl -X POST http://localhost:8000/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "health_check"
  }'
```

## 性能优化

### 缓存策略

- **查询缓存**: 搜索结果缓存 5 分钟
- **工具详情缓存**: 工具评估信息缓存 1 小时
- **统计数据缓存**: 分类统计缓存 30 分钟

### 分页建议

- 搜索结果默认限制 20 条记录
- 建议客户端实现分页加载
- 大量数据查询使用 offset 参数分页

### 批量操作

```python
# 批量获取多个工具的评估
tools = ["工具1", "工具2", "工具3"]
evaluations = []
for tool in tools:
    eval_result = await session.call_tool("get_tool_evaluation", {
        "tool_name": tool
    })
    evaluations.append(eval_result)
```

## 监控和调试

### 日志级别

- `DEBUG`: 详细的调试信息
- `INFO`: 一般运行信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息

### 监控指标

- API 响应时间
- 数据库查询时间
- 缓存命中率
- 错误率统计

### 调试模式

```bash
# 启用调试模式
export LOG_LEVEL=DEBUG
uv run python -m src.main
```

## 版本兼容性

### MCP 协议版本

- 支持 MCP 1.0+ 协议
- 兼容最新版本的 MCP SDK

### Python 版本

- Python 3.12+
- 支持 Python 3.13+

### 依赖版本

- FastMCP: 0.1.0+
- Pandas: 2.0.0+
- Supabase: 2.0.0+