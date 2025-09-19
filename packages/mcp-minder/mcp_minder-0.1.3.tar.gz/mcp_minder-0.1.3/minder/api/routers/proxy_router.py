"""
MCP代理路由

提供MCP代理、健康检查、服务发现等功能
"""

import json
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from minder.core.service_manager import ServiceManager
from minder.core.mcp_proxy import MCPProxyManager
from minder.api.models import (
    MCPAvailableServicesResponse,
    MCPHealthCheckRequest,
    MCPHealthCheckResponse
)

# 创建MCP代理路由
proxy_router = APIRouter(tags=["MCP代理"])

# 获取服务管理器实例（从main.py中共享）
def get_service_manager() -> ServiceManager:
    from minder.api.main import service_manager
    return service_manager

def get_mcp_proxy_manager() -> MCPProxyManager:
    from minder.core.mcp_proxy import MCPProxyManager
    return MCPProxyManager(get_service_manager())


# ==================== 获取信息类接口 ====================

@proxy_router.get("/api/mcp/services", response_model=MCPAvailableServicesResponse)
async def list_mcp_services():
    """
    获取可用的 MCP 服务列表
    
    返回所有正在运行且可用的 MCP 服务信息
    """
    try:
        services = await get_mcp_proxy_manager().get_available_services()
        
        return MCPAvailableServicesResponse(
            success=True,
            services=services,
            count=len(services),
            message=f"找到 {len(services)} 个可用的 MCP 服务"
        )
        
    except Exception as e:
        return MCPAvailableServicesResponse(
            success=False,
            services=[],
            count=0,
            message=f"获取服务列表失败: {str(e)}"
        )



@proxy_router.get("/api/mcp/services/{service_name}/health", response_model=MCPHealthCheckResponse)
async def check_mcp_service_health_by_name(service_name: str):
    """
    通过服务名检查 MCP 服务健康状态
    
    检查指定 MCP 服务的健康状态和连接性
    """
    try:
        health_info = await get_mcp_proxy_manager().health_check(service_name)
        
        return MCPHealthCheckResponse(
            success=health_info["status"] != "error",
            service_name=service_name,
            status=health_info["status"],
            port=health_info.get("port"),
            host=health_info.get("host"),
            message=health_info.get("message")
        )
        
    except Exception as e:
        return MCPHealthCheckResponse(
            success=False,
            service_name=service_name,
            status="error",
            message=f"健康检查失败: {str(e)}"
        )




# ==================== 核心代理转发接口 ====================

@proxy_router.post("/mcp/{service_name}")
async def mcp_middleware_proxy_by_name(service_name: str, request: Request):
    """
    MCP 中间件代理 - 通过 URL 路径指定服务名
    
    这个端点作为 MCP 中间件，可以：
    1. 接收标准的 MCP JSON-RPC 2.0 请求
    2. 根据 URL 路径中的服务名路由到对应的 MCP 服务
    3. 透明地转发请求并返回标准 MCP 响应
    
    用法: POST /mcp/{service_name}
    请求体: 标准的 MCP JSON-RPC 2.0 请求
    """
    try:
        # 读取原始请求体
        request_body = await request.body()
        
        # 解析MCP请求
        try:
            mcp_request = json.loads(request_body)
        except json.JSONDecodeError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error",
                        "data": f"Invalid JSON: {str(e)}"
                    }
                }
            )
        
        # 验证MCP请求格式
        if not isinstance(mcp_request, dict):
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": mcp_request.get("id") if isinstance(mcp_request, dict) else None,
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request",
                        "data": "Request must be a JSON object"
                    }
                }
            )
        
        if "method" not in mcp_request:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": mcp_request.get("id"),
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request",
                        "data": "Missing 'method' field"
                    }
                }
            )
        
        # 代理请求到目标服务
        try:
            response_data, session_id = await get_mcp_proxy_manager().proxy_mcp_request(
                service_name,
                mcp_request,
                request.headers.get("X-Session-ID")  # 使用现有的会话ID
            )
            
            # 返回标准 MCP 响应格式
            headers = {}
            if session_id:
                headers["X-Session-ID"] = session_id
            headers["X-Target-Service"] = service_name
            
            return JSONResponse(
                content=response_data,
                headers=headers
            )
            
        except Exception as proxy_error:
            return JSONResponse(
                status_code=500,
                content={
                    "jsonrpc": "2.0",
                    "id": mcp_request.get("id"),
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": f"Proxy error: {str(proxy_error)}"
                    }
                }
            )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": f"Unexpected error: {str(e)}"
                }
            }
        )