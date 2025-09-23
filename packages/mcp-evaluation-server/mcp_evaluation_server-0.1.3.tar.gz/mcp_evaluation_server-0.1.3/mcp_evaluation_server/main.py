"""FastMCP服务器 - MCP工具评估助手"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP
from .secure_config_manager import get_settings, get_security_status
from .database import DatabaseManager
from .models import MCPToolInfo, ToolSearchFilter, CategoryStats
from .utils import (
    format_tool_info,
    generate_recommendations,
    generate_use_cases,
    format_search_summary,
    validate_sort_field,
    log_search_query,
    calculate_comprehensive_score
)

# 设置日志
try:
    settings = get_settings()
    security_status = get_security_status()
    
    # 根据安全状态调整日志级别
    log_level = settings.log_level
    if security_status.get('security_enabled', False):
        print("✅ 安全保护已启用")
    else:
        print("⚠️  安全保护未启用，使用环境变量配置")
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(settings.log_file),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
except Exception as e:
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
    offset: int = 0
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
            "filters": filters.dict()
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
async def get_tool_evaluation(
    tool_name: str,
    include_recommendations: bool = True,
    include_use_cases: bool = True,
    include_test_results: bool = False,
    test_results_limit: int = 5
) -> Dict[str, Any]:
    """获取工具详细评估报告
    
    根据工具名称获取详细的评估信息，包括评分、建议和适用场景。
    
    Args:
        tool_name: 工具名称
        include_recommendations: 是否包含使用建议，默认True
        include_use_cases: 是否包含适用场景，默认True
        include_test_results: 是否包含测试结果，默认False
        test_results_limit: 测试结果数量限制，默认5
    
    Returns:
        包含工具详细信息和评估报告的字典
        
    Example:
        >>> get_tool_evaluation(tool_name="github-mcp-server")
        {
            "success": True,
            "tool_info": {...},
            "evaluation": {...},
            "recommendations": [...],
            "use_cases": [...],
            "test_results": [...]
        }
    """
    try:
        # 获取工具信息
        tool = await db_manager.get_tool_by_name(tool_name)
        if not tool:
            return {
                "success": False,
                "tool_info": None,
                "evaluation": {},
                "recommendations": [],
                "use_cases": [],
                "test_results": [],
                "error": f"未找到工具: {tool_name}"
            }
        
        # 格式化工具信息
        formatted_tool = format_tool_info(tool)
        
        # 构建评估信息
        evaluation = {
            "comprehensive_score": calculate_comprehensive_score(tool),
            "score_breakdown": {
                "tashan_score": tool.tashan_score,
                "utility_score": tool.utility_score,
                "sustainability_score": tool.sustainability_score,
                "popularity_score": tool.popularity_score,
                "lobehub_score": tool.lobehub_score,
                "lobehub_evaluate": tool.lobehub_evaluate,
            },
            "quality_metrics": {
                "test_success_rate": tool.test_success_rate,
                "test_count": tool.test_count,
                "last_test_time": tool.last_test_time.isoformat() if tool.last_test_time else None,
                "github_activity": {
                    "stars": tool.lobehub_stars,
                    "forks": tool.lobehub_forks,
                }
            },
            "deployment_info": {
                "method": tool.deployment_method,
                "package_name": tool.package_name,
                "requires_api_key": tool.requires_api_key,
                "github_url": tool.github_url,
                "project_url": tool.url
            }
        }
        
        # 生成建议和适用场景
        recommendations = generate_recommendations(tool) if include_recommendations else []
        use_cases = generate_use_cases(tool) if include_use_cases else []
        
        # 获取测试结果
        test_results = []
        if include_test_results:
            results = await db_manager.get_tool_test_results(tool.tool_id, test_results_limit)
            test_results = [result.dict() for result in results]
        
        result = {
            "success": True,
            "tool_info": formatted_tool,
            "evaluation": evaluation,
            "recommendations": recommendations,
            "use_cases": use_cases,
            "test_results": test_results
        }
        
        logger.info(f"获取工具评估报告: {tool_name}")
        return result
        
    except Exception as e:
        logger.error(f"获取工具评估失败: {e}")
        return {
            "success": False,
            "tool_info": None,
            "evaluation": {},
            "recommendations": [],
            "use_cases": [],
            "test_results": [],
            "error": str(e)
        }


@mcp.tool()
async def get_top_tools(
    sort_by: str = "tashan_score",
    limit: int = 10,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """获取热门工具排行榜
    
    根据指定评分维度获取热门工具排行榜。
    
    Args:
        sort_by: 排序字段，可选值：
                 - tashan_score (他山评分，默认)
                 - utility_score (实用性评分)
                 - sustainability_score (可持续性评分)
                 - popularity_score (受欢迎度评分)
                 - lobehub_score (LobeHub评分)
                 - test_success_rate (测试成功率)
        limit: 返回数量限制，默认10，最大50
        category: 可选分类过滤
    
    Returns:
        包含排行榜和统计信息的字典
        
    Example:
        >>> get_top_tools(sort_by="tashan_score", limit=5)
        {
            "success": True,
            "tools": [...],
            "sort_criteria": {
                "sort_by": "tashan_score",
                "limit": 5,
                "category": null
            },
            "statistics": {...}
        }
    """
    try:
        # 验证参数
        sort_by = validate_sort_field(sort_by)
        limit = max(1, min(50, limit))
        
        # 获取热门工具
        if category:
            # 如果有分类过滤，先搜索再排序
            filters = ToolSearchFilter(
                category=category,
                limit=limit,
                offset=0
            )
            tools = await db_manager.search_tools(filters)
            # 按指定字段排序
            reverse_sort = sort_by not in ["created_at", "updated_at"]
            tools.sort(key=lambda x: getattr(x, sort_by) or 0, reverse=reverse_sort)
        else:
            tools = await db_manager.get_top_tools(sort_by, limit)
        
        # 格式化工具信息
        formatted_tools = [format_tool_info(tool) for tool in tools]
        
        # 计算统计信息
        scores = [getattr(tool, sort_by) for tool in tools if getattr(tool, sort_by) is not None]
        statistics = {
            "total_tools": len(tools),
            "average_score": sum(scores) / len(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "tools_with_scores": len(scores)
        }
        
        result = {
            "success": True,
            "tools": formatted_tools,
            "sort_criteria": {
                "sort_by": sort_by,
                "limit": limit,
                "category": category
            },
            "statistics": statistics
        }
        
        logger.info(f"获取热门工具排行榜: {sort_by}, 数量: {limit}")
        return result
        
    except Exception as e:
        logger.error(f"获取热门工具排行榜失败: {e}")
        return {
            "success": False,
            "tools": [],
            "sort_criteria": {
                "sort_by": sort_by,
                "limit": limit,
                "category": category
            },
            "statistics": {},
            "error": str(e)
        }


@mcp.tool()
async def get_tool_categories() -> Dict[str, Any]:
    """获取工具分类统计信息
    
    获取所有工具分类及其统计信息，包括数量和平均评分。
    
    Returns:
        包含分类统计和汇总信息的字典
        
    Example:
        >>> get_tool_categories()
        {
            "success": True,
            "categories": [...],
            "summary": {
                "total_categories": 8,
                "total_tools": 1234,
                "average_score": 75.5
            }
        }
    """
    try:
        # 获取分类统计
        category_stats = await db_manager.get_category_stats()
        
        # 获取所有分类
        all_categories = await db_manager.get_all_categories()
        
        # 格式化分类信息
        formatted_categories = []
        total_tools = 0
        total_score = 0
        score_count = 0
        
        for stat in category_stats:
            formatted_category = {
                "category": stat.category,
                "tool_count": stat.tool_count,
                "average_scores": {
                    "tashan_score": stat.avg_tashan_score,
                    "utility_score": stat.avg_utility_score,
                    "sustainability_score": stat.avg_sustainability_score,
                    "popularity_score": stat.avg_popularity_score
                },
                "category_percentage": 0  # 稍后计算
            }
            formatted_categories.append(formatted_category)
            
            total_tools += stat.tool_count
            if stat.avg_tashan_score:
                total_score += stat.avg_tashan_score * stat.tool_count
                score_count += stat.tool_count
        
        # 计算百分比
        for category in formatted_categories:
            if total_tools > 0:
                category["category_percentage"] = (category["tool_count"] / total_tools) * 100
        
        # 计算汇总信息
        overall_average = total_score / score_count if score_count > 0 else 0
        
        summary = {
            "total_categories": len(formatted_categories),
            "total_tools": total_tools,
            "overall_average_score": round(overall_average, 2),
            "categories_with_tools": len([c for c in formatted_categories if c["tool_count"] > 0])
        }
        
        result = {
            "success": True,
            "categories": formatted_categories,
            "summary": summary
        }
        
        logger.info(f"获取分类统计: {summary['total_categories']} 个分类, {summary['total_tools']} 个工具")
        return result
        
    except Exception as e:
        logger.error(f"获取分类统计失败: {e}")
        return {
            "success": False,
            "categories": [],
            "summary": {
                "total_categories": 0,
                "total_tools": 0,
                "overall_average_score": 0
            },
            "error": str(e)
        }


@mcp.tool()
async def security_check() -> Dict[str, Any]:
    """安全状态检查
    
    检查系统的安全保护状态和配置安全。
    
    Returns:
        包含安全状态和配置信息的字典
    """
    try:
        # 获取安全状态
        security_status = get_security_status()
        
        # 检查配置安全
        config_secure = security_status.get('security_enabled', False)
        
        # 检查敏感信息
        secure_config = {}
        if config_secure:
            try:
                from .secure_config_manager import get_secure_supabase_config
                config = get_secure_supabase_config()
                secure_config = {
                    'supabase_url_length': len(config.get('supabase_url', '')),
                    'supabase_key_length': len(config.get('supabase_service_role_key', '')),
                    'config_complete': bool(config.get('supabase_url') and config.get('supabase_service_role_key'))
                }
            except Exception as e:
                secure_config = {'error': str(e)}
        
        result = {
            "success": True,
            "security_status": {
                "protection_enabled": config_secure,
                "access_count": security_status.get('access_count', 0),
                "max_accesses": security_status.get('max_accesses', 100),
                "cached_configs": len(security_status.get('cached_configs', []))
            },
            "config_security": secure_config,
            "recommendations": []
        }
        
        # 生成建议
        if not config_secure:
            result["recommendations"].append("建议启用安全保护以加密敏感配置")
        
        if secure_config.get('config_complete') is False:
            result["recommendations"].append("配置信息不完整，请检查数据库配置")
        
        logger.info(f"安全检查: 保护启用={config_secure}")
        return result
        
    except Exception as e:
        logger.error(f"安全检查失败: {e}")
        return {
            "success": False,
            "security_status": {},
            "config_security": {},
            "recommendations": ["安全检查失败"],
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
    logger.info("启动MCP工具评估助手服务器")
    
    # 启动服务器
    mcp.run()


if __name__ == "__main__":
    main()