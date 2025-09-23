"""
安全配置管理器
集成安全保护与现有配置系统
"""

import os
import sys
import logging
from typing import Optional, Dict, Any
from pathlib import Path

# 添加当前目录到路径，以便导入安全模块
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from practical_security import get_secure_config, get_all_secure_configs, EnvironmentSecurity
    import security_ext
    HAS_SECURITY = True
except ImportError as e:
    HAS_SECURITY = False
    print(f"警告: 安全模块不可用，将使用普通配置: {e}")

# 导入原有配置
try:
    from .config import Settings, ConfigurationError
except ImportError:
    # 如果相对导入失败，使用绝对导入
    try:
        from mcp_evaluation_server.config import Settings, ConfigurationError
    except ImportError:
        # 最后的回退方案
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        from config import Settings, ConfigurationError

logger = logging.getLogger(__name__)


class SecureConfigManager:
    """安全配置管理器"""
    
    def __init__(self):
        self._config_cache = {}
        self._security_enabled = HAS_SECURITY
        self._access_count = 0
        self._max_accesses = 100
        
    def _security_check(self):
        """安全检查"""
        if not self._security_enabled:
            return
            
        # 访问次数限制
        self._access_count += 1
        if self._access_count > self._max_accesses:
            raise Exception("超过最大访问次数限制")
        
        # 环境安全检查
        try:
            EnvironmentSecurity.validate_environment()
        except Exception as e:
            logger.warning(f"环境安全检查失败: {e}")
    
    def get_secure_supabase_config(self) -> Dict[str, str]:
        """获取安全的Supabase配置"""
        self._security_check()
        
        if self._security_enabled:
            try:
                # 使用安全配置
                configs = get_all_secure_configs()
                
                # 使用C扩展进行额外保护
                if hasattr(security_ext, 'check_integrity'):
                    for key, value in configs.items():
                        checksum = security_ext.check_integrity(value.encode())
                        logger.debug(f"配置 {key} 完整性检查: {checksum}")
                
                return {
                    'supabase_url': configs.get('supabase_url', ''),
                    'supabase_service_role_key': configs.get('supabase_key', ''),
                    'mcp_tools_table': configs.get('tools_table', 'mcp_tools'),
                    'mcp_test_results_table': configs.get('results_table', 'mcp_test_results')
                }
            except Exception as e:
                logger.error(f"安全配置获取失败: {e}")
                # 降级到环境变量配置
                return self._get_env_config()
        else:
            # 使用环境变量配置
            return self._get_env_config()
    
    def _get_env_config(self) -> Dict[str, str]:
        """从环境变量获取配置"""
        return {
            'supabase_url': os.getenv('SUPABASE_URL', ''),
            'supabase_service_role_key': os.getenv('SUPABASE_SERVICE_ROLE_KEY', ''),
            'mcp_tools_table': os.getenv('MCP_TOOLS_TABLE', 'mcp_tools'),
            'mcp_test_results_table': os.getenv('MCP_TEST_RESULTS_TABLE', 'mcp_test_results')
        }
    
    def get_settings(self) -> Settings:
        """获取设置实例，兼容原有API"""
        try:
            # 尝试使用安全配置
            secure_config = self.get_secure_supabase_config()
            
            # 创建临时环境变量
            original_env = {}
            for key, value in secure_config.items():
                env_key = key.upper()
                original_env[env_key] = os.getenv(env_key)
                os.environ[env_key] = value
            
            try:
                # 使用原有Settings类
                settings = Settings()
                return settings
            finally:
                # 恢复原始环境变量
                for env_key in original_env:
                    if original_env[env_key] is None:
                        os.environ.pop(env_key, None)
                    else:
                        os.environ[env_key] = original_env[env_key]
                        
        except Exception as e:
            logger.warning(f"安全配置失败，使用原有配置: {e}")
            # 降级到原有配置
            return Settings()
    
    def get_config_value(self, key: str) -> str:
        """获取特定配置值"""
        try:
            if self._security_enabled:
                # 映射配置键名
                key_mapping = {
                    'SUPABASE_URL': 'supabase_url',
                    'SUPABASE_SERVICE_ROLE_KEY': 'supabase_key',
                    'MCP_TOOLS_TABLE': 'tools_table',
                    'MCP_TEST_RESULTS_TABLE': 'results_table'
                }
                
                secure_key = key_mapping.get(key)
                if secure_key:
                    return get_secure_config(secure_key)
            
            # 降级到环境变量
            return os.getenv(key, '')
        except Exception as e:
            logger.error(f"获取配置 {key} 失败: {e}")
            return ''
    
    def is_security_enabled(self) -> bool:
        """检查安全功能是否启用"""
        return self._security_enabled
    
    def get_security_status(self) -> Dict[str, Any]:
        """获取安全状态"""
        return {
            'security_enabled': self._security_enabled,
            'access_count': self._access_count,
            'max_accesses': self._max_accesses,
            'cached_configs': list(self._config_cache.keys())
        }


# 全局配置管理器实例
_config_manager = SecureConfigManager()


def get_settings() -> Settings:
    """获取设置实例，兼容原有API"""
    return _config_manager.get_settings()


def get_secure_supabase_config() -> Dict[str, str]:
    """获取安全的Supabase配置"""
    return _config_manager.get_secure_supabase_config()


def get_config_value(key: str) -> str:
    """获取特定配置值"""
    return _config_manager.get_config_value(key)


def get_security_status() -> Dict[str, Any]:
    """获取安全状态"""
    return _config_manager.get_security_status()


# 向后兼容
def get_settings_legacy():
    """原有的配置获取函数，保持兼容"""
    try:
        return get_settings()
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        print("请确保设置了以下环境变量：")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_SERVICE_ROLE_KEY")
        print("或者创建 .env 文件（参考 .env.example）")
        raise ConfigurationError(f"配置加载失败: {e}")


# 测试函数
def test_security_integration():
    """测试安全集成"""
    print("🧪 测试安全配置集成...")
    
    try:
        # 测试安全状态
        status = get_security_status()
        print(f"安全状态: {status}")
        
        # 测试配置获取
        if status['security_enabled']:
            print("✅ 安全功能已启用")
            
            # 测试安全配置获取
            config = get_secure_supabase_config()
            print(f"Supabase URL: {config.get('supabase_url', 'N/A')[:20]}...")
            print(f"Tools表: {config.get('mcp_tools_table', 'N/A')}")
        else:
            print("⚠️  安全功能未启用，使用环境变量")
            
            # 测试原有配置
            settings = get_settings()
            print(f"原有配置可用: {bool(settings.supabase_url)}")
        
        print("✅ 安全集成测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 安全集成测试失败: {e}")
        return False


if __name__ == "__main__":
    # 运行测试
    test_security_integration()