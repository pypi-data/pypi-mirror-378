"""测试配置和fixtures"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from mcp_evaluation_server.models import MCPToolInfo, TestResult, ToolSearchFilter, CategoryStats
from mcp_evaluation_server.database import DatabaseManager
from mcp_evaluation_server.config import settings


@pytest.fixture
def mock_supabase_client():
    """模拟Supabase客户端"""
    mock_client = Mock()
    mock_client.table = Mock()
    return mock_client


@pytest.fixture
def mock_tool_info():
    """模拟工具信息"""
    return MCPToolInfo(
        tool_id="test-tool-001",
        name="测试工具",
        author="测试作者",
        description="这是一个测试工具",
        category="开发工具推荐",
        github_url="https://github.com/test/tool",
        url="https://test.com",
        deployment_method="npm",
        package_name="test-tool",
        requires_api_key=False,
        tashan_score=85.5,
        utility_score=80.0,
        sustainability_score=75.0,
        popularity_score=90.0,
        lobehub_evaluate="优质",
        lobehub_score=88.0,
        lobehub_stars=150,
        lobehub_forks=20,
        test_success_rate=95.0,
        test_count=100,
        last_test_time=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.fixture
def mock_test_result():
    """模拟测试结果"""
    return TestResult(
        test_id="test-result-001",
        tool_id="test-tool-001",
        test_timestamp=datetime.now(),
        test_success=True,
        deployment_success=True,
        communication_success=True,
        available_tools_count=5,
        test_duration_seconds=2.5,
        error_messages=[],
        platform_info="Linux",
        python_version="3.12.0",
        node_version="v18.0.0"
    )


@pytest.fixture
def mock_search_filter():
    """模拟搜索过滤器"""
    return ToolSearchFilter(
        query="测试",
        category="开发工具推荐",
        min_tashan_score=80.0,
        max_tashan_score=90.0,
        deployment_method="npm",
        author="测试作者",
        limit=10,
        offset=0
    )


@pytest.fixture
def mock_category_stats():
    """模拟分类统计"""
    return CategoryStats(
        category="开发工具推荐",
        tool_count=50,
        avg_tashan_score=85.0,
        avg_utility_score=80.0,
        avg_sustainability_score=75.0,
        avg_popularity_score=82.0
    )


@pytest.fixture
def database_manager(mock_supabase_client):
    """模拟数据库管理器"""
    # 模拟数据库管理器
    manager = Mock(spec=DatabaseManager)
    
    # 设置异步方法
    manager.search_tools = AsyncMock()
    manager.get_tool_by_name = AsyncMock()
    manager.get_tool_by_id = AsyncMock()
    manager.get_top_tools = AsyncMock()
    manager.get_category_stats = AsyncMock()
    manager.get_tool_test_results = AsyncMock()
    manager.get_total_tools_count = AsyncMock()
    manager.get_all_categories = AsyncMock()
    manager.health_check = AsyncMock()
    
    return manager


@pytest.fixture
def sample_tool_data():
    """示例工具数据"""
    return [
        {
            "tool_id": "tool-001",
            "name": "GitHub MCP Server",
            "author": "test-author",
            "description": "GitHub集成工具",
            "category": "开发工具推荐",
            "github_url": "https://github.com/test/github-mcp",
            "url": "https://test.com",
            "deployment_method": "npm",
            "package_name": "github-mcp-server",
            "requires_api_key": True,
            "tashan_score": 85.0,
            "utility_score": 80.0,
            "sustainability_score": 75.0,
            "popularity_score": 90.0,
            "lobehub_evaluate": "优质",
            "lobehub_score": 88.0,
            "lobehub_stars": 150,
            "lobehub_forks": 20,
            "test_success_rate": 95.0,
            "test_count": 100,
            "last_test_time": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "tool_id": "tool-002",
            "name": "文档处理工具",
            "author": "test-author",
            "description": "智能文档处理工具",
            "category": "文档处理",
            "github_url": "https://github.com/test/doc-processor",
            "url": "https://test.com",
            "deployment_method": "pip",
            "package_name": "doc-processor",
            "requires_api_key": False,
            "tashan_score": 75.0,
            "utility_score": 85.0,
            "sustainability_score": 80.0,
            "popularity_score": 70.0,
            "lobehub_evaluate": "良好",
            "lobehub_score": 78.0,
            "lobehub_stars": 100,
            "lobehub_forks": 15,
            "test_success_rate": 88.0,
            "test_count": 80,
            "last_test_time": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]


@pytest.fixture
def sample_category_stats_data():
    """示例分类统计数据"""
    return [
        {
            "category": "开发工具推荐",
            "tool_count": 50,
            "avg_tashan_score": 85.0,
            "avg_utility_score": 80.0,
            "avg_sustainability_score": 75.0,
            "avg_popularity_score": 82.0
        },
        {
            "category": "文档处理",
            "tool_count": 30,
            "avg_tashan_score": 75.0,
            "avg_utility_score": 85.0,
            "avg_sustainability_score": 80.0,
            "avg_popularity_score": 70.0
        }
    ]


@pytest.fixture
def sample_test_result_data():
    """示例测试结果数据"""
    return [
        {
            "test_id": "test-001",
            "tool_id": "tool-001",
            "test_timestamp": datetime.now().isoformat(),
            "test_success": True,
            "deployment_success": True,
            "communication_success": True,
            "available_tools_count": 5,
            "test_duration_seconds": 2.5,
            "error_messages": [],
            "platform_info": "Linux",
            "python_version": "3.12.0",
            "node_version": "v18.0.0"
        },
        {
            "test_id": "test-002",
            "tool_id": "tool-001",
            "test_timestamp": datetime.now().isoformat(),
            "test_success": False,
            "deployment_success": True,
            "communication_success": False,
            "available_tools_count": 0,
            "test_duration_seconds": 1.0,
            "error_messages": ["连接失败"],
            "platform_info": "Linux",
            "python_version": "3.12.0",
            "node_version": "v18.0.0"
        }
    ]