"""FastMCP服务器 - MCP工具评估助手（简化版）"""

import logging
import asyncio
import sys
import argparse
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP
from .secure_config_manager import get_settings, get_security_status
from .database import DatabaseManager
from .models import MCPToolInfo, ToolSearchFilter, CategoryStats
from .utils import (
    format_tool_info,
    format_search_summary,
    log_search_query
)

# 设置日志
try:
    settings = get_settings()
    security_status = get_security_status()
    
    # 根据安全状态调整日志级别
    log_level = settings.log_level
    
    # 创建日志处理器
    handlers = []
    log_file = settings.get_log_file()
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    # 只在非stdio模式时避免输出到控制台
    import sys
    if "server" in sys.argv[1:2] or "http" in sys.argv[1:2]:
        handlers.append(logging.StreamHandler())
        if security_status.get('security_enabled', False):
            print("✅ 安全保护已启用")
        else:
            print("⚠️  安全保护未启用，使用环境变量配置")
    else:
        # stdio模式，不输出到控制台
        handlers.append(logging.NullHandler())
    
    if not handlers:
        handlers = [logging.NullHandler()]
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    logger = logging.getLogger(__name__)
    
except Exception as e:
    import sys
    # 只在非stdio模式时输出错误
    if "server" in sys.argv[1:2] or "http" in sys.argv[1:2]:
        print(f"❌ 配置加载失败: {e}")
    raise

# 初始化FastMCP服务器
mcp = FastMCP("MCP工具评估助手")

# 初始化数据库管理器
db_manager = DatabaseManager()


@mcp.tool()
async def search_mcp_tools(
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_tashan_score: Optional[float] = None,
    max_tashan_score: Optional[float] = None,
    deployment_method: Optional[str] = None,
    author: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "tashan_score"
) -> Dict[str, Any]:
    """搜索MCP工具
    
    根据关键词、分类、评分等条件搜索MCP工具，返回工具列表和相关信息。
    
    Args:
        query: 搜索关键词，在工具名称和描述中搜索
        category: 工具分类，如"开发工具推荐"、"文档处理"等
        min_tashan_score: 最低他山评分（0-100）
        max_tashan_score: 最高他山评分（0-100）
        deployment_method: 部署方式，如"npm"、"pip"、"docker"等
        author: 工具作者
        limit: 返回结果数量限制，默认20，最大100
        offset: 偏移量，默认0
        sort_by: 排序方式，可选值：tashan_score（默认）、sustainability_score、popularity_score、lobehub_score
    
    Returns:
        包含工具列表、总数和搜索摘要的字典
        
    Example:
        >>> search_mcp_tools(query="github", limit=10)
        {
            "success": True,
            "tools": [...],
            "total_count": 45,
            "search_summary": "找到 10 个工具(共 45 个)基于条件: 关键词 'github'",
            "filters": {...}
        }
    """
    try:
        # 验证参数
        limit = max(1, min(100, limit))
        offset = max(0, offset)
        
        if min_tashan_score is not None:
            min_tashan_score = max(0, min(100, min_tashan_score))
        if max_tashan_score is not None:
            max_tashan_score = max(0, min(100, max_tashan_score))
        
        # 验证排序字段
        valid_sort_fields = ["tashan_score", "sustainability_score", "popularity_score", "lobehub_score"]
        if sort_by not in valid_sort_fields:
            sort_by = "tashan_score"
        
        # 创建搜索过滤器
        filters = ToolSearchFilter(
            query=query,
            category=category,
            min_tashan_score=min_tashan_score,
            max_tashan_score=max_tashan_score,
            deployment_method=deployment_method,
            author=author,
            limit=limit,
            offset=offset
        )
        
        # 记录搜索查询
        log_search_query(filters)
        
        # 执行搜索
        tools = await db_manager.search_tools(filters)
        
        # 根据sort_by参数进行排序
        if sort_by != "tashan_score":
            valid_sort_fields = {
                "tashan_score", "sustainability_score", "popularity_score", 
                "lobehub_score", "comprehensive_score", "test_timestamp"
            }
            
            if sort_by in valid_sort_fields:
                tools.sort(key=lambda x: getattr(x, sort_by) or 0, reverse=True)
        
        # 获取总数
        total_count = await db_manager.get_total_tools_count()
        
        # 格式化工具信息
        formatted_tools = [format_tool_info(tool) for tool in tools]
        
        # 生成搜索摘要
        search_summary = format_search_summary(filters, total_count, len(tools))
        
        result = {
            "success": True,
            "tools": formatted_tools,
            "total_count": total_count,
            "search_summary": search_summary,
            "filters": filters.dict(),
            "sort_by": sort_by
        }
        
        logger.info(f"搜索完成: {search_summary}")
        return result
        
    except Exception as e:
        logger.error(f"搜索工具失败: {e}")
        return {
            "success": False,
            "tools": [],
            "total_count": 0,
            "search_summary": f"搜索失败: {str(e)}",
            "filters": {},
            "error": str(e)
        }


