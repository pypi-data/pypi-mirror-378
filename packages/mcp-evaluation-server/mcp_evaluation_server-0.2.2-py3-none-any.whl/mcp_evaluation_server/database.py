"""Supabase数据库管理器"""

import logging
from typing import List, Optional, Dict, Any, Union
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
        self.client: Optional[Client] = self._create_client()
        self.tools_table = settings.mcp_tools_table
        self.test_results_table = settings.mcp_test_results_table

    def _create_client(self) -> Optional[Client]:
        """创建Supabase客户端"""
        try:
            settings = get_settings()
            if not settings.supabase_url or not settings.supabase_service_role_key:
                logger.warning("Supabase配置未提供，将使用离线模式")
                return None
            
            client = create_client(settings.supabase_url, settings.supabase_service_role_key)
            logger.info("Supabase客户端连接成功")
            return client
        except Exception as e:
            logger.warning(f"Supabase客户端连接失败，将使用离线模式: {e}")
            return None

    def _parse_datetime(self, datetime_str: Optional[str]) -> Optional[datetime]:
        """解析日期时间字符串"""
        if not datetime_str:
            return None
        try:
            # 如果已经是datetime对象，确保时区处理
            if isinstance(datetime_str, datetime):
                # 如果是naive datetime，添加时区信息
                if datetime_str.tzinfo is None:
                    return datetime_str.replace(tzinfo=None)  # 保持naive以兼容现有代码
                return datetime_str
            
            # 如果是字符串，尝试解析
            if isinstance(datetime_str, str):
                # 处理ISO格式字符串
                cleaned = datetime_str.replace('Z', '+00:00')
                try:
                    dt = datetime.fromisoformat(cleaned)
                    # 如果解析后的datetime有时区，转换为naive以兼容现有代码
                    if dt.tzinfo is not None:
                        dt = dt.replace(tzinfo=None)
                    return dt
                except ValueError:
                    # 尝试其他格式
                    try:
                        from dateutil import parser
                        dt = parser.parse(datetime_str)
                        if dt.tzinfo is not None:
                            dt = dt.replace(tzinfo=None)
                        return dt
                    except ImportError:
                        # 如果没有dateutil，尝试简单格式
                        formats = [
                            '%Y-%m-%d %H:%M:%S',
                            '%Y-%m-%d %H:%M:%S.%f',
                            '%Y-%m-%dT%H:%M:%S',
                            '%Y-%m-%dT%H:%M:%S.%f'
                        ]
                        for fmt in formats:
                            try:
                                return datetime.strptime(datetime_str, fmt)
                            except ValueError:
                                continue
            return None
        except Exception:
            return None

    def _validate_timestamps(self, tool_info: 'MCPToolInfo') -> 'MCPToolInfo':
        """验证和修复时间戳数据"""
        if not tool_info:
            return tool_info
        
        current_time = datetime.now()
        
        # 验证创建时间
        if tool_info.created_at and tool_info.created_at > current_time:
            logger.warning(f"创建时间异常: {tool_info.created_at} > {current_time}, 工具: {tool_info.name}")
            tool_info.created_at = current_time
        
        # 验证更新时间
        if tool_info.updated_at and tool_info.updated_at > current_time:
            logger.warning(f"更新时间异常: {tool_info.updated_at} > {current_time}, 工具: {tool_info.name}")
            tool_info.updated_at = current_time
        
        # 验证最后测试时间
        if tool_info.last_test_time and tool_info.last_test_time > current_time:
            logger.warning(f"最后测试时间异常: {tool_info.last_test_time} > {current_time}, 工具: {tool_info.name}")
            tool_info.last_test_time = current_time
        
        # 确保时间逻辑合理：创建时间 <= 更新时间
        if (tool_info.created_at and tool_info.updated_at and 
            tool_info.created_at > tool_info.updated_at):
            logger.warning(f"创建时间晚于更新时间: {tool_info.created_at} > {tool_info.updated_at}, 工具: {tool_info.name}")
            tool_info.created_at = tool_info.updated_at
        
        # 确保最后测试时间 <= 更新时间
        if (tool_info.last_test_time and tool_info.updated_at and 
            tool_info.last_test_time > tool_info.updated_at):
            logger.warning(f"最后测试时间晚于更新时间: {tool_info.last_test_time} > {tool_info.updated_at}, 工具: {tool_info.name}")
            tool_info.last_test_time = tool_info.updated_at
        
        return tool_info

    def _validate_tool_info(self, tool_info: 'MCPToolInfo') -> 'MCPToolInfo':
        """验证工具信息的完整性和合理性"""
        if not tool_info:
            return tool_info
        
        # 验证必填字段
        if not tool_info.name or not tool_info.name.strip():
            logger.warning("工具名称为空，设置默认名称")
            tool_info.name = "未知工具"
        
        if not tool_info.author or not tool_info.author.strip():
            logger.warning("工具作者为空，设置默认作者")
            tool_info.author = "未知作者"
        
        # 验证URL格式
        if tool_info.github_url and not tool_info.github_url.startswith(('http://', 'https://')):
            logger.warning(f"GitHub URL格式异常: {tool_info.github_url}")
            if not tool_info.github_url.startswith('github.com'):
                tool_info.github_url = f"https://github.com/{tool_info.github_url.lstrip('/')}"
            else:
                tool_info.github_url = f"https://{tool_info.github_url.lstrip('/')}"
        
        if tool_info.url and not tool_info.url.startswith(('http://', 'https://')):
            logger.warning(f"项目URL格式异常: {tool_info.url}")
            tool_info.url = f"https://{tool_info.url.lstrip('/')}"
        
        # 验证评分范围
        for score_field in ['tashan_score', 'utility_score', 'sustainability_score', 'popularity_score', 'lobehub_score']:
            score_value = getattr(tool_info, score_field, None)
            if score_value is not None:
                if not (0 <= score_value <= 100):
                    logger.warning(f"{score_field} 超出范围: {score_value}, 限制为0-100")
                    setattr(tool_info, score_field, max(0.0, min(100.0, float(score_value))))
        
        # 验证整数字段
        for int_field in ['lobehub_stars', 'lobehub_forks', 'test_count']:
            int_value = getattr(tool_info, int_field, None)
            if int_value is not None:
                if int_value < 0:
                    logger.warning(f"{int_field} 为负数: {int_value}, 设置为0")
                    setattr(tool_info, int_field, 0)
        
        # 验证成功率
        if tool_info.test_success_rate is not None:
            if not (0 <= tool_info.test_success_rate <= 100):
                logger.warning(f"测试成功率超出范围: {tool_info.test_success_rate}, 限制为0-100")
                tool_info.test_success_rate = max(0.0, min(100.0, float(tool_info.test_success_rate)))
        
        # 验证分类
        if not tool_info.category or not tool_info.category.strip():
            logger.warning("工具分类为空，设置为'其他'")
            tool_info.category = "其他"
        
        return tool_info

    def _validate_search_filters(self, filters: ToolSearchFilter) -> ToolSearchFilter:
        """验证搜索过滤器的有效性"""
        if not filters:
            return filters
        
        # 验证分页参数
        if filters.limit < 1:
            logger.warning(f"limit值过小: {filters.limit}, 设置为1")
            filters.limit = 1
        elif filters.limit > 100:
            logger.warning(f"limit值过大: {filters.limit}, 设置为100")
            filters.limit = 100
        
        if filters.offset < 0:
            logger.warning(f"offset值为负: {filters.offset}, 设置为0")
            filters.offset = 0
        
        # 验证评分范围
        if filters.min_tashan_score is not None:
            if filters.min_tashan_score < 0:
                logger.warning(f"最低评分过小: {filters.min_tashan_score}, 设置为0")
                filters.min_tashan_score = 0
            elif filters.min_tashan_score > 100:
                logger.warning(f"最低评分过大: {filters.min_tashan_score}, 设置为100")
                filters.min_tashan_score = 100
        
        if filters.max_tashan_score is not None:
            if filters.max_tashan_score < 0:
                logger.warning(f"最高评分过小: {filters.max_tashan_score}, 设置为0")
                filters.max_tashan_score = 0
            elif filters.max_tashan_score > 100:
                logger.warning(f"最高评分过大: {filters.max_tashan_score}, 设置为100")
                filters.max_tashan_score = 100
        
        # 验证评分范围逻辑
        if (filters.min_tashan_score is not None and filters.max_tashan_score is not None and
            filters.min_tashan_score > filters.max_tashan_score):
            logger.warning(f"评分范围异常: min({filters.min_tashan_score}) > max({filters.max_tashan_score}), 交换值")
            filters.min_tashan_score, filters.max_tashan_score = filters.max_tashan_score, filters.min_tashan_score
        
        return filters

    def _safe_execute_query(self, query_func, *args, **kwargs):
        """安全执行数据库查询，包含错误处理和重试机制"""
        max_retries = 3
        retry_delay = 1.0  # seconds
        
        for attempt in range(max_retries):
            try:
                return query_func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"查询执行失败，已达最大重试次数: {e}")
                    raise
                
                logger.warning(f"查询执行失败，第{attempt + 1}次重试: {e}")
                import time
                time.sleep(retry_delay * (2 ** attempt))  # 指数退避
        
        return None

    def _validate_test_result(self, test_result: 'TestResult') -> 'TestResult':
        """验证测试结果的完整性和合理性"""
        if not test_result:
            return test_result
        
        # 验证必填字段
        if not test_result.tool_name or not test_result.tool_name.strip():
            logger.warning("测试结果中工具名称为空")
            test_result.tool_name = "未知工具"
        
        # 验证布尔字段
        for bool_field in ['test_success', 'deployment_success', 'communication_success']:
            bool_value = getattr(test_result, bool_field, None)
            if bool_value is not None:
                setattr(test_result, bool_field, bool(bool_value))
        
        # 验证数值字段
        if test_result.available_tools_count is not None:
            if test_result.available_tools_count < 0:
                logger.warning(f"可用工具数量为负: {test_result.available_tools_count}, 设置为0")
                test_result.available_tools_count = 0
        
        if test_result.test_duration_seconds is not None:
            if test_result.test_duration_seconds < 0:
                logger.warning(f"测试持续时间为负: {test_result.test_duration_seconds}, 设置为0")
                test_result.test_duration_seconds = 0
            elif test_result.test_duration_seconds > 86400:  # 超过24小时
                logger.warning(f"测试持续时间过长: {test_result.test_duration_seconds}秒")
        
        # 验证评分范围
        for score_field in ['final_score', 'sustainability_score', 'popularity_score', 'lobehub_score']:
            score_value = getattr(test_result, score_field, None)
            if score_value is not None:
                if not (0 <= score_value <= 100):
                    logger.warning(f"{score_field} 超出范围: {score_value}, 限制为0-100")
                    setattr(test_result, score_field, max(0, min(100, int(score_value))))
        
        # 验证整数字段
        for int_field in ['lobehub_star_count', 'lobehub_fork_count']:
            int_value = getattr(test_result, int_field, None)
            if int_value is not None:
                if int_value < 0:
                    logger.warning(f"{int_field} 为负数: {int_value}, 设置为0")
                    setattr(test_result, int_field, 0)
        
        return test_result

    def _parse_score(self, score_value: Any, score_type: str = "score") -> Optional[float]:
        """安全解析评分值为浮点数"""
        if score_value is None:
            return None
        
        try:
            # 如果已经是浮点数，直接返回
            if isinstance(score_value, float):
                return max(0.0, min(100.0, score_value))  # 确保在0-100范围内
            
            # 如果是整数，转换为浮点数
            if isinstance(score_value, int):
                return float(max(0, min(100, score_value)))
            
            # 如果是字符串，尝试解析
            if isinstance(score_value, str):
                # 移除可能的百分号等字符
                cleaned = str(score_value).replace('%', '').strip()
                return float(max(0.0, min(100.0, float(cleaned))))
            
            # 其他类型，尝试转换
            return float(max(0.0, min(100.0, float(score_value))))
            
        except (ValueError, TypeError) as e:
            logger.warning(f"评分解析失败 - {score_type}: {score_value}, 错误: {e}")
            return None

    def _parse_integer(self, int_value: Any, field_name: str = "field") -> Optional[int]:
        """安全解析整数值"""
        if int_value is None:
            return None
        
        try:
            if isinstance(int_value, int):
                return max(0, int_value)  # 确保非负
            
            if isinstance(int_value, str):
                cleaned = str(int_value).strip()
                return max(0, int(float(cleaned)))  # 处理如 "85.0" 的字符串
            
            return max(0, int(float(int_value)))
            
        except (ValueError, TypeError) as e:
            logger.warning(f"整数值解析失败 - {field_name}: {int_value}, 错误: {e}")
            return None

    async def _calculate_test_statistics(self, tool_identifier: str) -> Dict[str, Any]:
        """计算工具的真实测试统计数据"""
        if not self.client:
            return {"test_count": 0, "test_success_rate": 0.0, "last_test_time": None}
        
        try:
            # 查询该工具的所有测试记录
            result = (
                self.client.table(self.test_results_table)
                .select("test_success, test_timestamp, test_duration_seconds")
                .eq("tool_identifier", tool_identifier)
                .order("test_timestamp", desc=True)
                .execute()
            )
            
            if not result.data:
                return {"test_count": 0, "test_success_rate": 0.0, "last_test_time": None}
            
            test_records = result.data
            total_tests = len(test_records)
            successful_tests = sum(1 for record in test_records if record.get("test_success", False))
            
            # 计算成功率
            success_rate = (successful_tests / total_tests * 100.0) if total_tests > 0 else 0.0
            
            # 获取最后测试时间
            last_test_time = None
            if test_records and test_records[0].get("test_timestamp"):
                last_test_time = self._parse_datetime(test_records[0].get("test_timestamp"))
            
            # 计算平均测试时长
            durations = [record.get("test_duration_seconds") for record in test_records 
                        if record.get("test_duration_seconds") is not None]
            avg_duration = sum(durations) / len(durations) if durations else None
            
            return {
                "test_count": total_tests,
                "test_success_rate": round(success_rate, 2),
                "last_test_time": last_test_time,
                "avg_test_duration": avg_duration,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests
            }
            
        except Exception as e:
            logger.warning(f"计算测试统计数据失败 - {tool_identifier}: {e}")
            return {"test_count": 0, "test_success_rate": 0.0, "last_test_time": None}

    async def search_tools(self, filters: ToolSearchFilter) -> List[MCPToolInfo]:
        """搜索MCP工具 - 智能关联查询机制"""
        if not self.client:
            logger.warning("数据库未连接，返回空结果")
            return []
            
        try:
            # 验证搜索过滤器
            validated_filters = self._validate_search_filters(filters)
            
            # 尝试智能关联查询
            tools = await self._safe_execute_query(
                self._search_tools_with_association, validated_filters
            )
            
            # 如果关联查询无结果，则回退到基础查询
            if not tools:
                tools = await self._safe_execute_query(
                    self._search_tools_from_main_table, validated_filters
                )
                
            # 如果仍然无结果，使用test_results表
            if not tools:
                tools = await self._safe_execute_query(
                    self._search_tools_from_test_results, validated_filters
                )
            
            # 对结果进行最终验证
            validated_tools = []
            for tool in tools:
                validated_tool = self._validate_tool_info(tool)
                validated_tools.append(validated_tool)
            
            return validated_tools
            
        except Exception as e:
            logger.error(f"搜索工具失败: {e}")
            raise

    async def _search_tools_with_association(self, filters: ToolSearchFilter) -> List[MCPToolInfo]:
        """智能关联查询 - 结合 tools_table 和 test_results 表的优势"""
        try:
            # 首先从 tools_table 获取基础信息
            main_query = self.client.table(self.tools_table).select("*")
            
            # 应用过滤条件
            if filters.query:
                main_query = main_query.or_(f"name.ilike.%{filters.query}%,description.ilike.%{filters.query}%,author.ilike.%{filters.query}%")
            
            if filters.category:
                main_query = main_query.eq("category", filters.category)
            
            if filters.author:
                main_query = main_query.eq("author", filters.author)
            
            if filters.deployment_method:
                main_query = main_query.eq("deployment_method", filters.deployment_method)
            
            # 评分范围过滤
            if filters.min_tashan_score is not None:
                main_query = main_query.gte("tashan_score", filters.min_tashan_score)
            
            if filters.max_tashan_score is not None:
                main_query = main_query.lte("tashan_score", filters.max_tashan_score)
            
            # 执行主查询
            main_result = main_query.execute()
            
            if not main_result.data:
                return []
            
            tools = []
            for item in main_result.data:
                try:
                    # 获取工具的测试统计信息
                    tool_name = item.get("name")
                    test_stats = await self._get_enhanced_test_stats(tool_name)
                    
                    # 合并基础信息和测试统计
                    tool_info = MCPToolInfo(
                        tool_id=item.get("tool_id"),
                        name=item.get("name", "未知工具"),
                        author=item.get("author", "未知作者"),
                        description=item.get("description", "暂无描述"),
                        category=item.get("category", "其他"),
                        github_url=item.get("github_url", ""),
                        url=item.get("url", ""),
                        deployment_method=item.get("deployment_method", "未知"),
                        package_name=item.get("package_name"),
                        requires_api_key=item.get("requires_api_key", False),
                        
                        # 使用 tools_table 的评分，如果没有则使用测试评分
                        tashan_score=self._parse_score(item.get("tashan_score"), "tashan_score") or 
                                    test_stats.get("avg_final_score"),
                        utility_score=self._parse_score(item.get("utility_score"), "utility_score"),
                        sustainability_score=self._parse_score(item.get("sustainability_score"), "sustainability_score") or 
                                          test_stats.get("avg_sustainability_score"),
                        popularity_score=self._parse_score(item.get("popularity_score"), "popularity_score") or 
                                         test_stats.get("avg_popularity_score"),
                        
                        lobehub_evaluate=item.get("lobehub_evaluate"),
                        lobehub_score=self._parse_score(item.get("lobehub_score"), "lobehub_score"),
                        lobehub_stars=self._parse_integer(item.get("lobehub_stars"), "lobehub_stars"),
                        lobehub_forks=self._parse_integer(item.get("lobehub_forks"), "lobehub_forks"),
                        
                        # 使用真实的测试统计
                        test_success_rate=test_stats.get("success_rate", 0.0),
                        test_count=test_stats.get("total_tests", 0),
                        last_test_time=test_stats.get("last_test_time"),
                        
                        created_at=self._parse_datetime(item.get("created_at")),
                        updated_at=self._parse_datetime(item.get("updated_at"))
                    )
                    
                    # 验证和修复时间戳数据
                    tool_info = self._validate_timestamps(tool_info)
                    
                    tools.append(tool_info)
                    
                except Exception as e:
                    logger.warning(f"处理关联工具信息失败: {item.get('name', 'unknown')}, 错误: {e}")
                    continue
            
            # 应用排序和分页
            tools = self._apply_sorting_and_pagination(tools, filters)
            
            return tools
            
        except Exception as e:
            logger.warning(f"关联查询失败: {e}")
            return []

    async def _get_enhanced_test_stats(self, tool_name: str) -> Dict[str, Any]:
        """获取增强的测试统计信息"""
        if not self.client:
            return {
                "total_tests": 0,
                "success_rate": 0.0,
                "last_test_time": None,
                "avg_final_score": None,
                "avg_sustainability_score": None,
                "avg_popularity_score": None
            }
        
        try:
            # 查询该工具的所有测试记录
            result = (
                self.client.table(self.test_results_table)
                .select("*")
                .eq("tool_name", tool_name)
                .order("test_timestamp", desc=True)
                .execute()
            )
            
            if not result.data:
                return {
                    "total_tests": 0,
                    "success_rate": 0.0,
                    "last_test_time": None,
                    "avg_final_score": None,
                    "avg_sustainability_score": None,
                    "avg_popularity_score": None
                }
            
            test_records = result.data
            total_tests = len(test_records)
            successful_tests = sum(1 for record in test_records if record.get("test_success", False))
            
            # 计算各种平均值
            final_scores = [self._parse_score(r.get("final_score"), "final_score") 
                          for r in test_records if r.get("final_score") is not None]
            sustainability_scores = [self._parse_score(r.get("sustainability_score"), "sustainability_score") 
                                  for r in test_records if r.get("sustainability_score") is not None]
            popularity_scores = [self._parse_score(r.get("popularity_score"), "popularity_score") 
                               for r in test_records if r.get("popularity_score") is not None]
            
            return {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": round((successful_tests / total_tests * 100.0), 2) if total_tests > 0 else 0.0,
                "last_test_time": self._parse_datetime(test_records[0].get("test_timestamp")) if test_records else None,
                "avg_final_score": round(sum(final_scores) / len(final_scores), 2) if final_scores else None,
                "avg_sustainability_score": round(sum(sustainability_scores) / len(sustainability_scores), 2) if sustainability_scores else None,
                "avg_popularity_score": round(sum(popularity_scores) / len(popularity_scores), 2) if popularity_scores else None,
            }
            
        except Exception as e:
            logger.warning(f"获取增强测试统计失败 - {tool_name}: {e}")
            return {
                "total_tests": 0,
                "success_rate": 0.0,
                "last_test_time": None,
                "avg_final_score": None,
                "avg_sustainability_score": None,
                "avg_popularity_score": None
            }

    def _apply_sorting_and_pagination(self, tools: List[MCPToolInfo], filters: ToolSearchFilter) -> List[MCPToolInfo]:
        """应用排序和分页"""
        if not tools:
            return tools
        
        # 排序
        sort_field = filters.sort_by if filters.sort_by in ["tashan_score", "sustainability_score", "popularity_score", "lobehub_score"] else "tashan_score"
        reverse = True  # 降序排列
        
        try:
            tools.sort(key=lambda x: getattr(x, sort_field) or 0, reverse=reverse)
        except Exception as e:
            logger.warning(f"排序失败: {e}, 使用默认排序")
        
        # 分页
        start = filters.offset
        end = start + filters.limit
        return tools[start:end]

    async def _search_tools_from_main_table(self, filters: ToolSearchFilter) -> List[MCPToolInfo]:
        """从 tools_table 搜索真实的工具信息"""
        try:
            query = self.client.table(self.tools_table).select("*")
            
            # 添加过滤条件
            if filters.query:
                query = query.or_(f"name.ilike.%{filters.query}%,description.ilike.%{filters.query}%,author.ilike.%{filters.query}%")
            
            if filters.category:
                query = query.eq("category", filters.category)
            
            if filters.author:
                query = query.eq("author", filters.author)
            
            if filters.deployment_method:
                query = query.eq("deployment_method", filters.deployment_method)
            
            # 评分范围过滤
            if filters.min_tashan_score is not None:
                query = query.gte("tashan_score", filters.min_tashan_score)
            
            if filters.max_tashan_score is not None:
                query = query.lte("tashan_score", filters.max_tashan_score)
            
            # 添加排序和分页
            sort_field = filters.sort_by if filters.sort_by in ["tashan_score", "sustainability_score", "popularity_score", "lobehub_score"] else "tashan_score"
            query = (
                query
                .order(sort_field, desc=True)
                .order("updated_at", desc=True)
                .range(filters.offset, filters.offset + filters.limit - 1)
            )
            
            # 执行查询
            result = query.execute()
            
            if result.data:
                tools = []
                for item in result.data:
                    try:
                        tool_info = MCPToolInfo(
                            tool_id=item.get("tool_id"),
                            name=item.get("name", "未知工具"),
                            author=item.get("author", "未知作者"),
                            description=item.get("description", "暂无描述"),
                            category=item.get("category", "其他"),
                            github_url=item.get("github_url", ""),
                            url=item.get("url", ""),
                            deployment_method=item.get("deployment_method", "未知"),
                            package_name=item.get("package_name"),
                            requires_api_key=item.get("requires_api_key", False),
                            tashan_score=self._parse_score(item.get("tashan_score"), "tashan_score"),
                            utility_score=self._parse_score(item.get("utility_score"), "utility_score"),
                            sustainability_score=self._parse_score(item.get("sustainability_score"), "sustainability_score"),
                            popularity_score=self._parse_score(item.get("popularity_score"), "popularity_score"),
                            lobehub_evaluate=item.get("lobehub_evaluate"),
                            lobehub_score=self._parse_score(item.get("lobehub_score"), "lobehub_score"),
                            lobehub_stars=self._parse_integer(item.get("lobehub_stars"), "lobehub_stars"),
                            lobehub_forks=self._parse_integer(item.get("lobehub_forks"), "lobehub_forks"),
                            test_success_rate=self._parse_score(item.get("test_success_rate"), "test_success_rate"),
                            test_count=self._parse_integer(item.get("test_count"), "test_count"),
                            last_test_time=self._parse_datetime(item.get("last_test_time")),
                            created_at=self._parse_datetime(item.get("created_at")),
                            updated_at=self._parse_datetime(item.get("updated_at"))
                        )
                        
                        # 验证和修复时间戳数据
                        tool_info = self._validate_timestamps(tool_info)
                        tools.append(tool_info)
                    except Exception as e:
                        logger.warning(f"解析工具信息失败: {item.get('tool_id', 'unknown')}, 错误: {e}")
                        continue
                
                return tools
            return []
            
        except Exception as e:
            logger.warning(f"从 tools_table 搜索失败: {e}")
            return []

    async def _search_tools_from_test_results(self, filters: ToolSearchFilter) -> List[MCPToolInfo]:
        """从 test_results 表搜索工具信息（回退方案）"""
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
                        
                        # 计算真实的测试统计数据
                        tool_identifier = item.get("tool_identifier", "")
                        test_stats = await self._calculate_test_statistics(tool_identifier)
                        
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
                            tashan_score=self._parse_score(item.get("final_score"), "final_score"),
                            sustainability_score=self._parse_score(item.get("sustainability_score"), "sustainability_score"),
                            popularity_score=self._parse_score(item.get("popularity_score"), "popularity_score"),
                            lobehub_evaluate=item.get("lobehub_evaluate"),
                            lobehub_score=self._parse_score(item.get("lobehub_score"), "lobehub_score"),
                            lobehub_stars=self._parse_integer(item.get("lobehub_star_count"), "lobehub_star_count"),
                            lobehub_forks=self._parse_integer(item.get("lobehub_fork_count"), "lobehub_fork_count"),
                            test_success_rate=test_stats["test_success_rate"],
                            test_count=test_stats["test_count"],
                            last_test_time=test_stats["last_test_time"],
                            created_at=self._parse_datetime(item.get("created_at")),
                            updated_at=self._parse_datetime(item.get("test_timestamp"))
                        )
                        
                        # 验证和修复时间戳数据
                        tool_info = self._validate_timestamps(tool_info)
                        tools.append(tool_info)
                
                return tools
            return []
            
        except Exception as e:
            logger.error(f"搜索工具失败: {e}")
            raise

    async def get_tool_by_name(self, name: str) -> Optional[MCPToolInfo]:
        """根据名称获取工具"""
        if not self.client:
            logger.warning("数据库未连接，返回None")
            return None
            
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
                
                # 计算真实的测试统计数据
                tool_identifier = item.get("tool_identifier", "")
                test_stats = await self._calculate_test_statistics(tool_identifier)
                
                return MCPToolInfo(
                    tool_id=item.get("test_id"),
                    name=item.get("tool_name", "未知工具"),
                    author=item.get("tool_author", "未知作者"),
                    description=f"来自 {item.get('tool_identifier', '未知来源')} 的MCP工具",
                    category=item.get("tool_category", "其他"),
                    github_url=item.get("tool_identifier", ""),
                    url=item.get("tool_identifier", ""),
                    deployment_method="未知",
                    tashan_score=self._parse_score(item.get("final_score"), "final_score"),
                    sustainability_score=self._parse_score(item.get("sustainability_score"), "sustainability_score"),
                    popularity_score=self._parse_score(item.get("popularity_score"), "popularity_score"),
                    lobehub_evaluate=item.get("lobehub_evaluate"),
                    lobehub_score=self._parse_score(item.get("lobehub_score"), "lobehub_score"),
                    lobehub_stars=self._parse_integer(item.get("lobehub_star_count"), "lobehub_star_count"),
                    lobehub_forks=self._parse_integer(item.get("lobehub_fork_count"), "lobehub_fork_count"),
                    test_success_rate=test_stats["test_success_rate"],
                    test_count=test_stats["test_count"],
                    last_test_time=test_stats["last_test_time"],
                    created_at=self._parse_datetime(item.get("created_at")),
                    updated_at=self._parse_datetime(item.get("test_timestamp"))
                )
                
                # 验证和修复时间戳数据
                tool_info = self._validate_timestamps(tool_info)
                return tool_info
            return None
            
        except Exception as e:
            logger.error(f"获取工具失败: {e}")
            return None

    async def get_tool_by_id(self, tool_id: str) -> Optional[MCPToolInfo]:
        """根据ID获取工具"""
        if not self.client:
            logger.warning("数据库未连接，返回None")
            return None
            
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
        if not self.client:
            logger.warning("数据库未连接，返回空结果")
            return []
            
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
                        
                        # 验证和修复时间戳数据
                        tool_info = self._validate_timestamps(tool_info)
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
        if not self.client:
            logger.warning("数据库未连接，返回空结果")
            return []
            
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
        if not self.client:
            logger.warning("数据库未连接，返回空结果")
            return []
            
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
                validated_results = []
                for item in result.data:
                    try:
                        test_result = TestResult(**item)
                        validated_result = self._validate_test_result(test_result)
                        validated_results.append(validated_result)
                    except Exception as e:
                        logger.warning(f"解析测试结果失败: {item}, 错误: {e}")
                        continue
                return validated_results
            return []
            
        except Exception as e:
            logger.error(f"获取测试结果失败: {e}")
            return []

    async def get_total_tools_count(self) -> int:
        """获取工具总数"""
        if not self.client:
            logger.warning("数据库未连接，返回0")
            return 0
            
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
        if not self.client:
            logger.warning("数据库未连接，返回空列表")
            return []
            
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
        if not self.client:
            logger.info("数据库未连接，健康检查返回False")
            return False
            
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
        if not self.client:
            logger.warning("数据库未连接，返回空结果")
            return []
            
        try:
            result = (
                self.client.table(self.test_results_table)
                .select("*")
                .order("test_timestamp", desc=True)
                .limit(limit)
                .execute()
            )
            
            if result.data:
                validated_results = []
                for item in result.data:
                    try:
                        test_result = TestResult(**item)
                        validated_result = self._validate_test_result(test_result)
                        validated_results.append(validated_result)
                    except Exception as e:
                        logger.warning(f"解析测试结果失败: {item}, 错误: {e}")
                        continue
                return validated_results
            return []
            
        except Exception as e:
            logger.error(f"获取最近测试结果失败: {e}")
            return []

    async def get_total_test_results_count(self) -> int:
        """获取测试结果总数"""
        if not self.client:
            logger.warning("数据库未连接，返回0")
            return 0
            
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