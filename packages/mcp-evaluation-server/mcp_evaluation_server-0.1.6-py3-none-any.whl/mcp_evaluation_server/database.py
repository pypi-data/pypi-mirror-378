"""Supabase数据库管理器"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from .config import get_settings
from .models import (
    MCPToolInfo, 
    TestResult, 
    ToolSearchFilter, 
    CategoryStats
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Supabase数据库管理器"""

    def __init__(self):
        """初始化数据库连接"""
        settings = get_settings()
        self.client: Client = self._create_client()
        self.tools_table = settings.mcp_tools_table
        self.test_results_table = settings.mcp_test_results_table

    def _create_client(self) -> Client:
        """创建Supabase客户端"""
        try:
            settings = get_settings()
            client = create_client(settings.supabase_url, settings.supabase_service_role_key)
            logger.info("Supabase客户端连接成功")
            return client
        except Exception as e:
            logger.error(f"Supabase客户端连接失败: {e}")
            raise

    def _parse_datetime(self, datetime_str: Optional[str]) -> Optional[datetime]:
        """解析日期时间字符串"""
        if not datetime_str:
            return None
        try:
            # 尝试解析 ISO 格式
            if isinstance(datetime_str, str):
                return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return datetime_str
        except Exception:
            return None

    async def search_tools(self, filters: ToolSearchFilter) -> List[MCPToolInfo]:
        """搜索MCP工具 - 基于 test_results 表"""
        try:
            # 从 test_results 表中提取唯一的工具信息
            query = self.client.table(self.test_results_table).select("*")
            
            # 添加过滤条件
            if filters.query:
                query = query.or_(f"tool_name.ilike.%{filters.query}%,tool_identifier.ilike.%{filters.query}%")
            
            if filters.author:
                query = query.eq("tool_author", filters.author)
            
            # 添加排序和分页
            query = (
                query
                .order("comprehensive_score", desc=True)
                .order("test_timestamp", desc=True)
                .range(filters.offset, filters.offset + filters.limit - 1)
            )
            
            # 执行查询
            result = query.execute()
            
            if result.data:
                # 转换为 MCPToolInfo 对象
                tools = []
                seen_tools = set()  # 去重
                
                for item in result.data:
                    tool_key = item.get("tool_identifier", item.get("tool_name", ""))
                    if tool_key and tool_key not in seen_tools:
                        seen_tools.add(tool_key)
                        
                        # 从测试结果构建工具信息
                        tool_info = MCPToolInfo(
                            tool_id=item.get("test_id"),
                            name=item.get("tool_name", "未知工具"),
                            author=item.get("tool_author", "未知作者"),
                            description=f"来自 {item.get('tool_identifier', '未知来源')} 的MCP工具",
                            category=item.get("tool_category", "其他"),
                            github_url=item.get("tool_identifier", ""),
                            url=item.get("tool_identifier", ""),
                            deployment_method="未知",  # 从测试结果中无法确定
                            tashan_score=float(item.get("final_score", 0)) if item.get("final_score") else None,
                            sustainability_score=float(item.get("sustainability_score", 0)) if item.get("sustainability_score") else None,
                            popularity_score=float(item.get("popularity_score", 0)) if item.get("popularity_score") else None,
                            lobehub_evaluate=item.get("lobehub_evaluate"),
                            lobehub_score=item.get("lobehub_score"),
                            lobehub_stars=item.get("lobehub_star_count"),
                            lobehub_forks=item.get("lobehub_fork_count"),
                            test_success_rate=100.0 if item.get("test_success") else 0.0,
                            test_count=1,
                            last_test_time=self._parse_datetime(item.get("test_timestamp")),
                            created_at=self._parse_datetime(item.get("created_at")),
                            updated_at=self._parse_datetime(item.get("test_timestamp"))
                        )
                        tools.append(tool_info)
                
                return tools
            return []
            
        except Exception as e:
            logger.error(f"搜索工具失败: {e}")
            raise

    async def get_tool_by_name(self, name: str) -> Optional[MCPToolInfo]:
        """根据名称获取工具"""
        try:
            result = (
                self.client.table(self.test_results_table)
                .select("*")
                .eq("tool_name", name)
                .order("test_timestamp", desc=True)
                .limit(1)
                .execute()
            )
            
            if result.data and len(result.data) > 0:
                item = result.data[0]
                return MCPToolInfo(
                    tool_id=item.get("test_id"),
                    name=item.get("tool_name", "未知工具"),
                    author=item.get("tool_author", "未知作者"),
                    description=f"来自 {item.get('tool_identifier', '未知来源')} 的MCP工具",
                    category=item.get("tool_category", "其他"),
                    github_url=item.get("tool_identifier", ""),
                    url=item.get("tool_identifier", ""),
                    deployment_method="未知",
                    tashan_score=float(item.get("final_score", 0)) if item.get("final_score") else None,
                    sustainability_score=float(item.get("sustainability_score", 0)) if item.get("sustainability_score") else None,
                    popularity_score=float(item.get("popularity_score", 0)) if item.get("popularity_score") else None,
                    lobehub_evaluate=item.get("lobehub_evaluate"),
                    lobehub_score=item.get("lobehub_score"),
                    lobehub_stars=item.get("lobehub_star_count"),
                    lobehub_forks=item.get("lobehub_fork_count"),
                    test_success_rate=100.0 if item.get("test_success") else 0.0,
                    test_count=1,
                    last_test_time=self._parse_datetime(item.get("test_timestamp")),
                    created_at=self._parse_datetime(item.get("created_at")),
                    updated_at=self._parse_datetime(item.get("test_timestamp"))
                )
            return None
            
        except Exception as e:
            logger.error(f"获取工具失败: {e}")
            return None

    async def get_tool_by_id(self, tool_id: str) -> Optional[MCPToolInfo]:
        """根据ID获取工具"""
        try:
            result = (
                self.client.table(self.tools_table)
                .select("*")
                .eq("tool_id", tool_id)
                .single()
                .execute()
            )
            
            if result.data:
                return MCPToolInfo(**result.data)
            return None
            
        except Exception as e:
            logger.error(f"获取工具失败: {e}")
            return None

    async def get_top_tools(
        self, 
        sort_by: str = "tashan_score", 
        limit: int = 10
    ) -> List[MCPToolInfo]:
        """获取热门工具排行榜"""
        try:
            # 验证排序字段
            valid_sort_fields = {
                "final_score", "sustainability_score", "popularity_score", 
                "comprehensive_score", "lobehub_score", "test_timestamp"
            }
            
            if sort_by not in valid_sort_fields:
                sort_by = "comprehensive_score"
            
            # 从测试结果中获取唯一的工具并排序
            result = (
                self.client.table(self.test_results_table)
                .select("*")
                .order(sort_by, desc=True)
                .limit(limit * 2)  # 获取更多结果以去重
                .execute()
            )
            
            if result.data:
                tools = []
                seen_tools = set()  # 去重
                
                for item in result.data:
                    tool_key = item.get("tool_identifier", item.get("tool_name", ""))
                    if tool_key and tool_key not in seen_tools:
                        seen_tools.add(tool_key)
                        
                        # 从测试结果构建工具信息
                        tool_info = MCPToolInfo(
                            tool_id=item.get("test_id"),
                            name=item.get("tool_name", "未知工具"),
                            author=item.get("tool_author", "未知作者"),
                            description=f"来自 {item.get('tool_identifier', '未知来源')} 的MCP工具",
                            category=item.get("tool_category", "其他"),
                            github_url=item.get("tool_identifier", ""),
                            url=item.get("tool_identifier", ""),
                            deployment_method="未知",
                            tashan_score=float(item.get("final_score", 0)) if item.get("final_score") else None,
                            sustainability_score=float(item.get("sustainability_score", 0)) if item.get("sustainability_score") else None,
                            popularity_score=float(item.get("popularity_score", 0)) if item.get("popularity_score") else None,
                            lobehub_evaluate=item.get("lobehub_evaluate"),
                            lobehub_score=item.get("lobehub_score"),
                            lobehub_stars=item.get("lobehub_star_count"),
                            lobehub_forks=item.get("lobehub_fork_count"),
                            test_success_rate=100.0 if item.get("test_success") else 0.0,
                            test_count=1,
                            last_test_time=self._parse_datetime(item.get("test_timestamp")),
                            created_at=self._parse_datetime(item.get("created_at")),
                            updated_at=self._parse_datetime(item.get("test_timestamp"))
                        )
                        tools.append(tool_info)
                        
                        if len(tools) >= limit:
                            break
                
                return tools
            return []
            
        except Exception as e:
            logger.error(f"获取热门工具失败: {e}")
            raise

    async def get_category_stats(self) -> List[CategoryStats]:
        """获取分类统计信息"""
        try:
            # 直接使用基础查询，因为mcp_tools表不存在
            return await self._get_category_stats_fallback()
            
        except Exception as e:
            logger.error(f"获取分类统计失败: {e}")
            return []

    async def _get_category_stats_fallback(self) -> List[CategoryStats]:
        """分类统计的备用实现"""
        try:
            # 获取所有测试结果中的工具分类信息
            result = (
                self.client.table(self.test_results_table)
                .select("*")
                .execute()
            )
            
            if not result.data:
                return []
            
            # 手动计算统计信息
            category_data = {}
            for test_data in result.data:
                category = test_data.get("tool_category", "其他")
                if category not in category_data:
                    category_data[category] = {
                        "tools": set(),
                        "tashan_scores": [],
                        "utility_scores": [],
                        "sustainability_scores": [],
                        "popularity_scores": []
                    }
                
                # 使用工具标识符作为唯一标识
                tool_identifier = test_data.get("tool_identifier", "")
                category_data[category]["tools"].add(tool_identifier)
                
                # 收集评分数据
                if test_data.get("final_score") is not None:
                    category_data[category]["tashan_scores"].append(test_data["final_score"])
                if test_data.get("sustainability_score") is not None:
                    category_data[category]["sustainability_scores"].append(test_data["sustainability_score"])
                if test_data.get("popularity_score") is not None:
                    category_data[category]["popularity_scores"].append(test_data["popularity_score"])
            
            # 构建统计结果
            stats = []
            for category, data in category_data.items():
                stats.append(CategoryStats(
                    category=category,
                    tool_count=len(data["tools"]),
                    avg_tashan_score=self._safe_avg(data["tashan_scores"]),
                    avg_utility_score=self._safe_avg(data["utility_scores"]),
                    avg_sustainability_score=self._safe_avg(data["sustainability_scores"]),
                    avg_popularity_score=self._safe_avg(data["popularity_scores"])
                ))
            
            # 按工具数量排序
            stats.sort(key=lambda x: x.tool_count, reverse=True)
            return stats
            
        except Exception as e:
            logger.error(f"分类统计备用实现失败: {e}")
            return []

    def _safe_avg(self, values: List[float]) -> Optional[float]:
        """安全计算平均值"""
        if not values:
            return None
        return sum(values) / len(values)

    async def get_tool_test_results(self, tool_identifier: str, limit: int = 10) -> List[TestResult]:
        """获取工具的测试结果"""
        try:
            result = (
                self.client.table(self.test_results_table)
                .select("*")
                .eq("tool_identifier", tool_identifier)
                .order("test_timestamp", desc=True)
                .limit(limit)
                .execute()
            )
            
            if result.data:
                return [TestResult(**item) for item in result.data]
            return []
            
        except Exception as e:
            logger.error(f"获取测试结果失败: {e}")
            return []

    async def get_total_tools_count(self) -> int:
        """获取工具总数"""
        try:
            # 获取唯一的工具数量
            result = (
                self.client.table(self.test_results_table)
                .select("tool_identifier")
                .execute()
            )
            
            if result.data:
                unique_tools = set()
                for item in result.data:
                    if item.get("tool_identifier"):
                        unique_tools.add(item["tool_identifier"])
                return len(unique_tools)
            return 0
            
        except Exception as e:
            logger.error(f"获取工具总数失败: {e}")
            return 0

    async def get_all_categories(self) -> List[str]:
        """获取所有分类"""
        try:
            result = (
                self.client.table(self.test_results_table)
                .select("tool_category")
                .execute()
            )
            
            if result.data:
                categories = set()
                for item in result.data:
                    if item.get("tool_category"):
                        categories.add(item["tool_category"])
                return sorted(list(categories))
            return []
            
        except Exception as e:
            logger.error(f"获取分类列表失败: {e}")
            return []

    async def health_check(self) -> bool:
        """数据库健康检查"""
        try:
            # 简单查询测试连接
            result = (
                self.client.table(self.test_results_table)
                .select("count", count="exact")
                .limit(1)
                .execute()
            )
            return True
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return False

    async def get_recent_test_results(self, limit: int = 10) -> List[TestResult]:
        """获取最近的测试结果"""
        try:
            result = (
                self.client.table(self.test_results_table)
                .select("*")
                .order("test_timestamp", desc=True)
                .limit(limit)
                .execute()
            )
            
            if result.data:
                return [TestResult(**item) for item in result.data]
            return []
            
        except Exception as e:
            logger.error(f"获取最近测试结果失败: {e}")
            return []

    async def get_total_test_results_count(self) -> int:
        """获取测试结果总数"""
        try:
            result = (
                self.client.table(self.test_results_table)
                .select("count", count="exact")
                .execute()
            )
            return result.count if hasattr(result, 'count') else 0
            
        except Exception as e:
            logger.error(f"获取测试结果总数失败: {e}")
            return 0