@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """服务健康检查
    
    检查数据库连接和服务状态。
    
    Returns:
        包含健康状态和系统信息的字典
    """
    try:
        # 检查数据库连接
        db_healthy = await db_manager.health_check()
        
        # 获取工具总数
        total_tools = await db_manager.get_total_tools_count()
        
        result = {
            "success": True,
            "status": "healthy" if db_healthy else "unhealthy",
            "database_connected": db_healthy,
            "total_tools": total_tools,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        logger.info(f"健康检查: {result['status']}")
        return result
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "success": False,
            "status": "error",
            "database_connected": False,
            "total_tools": 0,
            "timestamp": asyncio.get_event_loop().time(),
            "error": str(e)
        }


def main():
    """启动FastMCP服务器"""
    # 早期检测stdio模式，避免任何输出干扰MCP通信
    is_stdio_mode = False
    if len(sys.argv) == 2 and sys.argv[1] == "server":
        # MCP客户端调用时传递"server"参数，但实际需要stdio模式
        is_stdio_mode = True
    elif len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == "stdio"):
        is_stdio_mode = True
    
    if is_stdio_mode:
        # 为stdio模式配置完全静默运行
        import warnings
        import os
        warnings.filterwarnings("ignore")  # 禁用所有警告
        os.environ["FASTMCP_DISABLE_BANNER"] = "1"  # 禁用FastMCP横幅
        
        # 完全禁用日志输出到stdout/stderr
        root_logger = logging.getLogger()
        root_logger.handlers = []
        root_logger.addHandler(logging.NullHandler())
        root_logger.setLevel(logging.CRITICAL)
        
        # 直接运行stdio模式，不加载任何配置输出
        mcp.run(transport="stdio")
        return
    
    # 非stdio模式的正常参数解析和配置加载
    parser = argparse.ArgumentParser(description="MCP工具评估助手服务器")
    parser.add_argument(
        "mode",
        nargs="?",
        default="stdio", 
        choices=["stdio", "server", "http"],
        help="运行模式: stdio (默认), server (HTTP服务器), http (同server)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="HTTP服务器监听地址 (默认: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP服务器端口 (默认: 8000)"
    )
    parser.add_argument(
        "--path",
        default="/mcp",
        help="HTTP服务器路径 (默认: /mcp)"
    )
    
    args = parser.parse_args()
    
    # HTTP服务器模式
    if args.mode in ["server", "http"]:
        logger.info(f"启动HTTP服务器模式: http://{args.host}:{args.port}{args.path}")
        mcp.run(
            transport="http",
            host=args.host,
            port=args.port,
            path=args.path
        )
    else:
        # 默认stdio模式（不应该到达这里，因为已在上面处理）
        import warnings
        import os
        warnings.filterwarnings("ignore")
        os.environ["FASTMCP_DISABLE_BANNER"] = "1"
        root_logger = logging.getLogger()
        root_logger.handlers = []
        root_logger.addHandler(logging.NullHandler())
        mcp.run(transport="stdio")


def run_simple_server():
    """运行简化的MCP服务器"""
    import asyncio
    import os
    import sys
    
    # 添加项目路径以便导入
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    sys.path.insert(0, project_root)
    
    # 导入简化的服务器
    from .simple_server import SimpleMCPServer, run_stdio_server
    
    # 静默模式 - 禁用警告但不重定向stdio
    import warnings
    warnings.filterwarnings("ignore")
    
    # 运行简化的服务器
    asyncio.run(run_stdio_server())


if __name__ == "__main__":
    # 检查是否使用FastMCP模式
    if "--fastmcp" in sys.argv:
        main()
    else:
        # 默认使用simple_server模式以确保兼容性
        run_simple_server()