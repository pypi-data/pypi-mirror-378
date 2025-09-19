"""
服务管理路由

提供MCP服务的CRUD操作、启动停止、日志查看等功能
"""

import asyncio
import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import JSONResponse

from minder.core.service_manager import ServiceManager
from minder.api.models import (
    ServiceCreateRequest,
    ServiceUpdateRequest,
    ServiceStartRequest,
    ServiceListResponse,
    ServiceResponse,
    ServiceActionResponse,
    LogsResponse,
    ServiceInfo,
    UploadPackageResponse,
    UploadPythonFileResponse
)

# 创建服务管理路由
service_router = APIRouter(tags=["服务管理"])

# 获取服务管理器实例（从main.py中共享）
def get_service_manager() -> ServiceManager:
    from minder.api.main import service_manager
    return service_manager


@service_router.post("", response_model=ServiceResponse)
async def create_service(request: ServiceCreateRequest):
    """创建新服务"""
    try:
        service_id = get_service_manager().register_service(
            name=request.name,
            file_path=request.file_path,
            host=request.host,
            description=request.description,
            author=request.author
        )
        
        service_info = get_service_manager().get_service(service_id)
        return ServiceResponse(
            success=True,
            service=ServiceInfo(**service_info.__dict__),
            message=f"服务 {request.name} 创建成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@service_router.get("", response_model=ServiceListResponse)
async def list_services(status: Optional[str] = Query(None, description="状态过滤器")):
    """获取服务列表"""
    try:
        services = get_service_manager().list_services(status_filter=status)
        service_infos = [ServiceInfo(**service.__dict__) for service in services]
        
        return ServiceListResponse(
            success=True,
            services=service_infos,
            total=len(service_infos)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@service_router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: str):
    """获取特定服务信息"""
    try:
        service_info = get_service_manager().get_service(service_id)
        if not service_info:
            raise HTTPException(status_code=404, detail="服务不存在")
        
        return ServiceResponse(
            success=True,
            service=ServiceInfo(**service_info.__dict__)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@service_router.get("/by-name/{service_name}", response_model=ServiceResponse)
async def get_service_by_name(service_name: str):
    """根据服务名称获取服务信息"""
    try:
        service_info = get_service_manager().get_service_by_name(service_name)
        if not service_info:
            raise HTTPException(status_code=404, detail=f"服务 {service_name} 不存在")
        
        return ServiceResponse(
            success=True,
            service=ServiceInfo(**service_info.__dict__)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@service_router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(service_id: str, request: ServiceUpdateRequest):
    """更新服务信息"""
    try:
        result = get_service_manager().update_service(
            service_id=service_id,
            name=request.name,
            port=request.port,
            host=request.host,
            description=request.description
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        service_info = get_service_manager().get_service(service_id)
        return ServiceResponse(
            success=True,
            service=ServiceInfo(**service_info.__dict__),
            message=result['message']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@service_router.put("/by-name/{service_name}", response_model=ServiceResponse)
async def update_service_by_name(service_name: str, request: ServiceUpdateRequest):
    """根据服务名称更新服务信息"""
    try:
        # 先获取服务ID
        service_id = get_service_manager().get_service_id_by_name(service_name)
        if not service_id:
            raise HTTPException(status_code=404, detail=f"服务 {service_name} 不存在")
        
        result = get_service_manager().update_service(
            service_id=service_id,
            name=request.name,
            port=request.port,
            host=request.host,
            description=request.description
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        service_info = get_service_manager().get_service(service_id)
        return ServiceResponse(
            success=True,
            service=ServiceInfo(**service_info.__dict__),
            message=result['message']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@service_router.delete("/{service_id}", response_model=ServiceActionResponse)
async def delete_service(service_id: str):
    """删除服务"""
    try:
        result = get_service_manager().delete_service(service_id)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return ServiceActionResponse(
            success=True,
            service_id=service_id,
            message=result['message']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@service_router.delete("/by-name/{service_name}", response_model=ServiceActionResponse)
async def delete_service_by_name(service_name: str):
    """根据服务名称删除服务"""
    try:
        result = get_service_manager().delete_service_by_name(service_name)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return ServiceActionResponse(
            success=True,
            service_id=result.get('service_id'),
            message=result['message']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@service_router.post("/{service_id}/start", response_model=ServiceActionResponse)
async def start_service(service_id: str, request: ServiceStartRequest):
    """启动服务"""
    try:
        result = get_service_manager().start_service(service_id, request.port)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return ServiceActionResponse(
            success=True,
            service_id=service_id,
            message=result['message'],
            pid=result.get('pid')
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@service_router.post("/by-name/{service_name}/start", response_model=ServiceActionResponse)
async def start_service_by_name(service_name: str, request: ServiceStartRequest):
    """根据服务名称启动服务"""
    try:
        result = get_service_manager().start_service_by_name(service_name, request.port)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return ServiceActionResponse(
            success=True,
            service_id=result.get('service_id'),
            message=result['message'],
            pid=result.get('pid')
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@service_router.post("/{service_id}/stop", response_model=ServiceActionResponse)
async def stop_service(service_id: str):
    """停止服务"""
    try:
        result = get_service_manager().stop_service(service_id)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return ServiceActionResponse(
            success=True,
            service_id=service_id,
            message=result['message']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@service_router.post("/by-name/{service_name}/stop", response_model=ServiceActionResponse)
async def stop_service_by_name(service_name: str):
    """根据服务名称停止服务"""
    try:
        result = get_service_manager().stop_service_by_name(service_name)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return ServiceActionResponse(
            success=True,
            service_id=result.get('service_id'),
            message=result['message']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@service_router.post("/by-name/{service_name}/restart", response_model=ServiceActionResponse)
async def restart_service_by_name(service_name: str):
    """根据服务名称重启服务"""
    try:
        # 先停止服务
        stop_result = get_service_manager().stop_service_by_name(service_name)
        if not stop_result['success']:
            raise HTTPException(status_code=400, detail=f"停止服务失败: {stop_result['error']}")
        
        # 等待一秒
        await asyncio.sleep(1)
        
        # 再启动服务
        start_result = get_service_manager().start_service_by_name(service_name)
        if not start_result['success']:
            raise HTTPException(status_code=400, detail=f"启动服务失败: {start_result['error']}")
        
        return ServiceActionResponse(
            success=True,
            service_id=start_result.get('service_id'),
            message=f"服务 {service_name} 重启成功",
            pid=start_result.get('pid')
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@service_router.get("/{service_id}/logs", response_model=LogsResponse)
async def get_service_logs(
    service_id: str,
    lines: int = Query(50, description="返回的日志行数")
):
    """获取服务日志"""
    try:
        result = get_service_manager().get_service_logs(service_id, lines)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return LogsResponse(
            success=True,
            logs=result['logs'],
            total_lines=result['total_lines'],
            returned_lines=result['returned_lines']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@service_router.get("/by-name/{service_name}/logs", response_model=LogsResponse)
async def get_service_logs_by_name(
    service_name: str,
    lines: int = Query(50, description="返回的日志行数")
):
    """根据服务名称获取服务日志"""
    try:
        result = get_service_manager().get_service_logs_by_name(service_name, lines)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return LogsResponse(
            success=True,
            logs=result['logs'],
            total_lines=result['total_lines'],
            returned_lines=result['returned_lines']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@service_router.post("/sync", response_model=ServiceActionResponse)
async def sync_service_status():
    """同步服务状态"""
    try:
        get_service_manager().sync_service_status()
        return ServiceActionResponse(
            success=True,
            message="服务状态同步完成"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@service_router.post("/sync-services", response_model=ServiceActionResponse)
async def sync_services():
    """同步服务列表（重新扫描mcpserver目录）"""
    try:
        get_service_manager().sync_services()
        return ServiceActionResponse(
            success=True,
            message="服务列表同步完成"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 批量操作 API ====================

@service_router.post("/start-all", response_model=ServiceActionResponse)
async def start_all_services():
    """启动所有停止的服务"""
    try:
        services = get_service_manager().list_services(status_filter="stopped")
        started_count = 0
        failed_count = 0
        
        for service in services:
            result = get_service_manager().start_service(service.id)
            if result['success']:
                started_count += 1
            else:
                failed_count += 1
        
        return ServiceActionResponse(
            success=failed_count == 0,
            message=f"批量启动完成: 成功 {started_count} 个，失败 {failed_count} 个"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@service_router.post("/stop-all", response_model=ServiceActionResponse)
async def stop_all_services():
    """停止所有运行中的服务"""
    try:
        services = get_service_manager().list_services(status_filter="running")
        stopped_count = 0
        failed_count = 0
        
        for service in services:
            result = get_service_manager().stop_service(service.id)
            if result['success']:
                stopped_count += 1
            else:
                failed_count += 1
        
        return ServiceActionResponse(
            success=failed_count == 0,
            message=f"批量停止完成: 成功 {stopped_count} 个，失败 {failed_count} 个"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@service_router.post("/restart-all", response_model=ServiceActionResponse)
async def restart_all_services():
    """重启所有运行中的服务"""
    try:
        services = get_service_manager().list_services(status_filter="running")
        restarted_count = 0
        failed_count = 0
        
        for service in services:
            # 先停止
            stop_result = get_service_manager().stop_service(service.id)
            if stop_result['success']:
                # 等待一秒
                await asyncio.sleep(1)
                # 再启动
                start_result = get_service_manager().start_service(service.id)
                if start_result['success']:
                    restarted_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
        
        return ServiceActionResponse(
            success=failed_count == 0,
            message=f"批量重启完成: 成功 {restarted_count} 个，失败 {failed_count} 个"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 文件上传接口 ====================

@service_router.post("/upload-package", response_model=UploadPackageResponse)
async def upload_and_deploy_package(
    file: UploadFile = File(..., description="MCP服务器压缩包文件"),
    service_name: Optional[str] = Form(None, description="服务名称（可选）"),
    port: Optional[int] = Form(None, description="服务端口（可选）"),
    host: str = Form("127.0.0.1", description="服务主机"),
    description: Optional[str] = Form(None, description="服务描述"),
    author: Optional[str] = Form(None, description="作者"),
    auto_start: bool = Form(True, description="是否自动启动服务"),
    extract_path: Optional[str] = Form(None, description="解压路径（可选）"),
    entry_filename: Optional[str] = Form(None, description="指定入口文件名（用于uv run启动）")
):
    """
    上传MCP服务器压缩包并自动部署
    
    支持zip格式的压缩包上传，自动解压到mcpserver目录，
    检测入口文件并注册服务，可选择自动启动。
    
    如果指定了entry_filename，将优先使用该文件作为入口文件，
    否则使用默认逻辑查找入口文件（main.py, app.py, server.py等）。
    """
    temp_dir = None
    extracted_files = []
    
    try:
        # 验证文件类型
        if not file.filename:
            return UploadPackageResponse(
                success=False,
                error="未提供文件名"
            )
        
        # 检查文件扩展名
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ['.zip']:
            return UploadPackageResponse(
                success=False,
                error="仅支持zip格式的压缩包"
            )
        
        # 确定服务名称
        if not service_name:
            service_name = Path(file.filename).stem
        
        # 确定解压路径
        if not extract_path:
            extract_path = service_name
        
        # 创建临时目录用于解压
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        # 保存上传的文件到临时位置
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 解压文件
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            extracted_files = zip_ref.namelist()
        
        # 查找入口文件
        entry_file = None
        
        # 如果指定了入口文件名，优先使用指定的文件
        if entry_filename:
            # 在解压目录中查找指定的文件
            for root, dirs, files in os.walk(extract_dir):
                if entry_filename in files:
                    entry_file = os.path.join(root, entry_filename)
                    break
        
        # 如果没有指定文件名或没找到指定文件，使用默认逻辑查找
        if not entry_file:
            entry_candidates = ['main.py', 'app.py', 'server.py', 'index.py', f'{service_name}.py']
            
            # 首先在根目录查找
            for candidate in entry_candidates:
                candidate_path = os.path.join(extract_dir, candidate)
                if os.path.isfile(candidate_path):
                    entry_file = candidate_path
                    break
            
            # 如果根目录没找到，递归查找所有Python文件
            if not entry_file:
                for root, dirs, files in os.walk(extract_dir):
                    for file_name in files:
                        if file_name.endswith('.py'):
                            # 检查文件内容是否包含MCP相关代码
                            file_path = os.path.join(root, file_name)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    if any(keyword in content.lower() for keyword in ['mcp', 'server', 'tool', 'handler']):
                                        entry_file = file_path
                                        break
                            except:
                                continue
                    if entry_file:
                        break
        
        if not entry_file:
            if entry_filename:
                return UploadPackageResponse(
                    success=False,
                    error=f"未找到指定的入口文件: {entry_filename}"
                )
            else:
                return UploadPackageResponse(
                    success=False,
                    error="未找到有效的MCP服务器入口文件"
                )
        
        # 计算相对于解压目录的路径
        relative_entry_path = os.path.relpath(entry_file, extract_dir)
        
        # 创建mcpserver目录下的目标目录
        mcpserver_dir = Path("mcpserver")
        mcpserver_dir.mkdir(exist_ok=True)
        
        target_dir = mcpserver_dir / extract_path
        if target_dir.exists():
            # 如果目录已存在，添加时间戳后缀
            import time
            timestamp = int(time.time())
            extract_path = f"{extract_path}_{timestamp}"
            target_dir = mcpserver_dir / extract_path
        
        target_dir.mkdir(exist_ok=True)
        
        # 复制解压的文件到mcpserver目录
        shutil.copytree(extract_dir, target_dir, dirs_exist_ok=True)
        
        # 构建入口文件路径
        final_entry_path = target_dir / relative_entry_path
        
        # 注册服务
        service_id = get_service_manager().register_service(
            name=service_name,
            file_path=str(final_entry_path),
            host=host,
            description=description or f"从压缩包 {file.filename} 部署的服务",
            author=author or "文件上传部署"
        )
        
        # 获取服务信息
        service_info = get_service_manager().get_service(service_id)
        
        # 如果设置了自动启动，则启动服务
        pid = None
        if auto_start:
            start_result = get_service_manager().start_service(service_id, port)
            if start_result['success']:
                pid = start_result.get('pid')
            else:
                return UploadPackageResponse(
                    success=True,
                    service_id=service_id,
                    service_name=service_name,
                    extracted_files=extracted_files,
                    entry_file=str(final_entry_path),
                    port=service_info.port,
                    message=f"服务注册成功，但启动失败: {start_result['error']}"
                )
        
        return UploadPackageResponse(
            success=True,
            service_id=service_id,
            service_name=service_name,
            extracted_files=extracted_files,
            entry_file=str(final_entry_path),
            port=service_info.port,
            pid=pid,
            message=f"压缩包部署成功，服务{'已启动' if auto_start and pid else '已注册'}"
        )
        
    except zipfile.BadZipFile:
        return UploadPackageResponse(
            success=False,
            error="无效的zip文件格式"
        )
    except Exception as e:
        return UploadPackageResponse(
            success=False,
            error=f"部署失败: {str(e)}"
        )
    finally:
        # 清理临时目录
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


@service_router.post("/upload-python", response_model=UploadPythonFileResponse)
async def upload_python_file(
    file: UploadFile = File(..., description="MCP服务器Python文件"),
    service_name: Optional[str] = Form(None, description="服务名称（可选）"),
    port: Optional[int] = Form(None, description="服务端口（可选）"),
    host: str = Form("127.0.0.1", description="服务主机"),
    description: Optional[str] = Form(None, description="服务描述"),
    author: Optional[str] = Form(None, description="作者"),
    auto_start: bool = Form(True, description="是否自动启动服务")
):
    """
    上传Python文件并自动部署MCP服务器
    
    支持直接上传Python文件到mcpserver目录，
    自动注册服务，可选择自动启动。
    """
    try:
        # 验证文件类型
        if not file.filename:
            return UploadPythonFileResponse(
                success=False,
                error="未提供文件名"
            )
        
        # 检查文件扩展名
        file_extension = Path(file.filename).suffix.lower()
        if file_extension != '.py':
            return UploadPythonFileResponse(
                success=False,
                error="仅支持Python文件（.py格式）"
            )
        
        # 确定服务名称
        if not service_name:
            service_name = Path(file.filename).stem
        
        # 创建mcpserver目录
        mcpserver_dir = Path("mcpserver")
        mcpserver_dir.mkdir(exist_ok=True)
        
        # 处理文件名冲突
        file_path = mcpserver_dir / file.filename
        if file_path.exists():
            # 如果文件已存在，添加时间戳后缀
            import time
            timestamp = int(time.time())
            name_parts = file.filename.rsplit('.', 1)
            if len(name_parts) == 2:
                new_filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
            else:
                new_filename = f"{file.filename}_{timestamp}"
            file_path = mcpserver_dir / new_filename
        
        # 保存Python文件
        content = await file.read()
        try:
            # 尝试解码为UTF-8
            python_code = content.decode('utf-8')
        except UnicodeDecodeError:
            return UploadPythonFileResponse(
                success=False,
                error="文件编码错误，请确保文件为UTF-8编码"
            )
        
        # 验证Python文件内容
        if not any(keyword in python_code.lower() for keyword in ['mcp', 'server', 'tool', 'handler', 'uvicorn', 'fastapi']):
            return UploadPythonFileResponse(
                success=False,
                error="文件内容不符合MCP服务器格式，请检查是否包含MCP相关代码"
            )
        
        # 写入文件
        file_path.write_text(python_code, encoding='utf-8')
        
        # 注册服务
        service_id = get_service_manager().register_service(
            name=service_name,
            file_path=str(file_path),
            host=host,
            description=description or f"从Python文件 {file.filename} 部署的服务",
            author=author or "文件上传部署"
        )
        
        # 获取服务信息
        service_info = get_service_manager().get_service(service_id)
        
        # 如果设置了自动启动，则启动服务
        pid = None
        if auto_start:
            start_result = get_service_manager().start_service(service_id, port)
            if start_result['success']:
                pid = start_result.get('pid')
            else:
                return UploadPythonFileResponse(
                    success=True,
                    service_id=service_id,
                    service_name=service_name,
                    file_path=str(file_path),
                    port=service_info.port,
                    message=f"服务注册成功，但启动失败: {start_result['error']}"
                )
        
        return UploadPythonFileResponse(
            success=True,
            service_id=service_id,
            service_name=service_name,
            file_path=str(file_path),
            port=service_info.port,
            pid=pid,
            message=f"Python文件部署成功，服务{'已启动' if auto_start and pid else '已注册'}"
        )
        
    except Exception as e:
        return UploadPythonFileResponse(
            success=False,
            error=f"部署失败: {str(e)}"
        )
