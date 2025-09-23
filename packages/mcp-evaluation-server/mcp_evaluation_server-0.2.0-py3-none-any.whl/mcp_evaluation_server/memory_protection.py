"""
运行时内存保护和访问控制
提供敏感数据的内存管理和访问控制
"""

import threading
import time
import weakref
import gc
import os
import sys
from typing import Any, Optional, Dict
from contextlib import contextmanager
try:
    import ctypes
    import mmap
    HAS_MEMORY_PROTECTION = True
except ImportError:
    HAS_MEMORY_PROTECTION = False


class MemoryProtector:
    """内存保护器 - 保护敏感数据不被意外泄露"""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._protected_data = weakref.WeakValueDictionary()
        self._access_log = {}
        self._max_holding_time = 30  # 最大持有时间（秒）
        self._cleanup_interval = 10  # 清理间隔（秒）
        self._last_cleanup = time.time()
        
    def protect_data(self, data: Any, data_id: str) -> 'ProtectedData':
        """保护数据"""
        with self._lock:
            # 检查是否需要清理
            if time.time() - self._last_cleanup > self._cleanup_interval:
                self._cleanup_expired_data()
                self._last_cleanup = time.time()
            
            protected = ProtectedData(data, data_id, self)
            self._protected_data[data_id] = protected
            self._access_log[data_id] = {
                'created_time': time.time(),
                'access_count': 0,
                'last_access': time.time()
            }
            
            return protected
    
    def _cleanup_expired_data(self) -> None:
        """清理过期数据"""
        current_time = time.time()
        expired_ids = []
        
        for data_id, log in self._access_log.items():
            if current_time - log['created_time'] > self._max_holding_time:
                expired_ids.append(data_id)
        
        for data_id in expired_ids:
            if data_id in self._protected_data:
                del self._protected_data[data_id]
            if data_id in self._access_log:
                del self._access_log[data_id]
    
    def log_access(self, data_id: str) -> None:
        """记录访问"""
        with self._lock:
            if data_id in self._access_log:
                self._access_log[data_id]['access_count'] += 1
                self._access_log[data_id]['last_access'] = time.time()
    
    def get_access_stats(self, data_id: str) -> Optional[Dict]:
        """获取访问统计"""
        with self._lock:
            return self._access_log.get(data_id)


class ProtectedData:
    """受保护的数据对象"""
    
    def __init__(self, data: Any, data_id: str, protector: MemoryProtector):
        self._data = data
        self._data_id = data_id
        self._protector = protector
        self._created_time = time.time()
        self._encrypted = False
        self._memory_locked = False
        
    def __enter__(self) -> 'ProtectedData':
        """上下文管理器进入"""
        self._protector.log_access(self._data_id)
        
        # 如果数据被加密，先解密
        if self._encrypted:
            self._decrypt_data()
        
        # 锁定内存
        self._lock_memory()
        
        return self._data
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """上下文管理器退出"""
        # 加密数据
        self._encrypt_data()
        
        # 解锁内存
        self._unlock_memory()
        
        # 强制垃圾回收
        gc.collect()
    
    def _lock_memory(self) -> None:
        """锁定内存防止交换到磁盘"""
        if not HAS_MEMORY_PROTECTION or self._memory_locked:
            return
        
        try:
            # 获取数据内存地址
            data_address = id(self._data)
            data_size = sys.getsizeof(self._data)
            
            # 使用mlock锁定内存（Linux）
            if hasattr(ctypes, 'mlock'):
                libc = ctypes.CDLL('libc.so.6')
                result = libc.mlock(data_address, data_size)
                if result == 0:
                    self._memory_locked = True
        except:
            pass
    
    def _unlock_memory(self) -> None:
        """解锁内存"""
        if not HAS_MEMORY_PROTECTION or not self._memory_locked:
            return
        
        try:
            data_address = id(self._data)
            data_size = sys.getsizeof(self._data)
            
            if hasattr(ctypes, 'munlock'):
                libc = ctypes.CDLL('libc.so.6')
                libc.munlock(data_address, data_size)
                self._memory_locked = False
        except:
            pass
    
    def _encrypt_data(self) -> None:
        """加密数据（简化版本）"""
        if isinstance(self._data, str):
            # 简单的字符变换（实际应用中应使用更安全的加密）
            encrypted_chars = []
            for char in self._data:
                encrypted_chars.append(chr(ord(char) ^ 0xFF))
            self._data = ''.join(encrypted_chars)
            self._encrypted = True
    
    def _decrypt_data(self) -> None:
        """解密数据"""
        if isinstance(self._data, str) and self._encrypted:
            decrypted_chars = []
            for char in self._data:
                decrypted_chars.append(chr(ord(char) ^ 0xFF))
            self._data = ''.join(decrypted_chars)
            self._encrypted = False


class AccessController:
    """访问控制器 - 限制敏感信息的访问"""
    
    def __init__(self, max_accesses: int = 100, time_window: int = 3600):
        self._max_accesses = max_accesses
        self._time_window = time_window
        self._access_records = {}
        self._lock = threading.Lock()
        
    def check_access(self, resource_id: str) -> bool:
        """检查访问权限"""
        with self._lock:
            current_time = time.time()
            
            # 清理过期记录
            self._cleanup_expired_records(current_time)
            
            # 获取或创建访问记录
            if resource_id not in self._access_records:
                self._access_records[resource_id] = []
            
            # 检查访问次数
            recent_accesses = [
                access_time for access_time in self._access_records[resource_id]
                if current_time - access_time < self._time_window
            ]
            
            if len(recent_accesses) >= self._max_accesses:
                raise Exception(f"超过最大访问次数限制: {self._max_accesses}")
            
            # 记录访问
            self._access_records[resource_id].append(current_time)
            return True
    
    def _cleanup_expired_records(self, current_time: float) -> None:
        """清理过期记录"""
        expired_resources = []
        
        for resource_id, access_times in self._access_records.items():
            # 移除过期记录
            valid_times = [
                access_time for access_time in access_times
                if current_time - access_time < self._time_window
            ]
            
            if valid_times:
                self._access_records[resource_id] = valid_times
            else:
                expired_resources.append(resource_id)
        
        # 移除空记录
        for resource_id in expired_resources:
            del self._access_records[resource_id]
    
    def get_access_count(self, resource_id: str) -> int:
        """获取访问次数"""
        with self._lock:
            if resource_id not in self._access_records:
                return 0
            
            current_time = time.time()
            recent_accesses = [
                access_time for access_time in self._access_records[resource_id]
                if current_time - access_time < self._time_window
            ]
            
            return len(recent_accesses)


# 全局实例
_memory_protector = MemoryProtector()
_access_controller = AccessController()


@contextmanager
def secure_access(data: Any, data_id: str) -> Any:
    """安全访问上下文管理器"""
    _access_controller.check_access(data_id)
    protected_data = _memory_protector.protect_data(data, data_id)
    
    try:
        with protected_data as decrypted_data:
            yield decrypted_data
    finally:
        # 清理引用
        del protected_data
        gc.collect()


def get_access_stats(resource_id: str) -> Optional[Dict]:
    """获取访问统计"""
    return _memory_protector.get_access_stats(resource_id)