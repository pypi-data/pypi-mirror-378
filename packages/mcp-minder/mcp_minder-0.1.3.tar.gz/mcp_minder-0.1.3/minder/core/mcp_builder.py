"""
MCP服务器构建器模块

提供用于构建MCP服务器模板的链式API
"""

import json
import httpx
import inspect
import ast
from typing import List, Dict, Optional, Any, Callable, Union
from pathlib import Path


class FunctionParser:
    """函数解析器，用于自动解析函数签名和代码"""
    
    @staticmethod
    def parse_function(func: Callable) -> Dict[str, Any]:
        """
        解析函数，提取函数信息
        
        Args:
            func: 要解析的函数
            
        Returns:
            包含函数信息的字典
        """
        # 获取函数签名
        sig = inspect.signature(func)
        
        # 获取函数名
        name = func.__name__
        
        # 获取函数文档字符串
        docstring = inspect.getdoc(func) or ""
        
        # 解析参数
        params = []
        for param_name, param in sig.parameters.items():
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else "str"
            params.append({
                "name": param_name,
                "type": FunctionParser._get_type_string(param_type),
                "default": param.default if param.default != inspect.Parameter.empty else None
            })
        
        # 获取返回类型
        return_type = sig.return_annotation if sig.return_annotation != inspect.Parameter.empty else "str"
        return_type_str = FunctionParser._get_type_string(return_type)
        
        # 获取函数源代码
        try:
            source = inspect.getsource(func)
            # 移除函数定义行，只保留函数体
            lines = source.split('\n')
            # 找到函数体开始的位置
            body_start = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('def ') or line.strip().startswith('async def '):
                    # 找到函数体开始（第一个非空行或第一个有缩进的行）
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and not lines[j].startswith('    '):
                            body_start = j
                            break
                    break
            
            # 提取函数体代码
            if body_start > 0:
                body_lines = lines[body_start:]
                # 移除函数定义和文档字符串
                code_lines = []
                in_docstring = False
                for line in body_lines:
                    stripped = line.strip()
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        if in_docstring:
                            in_docstring = False
                        else:
                            in_docstring = True
                        continue
                    if not in_docstring and stripped and not stripped.startswith('def ') and not stripped.startswith('async def '):
                        # 移除函数定义行的缩进
                        if line.startswith('    '):
                            code_lines.append(line[4:])
                        else:
                            code_lines.append(line)
                
                function_body = '\n'.join(code_lines)
            else:
                function_body = "# 函数体代码\n    pass"
                
        except Exception:
            function_body = "# 无法获取函数源代码\n    pass"
        
        return {
            "name": name,
            "params": params,
            "return_type": return_type_str,
            "description": docstring,
            "code": function_body
        }
    
    @staticmethod
    def _get_type_string(type_annotation) -> str:
        """将类型注解转换为字符串"""
        if hasattr(type_annotation, '__name__'):
            return type_annotation.__name__
        elif hasattr(type_annotation, '__origin__'):
            # 处理泛型类型如 List[str], Dict[str, int] 等
            origin = type_annotation.__origin__
            if origin is list:
                return "List"
            elif origin is dict:
                return "Dict"
            elif origin is tuple:
                return "Tuple"
            else:
                return str(origin)
        else:
            return str(type_annotation)


