"""
统一的MCP Minder API客户端

提供同步和异步两种接口，用于与MCP Minder API服务通信
"""

import httpx
import asyncio
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import os


class MCPMinderAPIClient:
    """
    MCP Minder API客户端
    
    提供与MCP Minder API服务通信的统一接口
    支持同步和异步两种使用方式
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 30.0):
        """
        初始化API客户端
        
        Args:
            base_url: API服务器基础URL
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._sync_client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None
    
    def _get_sync_client(self) -> httpx.Client:
        """获取同步HTTP客户端"""
        if self._sync_client is None:
            self._sync_client = httpx.Client(base_url=self.base_url, timeout=self.timeout)
        return self._sync_client
    
    def _get_async_client(self) -> httpx.AsyncClient:
        """获取异步HTTP客户端"""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        return self._async_client
    
    def close(self):
        """关闭同步客户端连接"""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None
    
    async def aclose(self):
        """关闭异步客户端连接"""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None
    
    # ==================== 健康检查 ====================
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查（同步）"""
        response = self._get_sync_client().get("/health")
        return response.json()
    
    async def async_health_check(self) -> Dict[str, Any]:
        """健康检查（异步）"""
        response = await self._get_async_client().get("/health")
        return response.json()
    
    # ==================== 服务管理 ====================
    
    def get_services(self, status: Optional[str] = None) -> Dict[str, Any]:
        """获取服务列表（同步）"""
        params = {"status": status} if status else {}
        response = self._get_sync_client().get("/api/services", params=params)
        return response.json()
    
    async def async_get_services(self, status: Optional[str] = None) -> Dict[str, Any]:
        """获取服务列表（异步）"""
        params = {"status": status} if status else {}
        response = await self._get_async_client().get("/api/services", params=params)
        return response.json()
    
    def create_service(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建服务（同步）"""
        response = self._get_sync_client().post("/api/services", json=service_data)
        return response.json()
    
    async def async_create_service(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建服务（异步）"""
        response = await self._get_async_client().post("/api/services", json=service_data)
        return response.json()
    
    def get_service(self, service_id: str) -> Dict[str, Any]:
        """获取服务信息（同步）"""
        response = self._get_sync_client().get(f"/api/services/{service_id}")
        return response.json()
    
    async def async_get_service(self, service_id: str) -> Dict[str, Any]:
        """获取服务信息（异步）"""
        response = await self._get_async_client().get(f"/api/services/{service_id}")
        return response.json()
    
    def get_service_by_name(self, service_name: str) -> Dict[str, Any]:
        """根据名称获取服务信息（同步）"""
        response = self._get_sync_client().get(f"/api/services/by-name/{service_name}")
        return response.json()
    
    async def async_get_service_by_name(self, service_name: str) -> Dict[str, Any]:
        """根据名称获取服务信息（异步）"""
        response = await self._get_async_client().get(f"/api/services/by-name/{service_name}")
        return response.json()
    
    def update_service(self, service_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新服务（同步）"""
        response = self._get_sync_client().put(f"/api/services/{service_id}", json=update_data)
        return response.json()
    
    async def async_update_service(self, service_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新服务（异步）"""
        response = await self._get_async_client().put(f"/api/services/{service_id}", json=update_data)
        return response.json()
    
    def update_service_by_name(self, service_name: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """根据名称更新服务（同步）"""
        response = self._get_sync_client().put(f"/api/services/by-name/{service_name}", json=update_data)
        return response.json()
    
    async def async_update_service_by_name(self, service_name: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """根据名称更新服务（异步）"""
        response = await self._get_async_client().put(f"/api/services/by-name/{service_name}", json=update_data)
        return response.json()
    
    def delete_service(self, service_id: str) -> Dict[str, Any]:
        """删除服务（同步）"""
        response = self._get_sync_client().delete(f"/api/services/{service_id}")
        return response.json()
    
    async def async_delete_service(self, service_id: str) -> Dict[str, Any]:
        """删除服务（异步）"""
        response = await self._get_async_client().delete(f"/api/services/{service_id}")
        return response.json()
    
    def delete_service_by_name(self, service_name: str) -> Dict[str, Any]:
        """根据名称删除服务（同步）"""
        response = self._get_sync_client().delete(f"/api/services/by-name/{service_name}")
        return response.json()
    
    async def async_delete_service_by_name(self, service_name: str) -> Dict[str, Any]:
        """根据名称删除服务（异步）"""
        response = await self._get_async_client().delete(f"/api/services/by-name/{service_name}")
        return response.json()
    
    # ==================== 服务控制 ====================
    
    def start_service(self, service_id: str, port: int) -> Dict[str, Any]:
        """启动服务（同步）"""
        data = {"port": port}
        response = self._get_sync_client().post(f"/api/services/{service_id}/start", json=data)
        return response.json()
    
    async def async_start_service(self, service_id: str, port: int) -> Dict[str, Any]:
        """启动服务（异步）"""
        data = {"port": port}
        response = await self._get_async_client().post(f"/api/services/{service_id}/start", json=data)
        return response.json()
    
    def start_service_by_name(self, service_name: str, port: int) -> Dict[str, Any]:
        """根据名称启动服务（同步）"""
        data = {"port": port}
        response = self._get_sync_client().post(f"/api/services/by-name/{service_name}/start", json=data)
        return response.json()
    
    async def async_start_service_by_name(self, service_name: str, port: int) -> Dict[str, Any]:
        """根据名称启动服务（异步）"""
        data = {"port": port}
        response = await self._get_async_client().post(f"/api/services/by-name/{service_name}/start", json=data)
        return response.json()
    
    def stop_service(self, service_id: str) -> Dict[str, Any]:
        """停止服务（同步）"""
        response = self._get_sync_client().post(f"/api/services/{service_id}/stop")
        return response.json()
    
    async def async_stop_service(self, service_id: str) -> Dict[str, Any]:
        """停止服务（异步）"""
        response = await self._get_async_client().post(f"/api/services/{service_id}/stop")
        return response.json()
    
    def stop_service_by_name(self, service_name: str) -> Dict[str, Any]:
        """根据名称停止服务（同步）"""
        response = self._get_sync_client().post(f"/api/services/by-name/{service_name}/stop")
        return response.json()
    
    async def async_stop_service_by_name(self, service_name: str) -> Dict[str, Any]:
        """根据名称停止服务（异步）"""
        response = await self._get_async_client().post(f"/api/services/by-name/{service_name}/stop")
        return response.json()
    
    def restart_service_by_name(self, service_name: str) -> Dict[str, Any]:
        """根据名称重启服务（同步）"""
        response = self._get_sync_client().post(f"/api/services/by-name/{service_name}/restart")
        return response.json()
    
    async def async_restart_service_by_name(self, service_name: str) -> Dict[str, Any]:
        """根据名称重启服务（异步）"""
        response = await self._get_async_client().post(f"/api/services/by-name/{service_name}/restart")
        return response.json()
    
    # ==================== 日志管理 ====================
    
    def get_service_logs(self, service_id: str, lines: int = 50) -> Dict[str, Any]:
        """获取服务日志（同步）"""
        response = self._get_sync_client().get(f"/api/services/{service_id}/logs", params={"lines": lines})
        return response.json()
    
    async def async_get_service_logs(self, service_id: str, lines: int = 50) -> Dict[str, Any]:
        """获取服务日志（异步）"""
        response = await self._get_async_client().get(f"/api/services/{service_id}/logs", params={"lines": lines})
        return response.json()
    
    def get_service_logs_by_name(self, service_name: str, lines: int = 50) -> Dict[str, Any]:
        """根据名称获取服务日志（同步）"""
        response = self._get_sync_client().get(f"/api/services/by-name/{service_name}/logs", params={"lines": lines})
        return response.json()
    
    async def async_get_service_logs_by_name(self, service_name: str, lines: int = 50) -> Dict[str, Any]:
        """根据名称获取服务日志（异步）"""
        response = await self._get_async_client().get(f"/api/services/by-name/{service_name}/logs", params={"lines": lines})
        return response.json()
    
    # ==================== 批量操作 ====================
    
    def start_all_services(self) -> Dict[str, Any]:
        """启动所有服务（同步）"""
        response = self._get_sync_client().post("/api/services/start-all")
        return response.json()
    
    async def async_start_all_services(self) -> Dict[str, Any]:
        """启动所有服务（异步）"""
        response = await self._get_async_client().post("/api/services/start-all")
        return response.json()
    
    def stop_all_services(self) -> Dict[str, Any]:
        """停止所有服务（同步）"""
        response = self._get_sync_client().post("/api/services/stop-all")
        return response.json()
    
    async def async_stop_all_services(self) -> Dict[str, Any]:
        """停止所有服务（异步）"""
        response = await self._get_async_client().post("/api/services/stop-all")
        return response.json()
    
    def restart_all_services(self) -> Dict[str, Any]:
        """重启所有服务（同步）"""
        response = self._get_sync_client().post("/api/services/restart-all")
        return response.json()
    
    async def async_restart_all_services(self) -> Dict[str, Any]:
        """重启所有服务（异步）"""
        response = await self._get_async_client().post("/api/services/restart-all")
        return response.json()
    
    # ==================== 同步操作 ====================
    
    def sync_service_status(self) -> Dict[str, Any]:
        """同步服务状态（同步）"""
        response = self._get_sync_client().post("/api/services/sync")
        return response.json()
    
    async def async_sync_service_status(self) -> Dict[str, Any]:
        """同步服务状态（异步）"""
        response = await self._get_async_client().post("/api/services/sync")
        return response.json()
    
    def sync_services(self) -> Dict[str, Any]:
        """同步服务列表（同步）"""
        response = self._get_sync_client().post("/api/services/sync-services")
        return response.json()
    
    async def async_sync_services(self) -> Dict[str, Any]:
        """同步服务列表（异步）"""
        response = await self._get_async_client().post("/api/services/sync-services")
        return response.json()
    
    # ==================== 代码生成 ====================
    
    def generate_mcp_server(self, generate_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成MCP服务器（同步）"""
        response = self._get_sync_client().post("/api/generate", json=generate_data)
        return response.json()
    
    async def async_generate_mcp_server(self, generate_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成MCP服务器（异步）"""
        response = await self._get_async_client().post("/api/generate", json=generate_data)
        return response.json()
    
    def preview_mcp_server(self, preview_data: Dict[str, Any]) -> Dict[str, Any]:
        """预览MCP服务器代码（同步）"""
        response = self._get_sync_client().post("/api/preview", json=preview_data)
        return response.json()
    
    async def async_preview_mcp_server(self, preview_data: Dict[str, Any]) -> Dict[str, Any]:
        """预览MCP服务器代码（异步）"""
        response = await self._get_async_client().post("/api/preview", json=preview_data)
        return response.json()
    
    # ==================== MCP代理 ====================
    
    def get_mcp_services(self) -> Dict[str, Any]:
        """获取可用的MCP服务列表（同步）"""
        response = self._get_sync_client().get("/api/mcp/services")
        return response.json()
    
    async def async_get_mcp_services(self) -> Dict[str, Any]:
        """获取可用的MCP服务列表（异步）"""
        response = await self._get_async_client().get("/api/mcp/services")
        return response.json()
    
    def check_mcp_service_health(self, service_name: str) -> Dict[str, Any]:
        """检查MCP服务健康状态（同步）"""
        response = self._get_sync_client().get(f"/api/mcp/services/{service_name}/health")
        return response.json()
    
    async def async_check_mcp_service_health(self, service_name: str) -> Dict[str, Any]:
        """检查MCP服务健康状态（异步）"""
        response = await self._get_async_client().get(f"/api/mcp/services/{service_name}/health")
        return response.json()
    
    # ==================== 上下文管理器 ====================
    
    def __enter__(self):
        """同步上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """同步上下文管理器出口"""
        self.close()
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.aclose()
    
    # ==================== 文件上传 ====================
    
    def upload_package(
        self,
        file_path: Union[str, Path],
        service_name: Optional[str] = None,
        port: Optional[int] = None,
        host: str = "127.0.0.1",
        description: Optional[str] = None,
        author: Optional[str] = None,
        auto_start: bool = True,
        extract_path: Optional[str] = None,
        entry_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        上传压缩包并部署服务（同步）
        
        Args:
            file_path: 压缩包文件路径
            service_name: 服务名称（可选）
            port: 服务端口（可选）
            host: 服务主机
            description: 服务描述
            author: 作者
            auto_start: 是否自动启动服务
            extract_path: 解压路径（可选）
            entry_filename: 指定入口文件名（可选）
            
        Returns:
            部署结果
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return {"success": False, "error": "文件不存在"}
        
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "application/zip")}
            data = {
                "service_name": service_name,
                "port": port,
                "host": host,
                "description": description,
                "author": author,
                "auto_start": auto_start,
                "extract_path": extract_path,
                "entry_filename": entry_filename
            }
            # 过滤None值
            data = {k: v for k, v in data.items() if v is not None}
            
            response = self._get_sync_client().post("/api/services/upload-package", files=files, data=data)
            return response.json()
    
    async def async_upload_package(
        self,
        file_path: Union[str, Path],
        service_name: Optional[str] = None,
        port: Optional[int] = None,
        host: str = "127.0.0.1",
        description: Optional[str] = None,
        author: Optional[str] = None,
        auto_start: bool = True,
        extract_path: Optional[str] = None,
        entry_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        上传压缩包并部署服务（异步）
        
        Args:
            file_path: 压缩包文件路径
            service_name: 服务名称（可选）
            port: 服务端口（可选）
            host: 服务主机
            description: 服务描述
            author: 作者
            auto_start: 是否自动启动服务
            extract_path: 解压路径（可选）
            entry_filename: 指定入口文件名（可选）
            
        Returns:
            部署结果
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return {"success": False, "error": "文件不存在"}
        
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "application/zip")}
            data = {
                "service_name": service_name,
                "port": port,
                "host": host,
                "description": description,
                "author": author,
                "auto_start": auto_start,
                "extract_path": extract_path,
                "entry_filename": entry_filename
            }
            # 过滤None值
            data = {k: v for k, v in data.items() if v is not None}
            
            response = await self._get_async_client().post("/api/services/upload-package", files=files, data=data)
            return response.json()
    
    # ==================== Python文件上传 ====================
    
    def upload_python_file(
        self,
        file_path: Union[str, Path],
        service_name: Optional[str] = None,
        port: Optional[int] = None,
        host: str = "127.0.0.1",
        description: Optional[str] = None,
        author: Optional[str] = None,
        auto_start: bool = True
    ) -> Dict[str, Any]:
        """
        上传Python文件并部署服务（同步）
        
        Args:
            file_path: Python文件路径
            service_name: 服务名称（可选）
            port: 服务端口（可选）
            host: 服务主机
            description: 服务描述
            author: 作者
            auto_start: 是否自动启动服务
            
        Returns:
            部署结果
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return {"success": False, "error": "文件不存在"}
        
        if file_path.suffix.lower() != '.py':
            return {"success": False, "error": "仅支持Python文件（.py格式）"}
        
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "text/x-python")}
            data = {
                "service_name": service_name,
                "port": port,
                "host": host,
                "description": description,
                "author": author,
                "auto_start": auto_start
            }
            # 过滤None值
            data = {k: v for k, v in data.items() if v is not None}
            
            response = self._get_sync_client().post("/api/services/upload-python", files=files, data=data)
            return response.json()
    
    async def async_upload_python_file(
        self,
        file_path: Union[str, Path],
        service_name: Optional[str] = None,
        port: Optional[int] = None,
        host: str = "127.0.0.1",
        description: Optional[str] = None,
        author: Optional[str] = None,
        auto_start: bool = True
    ) -> Dict[str, Any]:
        """
        上传Python文件并部署服务（异步）
        
        Args:
            file_path: Python文件路径
            service_name: 服务名称（可选）
            port: 服务端口（可选）
            host: 服务主机
            description: 服务描述
            author: 作者
            auto_start: 是否自动启动服务
            
        Returns:
            部署结果
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return {"success": False, "error": "文件不存在"}
        
        if file_path.suffix.lower() != '.py':
            return {"success": False, "error": "仅支持Python文件（.py格式）"}
        
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "text/x-python")}
            data = {
                "service_name": service_name,
                "port": port,
                "host": host,
                "description": description,
                "author": author,
                "auto_start": auto_start
            }
            # 过滤None值
            data = {k: v for k, v in data.items() if v is not None}
            
            response = await self._get_async_client().post("/api/services/upload-python", files=files, data=data)
            return response.json()
