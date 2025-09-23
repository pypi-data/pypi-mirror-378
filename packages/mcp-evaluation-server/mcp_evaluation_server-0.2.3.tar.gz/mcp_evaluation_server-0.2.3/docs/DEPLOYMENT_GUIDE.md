# MCP Evaluation Server 部署和发布指南

## 安全发布方案

### 重要提醒
⚠️ **安全警告**：绝不将敏感信息（如API密钥、数据库凭证）硬编码到代码中或打包到发布包中。这会导致严重的安全风险。

## 1. GitHub私有仓库设置

### 1.1 创建GitHub仓库
```bash
# 1. 在GitHub上创建私有仓库
# 2. 初始化本地仓库
git init
git add .
git commit -m "Initial commit"

# 3. 添加远程仓库
git remote add origin https://github.com/your-username/mcp-evaluation-server.git

# 4. 推送到GitHub
git branch -M main
git push -u origin main
```

### 1.2 配置GitHub Secrets
在GitHub仓库设置中添加以下secrets：
- `PYPI_API_TOKEN`: PyPI发布令牌
- `TEST_PYPI_API_TOKEN`: 测试PyPI发布令牌

## 2. PyPI发布准备

### 2.1 构建包
```bash
# 安装构建工具
pip install build hatchling

# 构建包
python -m build

# 检查包
pip install twine
twine check dist/*
```

### 2.2 测试发布到Test PyPI
```bash
# 发布到测试PyPI
twine upload --repository testpypi dist/*
```

### 2.3 正式发布到PyPI
```bash
# 发布到正式PyPI
twine upload dist/*
```

## 3. 自动化发布流程

### 3.1 使用GitHub Actions
项目已配置以下自动化工作流：

- **测试工作流** (`.github/workflows/test.yml`): 自动运行测试
- **发布工作流** (`.github/workflows/publish.yml`): 自动发布到PyPI
- **发布工作流** (`.github/workflows/release.yml`): 自动创建GitHub Release

### 3.2 发布流程
```bash
# 1. 创建版本标签
git tag v0.1.0

# 2. 推送标签
git push origin v0.1.0

# 3. GitHub Actions会自动：
#    - 运行测试
#    - 构建包
#    - 发布到PyPI
#    - 创建GitHub Release
```

## 4. 用户安装和使用

### 4.1 安装
```bash
# 从PyPI安装
pip install mcp-evaluation-server

# 从源码安装
pip install git+https://github.com/your-username/mcp-evaluation-server.git
```

### 4.2 配置
```bash
# 初始化配置
mcp-evaluation-server --init-config

# 编辑配置文件
nano .env
```

### 4.3 运行
```bash
# 启动服务器
mcp-evaluation-server

# 检查配置
mcp-evaluation-server --check-config
```

## 5. 安全最佳实践

### 5.1 环境变量管理
- 使用 `.env` 文件进行本地开发
- 在生产环境中使用系统环境变量
- 在CI/CD中使用secrets管理敏感信息

### 5.2 配置验证
```python
# 代码中包含配置验证
def get_settings():
    try:
        return Settings()
    except Exception as e:
        raise ConfigurationError(f"配置加载失败: {e}")
```

### 5.3 敏感信息保护
- 永远不将 `.env` 文件提交到版本控制
- 使用 `.gitignore` 排除敏感文件
- 定期轮换API密钥和密码

## 6. 故障排除

### 6.1 常见问题
1. **配置加载失败**: 检查 `.env` 文件和环境变量
2. **权限问题**: 确保PyPI API token正确
3. **构建失败**: 检查依赖项和Python版本

### 6.2 调试技巧
```bash
# 启用详细日志
mcp-evaluation-server --log-level DEBUG

# 检查包内容
tar -tzf dist/*.tar.gz
```

## 7. 维护和更新

### 7.1 版本管理
使用语义化版本控制：
- 主版本号：破坏性更改
- 次版本号：新功能
- 修订版本号：错误修复

### 7.2 更新流程
1. 在开发分支进行开发
2. 创建Pull Request到main分支
3. 通过所有测试后合并
4. 创建版本标签
5. 自动发布

---

通过以上方案，您可以安全地将项目发布到GitHub私有仓库和PyPI，同时保护敏感信息安全。