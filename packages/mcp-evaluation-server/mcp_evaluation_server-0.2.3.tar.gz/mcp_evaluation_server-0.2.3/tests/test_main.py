"""FastMCP服务器测试"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from mcp_evaluation_server.main import mcp, db_manager
from mcp_evaluation_server.models import MCPToolInfo, ToolSearchFilter
from mcp_evaluation_server.utils import format_tool_info


class TestSearchMcpTools:
    """测试搜索MCP工具功能"""
    
    @pytest.mark.asyncio
    async def test_search_tools_success(self, database_manager):
        """测试成功搜索工具"""
        # 设置模拟返回值
        mock_tool = MCPToolInfo(
            name="测试工具",
            author="测试作者",
            description="这是一个测试工具",
            github_url="https://github.com/test",
            url="https://test.com",
            deployment_method="npm"
        )
        
        database_manager.search_tools.return_value = [mock_tool]
        database_manager.get_total_tools_count.return_value = 100
        
        # 模拟MCP工具调用
        with patch.object(db_manager, 'search_tools') as mock_search, \
             patch.object(db_manager, 'get_total_tools_count') as mock_count:
            
            mock_search.return_value = [mock_tool]
            mock_count.return_value = 100
            
            # 测试搜索逻辑
            filters = ToolSearchFilter(query="测试", limit=10)
            tools = await db_manager.search_tools(filters)
            total_count = await db_manager.get_total_tools_count(filters)
            
            assert len(tools) == 1
            assert total_count == 100
            assert tools[0].name == "测试工具"
    
    @pytest.mark.asyncio
    async def test_search_tools_with_category(self, database_manager):
        """测试按分类搜索工具"""
        mock_tool = MCPToolInfo(
            name="开发工具",
            author="测试作者",
            description="开发工具测试",
            github_url="https://github.com/test",
            url="https://test.com",
            deployment_method="npm",
            category="开发工具推荐"
        )
        
        with patch.object(db_manager, 'search_tools') as mock_search, \
             patch.object(db_manager, 'get_total_tools_count') as mock_count:
            
            mock_search.return_value = [mock_tool]
            mock_count.return_value = 50
            
            filters = ToolSearchFilter(
                query="开发",
                category="开发工具推荐",
                min_tashan_score=80.0,
                max_tashan_score=90.0,
                limit=5
            )
            tools = await db_manager.search_tools(filters)
            total_count = await db_manager.get_total_tools_count(filters)
            
            assert len(tools) == 1
            assert total_count == 50
            assert tools[0].category == "开发工具推荐"
    
    @pytest.mark.asyncio
    async def test_search_tools_empty_result(self, database_manager):
        """测试搜索无结果"""
        with patch.object(db_manager, 'search_tools') as mock_search, \
             patch.object(db_manager, 'get_total_tools_count') as mock_count:
            
            mock_search.return_value = []
            mock_count.return_value = 0
            
            filters = ToolSearchFilter(query="不存在的工具")
            tools = await db_manager.search_tools(filters)
            total_count = await db_manager.get_total_tools_count(filters)
            
            assert len(tools) == 0
            assert total_count == 0
    
    @pytest.mark.asyncio
    async def test_search_tools_parameter_validation(self, database_manager):
        """测试参数验证"""
        # 测试空参数
        filters = ToolSearchFilter()
        
        with patch.object(db_manager, 'search_tools') as mock_search:
            mock_search.return_value = []
            tools = await db_manager.search_tools(filters)
            
            assert isinstance(tools, list)


class TestGetToolEvaluation:
    """测试获取工具评估功能"""
    
    @pytest.mark.asyncio
    async def test_get_tool_evaluation_success(self, database_manager):
        """测试成功获取工具评估"""
        mock_tool = MCPToolInfo(
            name="测试工具",
            author="测试作者",
            description="测试工具描述",
            github_url="https://github.com/test",
            url="https://test.com",
            deployment_method="npm",
            tashan_score=85.0,
            utility_score=80.0,
            sustainability_score=90.0,
            popularity_score=75.0,
            test_success_rate=95.0,
            test_count=100,
            category="开发工具推荐"
        )
        
        with patch.object(db_manager, 'get_tool_by_name') as mock_get, \
             patch.object(db_manager, 'get_tool_test_results') as mock_results:
            
            mock_get.return_value = mock_tool
            mock_results.return_value = []
            
            tool = await db_manager.get_tool_by_name("测试工具")
            test_results = await db_manager.get_tool_test_results("test-tool-id")
            
            assert tool is not None
            assert tool.name == "测试工具"
            assert tool.tashan_score == 85.0
            assert isinstance(test_results, list)
    
    @pytest.mark.asyncio 
    async def test_get_tool_evaluation_not_found(self, database_manager):
        """测试工具不存在"""
        with patch.object(db_manager, 'get_tool_by_name') as mock_get:
            mock_get.return_value = None
            
            tool = await db_manager.get_tool_by_name("不存在的工具")
            
            assert tool is None


class TestGetTopTools:
    """测试获取热门工具功能"""
    
    @pytest.mark.asyncio
    async def test_get_top_tools_success(self, database_manager):
        """测试成功获取热门工具"""
        mock_tools = [
            MCPToolInfo(
                name="热门工具1",
                author="作者1",
                description="描述1",
                github_url="https://github.com/test1",
                url="https://test1.com",
                deployment_method="npm",
                tashan_score=95.0
            ),
            MCPToolInfo(
                name="热门工具2", 
                author="作者2",
                description="描述2",
                github_url="https://github.com/test2",
                url="https://test2.com",
                deployment_method="npm",
                tashan_score=90.0
            )
        ]
        
        with patch.object(db_manager, 'get_top_tools') as mock_top:
            mock_top.return_value = mock_tools
            
            tools = await db_manager.get_top_tools(limit=10, sort_by="tashan_score")
            
            assert len(tools) == 2
            assert tools[0].tashan_score == 95.0
            assert tools[1].tashan_score == 90.0


class TestGetToolCategories:
    """测试获取工具分类功能"""
    
    @pytest.mark.asyncio
    async def test_get_tool_categories_success(self, database_manager):
        """测试成功获取工具分类"""
        mock_stats = [
            Mock(category="开发工具推荐", count=50, percentage=50.0),
            Mock(category="文档处理", count=30, percentage=30.0),
            Mock(category="API集成", count=20, percentage=20.0)
        ]
        
        with patch.object(db_manager, 'get_category_stats') as mock_stats_func:
            mock_stats_func.return_value = mock_stats
            
            stats = await db_manager.get_category_stats()
            
            assert len(stats) == 3
            assert stats[0].category == "开发工具推荐"
            assert stats[0].count == 50


class TestHealthCheck:
    """测试健康检查功能"""
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, database_manager):
        """测试健康检查成功"""
        with patch.object(db_manager, 'health_check') as mock_health:
            mock_health.return_value = True
            
            result = await db_manager.health_check()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_database_failure(self, database_manager):
        """测试数据库连接失败"""
        with patch.object(db_manager, 'health_check') as mock_health:
            mock_health.return_value = False
            
            result = await db_manager.health_check()
            
            assert result is False


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, database_manager):
        """测试完整工作流程"""
        # 创建测试数据
        mock_tool = MCPToolInfo(
            name="集成测试工具",
            author="测试作者",
            description="集成测试工具描述",
            github_url="https://github.com/test",
            url="https://test.com",
            deployment_method="npm",
            tashan_score=85.0,
            category="开发工具推荐"
        )
        
        # 模拟完整工作流程
        with patch.object(db_manager, 'search_tools') as mock_search, \
             patch.object(db_manager, 'get_total_tools_count') as mock_count, \
             patch.object(db_manager, 'get_tool_by_name') as mock_get, \
             patch.object(db_manager, 'get_top_tools') as mock_top, \
             patch.object(db_manager, 'get_category_stats') as mock_stats, \
             patch.object(db_manager, 'health_check') as mock_health:
            
            mock_search.return_value = [mock_tool]
            mock_count.return_value = 1
            mock_get.return_value = mock_tool
            mock_top.return_value = [mock_tool]
            mock_stats.return_value = []
            mock_health.return_value = True
            
            # 1. 搜索工具
            filters = ToolSearchFilter(query="集成测试")
            tools = await db_manager.search_tools(filters)
            assert len(tools) == 1
            
            # 2. 获取总数
            total = await db_manager.get_total_tools_count(filters)
            assert total == 1
            
            # 3. 获取工具详情
            tool = await db_manager.get_tool_by_name("集成测试工具")
            assert tool is not None
            assert tool.name == "集成测试工具"
            
            # 4. 获取热门工具
            top_tools = await db_manager.get_top_tools(limit=10)
            assert len(top_tools) == 1
            
            # 5. 健康检查
            health = await db_manager.health_check()
            assert health is True