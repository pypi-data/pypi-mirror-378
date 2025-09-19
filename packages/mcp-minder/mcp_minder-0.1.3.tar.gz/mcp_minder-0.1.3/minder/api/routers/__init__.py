"""
路由模块

包含所有业务路由的定义
"""

from .service_router import service_router
from .generator_router import generator_router
from .proxy_router import proxy_router

__all__ = [
    "service_router",
    "generator_router", 
    "proxy_router"
]
