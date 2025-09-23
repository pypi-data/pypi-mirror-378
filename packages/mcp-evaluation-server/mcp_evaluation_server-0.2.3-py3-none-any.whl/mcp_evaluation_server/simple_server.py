"""简化的MCP服务器实现，避免FastMCP API兼容性问题"""

import json
import sys
import os
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

class DateTimeEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理datetime对象"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from .database import DatabaseManager
    from .models import ToolSearchFilter, MCPToolInfo, CategoryStats
except ImportError:
    # 如果相对导入失败，使用绝对导入
    from mcp_evaluation_server.database import DatabaseManager
    from mcp_evaluation_server.models import ToolSearchFilter, MCPToolInfo, CategoryStats

class SimpleMCPServer:
    """简化的MCP服务器实现"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
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
                        "offset": {"type": "integer", "default": 0, "description": "偏移量"},
                        "sort_by": {"type": "string", "enum": ["tashan_score", "sustainability_score", "popularity_score", "lobehub_score", "comprehensive_score"], "default": "tashan_score", "description": "排序方式"}
                    }
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
                    "version": "0.2.2"
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
                        "text": json.dumps(result, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
                    }
                ]
            }
        }
    
    async def _search_tools(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """搜索工具"""
        try:
            # 验证并设置默认值
            limit = min(max(1, args.get("limit", 20)), 100)  # 限制在1-100之间
            offset = max(0, args.get("offset", 0))
            sort_by = args.get("sort_by", "tashan_score")
            
            # 验证排序字段
            valid_sort_fields = {
                "tashan_score", "sustainability_score", "popularity_score", 
                "lobehub_score", "comprehensive_score", "test_timestamp"
            }
            if sort_by not in valid_sort_fields:
                sort_by = "tashan_score"
            
            # 验证分数范围
            min_score = args.get("min_tashan_score")
            max_score = args.get("max_tashan_score")
            
            if min_score is not None:
                min_score = max(0, min(100, min_score))
            if max_score is not None:
                max_score = max(0, min(100, max_score))
            
            filters = ToolSearchFilter(
                query=args.get("query"),
                category=args.get("category"),
                min_tashan_score=min_score,
                max_tashan_score=max_score,
                deployment_method=args.get("deployment_method"),
                author=args.get("author"),
                limit=limit,
                offset=offset
            )
            
            tools = await self.db_manager.search_tools(filters)
            
            # 根据sort_by参数进行排序
            if sort_by != "tashan_score":
                tools.sort(key=lambda x: getattr(x, sort_by) or 0, reverse=True)
            
            # 生成搜索摘要
            filter_parts = []
            if args.get("query"):
                filter_parts.append(f"关键词 '{args['query']}'")
            if args.get("category"):
                filter_parts.append(f"分类 '{args['category']}'")
            if args.get("author"):
                filter_parts.append(f"作者 '{args['author']}'")
            
            filter_text = "基于条件: " + ", ".join(filter_parts) if filter_parts else "所有工具"
            
            return {
                "tools": [tool.model_dump() for tool in tools],
                "total": len(tools),
                "summary": f"找到 {len(tools)} 个工具({filter_text})",
                "sort_by": sort_by,
                "filters": {
                    "query": args.get("query"),
                    "category": args.get("category"),
                    "author": args.get("author"),
                    "limit": limit,
                    "offset": offset
                }
            }
            
        except Exception as e:
            # 错误处理
            return {
                "tools": [],
                "total": 0,
                "summary": f"搜索失败: {str(e)}",
                "sort_by": args.get("sort_by", "tashan_score"),
                "error": str(e)
            }
    
        
    async def _health_check(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """健康检查"""
        db_healthy = await self.db_manager.health_check()
        
        return {
            "status": "healthy" if db_healthy else "degraded",
            "database": "connected" if db_healthy else "disconnected",
            "version": "0.2.2"
        }

async def run_stdio_server():
    """运行stdio模式的MCP服务器"""
    server = SimpleMCPServer()
    
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
    finally:
        print("MCP服务器已停止", flush=True, file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(run_stdio_server())