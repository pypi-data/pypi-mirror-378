# Supabase 配置指南

## 获取 Supabase 项目信息

### 1. 创建 Supabase 项目

1. 访问 [Supabase 控制台](https://supabase.com/dashboard)
2. 点击 "New Project" 创建新项目
3. 填写项目信息：
   - 组织名称：您的组织名称
   - 项目名称：mcp-evaluation-server
   - 数据库密码：设置强密码
   - 地区：选择离您最近的地区

### 2. 获取项目 URL 和密钥

项目创建完成后，在项目设置中找到连接信息：

1. 进入项目 -> Settings -> API
2. 复制以下信息：
   - **Project URL**: `https://your-project-id.supabase.co`
   - **service_role_key**: 在 Project API keys -> service_role -> secret

### 3. 配置数据库表

确保您的 Supabase 数据库中有以下表（这些应该由 @mcp_agent 自动创建）：

#### mcp_tools 表结构
```sql
CREATE TABLE mcp_tools (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tool_id TEXT UNIQUE,
    name TEXT NOT NULL,
    author TEXT,
    description TEXT,
    category TEXT,
    github_url TEXT,
    url TEXT,
    deployment_method TEXT,
    package_name TEXT,
    requires_api_key BOOLEAN DEFAULT FALSE,
    tashan_score FLOAT,
    utility_score FLOAT,
    sustainability_score FLOAT,
    popularity_score FLOAT,
    lobehub_score FLOAT,
    lobehub_evaluate TEXT,
    test_success_rate FLOAT,
    test_count INTEGER,
    lobehub_stars INTEGER,
    lobehub_forks INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### mcp_test_results 表结构
```sql
CREATE TABLE mcp_test_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tool_id TEXT REFERENCES mcp_tools(tool_id),
    test_id TEXT,
    test_type TEXT,
    result TEXT,
    test_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. 设置环境变量

将以下内容复制到您的 `.env` 文件中，并替换为实际值：

```bash
# Supabase 数据库配置
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-actual-service-role-key-here

# 数据表名称
MCP_TOOLS_TABLE=mcp_tools
MCP_TEST_RESULTS_TABLE=mcp_test_results

# Redis 缓存配置（可选）
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/mcp_server.log
```

### 5. 验证配置

运行以下命令验证配置是否正确：

```bash
# 测试数据库连接
uv run python -c "
from src.database import DatabaseManager
import asyncio

async def test_connection():
    db = DatabaseManager()
    result = await db.health_check()
    print('数据库连接状态:', '成功' if result else '失败')
    
    # 测试获取工具数量
    count = await db.get_total_tools_count()
    print('工具总数:', count)

asyncio.run(test_connection())
"
```

### 6. 常见问题解决

#### 连接失败
- 检查 SUPABASE_URL 是否正确
- 确认 SUPABASE_SERVICE_ROLE_KEY 是否有效
- 验证网络连接是否正常

#### 表不存在
- 确认 @mcp_agent 已经运行并创建了表
- 检查表名是否与 MCP_TOOLS_TABLE 和 MCP_TEST_RESULTS_TABLE 匹配

#### 权限问题
- 确保使用的是 service_role_key，而不是 anon key
- 检查密钥是否有足够的权限

### 7. 安全建议

1. **不要将密钥提交到版本控制**
   - 确保 .env 文件在 .gitignore 中
   - 使用环境变量管理密钥

2. **定期轮换密钥**
   - 定期更新 SUPABASE_SERVICE_ROLE_KEY
   - 监控密钥使用情况

3. **网络限制**
   - 在 Supabase 控制台中设置 IP 白名单
   - 限制数据库访问来源

### 8. 生产环境配置

对于生产环境，建议：

```bash
# 生产环境配置示例
SUPABASE_URL=https://your-production-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-production-service-role-key
MCP_TOOLS_TABLE=mcp_tools
MCP_TEST_RESULTS_TABLE=mcp_test_results
REDIS_URL=redis://your-redis-server:6379/0
CACHE_TTL=1800
LOG_LEVEL=WARNING
LOG_FILE=/var/log/mcp-server/mcp_server.log
```

### 9. 监控和日志

启用详细日志进行调试：

```bash
LOG_LEVEL=DEBUG uv run python -m src.main
```

监控数据库连接状态：

```bash
# 查看连接日志
tail -f logs/mcp_server.log

# 监控数据库性能
docker-compose exec mcp-evaluation-server python -c "
from src.database import DatabaseManager
import asyncio
import time

async def monitor():
    db = DatabaseManager()
    while True:
        start = time.time()
        health = await db.health_check()
        duration = time.time() - start
        print(f'健康检查: {health}, 耗时: {duration:.3f}s')
        time.sleep(30)

asyncio.run(monitor())
"
```