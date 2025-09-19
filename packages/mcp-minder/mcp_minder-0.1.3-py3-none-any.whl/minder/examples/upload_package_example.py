"""
MCP服务器压缩包上传示例

演示如何使用API上传MCP服务器压缩包并自动部署
"""

import asyncio
import zipfile
import tempfile
from pathlib import Path
from minder.client.api_client import MCPMinderAPIClient


def create_sample_mcp_server_zip():
    """创建一个示例MCP服务器zip文件用于测试"""
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建示例MCP服务器文件
        server_code = '''"""
示例MCP服务器

这是一个简单的MCP服务器示例
"""

import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent

# 创建服务器实例
server = Server("sample-server")

@server.list_tools()
async def list_tools():
    """列出可用工具"""
    return [
        Tool(
            name="echo",
            description="回显输入的文本",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "要回显的文本"
                    }
                },
                "required": ["text"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """调用工具"""
    if name == "echo":
        text = arguments.get("text", "")
        return [TextContent(type="text", text=f"回显: {text}")]
    else:
        raise ValueError(f"未知工具: {name}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server.app, host="0.0.0.0", port=8001)
'''
        
        # 写入主文件
        main_file = temp_path / "main.py"
        main_file.write_text(server_code, encoding='utf-8')
        
        # 创建requirements.txt
        requirements_file = temp_path / "requirements.txt"
        requirements_file.write_text("mcp>=1.13.1\nuvicorn>=0.24.0\n", encoding='utf-8')
        
        # 创建README.md
        readme_file = temp_path / "README.md"
        readme_file.write_text("# 示例MCP服务器\n\n这是一个简单的MCP服务器示例。", encoding='utf-8')
        
        # 创建zip文件
        zip_path = Path("sample_mcp_server.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_path.rglob('*'):
                if file_path.is_file():
                    zipf.write(file_path, file_path.relative_to(temp_path))
        
        print(f"✅ 创建示例zip文件: {zip_path}")
        return str(zip_path)


async def upload_example():
    """上传压缩包示例"""
    
    # 创建示例zip文件
    zip_path = create_sample_mcp_server_zip()
    
    try:
        # 创建API客户端
        async with MCPMinderAPIClient("http://localhost:8000") as client:
            
            print("📦 开始上传压缩包...")
            
            # 上传压缩包
            result = await client.async_upload_package(
                file_path=zip_path,
                service_name="sample_uploaded_service",
                description="从zip文件上传的示例服务",
                author="上传示例",
                auto_start=True,
                extract_path="sample_service"
            )
            
            if result.get("success"):
                print("✅ 压缩包上传成功!")
                print(f"服务ID: {result.get('service_id')}")
                print(f"服务名称: {result.get('service_name')}")
                print(f"入口文件: {result.get('entry_file')}")
                print(f"解压文件数: {len(result.get('extracted_files', []))}")
                print(f"服务端口: {result.get('port')}")
                print(f"进程ID: {result.get('pid')}")
                print(f"消息: {result.get('message')}")
                
                # 等待一下让服务启动
                await asyncio.sleep(2)
                
                # 检查服务状态
                print("\n🔍 检查服务状态...")
                services = await client.async_get_services()
                for service in services.get("services", []):
                    if service.get("name") == "sample_uploaded_service":
                        print(f"服务状态: {service.get('status')}")
                        print(f"服务端口: {service.get('port')}")
                        break
                
                # 获取服务日志
                print("\n📄 获取服务日志...")
                if result.get("service_id"):
                    logs = await client.async_get_service_logs(result["service_id"], lines=10)
                    if logs.get("success"):
                        print("服务日志:")
                        print(logs.get("logs", "无日志"))
                
            else:
                print(f"❌ 上传失败: {result.get('error')}")
                
    except Exception as e:
        print(f"❌ 上传过程中发生错误: {e}")
    
    finally:
        # 清理临时文件
        zip_file = Path(zip_path)
        if zip_file.exists():
            zip_file.unlink()
            print(f"🗑️ 清理临时文件: {zip_path}")


def sync_upload_example():
    """同步上传压缩包示例"""
    
    # 创建示例zip文件
    zip_path = create_sample_mcp_server_zip()
    
    try:
        # 创建API客户端
        with MCPMinderAPIClient("http://localhost:8000") as client:
            
            print("📦 开始同步上传压缩包...")
            
            # 上传压缩包
            result = client.upload_package(
                file_path=zip_path,
                service_name="sync_uploaded_service",
                description="同步上传的示例服务",
                author="同步上传示例",
                auto_start=False,  # 不上传后自动启动
                extract_path="sync_service"
            )
            
            if result.get("success"):
                print("✅ 压缩包同步上传成功!")
                print(f"服务ID: {result.get('service_id')}")
                print(f"服务名称: {result.get('service_name')}")
                print(f"入口文件: {result.get('entry_file')}")
                print(f"消息: {result.get('message')}")
                
                # 手动启动服务
                print("\n🚀 手动启动服务...")
                if result.get("service_id"):
                    start_result = client.start_service(result["service_id"])
                    if start_result.get("success"):
                        print(f"✅ 服务启动成功: {start_result.get('message')}")
                    else:
                        print(f"❌ 服务启动失败: {start_result.get('error')}")
                
            else:
                print(f"❌ 上传失败: {result.get('error')}")
                
    except Exception as e:
        print(f"❌ 上传过程中发生错误: {e}")
    
    finally:
        # 清理临时文件
        zip_file = Path(zip_path)
        if zip_file.exists():
            zip_file.unlink()
            print(f"🗑️ 清理临时文件: {zip_path}")


if __name__ == "__main__":
    print("🚀 MCP服务器压缩包上传示例")
    print("=" * 60)
    
    # 运行异步示例
    print("\n📱 异步上传示例:")
    asyncio.run(upload_example())
    
    print("\n" + "=" * 60)
    
    # 运行同步示例
    print("\n🔄 同步上传示例:")
    sync_upload_example()
    
    print("\n✅ 示例运行完成!")
    print("\n💡 提示:")
    print("1. 确保MCP Minder API服务器正在运行 (http://localhost:8000)")
    print("2. 上传的zip文件应包含有效的MCP服务器Python文件")
    print("3. 系统会自动检测入口文件（main.py, app.py, server.py等）")
    print("4. 支持自动启动或手动启动服务")
