"""
文件上传API测试脚本

测试压缩包上传和Python文件上传功能
"""

import asyncio
import tempfile
import zipfile
import requests
from pathlib import Path
from minder.client.api_client import MCPMinderAPIClient


def create_sample_python_file():
    """创建示例Python MCP服务器文件"""
    
    python_code = '''"""
示例MCP服务器

这是一个简单的MCP服务器示例，用于测试文件上传功能
"""

import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent

# 创建服务器实例
server = Server("test-upload-server")

@server.list_tools()
async def list_tools():
    """列出可用工具"""
    return [
        Tool(
            name="test_echo",
            description="测试回显功能",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "要回显的消息"
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="test_calculator",
            description="简单计算器",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的表达式，如 '2+3'"
                    }
                },
                "required": ["expression"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """调用工具"""
    if name == "test_echo":
        message = arguments.get("message", "")
        return [TextContent(type="text", text=f"回显: {message}")]
    
    elif name == "test_calculator":
        expression = arguments.get("expression", "")
        try:
            # 简单的安全计算（仅支持基本运算）
            allowed_chars = set('0123456789+-*/.() ')
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
                return [TextContent(type="text", text=f"{expression} = {result}")]
            else:
                return [TextContent(type="text", text="错误: 表达式包含不允许的字符")]
        except Exception as e:
            return [TextContent(type="text", text=f"计算错误: {str(e)}")]
    
    else:
        raise ValueError(f"未知工具: {name}")

if __name__ == "__main__":
    import uvicorn
    print("启动测试MCP服务器...")
    uvicorn.run(server.app, host="0.0.0.0", port=8002)
'''
    
    # 创建临时文件
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
    temp_file.write(python_code)
    temp_file.close()
    
    return temp_file.name


def create_sample_zip_package():
    """创建示例压缩包"""
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建主Python文件
        main_file = temp_path / "main.py"
        main_file.write_text('''"""
示例MCP服务器包

这是一个包含多个文件的MCP服务器示例
"""

import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent

# 创建服务器实例
server = Server("zip-package-server")

@server.list_tools()
async def list_tools():
    """列出可用工具"""
    return [
        Tool(
            name="hello_world",
            description="Hello World工具",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "要问候的名字"
                    }
                },
                "required": ["name"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """调用工具"""
    if name == "hello_world":
        name = arguments.get("name", "World")
        return [TextContent(type="text", text=f"Hello, {name}!")]
    else:
        raise ValueError(f"未知工具: {name}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server.app, host="0.0.0.0", port=8003)
''', encoding='utf-8')
        
        # 创建requirements.txt
        requirements_file = temp_path / "requirements.txt"
        requirements_file.write_text("mcp>=1.13.1\nuvicorn>=0.24.0\n", encoding='utf-8')
        
        # 创建README.md
        readme_file = temp_path / "README.md"
        readme_file.write_text("# 示例MCP服务器包\n\n这是一个从压缩包上传的MCP服务器示例。", encoding='utf-8')
        
        # 创建配置文件
        config_file = temp_path / "config.json"
        config_file.write_text('{"name": "zip-package-server", "version": "1.0.0"}', encoding='utf-8')
        
        # 创建zip文件
        zip_path = temp_path.parent / "test_mcp_package.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_path.rglob('*'):
                if file_path.is_file():
                    zipf.write(file_path, file_path.relative_to(temp_path))
        
        return str(zip_path)


def test_api_health():
    """测试API健康状态"""
    print("🔍 测试API健康状态...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API服务正常: {data.get('status')}")
            print(f"📊 当前服务数量: {data.get('services_count', 0)}")
            return True
        else:
            print(f"❌ API服务异常: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到API服务: {e}")
        return False


async def test_python_file_upload():
    """测试Python文件上传"""
    print("\n🐍 测试Python文件上传...")
    
    # 创建示例Python文件
    python_file = create_sample_python_file()
    
    try:
        async with MCPMinderAPIClient("http://localhost:8000") as client:
            
            # 测试上传
            result = await client.async_upload_python_file(
                file_path=python_file,
                service_name="test_python_upload",
                description="测试Python文件上传功能",
                author="测试脚本",
                auto_start=True
            )
            
            if result.get("success"):
                print("✅ Python文件上传成功!")
                print(f"📋 服务ID: {result.get('service_id')}")
                print(f"🏷️ 服务名称: {result.get('service_name')}")
                print(f"📁 文件路径: {result.get('file_path')}")
                print(f"🔌 服务端口: {result.get('port')}")
                print(f"🔄 进程ID: {result.get('pid')}")
                print(f"💬 消息: {result.get('message')}")
                
                # 等待服务启动
                await asyncio.sleep(2)
                
                # 检查服务状态
                services = await client.async_get_services()
                for service in services.get("services", []):
                    if service.get("name") == "test_python_upload":
                        print(f"📊 服务状态: {service.get('status')}")
                        break
                
                return True
            else:
                print(f"❌ Python文件上传失败: {result.get('error')}")
                return False
                
    except Exception as e:
        print(f"❌ Python文件上传测试异常: {e}")
        return False
    finally:
        # 清理临时文件
        Path(python_file).unlink(missing_ok=True)


