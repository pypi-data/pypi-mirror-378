"""
MCP Minder FastAPI 应用

提供 RESTful API 接口用于远程管理 MCP 服务
"""

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from minder.core.service_manager import ServiceManager
from minder.api.models import HealthResponse
from minder.api.routers import service_router, generator_router, proxy_router

# 创建 FastAPI 应用
app = FastAPI(
    title="MCP Minder API",
    description="MCP服务器管理框架的RESTful API接口",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务管理器
service_manager = ServiceManager()


@app.get("/", response_model=HealthResponse)
async def root():
    """根路径健康检查"""
    services = service_manager.list_services()
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="0.1.0",
        services_count=len(services)
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    services = service_manager.list_services()
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="0.1.0",
        services_count=len(services)
    )


# 注册路由
app.include_router(service_router, prefix="/api/services")
app.include_router(generator_router, prefix="/api")
app.include_router(proxy_router)




# ==================== 错误处理 ====================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """404错误处理"""
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": "资源不存在"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """500错误处理"""
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "内部服务器错误"}
    )




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
