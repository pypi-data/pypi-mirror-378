"""
API 数据模型

定义 FastAPI 请求和响应的数据模型
"""

from typing import Optional, List, Any, Dict, Union
from pydantic import BaseModel, Field
from datetime import datetime


class ServiceCreateRequest(BaseModel):
    """创建服务请求模型"""
    name: str = Field(..., description="服务名称")
    file_path: str = Field(..., description="服务文件路径")
    port: Optional[int] = Field(None, description="服务端口")
    host: str = Field("0.0.0.0", description="服务主机")
    description: Optional[str] = Field(None, description="服务描述")
    author: Optional[str] = Field(None, description="作者")


class ServiceUpdateRequest(BaseModel):
    """更新服务请求模型"""
    name: Optional[str] = Field(None, description="服务名称")
    port: Optional[int] = Field(None, description="服务端口")
    host: Optional[str] = Field(None, description="服务主机")
    description: Optional[str] = Field(None, description="服务描述")


class ServiceInfo(BaseModel):
    """服务信息响应模型"""
    id: str
    name: str
    file_path: str
    port: Optional[int]
    host: str
    status: str
    created_at: str
    updated_at: str
    pid: Optional[int] = None
    log_file: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None


class ServiceListResponse(BaseModel):
    """服务列表响应模型"""
    success: bool
    services: List[ServiceInfo]
    total: int


class ServiceResponse(BaseModel):
    """单个服务响应模型"""
    success: bool
    service: Optional[ServiceInfo] = None
    message: Optional[str] = None
    error: Optional[str] = None


class ServiceStartRequest(BaseModel):
    """启动服务请求模型"""
    port: int = Field(..., description="服务端口（必传）")


class ServiceActionResponse(BaseModel):
    """服务操作响应模型"""
    success: bool
    service_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None
    pid: Optional[int] = None


class LogsResponse(BaseModel):
    """日志响应模型"""
    success: bool
    logs: Optional[str] = None
    total_lines: Optional[int] = None
    returned_lines: Optional[int] = None
    error: Optional[str] = None


class MCPGenerateRequest(BaseModel):
    """MCP服务器生成请求模型"""
    output_path: str = Field(..., description="输出文件路径")
    service_name: Optional[str] = Field(None, description="服务名称")
    tool_name: Optional[str] = Field(None, description="工具函数名称")
    tool_param_name: str = Field("path", description="工具参数名称")
    tool_param_type: str = Field("str", description="工具参数类型")
    tool_return_type: str = Field("str", description="工具返回类型")
    tool_description: str = Field("MCP工具", description="工具描述")
    tool_code: str = Field("# 实现您的业务逻辑\n    output = \"处理完成\"", description="工具函数代码块")
    service_port: Optional[int] = Field(None, description="服务端口")
    author: str = Field("开发者", description="作者")


class MCPGenerateResponse(BaseModel):
    """MCP服务器生成响应模型"""
    success: bool
    output_path: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    timestamp: str
    version: str
    services_count: int


# MCP 代理相关模型

class MCPRequest(BaseModel):
    """MCP 请求模型"""
    jsonrpc: str = Field("2.0", description="JSON-RPC 版本")
    id: Union[str, int] = Field(..., description="请求ID")
    method: str = Field(..., description="MCP 方法名")
    params: Optional[Dict[str, Any]] = Field(None, description="方法参数")


class MCPResponse(BaseModel):
    """MCP 响应模型"""
    jsonrpc: str = Field("2.0", description="JSON-RPC 版本")
    id: Union[str, int] = Field(..., description="请求ID")
    result: Optional[Any] = Field(None, description="方法结果")
    error: Optional[Dict[str, Any]] = Field(None, description="错误信息")


class MCPProxyRequest(BaseModel):
    """MCP 代理请求模型"""
    service_name: str = Field(..., description="目标服务名称")
    mcp_request: MCPRequest = Field(..., description="MCP 请求数据")
    session_id: Optional[str] = Field(None, description="会话ID，如果不提供则创建新会话")


class MCPProxyResponse(BaseModel):
    """MCP 代理响应模型"""
    success: bool = Field(..., description="请求是否成功")
    service_name: str = Field(..., description="目标服务名称")
    session_id: Optional[str] = Field(None, description="会话ID")
    response: Optional[MCPResponse] = Field(None, description="MCP 响应数据")
    error: Optional[str] = Field(None, description="错误信息")
    timestamp: str = Field(..., description="响应时间戳")


class MCPServiceInfo(BaseModel):
    """MCP 服务信息模型"""
    name: str = Field(..., description="服务名称")
    port: int = Field(..., description="服务端口")
    host: str = Field(..., description="服务主机")
    status: str = Field(..., description="服务状态")
    description: Optional[str] = Field(None, description="服务描述")
    capabilities: Optional[Dict[str, Any]] = Field(None, description="服务能力")


class MCPAvailableServicesResponse(BaseModel):
    """可用 MCP 服务列表响应模型"""
    success: bool = Field(..., description="请求是否成功")
    services: List[MCPServiceInfo] = Field(..., description="可用服务列表")
    count: int = Field(..., description="服务数量")
    message: Optional[str] = Field(None, description="响应消息")