async def test_zip_package_upload():
    """测试压缩包上传"""
    print("\n📦 测试压缩包上传...")
    
    # 创建示例压缩包
    zip_file = create_sample_zip_package()
    
    try:
        async with MCPMinderAPIClient("http://localhost:8000") as client:
            
            # 测试上传
            result = await client.async_upload_package(
                file_path=zip_file,
                service_name="test_zip_upload",
                description="测试压缩包上传功能",
                author="测试脚本",
                auto_start=True
            )
            
            if result.get("success"):
                print("✅ 压缩包上传成功!")
                print(f"📋 服务ID: {result.get('service_id')}")
                print(f"🏷️ 服务名称: {result.get('service_name')}")
                print(f"📁 入口文件: {result.get('entry_file')}")
                print(f"🔌 服务端口: {result.get('port')}")
                print(f"📦 解压文件数: {len(result.get('extracted_files', []))}")
                print(f"🔄 进程ID: {result.get('pid')}")
                print(f"💬 消息: {result.get('message')}")
                
                # 显示解压的文件列表
                extracted_files = result.get('extracted_files', [])
                if extracted_files:
                    print("📁 解压的文件:")
                    for file in extracted_files[:5]:  # 只显示前5个
                        print(f"  - {file}")
                    if len(extracted_files) > 5:
                        print(f"  ... 还有 {len(extracted_files) - 5} 个文件")
                
                # 等待服务启动
                await asyncio.sleep(2)
                
                # 检查服务状态
                services = await client.async_get_services()
                for service in services.get("services", []):
                    if service.get("name") == "test_zip_upload":
                        print(f"📊 服务状态: {service.get('status')}")
                        break
                
                return True
            else:
                print(f"❌ 压缩包上传失败: {result.get('error')}")
                return False
                
    except Exception as e:
        print(f"❌ 压缩包上传测试异常: {e}")
        return False
    finally:
        # 清理临时文件
        Path(zip_file).unlink(missing_ok=True)


def test_sync_upload():
    """测试同步上传功能"""
    print("\n🔄 测试同步上传功能...")
    
    # 创建示例Python文件
    python_file = create_sample_python_file()
    
    try:
        with MCPMinderAPIClient("http://localhost:8000") as client:
            
            # 测试同步上传
            result = client.upload_python_file(
                file_path=python_file,
                service_name="test_sync_upload",
                description="测试同步上传功能",
                author="测试脚本",
                auto_start=False  # 不上传后自动启动
            )
            
            if result.get("success"):
                print("✅ 同步上传成功!")
                print(f"📋 服务ID: {result.get('service_id')}")
                print(f"🏷️ 服务名称: {result.get('service_name')}")
                print(f"📁 文件路径: {result.get('file_path')}")
                print(f"💬 消息: {result.get('message')}")
                
                # 手动启动服务
                if result.get("service_id"):
                    start_result = client.start_service(result["service_id"])
                    if start_result.get("success"):
                        print("✅ 服务手动启动成功!")
                    else:
                        print(f"❌ 服务启动失败: {start_result.get('error')}")
                
                return True
            else:
                print(f"❌ 同步上传失败: {result.get('error')}")
                return False
                
    except Exception as e:
        print(f"❌ 同步上传测试异常: {e}")
        return False
    finally:
        # 清理临时文件
        Path(python_file).unlink(missing_ok=True)


def test_error_cases():
    """测试错误情况"""
    print("\n🚫 测试错误情况...")
    
    try:
        with MCPMinderAPIClient("http://localhost:8000") as client:
            
            # 测试不存在的文件
            print("测试不存在的文件...")
            result = client.upload_python_file("nonexistent.py")
            if not result.get("success"):
                print("✅ 正确处理了不存在的文件")
            else:
                print("❌ 应该拒绝不存在的文件")
            
            # 测试非Python文件（创建临时txt文件）
            temp_txt = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
            temp_txt.write(b"This is not a Python file")
            temp_txt.close()
            
            print("测试非Python文件...")
            result = client.upload_python_file(temp_txt.name)
            if not result.get("success"):
                print("✅ 正确拒绝了非Python文件")
            else:
                print("❌ 应该拒绝非Python文件")
            
            # 清理
            Path(temp_txt.name).unlink(missing_ok=True)
            
            return True
            
    except Exception as e:
        print(f"❌ 错误测试异常: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始文件上传API测试")
    print("=" * 60)
    
    # 测试API健康状态
    if not test_api_health():
        print("❌ API服务不可用，请确保MCP Minder API正在运行")
        return
    
    # 测试计数
    total_tests = 0
    passed_tests = 0
    
    # 测试Python文件上传
    total_tests += 1
    if await test_python_file_upload():
        passed_tests += 1
    
    # 测试压缩包上传
    total_tests += 1
    if await test_zip_package_upload():
        passed_tests += 1
    
    # 测试同步上传
    total_tests += 1
    if test_sync_upload():
        passed_tests += 1
    
    # 测试错误情况
    total_tests += 1
    if test_error_cases():
        passed_tests += 1
    
    # 测试结果汇总
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查相关功能")


if __name__ == "__main__":
    asyncio.run(main())