class Tool:
    """工具类，用于定义MCP工具"""
    
    def __init__(
        self,
        name: str = None,
        param_name: str = "input",
        param_type: str = "str",
        return_type: str = "str",
        description: str = "MCP工具",
        code: str = "# 实现您的业务逻辑\n    output = \"处理完成\"",
        func: Callable = None
    ):
        """
        初始化工具
        
        Args:
            name: 工具函数名称
            param_name: 参数名称
            param_type: 参数类型
            return_type: 返回类型
            description: 工具描述
            code: 工具实现代码
            func: 函数对象（如果提供，将自动解析函数信息）
        """
        if func is not None:
            # 从函数自动解析信息
            func_info = FunctionParser.parse_function(func)
            self.name = func_info["name"]
            self.description = func_info["description"] or "MCP工具"
            self.code = func_info["code"]
            self.return_type = func_info["return_type"]
            
            # 处理参数（取第一个参数作为主要参数）
            if func_info["params"]:
                self.param_name = func_info["params"][0]["name"]
                self.param_type = func_info["params"][0]["type"]
            else:
                self.param_name = param_name
                self.param_type = param_type
        else:
            # 手动设置参数
            self.name = name or "unnamed_tool"
            self.param_name = param_name
            self.param_type = param_type
            self.return_type = return_type
            self.description = description
            self.code = code
    
    @classmethod
    def from_function(cls, func: Callable) -> 'Tool':
        """
        从函数创建工具实例
        
        Args:
            func: 函数对象
            
        Returns:
            Tool实例
        """
        return cls(func=func)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "param_name": self.param_name,
            "param_type": self.param_type,
            "return_type": self.return_type,
            "description": self.description,
            "code": self.code
        }


