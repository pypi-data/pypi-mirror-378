"""数据模型测试"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from mcp_evaluation_server.models import (
    MCPToolInfo,
    TestResult,
    ToolSearchFilter,
    SearchResponse,
    ToolEvaluation,
    CategoryStats
)


class TestMCPToolInfo:
    """测试MCP工具信息模型"""
    
    def test_create_valid_tool(self):
        """测试创建有效工具信息"""
        tool = MCPToolInfo(
            name="测试工具",
            author="测试作者",
            description="这是一个测试工具",
            github_url="https://github.com/test/tool",
            url="https://test.com",
            deployment_method="npm"
        )
        
        assert tool.name == "测试工具"
        assert tool.author == "测试作者"
        assert tool.description == "这是一个测试工具"
        assert tool.category == "其他"  # 默认值
        assert tool.requires_api_key == False  # 默认值
    
    def test_create_tool_with_all_fields(self):
        """测试创建包含所有字段的工具信息"""
        now = datetime.now()
        tool = MCPToolInfo(
            tool_id="test-001",
            name="完整工具",
            author="完整作者",
            description="完整的工具描述",
            category="开发工具推荐",
            github_url="https://github.com/test/full",
            url="https://test.com/full",
            deployment_method="pip",
            package_name="full-tool",
            requires_api_key=True,
            tashan_score=95.0,
            utility_score=90.0,
            sustainability_score=85.0,
            popularity_score=88.0,
            lobehub_evaluate="优质",
            lobehub_score=92.0,
            lobehub_stars=200,
            lobehub_forks=30,
            test_success_rate=96.0,
            test_count=150,
            last_test_time=now,
            created_at=now,
            updated_at=now
        )
        
        assert tool.tool_id == "test-001"
        assert tool.tashan_score == 95.0
        assert tool.requires_api_key == True
        assert tool.test_success_rate == 96.0
    
    def test_create_tool_invalid(self):
        """测试创建无效工具信息"""
        # 缺少必需字段
        with pytest.raises(ValidationError):
            MCPToolInfo(
                name="测试工具",
                # 缺少 author
                description="测试描述",
                github_url="https://github.com/test",
                url="https://test.com",
                deployment_method="npm"
            )
        
        # 无效评分范围
        with pytest.raises(ValidationError):
            MCPToolInfo(
                name="测试工具",
                author="测试作者",
                description="测试描述",
                github_url="https://github.com/test",
                url="https://test.com",
                deployment_method="npm",
                tashan_score=150.0  # 超过100
            )
        
        # 负评分
        with pytest.raises(ValidationError):
            MCPToolInfo(
                name="测试工具",
                author="测试作者",
                description="测试描述",
                github_url="https://github.com/test",
                url="https://test.com",
                deployment_method="npm",
                utility_score=-10.0  # 负值
            )
        
        # 负测试计数
        with pytest.raises(ValidationError):
            MCPToolInfo(
                name="测试工具",
                author="测试作者",
                description="测试描述",
                github_url="https://github.com/test",
                url="https://test.com",
                deployment_method="npm",
                test_count=-1  # 负值
            )


class TestTestResult:
    """测试结果模型"""
    
    def test_create_valid_test_result(self):
        """测试创建有效测试结果"""
        result = TestResult(
            test_success=True,
            deployment_success=True,
            communication_success=True
        )
        
        assert result.test_success == True
        assert result.deployment_success == True
        assert result.communication_success == True
    
    def test_create_test_result_with_all_fields(self):
        """测试创建包含所有字段的测试结果"""
        now = datetime.now()
        result = TestResult(
            test_id="test-001",
            tool_id="tool-001",
            test_timestamp=now,
            test_success=True,
            deployment_success=True,
            communication_success=True,
            available_tools_count=10,
            test_duration_seconds=5.5,
            error_messages=[],
            platform_info="Linux",
            python_version="3.12.0",
            node_version="v18.0.0"
        )
        
        assert result.test_id == "test-001"
        assert result.available_tools_count == 10
        assert result.test_duration_seconds == 5.5
    
    def test_create_test_result_invalid(self):
        """测试创建无效测试结果"""
        # 负可用工具数量
        with pytest.raises(ValidationError):
            TestResult(
                test_success=True,
                deployment_success=True,
                communication_success=True,
                available_tools_count=-1  # 负值
            )
        
        # 负测试时长
        with pytest.raises(ValidationError):
            TestResult(
                test_success=True,
                deployment_success=True,
                communication_success=True,
                test_duration_seconds=-1.0  # 负值
            )


class TestToolSearchFilter:
    """测试工具搜索过滤器模型"""
    
    def test_create_empty_filter(self):
        """测试创建空过滤器"""
        filter = ToolSearchFilter()
        
        assert filter.query is None
        assert filter.category is None
        assert filter.limit == 20  # 默认值
        assert filter.offset == 0  # 默认值
    
    def test_create_filter_with_values(self):
        """测试创建包含值的过滤器"""
        filter = ToolSearchFilter(
            query="GitHub",
            category="开发工具推荐",
            min_tashan_score=80.0,
            max_tashan_score=90.0,
            deployment_method="npm",
            author="test-author",
            limit=10,
            offset=20
        )
        
        assert filter.query == "GitHub"
        assert filter.category == "开发工具推荐"
        assert filter.min_tashan_score == 80.0
        assert filter.max_tashan_score == 90.0
        assert filter.limit == 10
        assert filter.offset == 20
    
    def test_create_filter_invalid(self):
        """测试创建无效过滤器"""
        # 无效限制值
        with pytest.raises(ValidationError):
            ToolSearchFilter(limit=0)  # 小于1
        
        with pytest.raises(ValidationError):
            ToolSearchFilter(limit=101)  # 大于100
        
        # 无效偏移值
        with pytest.raises(ValidationError):
            ToolSearchFilter(offset=-1)  # 负值
        
        # 无效评分范围
        with pytest.raises(ValidationError):
            ToolSearchFilter(min_tashan_score=-10.0)  # 负值
        
        with pytest.raises(ValidationError):
            ToolSearchFilter(max_tashan_score=150.0)  # 超过100


class TestSearchResponse:
    """测试搜索响应模型"""
    
    def test_create_search_response(self, mock_tool_info):
        """测试创建搜索响应"""
        response = SearchResponse(
            success=True,
            tools=[mock_tool_info],
            total_count=100,
            search_summary="找到 1 个工具",
            filters=ToolSearchFilter()
        )
        
        assert response.success == True
        assert len(response.tools) == 1
        assert response.total_count == 100
        assert response.search_summary == "找到 1 个工具"
        assert response.error is None


class TestToolEvaluation:
    """测试工具评估模型"""
    
    def test_create_tool_evaluation(self, mock_tool_info):
        """测试创建工具评估"""
        evaluation = ToolEvaluation(
            success=True,
            tool_info=mock_tool_info,
            evaluation={"score": 85.0},
            recommendations=["推荐使用"],
            use_cases=["开发", "测试"]
        )
        
        assert evaluation.success == True
        assert evaluation.tool_info == mock_tool_info
        assert evaluation.evaluation["score"] == 85.0
        assert len(evaluation.recommendations) == 1
        assert len(evaluation.use_cases) == 2
        assert evaluation.error is None


class TestCategoryStats:
    """测试分类统计模型"""
    
    def test_create_category_stats(self):
        """测试创建分类统计"""
        stats = CategoryStats(
            category="开发工具推荐",
            tool_count=50,
            avg_tashan_score=85.0,
            avg_utility_score=80.0,
            avg_sustainability_score=75.0,
            avg_popularity_score=82.0
        )
        
        assert stats.category == "开发工具推荐"
        assert stats.tool_count == 50
        assert stats.avg_tashan_score == 85.0
        assert stats.avg_utility_score == 80.0
        assert stats.avg_sustainability_score == 75.0
        assert stats.avg_popularity_score == 82.0
    
    def test_create_category_stats_partial(self):
        """测试创建部分分类统计"""
        stats = CategoryStats(
            category="文档处理",
            tool_count=30
            # 其他字段默认为None
        )
        
        assert stats.category == "文档处理"
        assert stats.tool_count == 30
        assert stats.avg_tashan_score is None
        assert stats.avg_utility_score is None
        assert stats.avg_sustainability_score is None
        assert stats.avg_popularity_score is None


class TestModelSerialization:
    """测试模型序列化"""
    
    def test_tool_info_serialization(self, mock_tool_info):
        """测试工具信息序列化"""
        tool_dict = mock_tool_info.model_dump()
        
        assert tool_dict["name"] == mock_tool_info.name
        assert tool_dict["author"] == mock_tool_info.author
        assert tool_dict["description"] == mock_tool_info.description
        assert tool_dict["category"] == mock_tool_info.category
    
    def test_tool_info_deserialization(self, mock_tool_info):
        """测试工具信息反序列化"""
        tool_dict = mock_tool_info.model_dump()
        tool = MCPToolInfo(**tool_dict)
        
        assert tool.name == mock_tool_info.name
        assert tool.author == mock_tool_info.author
        assert tool.description == mock_tool_info.description
        assert tool.category == mock_tool_info.category
    
    def test_from_attributes(self, mock_tool_info):
        """测试从属性创建模型"""
        # 模拟ORM对象
        class MockOrmObject:
            def __init__(self):
                self.name = "ORM工具"
                self.author = "ORM作者"
                self.description = "ORM描述"
                self.github_url = "https://github.com/orm"
                self.url = "https://orm.com"
                self.deployment_method = "pip"
        
        orm_obj = MockOrmObject()
        tool = MCPToolInfo.model_validate(orm_obj)
        
        assert tool.name == "ORM工具"
        assert tool.author == "ORM作者"
        assert tool.description == "ORM描述"