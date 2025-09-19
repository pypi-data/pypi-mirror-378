"""
代码生成路由

提供MCP服务器代码生成和预览功能
"""

from fastapi import APIRouter, HTTPException

from minder.core.generator import MCPGenerator
from minder.core.mcp_builder import MCPBuilder, Tool
from minder.api.models import (
    MCPGenerateRequest,
    MCPGenerateResponse,
    MCPBuilderRequest,
    MCPBuilderResponse,
    MCPBuilderConfig,
    ToolInfo
)

# 创建代码生成路由
generator_router = APIRouter(tags=["代码生成"])

# 初始化生成器
generator = MCPGenerator()

# 获取服务管理器实例（复用现有的逻辑）
def get_service_manager():
    from minder.api.main import service_manager
    return service_manager


def _build_output_path(server_name: str, output_path: str) -> str:
    """
    构建输出路径，确保文件保存在 mcpserver/servername/ 目录下
    
    Args:
        server_name: 服务器名称
        output_path: 原始输出路径
        
    Returns:
        完整的输出路径
    """
    import os
    from pathlib import Path
    
    # 如果输出路径是相对路径，则基于 mcpserver 目录
    if not os.path.isabs(output_path):
        # 获取当前工作目录
        current_dir = Path.cwd()
        mcpserver_dir = current_dir / "mcpserver"
        
        # 创建服务目录
        service_dir = mcpserver_dir / server_name
        service_dir.mkdir(parents=True, exist_ok=True)
        
        # 如果输出路径只是文件名，保持原文件名
        if os.path.basename(output_path) == output_path:
            # 保持原始文件名，不强制改为 server.py
            pass
        
        # 构建完整路径
        full_path = service_dir / output_path
        return str(full_path)
    else:
        # 如果是绝对路径，直接返回
        return output_path


@generator_router.post("/generate", response_model=MCPGenerateResponse)
async def generate_mcp_server(request: MCPGenerateRequest):
    """生成 MCP 服务器文件"""
    try:
        success = generator.generate(
            output_path=request.output_path,
            service_name=request.service_name,
            tool_name=request.tool_name,
            tool_param_name=request.tool_param_name,
            tool_param_type=request.tool_param_type,
            tool_return_type=request.tool_return_type,
            tool_description=request.tool_description,
            tool_code=request.tool_code,
            service_port=request.service_port,
            author=request.author
        )
        
        if success:
            return MCPGenerateResponse(
                success=True,
                output_path=request.output_path,
                message=f"MCP服务器文件生成成功: {request.output_path}"
            )
        else:
            raise HTTPException(status_code=500, detail="MCP服务器文件生成失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@generator_router.post("/preview")
async def preview_mcp_server(request: MCPGenerateRequest):
    """预览MCP服务器代码（不生成文件）"""
    try:
        content = generator.generate_content(
            service_name=request.service_name,
            tool_name=request.tool_name,
            tool_param_name=request.tool_param_name,
            tool_param_type=request.tool_param_type,
            tool_return_type=request.tool_return_type,
            tool_description=request.tool_description,
            tool_code=request.tool_code,
            service_port=request.service_port,
            author=request.author
        )
        
        return {
            "success": True,
            "content": content,
            "message": "MCP服务器代码预览生成成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@generator_router.post("/generate-mcp", response_model=MCPBuilderResponse)
async def generate_mcp_with_builder(request: MCPBuilderRequest):
    """使用 MCPBuilder 生成 MCP 服务器文件"""
    try:
        # 创建 MCPBuilder 实例
        builder = MCPBuilder()
        
        # 设置服务器名称
        builder.for_mcp_server(request.config.server_name)
        
        # 添加工具
        for tool_info in request.config.tools:
            tool = Tool(
                name=tool_info.name,
                param_name=tool_info.param_name,
                param_type=tool_info.param_type,
                return_type=tool_info.return_type,
                description=tool_info.description,
                code=tool_info.code
            )
            builder._tools.append(tool)
        
        # 设置作者和端口
        builder._author = request.config.author
        builder._port = request.config.port
        
        # 构建完整的输出路径（mcpserver/servername/server.py）
        output_path = _build_output_path(request.config.server_name, request.output_path)
        
        # 保存模板到文件
        success = builder.save_template(output_path)
        
        if not success:
            raise HTTPException(status_code=500, detail="MCP服务器文件生成失败")
        
        # 准备响应数据
        response_data = {
            "success": True,
            "output_path": output_path,
            "message": f"MCP服务器文件生成成功: {output_path}",
            "service_name": request.config.server_name,
            "started": False
        }
        
        # 如果启用自动启动
        if request.auto_start:
            try:
                # 获取服务管理器实例
                service_manager = get_service_manager()
                
                # 注册服务到服务管理器
                service_id = service_manager.register_service(
                    name=request.config.server_name,
                    file_path=request.output_path,
                    host=request.host,
                    description=f"由MCPBuilder自动生成的服务",
                    author=request.config.author
                )
                
                response_data["service_id"] = service_id
                
                # 确定端口
                port = request.config.port
                if port is None:
                    # 如果没有指定端口，使用随机端口
                    import random
                    port = random.randint(10001, 18000)
                
                response_data["port"] = port
                
                # 启动服务（复用现有的启动逻辑）
                start_result = service_manager.start_service(service_id, port)
                
                if start_result.get('success', False):
                    response_data["started"] = True
                    response_data["pid"] = start_result.get('pid')
                    response_data["message"] += f"，服务已启动在端口 {port}，进程ID: {start_result.get('pid')}"
                else:
                    response_data["message"] += f"，但服务启动失败: {start_result.get('error', '未知错误')}"
                    
            except Exception as e:
                response_data["message"] += f"，但服务启动失败: {str(e)}"
        
        return MCPBuilderResponse(**response_data)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@generator_router.post("/preview-mcp", response_model=MCPBuilderResponse)
async def preview_mcp_with_builder(request: MCPBuilderRequest):
    """使用 MCPBuilder 预览 MCP 服务器代码（不生成文件）"""
    try:
        # 创建 MCPBuilder 实例
        builder = MCPBuilder()
        
        # 设置服务器名称
        builder.for_mcp_server(request.config.server_name)
        
        # 添加工具
        for tool_info in request.config.tools:
            tool = Tool(
                name=tool_info.name,
                param_name=tool_info.param_name,
                param_type=tool_info.param_type,
                return_type=tool_info.return_type,
                description=tool_info.description,
                code=tool_info.code
            )
            builder._tools.append(tool)
        
        # 设置作者和端口
        builder._author = request.config.author
        builder._port = request.config.port
        
        # 生成模板内容
        content = builder.generate_template_content()
        
        return MCPBuilderResponse(
            success=True,
            content=content,
            message="MCP服务器代码预览生成成功"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
