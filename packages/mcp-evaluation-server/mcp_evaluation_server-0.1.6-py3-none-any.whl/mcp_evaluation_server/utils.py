"""工具函数和辅助方法"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from .models import MCPToolInfo, ToolSearchFilter

logger = logging.getLogger(__name__)


def format_tool_info(tool: MCPToolInfo) -> Dict[str, Any]:
    """格式化工具信息用于输出"""
    return {
        "tool_id": tool.tool_id,
        "name": tool.name,
        "author": tool.author,
        "description": tool.description,
        "category": tool.category,
        "github_url": tool.github_url,
        "url": tool.url,
        "deployment_method": tool.deployment_method,
        "package_name": tool.package_name,
        "requires_api_key": tool.requires_api_key,
        "scores": {
            "tashan_score": tool.tashan_score,
            "utility_score": tool.utility_score,
            "sustainability_score": tool.sustainability_score,
            "popularity_score": tool.popularity_score,
            "lobehub_score": tool.lobehub_score,
            "lobehub_evaluate": tool.lobehub_evaluate,
        },
        "stats": {
            "test_success_rate": tool.test_success_rate,
            "test_count": tool.test_count,
            "last_test_time": tool.last_test_time.isoformat() if tool.last_test_time else None,
        },
        "lobehub_data": {
            "stars": tool.lobehub_stars,
            "forks": tool.lobehub_forks,
        }
    }


def generate_recommendations(tool: MCPToolInfo) -> List[str]:
    """生成工具使用建议"""
    recommendations = []
    
    # 基于他山评分的建议
    if tool.tashan_score and tool.tashan_score >= 80:
        recommendations.append("该工具评分优秀，推荐优先考虑使用")
    elif tool.tashan_score and tool.tashan_score >= 60:
        recommendations.append("该工具评分良好，适合大多数使用场景")
    elif tool.tashan_score:
        recommendations.append("该工具评分一般，建议在充分评估后使用")
    
    # 基于LobeHub评估的建议
    if tool.lobehub_evaluate == "优质":
        recommendations.append("LobeHub平台评定为优质工具，质量有保障")
    elif tool.lobehub_evaluate == "良好":
        recommendations.append("LobeHub平台评定为良好工具")
    elif tool.lobehub_evaluate == "欠佳":
        recommendations.append("LobeHub平台评定为欠佳，使用需谨慎")
    
    # 基于测试成功率的建议
    if tool.test_success_rate and tool.test_success_rate >= 90:
        recommendations.append("工具测试成功率高，稳定性良好")
    elif tool.test_success_rate and tool.test_success_rate < 70:
        recommendations.append("工具测试成功率较低，可能存在兼容性问题")
    
    # 基于活跃度的建议
    if tool.sustainability_score and tool.sustainability_score >= 80:
        recommendations.append("项目活跃度高，维护情况良好")
    elif tool.sustainability_score and tool.sustainability_score < 50:
        recommendations.append("项目活跃度较低，需谨慎评估长期可用性")
    
    return recommendations if recommendations else ["暂无具体建议，请根据实际需求评估"]


def generate_use_cases(tool: MCPToolInfo) -> List[str]:
    """生成工具适用场景"""
    use_cases = []
    
    # 基于分类生成适用场景
    category_mapping = {
        "开发工具推荐": ["软件开发", "代码生成", "开发辅助", "IDE集成"],
        "文档处理": ["文档生成", "内容管理", "知识库建设", "文档自动化"],
        "API集成": ["系统集成", "API调用", "数据同步", "第三方服务集成"],
        "交流协作": ["团队协作", "沟通工具", "项目管理", "工作流程优化"],
        "数据管理": ["数据分析", "数据处理", "数据存储", "数据可视化"],
        "AI/ML": ["机器学习", "人工智能", "数据处理", "模型训练"],
        "测试工具": ["自动化测试", "代码测试", "质量保证", "性能测试"],
        "监控运维": ["系统监控", "日志分析", "性能监控", "运维自动化"],
        "安全工具": ["安全扫描", "漏洞检测", "安全监控", "权限管理"],
    }
    
    if tool.category in category_mapping:
        use_cases.extend(category_mapping[tool.category])
    else:
        use_cases.append("通用场景")
    
    # 基于描述的关键词添加更多场景
    description_lower = tool.description.lower()
    
    if any(keyword in description_lower for keyword in ["github", "git", "代码管理"]):
        use_cases.extend(["代码管理", "版本控制", "协作开发"])
    
    if any(keyword in description_lower for keyword in ["api", "接口", "集成"]):
        use_cases.extend(["API集成", "系统对接", "数据交换"])
    
    if any(keyword in description_lower for keyword in ["文档", "document", "知识"]):
        use_cases.extend(["文档处理", "知识管理", "内容创作"])
    
    if any(keyword in description_lower for keyword in ["搜索", "search", "查询"]):
        use_cases.extend(["信息检索", "数据查询", "搜索优化"])
    
    # 去重并限制数量
    use_cases = list(set(use_cases))[:8]
    
    return use_cases if use_cases else ["请根据工具描述确定适用场景"]


def format_search_summary(filters: ToolSearchFilter, total_count: int, result_count: int) -> str:
    """格式化搜索摘要"""
    parts = [f"找到 {result_count} 个工具"]
    
    if total_count > result_count:
        parts.append(f"(共 {total_count} 个)")
    
    conditions = []
    if filters.query:
        conditions.append(f"关键词 '{filters.query}'")
    if filters.category:
        conditions.append(f"分类 '{filters.category}'")
    if filters.min_tashan_score is not None:
        conditions.append(f"评分 >= {filters.min_tashan_score}")
    if filters.max_tashan_score is not None:
        conditions.append(f"评分 <= {filters.max_tashan_score}")
    if filters.deployment_method:
        conditions.append(f"部署方式 '{filters.deployment_method}'")
    if filters.author:
        conditions.append(f"作者 '{filters.author}'")
    
    if conditions:
        parts.append(f"基于条件: {', '.join(conditions)}")
    
    return " ".join(parts) + "."


def safe_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    """安全转换为浮点数"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    """安全转换为整数"""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def format_timestamp(timestamp: Any) -> str:
    """格式化时间戳"""
    if timestamp is None:
        return ""
    
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return str(timestamp)
    
    if isinstance(timestamp, datetime):
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    return str(timestamp)


def validate_sort_field(sort_by: str) -> str:
    """验证排序字段"""
    valid_fields = {
        "tashan_score", "utility_score", "sustainability_score", 
        "popularity_score", "lobehub_score", "test_success_rate",
        "created_at", "updated_at", "name", "author"
    }
    
    return sort_by if sort_by in valid_fields else "tashan_score"


def log_search_query(filters: ToolSearchFilter) -> None:
    """记录搜索查询日志"""
    query_info = {
        "timestamp": datetime.now().isoformat(),
        "query": filters.query,
        "category": filters.category,
        "min_score": filters.min_tashan_score,
        "max_score": filters.max_tashan_score,
        "deployment_method": filters.deployment_method,
        "author": filters.author,
        "limit": filters.limit,
        "offset": filters.offset
    }
    
    logger.info(f"搜索查询: {json.dumps(query_info, ensure_ascii=False)}")


def calculate_comprehensive_score(tool: MCPToolInfo) -> Optional[float]:
    """计算综合评分"""
    if tool.tashan_score is not None:
        return tool.tashan_score
    
    # 如果没有他山评分，基于其他评分计算
    scores = []
    if tool.utility_score is not None:
        scores.append(tool.utility_score)
    if tool.sustainability_score is not None:
        scores.append(tool.sustainability_score)
    if tool.popularity_score is not None:
        scores.append(tool.popularity_score)
    
    if scores:
        return sum(scores) / len(scores)
    
    return None