"""MCP工具数据模型定义"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class MCPToolInfo(BaseModel):
    """MCP工具信息数据模型"""

    # 基础信息
    tool_id: Optional[str] = None
    name: str = Field(description="工具名称")
    author: str = Field(description="工具作者")
    description: str = Field(description="工具描述")
    category: str = Field(default="其他", description="工具分类")
    github_url: str = Field(description="GitHub地址")
    url: str = Field(description="项目URL")

    # 技术信息
    deployment_method: str = Field(description="部署方式")
    package_name: Optional[str] = Field(None, description="包名")
    requires_api_key: bool = Field(default=False, description="是否需要API密钥")

    # 他山评分信息
    tashan_score: Optional[float] = Field(None, ge=0, le=100, description="他山综合评分")
    utility_score: Optional[float] = Field(None, ge=0, le=100, description="实用性评分")
    sustainability_score: Optional[float] = Field(None, ge=0, le=100, description="可持续性评分")
    popularity_score: Optional[float] = Field(None, ge=0, le=100, description="受欢迎度评分")

    # LobeHub评分信息
    lobehub_evaluate: Optional[str] = Field(None, description="LobeHub评估等级")
    lobehub_score: Optional[float] = Field(None, ge=0, le=100, description="LobeHub评分")
    lobehub_stars: Optional[int] = Field(None, ge=0, description="GitHub星标数")
    lobehub_forks: Optional[int] = Field(None, ge=0, description="GitHub分支数")

    # 测试信息
    test_success_rate: Optional[float] = Field(None, ge=0, le=100, description="测试成功率")
    test_count: Optional[int] = Field(None, ge=0, description="测试次数")
    last_test_time: Optional[datetime] = Field(None, description="最后测试时间")

    # 时间戳
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    model_config = {
        "from_attributes": True
    }


class TestResult(BaseModel):
    """测试结果数据模型 - 基于 @mcp_agent 实际数据库结构"""

    test_id: Optional[str] = None
    test_timestamp: Optional[datetime] = None
    tool_identifier: Optional[str] = Field(None, description="工具标识符 (GitHub URL)")
    tool_name: Optional[str] = Field(None, description="工具名称")
    tool_author: Optional[str] = Field(None, description="工具作者")
    tool_category: Optional[str] = Field(None, description="工具分类")
    test_success: bool = Field(..., description="测试是否成功")
    deployment_success: bool = Field(..., description="部署是否成功")
    communication_success: bool = Field(..., description="通信是否成功")
    available_tools_count: Optional[int] = Field(None, ge=0, description="可用工具数量")
    test_duration_seconds: Optional[float] = Field(None, ge=0, description="测试耗时")
    error_messages: Optional[List[str]] = Field(None, description="错误消息列表")
    test_details: Optional[List[Dict[str, Any]]] = Field(None, description="测试详细信息")

    # 环境信息
    environment_info: Optional[Dict[str, Any]] = Field(None, description="环境信息")
    created_at: Optional[datetime] = Field(None, description="创建时间")

    # 评分信息
    final_score: Optional[int] = Field(None, ge=0, description="最终评分")
    sustainability_score: Optional[int] = Field(None, ge=0, description="可持续性评分")
    popularity_score: Optional[int] = Field(None, ge=0, description="受欢迎度评分")
    sustainability_details: Optional[Dict[str, Any]] = Field(None, description="可持续性详情")
    popularity_details: Optional[Dict[str, Any]] = Field(None, description="受欢迎度详情")
    evaluation_timestamp: Optional[datetime] = Field(None, description="评估时间戳")

    # LobeHub 信息
    lobehub_url: Optional[str] = Field(None, description="LobeHub URL")
    lobehub_evaluate: Optional[str] = Field(None, description="LobeHub 评估")
    lobehub_score: Optional[float] = Field(None, ge=0, le=100, description="LobeHub 评分")
    lobehub_star_count: Optional[int] = Field(None, ge=0, description="LobeHub 星标数")
    lobehub_fork_count: Optional[int] = Field(None, ge=0, description="LobeHub 分支数")

    # 综合评分
    comprehensive_score: Optional[int] = Field(None, ge=0, description="综合评分")
    calculation_method: Optional[str] = Field(None, description="计算方法")
    evaluation_details: Optional[Dict[str, Any]] = Field(None, description="评估详情")


class ToolSearchFilter(BaseModel):
    """工具搜索过滤器"""

    query: Optional[str] = Field(None, description="搜索关键词")
    category: Optional[str] = Field(None, description="工具分类")
    min_tashan_score: Optional[float] = Field(None, ge=0, le=100, description="最低他山评分")
    max_tashan_score: Optional[float] = Field(None, ge=0, le=100, description="最高他山评分")
    deployment_method: Optional[str] = Field(None, description="部署方式")
    author: Optional[str] = Field(None, description="作者")
    limit: int = Field(default=20, ge=1, le=100, description="返回结果数量限制")
    offset: int = Field(default=0, ge=0, description="偏移量")


class SearchResponse(BaseModel):
    """搜索响应模型"""

    success: bool = Field(..., description="是否成功")
    tools: List[MCPToolInfo] = Field(..., description="工具列表")
    total_count: int = Field(..., description="总数量")
    search_summary: str = Field(..., description="搜索摘要")
    filters: ToolSearchFilter = Field(..., description="使用的过滤器")
    error: Optional[str] = Field(None, description="错误信息")


class ToolEvaluation(BaseModel):
    """工具评估报告模型"""

    success: bool = Field(..., description="是否成功")
    tool_info: MCPToolInfo = Field(..., description="工具信息")
    evaluation: Dict[str, Any] = Field(..., description="评估结果")
    recommendations: List[str] = Field(..., description="使用建议")
    use_cases: List[str] = Field(..., description="适用场景")
    error: Optional[str] = Field(None, description="错误信息")


class CategoryStats(BaseModel):
    """分类统计模型"""

    category: str = Field(..., description="分类名称")
    tool_count: int = Field(..., description="工具数量")
    avg_tashan_score: Optional[float] = Field(None, description="平均他山评分")
    avg_utility_score: Optional[float] = Field(None, description="平均实用性评分")
    avg_sustainability_score: Optional[float] = Field(None, description="平均可持续性评分")
    avg_popularity_score: Optional[float] = Field(None, description="平均受欢迎度评分")