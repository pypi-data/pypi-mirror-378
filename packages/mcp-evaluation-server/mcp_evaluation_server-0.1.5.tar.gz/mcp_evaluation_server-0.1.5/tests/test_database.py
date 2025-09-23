"""数据库管理器测试"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from mcp_evaluation_server.database import DatabaseManager
from mcp_evaluation_server.models import MCPToolInfo, TestResult, ToolSearchFilter, CategoryStats


class TestDatabaseManager:
    """测试数据库管理器"""
    
    @pytest.fixture
    def db_manager(self, mock_supabase_client):
        """创建数据库管理器实例"""
        with patch('src.database.create_client', return_value=mock_supabase_client):
            return DatabaseManager()
    
    @pytest.mark.asyncio
    async def test_search_tools_basic(self, db_manager, mock_supabase_client, sample_tool_data):
        """测试基本搜索功能"""
        # 设置模拟查询结果
        mock_query = Mock()
        mock_query.or_.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.gte.return_value = mock_query
        mock_query.lte.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.range.return_value = mock_query
        mock_query.execute.return_value = Mock(data=sample_tool_data)
        
        mock_supabase_client.table.return_value.select.return_value = mock_query
        
        # 执行搜索
        filters = ToolSearchFilter(query="测试", limit=10, offset=0)
        result = await db_manager.search_tools(filters)
        
        assert len(result) == 2
        assert result[0].name == "GitHub MCP Server"
        assert result[1].name == "文档处理工具"
    
    @pytest.mark.asyncio
    async def test_search_tools_with_category(self, db_manager, mock_supabase_client, sample_tool_data):
        """测试按分类搜索"""
        mock_query = Mock()
        mock_query.or_.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.gte.return_value = mock_query
        mock_query.lte.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.range.return_value = mock_query
        mock_query.execute.return_value = Mock(data=sample_tool_data[:1])  # 只返回第一个结果
        
        mock_supabase_client.table.return_value.select.return_value = mock_query
        
        filters = ToolSearchFilter(category="开发工具推荐", limit=10)
        result = await db_manager.search_tools(filters)
        
        assert len(result) == 1
        assert result[0].category == "开发工具推荐"
    
    @pytest.mark.asyncio
    async def test_search_tools_with_score_range(self, db_manager, mock_supabase_client, sample_tool_data):
        """测试按评分范围搜索"""
        mock_query = Mock()
        mock_query.or_.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.gte.return_value = mock_query
        mock_query.lte.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.range.return_value = mock_query
        mock_query.execute.return_value = Mock(data=sample_tool_data[:1])
        
        mock_supabase_client.table.return_value.select.return_value = mock_query
        
        filters = ToolSearchFilter(min_tashan_score=80.0, max_tashan_score=90.0, limit=10)
        result = await db_manager.search_tools(filters)
        
        assert len(result) == 1
        assert result[0].tashan_score == 85.0
    
    @pytest.mark.asyncio
    async def test_search_tools_empty_result(self, db_manager, mock_supabase_client):
        """测试空搜索结果"""
        mock_query = Mock()
        mock_query.or_.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.gte.return_value = mock_query
        mock_query.lte.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.range.return_value = mock_query
        mock_query.execute.return_value = Mock(data=[])
        
        mock_supabase_client.table.return_value.select.return_value = mock_query
        
        filters = ToolSearchFilter(query="不存在的工具")
        result = await db_manager.search_tools(filters)
        
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_get_tool_by_name_success(self, db_manager, mock_supabase_client, sample_tool_data):
        """测试成功根据名称获取工具"""
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.single.return_value = mock_query
        mock_query.execute.return_value = Mock(data=sample_tool_data[0])
        
        mock_supabase_client.table.return_value = mock_query
        
        result = await db_manager.get_tool_by_name("GitHub MCP Server")
        
        assert result is not None
        assert result.name == "GitHub MCP Server"
        assert result.tool_id == "tool-001"
    
    @pytest.mark.asyncio
    async def test_get_tool_by_name_not_found(self, db_manager, mock_supabase_client):
        """测试工具不存在的情况"""
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.single.return_value = mock_query
        mock_query.execute.return_value = Mock(data=None)
        
        mock_supabase_client.table.return_value = mock_query
        
        result = await db_manager.get_tool_by_name("不存在的工具")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_tool_by_id_success(self, db_manager, mock_supabase_client, sample_tool_data):
        """测试成功根据ID获取工具"""
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.single.return_value = mock_query
        mock_query.execute.return_value = Mock(data=sample_tool_data[0])
        
        mock_supabase_client.table.return_value = mock_query
        
        result = await db_manager.get_tool_by_id("tool-001")
        
        assert result is not None
        assert result.tool_id == "tool-001"
        assert result.name == "GitHub MCP Server"
    
    @pytest.mark.asyncio
    async def test_get_top_tools_success(self, db_manager, mock_supabase_client, sample_tool_data):
        """测试成功获取热门工具"""
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.not_.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.return_value = Mock(data=sample_tool_data)
        
        mock_supabase_client.table.return_value = mock_query
        
        result = await db_manager.get_top_tools("tashan_score", 10)
        
        assert len(result) == 2
        assert result[0].tashan_score == 85.0
    
    @pytest.mark.asyncio
    async def test_get_top_tools_invalid_sort_field(self, db_manager, mock_supabase_client, sample_tool_data):
        """测试无效排序字段"""
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.not_.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.return_value = Mock(data=sample_tool_data)
        
        mock_supabase_client.table.return_value = mock_query
        
        # 使用无效排序字段，应该默认使用tashan_score
        result = await db_manager.get_top_tools("invalid_field", 10)
        
        assert len(result) == 2
        # 验证调用使用了正确的排序字段
        mock_query.order.assert_called_with("tashan_score", desc=True)
    
    @pytest.mark.asyncio
    async def test_get_category_stats_success(self, db_manager, mock_supabase_client, sample_category_stats_data):
        """测试成功获取分类统计"""
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.group.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.execute.return_value = Mock(data=sample_category_stats_data)
        
        mock_supabase_client.table.return_value = mock_query
        
        result = await db_manager.get_category_stats()
        
        assert len(result) == 2
        assert result[0].category == "开发工具推荐"
        assert result[0].tool_count == 50
        assert result[0].avg_tashan_score == 85.0
    
    @pytest.mark.asyncio
    async def test_get_category_stats_fallback(self, db_manager, mock_supabase_client, sample_tool_data):
        """测试分类统计备用实现"""
        # 模拟RPC调用失败
        mock_query = Mock()
        mock_query.select.side_effect = Exception("RPC调用失败")
        mock_supabase_client.table.return_value = mock_query
        
        # 重新创建数据库管理器，使用模拟的create_client
        with patch('src.database.create_client', return_value=mock_supabase_client):
            db_manager = DatabaseManager()
        
        # 设置基本查询的模拟结果
        mock_basic_query = Mock()
        mock_basic_query.select.return_value = mock_basic_query
        mock_basic_query.execute.return_value = Mock(data=sample_tool_data)
        
        mock_supabase_client.table.return_value = mock_basic_query
        
        result = await db_manager.get_category_stats()
        
        assert len(result) == 2
        assert result[0].category == "开发工具推荐"  # 第一个分类
        assert result[0].tool_count == 1  # 该分类的工具数
        assert result[1].category == "文档处理"  # 第二个分类
        assert result[1].tool_count == 1  # 该分类的工具数
    
    @pytest.mark.asyncio
    async def test_get_tool_test_results_success(self, db_manager, mock_supabase_client, sample_test_result_data):
        """测试成功获取工具测试结果"""
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.return_value = Mock(data=sample_test_result_data)
        
        mock_supabase_client.table.return_value = mock_query
        
        result = await db_manager.get_tool_test_results("tool-001", 5)
        
        assert len(result) == 2
        assert result[0].test_id == "test-001"
        assert result[0].test_success == True
        assert result[1].test_id == "test-002"
        assert result[1].test_success == False
    
    @pytest.mark.asyncio
    async def test_get_total_tools_count_success(self, db_manager, mock_supabase_client):
        """测试成功获取工具总数"""
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.execute.return_value = Mock(count=100)
        
        mock_supabase_client.table.return_value = mock_query
        
        result = await db_manager.get_total_tools_count()
        
        assert result == 100
    
    @pytest.mark.asyncio
    async def test_get_total_tools_count_no_count(self, db_manager, mock_supabase_client):
        """测试没有count属性的情况"""
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_result = Mock()
        del mock_result.count  # 删除count属性
        mock_query.execute.return_value = mock_result
        
        mock_supabase_client.table.return_value = mock_query
        
        result = await db_manager.get_total_tools_count()
        
        assert result == 0
    
    @pytest.mark.asyncio
    async def test_get_all_categories_success(self, db_manager, mock_supabase_client, sample_tool_data):
        """测试成功获取所有分类"""
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.execute.return_value = Mock(data=sample_tool_data)
        
        mock_supabase_client.table.return_value = mock_query
        
        result = await db_manager.get_all_categories()
        
        assert len(result) == 2
        assert "开发工具推荐" in result
        assert "文档处理" in result
    
    @pytest.mark.asyncio
    async def test_get_all_categories_empty_result(self, db_manager, mock_supabase_client):
        """测试空分类结果"""
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.execute.return_value = Mock(data=[])
        
        mock_supabase_client.table.return_value = mock_query
        
        result = await db_manager.get_all_categories()
        
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, db_manager, mock_supabase_client):
        """测试健康检查成功"""
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.return_value = Mock(count=50)
        
        mock_supabase_client.table.return_value = mock_query
        
        result = await db_manager.health_check()
        
        assert result == True
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, db_manager, mock_supabase_client):
        """测试健康检查失败"""
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.side_effect = Exception("连接失败")
        
        mock_supabase_client.table.return_value = mock_query
        
        result = await db_manager.health_check()
        
        assert result == False
    
    @pytest.mark.asyncio
    async def test_safe_avg(self, db_manager):
        """测试安全平均值计算"""
        # 测试正常情况
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = db_manager._safe_avg(values)
        assert result == 3.0
        
        # 测试空列表
        result = db_manager._safe_avg([])
        assert result is None
        
        # 测试None值
        values = [1.0, None, 3.0, None, 5.0]
        result = db_manager._safe_avg([v for v in values if v is not None])
        assert result == 3.0


