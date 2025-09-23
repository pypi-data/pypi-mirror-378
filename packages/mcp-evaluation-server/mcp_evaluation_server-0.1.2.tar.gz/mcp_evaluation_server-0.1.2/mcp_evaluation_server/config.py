"""MCP评估服务器配置管理"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置"""

    # Supabase数据库配置
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_service_role_key: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")
    
    # 数据表名称
    mcp_tools_table: str = "mcp_tools"
    mcp_test_results_table: str = "mcp_test_results"

    # 缓存配置
    redis_url: Optional[str] = Field(None, env="REDIS_URL")
    cache_ttl: int = Field(3600, env="CACHE_TTL")

    # 日志配置
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("logs/mcp_server.log", env="LOG_FILE")
    
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
        # 如果配置加载失败，提供清晰的错误信息
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