"""
实用的安全编码混淆器
提供多层编码保护，适合实际应用场景
"""

import base64
import hashlib
import os
import time
import platform
import uuid
import json
from typing import List, Dict, Any, Optional
import threading


class PracticalObfuscator:
    """实用的编码混淆器"""
    
    def __init__(self) -> None:
        self._access_count = 0
        self._max_accesses = 200
        self._lock = threading.Lock()
        self._system_key = self._generate_system_key()
        self._time_salt = int(time.time()) // 3600  # 每小时变化的salt
        
    def _generate_system_key(self) -> str:
        """生成基于系统的密钥"""
        system_info = f"{platform.system()}-{platform.machine()}-{uuid.getnode()}"
        return hashlib.sha256(system_info.encode()).hexdigest()[:32]
    
    def _custom_transform(self, data: str, operation: str) -> str:
        """自定义变换 - XOR版本"""
        result = []
        shift = sum(ord(c) for c in self._system_key) % 256
        
        # 将字符串转换为字节，进行XOR操作，再转回字符串
        data_bytes = data.encode('utf-8')
        
        if operation == 'encode':
            transformed_bytes = bytes([b ^ (shift + i + self._time_salt) % 256 for i, b in enumerate(data_bytes)])
        else:  # decode
            transformed_bytes = bytes([b ^ (shift + i + self._time_salt) % 256 for i, b in enumerate(data_bytes)])
        
        # 将字节转换为Base64安全的字符串
        return base64.b64encode(transformed_bytes).decode()
    
    def encode_sensitive_data(self, data: str) -> List[str]:
        """编码敏感数据"""
        with self._lock:
            self._access_count += 1
            
            # 分段处理
            chunks = [data[i:i+16] for i in range(0, len(data), 16)]
            
            encoded_chunks = []
            for i, chunk in enumerate(chunks):
                # 第一层：Base64
                b64_data = base64.b64encode(chunk.encode()).decode()
                
                # 第二层：自定义变换
                transformed = self._custom_transform(b64_data, 'encode')
                
                # 第三层：再次Base64
                final_encoded = transformed
                
                encoded_chunks.append(final_encoded)
            
            return encoded_chunks
    
    def decode_sensitive_data(self, encoded_chunks: List[str]) -> str:
        """解码敏感数据"""
        with self._lock:
            if self._access_count > self._max_accesses:
                raise Exception("访问次数超过限制")
            
            decoded_parts = []
            
            for chunk in encoded_chunks:
                try:
                    # 第一层：Base64解码（处理填充）
                    padding_needed = len(chunk) % 4
                    if padding_needed:
                        chunk += '=' * (4 - padding_needed)
                    b64_data = base64.b64decode(chunk.encode())
                    
                    # 第二层：逆向自定义变换
                    transformed_bytes = self._custom_transform(b64_data.decode('latin1'), 'decode')
                    transformed = base64.b64decode(transformed_bytes)
                    
                    # 第三层：最终Base64解码为原始字符串
                    original = base64.b64decode(transformed).decode('utf-8')
                    
                    decoded_parts.append(original)
                except Exception as e:
                    raise Exception(f"解码失败: {e}")
            
            return ''.join(decoded_parts)


class EnvironmentSecurity:
    """环境安全检查"""
    
    @staticmethod
    def validate_environment() -> bool:
        """验证运行环境"""
        # 检查调试环境变量
        debug_envs = ['PYDEVD_LOAD_VALUES_ASYNC', 'DEBUGPY', 'PDB_ACTIVE']
        for env in debug_envs:
            if os.getenv(env):
                raise Exception("检测到调试环境")
        
        # 检查是否在预期环境中运行
        if not os.getenv('ALLOW_DEV_MODE'):
            # 简单的路径检查
            cwd = os.getcwd()
            if 'test' in cwd.lower() or 'debug' in cwd.lower():
                if not os.getenv('ALLOW_TEST_MODE'):
                    raise Exception("非生产环境")
        
        return True
    
    @staticmethod
    def get_environment_fingerprint() -> str:
        """获取环境指纹"""
        env_data = (
            f"{os.getpid()}-{os.getuid() if hasattr(os, 'getuid') else '0'}-"
            f"{platform.node()}-{os.getcwd()}"
        )
        return hashlib.md5(env_data.encode()).hexdigest()


class SecureConfigStorage:
    """安全配置存储"""
    
    def __init__(self) -> None:
        self.obfuscator = PracticalObfuscator()
        self.env_security = EnvironmentSecurity()
        
        # 预编码的配置数据（使用实际编码数据）
        # 从.env文件编码的真实配置信息
        self._encoded_configs = {
            'supabase_url': [
                'bEZdIHJaXiJZby4qe013bn5Jb01EYx4Z',
                'VGNdIkt8UXx0JU0reyhddVFwURFCYx4Z',
                'VFlFeHIgRmFMJC8l'
            ],
            'supabase_key': [
                'bjxFdnIgRX52e0EoQShNaFJZZ2R4RR4Z',
                'QlheJEd8Qm1Me3NCfU0uLEguSW90cx4Z',
                'VT5nfkN+QVBxJ1Yo'
            ],
            'tools_table': [
                'b1lBZ0khQWJ3JG9i'
            ],
            'results_table': [
                'b1lBZ0khQXh2JUV+endNZnlJZxBCVR4Z'
            ]
        }
    
    def get_config(self, key: str) -> str:
        """安全获取配置"""
        # 环境验证
        self.env_security.validate_environment()
        
        if key not in self._encoded_configs:
            raise Exception(f"配置不存在: {key}")
        
        try:
            encoded_chunks = self._encoded_configs[key]
            return self.obfuscator.decode_sensitive_data(encoded_chunks)
        except Exception as e:
            raise Exception(f"获取配置失败: {e}")
    
    def get_all_configs(self) -> Dict[str, str]:
        """获取所有配置"""
        configs = {}
        for key in self._encoded_configs.keys():
            try:
                configs[key] = self.get_config(key)
            except Exception as e:
                print(f"警告: 获取配置 {key} 失败: {e}")
        return configs


# 全局实例
_config_storage = SecureConfigStorage()


def get_secure_config(key: str) -> str:
    """获取安全配置的便捷函数"""
    return _config_storage.get_config(key)


def get_all_secure_configs() -> Dict[str, str]:
    """获取所有安全配置"""
    return _config_storage.get_all_configs()


# 使用示例
if __name__ == "__main__":
    try:
        # 测试编码解码
        test_data = "https://example.supabase.co"
        obfuscator = PracticalObfuscator()
        
        encoded = obfuscator.encode_sensitive_data(test_data)
        print(f"编码后: {encoded}")
        
        decoded = obfuscator.decode_sensitive_data(encoded)
        print(f"解码后: {decoded}")
        
        # 测试配置获取
        url = get_secure_config('supabase_url')
        print(f"Supabase URL: {url}")
        
        key = get_secure_config('supabase_key')
        print(f"Supabase Key: {key[:20]}...")
        
    except Exception as e:
        print(f"错误: {e}")