class MCPBuilder:
    """MCP服务器构建器类，提供链式API"""
    
    def __init__(self):
        """初始化构建器"""
        self._server_name: Optional[str] = None
        self._tools: List[Tool] = []
        self._api_url: Optional[str] = None
        self._api_token: Optional[str] = None
        self._author: str = "开发者"
        self._port: Optional[int] = None
    
    def for_mcp_server(self, server_name: str) -> 'MCPBuilder':
        """
        设定MCP服务器名称
        
        Args:
            server_name: 服务器名称
            
        Returns:
            返回自身以支持链式调用
        """
        self._server_name = server_name
        return self
    
    def add_tool(
        self,
        tool_or_func: Union[str, Callable],
        param_name: str = "input",
        param_type: str = "str",
        return_type: str = "str",
        description: str = "MCP工具",
        code: str = "# 实现您的业务逻辑\n    output = \"处理完成\""
    ) -> 'MCPBuilder':
        """
        添加工具到MCP服务器
        
        Args:
            tool_or_func: 工具名称（字符串）或函数对象
            param_name: 参数名称（仅在传入字符串时使用）
            param_type: 参数类型（仅在传入字符串时使用）
            return_type: 返回类型（仅在传入字符串时使用）
            description: 工具描述（仅在传入字符串时使用）
            code: 工具实现代码（仅在传入字符串时使用）
            
        Returns:
            返回自身以支持链式调用
        """
        if callable(tool_or_func):
            # 如果传入的是函数，自动解析函数信息
            tool = Tool.from_function(tool_or_func)
        else:
            # 如果传入的是字符串，使用传统方式创建工具
            tool = Tool(tool_or_func, param_name, param_type, return_type, description, code)
        
        self._tools.append(tool)
        return self
    
    def set_up(self, author: str = "开发者") -> 'MCPBuilder':
        """
        设置作者信息
        
        Args:
            author: 作者名称（可选，默认为"开发者"）
            
        Returns:
            返回自身以支持链式调用
        """
        self._author = author
        return self
    
    def from_market(self, url: str, token: Optional[str] = None) -> 'MCPBuilder':
        """
        设置镜像源市场配置
        
        Args:
            url: 镜像源API地址（只需要指定域名和端口，如 http://localhost:8000）
            token: API访问令牌（可选）
            
        Returns:
            返回自身以支持链式调用
        """
        self._api_url = url
        self._api_token = token
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        构建MCP服务器配置数据
        
        Returns:
            包含所有配置的字典
        """
        if not self._server_name:
            raise ValueError("必须设置服务器名称，请调用 for_mcp_server() 方法")
        
        if not self._tools:
            raise ValueError("必须至少添加一个工具，请调用 add_tool() 方法")
        
        if not self._api_url:
            raise ValueError("必须设置镜像源地址，请调用 from_market() 方法")
        
        return {
            "server_name": self._server_name,
            "tools": [tool.to_dict() for tool in self._tools],
            "api_url": self._api_url,
            "api_token": self._api_token,
            "author": self._author,
            "port": self._port
        }
    
    async def generate_and_deploy(self, output_path: Optional[str] = None) -> bool:
        """
        生成MCP服务器文件并部署到指定目录
        
        Args:
            output_path: 输出路径（可选，如果不指定则使用服务器名称）
            
        Returns:
            是否成功生成和部署
        """
        try:
            # 构建配置数据
            config = self.build()
            
            # 如果没有指定输出路径，使用服务器名称
            if not output_path:
                output_path = f"{self._server_name}.py"
            
            # 构建完整的输出路径（mcpserver/servername/server.py）
            output_path = self._build_output_path(output_path)
            
            # 准备发送到API的数据
            api_data = {
                "config": config,
                "output_path": output_path
            }
            
            # 构建完整的API URL，自动添加路径
            api_url = self._build_api_url()
            
            # 准备请求头
            headers = {"Content-Type": "application/json"}
            if self._api_token:
                headers["Authorization"] = f"Bearer {self._api_token}"
            
            # 发送请求到API服务
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    api_url,
                    json=api_data,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ MCP服务器生成成功: {result.get('output_path', output_path)}")
                    return True
                else:
                    print(f"❌ API请求失败: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ 生成和部署失败: {e}")
            return False
    
    def _build_api_url(self) -> str:
        """
        构建完整的API URL，自动添加路径
        
        Returns:
            完整的API URL
        """
        # 移除末尾的斜杠
        base_url = self._api_url.rstrip('/')
        
        # 如果URL已经包含路径，直接返回
        if '/api/' in base_url or base_url.endswith('/api'):
            return base_url
        
        # 自动添加API路径
        return f"{base_url}/api/generate-mcp"
    
    def _build_output_path(self, output_path: str) -> str:
        """
        构建输出路径，确保文件保存在 mcpserver/servername/ 目录下
        
        Args:
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
            service_dir = mcpserver_dir / self._server_name
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
    
    def generate_template_content(self) -> str:
        """
        生成本地模板内容（不发送到API）
        
        Returns:
            生成的MCP服务器模板内容
        """
        if not self._server_name:
            raise ValueError("必须设置服务器名称，请调用 for_mcp_server() 方法")
        
        if not self._tools:
            raise ValueError("必须至少添加一个工具，请调用 add_tool() 方法")
        
        # 处理端口
        port_code = "random.randint(10001, 18000)" if self._port is None else str(self._port)
        
        # 生成工具函数代码
        tools_code = ""
        for tool in self._tools:
            tools_code += f'''
# 确保 mcp 工具装饰器能正确处理异步函数
@mcp.tool()
async def {tool.name}({tool.param_name}: {tool.param_type}) -> {tool.return_type}:
    """
    {tool.description},
    :param {tool.param_name}: input {tool.param_name}
    :return: output result
    """
    {tool.code}

    return output
'''
        
        # 生成完整模板
        template = f'''"""
MCP服务器模板 - 基于HTTP Stream的MCP服务器
作者: {self._author}
服务名称: {self._server_name}
"""

import logging
import random
import sys
from fastmcp import FastMCP

mcp = FastMCP("{self._server_name}")

logger = logging.getLogger(__name__)
{tools_code}
if __name__ == "__main__":
    # 检查命令行参数中的端口
    port = None
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            try:
                port = int(sys.argv[i + 1])
                break
            except ValueError:
                pass
    
    # 如果没有指定端口，使用随机端口
    if port is None:
        port = {port_code}
    
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp", stateless_http=True)
'''
        
        return template
    
    def save_template(self, output_path: str) -> bool:
        """
        保存模板到本地文件
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            是否保存成功
        """
        try:
            template_content = self.generate_template_content()
            
            # 构建完整的输出路径
            full_output_path = self._build_output_path(output_path)
            
            # 确保输出目录存在
            output_file = Path(full_output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            print(f"✅ MCP服务器模板保存成功: {full_output_path}")
            return True
            
        except Exception as e:
            print(f"❌ 保存模板失败: {e}")
            return False
