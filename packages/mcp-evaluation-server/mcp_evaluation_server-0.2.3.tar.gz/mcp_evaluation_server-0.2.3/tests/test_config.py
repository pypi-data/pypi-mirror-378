"""测试配置"""

import pytest
import os
from unittest.mock import patch
from mcp_evaluation_server.config import Settings, get_settings


@pytest.fixture(autouse=True)
def setup_test_env():
    """设置测试环境变量"""
    # 清理所有可能的环境变量
    for key in ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "LOG_LEVEL"]:
        if key in os.environ:
            os.environ.pop(key, None)
    
    # 设置测试环境变量
    os.environ["SUPABASE_URL"] = "https://test.supabase.co"
    os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test-key"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    yield
    
    # 清理测试环境
    for key in ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "LOG_LEVEL"]:
        if key in os.environ:
            os.environ.pop(key, None)


class TestSettings:
    """测试配置管理"""
    
    def test_settings_from_env(self):
        """测试从环境变量加载配置"""
        # 验证设置可以正常创建
        settings = Settings()
        
        # 验证必要的字段存在
        assert settings.supabase_url is not None
        assert settings.supabase_service_role_key is not None
        assert settings.log_level is not None
        
        # 验证默认值
        assert settings.mcp_tools_table == "mcp_tools"
        assert settings.mcp_test_results_table == "mcp_test_results"
        assert settings.cache_ttl == 3600