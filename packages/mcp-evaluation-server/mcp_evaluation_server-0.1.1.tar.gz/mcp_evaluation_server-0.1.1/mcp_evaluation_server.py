#!/usr/bin/env python3
"""
MCP评估服务器命令行工具
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="MCP评估服务器 - 工具搜索和评估服务",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s                          # 启动服务器
  %(prog)s --version               # 显示版本
  %(prog)s --check-config          # 检查配置
  %(prog)s --init-config           # 初始化配置文件
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="检查配置文件是否正确"
    )
    
    parser.add_argument(
        "--init-config",
        action="store_true",
        help="初始化配置文件"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="日志级别 (默认: INFO)"
    )
    
    args = parser.parse_args()
    
    if args.init_config:
        init_config()
        return
    
    if args.check_config:
        check_config()
        return
    
    # 启动服务器
    start_server()


def init_config():
    """初始化配置文件"""
    print("🔧 初始化配置文件...")
    
    env_example = Path(__file__).parent / ".env.example"
    env_file = Path.cwd() / ".env"
    
    if not env_example.exists():
        print("❌ 找不到 .env.example 文件")
        sys.exit(1)
    
    if env_file.exists():
        response = input("⚠️  .env 文件已存在，是否覆盖？ (y/N): ")
        if response.lower() != 'y':
            print("❌ 取消初始化")
            return
    
    import shutil
    shutil.copy(env_example, env_file)
    
    print(f"✅ 配置文件已创建: {env_file}")
    print("📝 请编辑 .env 文件，填入您的配置信息")
    print("必需配置:")
    print("  - SUPABASE_URL")
    print("  - SUPABASE_SERVICE_ROLE_KEY")


def check_config():
    """检查配置"""
    print("🔍 检查配置...")
    
    try:
        from src.config import get_settings
        settings = get_settings()
        print("✅ 配置加载成功")
        print(f"📊 数据库URL: {settings.supabase_url}")
        print(f"📋 日志级别: {settings.log_level}")
        print(f"📁 日志文件: {settings.log_file}")
        
        # 测试数据库连接
        import asyncio
        async def test_connection():
            from src.database import DatabaseManager
            db_manager = DatabaseManager()
            return await db_manager.health_check()
        
        is_healthy = asyncio.run(test_connection())
        if is_healthy:
            print("✅ 数据库连接正常")
        else:
            print("❌ 数据库连接失败")
            
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        sys.exit(1)


def start_server():
    """启动服务器"""
    print("🚀 启动MCP评估服务器...")
    
    try:
        from src.main import main
        main()
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()