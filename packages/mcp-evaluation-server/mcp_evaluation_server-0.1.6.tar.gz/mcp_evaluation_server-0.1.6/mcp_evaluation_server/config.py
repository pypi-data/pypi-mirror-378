"""MCP评估服务器配置管理"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置"""

    # Supabase数据库配置
    supabase_url: str
    supabase_service_role_key: str
    
    # 数据表名称
    mcp_tools_table: str = "mcp_tools"
    mcp_test_results_table: str = "mcp_test_results"

    # 缓存配置
    redis_url: Optional[str] = None
    cache_ttl: int = 3600

    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None  # 默认不写文件
    
    def get_log_file(self) -> Optional[str]:
        """获取日志文件路径，如果目录不存在则创建"""
        if self.log_file:
            log_path = Path(self.log_file)
            # 如果是相对路径，使用当前目录
            if not log_path.is_absolute():
                log_path = Path.cwd() / log_path
            # 创建日志目录
            log_path.parent.mkdir(parents=True, exist_ok=True)
            return str(log_path)
        return None
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "allow"
    }


# 全局配置实例
def get_settings():
    """获取配置实例"""
    try:
        return Settings()
    except Exception as e:
        import sys
        # 只在HTTP模式下输出错误信息
        if "server" in sys.argv[1:2] or "http" in sys.argv[1:2]:
            print(f"❌ 配置加载失败: {e}")
            print("请确保设置了以下环境变量：")
            print("  - SUPABASE_URL")
            print("  - SUPABASE_SERVICE_ROLE_KEY")
            print("或者创建 .env 文件（参考 .env.example）")
        raise ConfigurationError(f"配置加载失败: {e}")


class ConfigurationError(Exception):
    """配置错误异常"""
    pass

# 延迟加载配置
settings = None