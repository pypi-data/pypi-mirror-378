# 部署指南

MCP Evaluation Server 支持多种部署方式，包括 Docker 容器化部署和传统的 systemd 服务部署。

## 部署方式

### 1. Docker 部署 (推荐)

#### 开发环境
```bash
# 设置环境变量
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"

# 启动服务
./deploy.sh dev

# 查看日志
./deploy.sh dev logs

# 健康检查
./deploy.sh dev health
```

#### 生产环境
```bash
# 设置环境变量
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
export LOG_LEVEL="INFO"

# 启动服务（包含Redis）
./deploy.sh prod
```

### 2. 系统服务部署

适用于生产环境的传统部署方式：

```bash
# 设置环境变量
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"

# 运行生产部署脚本
sudo ./deploy-prod.sh
```

## 环境变量配置

### 必需的环境变量

```bash
# Supabase 数据库配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### 可选的环境变量

```bash
# 数据表名称
MCP_TOOLS_TABLE=mcp_tools
MCP_TEST_RESULTS_TABLE=mcp_test_results

# Redis 缓存配置
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/mcp_server.log
```

## 监控和运维

### 健康检查

服务提供健康检查端点：

```bash
# Docker 环境
docker-compose exec mcp-evaluation-server python -c "from src.database import DatabaseManager; import asyncio; print(asyncio.run(DatabaseManager().health_check()))"

# 系统服务
systemctl is-active mcp-evaluation-server
```

### 日志管理

#### Docker 环境
```bash
# 查看实时日志
docker-compose logs -f

# 查看特定服务的日志
docker-compose logs -f mcp-evaluation-server

# 查看最近的日志
docker-compose logs --tail=100
```

#### 系统服务
```bash
# 查看服务状态
systemctl status mcp-evaluation-server

# 查看实时日志
journalctl -u mcp-evaluation-server -f

# 查看最近的日志
journalctl -u mcp-evaluation-server -n 100
```

### 性能监控

#### Prometheus + Grafana

1. 启动 Prometheus：
```bash
docker run -d -p 9090:9090 \
  -v $(pwd)/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

2. 启动 Grafana：
```bash
docker run -d -p 3000:3000 grafana/grafana
```

3. 导入监控面板：
   - 访问 http://localhost:3000
   - 导入 `monitoring/grafana-dashboard.json`

#### 关键指标

- **服务状态**: `up{job="mcp-evaluation-server"}`
- **数据库健康**: `mcp_database_health`
- **API 响应时间**: `mcp_api_response_time_seconds`
- **错误率**: `mcp_api_errors_total`

## 扩展和负载均衡

### 水平扩展

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  mcp-evaluation-server-1:
    build: .
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
    depends_on:
      - redis
  
  mcp-evaluation-server-2:
    build: .
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
    depends_on:
      - redis
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - mcp-evaluation-server-1
      - mcp-evaluation-server-2
```

### Nginx 负载均衡配置

```nginx
upstream mcp_servers {
    server mcp-evaluation-server-1:8000;
    server mcp-evaluation-server-2:8000;
}

server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://mcp_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 备份和恢复

### 数据库备份

```bash
# 使用 Supabase CLI
supabase db dump --local > backup-$(date +%Y%m%d).sql

# 或者使用 pg_dump
pg_dump $SUPABASE_URL > backup-$(date +%Y%m%d).sql
```

### 配置备份

```bash
# 备份环境变量
env > backup-$(date +%Y%m%d).env

# 备份配置文件
tar -czf config-backup-$(date +%Y%m%d).tar.gz \
  docker-compose.yml \
  deploy.sh \
  monitoring/
```

## 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查环境变量
echo $SUPABASE_URL
echo $SUPABASE_SERVICE_ROLE_KEY

# 测试连接
curl -X POST $SUPABASE_URL/rest/v1/ \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json"
```

#### 2. 内存使用过高
```bash
# 检查内存使用
docker stats

# 重启服务
docker-compose restart

# 调整内存限制
# 编辑 docker-compose.yml 中的 deploy.resources.limits.memory
```

#### 3. 服务启动失败
```bash
# 检查日志
docker-compose logs mcp-evaluation-server

# 检查依赖服务
docker-compose ps

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

### 性能优化

#### 1. 数据库优化
- 添加适当的索引
- 使用连接池
- 优化查询语句

#### 2. 缓存优化
- 启用 Redis 缓存
- 调整缓存 TTL
- 实现多级缓存

#### 3. 系统优化
- 增加 CPU 和内存资源
- 使用 SSD 存储
- 优化网络配置

## 安全配置

### 环境变量安全
```bash
# 使用环境变量文件
echo "SUPABASE_URL=your-url" >> .env
echo "SUPABASE_SERVICE_ROLE_KEY=your-key" >> .env
chmod 600 .env
```

### 网络安全
```yaml
# 仅允许内部网络访问
services:
  mcp-evaluation-server:
    ports:
      - "127.0.0.1:8000:8000"
    networks:
      - internal
```

### SSL/TLS 配置
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://mcp_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```