"""
快速文件上传测试脚本

简单的文件上传功能测试
"""

import tempfile
import requests
from pathlib import Path


def create_test_python_file():
    """创建测试用的Python文件"""
    python_code = '''"""
测试MCP服务器
"""
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("quick-test-server")

@server.list_tools()
async def list_tools():
    return [Tool(name="test", description="测试工具")]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    return [TextContent(type="text", text="测试成功")]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server.app, host="0.0.0.0", port=8004)
'''
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
    temp_file.write(python_code)
    temp_file.close()
    return temp_file.name


def test_python_upload():
    """测试Python文件上传"""
    print("🐍 测试Python文件上传...")
    
    python_file = create_test_python_file()
    
    try:
        with open(python_file, 'rb') as f:
            files = {'file': (Path(python_file).name, f, 'text/x-python')}
            data = {
                'service_name': 'quick_test_python',
                'auto_start': 'true'
            }
            
            response = requests.post(
                'http://localhost:8000/api/services/upload-python',
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Python文件上传成功!")
                print(f"服务ID: {result.get('service_id')}")
                print(f"服务名称: {result.get('service_name')}")
                print(f"文件路径: {result.get('file_path')}")
                print(f"服务端口: {result.get('port')}")
                return True
            else:
                print(f"❌ 上传失败: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 上传异常: {e}")
        return False
    finally:
        Path(python_file).unlink(missing_ok=True)


def test_api_health():
    """测试API健康状态"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API服务正常: {data.get('status')}")
            return True
        else:
            print(f"❌ API服务异常: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接API服务: {e}")
        return False


def main():
    """主函数"""
    print("🚀 快速文件上传测试")
    print("=" * 40)
    
    # 检查API健康状态
    if not test_api_health():
        print("❌ 请确保MCP Minder API正在运行 (http://localhost:8000)")
        return
    
    # 测试Python文件上传
    if test_python_upload():
        print("\n🎉 测试完成！")
    else:
        print("\n⚠️ 测试失败")


if __name__ == "__main__":
    main()
