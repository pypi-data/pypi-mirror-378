"""工具函数测试"""

import pytest
from datetime import datetime
from mcp_evaluation_server.models import MCPToolInfo, ToolSearchFilter
from mcp_evaluation_server.utils import (
    format_tool_info,
    generate_recommendations,
    generate_use_cases,
    format_search_summary,
    safe_float,
    safe_int,
    format_timestamp,
    validate_sort_field,
    calculate_comprehensive_score
)


class TestFormatToolInfo:
    """测试工具信息格式化"""
    
    def test_format_tool_info_basic(self, mock_tool_info):
        """测试基本工具信息格式化"""
        result = format_tool_info(mock_tool_info)
        
        assert result["tool_id"] == mock_tool_info.tool_id
        assert result["name"] == mock_tool_info.name
        assert result["author"] == mock_tool_info.author
        assert result["description"] == mock_tool_info.description
        assert result["category"] == mock_tool_info.category
        assert result["github_url"] == mock_tool_info.github_url
        assert result["url"] == mock_tool_info.url
        assert result["deployment_method"] == mock_tool_info.deployment_method
        assert result["package_name"] == mock_tool_info.package_name
        assert result["requires_api_key"] == mock_tool_info.requires_api_key
        
        # 验证评分信息
        assert result["scores"]["tashan_score"] == mock_tool_info.tashan_score
        assert result["scores"]["utility_score"] == mock_tool_info.utility_score
        assert result["scores"]["sustainability_score"] == mock_tool_info.sustainability_score
        assert result["scores"]["popularity_score"] == mock_tool_info.popularity_score
        
        # 验证统计信息
        assert result["stats"]["test_success_rate"] == mock_tool_info.test_success_rate
        assert result["stats"]["test_count"] == mock_tool_info.test_count
        
        # 验证LobeHub数据
        assert result["lobehub_data"]["stars"] == mock_tool_info.lobehub_stars
        assert result["lobehub_data"]["forks"] == mock_tool_info.lobehub_forks
    
    def test_format_tool_info_none_values(self):
        """测试空值处理"""
        tool = MCPToolInfo(
            name="测试工具",
            author="测试作者",
            description="测试描述",
            github_url="https://github.com/test",
            url="https://test.com",
            deployment_method="npm"
        )
        
        result = format_tool_info(tool)
        
        # 验证空值字段被正确处理
        assert result["scores"]["tashan_score"] is None
        assert result["scores"]["utility_score"] is None
        assert result["stats"]["test_success_rate"] is None
        assert result["stats"]["test_count"] is None
        assert result["stats"]["last_test_time"] is None


class TestGenerateRecommendations:
    """测试生成建议功能"""
    
    def test_generate_recommendations_excellent_score(self, mock_tool_info):
        """测试优秀评分的建议"""
        mock_tool_info.tashan_score = 95.0
        mock_tool_info.lobehub_evaluate = "优质"
        mock_tool_info.test_success_rate = 98.0
        mock_tool_info.sustainability_score = 90.0
        
        recommendations = generate_recommendations(mock_tool_info)
        
        assert "该工具评分优秀，推荐优先考虑使用" in recommendations
        assert "LobeHub平台评定为优质工具，质量有保障" in recommendations
        assert "工具测试成功率高，稳定性良好" in recommendations
        assert "项目活跃度高，维护情况良好" in recommendations
    
    def test_generate_recommendations_average_score(self, mock_tool_info):
        """测试平均评分的建议"""
        mock_tool_info.tashan_score = 70.0
        mock_tool_info.lobehub_evaluate = "良好"
        mock_tool_info.test_success_rate = 85.0
        mock_tool_info.sustainability_score = 75.0
        
        recommendations = generate_recommendations(mock_tool_info)
        
        assert "该工具评分良好，适合大多数使用场景" in recommendations
        assert "LobeHub平台评定为良好工具" in recommendations
    
    def test_generate_recommendations_poor_score(self, mock_tool_info):
        """测试较差评分的建议"""
        mock_tool_info.tashan_score = 45.0
        mock_tool_info.lobehub_evaluate = "欠佳"
        mock_tool_info.test_success_rate = 60.0
        mock_tool_info.sustainability_score = 40.0
        
        recommendations = generate_recommendations(mock_tool_info)
        
        assert "该工具评分一般，建议在充分评估后使用" in recommendations
        assert "LobeHub平台评定为欠佳，使用需谨慎" in recommendations
        assert "工具测试成功率较低，可能存在兼容性问题" in recommendations
        assert "项目活跃度较低，需谨慎评估长期可用性" in recommendations
    
    def test_generate_recommendations_no_scores(self, mock_tool_info):
        """测试无评分的情况"""
        mock_tool_info.tashan_score = None
        mock_tool_info.lobehub_evaluate = None
        mock_tool_info.test_success_rate = None
        mock_tool_info.sustainability_score = None
        
        recommendations = generate_recommendations(mock_tool_info)
        
        assert recommendations == ["暂无具体建议，请根据实际需求评估"]


