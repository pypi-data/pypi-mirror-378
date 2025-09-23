"""独立的MCP服务器测试版本"""

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
                        "limit": {"type": "integer", "default": 20, "description": "返回结果数量限制"},
                        "offset": {"type": "integer", "default": 0, "description": "偏移量"}
                    }
                }
            },
            {
                "name": "get_top_tools",
                "description": "获取热门MCP工具排行榜，可按不同评分维度排序",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "sort_by": {"type": "string", "default": "tashan_score", "description": "排序字段"},
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
                "name": f"搜索结果工具{i}",
                "description": f"匹配'{query}'的工具{i}",
                "category": "开发工具"
            }
            for i in range(min(limit, 5))
        ]
        
        return {
            "tools": mock_tools,
            "total": len(mock_tools),
            "summary": f"找到 {len(mock_tools)} 个工具"
        }
    
    async def _get_top_tools(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取热门工具"""
        sort_by = args.get("sort_by", "tashan_score")
        limit = args.get("limit", 10)
        
        # 模拟热门工具
        mock_tools = [
            {
                "name": f"热门工具{i}",
                "description": f"按{sort_by}排序的热门工具{i}",
                "score": 90 - i * 5
            }
            for i in range(min(limit, 5))
        ]
        
        return {
            "tools": mock_tools,
            "sort_by": sort_by,
            "limit": limit
        }
    
    async def _get_tool_categories(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取工具分类"""
        # 模拟分类统计
        categories = [
            {"category": "开发工具", "count": 25},
            {"category": "文档处理", "count": 15},
            {"category": "数据分析", "count": 12}
        ]
        
        return {
            "categories": categories,
            "total_categories": len(categories)
        }
    
    async def _health_check(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """健康检查"""
        return {
            "status": "healthy",
            "version": "0.1.8",
            "database": "connected"
        }

async def run_stdio_server():
    """运行stdio模式的MCP服务器"""
    server = TestMCPServer()
    
    try:
        while True:
            # 读取JSON-RPC请求
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
                
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    # 完全静默模式
    import warnings
    warnings.filterwarnings("ignore")
    
    # 运行服务器
    asyncio.run(run_stdio_server())