class MCPHealthCheckRequest(BaseModel):
    """MCP 健康检查请求模型"""
    service_name: str = Field(..., description="服务名称")


class MCPHealthCheckResponse(BaseModel):
    """MCP 健康检查响应模型"""
    success: bool = Field(..., description="请求是否成功")
    service_name: str = Field(..., description="服务名称")
    status: str = Field(..., description="健康状态")
    port: Optional[int] = Field(None, description="服务端口")
    host: Optional[str] = Field(None, description="服务主机")
    message: Optional[str] = Field(None, description="状态消息")


# 文件上传相关模型

class UploadPackageRequest(BaseModel):
    """上传压缩包请求模型"""
    service_name: Optional[str] = Field(None, description="服务名称（可选，默认从压缩包名提取）")
    port: Optional[int] = Field(None, description="服务端口（可选，默认随机）")
    host: str = Field("127.0.0.1", description="服务主机")
    description: Optional[str] = Field(None, description="服务描述")
    author: Optional[str] = Field(None, description="作者")
    auto_start: bool = Field(True, description="是否自动启动服务")
    extract_path: Optional[str] = Field(None, description="解压路径（可选，默认为服务名）")
    entry_filename: Optional[str] = Field(None, description="指定入口文件名（用于uv run启动）")


class UploadPackageResponse(BaseModel):
    """上传压缩包响应模型"""
    success: bool = Field(..., description="请求是否成功")
    service_id: Optional[str] = Field(None, description="服务ID")
    service_name: Optional[str] = Field(None, description="服务名称")
    extracted_files: List[str] = Field(default_factory=list, description="解压的文件列表")
    entry_file: Optional[str] = Field(None, description="入口文件路径")
    port: Optional[int] = Field(None, description="服务端口")
    pid: Optional[int] = Field(None, description="进程ID（如果自动启动）")
    message: Optional[str] = Field(None, description="响应消息")
    error: Optional[str] = Field(None, description="错误信息")


class UploadPythonFileRequest(BaseModel):
    """上传Python文件请求模型"""
    service_name: Optional[str] = Field(None, description="服务名称（可选，默认从文件名提取）")
    port: Optional[int] = Field(None, description="服务端口（可选，默认随机）")
    host: str = Field("127.0.0.1", description="服务主机")
    description: Optional[str] = Field(None, description="服务描述")
    author: Optional[str] = Field(None, description="作者")
    auto_start: bool = Field(True, description="是否自动启动服务")


class UploadPythonFileResponse(BaseModel):
    """上传Python文件响应模型"""
    success: bool = Field(..., description="请求是否成功")
    service_id: Optional[str] = Field(None, description="服务ID")
    service_name: Optional[str] = Field(None, description="服务名称")
    file_path: Optional[str] = Field(None, description="保存的文件路径")
    port: Optional[int] = Field(None, description="服务端口")
    pid: Optional[int] = Field(None, description="进程ID（如果自动启动）")
    message: Optional[str] = Field(None, description="响应消息")
    error: Optional[str] = Field(None, description="错误信息")


# MCPBuilder 相关模型

class ToolInfo(BaseModel):
    """工具信息模型"""
    name: str = Field(..., description="工具函数名称")
    param_name: str = Field(..., description="参数名称")
    param_type: str = Field(..., description="参数类型")
    return_type: str = Field(..., description="返回类型")
    description: str = Field(..., description="工具描述")
    code: str = Field(..., description="工具实现代码")


class MCPBuilderConfig(BaseModel):
    """MCPBuilder 配置模型"""
    server_name: str = Field(..., description="服务器名称")
    tools: List[ToolInfo] = Field(..., description="工具列表")
    author: str = Field("开发者", description="作者")
    port: Optional[int] = Field(None, description="服务端口")


class MCPBuilderRequest(BaseModel):
    """MCPBuilder 请求模型"""
    config: MCPBuilderConfig = Field(..., description="MCPBuilder 配置")
    output_path: str = Field(..., description="输出文件路径")
    auto_start: bool = Field(True, description="是否自动启动服务")
    host: str = Field("0.0.0.0", description="服务主机地址")


class MCPBuilderResponse(BaseModel):
    """MCPBuilder 响应模型"""
    success: bool = Field(..., description="请求是否成功")
    output_path: Optional[str] = Field(None, description="输出文件路径")
    message: Optional[str] = Field(None, description="响应消息")
    error: Optional[str] = Field(None, description="错误信息")
    content: Optional[str] = Field(None, description="生成的模板内容（预览模式）")
    service_id: Optional[str] = Field(None, description="服务ID（如果自动启动）")
    service_name: Optional[str] = Field(None, description="服务名称")
    port: Optional[int] = Field(None, description="服务端口")
    pid: Optional[int] = Field(None, description="进程ID（如果自动启动成功）")
    started: bool = Field(False, description="服务是否已启动")