class TestGenerateUseCases:
    """测试生成适用场景功能"""
    
    def test_generate_use_cases_development_tools(self, mock_tool_info):
        """测试开发工具的适用场景"""
        mock_tool_info.category = "开发工具推荐"
        
        use_cases = generate_use_cases(mock_tool_info)
        
        expected_cases = ["软件开发", "代码生成", "开发辅助", "IDE集成"]
        for case in expected_cases:
            assert case in use_cases
    
    def test_generate_use_cases_document_processing(self, mock_tool_info):
        """测试文档处理的适用场景"""
        mock_tool_info.category = "文档处理"
        
        use_cases = generate_use_cases(mock_tool_info)
        
        expected_cases = ["文档生成", "内容管理", "知识库建设", "文档自动化"]
        for case in expected_cases:
            assert case in use_cases
    
    def test_generate_use_cases_github_keywords(self, mock_tool_info):
        """测试GitHub关键词的适用场景"""
        mock_tool_info.description = "GitHub代码管理工具"
        
        use_cases = generate_use_cases(mock_tool_info)
        
        assert "代码管理" in use_cases
        assert "版本控制" in use_cases
        assert "协作开发" in use_cases
    
    def test_generate_use_cases_api_keywords(self, mock_tool_info):
        """测试API关键词的适用场景"""
        mock_tool_info.description = "API集成工具"
        
        use_cases = generate_use_cases(mock_tool_info)
        
        assert "API集成" in use_cases
        assert "系统对接" in use_cases
        assert "数据交换" in use_cases
    
    def test_generate_use_cases_no_category(self, mock_tool_info):
        """测试无分类的情况"""
        mock_tool_info.category = "未知分类"
        mock_tool_info.description = "一个通用工具"
        
        use_cases = generate_use_cases(mock_tool_info)
        
        assert "通用场景" in use_cases


class TestFormatSearchSummary:
    """测试搜索摘要格式化"""
    
    def test_format_search_summary_basic(self, mock_search_filter):
        """测试基本搜索摘要"""
        result_count = 10
        total_count = 50
        
        summary = format_search_summary(mock_search_filter, total_count, result_count)
        
        assert "找到 10 个工具" in summary
        assert "(共 50 个)" in summary
        assert "关键词 '测试'" in summary
        assert "分类 '开发工具推荐'" in summary
        assert "评分 >= 80" in summary
        assert "评分 <= 90" in summary
        assert "部署方式 'npm'" in summary
        assert "作者 '测试作者'" in summary
    
    def test_format_search_summary_no_filters(self):
        """测试无过滤条件的搜索摘要"""
        filters = ToolSearchFilter()
        result_count = 10
        total_count = 50
        
        summary = format_search_summary(filters, total_count, result_count)
        
        assert "找到 10 个工具 (共 50 个)." == summary
    
    def test_format_search_summary_no_total(self, mock_search_filter):
        """测试无总数的情况"""
        result_count = 10
        total_count = 10
        
        summary = format_search_summary(mock_search_filter, total_count, result_count)
        
        assert "找到 10 个工具" in summary
        assert "(共 10 个)" not in summary


class TestUtilityFunctions:
    """测试工具函数"""
    
    def test_safe_float(self):
        """测试安全浮点数转换"""
        assert safe_float("123.45") == 123.45
        assert safe_float(123.45) == 123.45
        assert safe_float("invalid") is None
        assert safe_float(None) is None
        assert safe_float("invalid", 0) == 0
    
    def test_safe_int(self):
        """测试安全整数转换"""
        assert safe_int("123") == 123
        assert safe_int(123) == 123
        assert safe_int("invalid") is None
        assert safe_int(None) is None
        assert safe_int("invalid", 0) == 0
    
    def test_format_timestamp(self):
        """测试时间戳格式化"""
        # 测试datetime对象
        dt = datetime(2023, 1, 1, 12, 0, 0)
        assert format_timestamp(dt) == "2023-01-01 12:00:00"
        
        # 测试字符串
        assert format_timestamp("2023-01-01T12:00:00") == "2023-01-01 12:00:00"
        
        # 测试None
        assert format_timestamp(None) == ""
    
    def test_validate_sort_field(self):
        """测试排序字段验证"""
        # 测试有效字段
        assert validate_sort_field("tashan_score") == "tashan_score"
        assert validate_sort_field("utility_score") == "utility_score"
        assert validate_sort_field("created_at") == "created_at"
        
        # 测试无效字段
        assert validate_sort_field("invalid_field") == "tashan_score"
        assert validate_sort_field("") == "tashan_score"
    
    def test_calculate_comprehensive_score(self, mock_tool_info):
        """测试综合评分计算"""
        # 测试有他山评分的情况
        assert calculate_comprehensive_score(mock_tool_info) == mock_tool_info.tashan_score
        
        # 测试无他山评分但有其他评分的情况
        mock_tool_info.tashan_score = None
        mock_tool_info.utility_score = 80.0
        mock_tool_info.sustainability_score = 75.0
        mock_tool_info.popularity_score = 85.0
        
        expected = (80.0 + 75.0 + 85.0) / 3
        assert calculate_comprehensive_score(mock_tool_info) == expected
        
        # 测试无任何评分的情况
        mock_tool_info.utility_score = None
        mock_tool_info.sustainability_score = None
        mock_tool_info.popularity_score = None
        
        assert calculate_comprehensive_score(mock_tool_info) is None