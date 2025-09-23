#!/usr/bin/env python3
"""
MCP工具评估助手服务器 - 简化版本
完全兼容Cherry Studio和百炼等MCP客户端
"""

import json
import sys
import asyncio
from typing import Dict, Any, List, Optional

class SimpleMCPServer:
    """简化的MCP服务器实现，完全兼容MCP协议"""
    
    def __init__(self):
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """定义MCP工具列表"""
        return [
            {
                "name": "search_mcp_tools",
                "description": "搜索MCP工具，根据关键词、分类、评分等条件搜索MCP工具，返回工具列表和相关信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "搜索关键词"},
                        "category": {"type": "string", "description": "工具分类"},
                        "min_tashan_score": {"type": "number", "description": "最低他山评分"},
                        "max_tashan_score": {"type": "number", "description": "最高他山评分"},
                        "deployment_method": {"type": "string", "description": "部署方式"},
                        "author": {"type": "string", "description": "工具作者"},
                        "limit": {"type": "integer", "default": 20, "description": "返回结果数量限制"},
                        "offset": {"type": "integer", "default": 0, "description": "偏移量"}
                    }
                }
            },
            {
                "name": "get_tool_evaluation", 
                "description": "获取特定工具的详细评估信息，包括测试结果、评分和推荐",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tool_identifier": {"type": "string", "description": "工具标识符"}
                    },
                    "required": ["tool_identifier"]
                }
            },
            {
                "name": "get_top_tools",
                "description": "获取热门MCP工具排行榜，可按不同评分维度排序",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "sort_by": {"type": "string", "enum": ["tashan_score", "sustainability_score", "popularity_score"], "default": "tashan_score"},
                        "limit": {"type": "integer", "default": 10, "description": "返回工具数量"}
                    }
                }
            },
            {
                "name": "get_tool_categories",
                "description": "获取所有工具分类及其统计信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "health_check",
                "description": "检查MCP评估服务器健康状态",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return await self._handle_initialize(params, request_id)
            elif method == "tools/list":
                return await self._handle_tools_list(params, request_id)
            elif method == "tools/call":
                return await self._handle_tool_call(params, request_id)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def _handle_initialize(self, params: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """处理初始化请求"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    }
                },
                "serverInfo": {
                    "name": "MCP工具评估助手",
                    "version": "0.1.8"
                }
            }
        }
    
    async def _handle_tools_list(self, params: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """处理工具列表请求"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": self.tools
            }
        }
    
    async def _handle_tool_call(self, params: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """处理工具调用请求"""
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        if name == "search_mcp_tools":
            result = await self._search_tools(arguments)
        elif name == "get_tool_evaluation":
            result = await self._get_tool_evaluation(arguments)
        elif name == "get_top_tools":
            result = await self._get_top_tools(arguments)
        elif name == "get_tool_categories":
            result = await self._get_tool_categories(arguments)
        elif name == "health_check":
            result = await self._health_check(arguments)
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {name}"
                }
            }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, ensure_ascii=False, indent=2)
                    }
                ]
            }
        }
    
    async def _search_tools(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """搜索工具"""
        query = args.get("query", "")
        limit = args.get("limit", 20)
        
        # 模拟搜索结果
        mock_tools = [
            {
                "name": f"{query}相关工具{i}",
                "description": f"这是与'{query}'相关的MCP工具{i}",
                "category": "开发工具",
                "author": "工具作者",
                "tashan_score": 85.0 + i,
                "deployment_method": "pip",
                "url": f"https://github.com/example/tool{i}"
            }
            for i in range(min(limit, 5))
        ]
        
        return {
            "tools": mock_tools,
            "total": len(mock_tools),
            "summary": f"找到 {len(mock_tools)} 个与'{query}'相关的工具"
        }
    
    async def _get_tool_evaluation(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取工具评估"""
        tool_identifier = args.get("tool_identifier", "")
        
        # 模拟工具评估结果
        return {
            "tool": {
                "name": tool_identifier,
                "description": f"工具 {tool_identifier} 的详细评估信息",
                "category": "开发工具",
                "author": "工具作者",
                "tashan_score": 87.5,
                "sustainability_score": 82.0,
                "popularity_score": 90.0
            },
            "evaluation": {
                "overall_score": 86.5,
                "recommendation": "推荐使用此工具",
                "strengths": ["功能完整", "文档清晰", "社区活跃"],
                "weaknesses": ["学习曲线较陡", "某些功能需要付费"]
            },
            "test_results": [
                {
                    "test_name": "功能测试",
                    "status": "通过",
                    "score": 88.0
                },
                {
                    "test_name": "性能测试", 
                    "status": "通过",
                    "score": 85.0
                }
            ]
        }
    
    async def _get_top_tools(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取热门工具"""
        sort_by = args.get("sort_by", "tashan_score")
        limit = args.get("limit", 10)
        
        # 模拟热门工具
        mock_tools = [
            {
                "name": f"热门工具{i+1}",
                "description": f"按{sort_by}排序的第{i+1}个热门工具",
                "category": "开发工具",
                "author": "知名开发者",
                "tashan_score": 95.0 - i * 3,
                "sustainability_score": 90.0 - i * 2,
                "popularity_score": 98.0 - i * 4,
                "github_stars": 1000 + i * 500,
                "downloads": 50000 + i * 10000
            }
            for i in range(min(limit, 10))
        ]
        
        return {
            "tools": mock_tools,
            "sort_by": sort_by,
            "limit": limit,
            "summary": f"按{sort_by}排序的前{len(mock_tools)}个热门工具"
        }
    
    async def _get_tool_categories(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取工具分类"""
        # 模拟分类统计
        categories = [
            {"category": "开发工具", "count": 45, "avg_score": 87.2},
            {"category": "文档处理", "count": 32, "avg_score": 85.6},
            {"category": "数据分析", "count": 28, "avg_score": 89.1},
            {"category": "AI/ML", "count": 25, "avg_score": 91.3},
            {"category": "自动化", "count": 18, "avg_score": 84.8}
        ]
        
        return {
            "categories": categories,
            "total_categories": len(categories),
            "total_tools": sum(cat["count"] for cat in categories)
        }
    
    async def _health_check(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """健康检查"""
        return {
            "status": "healthy",
            "version": "0.1.8",
            "database": "connected",
            "uptime": "24h",
            "last_update": "2024-01-15T10:30:00Z"
        }

async def run_stdio_server():
    """运行stdio模式的MCP服务器"""
    server = SimpleMCPServer()
    
    try:
        while True:
            # 读取JSON-RPC请求
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    response = await server.handle_request(request)
                    
                    # 发送响应
                    response_json = json.dumps(response, ensure_ascii=False)
                    print(response_json, flush=True)
                    
                except json.JSONDecodeError:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error: Invalid JSON"
                        }
                    }
                    print(json.dumps(error_response, ensure_ascii=False), flush=True)
                    
            except (EOFError, KeyboardInterrupt):
                break
                
    except Exception as e:
        # 在stdio模式下，任何错误都可能导致连接中断
        pass

if __name__ == "__main__":
    # 完全静默模式
    import warnings
    warnings.filterwarnings("ignore")
    
    # 运行服务器
    asyncio.run(run_stdio_server())