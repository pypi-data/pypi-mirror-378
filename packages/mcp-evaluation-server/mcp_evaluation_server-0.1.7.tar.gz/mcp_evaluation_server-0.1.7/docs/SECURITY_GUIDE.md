# MCP代理安全部署指南

## 🛡️ 安全架构概述

本项目采用多层安全保护机制，确保敏感信息在Python包打包后难以被逆向工程获取：

### 安全层级
1. **编码混淆层** - 多层Base64编码 + 自定义字符变换
2. **C扩展保护层** - 核心加密逻辑用C实现，编译为.so文件
3. **内存保护层** - 运行时内存管理和访问控制
4. **反逆向工程层** - 反调试、反编译检测
5. **环境验证层** - 运行环境完整性检查
6. **打包保护层** - PyInstaller加密 + UPX压缩

## 🚀 快速开始

### 1. 安全打包

```bash
# 运行安全打包脚本
./build_secure.sh
```

### 2. 部署选项

#### 选项A：直接运行二进制文件
```bash
# 运行打包后的二进制文件
./dist/mcp-agent
```

#### 选项B：安装为系统服务（Ubuntu/Debian）
```bash
# 安装deb包
sudo dpkg -i mcp-agent_1.0.0_amd64.deb

# 启动服务
sudo systemctl start mcp-agent
sudo systemctl enable mcp-agent
```

#### 选项C：手动部署
```bash
# 解压tar包
tar -xzf release/mcp-agent-1.0.0.tar.gz

# 运行
./mcp-agent
```

## 🔧 配置说明

### 敏感信息保护
所有敏感信息都经过多层加密和混淆：

```python
# 配置获取方式
from src.secure_config import get_supabase_config

# 安全获取配置
config = get_supabase_config()
# config包含：url, key, tools_table, results_table
```

### 环境变量
```bash
# 运行时环境变量
export PACKAGED=1                    # 标记为打包环境
export ALLOW_ROOT=1                  # 允许root运行（可选）
export PYTHONIOENCODING=utf-8        # 设置编码
```

## 🛡️ 安全特性

### 1. 反调试保护
- 检测常见调试器（gdb, lldb, strace等）
- 监控调试环境变量
- 后台线程定期检查
- 检测到调试时自动退出

### 2. 反编译保护
- 检测反编译工具（uncompyle6, pycdc等）
- 检查调用栈异常
- 检测编译特征
- 发现反编译时数据自毁

### 3. 内存保护
- 敏感数据内存锁定
- 访问次数限制
- 自动内存清理
- 上下文管理器保护

### 4. 访问控制
- 基于时间的访问限制
- 系统指纹验证
- 环境完整性检查
- 异常行为监控

## 🔍 安全验证

### 1. 文件完整性检查
```bash
# 检查文件权限
ls -la dist/mcp-agent
# 应该显示: -r-x------ (权限500)

# 检查依赖库
ldd dist/mcp-agent
# 确保没有 "not found" 的库
```

### 2. 运行时检查
```bash
# 运行程序
./dist/mcp-agent

# 检查日志文件
tail -f debug_detection.log
tail -f decompile_detection.log
```

### 3. 安全测试
```bash
# 尝试调试（应该失败）
gdb ./dist/mcp-agent

# 尝试反编译（应该失败）
uncompyle6 dist/mcp-agent
```

## 🚨 安全最佳实践

### 1. 部署环境
- 使用最小权限原则运行
- 定期更新系统和依赖
- 监控系统日志
- 使用防火墙限制访问

### 2. 密钥管理
- 定期轮换敏感信息
- 使用不同的开发/生产环境配置
- 备份配置信息（安全存储）
- 监控配置访问

### 3. 监控和日志
```bash
# 监控安全日志
tail -f /var/log/mcp-agent/security.log

# 监控系统日志
journalctl -u mcp-agent -f
```

### 4. 应急响应
- 发现异常立即停止服务
- 保存日志和证据
- 更新配置和密钥
- 重新部署应用

## 🔧 故障排除

### 常见问题

#### 1. "调试器检测"错误
```bash
# 确保没有调试器在运行
# 检查环境变量
env | grep -i debug
# 关闭相关调试工具
```

#### 2. "系统指纹验证失败"
```bash
# 检查系统配置是否变化
# 重新生成指纹或更新配置
```

#### 3. "超过最大访问次数"
```bash
# 重启应用或等待时间窗口
# 检查是否有异常访问模式
```

#### 4. "缺少依赖库"
```bash
# 安装必要的系统库
sudo apt-get install libssl3 libc6 python3-dev
```

## 📊 性能影响

### 资源使用
- **内存**: 额外5-10MB用于安全保护
- **CPU**: 轻微性能开销（<5%）
- **启动时间**: 额外1-2秒用于安全检查

### 优化建议
- 在生产环境中禁用调试检测
- 定期清理安全日志
- 监控资源使用情况

## 🔄 更新和维护

### 1. 更新流程
```bash
# 备份当前配置
./dist/mcp-agent --backup-config

# 停止服务
sudo systemctl stop mcp-agent

# 更新应用
sudo dpkg -i mcp-agent-new-version.deb

# 启动服务
sudo systemctl start mcp-agent
```

### 2. 密钥轮换
```bash
# 运行密钥轮换
./dist/mcp-agent --rotate-keys

# 重启应用
sudo systemctl restart mcp-agent
```

## 📞 技术支持

如果遇到安全问题或需要技术支持：
1. 检查日志文件
2. 查看故障排除部分
3. 联系安全团队

---

**注意**: 本安全方案提供了深度保护，但没有任何系统能保证100%安全。请根据您的具体需求和安全要求选择合适的安全级别。